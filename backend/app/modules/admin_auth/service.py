import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.engine import Engine

from app.common.errors import AppError
from app.infrastructure.models import (
    admin_password_reset,
    admin_session,
    admin_user,
    rate_limit_counter,
)
from app.modules.admin_auth.security import (
    DUMMY_HASH,
    PASSWORD_HASHER,
    SESSION_LIFETIME,
    token_digest,
    utc_now,
    verify_password,
)
from app.modules.system.service import audit, permissions

RATE_ACTION = "admin_login"
RATE_LIMIT = 10
WINDOW_SECONDS = 300


class AdminAuthService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def record_login_request(self, peer: str, now: datetime | None = None):
        now = now or utc_now()
        epoch = int(now.replace(tzinfo=timezone.utc).timestamp())
        start = datetime.fromtimestamp(epoch // WINDOW_SECONDS * WINDOW_SECONDS, timezone.utc)
        start = start.replace(tzinfo=None)
        end = start + timedelta(seconds=WINDOW_SECONDS)
        key = and_(
            rate_limit_counter.c.action == RATE_ACTION,
            rate_limit_counter.c.dimension_type == "ip",
            rate_limit_counter.c.dimension_key == peer,
            rate_limit_counter.c.window_start_at == start,
        )
        # 唯一键 upsert 锁住窗口行；计数与读取在同一事务，超限记录也提交。
        with self.engine.begin() as db:
            statement = mysql_insert(rate_limit_counter).values(
                action=RATE_ACTION,
                dimension_type="ip",
                dimension_key=peer,
                window_start_at=start,
                expires_at=end,
                request_count=1,
            )
            db.execute(
                statement.on_duplicate_key_update(
                    request_count=rate_limit_counter.c.request_count + 1
                )
            )
            count = db.execute(select(rate_limit_counter.c.request_count).where(key)).scalar_one()
        if count > RATE_LIMIT:
            remaining = max(1, int((end - now).total_seconds() + 0.999999))
            raise AppError(
                429, "RATE_LIMITED", "登录请求过于频繁，请稍后重试", {"Retry-After": str(remaining)}
            )

    def login(self, username: str, password: str, old_token: str | None = None, context=None):
        with self.engine.connect() as db:
            account = (
                db.execute(
                    select(admin_user).where(
                        admin_user.c.username == username, admin_user.c.deleted_at.is_(None)
                    )
                )
                .mappings()
                .first()
            )
            reset = (
                db.execute(
                    select(admin_password_reset).where(
                        admin_password_reset.c.admin_user_id == account["id"]
                    )
                )
                .mappings()
                .first()
                if account
                else None
            )
        valid = verify_password(account["password_hash"] if account else DUMMY_HASH, password)
        use_reset = False
        if not valid and reset and reset["consumed_at"] is None and reset["expires_at"] > utc_now():
            use_reset = verify_password(reset["password_hash"], password)
            valid = use_reset
        if account is None or not valid or not account["enabled"]:
            raise AppError(401, "INVALID_CREDENTIALS", "账号或密码错误")
        now = utc_now()
        expires = now + SESSION_LIFETIME
        token = secrets.token_urlsafe(32)
        with self.engine.begin() as db:
            # 哈希验证后再次校验账号，避免账号被删除或密码同时变更后仍建立会话。
            current = (
                db.execute(
                    select(admin_user)
                    .where(admin_user.c.id == account["id"], admin_user.c.deleted_at.is_(None))
                    .with_for_update()
                )
                .mappings()
                .first()
            )
            if (
                not current
                or not current["enabled"]
                or current["password_hash"] != account["password_hash"]
            ):
                raise AppError(401, "INVALID_CREDENTIALS", "账号或密码错误")
            restricted = bool(current["must_change_password"] or use_reset)
            if restricted:
                expires = now + timedelta(minutes=15)
            if use_reset:
                current_reset = (
                    db.execute(
                        select(admin_password_reset)
                        .where(admin_password_reset.c.admin_user_id == account["id"])
                        .with_for_update()
                    )
                    .mappings()
                    .first()
                )
                if (
                    not current_reset
                    or current_reset["consumed_at"]
                    or current_reset["expires_at"] <= now
                    or current_reset["password_hash"] != reset["password_hash"]
                ):
                    raise AppError(401, "INVALID_CREDENTIALS", "临时密码已使用或失效")
                db.execute(
                    update(admin_password_reset)
                    .where(admin_password_reset.c.id == current_reset["id"])
                    .values(consumed_at=now)
                )
            if not use_reset and PASSWORD_HASHER.check_needs_rehash(current["password_hash"]):
                db.execute(
                    update(admin_user)
                    .where(admin_user.c.id == account["id"])
                    .values(password_hash=PASSWORD_HASHER.hash(password), updated_at=now)
                )
            if old_token:
                db.execute(
                    update(admin_session)
                    .where(
                        admin_session.c.session_token_hash == token_digest(old_token),
                        admin_session.c.revoked_at.is_(None),
                    )
                    .values(revoked_at=now)
                )
            db.execute(
                insert(admin_session).values(
                    admin_user_id=account["id"],
                    restricted=int(restricted),
                    session_token_hash=token_digest(token),
                    created_at=now,
                    expires_at=expires,
                )
            )
            db.execute(
                update(admin_user).where(admin_user.c.id == account["id"]).values(last_login_at=now)
            )
            audit(
                db,
                {"admin_user_id": account["id"], "username": username},
                "auth.login",
                "管理端登录",
                context or {},
            )
        return token, expires

    def current_session(self, token: str | None):
        if not token or len(token) > 256:
            raise AppError(401, "AUTH_REQUIRED", "请先登录管理后台")
        with self.engine.connect() as db:
            session = (
                db.execute(
                    select(
                        admin_session.c.id,
                        admin_session.c.admin_user_id,
                        admin_session.c.expires_at,
                        admin_user.c.username,
                        admin_user.c.role_id,
                        admin_user.c.is_super,
                        admin_user.c.must_change_password,
                        admin_session.c.restricted,
                    )
                    .join(admin_user, admin_user.c.id == admin_session.c.admin_user_id)
                    .where(
                        admin_session.c.session_token_hash == token_digest(token),
                        admin_session.c.revoked_at.is_(None),
                        admin_user.c.deleted_at.is_(None),
                        admin_user.c.enabled == 1,
                    )
                )
                .mappings()
                .first()
            )
        if not session:
            raise AppError(401, "AUTH_REQUIRED", "登录状态已失效，请重新登录")
        if session["expires_at"] <= utc_now():
            raise AppError(401, "SESSION_EXPIRED", "登录已过期，请重新登录")
        result = dict(session)
        result["must_change_password"] = bool(
            result["must_change_password"] or result["restricted"]
        )
        with self.engine.connect() as db:
            result["permissions"] = (
                [] if result["must_change_password"] else permissions(db, result)
            )
        return result

    def logout(self, token: str, context=None):
        actor = self.current_session(token)
        with self.engine.begin() as db:
            db.execute(
                update(admin_session)
                .where(
                    admin_session.c.session_token_hash == token_digest(token),
                    admin_session.c.revoked_at.is_(None),
                )
                .values(revoked_at=utc_now())
            )

            audit(db, actor, "auth.logout", "管理端退出", context or {})

    def log_login_failure(self, context, outcome):
        with self.engine.begin() as db:
            audit(db, {"username": "未认证"}, "auth.login", "管理端登录失败", context, outcome)

    def change_password(self, token, new_password, current_password, context):
        actor = self.current_session(token)
        encoded = PASSWORD_HASHER.hash(new_password)
        with self.engine.begin() as db:
            account = (
                db.execute(
                    select(admin_user)
                    .where(admin_user.c.id == actor["admin_user_id"])
                    .with_for_update()
                )
                .mappings()
                .one()
            )
            current = (
                db.execute(
                    select(admin_session).where(admin_session.c.id == actor["id"]).with_for_update()
                )
                .mappings()
                .one()
            )
            now = utc_now()
            if (
                current["revoked_at"]
                or current["expires_at"] <= now
                or not account["enabled"]
                or account["deleted_at"]
            ):
                raise AppError(401, "AUTH_REQUIRED", "会话已失效")
            if (
                not current["restricted"]
                and not account["must_change_password"]
                and not verify_password(account["password_hash"], current_password or "")
            ):
                raise AppError(401, "INVALID_CREDENTIALS", "原密码错误")
            if verify_password(account["password_hash"], new_password):
                raise AppError(400, "VALIDATION_ERROR", "新密码不能与原密码相同")
            db.execute(
                update(admin_user)
                .where(admin_user.c.id == account["id"])
                .values(
                    password_hash=encoded,
                    must_change_password=0,
                    version=admin_user.c.version + 1,
                    updated_at=now,
                )
            )
            db.execute(
                delete(admin_password_reset).where(
                    admin_password_reset.c.admin_user_id == account["id"]
                )
            )
            db.execute(
                update(admin_session)
                .where(
                    admin_session.c.admin_user_id == account["id"],
                    admin_session.c.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
            new_token = secrets.token_urlsafe(32)
            expires = now + SESSION_LIFETIME
            db.execute(
                insert(admin_session).values(
                    admin_user_id=account["id"],
                    session_token_hash=token_digest(new_token),
                    created_at=now,
                    expires_at=expires,
                    restricted=0,
                )
            )
            audit(db, actor, "auth.password", "修改本人密码", context)
        return new_token, expires
