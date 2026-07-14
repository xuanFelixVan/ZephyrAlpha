# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.financial_governance.microstructure_defense
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
# [A_module] module_id=MOD-GOV_microstructure_defense | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum

from pydantic import BaseModel


class DefenseType(str, Enum):
    HFT_FRONT_RUN = "HFT_FRONT_RUN"
    STOP_HUNTING = "STOP_HUNTING"
    SPREAD_EXPLOIT = "SPREAD_EXPLOIT"
    ORDER_BOOK_HOLLOW = "ORDER_BOOK_HOLLOW"
    GAPPING = "GAPPING"


class DefenseStrategy(BaseModel):
    defense: DefenseType
    threat: str
    countermeasure: str


DEFENSE_STRATEGIES: Final[dict[DefenseType, DefenseStrategy]] = {
    DefenseType.HFT_FRONT_RUN: DefenseStrategy(
        defense=DefenseType.HFT_FRONT_RUN,
        threat="HFT抢先交易 — 探测大订单并前置",
        countermeasure="订单切割 + TWAP + 不显示完整量",
    ),
    DefenseType.STOP_HUNTING: DefenseStrategy(
        defense=DefenseType.STOP_HUNTING,
        threat="止损掠食 — 刻意推动价格触发止损群",
        countermeasure="非整数位止损 + Server端止损 + 动态调整",
    ),
    DefenseType.SPREAD_EXPLOIT: DefenseStrategy(
        defense=DefenseType.SPREAD_EXPLOIT,
        threat="价差剥削 — 宽Spread被MM套利",
        countermeasure="避宽Spread + 中间价限价",
    ),
    DefenseType.ORDER_BOOK_HOLLOW: DefenseStrategy(
        defense=DefenseType.ORDER_BOOK_HOLLOW,
        threat="盘口空洞 — 虚假深度引诱成交",
        countermeasure="验证盘口深度 ≤ 20%×Amount",
    ),
    DefenseType.GAPPING: DefenseStrategy(
        defense=DefenseType.GAPPING,
        threat="Gapping跳空 — 新闻/事件导致价格断层",
        countermeasure="止损+止损限价结合 + 风险事件前减仓",
    ),
}


class FidelityFactor(BaseModel):
    fill_probability: float = 0.85
    slippage: float = 0.30
    order_book_depth: float = 0.20
    partial_fill: float = 0.60

    @property
    def composite_ff(self) -> float:
        weights = {"fill_probability": 0.30, "slippage": 0.35, "order_book_depth": 0.20, "partial_fill": 0.15}
        total = (
            self.fill_probability * weights["fill_probability"]
            + self.slippage * weights["slippage"]
            + self.order_book_depth * weights["order_book_depth"]
            + self.partial_fill * weights["partial_fill"]
        )
        return round(total, 4)

    @property
    def description(self) -> str:
        return f"预期实盘/模拟 ≈ {self.composite_ff * 100:.0f}%-{self.composite_ff * 100 + 30:.0f}%"


DEFAULT_FIDELITY: Final[FidelityFactor] = FidelityFactor()
