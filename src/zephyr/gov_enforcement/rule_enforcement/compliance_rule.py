# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.compliance_rule
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.contracts.compliance_rule
# [CONSUMERS] l10-compliance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.compliance_rule
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.compliance_rule
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_compliance_rule | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — ComplianceRule 真源已合并至 zephyr.shared.contracts.compliance_rule。

SSoT: cross_layer_contracts.yaml -> CTR-P1-012
canonical: src/zephyr/shared/contracts/compliance_rule.py
"""

from zephyr.shared.contracts.compliance_rule import ComplianceRule  # noqa: F401

__all__ = ["ComplianceRule"]
