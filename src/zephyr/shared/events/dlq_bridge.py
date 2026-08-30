# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.events.dlq_bridge
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.events.dlq
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CT-DLQ-001: DeadLetterQueue -> System Event Bus integration bridge.

Connects the existing DeadLetterQueue (438 lines, shared/events/dlq.py)
to the system event observer (shared/infra/observer.py) so that failed
events are automatically persisted to DLQ.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: dlq 参数
#   fields: 参数 dlq，类型注解 DeadLetterQueue
#   code: dlq_bridge.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: observer 参数
#   fields: 参数 observer，类型注解 Observer
#   code: dlq_bridge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① make_dlq_event_handler
#   name_en: make_dlq_event_handler
#   intro: make_dlq_event_handler(dlq) 源码 L98-L110
#   desc: 源码 L98-L110
#   inputs: dlq
#   outputs: Callable[[str, dict[str, Any], Exceptio…
# - id: A2
#   name_zh: ② DLQEventBridge
#   name_en: DLQEventBridge
#   intro: class DLQEventBridge 源码 L113-L146
#   desc: 公共方法（定义序）: attach, attached, replay_failed；源码 L113-L146
#   inputs: dlq observer
#   outputs: 返回值
# - id: A3
#   name_zh: ③ attach_dlq_to_observer
#   name_en: attach_dlq_to_observer
#   intro: attach_dlq_to_observer(dlq, observer) 源码 L149-L155
#   desc: 源码 L149-L155
#   inputs: dlq observer
#   outputs: DLQEventBridge
# 层: 输出
# - id: O1
#   name_zh: Callable[[str, dict[str, Any], Exceptio…
#   name_en: Callable[[str, dict[str, Any], Exceptio…
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# - id: O2
#   name_zh: DLQEventBridge
#   name_en: DLQEventBridge
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: N/A (all consumers verified as phantom — stale references removed)
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
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from zephyr.shared.events.dlq import DeadLetterQueue

if TYPE_CHECKING:
    from zephyr.shared.infra.observer import Observer

__all__ = [
    "DLQEventBridge",
    "attach_dlq_to_observer",
    "make_dlq_event_handler",
]

_logger = logging.getLogger(__name__)


def make_dlq_event_handler(dlq: DeadLetterQueue) -> Callable[[str, dict[str, Any], Exception], None]:
    def _handler(event_name: str, payload: dict[str, Any], error: Exception) -> None:
        try:
            error_msg = f"{type(error).__name__}: {error}"
            dlq.enqueue(
                event_type=event_name,
                payload=payload,
                error=error_msg,
            )
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.error("DLQ event handler failed: event=%s error=%s", event_name, exc, exc_info=True)

    return _handler


class DLQEventBridge:
    def __init__(self, dlq: DeadLetterQueue, observer: Observer | None = None) -> None:
        self._dlq = dlq
        self._observer = observer
        self._attached = False

    def attach(self, observer: Observer | None = None) -> None:
        obs = observer or self._observer
        if obs is None:
            _logger.warning("DLQEventBridge.attach: no observer available")
            return
        if self._attached:
            return

        try:
            self._dlq.attach_to_observer(obs)
            self._attached = True
            _logger.info("DLQEventBridge attached to observer: %s events in DLQ", len(self._dlq))
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.error("DLQEventBridge.attach failed: %s", exc, exc_info=True)

    @property
    def attached(self) -> bool:
        return self._attached

    def replay_failed(self) -> int:
        count = 0
        for entry in self._dlq.list_pending():
            try:
                self._dlq.retry(entry.id)
                count += 1
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                _logger.warning("DLQ replay failed for entry %d: %s", entry.id, exc, exc_info=True)
        return count


def attach_dlq_to_observer(
    dlq: DeadLetterQueue,
    observer: Observer,
) -> DLQEventBridge:
    bridge = DLQEventBridge(dlq, observer)
    bridge.attach()
    return bridge
