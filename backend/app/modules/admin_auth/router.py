from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from app.common.responses import respond
from app.common.schemas import ApiResponse
from app.modules.admin_auth.security import COOKIE_PATH
from app.modules.admin_auth.service import AdminAuthService

router = APIRouter(prefix="/api/v1/admin/auth", tags=["管理端认证"])


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class PasswordInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    new_password: str = Field(min_length=8, max_length=128)
    current_password: str | None = Field(default=None, max_length=128)


class LoginData(BaseModel):
    expires_at: datetime


class SessionData(LoginData):
    id: int
    username: str
    is_super: bool
    must_change_password: bool
    permissions: list[str]


def service(request):
    return AdminAuthService(request.app.state.connections.engine)


def context(request):
    return {
        "ip": request.client.host if request.client else "unknown",
        "request_id": request.state.request_id,
    }


def set_cookie(response, request, token, expires):
    now = datetime.now(timezone.utc)
    expiry = expires.replace(tzinfo=timezone.utc)
    response.set_cookie(
        request.app.state.settings.admin_cookie_name,
        token,
        max_age=max(0, int((expiry - now).total_seconds())),
        expires=expiry,
        httponly=True,
        secure=request.app.state.settings.admin_cookie_secure,
        samesite="strict",
        path=COOKIE_PATH,
    )


@router.post("/sessions", response_model=ApiResponse[LoginData])
def login(body: LoginInput, request: Request):
    token, expires = service(request).login(
        body.username,
        body.password,
        request.cookies.get(request.app.state.settings.admin_cookie_name),
        context=context(request),
    )
    response = respond(request, {"expires_at": expires})
    set_cookie(response, request, token, expires)
    return response


@router.get("/session", response_model=ApiResponse[SessionData])
def session(request: Request):
    current = service(request).current_session(
        request.cookies.get(request.app.state.settings.admin_cookie_name)
    )
    return respond(
        request,
        {
            "id": current["admin_user_id"],
            "username": current["username"],
            "expires_at": current["expires_at"],
            "is_super": bool(current["is_super"]),
            "must_change_password": current["must_change_password"],
            "permissions": current["permissions"],
        },
    )


@router.delete("/session", response_model=ApiResponse[None])
def logout(request: Request):
    service(request).logout(
        request.cookies.get(request.app.state.settings.admin_cookie_name), context=context(request)
    )
    response = respond(request)
    response.delete_cookie(
        request.app.state.settings.admin_cookie_name,
        path=COOKIE_PATH,
        httponly=True,
        secure=request.app.state.settings.admin_cookie_secure,
        samesite="strict",
    )
    return response


@router.post("/password", response_model=ApiResponse[LoginData])
def password(body: PasswordInput, request: Request):
    token, expires = service(request).change_password(
        request.cookies.get(request.app.state.settings.admin_cookie_name),
        body.new_password,
        body.current_password,
        context(request),
    )
    response = respond(request, {"expires_at": expires})
    set_cookie(response, request, token, expires)
    return response
