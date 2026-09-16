# [BLUEPRINT] MOD-XS-008 | docs/03_modules/_domain_ex_sor/rl_execution_training_env/blueprint.md
# [MODULE] zephyr.ex_sor.core.rl_exec_boundary
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.ex_sor.core.rl_exec_contract; zephyr.ex_core.board_lot; zephyr.ex_core.price_cage; zephyr.backtest.core.matching_logic; stdlib; zephyr.ex_sor.core.rl_exec_env
# [CONSUMERS] zephyr.ex_sor.core.rl_exec_env
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 硬约束不可逾越:越界价格裁剪到涨跌停带/越界数量裁剪到POV上限/禁市价时市价类动作拒绝; 约束层独立于策略层,环境 step 必经本层; 纯函数式无副作用
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_sor/test_rl_exec_env.py
# [A_module] module_id=MOD-XS-008 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


RL Execution Hard Boundary — RL 执行硬边界包裹层 (MOD-XS-008, P-4 裁定组件·核心)

D-EX-SOR §2.1 XS-08: RL Execution Training Env 的硬约束层。

职责:
    - 限价: 动作价格偏移换算限价后, 不得越出涨跌停带
      [prev_close×(1-pct), prev_close×(1+pct)]——越界裁剪(clip)到带边界
    - 限量: 单步数量 ≤ min(数量比例×剩余量, POV 上限×对方五档盘口总量, 剩余量),
      再按整手规则向下对齐; 尾单(≥剩余量)一次性全清
    - 禁市价: forbid_market=True 时市价类动作直接拒绝（本步不成交）

不可绕过性（核心不变量）:
    本层独立于策略层——策略只产出 RlExecAction, 环境 step 内部必经
    RlExecBoundary.enforce, 策略侧无任何通道直挂撮合。

复用:
    - PRICE_TICK (zephyr.ex_core.price_cage): 0.01 元最小价格变动单位
    - round_buy_qty (zephyr.ex_core.board_lot): 板块差异化买入整手对齐
    - OrderBookSnapshot (zephyr.backtest.core.matching_logic): 盘口快照值对象

SSoT: depgraph MOD-XS-008
Version: 0.1.0

# [ALGO_FLOW] external: docs/03_modules/_domain_ex_sor/algo_flow/rl_exec_boundary.yaml
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from zephyr.backtest.core.matching_logic import OrderBookSnapshot
from zephyr.ex_core.board_lot import round_buy_qty
from zephyr.ex_core.price_cage import PRICE_TICK
from zephyr.ex_sor.core.rl_exec_contract import RlExecContract

if TYPE_CHECKING:
    from zephyr.ex_sor.core.rl_exec_env import RlExecAction

__all__: list[str] = ["BoundedAction", "RlExecBoundary"]

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BoundedAction:
    """硬边界裁定后的有界动作（frozen，纯值对象，含审计标记）。

    Attributes:
        limit_price: 裁剪后限价（量化到 tick，必在涨跌停带内）；市价类动作为 None
        quantity: 裁剪后数量（股，≥0；0 = 本步无有效申报）
        is_market: 是否市价类动作（透传策略意图）
        rejected: 是否被拒绝（True = 本步不成交，仅禁市价拒绝一种路径）
        clipped_price: 价格是否发生过裁剪
        clipped_qty: 数量是否发生过裁剪/整手对齐
        reason: 审计说明（"ok" / "market_forbidden" / "zero_quantity"）
    """

    limit_price: Decimal | None
    quantity: Decimal
    is_market: bool
    rejected: bool
    clipped_price: bool
    clipped_qty: bool
    reason: str


