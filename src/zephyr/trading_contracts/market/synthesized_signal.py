# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.market.synthesized_signal

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l03_signal_generation; _cross_layer

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
# ==== BEGIN CODGEN:CTR-P1-015 ====
from dataclasses import dataclass, field
from datetime import datetime

from zephyr.shared.contracts.core.trace_context import TraceContext

@dataclass(frozen=True)
class SynthesizedSignal:
    as_of_timestamp: datetime
    confidence: float
    generation_latency_ms: int
    idempotency_key: str
    signal_direction: str
    signal_id: str
    signal_value: float
    symbol: str
    contributing_factors: dict[str, float] = field(default_factory=dict)
    is_degraded: bool = False
    regime: str = ""
    schema_version: str = "1.0"
    suggested_position_pct: float = 0
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-P1-015 ====
