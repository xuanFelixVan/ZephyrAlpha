# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_drift.autonomy_regressor
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 渐进自治可逆性必须保证;回归触发器不可禁用
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Autonomy Regressor — v0.10.0 渐进自治可逆性管理器: confidence<阈值->自动regress自治级别。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: autonomy_regressor.py
# 层: 算法
# - id: A1
#   name_zh: ① AutonomyRegressor
#   name_en: AutonomyRegressor
#   intro: class AutonomyRegressor 源码 L51-L64
#   desc: 公共方法（定义序）: should_regress, regression_path；源码 L51-L64
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AutonomyRegressor
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class AutonomyRegressor:
    LEVELS = ["autonomous", "auto_guard", "blocked"]

    def should_regress(self, current_level: str, confidence: float, error_count: int) -> str:
        idx = self.LEVELS.index(current_level) if current_level in self.LEVELS else 0
        if confidence < 0.3 and idx < len(self.LEVELS) - 1:
            return self.LEVELS[idx + 1]
        if error_count > 5 and idx < len(self.LEVELS) - 1:
            return self.LEVELS[idx + 1]
        return current_level

    def regression_path(self, level: str) -> list[str]:
        idx = self.LEVELS.index(level) if level in self.LEVELS else 0
        return self.LEVELS[idx:]
