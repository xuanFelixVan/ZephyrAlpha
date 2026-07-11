# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.scope_creep_monitor
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.gates.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_scope_creep_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Scope Creep Monitor — v0.15.0 R220

Blindspot: Autonomous repairs grow in scope over time; permission boundaries drift.
Risk: R220 — L2 repair slowly grows to L4 scope; autonomy level silently escalates.

Mitigation: Permission boundary tracking; alert when repair scope exceeds authorized level.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScopeEvent:
    action_id: str
    authorized_level: int
    actual_scope: int
    timestamp: str = ""


@dataclass
class ScopeCreepMonitor:
    events: list[ScopeEvent] = field(default_factory=list)
    max_tolerance: int = 1

    def audit(self, action_id: str, authorized_level: int, actual_scope: int) -> bool:
        event = ScopeEvent(action_id=action_id, authorized_level=authorized_level, actual_scope=actual_scope)
        self.events.append(event)
        return actual_scope <= authorized_level + self.max_tolerance

    def violation_count(self) -> int:
        return sum(1 for e in self.events if e.actual_scope > e.authorized_level + self.max_tolerance)
