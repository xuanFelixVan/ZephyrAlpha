# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.maintenance_window_adapter
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 维护窗口适配不可跳过;阈值调整必须审计
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Maintenance Window Adapter — v0.10.0 计划维护窗口适配器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: maintenance_window_adapter.py
# 层: 算法
# - id: A1
#   name_zh: ① MaintenanceWindowAdapter
#   name_en: MaintenanceWindowAdapter
#   intro: class MaintenanceWindowAdapter 源码 L51-L68
#   desc: 公共方法（定义序）: start_maintenance, end_maintenance, in_maintenance, adjust_escalation；源码 L51-L68
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: MaintenanceWindowAdapter
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class MaintenanceWindowAdapter:
    def __init__(self):
        self._in_maintenance = False

    def start_maintenance(self) -> None:
        self._in_maintenance = True

    def end_maintenance(self) -> None:
        self._in_maintenance = False

    @property
    def in_maintenance(self) -> bool:
        return self._in_maintenance

    def adjust_escalation(self, original_level: str) -> str:
        if self._in_maintenance and original_level == "auto_guard":
            return "autonomous"
        return original_level
