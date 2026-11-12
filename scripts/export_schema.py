"""Export current MySQL metadata. Does not connect to a DB or rewrite old migrations.

Run from project root: backend/.venv/bin/python scripts/export_schema.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy.dialects import mysql  # noqa: E402
from sqlalchemy.schema import CreateIndex, CreateTable  # noqa: E402

from app.infrastructure.models import Base  # noqa: E402

header = (
    "-- 云枢智学 MySQL 8.4 初始结构；禁止物理外键；仅在空库通过 Alembic 初始化。\n"
    "-- 基于 SQLAlchemy metadata；UTC DATETIME(6)，数据库连接时区设为 +00:00。\n"
    "-- active_guard 等为实现软删除唯一约束的派生列，不供 API 写入。\n\n"
)
statements = [header]
for table in Base.metadata.sorted_tables:
    statements.append(str(CreateTable(table).compile(dialect=mysql.dialect())).strip() + ";\n\n")
    for index in sorted(table.indexes, key=lambda item: item.name):
        statements.append(str(CreateIndex(index).compile(dialect=mysql.dialect())).strip() + ";\n")
    statements.append("\n")
(ROOT / "scripts/sql/schema.sql").write_text("".join(statements))
print(f"Exported {len(Base.metadata.tables)} tables; historical migrations unchanged.")
