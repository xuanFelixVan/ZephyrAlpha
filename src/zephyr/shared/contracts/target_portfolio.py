# ==== BEGIN CODGEN:CTR-007 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.target_portfolio
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
from typing import Dict, Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
from zephyr.shared.contracts.risk_limits import RiskLimits

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-08-03"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/target_portfolio.py

CTR-007: TargetPortfolio / 目标组合

组合优化器输出的目标组合契约。不可变快照，代表某次再平衡决策产生的目标权重及漂移信息，由 Execution/Position/Reporting 消费。

SSoT: cross_layer_contracts.yaml -> CTR-007
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 Portfolio 中产出目标组合或在 Execution/Position/Reporting 中消费目标组合时，MUST 使用 TargetPortfolio 类型。 TargetPortfolio 是不可变对象（frozen=true），代表组合优化器一次再平衡决策的完整输出。 target_weights 是优化后的目标权重 {symbol: weight}，权重之和应归一化到 [0, max_gross_leverage]。 current_weights 是决策时刻的当前持仓权重，drift_pct 是两者之间的加权漂移百分比。 risk_limits 字段引用本次优化所遵循的风险限额（CTR-003），下游 MUST 据此做合规校验，不得自行构造限额。 rebalance_reason 记录触发本次再平衡的原因（drift_threshold/calendar/event/risk_breach）。 idempotency_key 保证同一再平衡决策不会被重复执行——下游 MUST 校验幂等键避免重复下单。 消费方若发现 target_weights 与 risk_limits 冲突（如某标的超 max_single_position），MUST 拒绝并上报 RiskLimitViolationError（CTR-ERR-004）。
"""


@dataclass(frozen=True)
class TargetPortfolio:
    created_at: datetime
    drift_pct: float
    idempotency_key: str
    portfolio_id: str
    rebalance_reason: str
    risk_limits: RiskLimits
    strategy_id: str
    current_weights: dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"
    target_weights: dict[str, float] = field(default_factory=dict)
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-007 ====
