import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, insert, select, update

from app.common.errors import AppError
from app.entry.config import Settings
from app.entry.main import create_app
from app.infrastructure.connections import Connections
from app.infrastructure.models import Base, admin_session, admin_user, rate_limit_counter
from app.modules.admin_auth.security import PASSWORD_HASHER, token_digest, utc_now
from app.modules.admin_auth.service import AdminAuthService

pytestmark = pytest.mark.skipif(
    not os.environ.get("MYSQL_TEST_DATABASE"), reason="需要独立 MYSQL_TEST_DATABASE"
)
ORIGIN = {"Origin": "http://127.0.0.1:5174", "X-Requested-With": "XMLHttpRequest"}
CREDENTIALS = {"username": "auth-test-admin", "password": "LocalTestOnly!2026"}


@pytest.fixture(scope="module")
def resources():
    name = os.environ["MYSQL_TEST_DATABASE"]
    if not name.startswith("yunshu_test_") or not name.replace("_", "").isalnum():
        raise RuntimeError("仅允许独立测试数据库")
    connections = Connections(Settings().model_copy(update={"mysql_database": name}))
    Base.metadata.create_all(connections.engine)
    try:
        yield connections
    finally:
        Base.metadata.drop_all(connections.engine)
        connections.close()


@pytest.fixture
def api(resources, monkeypatch):
    now = utc_now()
    with resources.engine.begin() as db:
        db.execute(delete(admin_session))
        db.execute(delete(admin_user))
        db.execute(delete(rate_limit_counter))
        db.execute(
            insert(admin_user).values(
                username=CREDENTIALS["username"],
                password_hash=PASSWORD_HASHER.hash(CREDENTIALS["password"]),
                created_at=now,
                updated_at=now,
            )
        )
    connection = SimpleNamespace(engine=resources.engine, close=lambda: None)
    monkeypatch.setattr("app.entry.main.Connections", lambda _settings: connection)
    app = create_app(
        Settings(
            _env_file=None,
            mysql_password="test-only",
            minio_access_key="test-only",
            minio_secret_key="test-only",
        )
    )
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        yield client, resources.engine


def test_login_logout_revokes_server_side_session(api):
    client, engine = api
    wrong = client.post(
        "/api/v1/admin/auth/sessions", headers=ORIGIN, json={**CREDENTIALS, "password": "wrong"}
    )
    assert wrong.status_code == 401 and wrong.json()["code"] == "INVALID_CREDENTIALS"
    response = client.post("/api/v1/admin/auth/sessions", json=CREDENTIALS, headers=ORIGIN)
    assert response.status_code == 200
    token = client.cookies.get("yszx_admin_session")
    with engine.connect() as db:
        saved = db.execute(select(admin_session)).mappings().one()
        assert saved["session_token_hash"] == token_digest(token)
        assert saved["session_token_hash"] != token
        assert saved["expires_at"] - saved["created_at"] == timedelta(days=7)
    assert (
        client.get("/api/v1/admin/auth/session").json()["data"]["username"]
        == CREDENTIALS["username"]
    )
    assert client.delete("/api/v1/admin/auth/session", headers=ORIGIN).status_code == 200
    assert (
        client.get(
            "/api/v1/admin/auth/session", headers={"Cookie": f"yszx_admin_session={token}"}
        ).status_code
        == 401
    )
    with engine.connect() as db:
        assert db.execute(select(admin_session.c.revoked_at)).scalar_one() is not None


def test_expired_deleted_and_other_account_domain_rejected(api):
    client, engine = api
    assert (
        client.get(
            "/api/v1/admin/auth/session",
            headers={"Cookie": "yszx_student_session=not-an-admin-token"},
        ).status_code
        == 401
    )
    client.post("/api/v1/admin/auth/sessions", json=CREDENTIALS, headers=ORIGIN)
    with engine.begin() as db:
        db.execute(update(admin_session).values(expires_at=utc_now() - timedelta(seconds=1)))
    response = client.get("/api/v1/admin/auth/session")
    assert response.status_code == 401 and response.json()["code"] == "SESSION_EXPIRED"
    client.post("/api/v1/admin/auth/sessions", json=CREDENTIALS, headers=ORIGIN)
    with engine.begin() as db:
        db.execute(update(admin_user).values(deleted_at=utc_now()))
    assert client.get("/api/v1/admin/auth/session").status_code == 401


def test_invalid_requests_count_and_limit_survives_service_recreation(api):
    client, engine = api
    for _ in range(10):
        assert (
            client.post("/api/v1/admin/auth/sessions", json={}, headers=ORIGIN).status_code == 400
        )
    response = client.post("/api/v1/admin/auth/sessions", json=CREDENTIALS, headers=ORIGIN)
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 300
    with pytest.raises(AppError) as error:
        AdminAuthService(engine).record_login_request("127.0.0.1")
    assert error.value.code == "RATE_LIMITED"


def test_fixed_window_and_parallel_requests(api):
    _, engine = api
    service = AdminAuthService(engine)
    moment = utc_now().replace(minute=0, second=0, microsecond=0)

    def request(_):
        try:
            service.record_login_request("127.0.0.2", moment)
            return True
        except AppError as error:
            assert error.status == 429
            return False

    with ThreadPoolExecutor(max_workers=5) as pool:
        assert sum(pool.map(request, range(20))) == 10
    service.record_login_request("127.0.0.2", moment + timedelta(minutes=5))
    with engine.connect() as db:
        assert sorted(
            db.execute(
                select(rate_limit_counter.c.request_count).where(
                    rate_limit_counter.c.dimension_key == "127.0.0.2"
                )
            )
            .scalars()
            .all()
        ) == [1, 20]


def test_csrf_rejection_does_not_revoke_current_session(api):
    client, _ = api
    client.post("/api/v1/admin/auth/sessions", json=CREDENTIALS, headers=ORIGIN)
    for headers in [{}, {**ORIGIN, "Origin": "https://untrusted.example"}]:
        assert client.delete("/api/v1/admin/auth/session", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/auth/session").status_code == 200


def test_relogin_rotates_and_revokes_previous_browser_token(api):
    client, _ = api
    client.post("/api/v1/admin/auth/sessions", json=CREDENTIALS, headers=ORIGIN)
    first = client.cookies.get("yszx_admin_session")
    client.post("/api/v1/admin/auth/sessions", json=CREDENTIALS, headers=ORIGIN)
    second = client.cookies.get("yszx_admin_session")
    assert first != second
    assert (
        client.get(
            "/api/v1/admin/auth/session", headers={"Cookie": f"yszx_admin_session={first}"}
        ).status_code
        == 401
    )
    assert client.get("/api/v1/admin/auth/session").status_code == 200
