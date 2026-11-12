"""System administration; preserve all existing accounts and sessions."""

from datetime import datetime, timezone
from pathlib import Path

import sqlparse
from alembic import op
from sqlalchemy import text

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# Frozen seed contract; subsequent changes require a new migration.
GROUPS = {
    "dashboard": "view",
    "subject": "view create edit delete",
    "course": "view create edit delete",
    "question": "view create edit delete import export review",
    "kb": "view upload edit delete search",
    "route": "view create edit delete",
    "student": "view edit delete",
    "user": "view create edit disable delete reset",
    "system": "roles logs export settings",
}


def upgrade():
    db = op.get_bind()
    for statement in sqlparse.split(Path(__file__).with_name("0002_system.sql").read_text()):
        op.execute(statement)
    op.execute("""ALTER TABLE admin_user
        DROP INDEX uq_admin_single_active, DROP COLUMN active_guard,
        ADD COLUMN phone VARCHAR(32) NOT NULL DEFAULT '',
        ADD COLUMN email VARCHAR(254) NOT NULL DEFAULT '',
        ADD COLUMN role_id BIGINT NULL,
        ADD COLUMN is_super INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN enabled INTEGER NOT NULL DEFAULT 1,
        ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN version INTEGER NOT NULL DEFAULT 1,
        ADD COLUMN last_login_at DATETIME(6) NULL,
        ADD CONSTRAINT ck_admin_flags CHECK (enabled IN (0,1) AND is_super IN (0,1) AND must_change_password IN (0,1))""")  # noqa: E501
    op.execute("ALTER TABLE admin_session ADD COLUMN restricted INTEGER NOT NULL DEFAULT 0")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    permissions = {
        f"{group}:{action}" for group, actions in GROUPS.items() for action in actions.split()
    }
    roles = [
        ("super_admin", "超级管理员", "内置唯一超级管理员", permissions),
        (
            "content_reviewer",
            "内容审核",
            "查看内容与审核题目",
            {p for p in permissions if p.endswith(":view") and not p.startswith("user:")}
            | {"question:review"},
        ),
        (
            "operator",
            "运营人员",
            "内容维护与学员管理，不含审核和系统管理",
            {
                p
                for p in permissions
                if not p.startswith(("user:", "system:")) and p != "question:review"
            },
        ),
    ]
    for code, name, description, perms in roles:
        result = db.execute(
            text(
                "INSERT INTO admin_role (code,name,description,built_in,version,created_at,updated_at) VALUES (:code,:name,:description,1,1,:now,:now)"  # noqa: E501
            ),
            dict(code=code, name=name, description=description, now=now),
        )
        role_id = result.lastrowid
        for permission in sorted(perms):
            db.execute(
                text("INSERT INTO admin_role_permission(role_id,permission) VALUES (:id,:p)"),
                dict(id=role_id, p=permission),
            )
        if code == "super_admin":
            db.execute(
                text("UPDATE admin_user SET role_id=:id WHERE role_id IS NULL"), dict(id=role_id)
            )
    # The previous schema permits at most one undeleted administrator.
    op.execute("UPDATE admin_user SET is_super=1 WHERE deleted_at IS NULL")
    op.execute(
        "ALTER TABLE admin_user ADD COLUMN active_guard INTEGER GENERATED ALWAYS AS (CASE WHEN is_super=1 THEN 1 ELSE NULL END) STORED, ADD UNIQUE INDEX uq_admin_single_active(active_guard)"  # noqa: E501
    )
    db.execute(
        text(
            "INSERT INTO platform_settings(id,name,description,version,updated_at) VALUES(1,'云枢智学','让学习更有章法，让成长清晰可见。',1,:now)"  # noqa: E501
        ),
        dict(now=now),
    )


def downgrade():
    raise RuntimeError("系统管理迁移涉及账号与审计数据，禁止自动删除；请按备份恢复方案回退。")
