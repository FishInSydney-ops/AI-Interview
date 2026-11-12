"""Local setup utilities. Never prints credentials or overwrites an existing .env."""

import argparse
import getpass
import os

from dotenv import dotenv_values

from app.entry.config import BACKEND_DIR


def configure():
    target = BACKEND_DIR / ".env"
    if target.exists():
        print("backend/.env 已存在，未覆盖。")
        return
    source = BACKEND_DIR.parent / "docker/local/.env"
    values = dotenv_values(source, interpolate=False)
    required = ("MYSQL_PASSWORD", "MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD")
    if any(not values.get(key) for key in required):
        raise SystemExit("请先配置 docker/local/.env 的数据库和 MinIO 凭据。")
    config = {
        "APP_ENV": "development",
        "MYSQL_HOST": "127.0.0.1",
        "MYSQL_PORT": values.get("MYSQL_PORT") or "3306",
        "MYSQL_DATABASE": values.get("MYSQL_DATABASE") or "yunshu",
        "MYSQL_USER": values.get("MYSQL_USER") or "yunshu",
        "MYSQL_PASSWORD": values["MYSQL_PASSWORD"],
        "REDIS_URL": f"redis://127.0.0.1:{values.get('REDIS_PORT') or '6379'}/0",
        "MINIO_ENDPOINT": f"127.0.0.1:{values.get('MINIO_API_PORT') or '9000'}",
        "MINIO_ACCESS_KEY": values["MINIO_ROOT_USER"],
        "MINIO_SECRET_KEY": values["MINIO_ROOT_PASSWORD"],
        "MINIO_BUCKET": "yszx-files",
        "MINIO_SECURE": "false",
    }

    def quote(value):
        return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"

    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write("\n".join(f"{key}={quote(value)}" for key, value in config.items()) + "\n")
    print("已创建 backend/.env，已读取本地 Docker 配置；未输出凭据。")


def create_admin():
    from sqlalchemy import insert, select
    from sqlalchemy.exc import IntegrityError

    from app.entry.config import Settings
    from app.infrastructure.connections import Connections
    from app.infrastructure.models import admin_role, admin_user
    from app.modules.admin_auth.security import PASSWORD_HASHER, utc_now

    connections = Connections(Settings())
    try:
        with connections.engine.connect() as db:
            if db.execute(select(admin_user.c.id).where(admin_user.c.deleted_at.is_(None))).first():
                raise SystemExit("已有有效管理员，不会覆盖其账号或密码。")
        username = input("管理员用户名 [admin]: ").strip() or "admin"
        if len(username) > 64 or not username.strip():
            raise SystemExit("用户名须为1–64个字符。")
        password = getpass.getpass("管理员密码（8–128个字符，输入不回显）: ")
        if not 8 <= len(password) <= 128:
            raise SystemExit("密码长度须为8–128个字符。")
        if password != getpass.getpass("再次输入密码: "):
            raise SystemExit("两次密码不一致，未创建账号。")
        now = utc_now()
        try:
            with connections.engine.begin() as db:
                db.execute(
                    insert(admin_user).values(
                        username=username,
                        is_super=1,
                        role_id=db.execute(
                            select(admin_role.c.id).where(admin_role.c.code == "super_admin")
                        ).scalar_one(),
                        password_hash=PASSWORD_HASHER.hash(password),
                        created_at=now,
                        updated_at=now,
                    )
                )
        except IntegrityError:
            raise SystemExit("管理员已存在或用户名冲突，未覆盖已有账号。") from None
        print("管理员创建成功，请使用刚设置的账号密码登录。")
    finally:
        connections.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["configure", "create-admin"])
    args = parser.parse_args()
    if args.command == "configure":
        configure()
    else:
        create_admin()
