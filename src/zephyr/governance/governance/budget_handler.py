# [A_module] module_id=MOD-GOV_budget_handler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [MODULE] zephyr.governance.governance.budget_handler

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-006 消费端 — Escalation.on_budget_alert() 预算告急升级处理."""

import logging
from typing import Any

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert
from zephyr.governance.contracts import EscalationContracts

_logger = logging.getLogger(__name__)
_escalation = EscalationContracts()

def on_budget_alert(alert: BudgetAlert) -> dict[str, Any]:
    result = _escalation.on_budget_alert(alert)

    try:
        from zephyr.governance.adapter import escalate_if_needed

        decision = escalate_if_needed("budget_exceeded", str(alert), owner_id="budget-handler")
        result["escalation_level"] = decision.escalation_level
        result["should_block"] = decision.should_block
    except ImportError:
        _logger.debug("escalation adapter not available for budget alert")
    except Exception:
        pass

    return result
