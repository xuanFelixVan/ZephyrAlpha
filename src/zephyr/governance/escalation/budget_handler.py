"""G-CT-006 消费端 — Escalation.on_budget_alert() 预算告急升级处理."""

from __future__ import annotations

import logging
from typing import Any

from zephyr.governance.budget_enforcer.alerts import BudgetAlert
from zephyr.governance.escalation.contracts import EscalationContracts

_logger = logging.getLogger(__name__)
_escalation = EscalationContracts()


def on_budget_alert(alert: BudgetAlert) -> dict[str, Any]:
    result = _escalation.on_budget_alert(alert)

    try:
        from zephyr.escalation_engine.adapter import escalate_if_needed

        decision = escalate_if_needed("budget_exceeded", str(alert), owner_id="budget-handler")
        result["escalation_level"] = decision.escalation_level
        result["should_block"] = decision.should_block
    except ImportError:
        _logger.debug("escalation adapter not available for budget alert")
    except Exception:
        pass

    return result
