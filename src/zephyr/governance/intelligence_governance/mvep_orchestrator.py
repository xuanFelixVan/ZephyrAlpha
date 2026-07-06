# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.mvep_orchestrator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MVEP Phase Gate不可跳过;Phase 0→5顺序不可逆
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_mvep_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

MVEP Orchestrator — v0.11.0 Minimum Viable Escalation Protocol调度器。
"""

from __future__ import annotations

from typing import Final
MVE_SEQUENCE: Final[list] = [
    "D-022-01 engine",
    "D-022-02 delegation",
    "D-022-03 economic",
    "D-022-04 deadlock",
    "D-022-05 confidence",
]


class MVEPOrchestrator:
    def __init__(self):
        self._implemented: set[str] = set()

    def mark_implemented(self, decision_id: str):
        self._implemented.add(decision_id)

    def missing_mvps(self) -> list[str]:
        base = {d.split()[0] for d in MVE_SEQUENCE}
        return list(base - self._implemented)

    def all_implemented(self) -> bool:
        return len(self.missing_mvps()) == 0
