import csv
import io
import secrets
from contextlib import contextmanager
from datetime import timedelta

from sqlalchemy import delete, func, insert, or_, select, update
from sqlalchemy.exc import IntegrityError

from app.common.errors import AppError
from app.infrastructure.models import (
    admin_operation_log as logs,
)
from app.infrastructure.models import (
    admin_password_reset as resets,
)
from app.infrastructure.models import (
    admin_role as roles,
)
from app.infrastructure.models import (
    admin_role_permission as grants,
)
from app.infrastructure.models import (
    admin_session as sessions,
)
from app.infrastructure.models import (
    admin_user as users,
)
from app.infrastructure.models import (
    platform_settings as settings,
)
from app.infrastructure.models import (
    stored_file as files,
)
from app.modules.admin_auth.security import PASSWORD_HASHER, utc_now
from app.modules.system.permissions import ALL_PERMISSIONS

USER_COLUMNS = [
    users.c.id,
    users.c.username,
    users.c.phone,
    users.c.email,
    users.c.role_id,
    users.c.is_super,
    users.c.enabled,
    users.c.version,
    users.c.created_at,
    users.c.last_login_at,
    roles.c.name.label("role_name"),
]
DEFAULT_SETTINGS = dict(
    name="云枢智学",
    description="让学习更有章法，让成长清晰可见。",
    logo_file_id=None,
    avatar_file_id=None,
)


def audit(db, actor, action, target, context, outcome="success"):
    db.execute(
        insert(logs).values(
            actor_id=actor.get("admin_user_id"),
            actor_name=actor.get("username", "匿名")[:64],
            action=action,
            target=str(target)[:255],
            ip=context.get("ip", "")[:128],
            request_id=context.get("request_id", "")[:64],
            outcome=outcome,
            created_at=utc_now(),
        )
    )


def permissions(db, account):
    if account["is_super"]:
        return sorted(ALL_PERMISSIONS)
    return list(
        db.execute(
            select(grants.c.permission).where(grants.c.role_id == account["role_id"])
        ).scalars()
    )


def require(actor, permission):
    if actor.get("must_change_password"):
        raise AppError(403, "PASSWORD_RESET_REQUIRED", "请先修改密码")
    if permission == "system:roles" and not actor.get("is_super"):
        raise AppError(403, "FORBIDDEN", "仅超级管理员可管理角色")
    if not actor.get("is_super") and permission not in actor.get("permissions", []):
        raise AppError(403, "FORBIDDEN", "没有此操作权限")


