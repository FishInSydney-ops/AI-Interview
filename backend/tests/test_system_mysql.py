import os

import pytest
from sqlalchemy import insert, select
from test_admin_auth_mysql import CREDENTIALS, ORIGIN, api, resources  # noqa: F401

from app.infrastructure.models import (
    admin_operation_log,
    admin_role,
    admin_role_permission,
    admin_user,
    platform_settings,
)
from app.modules.admin_auth.security import utc_now

pytestmark = pytest.mark.skipif(not os.environ.get("MYSQL_TEST_DATABASE"), reason="需要独立数据库")


def test_system_permissions_reset_and_audit(api):  # noqa: F811
    client, engine = api
    now = utc_now()
    with engine.begin() as db:
        rid = db.execute(
            insert(admin_role).values(
                name="测试角色", code="test_role", created_at=now, updated_at=now
            )
        ).inserted_primary_key[0]
        db.execute(insert(admin_role_permission).values(role_id=rid, permission="dashboard:view"))
        db.execute(admin_user.update().values(is_super=1))
        db.execute(insert(platform_settings).values(id=1, name="测试平台", updated_at=now))
    assert (
        client.post("/api/v1/admin/auth/sessions", json=CREDENTIALS, headers=ORIGIN).status_code
        == 200
    )
    prefix = "/api/v1/admin/system/"
    result = client.post(
        prefix + "users",
        headers=ORIGIN,
        json=dict(
            username="tester",
            phone="13800000000",
            email="",
            role_id=rid,
            enabled=True,
            password="InitialPass!2026",
        ),
    )
    assert result.status_code == 201, result.text
    uid = result.json()["data"]["id"]
    assert (
        client.post(
            prefix + "user-batches",
            headers=ORIGIN,
            json={"ids": [uid, 999999], "action": "disable"},
        ).status_code
        == 404
    )
    detail = client.get(prefix + f"users/{uid}").json()["data"]
    assert detail["enabled"] == 1
    reset = client.post(prefix + f"users/{uid}/password-resets", headers=ORIGIN)
    assert reset.status_code == 200, reset.text
    temporary = reset.json()["data"]["temporary_password"]
    client.delete("/api/v1/admin/auth/session", headers=ORIGIN)
    assert (
        client.post(
            "/api/v1/admin/auth/sessions",
            headers=ORIGIN,
            json={"username": "tester", "password": temporary},
        ).status_code
        == 200
    )
    assert client.get(prefix + "users").status_code == 403
    assert (
        client.post(
            "/api/v1/admin/auth/password", headers=ORIGIN, json={"new_password": "ChangedPass!2026"}
        ).status_code
        == 200
    )
    assert client.get(prefix + "roles").status_code == 403
    assert client.get("/api/v1/admin/auth/session").json()["data"]["must_change_password"] is False
    assert (
        client.post(
            "/api/v1/admin/auth/sessions",
            headers=ORIGIN,
            json={"username": "tester", "password": temporary},
        ).status_code
        == 401
    )
    with engine.connect() as db:
        contents = str(db.execute(select(admin_operation_log)).all())
        assert temporary not in contents and "InitialPass!2026" not in contents
