# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_drift.autonomy_regressor
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 渐进自治可逆性必须保证;回归触发器不可禁用
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_autonomy_regressor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Autonomy Regressor — v0.10.0 渐进自治可逆性管理器: confidence<阈值->自动regress自治级别。
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
