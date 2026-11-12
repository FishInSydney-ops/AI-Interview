import io
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import insert, or_, select

from app.common.errors import AppError
from app.common.responses import respond
from app.infrastructure.models import admin_operation_log, platform_settings, stored_file
from app.modules.admin_auth.router import context
from app.modules.admin_auth.security import utc_now
from app.modules.admin_auth.service import AdminAuthService
from app.modules.system.permissions import catalogue
from app.modules.system.service import SystemService, audit, require

router = APIRouter(prefix="/api/v1/admin/system", tags=["系统管理"])
public_router = APIRouter(prefix="/api/v1/platform", tags=["平台展示"])


def svc(request):
    return SystemService(request.app.state.connections.engine)


def actor(request: Request):
    return AdminAuthService(request.app.state.connections.engine).current_session(
        request.cookies.get(request.app.state.settings.admin_cookie_name)
    )


def guard(permission):
    def dependency(current=Depends(actor)):
        require(current, permission)
        return current

    return dependency


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)


class RoleInput(Input):
    name: str = Field(min_length=1, max_length=64)
    code: str = Field(pattern=r"^[a-z][a-z0-9_]{1,63}$")
    description: str = Field(default="", max_length=500)
    permissions: list[str] = Field(max_length=100)
    version: int | None = Field(default=None, ge=1)

    @field_validator("name")
    @classmethod
    def nonempty(cls, value):
        if not value.strip():
            raise ValueError("名称不能为空")
        return value.strip()


class UserInput(Input):
    username: str = Field(pattern=r"^[A-Za-z0-9_\-\u4e00-\u9fff]{1,64}$")
    phone: str = Field(pattern=r"^\+?[0-9][0-9 -]{4,30}$")
    email: str = Field(default="", max_length=254)
    role_id: int = Field(gt=0)
    enabled: bool = True
    password: str | None = Field(default=None, min_length=8, max_length=128)
    version: int | None = Field(default=None, ge=1)

    @field_validator("email")
    @classmethod
    def email_format(cls, value):
        if value and ("@" not in value or " " in value or "\n" in value):
            raise ValueError("邮箱格式无效")
        return value


class BatchInput(Input):
    ids: list[int] = Field(min_length=1, max_length=100)
    action: str = Field(pattern=r"^(enable|disable|delete)$")

    @field_validator("ids")
    @classmethod
    def positive(cls, values):
        if any(v <= 0 for v in values):
            raise ValueError("ID必须为正数")
        return values


class SettingsInput(Input):
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(default="", max_length=1000)
    logo_file_id: int | None = Field(default=None, gt=0)
    avatar_file_id: int | None = Field(default=None, gt=0)
    version: int = Field(ge=1)

    @field_validator("name")
    @classmethod
    def nonempty(cls, value):
        if not value.strip():
            raise ValueError("平台名称不能为空")
        return value.strip()


@router.get("/permissions")
def permission_catalogue(request: Request, current=Depends(guard("system:roles"))):
    return respond(request, catalogue())


@router.get("/roles")
def list_roles(request: Request, current=Depends(guard("system:roles"))):
    return respond(request, svc(request).role_list())


@router.get("/role-options")
def role_options(request: Request, current=Depends(guard("user:view"))):
    return respond(
        request,
        [{"id": r["id"], "name": r["name"], "code": r["code"]} for r in svc(request).role_list()],
    )


@router.post("/roles")
def create_role(body: RoleInput, request: Request, current=Depends(guard("system:roles"))):
    return respond(
        request,
        svc(request).save_role(current, context(request), body.model_dump(exclude_none=True)),
        status=201,
    )


@router.put("/roles/{role_id}")
def update_role(
    role_id: int, body: RoleInput, request: Request, current=Depends(guard("system:roles"))
):
    return respond(
        request,
        svc(request).save_role(
            current, context(request), body.model_dump(exclude_none=True), role_id
        ),
    )


@router.delete("/roles/{role_id}")
def delete_role(role_id: int, request: Request, current=Depends(guard("system:roles"))):
    svc(request).delete_role(current, context(request), role_id)
    return respond(request)


