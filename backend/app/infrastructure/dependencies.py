from collections.abc import Iterator

from fastapi import Request
from minio import Minio
from redis import Redis
from sqlalchemy.orm import Session


def get_session(request: Request) -> Iterator[Session]:
    # 请求关闭时释放连接；业务模块须显式定义事务和提交边界。
    with request.app.state.connections.sessions() as session:
        yield session


def get_cache(request: Request) -> Redis:
    return request.app.state.connections.redis


def get_object_store(request: Request) -> Minio:
    return request.app.state.connections.minio
