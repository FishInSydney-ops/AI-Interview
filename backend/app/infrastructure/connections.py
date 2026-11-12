from minio import Minio
from redis import Redis
from sqlalchemy import URL, create_engine, event
from sqlalchemy.orm import sessionmaker
from urllib3 import PoolManager
from urllib3.util import Retry, Timeout

from app.entry.config import Settings


class Connections:
    def __init__(self, settings: Settings):
        self.engine = create_engine(
            URL.create(
                "mysql+pymysql",
                username=settings.mysql_user,
                password=settings.mysql_password.get_secret_value(),
                host=settings.mysql_host,
                port=settings.mysql_port,
                database=settings.mysql_database,
                query={"charset": "utf8mb4"},
            ),
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3, "read_timeout": 3, "write_timeout": 3},
        )

        @event.listens_for(self.engine, "connect")
        def configure_utc(dbapi_connection, _record):
            with dbapi_connection.cursor() as cursor:
                cursor.execute("SET time_zone = '+00:00'")

        self.sessions = sessionmaker(self.engine, expire_on_commit=False)
        self.redis = Redis.from_url(
            settings.redis_url.get_secret_value(), socket_timeout=3, socket_connect_timeout=3
        )
        self.http = PoolManager(timeout=Timeout(connect=3, read=3), retries=Retry(total=0))
        self.minio = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key.get_secret_value(),
            secret_key=settings.minio_secret_key.get_secret_value(),
            secure=settings.minio_secure,
            http_client=self.http,
        )

    def close(self):
        self.redis.close()
        self.http.clear()
        self.engine.dispose()
