# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.events.dlq_bridge
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.events.dlq
# [CONSUMERS] infrastructure_runtime_integration.pipeline.dead_letter_queue
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_dlq_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""CT-DLQ-001: DeadLetterQueue -> System Event Bus integration bridge.

Connects the existing DeadLetterQueue (438 lines, shared/events/dlq.py)
to the system event observer (shared/infra/observer.py) so that failed
events are automatically persisted to DLQ.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from zephyr.shared.events.dlq import DeadLetterQueue

__all__ = [
    "DLQEventBridge",
    "attach_dlq_to_observer",
    "make_dlq_event_handler",
]

_logger = logging.getLogger(__name__)


def make_dlq_event_handler(dlq: DeadLetterQueue) -> Callable[[str, Any, Exception], None]:
    def _handler(event_name: str, payload: Any, error: Exception) -> None:
        try:
            error_msg = f"{type(error).__name__}: {error}"
            dlq.enqueue(
                event_type=event_name,
                payload=payload,
                error=error_msg,
            )
        except Exception as exc:
            _logger.error("DLQ event handler failed: event=%s error=%s", event_name, exc)

    return _handler


class DLQEventBridge:
    def __init__(self, dlq: DeadLetterQueue, observer: Any | None = None) -> None:
        self._dlq = dlq
        self._observer = observer
        self._attached = False

    def attach(self, observer: Any | None = None) -> None:
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
        except Exception as exc:
            _logger.error("DLQEventBridge.attach failed: %s", exc)

    @property
    def attached(self) -> bool:
        return self._attached

    def replay_failed(self) -> int:
        count = 0
        for entry in self._dlq.list_pending():
            try:
                self._dlq.retry(entry.id)
                count += 1
            except Exception as exc:
                _logger.warning("DLQ replay failed for entry %d: %s", entry.id, exc)
        return count


def attach_dlq_to_observer(
    dlq: DeadLetterQueue,
    observer: Any,
) -> DLQEventBridge:
    bridge = DLQEventBridge(dlq, observer)
    bridge.attach()
    return bridge
