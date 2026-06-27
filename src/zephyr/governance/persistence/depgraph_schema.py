# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.persistence.depgraph_schema
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# 代理模块：将 zephyr.governance.persistence.depgraph_schema 重定向到 zephyr.governance.depgraph_schema
from zephyr.governance.depgraph_schema import DB_PATH, get_db_connection, init_db

__all__ = ["DB_PATH", "get_db_connection", "init_db"]
