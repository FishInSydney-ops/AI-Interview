from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.common.errors import AppError
from app.entry.config import Settings
from app.entry.main import create_app
from app.modules.admin_auth.security import COOKIE_PATH

ORIGIN = {"Origin": "http://127.0.0.1:5174", "X-Requested-With": "XMLHttpRequest"}


def test_admin_http_contract_cookies_and_csrf(monkeypatch):
    class Service:
        def __init__(self, _engine):
            pass

        def record_login_request(self, _peer):
            pass

        def login(self, username, password, _old, **kwargs):
            from datetime import datetime

            if username != "test" or password != "test-password":
                raise AppError(401, "INVALID_CREDENTIALS", "账号或密码错误")
            return "test-session", datetime(2030, 1, 1)

        def current_session(self, token):
            if token != "test-session":
                raise AppError(401, "AUTH_REQUIRED", "请登录")
            from datetime import datetime

            return {
                "admin_user_id": 1,
                "username": "test",
                "expires_at": datetime(2030, 1, 1),
                "is_super": True,
                "must_change_password": False,
                "permissions": [],
            }

        def logout(self, token, **kwargs):
            self.current_session(token)

    resources = SimpleNamespace(engine=object(), close=lambda: None)
    monkeypatch.setattr("app.entry.main.Connections", lambda _settings: resources)
    monkeypatch.setattr("app.entry.main.AdminAuthService", Service)
    monkeypatch.setattr("app.modules.admin_auth.router.AdminAuthService", Service)
    app = create_app(
        Settings(
            _env_file=None,
            mysql_password="test-only",
            minio_access_key="test-only",
            minio_secret_key="test-only",
        )
    )
    with TestClient(app) as client:
        assert client.get("/api/v1/admin/auth/session").status_code == 401
        credentials = {"username": "test", "password": "test-password"}
        assert client.post("/api/v1/admin/auth/sessions", json=credentials).status_code == 403
        response = client.post("/api/v1/admin/auth/sessions", json=credentials, headers=ORIGIN)
        assert response.status_code == 200
        cookie = response.headers["set-cookie"]
        assert "HttpOnly" in cookie and "SameSite=strict" in cookie
        assert f"Path={COOKIE_PATH}" in cookie
        assert "test-session" not in response.text
        assert client.get("/api/v1/admin/auth/session").json()["data"]["username"] == "test"
        response = client.delete("/api/v1/admin/auth/session", headers=ORIGIN)
        assert response.status_code == 200
        assert "Max-Age=0" in response.headers["set-cookie"]
