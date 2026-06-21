# 代理模块：将 zephyr.data.persistence.sqlite_schema 重定向到 zephyr.governance.sqlite_schema
# 原因：多个模块导入 zephyr.data.persistence.sqlite_schema，
# 但实际模块在 zephyr.governance.sqlite_schema（模块迁移后路径未更新）
from zephyr.governance.sqlite_schema import DB_PATH, SchemaManager, get_db_connection, init_db, schema_version

__all__ = ["DB_PATH", "SchemaManager", "get_db_connection", "init_db", "schema_version"]
