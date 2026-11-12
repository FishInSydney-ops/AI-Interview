from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    app_name: str = "云枢智学 API"
    app_env: str = "development"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "yunshu"
    mysql_user: str = "yunshu"
    mysql_password: SecretStr
    redis_url: SecretStr = SecretStr("redis://127.0.0.1:6379/0")
    minio_endpoint: str = "127.0.0.1:9000"
    minio_access_key: SecretStr
    minio_secret_key: SecretStr
    minio_bucket: str = "yszx-files"
    minio_secure: bool = False

    admin_cookie_name: str = "yszx_admin_session"
    admin_cookie_secure: bool = False
    admin_allowed_origins: list[str] = [
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
