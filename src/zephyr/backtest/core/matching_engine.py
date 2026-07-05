# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.matching_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.portfolio; zephyr.backtest.core.matching_logic
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] A股约束: T+1/涨跌停/停牌/100股整数倍; 委托MatchingLogic保证回测=实盘一致性
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MatchingError
# [TESTS]
# [A_module] module_id=MOD-BT-001-matching_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""回测撮合引擎模块（v1.1.0 重构：委托 MatchingLogic 保证回测=实盘一致性）

职责:
  - 根据目标权重生成买卖订单（回测专用 orchestrator）
  - 委托 MatchingLogic 执行纯函数式撮合（回测=实盘一致性核心）
  - 应用A股约束: 100股整数倍/涨跌停/停牌
  - 将 MatchingFill 转换为 BacktestFill（加 date 字段）

v1.1.0 重构要点:
  - 移除重复的 MatchingConfig（ARCH-034 CLASS-UNIQUENESS 违规）→ 从 matching_logic 导入并 re-export
  - 移除重复的 _apply_slippage / _calc_commission → 委托给 MatchingLogic
  - 新增 generate_fills_with_order_book() 支持5档盘口撮合（Level 4 撮合）
  - 新增 generate_fills_with_tick() 支持 Tick级5档撮合（做T专用）
  - 新增 match_order/match_limit_order/match_tick_order 单笔撮合入口

约束:
  - 撮合行为与 D_EX_CORE MiniQmtBroker 完全一致（共用同一份 MatchingLogic）
  - 涨跌停: 价格触及涨跌停板时不成交
  - 停牌: 无数据时跳过
  - T+1: 由 Portfolio 负责（matching_engine 只生成 fills）

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.2 §5.1 §16.7
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from zephyr.backtest.core.matching_logic import (
    MatchingConfig,
    MatchingFill,
    MatchingLogic,
    MatchingLogicError,
    MatchOrderInput,
    OrderBookSnapshot,
    TickSnapshot,
)
from zephyr.backtest.core.portfolio import BacktestFill, Portfolio


class MatchingError(Exception):
    """撮合引擎错误（回测专用 orchestrator 错误，区分 MatchingLogicError 纯函数错误）"""


# 兼容性 sentinel: 用于从单一价格构造的合成1档盘口的虚拟深度
_SYNTHETIC_DEPTH = Decimal("99999999")


