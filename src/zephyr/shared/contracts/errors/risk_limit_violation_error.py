from __future__ import annotations

from dataclasses import dataclass

from zephyr.shared.contracts.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/risk_limit_violation_error.py

CTR-ERR-004: RiskLimitViolationError / 风险限额突破错误

L04 检测到当前或计划操作将突破风险限额时抛出的硬错误。L05/L06 MUST 据此阻止订单生成和执行。

SSoT: cross-layer-contracts.yaml → CTR-ERR-004
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 L04 风控系统检测到任何风险约束被突破时，MUST 抛出 RiskLimitViolationError。 这是一个 HALT 级别的错误——下游（L05/L06）MUST 拒绝继续处理并停止当前调仓周期。 violated_constraint 精确指出是哪条规则被突破（position_limit / leverage_limit / var_breach / drawdown_trigger / sector_concentration）。 不要降级为 WARNING——如果这是代码逻辑导致的，降级等于资金安全风险。
"""

@dataclass(frozen=True)
class RiskLimitViolationError:
    error_id: str
    portfolio_id: str
    violated_constraint: str
    violation_detail: str
    limit_value: float
    actual_value: float
    recovery_hint: str
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None
