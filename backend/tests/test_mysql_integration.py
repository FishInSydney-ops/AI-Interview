"""Opt-in tests; refuse databases other than a separately created yunshu_test_* database."""

import os
from datetime import datetime

import pytest
from sqlalchemy import insert, update
from sqlalchemy.exc import IntegrityError

from app.entry.config import Settings
from app.infrastructure.connections import Connections
from app.infrastructure.models import Base, course, practice_session, student, subject

pytestmark = pytest.mark.skipif(
    not os.environ.get("MYSQL_TEST_DATABASE"), reason="需要独立 MYSQL_TEST_DATABASE"
)
NOW = datetime(2026, 11, 9, 0, 0)


@pytest.fixture(scope="module")
def resources():
    name = os.environ["MYSQL_TEST_DATABASE"]
    if not name.startswith("yunshu_test_") or not name.replace("_", "").isalnum():
        raise RuntimeError("仅允许独立的 yunshu_test_* 数据库")
    settings = Settings().model_copy(update={"mysql_database": name})
    connections = Connections(settings)
    Base.metadata.create_all(connections.engine)
    try:
        yield connections
    finally:
        Base.metadata.drop_all(connections.engine)
        connections.close()


@pytest.fixture
def db(resources):
    with resources.engine.connect() as connection:
        tx = connection.begin()
        try:
            yield connection
        finally:
            tx.rollback()


def test_deleted_username_stays_reserved_but_subject_name_can_be_reused(db):
    db.execute(
        insert(student).values(
            username="reserved",
            password_hash="test",
            created_at=NOW,
            updated_at=NOW,
            deleted_at=NOW,
        )
    )
    with pytest.raises(IntegrityError):
        db.execute(
            insert(student).values(
                username="reserved", password_hash="test", created_at=NOW, updated_at=NOW
            )
        )
    db.execute(insert(subject).values(name="test", created_at=NOW, updated_at=NOW, deleted_at=NOW))
    db.execute(insert(subject).values(name="test", created_at=NOW, updated_at=NOW))
    with pytest.raises(IntegrityError):
        db.execute(insert(subject).values(name="test", created_at=NOW, updated_at=NOW))


def test_only_one_active_practice_across_both_types(db):
    first = db.execute(
        insert(practice_session).values(
            student_id=1,
            session_type="stage",
            stage_id=1,
            status="in_progress",
            question_count=1,
            started_at=NOW,
        )
    ).inserted_primary_key[0]
    new = dict(
        student_id=1, session_type="mistake", status="in_progress", question_count=1, started_at=NOW
    )
    with pytest.raises(IntegrityError):
        db.execute(insert(practice_session).values(**new))
    db.execute(
        update(practice_session).where(practice_session.c.id == first).values(status="abandoned")
    )
    db.execute(insert(practice_session).values(**new))


def test_url_uniqueness_uses_full_string_and_soft_deletion(db):
    values = dict(
        stage_id=1,
        title="test",
        total_episodes=1,
        status="published",
        created_at=NOW,
        updated_at=NOW,
    )
    db.execute(insert(course).values(**values, course_url="https://example.test/video?p=1"))
    db.execute(insert(course).values(**values, course_url="https://example.test/video?p=2"))
    with pytest.raises(IntegrityError):
        db.execute(insert(course).values(**values, course_url="https://example.test/video?p=1"))
    db.execute(
        update(course)
        .where(course.c.course_url == "https://example.test/video?p=1")
        .values(deleted_at=NOW)
    )
    db.execute(insert(course).values(**values, course_url="https://example.test/video?p=1"))
