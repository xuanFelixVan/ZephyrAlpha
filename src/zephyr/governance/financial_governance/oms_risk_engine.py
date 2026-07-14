# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.financial_governance.oms_risk_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.financial_governance.__init__
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
# [A_module] module_id=MOD-GOV_oms_risk_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RiskLayer(str, Enum):
    PRE_TRADE = "PRE_TRADE"
    AT_TRADE = "AT_TRADE"
    POST_TRADE = "POST_TRADE"


class OrderState(str, Enum):
    PENDING = "PENDING"
    ACK = "ACK"
    PARTIAL_FILL = "PARTIAL_FILL"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


TERMINAL_STATES: Final[set[OrderState]] = {OrderState.FILLED, OrderState.REJECTED, OrderState.CANCELLED}


class RiskCheckResult(BaseModel):
    passed: bool = True
    reason: str = ""
    layer: RiskLayer = RiskLayer.PRE_TRADE


class PreTradeCheck(BaseModel):
    position_cap_ok: bool = True
    risk_exposure_ok: bool = True
    funds_sufficient_ok: bool = True
    circuit_breaker_ok: bool = True

    def all_pass(self) -> bool:
        return self.position_cap_ok and self.risk_exposure_ok and self.funds_sufficient_ok and self.circuit_breaker_ok


class AtTradeCheck(BaseModel):
    price_deviation_bps: float = 0.0
    order_frequency_l1s: int = 0
    max_deviation_bps: int = 5000
    max_frequency_l1s: int = 10

    def all_pass(self) -> bool:
        return self.price_deviation_bps < self.max_deviation_bps and self.order_frequency_l1s < self.max_frequency_l1s


class PostTradeMetrics(BaseModel):
    pnl_attribution: dict[str, float] = Field(default_factory=dict)
    tca_slippage_bps: float = 0.0
    cumulative_slippage_bps: float = 0.0


class OMSRiskEngine:
    def pre_trade_check(self, check: PreTradeCheck) -> RiskCheckResult:
        if not check.all_pass():
            return RiskCheckResult(passed=False, reason="Pre-trade check failed", layer=RiskLayer.PRE_TRADE)
        return RiskCheckResult(passed=True, layer=RiskLayer.PRE_TRADE)

    def at_trade_check(self, check: AtTradeCheck) -> RiskCheckResult:
        if not check.all_pass():
            return RiskCheckResult(
                passed=False, reason="At-trade check failed — cancel order", layer=RiskLayer.AT_TRADE
            )
        return RiskCheckResult(passed=True, layer=RiskLayer.AT_TRADE)

    def post_trade_evaluate(self, metrics: PostTradeMetrics) -> None:
        logger.info(
            "Post-trade: slippage=%.2fbps cumulative=%.2fbps", metrics.tca_slippage_bps, metrics.cumulative_slippage_bps
        )


def is_terminal(state: OrderState) -> bool:
    return state in TERMINAL_STATES


def valid_transitions(current: OrderState, next_state: OrderState) -> bool:
    transitions = {
        OrderState.PENDING: {OrderState.ACK, OrderState.REJECTED},
        OrderState.ACK: {OrderState.PARTIAL_FILL, OrderState.FILLED, OrderState.CANCELLED},
        OrderState.PARTIAL_FILL: {OrderState.PARTIAL_FILL, OrderState.FILLED, OrderState.CANCELLED},
    }
    allowed = transitions.get(current, set())
    return next_state in allowed
