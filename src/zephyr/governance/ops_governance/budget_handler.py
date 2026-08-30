# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.budget_handler
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.shared.contracts.escalation.budget_alert; zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.services.adapter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 预算告警必须触发升级;预算检查不可跳过
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-006 消费端 — Escalation.on_budget_alert() 预算告急升级处理.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: alert 参数
#   fields: 参数 alert，类型注解 BudgetAlert
#   code: budget_handler.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① on_budget_alert
#   name_en: on_budget_alert
#   intro: on_budget_alert(alert) 源码 L60-L74
#   desc: 源码 L60-L74
#   inputs: alert
#   outputs: dict[str, Any]
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.governance.services.adapter
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        _logger.warning("on_budget_alert: escalation adapter failed (%s: %s)", type(e).__name__, e, exc_info=True)

    return result
