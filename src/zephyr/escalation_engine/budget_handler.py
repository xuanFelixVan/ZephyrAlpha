# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.budget_handler

# [INVARIANTS] 预算告警必须触发升级;预算检查不可跳过

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine.adapter

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

G-CT-006 消费端 — Escalation.on_budget_alert() 预算告急升级处理.
"""

from __future__ import annotations

import logging
from typing import Any

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert
from zephyr.escalation_engine.contracts import EscalationContracts

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
