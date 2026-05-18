# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.market.factor_signal

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l03_signal_generation; _cross_layer

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
# ==== BEGIN CODGEN:CTR-002 ====
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from zephyr.shared.contracts.core.trace_context import TraceContext

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
