# [A_module] module_id=MOD-INF_event_reactor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] SRC-096 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md

# [MODULE] zephyr.infrastructure.shared_services.events.event_reactor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Event Reactor — 事件反应器（自动响应事件）。

依据：
    蓝图 MOD-INF-006 §6.13.4 + v0.6.0
    任务卡 TASK-INF-0125
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from zephyr.shared.shared_services.events.event_bus import DomainEvent, EventBus, EventType

@dataclass
class Reaction:
    reaction_id: str
    trigger_event: EventType
    action: str
    executed: bool = False
    timestamp_utc: str = ""

class EventReactor:

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._bus = event_bus or EventBus.get_instance()
        self._reactions: list[Reaction] = []
        self._register_handlers()

    def _register_handlers(self) -> None:
        self._bus.subscribe(EventType.TASK_FAILED, self._on_task_failed)
        self._bus.subscribe(EventType.TASK_COMPLETED, self._on_task_completed)
        self._bus.subscribe(EventType.SCOPE_DRIFT, self._on_scope_drift)
        self._bus.subscribe(EventType.DEPENDENCY_RESOLVED, self._on_dependency_resolved)

    def _on_task_failed(self, event: DomainEvent) -> None:
        self._log_reaction(EventType.TASK_FAILED, f"Notify owner about failure: {event.task_id}")

    def _on_task_completed(self, event: DomainEvent) -> None:
        self._log_reaction(EventType.TASK_COMPLETED, f"Update journal: {event.task_id}")

    def _on_scope_drift(self, event: DomainEvent) -> None:
        extras = event.payload.get("extra_touch", [])
        self._log_reaction(
            EventType.SCOPE_DRIFT,
            f"Alert: scope drift detected for {event.task_id} — extra files: {extras}"
        )

    def _on_dependency_resolved(self, event: DomainEvent) -> None:
        self._log_reaction(
            EventType.DEPENDENCY_RESOLVED,
            f"Unblock dependent tasks for {event.task_id}"
        )

    def _log_reaction(self, trigger: EventType, action: str) -> None:
        reaction = Reaction(
            reaction_id=f"REACT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            trigger_event=trigger,
            action=action,
            executed=True,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )
        self._reactions.append(reaction)

    def get_reactions(self) -> list[Reaction]:
        return list(self._reactions)
