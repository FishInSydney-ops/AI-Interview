from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import Query, Request
from fastapi.testclient import TestClient
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.common.responses import respond, utc_iso
from app.entry.config import Settings
from app.entry.main import create_app
from app.infrastructure.models import Base


@pytest.fixture
def client(monkeypatch):
    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def execute(self, _statement):
            return SimpleNamespace(scalar_one=lambda: 1)

    resources = SimpleNamespace(
        engine=SimpleNamespace(connect=Connection),
        redis=SimpleNamespace(ping=lambda: True),
        minio=SimpleNamespace(bucket_exists=lambda _bucket: True),
        close=lambda: None,
    )
    monkeypatch.setattr("app.entry.main.Connections", lambda _settings: resources)
    app = create_app(
        Settings(
            _env_file=None,
            mysql_password="test-only",
            minio_access_key="test-only",
            minio_secret_key="test-only",
        )
    )

    @app.get("/test/validation")
    def validation(request: Request, count: int = Query(ge=1)):
        return respond(request, {"count": count})

    @app.get("/test/error")
    def error():
        raise RuntimeError("password=do-not-leak")

    with TestClient(app) as test_client:
        yield test_client, resources


def test_health_and_request_id(client):
    response = client[0].get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "OK"
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert response.headers["Cache-Control"] == "no-store"


def test_readiness_checks_bucket_and_reports_failure(client):
    test_client, resources = client
    assert test_client.get("/api/v1/ready").json()["data"]["status"] == "ready"
    resources.minio.bucket_exists = lambda _bucket: False
    response = test_client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json()["data"]["services"]["minio"] == "unavailable"
    assert response.json()["code"] == "SERVICE_UNAVAILABLE"


def test_error_contract_and_no_secret_leaks(client):
    test_client, _ = client
    response = test_client.get("/test/validation?count=0")
    assert response.status_code == 400
    assert response.json()["details"][0]["field"] == "query.count"
    assert "input" not in response.json()["details"][0]
    assert test_client.get("/missing").json()["code"] == "NOT_FOUND"
    response = test_client.get("/test/error")
    assert response.status_code == 500
    assert "do-not-leak" not in response.text


def test_schema_has_logical_references_only_and_compiles_for_mysql():
    assert len(Base.metadata.tables) == 30
    for table in Base.metadata.tables.values():
        assert not table.foreign_keys
        assert "AUTO_INCREMENT" in str(CreateTable(table).compile(dialect=mysql.dialect()))
    session = Base.metadata.tables["practice_session"]
    assert session.c.in_progress_guard.computed is not None
    unique_index = next(i for i in session.indexes if i.name.endswith("in_progress"))
    assert unique_index.unique
    assert "WHERE" not in str(CreateIndex(unique_index).compile(dialect=mysql.dialect()))


def test_initial_schema_snapshot_remains_frozen():
    import hashlib

    root = Path(__file__).resolve().parents[2]
    snapshot = root / "backend/migrations/versions/0001_schema.sql"
    assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == (
        "451c49400ef21fa845d31ea3990cc74e1d01fe5529911e86191706468c76adaa"
    )
    current = (root / "scripts/sql/schema.sql").read_text()
    for name in Base.metadata.tables:
        assert f"CREATE TABLE {name} (" in current


def test_datetime_serialization_always_uses_utc_z():
    value = datetime(2026, 11, 9, 8, tzinfo=timezone(timedelta(hours=8)))
    assert utc_iso(value) == "2026-11-09T00:00:00.000000Z"
    assert utc_iso(datetime(2026, 11, 9)) == "2026-11-09T00:00:00.000000Z"
