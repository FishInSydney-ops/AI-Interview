from alembic import context

from app.entry.config import Settings
from app.infrastructure.connections import Connections
from app.infrastructure.models import Base


def run_migrations_online():
    connections = Connections(Settings())
    try:
        with connections.engine.connect() as connection:
            context.configure(connection=connection, target_metadata=Base.metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connections.close()


if context.is_offline_mode():
    raise RuntimeError("请使用在线迁移，在独立且已备份的目标数据库上执行。")
else:
    run_migrations_online()