class MatchingEngine:
    """回测撮合引擎（v1.1.0 重构：委托 MatchingLogic）

    根据目标权重生成买卖订单，委托 MatchingLogic 应用滑点和手续费，
    产出 BacktestFill 列表。

    撮合逻辑（委托 MatchingLogic）:
      1. 计算当前总 NAV（现金+市值）
      2. 对每个 symbol 计算目标持仓金额 = NAV * target_weight
      3. 计算目标数量 = floor(目标金额 / price / lot_size) * lot_size
      4. 差额 = 目标数量 - 当前持仓
      5. 先卖后买（避免现金不足）
      6. 委托 MatchingLogic.{match_market_order|match_limit_order|match_tick_order} 撮合
      7. MatchingFill → BacktestFill（加 date 字段）

    A股约束（本引擎校验）:
      - 100股整数倍（买入）
      - 涨跌停不成交（有 prev_close 时检查）
      - 停牌不成交（无价格数据时跳过）
      - T+1 由 Portfolio 负责（matching_engine 只生成 fills）

    Usage（向后兼容，日线回测）:
        engine = MatchingEngine(config=MatchingConfig(...))
        fills = engine.generate_fills(
            target_weights={"000001.SZ": 0.5, "600000.SH": 0.5},
            prices={"000001.SZ": Decimal("10.5"), "600000.SH": Decimal("8.3")},
            portfolio=portfolio,
            date="2024-01-15",
        )

    Usage（v1.1.0 新增，5档盘口撮合）:
        fills = engine.generate_fills_with_order_book(
            target_weights={"000001.SZ": 0.5},
            order_books={"000001.SZ": order_book_snapshot},
            portfolio=portfolio,
            date="2024-01-15",
        )

    Usage（v1.1.0 新增，Tick级5档撮合做T）:
        fills = engine.generate_fills_with_tick(
            target_weights={"000001.SZ": 0.5},
            ticks={"000001.SZ": tick_snapshot},
            portfolio=portfolio,
            date="2024-01-15",
        )
    """

    def __init__(self, config: Optional[MatchingConfig] = None):
        """初始化撮合引擎

        Args:
            config: 撮合配置（可选，默认使用 MatchingConfig 默认值，frozen 不可变）
        """
        self._config = config or MatchingConfig()
        self._logic = MatchingLogic(self._config)

    # ------------------------------------------------------------------
    # 批量撮合入口（回测主流程调用）
    # ------------------------------------------------------------------

    def generate_fills(
        self,
        target_weights: dict[str, float],
        prices: dict[str, Decimal],
        portfolio: Portfolio,
        date: Any,
        prev_close: Optional[dict[str, Decimal]] = None,
    ) -> list[BacktestFill]:
        """根据目标权重生成成交记录（市价单，向后兼容接口）

        内部将单一价格构造成合成1档盘口，委托 MatchingLogic.match_market_order 撮合。
        撮合行为与原实现完全一致（BUY 按 price 成交，SELL 按 price 成交，应用滑点）。

        Args:
            target_weights: {symbol: weight} 目标权重（0.0-1.0, sum<=1.0）
            prices: {symbol: price} 当日价格
            portfolio: 当前持仓
            date: 当前日期
            prev_close: 前一日收盘价（可选，用于涨跌停检查）

        Returns:
            BacktestFill 列表（先卖后买排序）

        Raises:
            MatchingError: 参数无效
        """
        if not target_weights:
            return []

        if not prices:
            raise MatchingError("prices 不能为空")

        # 构造合成1档盘口 dict
        order_books: dict[str, OrderBookSnapshot] = {}
        for symbol, price in prices.items():
            if price is None or price <= 0:
                continue  # 停牌或无数据，跳过
            order_books[symbol] = self._synthetic_order_book(symbol, price)

        return self._generate_fills_from_order_books(
            target_weights=target_weights,
            order_books=order_books,
            portfolio=portfolio,
            date=date,
            prev_close=prev_close,
            tick_mode=False,
        )

    def generate_fills_with_order_book(
        self,
        target_weights: dict[str, float],
        order_books: dict[str, OrderBookSnapshot],
        portfolio: Portfolio,
        date: Any,
        prev_close: Optional[dict[str, Decimal]] = None,
    ) -> list[BacktestFill]:
        """根据目标权重 + 5档盘口生成成交记录（Level 4 撮合）

        v1.1.0 新增：使用真实5档盘口撮合，BUY 按 ask1 成交，SELL 按 bid1 成交。

        Args:
            target_weights: {symbol: weight} 目标权重
            order_books: {symbol: OrderBookSnapshot} 5档盘口快照
            portfolio: 当前持仓
            date: 当前日期
            prev_close: 前一日收盘价（可选，用于涨跌停检查）

        Returns:
            BacktestFill 列表（先卖后买排序）
        """
        if not target_weights:
            return []
        if not order_books:
            raise MatchingError("order_books 不能为空")

        return self._generate_fills_from_order_books(
            target_weights=target_weights,
            order_books=order_books,
            portfolio=portfolio,
            date=date,
            prev_close=prev_close,
            tick_mode=False,
        )

    def generate_fills_with_tick(
        self,
        target_weights: dict[str, float],
        ticks: dict[str, TickSnapshot],
        portfolio: Portfolio,
        date: Any,
    ) -> list[BacktestFill]:
        """根据目标权重 + Tick快照生成成交记录（Tick级5档撮合，做T专用）

        v1.1.0 新增：基于 Tick 快照的5档逐档消化撮合。
        委托 MatchingLogic.match_tick_order，逐档消化 ask1→ask2→...→ask5（BUY）
        或 bid1→bid2→...→bid5（SELL），流动性约束为单档成交量上限=该档 vol。

        Args:
            target_weights: {symbol: weight} 目标权重
            ticks: {symbol: TickSnapshot} Tick快照（含5档盘口）
            portfolio: 当前持仓
            date: 当前日期

        Returns:
            BacktestFill 列表（先卖后买排序）
        """
        if not target_weights:
            return []
        if not ticks:
            raise MatchingError("ticks 不能为空")

        # 将 Tick 转换为 OrderBook，复用统一流程
        order_books: dict[str, OrderBookSnapshot] = {}
        for symbol, tick in ticks.items():
            if tick.last_price <= 0:
                continue  # 停牌
            order_books[symbol] = tick.to_order_book()

        return self._generate_fills_from_order_books(
            target_weights=target_weights,
            order_books=order_books,
            portfolio=portfolio,
            date=date,
            prev_close=None,  # Tick 模式不做涨跌停检查（Tick 内已含状态）
            tick_mode=True,
            ticks=ticks,
        )

    # ------------------------------------------------------------------
    # 单笔撮合入口（委托 MatchingLogic，供外部直接调用）
    # ------------------------------------------------------------------

    def match_order(
        self,
        order: MatchOrderInput,
        order_book: OrderBookSnapshot,
    ) -> MatchingFill:
        """撮合市价单（委托 MatchingLogic.match_market_order）

        Args:
            order: 委托订单（MARKET 类型）
            order_book: 5档盘口快照

        Returns:
            MatchingFill 成交结果
        """
        try:
            return self._logic.match_market_order(order, order_book)
        except MatchingLogicError as e:
            raise MatchingError(str(e)) from e

    def match_limit_order(
        self,
        order: MatchOrderInput,
        order_book: OrderBookSnapshot,
    ) -> MatchingFill:
        """撮合限价单（委托 MatchingLogic.match_limit_order）

        Args:
            order: 委托订单（LIMIT 类型，limit_price 必填）
            order_book: 5档盘口快照

        Returns:
            MatchingFill 成交结果（filled=False 表示未成交）
        """
        try:
            return self._logic.match_limit_order(order, order_book)
        except MatchingLogicError as e:
            raise MatchingError(str(e)) from e

    def match_tick_order(
        self,
        order: MatchOrderInput,
        tick: TickSnapshot,
    ) -> MatchingFill:
        """撮合Tick级订单（委托 MatchingLogic.match_tick_order，做T专用）

        逐档消化5档盘口，流动性约束为单档 vol。

        Args:
            order: 委托订单（TICK 类型）
            tick: Tick快照（含5档盘口）

        Returns:
            MatchingFill 成交结果（filled=False 表示未成交或部分成交）
        """
        try:
            return self._logic.match_tick_order(order, tick)
        except MatchingLogicError as e:
            raise MatchingError(str(e)) from e

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def config(self) -> MatchingConfig:
        """撮合配置（只读，frozen）"""
        return self._config

    @property
    def logic(self) -> MatchingLogic:
        """暴露内部 MatchingLogic 供 MiniQmtBroker 复用（回测=实盘一致性）"""
        return self._logic

    # ------------------------------------------------------------------
    # 私有辅助方法
    # ------------------------------------------------------------------

    def _generate_fills_from_order_books(
        self,
        target_weights: dict[str, float],
        order_books: dict[str, OrderBookSnapshot],
        portfolio: Portfolio,
        date: Any,
        prev_close: Optional[dict[str, Decimal]] = None,
        tick_mode: bool = False,
        ticks: Optional[dict[str, TickSnapshot]] = None,
    ) -> list[BacktestFill]:
        """统一批量撮合流程（内部共享方法）

        流程:
          1. 计算当前总 NAV
          2. 对每个 symbol 计算目标数量（100股整数倍）
          3. 计算差额（目标 - 当前持仓）
          4. 先卖后买排序
          5. 委托 MatchingLogic 撮合（市价/限价/Tick）
          6. MatchingFill → BacktestFill
        """
        # 计算当前总 NAV（用 last_price 汇总市值）
        prices_for_nav = {
            symbol: ob.last_price for symbol, ob in order_books.items()
        }
        total_nav = portfolio.total_nav(prices_for_nav)
        if total_nav <= 0:
            raise MatchingError(f"总 NAV 必须 > 0, got {total_nav}")

        # 计算目标持仓和差额
        orders: list[dict] = []
        for symbol, weight in target_weights.items():
            if weight <= 0:
                continue

            ob = order_books.get(symbol)
            if ob is None or ob.last_price <= 0:
                continue  # 停牌或无数据

            # 涨跌停检查（Tick 模式跳过，Tick 内已含状态）
            if not tick_mode and prev_close and self._is_price_limit(
                symbol, ob.last_price, prev_close.get(symbol)
            ):
                continue

            # 计算目标数量（100股整数倍）
            target_value = total_nav * Decimal(str(weight))
            target_qty = (
                int(target_value / ob.last_price / self._config.lot_size)
                * self._config.lot_size
            )

            # 当前持仓
            current_pos = portfolio.get_position(symbol)
            current_qty = current_pos.quantity if current_pos else Decimal("0")

            # 差额
            diff = Decimal(target_qty) - current_qty
            if diff > 0:
                orders.append(
                    {"side": "BUY", "symbol": symbol, "quantity": diff}
                )
            elif diff < 0:
                orders.append(
                    {"side": "SELL", "symbol": symbol, "quantity": abs(diff)}
                )

        # 先卖后买（避免现金不足）
        orders.sort(key=lambda o: 0 if o["side"] == "SELL" else 1)

        # 生成 fills
        fills: list[BacktestFill] = []
        for order_dict in orders:
            fill = self._match_order_dict(
                order_dict, order_books, tick_mode=tick_mode, ticks=ticks
            )
            # Tick 模式下部分成交（quantity>0 但 filled=False）也应当应用
            # 市价单/限价单完全成交才应用（filled=True）
            if fill is not None and (fill.filled or fill.filled_quantity > 0):
                fills.append(self._to_backtest_fill(fill, date))
        return fills

    def _match_order_dict(
        self,
        order_dict: dict,
        order_books: dict[str, OrderBookSnapshot],
        tick_mode: bool = False,
        ticks: Optional[dict[str, TickSnapshot]] = None,
    ) -> Optional[MatchingFill]:
        """根据订单字典和盘口撮合，返回 MatchingFill

        Args:
            order_dict: {side, symbol, quantity}
            order_books: 盘口 dict
            tick_mode: True=Tick级5档撮合, False=市价单撮合
            ticks: Tick快照 dict（tick_mode=True 时必填）
        """
        symbol = order_dict["symbol"]
        side = order_dict["side"]
        quantity = order_dict["quantity"]

        if quantity <= 0:
            return None

        order_input = MatchOrderInput(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type="TICK" if tick_mode else "MARKET",
        )

        try:
            if tick_mode and ticks is not None:
                tick = ticks.get(symbol)
                if tick is None:
                    return None
                return self._logic.match_tick_order(order_input, tick)
            else:
                ob = order_books.get(symbol)
                if ob is None:
                    return None
                return self._logic.match_market_order(order_input, ob)
        except MatchingLogicError:
            # 撮合失败（如盘口为空）视为未成交
            return None

    def _to_backtest_fill(self, fill: MatchingFill, date: Any) -> BacktestFill:
        """将 MatchingFill 转换为 BacktestFill（加 date 字段）

        使用 filled_quantity（实际成交数量）而非 quantity（委托数量），
        以正确处理 Tick 级部分成交场景。
        """
        return BacktestFill(
            date=date,
            symbol=fill.symbol,
            side=fill.side,
            quantity=fill.filled_quantity,
            price=fill.price,
            commission=fill.commission,
            slippage_cost=fill.slippage_cost,
        )

    def _synthetic_order_book(
        self, symbol: str, price: Decimal
    ) -> OrderBookSnapshot:
        """从单一价格构造合成1档盘口（日线回测兼容模式）

        用途: generate_fills() 接收单一价格时，构造1档盘口委托给 MatchingLogic。
        BUY 按 ask1=price 成交，SELL 按 bid1=price 成交，与原实现行为一致。
        虚拟深度设为大数（_SYNTHETIC_DEPTH）避免流动性约束触发。
        """
        return OrderBookSnapshot(
            symbol=symbol,
            ask_price=(price,),
            bid_price=(price,),
            ask_vol=(_SYNTHETIC_DEPTH,),
            bid_vol=(_SYNTHETIC_DEPTH,),
            last_price=price,
            timestamp=None,
        )

    def _is_price_limit(
        self, symbol: str, price: Decimal, prev_close: Optional[Decimal]
    ) -> bool:
        """检查是否涨跌停（A股 ±10%，ST股 ±5% 简化统一用10%）

        Args:
            symbol: 标的代码
            price: 当前价格
            prev_close: 前一日收盘价

        Returns:
            True=涨跌停（不成交）, False=正常
        """
        if prev_close is None or prev_close <= 0:
            return False
        upper_limit = (prev_close * (1 + self._config.price_limit_pct)).quantize(
            Decimal("0.01")
        )
        lower_limit = (prev_close * (1 - self._config.price_limit_pct)).quantize(
            Decimal("0.01")
        )
        return price >= upper_limit or price <= lower_limit


# MatchingConfig / MatchingFill / MatchOrderInput / OrderBookSnapshot / TickSnapshot
# 从 matching_logic re-export，保持 `from zephyr.backtest.core.matching_engine import MatchingConfig`
# 向后兼容（vectorized_engine 和 __init__.py 依赖此导入路径）
__all__ = [
    "MatchingEngine",
    "MatchingConfig",
    "MatchingError",
    "MatchingFill",
    "MatchOrderInput",
    "OrderBookSnapshot",
    "TickSnapshot",
]
