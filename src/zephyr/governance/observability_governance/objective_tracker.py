# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.observability_governance.objective_tracker
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 目标漂移检测不可跳过;余弦相似度阈值不可手动覆盖
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_objective_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Objective Tracker — v0.9.0 目标漂移检测器: agent目标函数稳定性+变更检测+rollback。
"""

from __future__ import annotations


class ObjectiveTracker:
    def __init__(self):
        self._objectives: dict[str, list[str]] = {}
        self._versions: dict[str, int] = {}

    def set_objective(self, agent_id: str, objective: str):
        if agent_id not in self._objectives:
            self._objectives[agent_id] = []
        self._objectives[agent_id].append(objective)
        self._versions[agent_id] = self._versions.get(agent_id, 0) + 1

    def detect_drift(self, agent_id: str) -> bool:
        objs = self._objectives.get(agent_id, [])
        return len(objs) > 1

    def rollback(self, agent_id: str) -> str:
        objs = self._objectives.get(agent_id, [])
        if len(objs) >= 2:
            objs.pop()
            self._versions[agent_id] = max(0, self._versions.get(agent_id, 1) - 1)
        return objs[-1] if objs else ""
