from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime, timezone

from zephyr.shared.contracts.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/risk_limits.py

CTR-003: RiskLimits / 风险限额

L04 → L05 核心数据契约。风险限额约束集合，由 L05 组合优化器强制执行。

SSoT: cross-layer-contracts.yaml → CTR-003
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 L04 中定义风险限额或在 L05 中使用风险限额时，MUST 使用 RiskLimits 类型。 max_single_position 是单标的权重上限（如 0.10 = 10%），L05 组合优化器 MUST 确保不超此值。 max_gross_leverage 是总杠杆上限，默认为 1.0（满仓不加杠杆）。 symbol_overrides 用于个股特殊限制，key 为 symbol，value 为 max_weight。 如果 L05 组合优化器检测到任何约束被突破，MUST 抛出 RiskLimitViolationError（CTR-ERR-004），阻止订单生成。 max_drawdown_limit 触发时，系统应进入风控熔断状态。
"""

@dataclass(frozen=True)
class RiskLimits:
    as_of_date: datetime
    max_single_position: float = 0.1
    min_single_position: float = 0.0
    max_gross_leverage: float = 1.0
    max_sector_concentration: float = 0.3
    schema_version: str = "1.0"
    max_portfolio_var_1d: Optional[float] = None
    max_drawdown_limit: Optional[float] = None
    symbol_overrides: Dict[str, float] = field(default_factory=dict)
    trace_context: Optional[TraceContext] = None
