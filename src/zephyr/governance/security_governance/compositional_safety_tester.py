# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.compositional_safety_tester
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 组合安全测试不可跳过;pairwise覆盖必须完整
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_compositional_safety_tester | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Compositional Safety Tester — v0.14.0 组合性不安全测试器。
"""

from __future__ import annotations


class CompositionalSafetyTester:
    INDIVIDUALLY_SAFE = ["read_config", "write_log", "send_metric"]
    DANGEROUS_COMBOS = [
        ({"read_config", "write_log"}, "config_modification"),
        ({"read_config", "send_metric"}, "config_exfiltration"),
    ]

    def test_composition(self, operations: set[str]) -> list[str]:
        risks = []
        for combo, description in self.DANGEROUS_COMBOS:
            if combo.issubset(operations):
                risks.append(description)
        return risks

    def is_safe_combination(self, operations: set[str]) -> bool:
        return len(self.test_composition(operations)) == 0
