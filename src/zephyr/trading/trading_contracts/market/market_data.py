# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.market.market_data
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] factor; _cross_layer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_market_data | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-001 ====
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


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
    adj_factor: Decimal | None = None
    amount: Decimal | None = None
    config_load_retry_policy: str = "linear"
    config_load_timeout_ms: int = 1000
    exceptions: list[str] = field(default_factory=list)
    ingested_at: datetime | None = None
    is_suspended: bool = False
    max_retries: int = 3
    quality_score: float = 1.0
    retry_policy: str = "exponential_backoff"
    schema_version: str = "1.0"
    timeout_ms: int = 5000
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-001 ====
