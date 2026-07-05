# ==== BEGIN CODGEN:CTR-002 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.factor_signal
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
from typing import Any
from typing import Dict
from typing import List
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
ZephyrAlpha — shared/contracts/factor_signal.py

CTR-002: FactorSignal / 因子信号

D_FACTOR → D_SIGNAL/D_RISK/D_PORTFOLIO_CORE 核心数据契约。单个因子在单个时间截面对单个标的的信号值。

SSoT: cross_layer_contracts.yaml -> CTR-002
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 D_FACTOR 中生成因子信号时，MUST 使用 FactorSignal 类型。 不要自行定义因子信号的数据结构。factor_id 必须对应 FactorRegistry 中已注册的因子 key。 raw_value 是因子原始计算结果，normalized_value 是截面标准化后的 z-score，rank_pct 是 0-1 分位数排名。 如果因子计算失败，不要产出 FactorSignal——应该抛出 FactorComputationError（CTR-ERR-002）。 如果 confidence < 0.5，该信号可能不可靠，下游（D_SIGNAL/D_RISK/D_PORTFOLIO_CORE）可以忽略。 is_valid = False 时下游 MUST 跳过该信号。 extra 字段用于放非标准化的扩展数据，不要滥用——能用标准字段就用标准字段。
"""

@dataclass(frozen=True)
class FactorSignal:
    as_of_date: datetime
    factor_id: str
    idempotency_key: str
    raw_value: float
    symbol: str
    confidence: float = 1.0
    exceptions: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)
    factor_version: str = "1.0"
    is_valid: bool = True
    max_retries: int = 2
    normalized_value: Optional[float] = None
    rank_pct: Optional[float] = None
    retry_policy: str = "linear"
    schema_version: str = "1.0"
    timeout_ms: int = 3000
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-002 ====








