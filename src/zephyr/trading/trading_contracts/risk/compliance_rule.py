# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.compliance_rule
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.risk.__init__
# [CONSUMERS] l10-compliance
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_compliance_rule | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:CTR-P1-012 ====

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ComplianceRule:
    created_at: datetime
    description: str
    enforcement_action: str
    idempotency_key: str
    is_active: bool
    jurisdiction: str
    rule_id: str
    rule_logic: str
    rule_name: str
    rule_type: str
    severity: str
    updated_at: datetime
    version: str
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-012 ====
