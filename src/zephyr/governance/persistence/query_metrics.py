# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.persistence.query_metrics
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.query_metrics
# [CONSUMERS] zephyr.governance.database_manager; tests.unit.test_query_metrics_unit; tests.unit.db.test_query_metrics_db
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# 代理模块：将 zephyr.governance.query_metrics 重定向到 zephyr.governance.query_metrics
from zephyr.governance.query_metrics import QueryMetrics, query_metrics

__all__ = ["QueryMetrics", "query_metrics"]
