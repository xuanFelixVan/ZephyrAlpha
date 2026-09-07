# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.matching_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.portfolio; zephyr.backtest.core.matching_logic; zephyr.data.ch_reader（StkLimitProvider lazy import）; zephyr.data.implementations.akshare_provider（_limit_pct_of lazy import，涨跌幅切片单一真源）
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.implementations.event_driven_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] A股约束: T+1/涨跌停/停牌/100股整数倍; 委托MatchingLogic保证回测=实盘一致性; 涨跌停价三级解析链=stk_limit表PIT行→limit_pct_of切片规则（ST经st_stock_list最近可得快照）→板块前缀推断（无日期兜底），禁再造第四份口径（#ARCH-DATA-020）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MatchingError
# [TESTS] tests/backtest/test_matching_engine.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""回测撮合引擎模块（v1.1.0 重构：委托 MatchingLogic 保证回测=实盘一致性）

职责:
  - 根据目标权重生成买卖订单（回测专用 orchestrator）
  - 委托 MatchingLogic 执行纯函数式撮合（回测=实盘一致性核心）
  - 应用A股约束: 100股整数倍/涨跌停/停牌
  - 将 MatchingFill 转换为 BacktestFill（加 date 字段）

v1.1.0 重构要点:
  - 移除重复的 MatchingConfig（ARCH-034 CLASS-UNIQUENESS 违规）-> 从 matching_logic 导入并 re-export
  - 移除重复的 _apply_slippage / _calc_commission -> 委托给 MatchingLogic
  - 新增 generate_fills_with_order_book() 支持5档盘口撮合（Level 4 撮合）
  - 新增 generate_fills_with_tick() 支持 Tick级5档撮合（做T专用）
  - 新增 match_order/match_limit_order/match_tick_order 单笔撮合入口

约束:
  - 撮合行为与 D_EX_CORE MiniQmtBroker 完全一致（共用同一份 MatchingLogic）
  - 涨跌停: 价格触及涨跌停板时不成交（价源三级解析链，见 _limit_bounds docstring；
    stk_limit 表 PIT 行优先，缺行走 _limit_pct_of 日期切片规则，#ARCH-DATA-020）
  - 停牌: 无数据时跳过
  - T+1: 由 Portfolio 负责（matching_engine 只生成 fills）

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.2 §5.1 §16.7

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 目标权重+盘口快照
#   fields: target_weights / order_books(OrderBookSnapshot|TickSnapshot) / portfolio / prev_close
#   code: MatchingEngine.generate_fills (L181) / _build_target_orders (L73)
# 层: 算法
# - id: A1
#   name_zh: 目标订单生成
#   name_en: build_target_orders
#   intro: 按权重×NAV换算目标股数(100股整数倍)，剔除停牌/涨跌停标的
#   code: _build_target_orders (L73)
# - id: A2
#   name_zh: 委托撮合与成交转换
#   name_en: delegate_match_convert
#   intro: 委托 MatchingLogic 纯函数撮合，MatchingFill 加 date 转 BacktestFill
#   code: _generate_fills_from_order_books (L390) / _to_backtest_fill (L488)
# 层: 输出
# - id: O1
#   name_zh: 回测成交列表
#   name_en: backtest_fills
#   intro: list[BacktestFill]（含 date/price/commission/slippage_cost）
#   downstream: zephyr.backtest.core.portfolio.Portfolio.apply_fill
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Callable, Iterable, Optional

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

_logger = logging.getLogger(__name__)


class MatchingError(Exception):
    """撮合引擎错误（回测专用 orchestrator 错误，区分 MatchingLogicError 纯函数错误）"""

    error_code = "ZA-BT-0008"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# 兼容性 sentinel: 用于从单一价格构造的合成1档盘口的虚拟深度
_SYNTHETIC_DEPTH = Decimal("99999999")


def _normalize_date(value: object) -> datetime.date | None:
    """归一化交易日（str/date/datetime/Timestamp → date；None/非法 → None）。

    generate_fills* 的 date 参数历史上是 object（str/date/pd.Timestamp 均有），
    涨跌停 PIT 解析需要 date 型；非法输入返回 None（调用方退回无日期兜底路径）。
    """
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    s = str(value).strip()[:10]
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        return None