@router.get("/users")
def list_users(
    request: Request,
    keyword: str = Query("", max_length=64),
    role_id: int | None = Query(None, gt=0),
    enabled: int | None = Query(None, ge=0, le=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current=Depends(guard("user:view")),
):
    return respond(request, svc(request).user_list(keyword, role_id, enabled, page, page_size))


@router.get("/users/{user_id}")
def user_detail(user_id: int, request: Request, current=Depends(guard("user:view"))):
    return respond(request, svc(request).user_detail(user_id))


@router.post("/users")
def create_user(body: UserInput, request: Request, current=Depends(guard("user:create"))):
    return respond(
        request, svc(request).save_user(current, context(request), body.model_dump()), status=201
    )


@router.put("/users/{user_id}")
def update_user(
    user_id: int, body: UserInput, request: Request, current=Depends(guard("user:edit"))
):
    return respond(
        request, svc(request).save_user(current, context(request), body.model_dump(), user_id)
    )


@router.post("/user-batches")
def batch_users(body: BatchInput, request: Request, current=Depends(actor)):
    svc(request).batch_users(current, context(request), body.ids, body.action)
    return respond(request)


@router.post("/users/{user_id}/password-resets")
def reset_password(user_id: int, request: Request, current=Depends(guard("user:reset"))):
    return respond(request, svc(request).reset_password(current, context(request), user_id))


def log_query(request, keyword, action, start, end):
    def utc(value):
        if value is None:
            return None
        if value.tzinfo is None:
            raise AppError(400, "VALIDATION_ERROR", "日志筛选时间须包含时区")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    start, end = utc(start), utc(end)
    if start and end and start >= end:
        raise AppError(400, "VALIDATION_ERROR", "结束时间必须晚于开始时间")
    return svc(request).log_query(keyword, action, start, end)


@router.get("/logs")
def list_logs(
    request: Request,
    keyword: str = Query("", max_length=64),
    action: str = Query("", max_length=64),
    start: datetime | None = None,
    end: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current=Depends(guard("system:logs")),
):
    return respond(
        request,
        svc(request).log_list(log_query(request, keyword, action, start, end), page, page_size),
    )


@router.get("/logs/{log_id}")
def log_detail(log_id: int, request: Request, current=Depends(guard("system:logs"))):
    with request.app.state.connections.engine.connect() as db:
        row = (
            db.execute(select(admin_operation_log).where(admin_operation_log.c.id == log_id))
            .mappings()
            .first()
        )
    if not row:
        raise AppError(404, "NOT_FOUND", "日志不存在")
    return respond(request, dict(row))


@router.post("/log-exports")
def export_logs(
    request: Request,
    keyword: str = Query("", max_length=64),
    action: str = Query("", max_length=64),
    start: datetime | None = None,
    end: datetime | None = None,
    current=Depends(guard("system:export")),
):
    content = svc(request).export_logs(
        current, context(request), log_query(request, keyword, action, start, end)
    )
    return Response(
        content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="operation-logs.csv"'},
    )


@router.get("/settings")
def get_settings(request: Request, current=Depends(guard("system:settings"))):
    return respond(request, svc(request).get_settings())


@router.put("/settings")
def save_settings(body: SettingsInput, request: Request, current=Depends(guard("system:settings"))):
    return respond(
        request, svc(request).save_settings(current, context(request), body.model_dump())
    )


@router.post("/files")
async def upload_image(request: Request, current=Depends(guard("system:settings"))):
    from starlette.concurrency import run_in_threadpool

    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content) > 2 * 1024 * 1024:
            raise AppError(400, "VALIDATION_ERROR", "图片不能超过2MB")

    def store():
        try:
            with Image.open(io.BytesIO(content)) as image:
                if (
                    image.format not in {"PNG", "JPEG", "WEBP"}
                    or max(image.size) > 2048
                    or min(image.size) < 1
                ):
                    raise AppError(400, "VALIDATION_ERROR", "仅支持最大2048像素的PNG/JPEG/WebP图片")
                image.load()
                output = io.BytesIO()
                image.convert("RGBA").save(output, format="PNG")
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            raise AppError(400, "VALIDATION_ERROR", "图片文件无效") from None
        data = output.getvalue()
        if len(data) > 4 * 1024 * 1024:
            raise AppError(400, "VALIDATION_ERROR", "转换后的图片过大，请压缩后重试")
        key = f"platform/{uuid4().hex}.png"
        connections = request.app.state.connections
        bucket = request.app.state.settings.minio_bucket
        try:
            connections.minio.put_object(
                bucket, key, io.BytesIO(data), len(data), content_type="image/png"
            )
        except Exception:
            raise AppError(503, "STORAGE_UNAVAILABLE", "图片存储暂不可用，请稍后重试") from None
        try:
            with svc(request).writing(current, "system:settings") as db:
                file_id = db.execute(
                    insert(stored_file).values(
                        object_key=key,
                        content_type="image/png",
                        size_bytes=len(data),
                        created_at=utc_now(),
                    )
                ).inserted_primary_key[0]
                audit(db, current, "file.upload", f"平台图片:{file_id}", context(request))
        except Exception:
            try:
                connections.minio.remove_object(bucket, key)
            except Exception:
                pass
            raise
        return {"id": file_id}

    return respond(request, await run_in_threadpool(store), status=201)


def image_response(request, file_id, public=False):
    with request.app.state.connections.engine.connect() as db:
        row = db.execute(select(stored_file).where(stored_file.c.id == file_id)).mappings().first()
        if public:
            visible = db.execute(
                select(platform_settings.c.id).where(
                    or_(
                        platform_settings.c.logo_file_id == file_id,
                        platform_settings.c.avatar_file_id == file_id,
                    )
                )
            ).first()
            if not visible:
                row = None
    if not row:
        raise AppError(404, "NOT_FOUND", "图片不存在")
    resource = None
    try:
        resource = request.app.state.connections.minio.get_object(
            request.app.state.settings.minio_bucket, row["object_key"]
        )
        data = resource.read(4 * 1024 * 1024 + 1)
        if len(data) > 4 * 1024 * 1024:
            raise RuntimeError("invalid image size")
        return Response(data, media_type="image/png", headers={"X-Content-Type-Options": "nosniff"})
    except Exception:
        raise AppError(503, "STORAGE_UNAVAILABLE", "图片暂不可用") from None
    finally:
        if resource:
            resource.close()
            resource.release_conn()


@router.get("/files/{file_id}")
def admin_image(file_id: int, request: Request, current=Depends(guard("system:settings"))):
    return image_response(request, file_id)


@public_router.get("/settings")
def public_settings(request: Request):
    values = svc(request).get_settings()
    return respond(
        request,
        {key: values[key] for key in ["name", "description", "logo_file_id", "avatar_file_id"]},
    )


@public_router.get("/files/{file_id}")
def public_image(file_id: int, request: Request):
    return image_response(request, file_id, public=True)