class RlExecBoundary:
    """RL 执行硬边界包裹层（纯函数式裁定，独立于策略层，环境 step 必经）。

    Usage:
        boundary = RlExecBoundary(contract)
        bounded = boundary.enforce(action, book, remaining)
        if bounded.rejected:  # 本步不成交
            ...
    """

    def __init__(self, contract: RlExecContract) -> None:
        self._contract = contract

    @property
    def contract(self) -> RlExecContract:
        """冻结契约（只读）。"""
        return self._contract

    def enforce(
        self,
        action: RlExecAction,
        book: OrderBookSnapshot,
        remaining: Decimal,
    ) -> BoundedAction:
        """硬约束裁定：禁市价拒绝 → 价格裁剪 → 数量裁剪（不可逾越）。

        Args:
            action: 策略原始动作（价格偏移档位索引 + 数量比例 + 市价标志）
            book: 当前五档盘口快照（中间价基准 / POV 档量基数）
            remaining: 母单剩余量（股）

        Returns:
            BoundedAction：裁剪/拒绝后的可执行动作与审计标记
        """
        # A1 禁市价拒绝（硬阻断，本步不成交）
        if action.is_market and self._contract.forbid_market:
            _logger.info("rl_exec_boundary REJECT market action (forbid_market=True)")
            return BoundedAction(
                limit_price=None,
                quantity=Decimal("0"),
                is_market=True,
                rejected=True,
                clipped_price=False,
                clipped_qty=False,
                reason="market_forbidden",
            )

        limit_price, clipped_price = self._clip_price_to_band(action, book)
        quantity, clipped_qty = self._clip_qty_to_pov(action, book, remaining)

        reason = "ok" if quantity > 0 else "zero_quantity"
        return BoundedAction(
            limit_price=limit_price,
            quantity=quantity,
            is_market=action.is_market,
            rejected=False,
            clipped_price=clipped_price,
            clipped_qty=clipped_qty,
            reason=reason,
        )

    def _clip_price_to_band(
        self,
        action: RlExecAction,
        book: OrderBookSnapshot,
    ) -> tuple[Decimal | None, bool]:
        """价格裁剪：限价=mid×(1+offset)，夹到涨跌停带内（越界 clip 不废单）。"""
        if action.is_market:
            return None, False
        c = self._contract
        offset = c.offset_levels[action.price_offset_idx]
        mid = (book.ask_price[0] + book.bid_price[0]) / Decimal("2")
        raw = (mid * (Decimal("1") + offset)).quantize(PRICE_TICK, rounding=ROUND_HALF_UP)
        upper = (c.prev_close * (Decimal("1") + c.price_limit_pct)).quantize(PRICE_TICK, rounding=ROUND_FLOOR)
        lower = (c.prev_close * (Decimal("1") - c.price_limit_pct)).quantize(PRICE_TICK, rounding=ROUND_CEILING)
        clipped = min(max(raw, lower), upper)
        if clipped != raw:
            _logger.info(
                "rl_exec_boundary CLIP price: raw=%s → %s (band [%s, %s])",
                raw,
                clipped,
                lower,
                upper,
            )
        return clipped, clipped != raw

    def _clip_qty_to_pov(
        self,
        action: RlExecAction,
        book: OrderBookSnapshot,
        remaining: Decimal,
    ) -> tuple[Decimal, bool]:
        """数量裁剪：min(比例×剩余量, POV×对方五档总量, 剩余量)，再整手向下对齐。"""
        c = self._contract
        ratio = Decimal(str(action.quantity_ratio))
        raw = ratio * remaining
        opposite_total = sum(book.ask_vol) if c.side == "BUY" else sum(book.bid_vol)
        pov_cap = c.pov_limit * opposite_total
        qty = min(raw, pov_cap, remaining)
        if qty <= 0:
            return Decimal("0"), raw > 0
        if qty >= remaining:
            # 尾单一次性全清（含零股；A 股卖出零股必须一次性申报，买入尾单由剩余量收敛）
            return remaining, remaining != raw
        # 整手向下对齐：买入复用板块差异化规则，卖出按 lot_size 向下取整
        if c.side == "BUY":
            aligned = round_buy_qty(qty, c.symbol)
        else:
            lot = Decimal(c.lot_size)
            aligned = (qty // lot) * lot
        return aligned, aligned != raw
