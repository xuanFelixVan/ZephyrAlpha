# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.rule_engine.rule_debt_auditor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 规则债务审计不可跳过;过时规则必须标记
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_rule_debt_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Rule Debt Auditor — v0.7.0 规则债务审计器: 分析escalation_rules.yaml维护债务指标。
"""

from __future__ import annotations


class RuleDebtAuditor:
    def audit(self, rules: list[dict]) -> dict:
        total = len(rules)
        levels = {r.get("level", "unknown") for r in rules}
        duplicate_patterns = set()
        all_patterns = []
        for r in rules:
            for p in r.get("patterns", []):
                if p in all_patterns:
                    duplicate_patterns.add(p)
                all_patterns.append(p)
        return {
            "total_rules": total,
            "unique_levels": len(levels),
            "duplicate_patterns": len(duplicate_patterns),
            "debt_score": len(duplicate_patterns) / max(1, total),
        }
