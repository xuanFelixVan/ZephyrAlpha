# ==== BEGIN CODGEN:CTR-001 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.market_data
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
from decimal import Decimal
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
ZephyrAlpha — shared/contracts/market_data.py

CTR-001: NormalizedMarketData / 标准化行情数据

D_DATA -> D_FACTOR 核心数据契约。质量门禁通过后的标准化行情数据。

SSoT: cross_layer_contracts.yaml -> CTR-001
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 D_FACTOR 中使用来自 D_DATA 的行情数据时，MUST 使用 NormalizedMarketData 类型。 该类型的 symbol 字段已由 D_DATA 标准化为 "600519.SH" 格式（证券代码.交易所），你不需要再做格式转换。 所有价格字段（open/high/low/close）和成交量（volume）使用 Decimal 类型——禁止用 float 做任何算术运算。 如果 quality_score < 0.7，该数据可能不可靠，请标记为低置信度。 如果 is_suspended = True，不要基于该数据生成任何信号，跳过该标的。 ingested_at 为数据入库时间，不一定等于 timestamp（数据时间戳），请使用 timestamp 做截面对齐。
"""

@dataclass(frozen=True)
class NormalizedMarketData:
    close: Decimal
    data_source: str
    high: Decimal
    idempotency_key: str
    low: Decimal
    open: Decimal
    symbol: str
    timestamp: datetime
    volume: Decimal
    adj_factor: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    config_load_retry_policy: str = "linear"
    config_load_timeout_ms: int = 1000
    exceptions: List[str] = field(default_factory=list)
    ingested_at: Optional[datetime] = None
    is_suspended: bool = False
    max_retries: int = 3
    quality_score: float = 1.0
    retry_policy: str = "exponential_backoff"
    schema_version: str = "1.0"
    timeout_ms: int = 5000
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-001 ====








