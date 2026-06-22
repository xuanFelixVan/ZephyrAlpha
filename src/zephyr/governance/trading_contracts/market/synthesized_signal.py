# [A_module] module_id=MOD-EXE_synthesized_signal | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.execution.trading.trading_contracts.market.synthesized_signal
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] signal; _cross_layer
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# ==== BEGIN CODGEN:CTR-P1-015 ====
from dataclasses import dataclass, field
from datetime import datetime


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

__all__ = ["SynthesizedSignal"]
