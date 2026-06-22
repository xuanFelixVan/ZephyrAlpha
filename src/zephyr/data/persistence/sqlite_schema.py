# 代理模块：将 zephyr.data.persistence.sqlite_schema 重定向到 zephyr.governance.sqlite_schema
# 原因：多个模块导入 zephyr.data.persistence.sqlite_schema，
# 但实际模块在 zephyr.governance.sqlite_schema（模块迁移后路径未更新）
from zephyr.governance.sqlite_schema import (
    _MIGRATIONS,
    DB_PATH,
    SchemaManager,
    get_db_connection,
    init_db,
    migration_dry_run,
    schema_version,
    table_names,
    view_names,
)

__all__ = [
    "DB_PATH",
    "_MIGRATIONS",
    "SchemaManager",
    "get_db_connection",
    "init_db",
    "migration_dry_run",
    "schema_version",
    "table_names",
    "view_names",
]
