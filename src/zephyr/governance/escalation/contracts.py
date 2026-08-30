# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.contracts
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.shared.contracts.rollback_types; zephyr.shared.contracts.escalation.budget_alert
# [CONSUMERS] zephyr.infrastructure.rollback;zephyr.governance.services.adapter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 契约接口签名不可变;升级入口必须返回结构化结果
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-003 消费端 — Escalation.on_rollback_failure() + G-CT-004/G-CT-006/G-CT-008 升级入口.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: contracts.py
# 层: 算法
# - id: A1
#   name_zh: ① EscalationContracts
#   name_en: EscalationContracts
#   intro: 升级协议入口 — G-CT-003/004/006/008 消费端.
#   desc: 升级协议入口 — G-CT-003/004/006/008 消费端.；公共方法（定义序）: on_rollback_failure, on_budget_alert, on_a2a_failure；源码 L58-L105
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: EscalationContracts
#   downstream: zephyr.infrastructure.rollback;zephyr.governance.services.adapter
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Any

# G-CT-002: RollbackHandler re-export from infrastructure.rollback.contracts
# (SSoT: tests/governance/audit/test_gct_002_audit_to_rollback.py imports from here)
from zephyr.infrastructure.rollback.contracts import RollbackHandler  # noqa: E402,F401
from zephyr.shared.contracts.rollback_types import RollbackResult


class EscalationContracts:
    """升级协议入口 — G-CT-003/004/006/008 消费端."""

    def on_rollback_failure(self, result: RollbackResult) -> dict[str, Any]:
        if not result.needs_escalation:
            return {"escalated": False, "reason": "no_escalation_needed", "rollback_id": result.rollback_id}

        return {
            "escalated": True,
            "rollback_id": result.rollback_id,
            "target": result.target,
            "status": result.status.value,
            "validation_result": result.validation_result.value,
            "error_detail": result.error_detail,
            "ticket_id": f"ESC-{result.rollback_id}",
            "priority": "P1" if result.status.value == "FAILED" else "P2",
        }

    def on_budget_alert(self, alert: object) -> dict[str, Any]:
        from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert

        if not isinstance(alert, BudgetAlert):
            return {"escalated": False, "reason": "invalid_alert_type"}

        severity = alert.severity.value
        response = {
            "escalated": True,
            "alert_id": alert.alert_id,
            "session_id": alert.session_id,
            "severity": severity,
            "action": "notify" if severity == "WARNING" else "escalate",
        }

        if severity == "CRITICAL":
            response["ticket_id"] = f"ESC-BUDGET-{alert.alert_id}"
            response["priority"] = "P0"

        return response

    def on_a2a_failure(self, communication: object) -> dict[str, Any]:
        return {
            "escalated": True,
            "a2a_id": getattr(communication, "a2a_id", ""),
            "from_agent": getattr(communication, "from_agent_id", ""),
            "to_agent": getattr(communication, "to_agent_id", ""),
            "action": "retry_or_degrade",
            "ticket_id": f"ESC-A2A-{getattr(communication, 'a2a_id', 'unknown')}",
        }
