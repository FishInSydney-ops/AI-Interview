from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: str
    message: str
    data: T
    request_id: str


class HealthData(BaseModel):
    status: Literal["ok"]
    version: str


class ReadinessData(BaseModel):
    status: Literal["ready", "degraded"]
    services: dict[str, Literal["ok", "unavailable"]]
