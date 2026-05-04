from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime, timezone
from typing import Any

from zephyr.shared.contracts.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/factor_signal.py

CTR-002: FactorSignal / 因子信号

L02 → L03/L04/L05 核心数据契约。单个因子在单个时间截面对单个标的的信号值。

SSoT: cross-layer-contracts.yaml → CTR-002
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 L02 中生成因子信号时，MUST 使用 FactorSignal 类型。 不要自行定义因子信号的数据结构。factor_id 必须对应 FactorRegistry 中已注册的因子 key。 raw_value 是因子原始计算结果，normalized_value 是截面标准化后的 z-score，rank_pct 是 0-1 分位数排名。 如果因子计算失败，不要产出 FactorSignal——应该抛出 FactorComputationError（CTR-ERR-002）。 如果 confidence < 0.5，该信号可能不可靠，下游（L03/L04/L05）可以忽略。 is_valid = False 时下游 MUST 跳过该信号。 extra 字段用于放非标准化的扩展数据，不要滥用——能用标准字段就用标准字段。
"""

@dataclass(frozen=True)
class FactorSignal:
    factor_id: str
    symbol: str
    as_of_date: datetime
    raw_value: float
    confidence: float = 1.0
    is_valid: bool = True
    factor_version: str = "1.0"
    timeout_ms: int = 3000
    retry_policy: str = "linear"
    max_retries: int = 2
    schema_version: str = "1.0"
    normalized_value: Optional[float] = None
    rank_pct: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    trace_context: Optional[TraceContext] = None
    exceptions: List[str] = field(default_factory=list)
