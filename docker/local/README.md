# 本地 MySQL、Redis 和 MinIO

本配置供本机开发使用，后续基础工程已按用户确认切换 MySQL，并连接 Redis 和 MinIO；容器启动本身不执行应用数据库迁移。端口只绑定到本机 `127.0.0.1`；Redis 未设置密码，不适合开放给局域网或公网。

## 启动

1. 打开 Docker Desktop，等待 Docker 启动完成。
2. 在终端进入本目录，复制配置并修改 `.env` 中的密码：

   ```bash
   cd docker/local
   cp .env.example .env
   ```

   用编辑器打开 `.env`，修改 MySQL root 密码、MySQL 普通用户密码和 MinIO 密码。MinIO 用户名至少 3 个字符，密码至少 8 个字符。为避免 Compose 环境变量解析歧义，建议密码使用英文字母和数字；`.env` 是本地敏感文件，不要提交或分享。
3. 启动服务：

   ```bash
   docker compose up -d --build
   ```

   首次启动需要下载镜像并从 MinIO 官方源码编译，可能需要较长时间；MySQL 初始化也可能需要一些时间。MinIO 依赖 Docker Hub、Go 模块代理与 GitHub 的网络访问；如下载失败，请检查 Docker Desktop 的网络代理与错误信息。该源码构建方案尚需在本机实测；MinIO 社区源码仓库已归档，仅供本地开发。查看状态：

   ```bash
   docker compose ps
   ```

   MySQL、Redis 有健康检查；MinIO 检查运行状态并通过控制台验证。查看日志：

   ```bash
   docker compose logs --tail=100
   ```

## 连接

| 服务 | 本机地址 | 账号说明 |
|---|---|---|
| MySQL | `127.0.0.1:3306` | 普通账号、密码和数据库名见 `.env` |
| Redis | `127.0.0.1:6379` | 本机开发未设置密码 |
| MinIO S3 API | `http://127.0.0.1:9000` | 用户名和密码见 `.env` |
| MinIO 控制台 | `http://127.0.0.1:9001` | 使用 `.env` 中的 MinIO 用户名和密码登录 |

端口被占用时，修改 `.env` 中对应的 `*_PORT`，再运行 `docker compose up -d`。Compose 网络内的其他容器应使用服务名 `mysql`、`redis`、`minio` 和容器内端口连接；`127.0.0.1` 指的是容器自身。

MySQL 的账号、密码、数据库环境变量只在首次初始化空数据卷时生效；已有数据时直接修改 `.env` 不会自动修改数据库账号或密码。MinIO 存储桶可以使用 MinIO Console 或 S3 客户端创建；源码版本的控制台功能可能与旧版不同。

## 停止和数据

```bash
docker compose down
```

普通停止或删除容器会保留三个命名数据卷。`docker compose down -v` 会删除这些数据卷及其数据，除非明确需要清空数据，否则不要使用。

项目后端连接与迁移见根目录 README。当前已创建业务桶 `yszx-files`，后端只检查其存在，不自动创建桶或修改策略。
