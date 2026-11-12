"""Initial MySQL schema, frozen snapshot. No seed users or business data."""

from pathlib import Path

import sqlparse
from alembic import op
from sqlalchemy import inspect

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    existing = set(inspect(connection).get_table_names()) - {"alembic_version"}
    if existing:
        raise RuntimeError("初始迁移仅支持空数据库；检测到现有表，已停止。")
    schema = Path(__file__).with_name("0001_schema.sql").read_text()
    for statement in sqlparse.split(schema):
        op.execute(statement)


def downgrade():
    raise RuntimeError("初始迁移不自动删除业务表；如需回滚请先备份并制定数据保留方案。")
