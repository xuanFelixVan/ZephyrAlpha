# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.escalation.budget_alert
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.budget_enforcement.alerts;zephyr.infrastructure.budget_enforcement.bridges.alerts;zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 告警阈值不可被静默;告警事件必须可审计
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] 异常必须包含 budget_context 和 operation_id
# [TESTS] tests/test_budget_enforcer.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: budget_alert.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: BudgetSeverity, BudgetType, BudgetAlert
#   desc: 数据契约/异常/枚举声明共 3 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（3 类）
#   name_en: data classes
#   intro: BudgetSeverity, BudgetType, BudgetAlert
#   downstream: zephyr.infrastructure.budget_enforcement.alerts;zephyr.infrastructure.budget_en…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class BudgetSeverity(str, Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class BudgetType(str, Enum):
    TOKEN = "TOKEN"
    TIME = "TIME"
    MEMORY = "MEMORY"
    API_CALLS = "API_CALLS"


class BudgetAlert(BaseModel):
    alert_id: str
    detected_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str = ""
    budget_type: BudgetType = BudgetType.TOKEN
    burn_rate: float = 0.0
    burn_rate_threshold: float = 0.8
    remaining_budget: float = 0.0
    severity: BudgetSeverity = BudgetSeverity.WARNING

    @classmethod
    def from_burn_rate(
        cls,
        alert_id: str,
        burn_rate: float,
        threshold: float,
        remaining: float,
        session_id: str = "",
        budget_type: BudgetType = BudgetType.TOKEN,
    ) -> BudgetAlert:
        if remaining <= 0:
            severity = BudgetSeverity.CRITICAL
        elif burn_rate > threshold:
            severity = BudgetSeverity.WARNING
        else:
            severity = BudgetSeverity.WARNING

        return cls(
            alert_id=alert_id,
            session_id=session_id,
            budget_type=budget_type,
            burn_rate=burn_rate,
            burn_rate_threshold=threshold,
            remaining_budget=remaining,
            severity=severity,
        )
