"""MySQL 8.4 metadata. Logical references only; no physical foreign keys."""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Computed,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


student = Table(
    "student",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("username", String(64), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("nickname", String(128), nullable=True),
    Column("avatar_path", String(1024), nullable=True),
    Column("onboarding_completed_at", DATETIME(fsp=6), nullable=True),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    CheckConstraint("length(trim(username)) > 0"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

student_password_reset = Table(
    "student_password_reset",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("student_id", BigInteger, nullable=False),
    Column("temporary_password_hash", String(255), nullable=False),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("consumed_at", DATETIME(fsp=6), nullable=True),
    Column("revoked_at", DATETIME(fsp=6), nullable=True),
    Column(
        "pending_guard",
        Integer,
        Computed(
            "CASE WHEN consumed_at IS NULL AND revoked_at IS NULL THEN 1 ELSE NULL END",
            persisted=True,
        ),
    ),
    CheckConstraint("consumed_at IS NULL OR revoked_at IS NULL"),
    Index("uq_student_reset_pending", "student_id", "pending_guard", unique=True),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

student_session = Table(
    "student_session",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("student_id", BigInteger, nullable=False),
    Column("session_token_hash", String(64), nullable=False, unique=True),
    Column("session_purpose", String(32), nullable=False),
    Column("password_reset_id", BigInteger, nullable=True),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("expires_at", DATETIME(fsp=6), nullable=False),
    Column("revoked_at", DATETIME(fsp=6), nullable=True),
    CheckConstraint("length(session_token_hash) > 0"),
    CheckConstraint("session_purpose IN ('normal', 'password_reset')"),
    CheckConstraint(
        "(session_purpose = 'password_reset' AND password_reset_id IS NOT NULL) "
        "OR (session_purpose = 'normal' AND password_reset_id IS NULL)"
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

ADMIN_OPTIONS = dict(
    mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_0900_bin"
)

admin_role = Table(
    "admin_role",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("name", String(64), nullable=False, unique=True),
    Column("code", String(64), nullable=False, unique=True),
    Column("description", String(500), nullable=False, server_default=""),
    Column("built_in", Integer, nullable=False, server_default="0"),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    **ADMIN_OPTIONS,
)
admin_role_permission = Table(
    "admin_role_permission",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("role_id", BigInteger, nullable=False),
    Column("permission", String(64), nullable=False),
    UniqueConstraint("role_id", "permission"),
    **ADMIN_OPTIONS,
)
admin_user = Table(
    "admin_user",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("username", String(64), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("phone", String(32), nullable=False, server_default=""),
    Column("email", String(254), nullable=False, server_default=""),
    Column("role_id", BigInteger, nullable=True),
    Column("is_super", Integer, nullable=False, server_default="0"),
    Column("enabled", Integer, nullable=False, server_default="1"),
    Column("must_change_password", Integer, nullable=False, server_default="0"),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("last_login_at", DATETIME(fsp=6), nullable=True),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    Column(
        "active_guard",
        Integer,
        Computed("CASE WHEN is_super = 1 THEN 1 ELSE NULL END", persisted=True),
    ),
    CheckConstraint("length(trim(username)) > 0"),
    CheckConstraint("enabled IN (0,1) AND is_super IN (0,1) AND must_change_password IN (0,1)"),
    Index("uq_admin_single_active", "active_guard", unique=True),
    **ADMIN_OPTIONS,
)
admin_session = Table(
    "admin_session",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("admin_user_id", BigInteger, nullable=False),
    Column("session_token_hash", String(64), nullable=False, unique=True),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("expires_at", DATETIME(fsp=6), nullable=False),
    Column("revoked_at", DATETIME(fsp=6), nullable=True),
    Column("restricted", Integer, nullable=False, server_default="0"),
    CheckConstraint("length(session_token_hash) > 0"),
    **ADMIN_OPTIONS,
)
admin_password_reset = Table(
    "admin_password_reset",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("admin_user_id", BigInteger, nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("expires_at", DATETIME(fsp=6), nullable=False),
    Column("consumed_at", DATETIME(fsp=6), nullable=True),
    **ADMIN_OPTIONS,
)
admin_operation_log = Table(
    "admin_operation_log",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("actor_id", BigInteger, nullable=True),
    Column("actor_name", String(64), nullable=False),
    Column("action", String(64), nullable=False),
    Column("target", String(255), nullable=False),
    Column("ip", String(128), nullable=False),
    Column("outcome", String(32), nullable=False),
    Column("request_id", String(64), nullable=False),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Index("ix_admin_log_time", "created_at", "id"),
    **ADMIN_OPTIONS,
)
stored_file = Table(
    "stored_file",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("object_key", String(255), nullable=False, unique=True),
    Column("content_type", String(64), nullable=False),
    Column("size_bytes", BigInteger, nullable=False),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    **ADMIN_OPTIONS,
)
platform_settings = Table(
    "platform_settings",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("name", String(64), nullable=False),
    Column("description", String(1000), nullable=False, server_default=""),
    Column("logo_file_id", BigInteger, nullable=True),
    Column("avatar_file_id", BigInteger, nullable=True),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    **ADMIN_OPTIONS,
)

login_lock = Table(
    "login_lock",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("account_domain", String(32), nullable=False),
    Column("account_key", String(128), nullable=False),
    Column("failed_count", Integer, nullable=False, server_default=text("0")),
    Column("locked_until", String(32), nullable=True),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    CheckConstraint("account_domain IN ('student', 'admin')"),
    CheckConstraint("length(account_key) > 0"),
    CheckConstraint("failed_count >= 0"),
    UniqueConstraint("account_domain", "account_key"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

rate_limit_counter = Table(
    "rate_limit_counter",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("action", String(64), nullable=False),
    Column("dimension_type", String(32), nullable=False),
    Column("dimension_key", String(128), nullable=False),
    Column("window_start_at", DATETIME(fsp=6), nullable=False),
    Column("expires_at", DATETIME(fsp=6), nullable=False),
    Column("request_count", Integer, nullable=False, server_default=text("0")),
    CheckConstraint("length(action) > 0"),
    CheckConstraint("dimension_type IN ('ip', 'account')"),
    CheckConstraint("length(dimension_key) > 0"),
    CheckConstraint("request_count >= 0"),
    UniqueConstraint("action", "dimension_type", "dimension_key", "window_start_at"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

subject = Table(
    "subject",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("name", String(128), nullable=False),
    Column("icon", String(255), nullable=True),
    Column("description", Text, nullable=True),
    Column("sort_order", Integer, nullable=False, server_default=text("0")),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    Column(
        "active_guard",
        Integer,
        Computed("CASE WHEN deleted_at IS NULL THEN 1 ELSE NULL END", persisted=True),
    ),
    CheckConstraint("length(trim(name)) > 0"),
    Index("uq_subject_name_active", "name", "active_guard", unique=True),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

stage = Table(
    "stage",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("subject_id", BigInteger, nullable=False),
    Column("name", String(128), nullable=False),
    Column("sort_order", Integer, nullable=False, server_default=text("0")),
    Column("is_enabled", Integer, nullable=False, server_default=text("1")),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    Column(
        "active_guard",
        Integer,
        Computed("CASE WHEN deleted_at IS NULL THEN 1 ELSE NULL END", persisted=True),
    ),
    CheckConstraint("length(trim(name)) > 0"),
    CheckConstraint("is_enabled IN (0, 1)"),
    Index("uq_stage_name_active", "subject_id", "name", "active_guard", unique=True),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

content_deletion_batch = Table(
    "content_deletion_batch",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("root_type", String(32), nullable=False),
    Column("root_id", BigInteger, nullable=False),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    CheckConstraint("root_type IN ('subject', 'stage')"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

content_deletion_item = Table(
    "content_deletion_item",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("batch_id", BigInteger, nullable=False),
    Column("entity_type", String(32), nullable=False),
    Column("entity_id", BigInteger, nullable=False),
    Column("restored_at", DATETIME(fsp=6), nullable=True),
    Column(
        "pending_guard",
        Integer,
        Computed("CASE WHEN restored_at IS NULL THEN 1 ELSE NULL END", persisted=True),
    ),
    CheckConstraint(
        "entity_type IN ('subject', 'stage', 'course', 'question', "
        "'learning_route', 'course_subject_link', 'route_course')"
    ),
    UniqueConstraint("batch_id", "entity_type", "entity_id"),
    Index("uq_content_deletion_current", "entity_type", "entity_id", "pending_guard", unique=True),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

course = Table(
    "course",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("stage_id", BigInteger, nullable=False),
    Column("title", String(255), nullable=False),
    Column("course_url", String(2048), nullable=False),
    Column("total_episodes", Integer, nullable=False),
    Column("status", String(32), nullable=False),
    Column("cover_url", String(2048), nullable=True),
    Column("duration_minutes", Integer, nullable=True),
    Column("description", Text, nullable=True),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    Column(
        "active_url_hash",
        String(64),
        Computed(
            "CASE WHEN deleted_at IS NULL THEN SHA2(course_url, 256) ELSE NULL END", persisted=True
        ),
    ),
    CheckConstraint("length(trim(title)) > 0"),
    CheckConstraint("total_episodes > 0"),
    CheckConstraint("status IN ('published', 'unpublished')"),
    CheckConstraint("duration_minutes IS NULL OR duration_minutes >= 0"),
    Index("uq_course_url_active", "active_url_hash", unique=True),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

course_subject_link = Table(
    "course_subject_link",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("course_id", BigInteger, nullable=False),
    Column("subject_id", BigInteger, nullable=False),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    Column(
        "active_guard",
        Integer,
        Computed("CASE WHEN deleted_at IS NULL THEN 1 ELSE NULL END", persisted=True),
    ),
    Index("uq_course_subject_active", "course_id", "subject_id", "active_guard", unique=True),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

learning_route = Table(
    "learning_route",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("subject_id", BigInteger, nullable=False),
    Column("name", String(128), nullable=False),
    Column("description", Text, nullable=True),
    Column("is_enabled", Integer, nullable=False, server_default=text("1")),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    CheckConstraint("length(trim(name)) > 0"),
    CheckConstraint("is_enabled IN (0, 1)"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

route_course = Table(
    "route_course",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("route_id", BigInteger, nullable=False),
    Column("course_id", BigInteger, nullable=False),
    Column("sort_order", Integer, nullable=False),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    Column(
        "active_guard",
        Integer,
        Computed("CASE WHEN deleted_at IS NULL THEN 1 ELSE NULL END", persisted=True),
    ),
    CheckConstraint("sort_order > 0"),
    Index("uq_route_course_active", "route_id", "course_id", "active_guard", unique=True),
    Index("uq_route_order_active", "route_id", "sort_order", "active_guard", unique=True),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

student_episode_completion = Table(
    "student_episode_completion",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("student_id", BigInteger, nullable=False),
    Column("course_id", BigInteger, nullable=False),
    Column("episode_number", Integer, nullable=False),
    Column("completed_at", DATETIME(fsp=6), nullable=False),
    Column("revoked_at", DATETIME(fsp=6), nullable=True),
    CheckConstraint("episode_number > 0"),
    UniqueConstraint("student_id", "course_id", "episode_number"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

question = Table(
    "question",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("stage_id", BigInteger, nullable=False),
    Column("question_type", String(32), nullable=False),
    Column("difficulty", String(32), nullable=False),
    Column("prompt", Text, nullable=False),
    Column("explanation", Text, nullable=True),
    Column("reference_source", String(2048), nullable=True),
    Column("status", String(32), nullable=False),
    Column("answer_revision", Integer, nullable=False, server_default=text("1")),
    Column("last_published_fingerprint", String(128), nullable=True),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    Column("deleted_at", DATETIME(fsp=6), nullable=True),
    CheckConstraint("question_type IN ('single', 'multiple', 'judgment')"),
    CheckConstraint("difficulty IN ('easy', 'medium', 'hard')"),
    CheckConstraint("length(trim(prompt)) > 0"),
    CheckConstraint("status IN ('draft', 'published', 'unpublished')"),
    CheckConstraint("answer_revision >= 1"),
    CheckConstraint("last_published_fingerprint IS NULL OR length(last_published_fingerprint) > 0"),
    CheckConstraint("status <> 'published' OR last_published_fingerprint IS NOT NULL"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

question_option = Table(
    "question_option",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("question_id", BigInteger, nullable=False),
    Column("option_order", Integer, nullable=False),
    Column("content", Text, nullable=False),
    Column("is_correct", Integer, nullable=False),
    CheckConstraint("option_order > 0"),
    CheckConstraint("length(trim(content)) > 0"),
    CheckConstraint("is_correct IN (0, 1)"),
    UniqueConstraint("question_id", "option_order"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

practice_session = Table(
    "practice_session",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("student_id", BigInteger, nullable=False),
    Column("session_type", String(32), nullable=False),
    Column("stage_id", BigInteger, nullable=True),
    Column("status", String(32), nullable=False),
    Column("question_count", Integer, nullable=False),
    Column("started_at", DATETIME(fsp=6), nullable=False),
    Column("completed_at", DATETIME(fsp=6), nullable=True),
    Column(
        "in_progress_guard",
        Integer,
        Computed("CASE WHEN status = 'in_progress' THEN 1 ELSE NULL END", persisted=True),
    ),
    CheckConstraint("session_type IN ('stage', 'mistake')"),
    CheckConstraint("status IN ('in_progress', 'completed', 'abandoned')"),
    CheckConstraint("question_count BETWEEN 0 AND 10"),
    CheckConstraint(
        "(session_type = 'stage' AND stage_id IS NOT NULL) "
        "OR (session_type = 'mistake' AND stage_id IS NULL)"
    ),
    CheckConstraint(
        "(status = 'completed' AND completed_at IS NOT NULL AND question_count > 0) "
        "OR (status <> 'completed' AND completed_at IS NULL)"
    ),
    Index(
        "uq_practice_session_student_in_progress", "student_id", "in_progress_guard", unique=True
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

practice_session_item = Table(
    "practice_session_item",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("session_id", BigInteger, nullable=False),
    Column("question_id", BigInteger, nullable=False),
    Column("question_order", Integer, nullable=False),
    Column("presented_fingerprint", String(128), nullable=True),
    Column("item_status", String(32), nullable=False),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    Column("updated_at", DATETIME(fsp=6), nullable=False),
    CheckConstraint("question_order > 0"),
    CheckConstraint("presented_fingerprint IS NULL OR length(presented_fingerprint) > 0"),
    CheckConstraint("item_status IN ('pending', 'answered', 'removed')"),
    UniqueConstraint("session_id", "question_id"),
    UniqueConstraint("session_id", "question_order"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

practice_answer = Table(
    "practice_answer",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("session_id", BigInteger, nullable=False),
    Column("question_id", BigInteger, nullable=False),
    Column("question_type_snapshot", String(32), nullable=False),
    Column("prompt_snapshot", Text, nullable=False),
    Column("explanation_snapshot", Text, nullable=True),
    Column("is_correct", Integer, nullable=False),
    Column("answered_at", DATETIME(fsp=6), nullable=False),
    CheckConstraint("question_type_snapshot IN ('single', 'multiple', 'judgment')"),
    CheckConstraint("is_correct IN (0, 1)"),
    UniqueConstraint("session_id", "question_id"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

practice_answer_option = Table(
    "practice_answer_option",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("practice_answer_id", BigInteger, nullable=False),
    Column("option_order", Integer, nullable=False),
    Column("content_snapshot", Text, nullable=False),
    Column("is_correct_snapshot", Integer, nullable=False),
    Column("is_selected", Integer, nullable=False),
    CheckConstraint("option_order > 0"),
    CheckConstraint("is_correct_snapshot IN (0, 1)"),
    CheckConstraint("is_selected IN (0, 1)"),
    UniqueConstraint("practice_answer_id", "option_order"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

mistake_record = Table(
    "mistake_record",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("student_id", BigInteger, nullable=False),
    Column("question_id", BigInteger, nullable=False),
    Column("last_wrong_answer_id", BigInteger, nullable=False),
    Column("error_count", Integer, nullable=False),
    Column("consecutive_correct", Integer, nullable=False, server_default=text("0")),
    Column("last_wrong_at", DATETIME(fsp=6), nullable=False),
    Column("removed_at", DATETIME(fsp=6), nullable=True),
    CheckConstraint("error_count > 0"),
    CheckConstraint("consecutive_correct BETWEEN 0 AND 3"),
    UniqueConstraint("student_id", "question_id"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

student_subject_preference = Table(
    "student_subject_preference",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("student_id", BigInteger, nullable=False),
    Column("subject_id", BigInteger, nullable=False),
    Column("created_at", DATETIME(fsp=6), nullable=False),
    UniqueConstraint("student_id", "subject_id"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_0900_bin",
)

Index("ix_student_session_owner", student_session.c.student_id, student_session.c.revoked_at)
Index("ix_admin_session_owner", admin_session.c.admin_user_id, admin_session.c.revoked_at)
Index("ix_rate_limit_expiry", rate_limit_counter.c.expires_at)
Index("ix_stage_subject", stage.c.subject_id, stage.c.sort_order)
Index("ix_course_stage", course.c.stage_id)
Index(
    "ix_course_subject_subject", course_subject_link.c.subject_id, course_subject_link.c.course_id
)
Index("ix_route_subject", learning_route.c.subject_id, learning_route.c.is_enabled)
Index(
    "ix_episode_course_student",
    student_episode_completion.c.course_id,
    student_episode_completion.c.student_id,
)
Index("ix_question_stage_status", question.c.stage_id, question.c.status, question.c.deleted_at)
Index(
    "ix_session_student_completed",
    practice_session.c.student_id,
    practice_session.c.status,
    practice_session.c.completed_at,
)
Index(
    "ix_session_stage",
    practice_session.c.student_id,
    practice_session.c.stage_id,
    practice_session.c.status,
)
Index(
    "ix_session_item_status",
    practice_session_item.c.session_id,
    practice_session_item.c.item_status,
    practice_session_item.c.question_order,
)
Index("ix_answer_question", practice_answer.c.question_id, practice_answer.c.answered_at)
Index(
    "ix_mistake_review",
    mistake_record.c.student_id,
    mistake_record.c.removed_at,
    mistake_record.c.consecutive_correct,
    mistake_record.c.last_wrong_at,
)
