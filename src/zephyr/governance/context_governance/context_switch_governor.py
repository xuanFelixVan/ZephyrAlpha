# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_switch_governor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 上下文切换预算不可超限;daily_capacity=16不可修改
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Context Switch Governor — v0.11.0 Owner上下文切换预算管理器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: context_switch_governor.py
# 层: 算法
# - id: A1
#   name_zh: ① ContextSwitchGovernor
#   name_en: ContextSwitchGovernor
#   intro: class ContextSwitchGovernor 源码 L51-L82
#   desc: 公共方法（定义序）: daily_switches, max_switches_per_owner, can_switch, record_switch；源码 L51-L82
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ContextSwitchGovernor
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class ContextSwitchGovernor:
    def __init__(self):
        self._daily_switches: dict[str, int] = {}
        self._max_switches_per_owner = 12

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def daily_switches(self) -> dict[str, int]:
        """只读：daily_switches（Stage 4 公共化）。"""
        return self._daily_switches

    @daily_switches.setter
    def daily_switches(self, value):
        """写入：daily_switches（Stage 4 公共化）。"""
        self._daily_switches = value

    @property
    def max_switches_per_owner(self):
        """只读：max_switches_per_owner（Stage 4 公共化）。"""
        return self._max_switches_per_owner

    @max_switches_per_owner.setter
    def max_switches_per_owner(self, value):
        """写入：max_switches_per_owner（Stage 4 公共化）。"""
        self._max_switches_per_owner = value

    def can_switch(self, owner_id: str) -> bool:
        current = self._daily_switches.get(owner_id, 0)
        return current < self._max_switches_per_owner

    def record_switch(self, owner_id: str):
        self._daily_switches[owner_id] = self._daily_switches.get(owner_id, 0) + 1
