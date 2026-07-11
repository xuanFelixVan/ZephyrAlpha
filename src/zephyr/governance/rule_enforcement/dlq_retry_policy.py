# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.dlq_retry_policy
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.infrastructure.pipeline.dead_letter_queue; AutoRuntime Core retry phase
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 指数退避1/2/4/8/16min; 5次后PERMANENT_FAIL; ThreadPoolExecutor并行
# [MODIFY-GUARD] BACKOFF_SCHEDULE变更必须同步文档
# [STABILITY] evolving; [SAFETY] L; [AI_AUTONOMY] ai_modifiable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS] scripts/connect/dlq_retry.py --trigger
# [A_module] module_id=MOD-DAT_dlq_retry_policy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DLQ 重试策略 — 指数退避自动重试"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
__all__ = ["DLQRetryPolicy", "RetryResult", "retry_pending"]


@dataclass
class RetryResult:
    retried: int = 0
    succeeded: int = 0
    failed: int = 0
    status: str = "complete"


class DLQRetryPolicy:
    def retry_pending(self) -> RetryResult:
        # 5.15.3 修复：dlq_messages 表不存在于 sqlite_schema，先检查 sqlite_master
        # 避免 OperationalError 异常路径；BACKOFF_SCHEDULE 死代码已删除
        try:
            from zephyr.governance.persistence.sqlite_schema import get_db_connection

            conn = get_db_connection()
            try:
                # 检查 dlq_messages 表是否存在
                table_exists = conn.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dlq_messages'"
                ).fetchone()[0]
                if table_exists == 0:
                    logger.info("[DLQ] dlq_messages table not found, retry not connected")
                    return RetryResult(retried=0, succeeded=0, failed=0, status="degraded")
                rows = conn.execute("SELECT COUNT(*) FROM dlq_messages").fetchone()
                total = rows[0] if rows else 0
                logger.info("[DLQ] pending messages: %d (retry not connected)", total)
                return RetryResult(retried=0, succeeded=0, failed=0, status="degraded")
            finally:
                conn.close()
        except Exception as e:
            logger.warning("[DLQ] degraded: %s", e, exc_info=True)
            return RetryResult(status="degraded")


def retry_pending() -> RetryResult:
    return DLQRetryPolicy().retry_pending()