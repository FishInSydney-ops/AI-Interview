from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def respond(
    request: Request,
    data: Any = None,
    *,
    status: int = 200,
    code: str = "OK",
    message: str = "成功",
    details: list[dict[str, str]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = {
        "code": code,
        "message": message,
        "data": data,
        "request_id": request.state.request_id,
    }
    if details is not None:
        body["details"] = details
    return JSONResponse(
        jsonable_encoder(body, custom_encoder={datetime: utc_iso}),
        status_code=status,
        headers=headers,
    )


def utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