class SystemService:
    def __init__(self, engine):
        self.engine = engine

    @contextmanager
    def writing(self, actor, permission):
        try:
            with self.engine.begin() as db:
                # Serialize administrative changes, including role assignment/deletion and grants.
                db.execute(select(users.c.id).where(users.c.is_super == 1).with_for_update()).all()
                current = (
                    db.execute(
                        select(users)
                        .where(
                            users.c.id == actor["admin_user_id"],
                            users.c.deleted_at.is_(None),
                            users.c.enabled == 1,
                        )
                        .with_for_update()
                    )
                    .mappings()
                    .first()
                )
                if not current:
                    raise AppError(401, "AUTH_REQUIRED", "账号已不可用")
                refreshed = {**dict(current), "permissions": permissions(db, current)}
                valid_session = db.execute(
                    select(sessions.c.id).where(
                        sessions.c.id == actor["id"],
                        sessions.c.revoked_at.is_(None),
                        sessions.c.expires_at > utc_now(),
                    )
                ).first()
                if not valid_session:
                    raise AppError(401, "AUTH_REQUIRED", "会话已失效")
                require(refreshed, permission)
                actor["permissions"] = refreshed["permissions"]
                actor["is_super"] = refreshed["is_super"]
                yield db
        except IntegrityError:
            raise AppError(409, "CONFLICT", "名称、编码或用户名已存在，请刷新后重试") from None

    def role_list(self):
        with self.engine.connect() as db:
            counts = (
                select(users.c.role_id, func.count().label("n"))
                .where(users.c.deleted_at.is_(None))
                .group_by(users.c.role_id)
                .subquery()
            )
            rows = (
                db.execute(
                    select(roles, func.coalesce(counts.c.n, 0).label("user_count"))
                    .outerjoin(counts, roles.c.id == counts.c.role_id)
                    .order_by(roles.c.id)
                )
                .mappings()
                .all()
            )
            all_grants = db.execute(select(grants.c.role_id, grants.c.permission)).all()
            by_role = {}
            for role_id, permission in all_grants:
                by_role.setdefault(role_id, []).append(permission)
            return [{**r, "permissions": by_role.get(r["id"], [])} for r in rows]

    def save_role(self, actor, context, data, role_id=None):
        with self.writing(actor, "system:roles") as db:
            payload = dict(data)
            requested = set(payload.pop("permissions"))
            version = payload.pop("version", None)
            if not requested <= ALL_PERMISSIONS or "system:roles" in requested:
                raise AppError(400, "VALIDATION_ERROR", "角色权限无效；角色管理仅超级管理员可用")
            now = utc_now()
            if role_id:
                role = db.execute(select(roles).where(roles.c.id == role_id)).mappings().first()
                if not role:
                    raise AppError(404, "NOT_FOUND", "角色不存在")
                if role["code"] == "super_admin":
                    raise AppError(409, "PROTECTED_RESOURCE", "超级管理员角色不可修改")
                if role["version"] != version:
                    raise AppError(409, "VERSION_CONFLICT", "角色已变化，请刷新")
                if role["built_in"] and payload["code"] != role["code"]:
                    raise AppError(409, "PROTECTED_RESOURCE", "内置角色编码不可修改")
                db.execute(
                    update(roles)
                    .where(roles.c.id == role_id)
                    .values(**payload, version=version + 1, updated_at=now)
                )
                db.execute(delete(grants).where(grants.c.role_id == role_id))
            else:
                if payload["code"] == "super_admin":
                    raise AppError(409, "PROTECTED_RESOURCE", "不能创建超级管理员角色")
                role_id = db.execute(
                    insert(roles).values(**payload, created_at=now, updated_at=now)
                ).inserted_primary_key[0]
            if requested:
                db.execute(
                    insert(grants), [dict(role_id=role_id, permission=p) for p in sorted(requested)]
                )
            audit(
                db, actor, "role.update" if version else "role.create", f"角色:{role_id}", context
            )
        return {"id": role_id}

    def delete_role(self, actor, context, role_id):
        with self.writing(actor, "system:roles") as db:
            role = db.execute(select(roles).where(roles.c.id == role_id)).mappings().first()
            if not role:
                raise AppError(404, "NOT_FOUND", "角色不存在")
            if (
                role["built_in"]
                or db.execute(
                    select(users.c.id).where(
                        users.c.role_id == role_id, users.c.deleted_at.is_(None)
                    )
                ).first()
            ):
                raise AppError(409, "ROLE_IN_USE", "内置角色或有用户的角色不能删除")
            db.execute(delete(grants).where(grants.c.role_id == role_id))
            db.execute(delete(roles).where(roles.c.id == role_id))
            audit(db, actor, "role.delete", f"角色:{role_id}", context)

    def user_list(self, keyword, role_id, enabled, page, page_size):
        query = (
            select(*USER_COLUMNS)
            .outerjoin(roles, roles.c.id == users.c.role_id)
            .where(users.c.deleted_at.is_(None))
        )
        if keyword:
            query = query.where(
                or_(
                    users.c.username.contains(keyword, autoescape=True),
                    users.c.phone.contains(keyword, autoescape=True),
                )
            )
        if role_id:
            query = query.where(users.c.role_id == role_id)
        if enabled is not None:
            query = query.where(users.c.enabled == enabled)
        with self.engine.connect() as db:
            count = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
            rows = (
                db.execute(
                    query.order_by(users.c.id.desc())
                    .offset((page - 1) * page_size)
                    .limit(page_size)
                )
                .mappings()
                .all()
            )
        return dict(items=[dict(r) for r in rows], total=count, page=page, page_size=page_size)

    def user_detail(self, user_id):
        with self.engine.connect() as db:
            row = (
                db.execute(
                    select(*USER_COLUMNS)
                    .outerjoin(roles, roles.c.id == users.c.role_id)
                    .where(users.c.id == user_id, users.c.deleted_at.is_(None))
                )
                .mappings()
                .first()
            )
            if not row:
                raise AppError(404, "NOT_FOUND", "用户不存在")
            recent = (
                db.execute(
                    select(logs)
                    .where(logs.c.actor_id == user_id)
                    .order_by(logs.c.id.desc())
                    .limit(10)
                )
                .mappings()
                .all()
            )
            return {**row, "recent_logs": [dict(r) for r in recent]}

    def target(self, db, actor, user_id):
        target = (
            db.execute(
                select(users)
                .where(users.c.id == user_id, users.c.deleted_at.is_(None))
                .with_for_update()
            )
            .mappings()
            .first()
        )
        if not target:
            raise AppError(404, "NOT_FOUND", "用户不存在")
        if target["is_super"]:
            raise AppError(409, "PROTECTED_RESOURCE", "内置超级管理员不可在用户管理中修改或重置")
        if not actor["is_super"] and not set(permissions(db, target)) <= set(actor["permissions"]):
            raise AppError(403, "FORBIDDEN", "不能管理权限高于自己的账号")
        return target

    def save_user(self, actor, context, data, user_id=None):
        payload = dict(data)
        password = payload.pop("password", None)
        password_hash = PASSWORD_HASHER.hash(password) if password else None
        version = payload.pop("version", None)
        with self.writing(actor, "user:edit" if user_id else "user:create") as db:
            if not user_id and not password_hash:
                raise AppError(400, "VALIDATION_ERROR", "新用户必须设置密码")
            if user_id:
                target = self.target(db, actor, user_id)
                if target["version"] != version:
                    raise AppError(409, "VERSION_CONFLICT", "用户已变化，请刷新")
                if target["enabled"] != payload["enabled"]:
                    require(actor, "user:disable")
            role = (
                db.execute(select(roles).where(roles.c.id == payload["role_id"])).mappings().first()
            )
            if not role or role["code"] == "super_admin":
                raise AppError(400, "VALIDATION_ERROR", "请选择有效的非超级管理员角色")
            assigned = set(
                db.execute(
                    select(grants.c.permission).where(grants.c.role_id == role["id"])
                ).scalars()
            )
            if not actor["is_super"] and not assigned <= set(actor["permissions"]):
                raise AppError(403, "FORBIDDEN", "不能授予自己没有的权限")
            now = utc_now()
            if password_hash:
                payload.update(password_hash=password_hash, must_change_password=0)
            if user_id:
                db.execute(
                    update(users)
                    .where(users.c.id == user_id)
                    .values(**payload, version=version + 1, updated_at=now)
                )
                self.revoke(db, user_id)
                if password_hash:
                    db.execute(delete(resets).where(resets.c.admin_user_id == user_id))
            else:
                user_id = db.execute(
                    insert(users).values(**payload, created_at=now, updated_at=now)
                ).inserted_primary_key[0]
            audit(
                db, actor, "user.update" if version else "user.create", f"用户:{user_id}", context
            )
        return {"id": user_id}

    @staticmethod
    def revoke(db, user_id):
        db.execute(
            update(sessions)
            .where(sessions.c.admin_user_id == user_id, sessions.c.revoked_at.is_(None))
            .values(revoked_at=utc_now())
        )

    def batch_users(self, actor, context, ids, action):
        with self.writing(actor, "user:delete" if action == "delete" else "user:disable") as db:
            for user_id in sorted(set(ids)):
                self.target(db, actor, user_id)
            for user_id in sorted(set(ids)):
                values = (
                    {"deleted_at": utc_now()}
                    if action == "delete"
                    else {"enabled": int(action == "enable")}
                )
                db.execute(
                    update(users)
                    .where(users.c.id == user_id)
                    .values(**values, updated_at=utc_now(), version=users.c.version + 1)
                )
                self.revoke(db, user_id)
                audit(db, actor, "user." + action, f"用户:{user_id}", context)

    def reset_password(self, actor, context, user_id):
        password = secrets.token_urlsafe(18)
        encoded = PASSWORD_HASHER.hash(password)
        with self.writing(actor, "user:reset") as db:
            self.target(db, actor, user_id)
            db.execute(delete(resets).where(resets.c.admin_user_id == user_id))
            expires = utc_now() + timedelta(hours=24)
            db.execute(
                insert(resets).values(
                    admin_user_id=user_id, password_hash=encoded, expires_at=expires
                )
            )
            db.execute(
                update(users)
                .where(users.c.id == user_id)
                .values(must_change_password=1, version=users.c.version + 1, updated_at=utc_now())
            )
            self.revoke(db, user_id)
            audit(db, actor, "user.reset_password", f"用户:{user_id}", context)
        return dict(temporary_password=password, expires_at=expires)

    def log_query(self, keyword, action, start, end):
        query = select(logs)
        if keyword:
            query = query.where(
                or_(
                    *[
                        c.contains(keyword, autoescape=True)
                        for c in [logs.c.actor_name, logs.c.action, logs.c.target]
                    ]
                )
            )
        if action:
            query = query.where(logs.c.action.startswith(action, autoescape=True))
        if start:
            query = query.where(logs.c.created_at >= start)
        if end:
            query = query.where(logs.c.created_at < end)
        return query

    def log_list(self, query, page, page_size):
        with self.engine.connect() as db:
            count = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
            rows = (
                db.execute(
                    query.order_by(logs.c.id.desc()).offset((page - 1) * page_size).limit(page_size)
                )
                .mappings()
                .all()
            )
        return dict(items=[dict(r) for r in rows], total=count, page=page, page_size=page_size)

    def export_logs(self, actor, context, query):
        with self.writing(actor, "system:export") as db:
            rows = db.execute(query.order_by(logs.c.id.desc()).limit(10001)).mappings().all()
            if len(rows) > 10000:
                raise AppError(400, "EXPORT_TOO_LARGE", "单次最多导出10000条，请缩小筛选范围")
            audit(db, actor, "log.export", "操作日志CSV", context)
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["ID", "用户", "操作", "目标", "IP", "结果", "时间(UTC)", "请求标识"])
        for row in rows:
            values = [
                row[k]
                for k in [
                    "id",
                    "actor_name",
                    "action",
                    "target",
                    "ip",
                    "outcome",
                    "created_at",
                    "request_id",
                ]
            ]
            writer.writerow(
                [
                    ("'" + str(v))
                    if str(v).lstrip().startswith(("=", "+", "-", "@", "\t", "\r"))
                    else str(v)
                    for v in values
                ]
            )
        return "\ufeff" + output.getvalue()

    def get_settings(self):
        with self.engine.connect() as db:
            row = db.execute(select(settings).where(settings.c.id == 1)).mappings().first()
            return dict(row) if row else dict(id=1, version=0, **DEFAULT_SETTINGS)

    def save_settings(self, actor, context, data):
        with self.writing(actor, "system:settings") as db:
            row = (
                db.execute(select(settings).where(settings.c.id == 1).with_for_update())
                .mappings()
                .first()
            )
            if not row or row["version"] != data["version"]:
                raise AppError(409, "VERSION_CONFLICT", "设置已变化，请刷新")
            payload = dict(data)
            for key in ["logo_file_id", "avatar_file_id"]:
                if (
                    payload[key] is not None
                    and not db.execute(select(files.c.id).where(files.c.id == payload[key])).first()
                ):
                    raise AppError(400, "VALIDATION_ERROR", "图片不存在，请重新上传")
            payload.update(version=row["version"] + 1, updated_at=utc_now())
            db.execute(update(settings).where(settings.c.id == 1).values(**payload))
            audit(db, actor, "settings.update", "平台基本信息", context)
        return self.get_settings()
