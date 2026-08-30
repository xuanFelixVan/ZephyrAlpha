# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.architecture_governance.blueprint_bloat_monitor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 蓝图膨胀监控不可禁用;max=100不可修改
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Blueprint Bloat Monitor — v0.11.0 蓝图膨胀监控器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: blueprint_bloat_monitor.py
# 层: 算法
# - id: A1
#   name_zh: ① BlueprintBloatMonitor
#   name_en: BlueprintBloatMonitor
#   intro: class BlueprintBloatMonitor 源码 L51-L64
#   desc: 公共方法（定义序）: check_bloat, should_refactor；源码 L51-L64
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: BlueprintBloatMonitor
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class BlueprintBloatMonitor:
    MAX_BLUEPRINT_LINES = 5000
    MAX_TASK_CARDS = 50

    def check_bloat(self, blueprint_lines: int, task_cards: int) -> dict:
        return {
            "blueprint_ok": blueprint_lines <= self.MAX_BLUEPRINT_LINES,
            "task_cards_ok": task_cards <= self.MAX_TASK_CARDS,
            "lines": blueprint_lines,
            "cards": task_cards,
        }

    def should_refactor(self, blueprint_lines: int) -> bool:
        return blueprint_lines > self.MAX_BLUEPRINT_LINES
