# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] zephyr.infrastructure.a2a_protocol.phase_hold
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.__init__
# [CONSUMERS] zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Phase4Hold 状态转换必须合法; hold 释放必须通过验证门禁
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 agent_id 和 protocol_layer
# [TESTS] tests/test_a2a_protocol.py
# [A_module] module_id=MOD-INF_phase_hold | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3

Phase 4 Hold — A2A Phase 4 锁定标记模块 与其他 Phase 3 模块不可并发施工.

"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

PHASE_HOLD_ACTIVE = True


PHASE_HOLD_REASON = "A2A module locked to Phase 4 — cannot be built concurrently with Phase 3 modules (Drift, Budget, Rollback, Escalation)"


class Phase4Hold:
    """A2A Phase 4 施工锁定."""

    def __init__(self) -> None:
        self.hold_active = PHASE_HOLD_ACTIVE

        self.hold_since = datetime.now(UTC).isoformat()

    def check(self) -> dict[str, Any]:
        return {
            "hold_active": self.hold_active,
            "reason": PHASE_HOLD_REASON,
            "hold_since": self.hold_since,
        }

    def can_proceed(self, current_phase: str) -> bool:
        return current_phase in ("Phase4", "phase4", "4") and self.hold_active
