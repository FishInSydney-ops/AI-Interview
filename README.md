# 云枢智学

Python + FastAPI 单体后端，Vue 3 + TypeScript 学员端和管理端，MySQL 8.4 + SQLAlchemy，Redis 可选缓存，MinIO 对象存储。当前已实现基础工程、学员首页与登录页样式、管理端基本布局、真实登录/退出及系统管理四模块；学员注册登录、内容 CRUD、练习判分等业务仍待开发。

## 本机启动

要求 Docker Desktop 已启动、三个基础服务正常运行，MinIO 已有私有桶 `yszx-files`；Node.js >=22.12、npm、uv 可用。依赖版本固定在 `package-lock.json` 和 `backend/uv.lock`。

在项目根目录执行：

```bash
make install
make configure
make migrate
make init-admin
```

`make configure` 从 `docker/local/.env` 读取本机连接配置，生成权限为 600 的 `backend/.env`，已有文件不会覆盖。不会打印密码、创建桶或修改桶访问策略。若 MySQL 已有数据，首次迁移会停止，不会覆盖现存表。MySQL 的 DDL 不能保证整批回滚，迁移中断后须检查已有表并制定恢复方案，禁止直接删除数据重试。

`make init-admin` 在终端交互创建首个管理员，用户名默认 `admin`，密码由你设置（8–128 个字符，输入不回显）。没有默认密码；已有有效管理员时不会覆盖。请勿在聊天、命令行参数或版本库中填写密码。

分别在三个终端执行：

```bash
make api
```

```bash
make portal
```

```bash
make admin
```

| 入口 | 地址 |
|---|---|
| 学员端 | http://127.0.0.1:5173/ |
| 管理端 | http://127.0.0.1:5174/admin/ |
| API 文档 | http://127.0.0.1:8000/api/docs |
| 存活检查 | http://127.0.0.1:8000/api/v1/health |
| 依赖就绪检查 | http://127.0.0.1:8000/api/v1/ready |

两个前端独立运行，均将 `/api` 代理到本机 8000 端口。学员端首页已改为学习门户，新增 `/login` 登录页（当前仅界面，学员认证尚未开放）；管理端登录入口为 `/admin/login`，未登录访问业务页会跳转登录，登录后可访问侧栏、顶栏和11个空白业务页面。管理员下拉提供确认退出，退出会撤销 MySQL 会话。AI 面试入口显示即将上线。前后端服务在各自终端按 Ctrl+C 停止；Docker 服务使用 `docker compose` 管理。

## 验证与数据库

```bash
make check
```

后端基础测试使用隔离替身验证健康检查及认证契约，不访问真实业务数据；真实数据库测试另需独立的 `yunshu_test_*` 数据库及 `MYSQL_TEST_DATABASE` 环境变量，涵盖约束、认证和并发频控。`make check` 还执行 Ruff、双前端 TypeScript 检查及生产构建。

- 初始迁移：`backend/migrations/versions/0001_initial.py` 及冻结的 SQL 快照。
- 当前结构导出：`scripts/sql/schema.sql`；历史 SQLite 草案：`scripts/sql/schema.sqlite.sql`。
- SQLAlchemy metadata：`backend/app/infrastructure/models.py`，30 张业务表，禁止物理外键。
- 以 Alembic 版本管理结构，服务启动不会自动建表。初始迁移不自动删除业务表；后续变更须新增迁移并制定回滚计划。
- `backend/.venv/bin/python scripts/export_schema.py` 仅导出当前 metadata，不连接数据库、不改写历史迁移。
- 会话、锁定、频控仍由 MySQL 持久保存；Redis 用于可丢失的缓存。当前只连接三项服务并检查桶是否存在，未开放上传。

详见 [基础工程说明](docs/development/基础工程搭建.md)。`.env`、依赖目录、构建目录和本地运行数据不提交版本管理；原型位于 `prototype/`，保留作后续业务页面参考。

## 管理端认证

采用 Argon2id 密码哈希和随机会话凭据；MySQL 仅保存凭据 SHA-256 摘要，会话固定 7 天。Cookie 为 `yszx_admin_session`，HttpOnly、SameSite=Strict，Path=/api/v1/admin，本机 HTTP 开发模式 Secure=false。每次导航向后端验证身份；浏览器不将密码或凭据写入 localStorage。

管理端写请求必须携带允许的 Origin 与 `X-Requested-With: XMLHttpRequest`，前端请求封装自动设置。仅允许本机 5174 管理端和 8000 文档来源，无通配 CORS；本机代理保留 Origin，`make api` 禁止信任转发 IP 头。后台登录按后端看到的来源 IP 在固定 UTC 5 分钟窗口最多放行 10 次，MySQL 原子累计，超限返回 429 和 Retry-After。HTTP 本机方案不适用于公网；部署 HTTPS 时设置 `ADMIN_COOKIE_SECURE=true` 并调整明确的来源清单。详见 [认证实现记录](docs/development/管理端认证与页面优化.md)。

系统管理模块已接入真实数据库，新增迁移0002；已有管理员保留原账号密码。详见 [系统管理模块](docs/development/系统管理模块.md)。数据库迁移前备份存于 `backend/.backups/`，不纳入版本管理。
