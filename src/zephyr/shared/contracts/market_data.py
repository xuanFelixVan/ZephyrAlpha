from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from zephyr.shared.contracts.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/market_data.py

CTR-001: NormalizedMarketData / 标准化行情数据

L00 → L02 核心数据契约。质量门禁通过后的标准化行情数据。

SSoT: cross-layer-contracts.yaml → CTR-001
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 L02 中使用来自 L00 的行情数据时，MUST 使用 NormalizedMarketData 类型。 该类型的 symbol 字段已由 L00 标准化为 "600519.SH" 格式（证券代码.交易所），你不需要再做格式转换。 所有价格字段（open/high/low/close）和成交量（volume）使用 Decimal 类型——禁止用 float 做任何算术运算。 如果 quality_score < 0.7，该数据可能不可靠，请标记为低置信度。 如果 is_suspended = True，不要基于该数据生成任何信号，跳过该标的。 ingested_at 为数据入库时间，不一定等于 timestamp（数据时间戳），请使用 timestamp 做截面对齐。
"""


@dataclass(frozen=True)
class NormalizedMarketData:
    symbol: str
    data_source: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    quality_score: float = 1.0
    is_suspended: bool = False
    timeout_ms: int = 5000
    retry_policy: str = "exponential_backoff"
    config_load_timeout_ms: int = 1000
    config_load_retry_policy: str = "linear"
    max_retries: int = 3
    schema_version: str = "1.0"
    amount: Optional[Decimal] = None
    adj_factor: Optional[Decimal] = None
    ingested_at: Optional[datetime] = None
    trace_context: Optional[TraceContext] = None
    exceptions: List[str] = field(default_factory=list)
