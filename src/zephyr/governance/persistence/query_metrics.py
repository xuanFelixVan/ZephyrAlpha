# 代理模块：将 zephyr.governance.query_metrics 重定向到 zephyr.governance.query_metrics
from zephyr.governance.query_metrics import QueryMetrics, query_metrics

__all__ = ["QueryMetrics", "query_metrics"]
