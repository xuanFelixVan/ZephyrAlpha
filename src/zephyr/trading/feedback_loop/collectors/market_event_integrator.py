# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.market_event_integrator
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_market_event_integrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Market Event Integrator — v0.14.0 R197

Blindspot: FLE unaware of market events (circuit breaker, FOMC, holidays); normal operations during chaos.
Risk: R197 — Market-wide circuit breaker tripped; FLE diagnoses "missing data" as pipeline failure.

Mitigation: Market calendar + event-driven mode switching for FLE behavior.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class MarketMode(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    EMERGENCY = "EMERGENCY"
    HOLIDAY = "HOLIDAY"


@dataclass
class MarketEvent:
    event_type: str
    timestamp: float
    mode: MarketMode
    description: str


@dataclass
class MarketEventIntegrator:
    events: list[MarketEvent] = field(default_factory=list)
    current_mode: MarketMode = MarketMode.NORMAL

    def on_circuit_breaker(self, exchange: str) -> None:
        event = MarketEvent(
            event_type="CIRCUIT_BREAKER",
            timestamp=time.time(),
            mode=MarketMode.EMERGENCY,
            description=f"Circuit breaker triggered on {exchange}",
        )
        self.events.append(event)
        self.current_mode = MarketMode.EMERGENCY

    def on_fomc(self) -> None:
        event = MarketEvent(
            event_type="FOMC",
            timestamp=time.time(),
            mode=MarketMode.CAUTION,
            description="FOMC announcement window",
        )
        self.events.append(event)
        self.current_mode = MarketMode.CAUTION

    def on_holiday(self, holiday_name: str) -> None:
        event = MarketEvent(
            event_type="HOLIDAY",
            timestamp=time.time(),
            mode=MarketMode.HOLIDAY,
            description=f"Market holiday: {holiday_name}",
        )
        self.events.append(event)
        self.current_mode = MarketMode.HOLIDAY

    def should_suppress_anomaly(self, anomaly_type: str) -> bool:
        if self.current_mode is MarketMode.HOLIDAY:
            return anomaly_type in ("missing_data", "low_volume")
        if self.current_mode is MarketMode.EMERGENCY:
            return anomaly_type in ("high_volatility", "latency_spike")
        return False
