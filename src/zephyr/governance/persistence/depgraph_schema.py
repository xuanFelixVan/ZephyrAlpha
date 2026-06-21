# 代理模块：将 zephyr.governance.persistence.depgraph_schema 重定向到 zephyr.governance.depgraph_schema
from zephyr.governance.depgraph_schema import init_db, get_db_connection, DB_PATH

__all__ = ["init_db", "get_db_connection", "DB_PATH"]