@dataclass(frozen=True)
class LimitInfo:
    """单标的单日涨跌停约束包（StkLimitProvider 产出，撮合判定消费）。

    Attributes:
        limit_up: 涨停价（stk_limit 表 PIT 行命中时给出；NULL=无涨跌幅限制期）
        limit_down: 跌停价（同上）
        limit_pct: 涨跌停幅度小数（表行 limit_pct 或规则切片兜底产出；None=未知/无限制）
        st_flag: ST/*ST 标记（表行 st_flag 或 st_stock_list 最近可得快照 PIT）
        from_table: True=stk_limit 表 PIT 行直用（价格精确，撮合不重算）；
                    False=规则切片兜底（引擎按 prev_close×(1±pct) ROUND_HALF_UP 重算）
    """

    limit_up: Optional[Decimal] = None
    limit_down: Optional[Decimal] = None
    limit_pct: Optional[Decimal] = None
    st_flag: bool = False
    from_table: bool = False


#: StkLimitProvider 协议：`(trade_date, symbols) -> {symbol: LimitInfo}`。
#: trade_date 已归一化为 date；symbols 为撮合当日标的的原始 symbol 形态。
LimitProvider = Callable[[datetime.date, Iterable[str]], dict]


def _build_target_orders(
    engine: MatchingEngine,
    target_weights: dict[str, float],
    order_books: dict[str, OrderBookSnapshot],
    portfolio: Portfolio,
    total_nav: Decimal,
    prev_close: dict[str, Decimal] | None,
    tick_mode: bool,
    trade_date: datetime.date | None = None,
    limit_map: dict | None = None,
) -> list[dict]:
    orders: list[dict] = []
    for symbol, weight in target_weights.items():
        if weight <= 0:
            continue

        ob = order_books.get(symbol)
        if ob is None or ob.last_price <= 0:
            continue  # 停牌或无数据

        # 计算目标数量（100股整数倍）
        target_value = total_nav * Decimal(str(weight))
        target_qty = int(target_value / ob.last_price / engine._config.lot_size) * engine._config.lot_size

        # 当前持仓
        current_pos = portfolio.get_position(symbol)
        current_qty = current_pos.quantity if current_pos else Decimal("0")

        # 差额
        diff = Decimal(target_qty) - current_qty
        if diff > 0:
            # 涨停封板：买单拒成（2026-08-19 阶段2 改方向感知——原买卖对称
            # 阻断把涨停日可成交的卖单也一并锁死）
            if not tick_mode and prev_close and engine._is_limit_up(
                symbol, ob.last_price, prev_close.get(symbol), trade_date, limit_map
            ):
                continue
            orders.append({"side": "BUY", "symbol": symbol, "quantity": diff})
        elif diff < 0:
            # 跌停封板：卖单拒成；涨停日卖单可成交（排队买盘即时消化）
            if not tick_mode and prev_close and engine._is_limit_down(
                symbol, ob.last_price, prev_close.get(symbol), trade_date, limit_map
            ):
                continue
            orders.append({"side": "SELL", "symbol": symbol, "quantity": abs(diff)})

    # 目标权重语义补全（2026-08-19 AI-NIGHT-001 阶段2 红队实证 P0）：持仓但
    # 目标权重缺失/<=0 的标的目标仓位=0，必须生成清仓卖单——否则轮动策略
    # 跌出信号的持仓永久滞留（实证：A 轮出后 59900 股滞留，轮入标的买入因
    # 现金被占连续被拒），回测系统性偏离信号意图。停牌/跌停无法卖出时跳过。
    for symbol, pos in portfolio.positions.items():
        if pos.quantity <= 0:
            continue
        if target_weights.get(symbol, 0.0) > 0:
            continue  # 已在上方差额逻辑处理
        ob = order_books.get(symbol)
        if ob is None or ob.last_price <= 0:
            continue  # 停牌或无数据，无法卖出
        if not tick_mode and prev_close and engine._is_limit_down(
            symbol, ob.last_price, prev_close.get(symbol), trade_date, limit_map
        ):
            continue  # 跌停封板无法卖出（涨停日卖单可成交，不阻断清仓）
        orders.append({"side": "SELL", "symbol": symbol, "quantity": pos.quantity})
    return orders


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
      7. MatchingFill -> BacktestFill（加 date 字段）

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

    def __init__(
        self,
        config: MatchingConfig | None = None,
        limit_provider: LimitProvider | None = None,
    ):
        """初始化撮合引擎

        Args:
            config: 撮合配置（可选，默认使用 MatchingConfig 默认值，frozen 不可变）
            limit_provider: 涨跌停 PIT 提供器（可选，协议见 LimitProvider）。注入后
                撮合涨跌停价优先消费其 stk_limit 表 PIT 行（#ARCH-DATA-020）；
                None=纯规则兜底（日期切片仅由 provider 内部兜底覆盖 ST，
                无 provider 时主板 ST 历史约束按无 ST 口径处理——生产路径经
                vectorized_engine 默认注入 StkLimitProvider）。
        """
        self._config = config or MatchingConfig()
        self._logic = MatchingLogic(self._config)
        self._limit_provider = limit_provider

    # ------------------------------------------------------------------
    # 批量撮合入口（回测主流程调用）
    # ------------------------------------------------------------------

    def generate_fills(
        self,
        target_weights: dict[str, float],
        prices: dict[str, Decimal],
        portfolio: Portfolio,
        date: object,
        prev_close: dict[str, Decimal] | None = None,
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
        date: object,
        prev_close: dict[str, Decimal] | None = None,
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
        date: object,
    ) -> list[BacktestFill]:
        """根据目标权重 + Tick快照生成成交记录（Tick级5档撮合，做T专用）

        v1.1.0 新增：基于 Tick 快照的5档逐档消化撮合。
        委托 MatchingLogic.match_tick_order，逐档消化 ask1->ask2->...->ask5（BUY）
        或 bid1->bid2->...->bid5（SELL），流动性约束为单档成交量上限=该档 vol。

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
        date: object,
        prev_close: dict[str, Decimal] | None = None,
        tick_mode: bool = False,
        ticks: dict[str, TickSnapshot] | None = None,
    ) -> list[BacktestFill]:
        """统一批量撮合流程（内部共享方法）

        流程:
          1. 计算当前总 NAV
          2. 对每个 symbol 计算目标数量（100股整数倍）
          3. 计算差额（目标 - 当前持仓）
          4. 先卖后买排序
          5. 委托 MatchingLogic 撮合（市价/限价/Tick）
          6. MatchingFill -> BacktestFill
        """
        # 计算当前总 NAV（用 last_price 汇总市值）
        prices_for_nav = {symbol: ob.last_price for symbol, ob in order_books.items()}
        total_nav = portfolio.total_nav(prices_for_nav)
        if total_nav <= 0:
            raise MatchingError(f"总 NAV 必须 > 0, got {total_nav}")

        # 涨跌停 PIT 预取（每次调用=一个回测日：一次批量查询，逐 symbol 查内存）。
        # tick_mode 不做涨跌停检查（prev_close=None），跳过预取防无谓触库。
        trade_date = _normalize_date(date)
        limit_map = None if tick_mode else self._prefetch_limit_map(trade_date, order_books.keys())

        # 计算目标持仓和差额
        orders: list[dict] = _build_target_orders(
            self,
            target_weights,
            order_books,
            portfolio,
            total_nav,
            prev_close,
            tick_mode,
            trade_date,
            limit_map,
        )

        # 先卖后买（避免现金不足）
        orders.sort(key=lambda o: 0 if o["side"] == "SELL" else 1)

        # 满仓归一化成本摩擦修复（2026-08-20 AI-NIGHT-001 包3.2 登记项#2）：
        # 目标 sizing 按 NAV×weight 换算不含交易成本余量，满仓（Σ=1）时买入
        # 总成本=成交额×(1+滑点)+佣金 必然超现金 → 整单被拒（每日重复 warning、
        # 回测偏离信号意图）。此处按"先卖后买"顺序投影现金，买单预计超支时
        # 收缩到可负担的最大整手；现金充足的非满仓场景逐位不变（零回归）。
        orders = self._clamp_buys_to_projected_cash(orders, order_books, portfolio)

        # 生成 fills
        fills: list[BacktestFill] = []
        for order_dict in orders:
            fill = self._match_order_dict(order_dict, order_books, tick_mode=tick_mode, ticks=ticks)
            # Tick 模式下部分成交（quantity>0 但 filled=False）也应当应用
            # 市价单/限价单完全成交才应用（filled=True）
            if fill is not None and (fill.filled or fill.filled_quantity > 0):
                fills.append(self._to_backtest_fill(fill, date))
        return fills

    def _clamp_buys_to_projected_cash(
        self,
        orders: list[dict],
        order_books: dict[str, OrderBookSnapshot],
        portfolio: Portfolio,
    ) -> list[dict]:
        """按投影现金收缩买单至可负担的最大整手（满仓成本摩擦修复）

        逐单按"先卖后买"顺序投影现金：卖单按估算净回款累加，买单按估算总成本
        （成交额×(1+滑点)+max(佣金率佣金,最低佣金)+过户费，与 MatchingLogic 口径一致）
        扣减；买单预计超支时收缩数量到可负担整手，不足一手则丢弃。
        Portfolio._apply_buy 的现金非负检查仍是最终防线（本步骤只做 sizing 收缩）。
        （2026-08-21 费率口径统一 #233：估算含双向过户费 万0.1）
        """
        slip = self._config.slippage_bps / Decimal("10000")
        rate = self._config.commission_rate
        min_comm = self._config.min_commission
        stamp = self._config.stamp_tax_rate
        transfer = self._config.transfer_fee_rate
        lot = self._config.lot_size

        projected = portfolio.cash
        out: list[dict] = []
        for order in orders:
            ob = order_books.get(order["symbol"])
            if order["side"] == "SELL":
                base = self._side_base_price(ob, "SELL")
                exec_price = base * (1 - slip)
                gross = order["quantity"] * exec_price
                comm = max(gross * rate, min_comm) + gross * stamp + gross * transfer
                projected += gross - comm
                out.append(order)
                continue

            base = self._side_base_price(ob, "BUY")
            exec_price = base * (1 + slip)
            qty = order["quantity"]

            def _buy_cost(q: Decimal) -> Decimal:
                g = q * exec_price
                return g + max(g * rate, min_comm) + g * transfer

            if _buy_cost(qty) > projected:
                # 佣金率情形的可负担手数，再按最低佣金/滑点实际成本回校验递减
                qty = Decimal(int(projected / (exec_price * (1 + rate + transfer)) / lot) * lot)
                while qty > 0 and _buy_cost(qty) > projected:
                    qty -= lot
                if qty <= 0:
                    continue  # 现金不足一手，放弃该买单（无单可成）
                order = dict(order, quantity=qty)
            projected -= _buy_cost(qty)
            out.append(order)
        return out

    @staticmethod
    def _side_base_price(ob: OrderBookSnapshot | None, side: str) -> Decimal:
        """取估算执行基准价：BUY 用 ask1、SELL 用 bid1，缺失回退 last_price。"""
        if ob is None:
            return Decimal("0")
        if side == "BUY":
            if ob.ask_price and ob.ask_price[0] > 0:
                return ob.ask_price[0]
        else:
            if ob.bid_price and ob.bid_price[0] > 0:
                return ob.bid_price[0]
        return ob.last_price

    def _match_order_dict(
        self,
        order_dict: dict,
        order_books: dict[str, OrderBookSnapshot],
        tick_mode: bool = False,
        ticks: dict[str, TickSnapshot] | None = None,
    ) -> MatchingFill | None:
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

    def _to_backtest_fill(self, fill: MatchingFill, date: object) -> BacktestFill:
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

    def _synthetic_order_book(self, symbol: str, price: Decimal) -> OrderBookSnapshot:
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

    def _prefetch_limit_map(
        self, trade_date: datetime.date | None, symbols: Iterable[str]
    ) -> dict | None:
        """按回测日批量预取涨跌停约束包（limit_provider 一次调用，结果内存直查）。

        provider 异常 fail-open（warn 一次 + 返回 {}，退回规则兜底）——回测撮合
        不因数据面故障中断；trade_date 非法/无 provider 返回 None（纯规则路径）。
        """
        if self._limit_provider is None or trade_date is None:
            return None
        try:
            return self._limit_provider(trade_date, list(symbols)) or {}
        except Exception as e:  # noqa: BLE001 — provider 故障降级不炸回测
            _logger.warning(
                "StkLimitProvider 预取失败（%s %s），退回规则兜底: %s",
                trade_date, list(symbols)[:5], e,
            )
            return {}

    def _fallback_limit_pct(
        self, symbol: str, trade_date: datetime.date | None, st_flag: bool
    ) -> Decimal | None:
        """规则切片兜底幅度：复用生成侧单一真源 _limit_pct_of（#ARCH-DATA-020）。

        trade_date=None（旧调用路径无日期）返回 None（调用方退板块前缀推断）；
        akshare_provider 导入失败/口径返回 None 均返回 None（保守回退链）。
        lazy import：撮合引擎不在模块级依赖 data.implementations（防环+轻导入）。
        """
        if trade_date is None:
            return None
        try:
            from zephyr.data.implementations.akshare_provider import AkshareIngestProvider

            pct = AkshareIngestProvider._limit_pct_of(symbol.split(".")[0], trade_date, st_flag)
        except Exception as e:  # noqa: BLE001 — 真源导入/查询故障退保守回退链
            _logger.warning("_limit_pct_of 切片真源调用失败（%s %s）: %s", symbol, trade_date, e)
            return None
        return None if pct is None else Decimal(str(pct))

    def _limit_bounds(
        self,
        symbol: str,
        trade_date: datetime.date | None,
        prev_close: Decimal | None,
        limit_map: dict | None,
    ) -> tuple[Decimal, Decimal] | None:
        """单标的当日涨跌停价（三级解析链，#ARCH-DATA-020 重评条件②闭环）。

        链路（禁再造第四份口径）：
          1. stk_limit 表 PIT 行（from_table，limit_up/limit_down 精确价直用）；
             行在但 limit_*=NULL（新股无涨跌幅限制期）→ None（不封板）；
          2. 规则切片兜底：provider 兜底 limit_pct 或 AkshareIngestProvider._limit_pct_of
             （trade_date 切片，ST 由 provider 的 st_stock_list 最近可得快照），
             引擎按 prev_close×(1±pct) ROUND_HALF_UP 到分（与生成侧同口径）；
          3. 板块前缀推断 _infer_limit_pct（未知前缀保守回退，无日期无 ST）。
        prev_close 缺失/非正 → None（无基准不封板，保持既有行为）。
        """
        if prev_close is None or prev_close <= 0:
            return None
        info = limit_map.get(symbol) if limit_map else None
        if info is not None and info.from_table:
            if info.limit_up is None or info.limit_down is None:
                return None  # 表行 limit_*=NULL：新股无涨跌幅限制期，不封板
            return (info.limit_up, info.limit_down)
        st_flag = bool(info.st_flag) if info is not None else False
        pct: Decimal | None = None
        if info is not None and info.limit_pct is not None:
            pct = info.limit_pct
        else:
            pct = self._fallback_limit_pct(symbol, trade_date, st_flag)
        if pct is None:
            pct = self._infer_limit_pct(symbol)
        upper = (prev_close * (1 + pct)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        lower = (prev_close * (1 - pct)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return (upper, lower)

    def _infer_limit_pct(self, symbol: str) -> Decimal:
        """按代码前缀推断板块涨跌停幅度（2026-08-19 AI-NIGHT-001 #211）。

        原实现全板块统一 ±10%（config.price_limit_pct），与宪章约束四不符：
        主板 ±10% / 科创板(68x) ±20% / 创业板(30x) ±20% / 北交所(4xx/8xx/92x) ±30%。
        本函数是涨跌停三级解析链的最后防线（#ARCH-DATA-020）：仅未知前缀
        （_limit_pct_of 返回 None 的异形代码）与无 trade_date 的旧调用路径生效；
        A 股股票的历史正确口径由 stk_limit 表 PIT 行 / _limit_pct_of 切片承载。
        """
        code = symbol.split(".")[0]
        if code.startswith(("68", "30")):
            return Decimal("0.20")
        if code.startswith(("4", "8", "92")):
            return Decimal("0.30")
        return self._config.price_limit_pct

    def _is_limit_up(
        self,
        symbol: str,
        price: Decimal,
        prev_close: Decimal | None,
        trade_date: datetime.date | None = None,
        limit_map: dict | None = None,
    ) -> bool:
        """是否涨停（封板价之上，买单拒成；卖单不受限）。

        涨跌停价取整口径与交易所一致：ROUND_HALF_UP 到分（非默认
        ROUND_HALF_EVEN），消除 x.xx5 边界 1 分差异；表 PIT 行命中时直接
        比对表价（stk_limit 生成侧已是同口径 ROUND_HALF_UP）。
        trade_date/limit_map 缺省时保持旧调用行为（板块前缀推断）。
        """
        bounds = self._limit_bounds(symbol, trade_date, prev_close, limit_map)
        return bounds is not None and price >= bounds[0]

    def _is_limit_down(
        self,
        symbol: str,
        price: Decimal,
        prev_close: Decimal | None,
        trade_date: datetime.date | None = None,
        limit_map: dict | None = None,
    ) -> bool:
        """是否跌停（封板价之下，卖单拒成；买单不受限）。

        取整口径同 _is_limit_up；参数缺省时保持旧调用行为。
        """
        bounds = self._limit_bounds(symbol, trade_date, prev_close, limit_map)
        return bounds is not None and price <= bounds[1]

    def _is_price_limit(
        self,
        symbol: str,
        price: Decimal,
        prev_close: Decimal | None,
        trade_date: datetime.date | None = None,
        limit_map: dict | None = None,
    ) -> bool:
        """检查是否涨跌停（三级解析链：stk_limit PIT 行 → 切片规则 → 前缀推断）

        Args:
            symbol: 标的代码
            price: 当前价格
            prev_close: 前一日收盘价
            trade_date: 交易日（涨跌停口径日期切片，缺省走旧推断路径）
            limit_map: 当日预取约束包（_prefetch_limit_map 产物，缺省走规则兜底）

        Returns:
            True=涨跌停（不成交）, False=正常
        """
        return self._is_limit_up(symbol, price, prev_close, trade_date, limit_map) or self._is_limit_down(
            symbol, price, prev_close, trade_date, limit_map
        )


class StkLimitProvider:
    """撮合涨跌停 PIT 提供器（c1_market.stk_limit 优先 + st_stock_list 快照兜底）。

    三级解析链的数据腿（#ARCH-DATA-020 重评条件②）：
      1. stk_limit 表单日 FINAL 查询（trade_date=当日，PIT strict）→ LimitInfo
         (from_table=True, limit_up/limit_down/limit_pct/st_flag=表行)；
      2. 表缺行（如 2026-07-06 前未回补历史/新股无行）→ st_stock_list 最近可得
         （≤T）快照取 st_flag → limit_pct 经生成侧单一真源 _limit_pct_of 按日切片
         （主板 ST 2026-07-06 起 10%、此前 5%；创业板 2020-08-24 切片同构）；
      3. CH 不可达/查询异常 → warn 一次后降级记忆（本实例不再重试），返回
         {}——撮合退回引擎内规则兜底（无 ST，fail-open 不炸回测）。

    使用：vectorized_engine 每次回测构造一个实例注入 MatchingEngine(limit_provider=)；
    撮合引擎按日批量调用本 provider（一次 SQL/回测日），不在逐 symbol 判定中触库。
    """

    #: stk_limit 单日行（inject_final 对 ReplacingMergeTree 注入 FINAL；
    #: symbol 列为 6 位裸码——撮合侧传 canonical 形态时须先取 split(".")[0]）
    _SQL_STK_LIMIT_DAY = (
        "SELECT symbol, limit_up, limit_down, limit_pct, st_flag "
        "FROM c1_market.stk_limit WHERE trade_date = '{d}' AND symbol IN ({symbols})"
    )
    #: ST 最近可得快照（≤T 口径 PIT 严格，与生成侧 _load_st_snapshots 同语义）
    _SQL_ST_SNAPSHOT_DAY = (
        "SELECT symbol FROM {st_table} WHERE trade_date = ("
        "SELECT max(trade_date) FROM {st_table} WHERE trade_date <= '{d}')"
    )

    def __init__(self) -> None:
        self._degraded = False
        self._st_cache: dict[datetime.date, set[str] | None] = {}

    def __call__(self, trade_date: datetime.date, symbols: Iterable[str]) -> dict:
        from zephyr.data import ch_reader as _chr

        out: dict = {}
        symbols = list(symbols)  # 可能被迭代两次（裸码集 + _canon 回映射），防生成器耗尽
        codes = {str(s or "").split(".")[0].zfill(6) for s in symbols if str(s or "").strip()}
        if not codes:
            return out
        sym_list = ",".join(f"'{c}'" for c in sorted(codes))
        tsv = _chr.query(_chr.inject_final(self._SQL_STK_LIMIT_DAY.format(d=trade_date.isoformat(), symbols=sym_list)))
        seen: set[str] = set()
        for line in (tsv or "").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) != 5:
                continue
            code = parts[0].strip().zfill(6)
            seen.add(code)
            out[self._canon(code, symbols)] = LimitInfo(
                limit_up=_parse_tsv_decimal(parts[1]),
                limit_down=_parse_tsv_decimal(parts[2]),
                limit_pct=_parse_tsv_decimal(parts[3]),
                st_flag=parts[4].strip() == "1",
                from_table=True,
            )
        missing = [c for c in codes if c not in seen]
        if not missing:
            return out
        if self._degraded:
            return out
        st_set = self._st_flag_set(trade_date, _chr)
        if st_set is None:
            return out  # CH 不可达已降级（_st_flag_set 内置记忆）
        for code in missing:
            out[self._canon(code, symbols)] = LimitInfo(
                limit_pct=_fallback_pct(code, trade_date, code in st_set),
                st_flag=code in st_set,
                from_table=False,
            )
        return out

    @staticmethod
    def _canon(code: str, symbols: Iterable[str]) -> str:
        """把裸码映射回调用方传入的原始 symbol 形态（撮合侧按原 symbol 查内存）。"""
        for s in symbols:
            if str(s or "").split(".")[0].zfill(6) == code:
                return str(s)
        return code

    def _st_flag_set(self, trade_date: datetime.date, ch_reader_mod: object) -> set[str] | None:
        """trade_date 的 ST 代码集合（最近可得 ≤T 快照；None=CH 不可达降级）。"""
        if trade_date in self._st_cache:
            return self._st_cache[trade_date]
        try:
            from zephyr.data.table_registry import get_registry

            st_table = get_registry().table("market_st_stock_list")
        except Exception as e:  # noqa: BLE001 — registry 故障等同 CH 故障降级
            _logger.warning("st_stock_list 表名解析失败（ST 兜底降级）: %s", e)
            self._degraded = True
            return None
        sql = self._SQL_ST_SNAPSHOT_DAY.format(st_table=st_table, d=trade_date.isoformat())
        tsv = ch_reader_mod.query(ch_reader_mod.inject_final(sql))
        if not (tsv or "").strip():
            # 空结果：可能是 CH 不可达（query 故障静默空串）或该窗口确无快照——
            # 一律降级记忆（fail-open，撮合退规则兜底），warn 留痕
            _logger.warning("st_stock_list 快照查询为空（%s），ST 兜底降级为非 ST 口径", trade_date)
            self._st_cache[trade_date] = set()
            self._degraded = True
            return set()
        codes: set[str] = set()
        for line in tsv.strip().split("\n"):
            code = line.split("\t")[0].strip().split(".")[0].zfill(6)
            if code:
                codes.add(code)
        self._st_cache[trade_date] = codes
        return codes


def _parse_tsv_decimal(v: str) -> Decimal | None:
    """TSV 单元格 → Decimal（''/'\\N'/非法 → None，对应 CH NULL）。"""
    s = str(v or "").strip()
    if not s or s == "\\N":
        return None
    try:
        return Decimal(s)
    except Exception:  # noqa: BLE001 — 坏行按 NULL 处理
        return None


def _fallback_pct(code: str, trade_date: datetime.date, st_flag: bool) -> Decimal | None:
    """规则切片兜底幅度（provider 数据腿）：复用 _limit_pct_of 单一真源。

    返回 None 时撮合引擎自行退板块前缀推断（_infer_limit_pct）。
    """
    try:
        from zephyr.data.implementations.akshare_provider import AkshareIngestProvider

        pct = AkshareIngestProvider._limit_pct_of(code, trade_date, st_flag)
    except Exception as e:  # noqa: BLE001 — 真源故障退引擎回退链
        _logger.warning("_limit_pct_of 切片真源调用失败（%s %s）: %s", code, trade_date, e)
        return None
    return None if pct is None else Decimal(str(pct))


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
    "LimitInfo",
    "LimitProvider",
    "StkLimitProvider",
]
