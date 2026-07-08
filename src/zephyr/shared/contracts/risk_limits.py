# ==== BEGIN CODGEN:CTR-003 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.risk_limits
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from dataclasses import dataclass, field

from datetime import datetime, timezone
from typing import Dict
from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/risk_limits.py

CTR-003: RiskLimits / 风险限额

D_RISK -> D_PORTFOLIO_CORE 核心数据契约。风险限额约束集合，由 D_PORTFOLIO_CORE 组合优化器强制执行。

SSoT: cross_layer_contracts.yaml -> CTR-003
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 D_RISK 中定义风险限额或在 D_PORTFOLIO_CORE 中使用风险限额时，MUST 使用 RiskLimits 类型。 max_single_position 是单标的权重上限（如 0.10 = 10%），D_PORTFOLIO_CORE 组合优化器 MUST 确保不超此值。 max_gross_leverage 是总杠杆上限，默认为 1.0（满仓不加杠杆）。 symbol_overrides 用于个股特殊限制，key 为 symbol，value 为 max_weight。 如果 D_PORTFOLIO_CORE 组合优化器检测到任何约束被突破，MUST 抛出 RiskLimitViolationError（CTR-ERR-004），阻止订单生成。 max_drawdown_limit 触发时，系统应进入风控熔断状态。
"""

@dataclass(frozen=True)
class RiskLimits:
    as_of_date: datetime
    idempotency_key: str
    max_drawdown_limit: Optional[float] = None
    max_gross_leverage: float = 1.0
    max_portfolio_var_1d: Optional[float] = None
    max_sector_concentration: float = 0.3
    max_single_position: float = 0.1
    min_single_position: float = 0.0
    schema_version: str = "1.0"
    symbol_overrides: Dict[str, float] = field(default_factory=dict)
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-003 ====








