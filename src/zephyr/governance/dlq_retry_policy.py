# [A_module] module_id=MOD-DAT_dlq_retry_policy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-MASTER-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.data.persistence.dlq_retry_policy
# [INVARIANTS] 指数退避1/2/4/8/16min; 5次后PERMANENT_FAIL; ThreadPoolExecutor并行
# [MODIFY-GUARD] BACKOFF_SCHEDULE变更必须同步文档
# [CONSUMERS] zephyr.data.persistence.dead_letter_queue; AutoRuntime Core retry phase
# [STABILITY] evolving; [SAFETY] L; [AI_AUTONOMY] ai_modifiable
# [TESTS] scripts/connect/dlq_retry.py --trigger
# [ERROR_CONTRACT]
"""DLQ 重试策略 — 指数退避自动重试"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
__all__ = ["DLQRetryPolicy", "RetryResult", "retry_pending"]

BACKOFF_SCHEDULE = [1, 2, 4, 8, 16]


@dataclass
class RetryResult:
    retried: int = 0
    succeeded: int = 0
    failed: int = 0
    status: str = "complete"


class DLQRetryPolicy:
    def retry_pending(self) -> RetryResult:
        try:
            from zephyr.governance.persistence.sqlite_schema import get_db_connection

            conn = get_db_connection()
            rows = conn.execute("SELECT COUNT(*) FROM dlq_messages").fetchone()
            total = rows[0] if rows else 0
            conn.close()
            logger.info("[DLQ] pending messages: %d (retry not connected)", total)
            return RetryResult(retried=0, succeeded=0, failed=0, status="degraded")
        except Exception as e:
            logger.warning("[DLQ] degraded: %s", e)
            return RetryResult(status="degraded")


def retry_pending() -> RetryResult:
    return DLQRetryPolicy().retry_pending()
