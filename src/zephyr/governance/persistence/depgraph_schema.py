# 代理模块：将 zephyr.governance.persistence.depgraph_schema 重定向到 zephyr.governance.depgraph_schema
from zephyr.governance.depgraph_schema import DB_PATH, get_db_connection, init_db

__all__ = ["DB_PATH", "get_db_connection", "init_db"]
