# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.observability_governance.objective_tracker
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 目标漂移检测不可跳过;余弦相似度阈值不可手动覆盖
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Objective Tracker — v0.9.0 目标漂移检测器: agent目标函数稳定性+变更检测+rollback。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: objective_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① ObjectiveTracker
#   name_en: ObjectiveTracker
#   intro: class ObjectiveTracker 源码 L51-L83
#   desc: 公共方法（定义序）: objectives, versions, set_objective, detect_drift, rollback；源码 L51-L83
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ObjectiveTracker
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class ObjectiveTracker:
    def __init__(self):
        self._objectives: dict[str, list[str]] = {}
        self._versions: dict[str, int] = {}

    # ── Stage 4 公共化属性 ──

    @property
    def objectives(self) -> dict[str, list[str]]:
        """每 agent 目标列表（public API, Stage 4）."""
        return self._objectives

    @property
    def versions(self) -> dict[str, int]:
        """每 agent 版本号（public API, Stage 4）."""
        return self._versions

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
