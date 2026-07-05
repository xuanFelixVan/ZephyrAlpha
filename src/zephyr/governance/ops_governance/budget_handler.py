# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.budget_handler
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.shared.contracts.escalation.budget_alert; zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.services.adapter
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 预算告警必须触发升级;预算检查不可跳过
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_budget_handler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

G-CT-006 消费端 — Escalation.on_budget_alert() 预算告急升级处理.
"""

from __future__ import annotations

import logging
from typing import Any

from zephyr.governance.escalation.contracts import EscalationContracts
from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert

_logger = logging.getLogger(__name__)
_escalation = EscalationContracts()


def on_budget_alert(alert: BudgetAlert) -> dict[str, Any]:
    result = _escalation.on_budget_alert(alert)

    try:
        from zephyr.governance.services.adapter import escalate_if_needed

        decision = escalate_if_needed("budget_exceeded", str(alert), owner_id="budget-handler")
        result["escalation_level"] = decision.escalation_level
        result["should_block"] = decision.should_block
    except ImportError:
        _logger.debug("escalation adapter not available for budget alert")
    except Exception as e:
        _logger.warning("on_budget_alert: escalation adapter failed (%s: %s)", type(e).__name__, e, exc_info=True)

    return result
