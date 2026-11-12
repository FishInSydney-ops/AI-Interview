# 后端

运行环境、安装和启动见项目根 README。

- `app/entry/main.py` 提供 `create_app` 工厂；应用启动不执行建表或写种子数据。
- `app/infrastructure/models.py` 是24张表的 SQLAlchemy metadata；业务逻辑关联而非物理外键。
- `dependencies.py` 提供 MySQL 请求会话、Redis 客户端及 MinIO 客户端；业务事务由模块显式提交。
- 修改模型后导出 `schema.sql`，通过新增 Alembic 迁移管理结构，不能修改已应用的版本。
- 自动化基础测试隔离连接；`tests/test_mysql_integration.py` 只接受事先创建的 `yunshu_test_*` 独立数据库。

集成测试例（先创建并授权独立空测试库）：

```bash
MYSQL_TEST_DATABASE=yunshu_test_local uv run pytest -q tests/test_mysql_integration.py
```

集成测试会在该测试库建表并在结束时删除测试表，禁止指定业务库；必须使用可丢弃的独立库。测试不会创建测试数据库或授予权限。
