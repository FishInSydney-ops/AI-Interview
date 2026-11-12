import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException

from app.common.errors import AppError
from app.common.responses import respond
from app.common.schemas import ApiResponse, HealthData, ReadinessData
from app.entry.config import Settings
from app.infrastructure.connections import Connections
from app.modules.admin_auth.router import router as admin_auth_router
from app.modules.admin_auth.service import AdminAuthService
from app.modules.system.router import public_router
from app.modules.system.router import router as system_router

logger = logging.getLogger("yunshu.api")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.connections = Connections(settings)
        try:
            yield
        finally:
            app.state.connections.close()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = uuid4().hex
        try:
            if request.method == "POST" and request.url.path == "/api/v1/admin/auth/sessions":
                peer = request.client.host if request.client else "unknown"
                await run_in_threadpool(
                    AdminAuthService(request.app.state.connections.engine).record_login_request,
                    peer,
                )
            if request.url.path.startswith("/api/v1/admin/") and request.method in {
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            }:
                # 本机同源代理保留 Origin；不信任客户端的转发 IP，不开放通配跨域。
                if (
                    request.headers.get("origin") not in settings.admin_allowed_origins
                    or request.headers.get("x-requested-with") != "XMLHttpRequest"
                ):
                    raise AppError(403, "FORBIDDEN", "请求来源无效，请从管理端页面重试")
            response = await call_next(request)
        except AppError as exc:
            response = respond(
                request, status=exc.status, code=exc.code, message=exc.message, headers=exc.headers
            )
        except Exception as exc:
            # 不记录异常正文，避免驱动异常泄露连接串、凭据或 SQL 参数。
            logger.error(
                "request_failed request_id=%s type=%s",
                request.state.request_id,
                type(exc).__name__,
            )
            response = respond(request, status=500, code="INTERNAL_ERROR", message="服务内部错误")
        if (
            request.method == "POST"
            and request.url.path == "/api/v1/admin/auth/sessions"
            and response.status_code >= 400
        ):
            try:
                await run_in_threadpool(
                    AdminAuthService(request.app.state.connections.engine).log_login_failure,
                    {
                        "ip": request.client.host if request.client else "unknown",
                        "request_id": request.state.request_id,
                    },
                    str(response.status_code),
                )
            except Exception:
                logger.error("login_audit_failed request_id=%s", request.state.request_id)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(AppError)
    async def business_error(request: Request, exc: AppError):
        return respond(
            request, status=exc.status, code=exc.code, message=exc.message, headers=exc.headers
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return respond(
            request,
            status=400,
            code="VALIDATION_ERROR",
            message="请求参数无效",
            details=[
                {"field": ".".join(map(str, item["loc"])), "reason": item["msg"]}
                for item in exc.errors()
            ],
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        codes = {
            401: "AUTH_REQUIRED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
        }
        return respond(
            request,
            status=exc.status_code,
            code=codes.get(exc.status_code, "HTTP_ERROR"),
            message="请求资源不可用",
            headers=exc.headers,
        )

    @app.get("/api/v1/health", tags=["基础工程"], response_model=ApiResponse[HealthData])
    def health(request: Request):
        return respond(request, {"status": "ok", "version": "0.1.0"})

    @app.get(
        "/api/v1/ready",
        tags=["基础工程"],
        response_model=ApiResponse[ReadinessData],
        responses={503: {"model": ApiResponse[ReadinessData]}},
    )
    def ready(request: Request):
        connections = request.app.state.connections
        checks: dict[str, str] = {}
        for name, check in {
            "mysql": lambda: _mysql_ready(connections),
            "redis": connections.redis.ping,
            "minio": lambda: connections.minio.bucket_exists(settings.minio_bucket),
        }.items():
            try:
                checks[name] = "ok" if check() else "unavailable"
            except Exception:
                checks[name] = "unavailable"
        available = all(value == "ok" for value in checks.values())
        return respond(
            request,
            {"status": "ready" if available else "degraded", "services": checks},
            status=200 if available else 503,
            code="OK" if available else "SERVICE_UNAVAILABLE",
            message="服务已就绪" if available else "部分基础服务暂不可用",
        )

    app.include_router(admin_auth_router)
    app.include_router(system_router)
    app.include_router(public_router)
    return app


def _mysql_ready(connections: Connections) -> bool:
    with connections.engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar_one() == 1
