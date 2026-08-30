# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.financial_governance.oms_risk_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.financial_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: state 参数
#   fields: 参数 state，类型注解 OrderState
#   code: oms_risk_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: current 参数
#   fields: 参数 current，类型注解 OrderState
#   code: oms_risk_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: next_state 参数
#   fields: 参数 next_state，类型注解 OrderState
#   code: oms_risk_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① OMSRiskEngine
#   name_en: OMSRiskEngine
#   intro: class OMSRiskEngine 源码 L136-L152
#   desc: 公共方法（定义序）: pre_trade_check, at_trade_check, post_trade_evaluate；源码 L136-L152
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② is_terminal
#   name_en: is_terminal
#   intro: is_terminal(state) 源码 L155-L156
#   desc: 源码 L155-L156
#   inputs: state
#   outputs: bool
# - id: A3
#   name_zh: ③ valid_transitions
#   name_en: valid_transitions
#   intro: valid_transitions(current, next_state) 源码 L159-L166
#   desc: 源码 L159-L166
#   inputs: current next_state
#   outputs: bool
#   （注：A3 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Final

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
