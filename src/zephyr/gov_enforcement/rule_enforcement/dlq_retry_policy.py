# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.dlq_retry_policy
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.events.dlq; zephyr.shared.infra.observer; zephyr.shared.io.paths
# [CONSUMERS] zephyr.infrastructure.pipeline.dead_letter_queue; AutoRuntime Core retry phase
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 指数退避1/2/4/8/16min; 5次后PERMANENT_FAIL; ThreadPoolExecutor并行
# [MODIFY-GUARD] BACKOFF_SCHEDULE变更必须同步文档
# [STABILITY] evolving; [SAFETY] L; [AI_AUTONOMY] ai_modifiable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS] scripts/connect/dlq_retry.py --trigger
# [A_module] module_id=MOD-DAT-dlq_retry_policy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的真重试。

5.40.4 修复：原 retry_pending 仅 SELECT COUNT(*) 打印日志后返回 degraded
（假重试——死信永远不被重新投递）。现对接项目已有 DLQ 投递接口：

  - 取出待重试死信：`DeadLetterQueue.pop_retryable()`（过滤 resolved/超次数/未到点）
  - 重新投递：`Observer.emit(event_type, payload)`，返回成功处理的 handler 数
  - 投递成功（>=1 个 handler 成功）-> `mark_resolved(db_id)`
  - 投递失败（无订阅者或全部失败）-> `record_failure(dl)`（attempt+1，安排下次重试）
  - 本次失败且已达 max_attempts -> `mark_exhausted(db_id)`（终态，不再重试）

注：若 observer 已被 DLQ attach 包装（attach_dlq_to_observer），仍失败的 handler
会被自动重新捕获为新死信（幂等键去重）。退避间隔由 DeadLetterQueue 的
retry_interval 控制（构造参数，默认 60s）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: dlq 参数
#   fields: 参数 dlq（无注解）
#   code: dlq_retry_policy.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: observer 参数
#   fields: 参数 observer（无注解）
#   code: dlq_retry_policy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_default_observer
#   name_en: get_default_observer
#   intro: 进程级默认重投递总线（懒加载单例）。
#   desc: 进程级默认重投递总线（懒加载单例）。 生产接线：运行时应将事件消费者 subscribe 到本总线（或通过 `DLQRetryPolicy(observer=...)` 注入自己…；源码 L103-L115
#   inputs: 无参数
#   outputs: Observer
# - id: A2
#   name_zh: ② DLQRetryPolicy
#   name_en: DLQRetryPolicy
#   intro: 死信重试策略——从 DeadLetterQueue 取待重试死信并真重投递。
#   desc: 死信重试策略——从 DeadLetterQueue 取待重试死信并真重投递。 Args: dlq: 注入的 DeadLetterQueue（测试/定制 DB 路径）；None -…；公共方法（定义序）: retry_p…
#   inputs: dlq observer
#   outputs: 返回值
# - id: A3
#   name_zh: ③ retry_pending
#   name_en: retry_pending
#   intro: retry_pending() 源码 L196-L197
#   desc: 源码 L196-L197
#   inputs: 无参数
#   outputs: RetryResult
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: Observer
#   name_en: Observer
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.pipeline.dead_letter_queue; AutoRuntime Core retry phase
# - id: O2
#   name_zh: RetryResult
#   name_en: RetryResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.pipeline.dead_letter_queue; AutoRuntime Core retry phase
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.shared.events.dlq import DeadLetter, DeadLetterQueue
    from zephyr.shared.infra.observer import Observer

logger = logging.getLogger(__name__)
__all__ = ["DLQRetryPolicy", "RetryResult", "get_default_observer", "retry_pending"]

_default_observer: Observer | None = None


def get_default_observer() -> Observer:
    """进程级默认重投递总线（懒加载单例）。

    生产接线：运行时应将事件消费者 subscribe 到本总线（或通过
    `DLQRetryPolicy(observer=...)` 注入自己的总线），否则重投递因
    无订阅者计为失败并按 max_attempts 耗尽。
    """
    global _default_observer
    if _default_observer is None:
        from zephyr.shared.infra.observer import Observer

        _default_observer = Observer()
    return _default_observer


@dataclass
class RetryResult:
    retried: int = 0
    succeeded: int = 0
    failed: int = 0
    status: str = "complete"


class DLQRetryPolicy:
    """死信重试策略——从 DeadLetterQueue 取待重试死信并真重投递。

    Args:
        dlq: 注入的 DeadLetterQueue（测试/定制 DB 路径）；None -> 默认 governance.db。
        observer: 注入的重投递总线；None -> 进程级默认总线（get_default_observer()）。
    """

    def __init__(self, dlq: DeadLetterQueue | None = None, observer: Observer | None = None) -> None:
        self._dlq = dlq
        self._observer = observer

    def _get_dlq(self) -> DeadLetterQueue:
        if self._dlq is None:
            from zephyr.shared.events.dlq import DeadLetterQueue
            from zephyr.shared.io.paths import DB_PATH

            self._dlq = DeadLetterQueue(str(DB_PATH))
        return self._dlq

    def _get_observer(self) -> Observer:
        if self._observer is None:
            self._observer = get_default_observer()
        return self._observer

    @staticmethod
    def _redeliver(observer: Observer, dl: DeadLetter) -> bool:
        """重投递单条死信。emit 返回成功处理的 handler 数，> 0 视为投递成功。"""
        try:
            delivered = observer.emit(dl.event_type, dl.payload)
        except Exception:  # noqa: BLE001 — emit 实现异常不得中断批量重试
            logger.warning("[DLQ] redeliver raised for dead letter id=%s", dl.db_id, exc_info=True)
            return False
        return delivered > 0

    def retry_pending(self) -> RetryResult:
        try:
            dlq = self._get_dlq()
            pending = dlq.pop_retryable()
        except Exception as e:  # noqa: BLE001 — DB 不可达等降级为 degraded，不阻断调用方
            logger.warning("[DLQ] degraded: %s", e, exc_info=True)
            return RetryResult(status="degraded")

        if not pending:
            return RetryResult(retried=0, succeeded=0, failed=0, status="complete")

        observer = self._get_observer()
        result = RetryResult(status="complete")
        for dl in pending:
            result.retried += 1
            if self._redeliver(observer, dl):
                dlq.mark_resolved(dl.db_id)  # type: ignore[arg-type]
                result.succeeded += 1
            else:
                # 失败：已达最大次数 -> 终态 exhausted；否则 record_failure 安排下次重试
                if dl.attempt_count + 1 >= dl.max_attempts:
                    dlq.mark_exhausted(dl.db_id)  # type: ignore[arg-type]
                else:
                    dlq.record_failure(dl)
                result.failed += 1

        logger.info(
            "[DLQ] retry_pending: retried=%d succeeded=%d failed=%d",
            result.retried,
            result.succeeded,
            result.failed,
        )
        return result


def retry_pending() -> RetryResult:
    return DLQRetryPolicy().retry_pending()
