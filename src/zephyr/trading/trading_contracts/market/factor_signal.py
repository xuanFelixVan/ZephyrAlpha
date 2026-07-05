# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.market.factor_signal
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] signal; _cross_layer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_factor_signal | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-002 ====
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FactorSignal:
    as_of_date: datetime
    factor_id: str
    idempotency_key: str
    raw_value: float
    symbol: str
    confidence: float = 1.0
    exceptions: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)
    factor_version: str = "1.0"
    is_valid: bool = True
    max_retries: int = 2
    normalized_value: float | None = None
    rank_pct: float | None = None
    retry_policy: str = "linear"
    schema_version: str = "1.0"
    timeout_ms: int = 3000
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-002 ====
