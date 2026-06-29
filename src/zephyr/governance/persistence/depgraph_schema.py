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
# P2 迁移后治本（2026-06-27）：DB_PATH 常量已从真源删除（路径污染源），此处同步移除。
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection, init_db

__all__ = ["get_depgraph_pg_connection", "init_db"]
