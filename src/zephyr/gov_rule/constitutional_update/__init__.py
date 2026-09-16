# [A_module] module_id=MOD-GOV-constitutional_update | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RULE_DOMAIN | docs/03_modules/_domain_governance/rule/blueprint.md
# [MODULE] zephyr.gov_rule.constitutional_update
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_gov_rule/algo_flow/constitutional_update__init__.yaml
"""

from zephyr.gov_rule.constitutional_update.constitutional_update import (
    ConstitutionalAutoUpdate,
    Learning,
    ProposedUpdate,
)

__all__ = ["ConstitutionalAutoUpdate", "Learning", "ProposedUpdate", "constitutional_update"]
