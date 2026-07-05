# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.matching_logic
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.core.matching_engine; zephyr.ex_core.adapters.miniqmt_broker
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数式无副作用; 回测=实盘一致性; A股约束(100股整数倍/涨跌停/T+1由调用方负责)
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MatchingLogicError
# [TESTS]
# [A_module] module_id=MOD-BT-001-matching_logic | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""共享撮合逻辑模块（回测=实盘一致性核心）

职责:
  - 提供纯函数式撮合逻辑，被 D_BACKTEST matching_engine(回测) 和
    D_EX_CORE MiniQmtBroker(实盘) 共同调用，保证回测与实盘撮合行为完全一致。
  - 支持三种撮合模式:
    1. match_market_order: 市价单撮合（按盘口最优价成交）
    2. match_limit_order:  限价单撮合（限价内成交，否则不成交）
    3. match_tick_order:   Tick级5档撮合（逐档消化，流动性约束）

约束:
  - 纯函数式实现: 输入(order, order_book/tick_data, config) → 输出(MatchingFill)
  - 无副作用: 不修改输入参数，不访问外部状态，不产生I/O
  - MatchingConfig 为 frozen dataclass，实例化后不可变
  - A股约束: 100股整数倍(由调用方校验)、涨跌停(由调用方校验)、T+1(由调用方校验)
  - 本模块只负责"给定订单和盘口，计算成交结果"，不负责订单校验/持仓校验/资金校验

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7 matching_engine
      docs/03_modules/_domain_execution_core/blueprint.md §16.7.1 E 共享撮合逻辑抽取方案
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional


class MatchingLogicError(Exception):
    """撮合逻辑错误"""


@dataclass(frozen=True)
class MatchingConfig:
    """撮合配置（frozen，实例化后不可变，保证纯函数式语义）

    Attributes:
        commission_rate: 券商佣金费率(万三=0.0003)
        slippage_bps: 滑点(bps, 1bp=0.01%)
        stamp_tax_rate: 印花税率(卖出0.1%=0.001)
        min_commission: 最低佣金(5元)
        lot_size: 最小交易单位(A股100股)
        price_limit_pct: 涨跌停板限制(10%=0.10, ST股5%=0.05)
    """

    commission_rate: Decimal = Decimal("0.0003")
    slippage_bps: Decimal = Decimal("1")
    stamp_tax_rate: Decimal = Decimal("0.001")
    min_commission: Decimal = Decimal("5")
    lot_size: int = 100
    price_limit_pct: Decimal = Decimal("0.10")


@dataclass(frozen=True)
class MatchOrderInput:
    """撮合订单输入（与实盘 Order 解耦，避免跨模块依赖）

    Attributes:
        symbol: 标的代码
        side: 买卖方向 "BUY" | "SELL"
        quantity: 委托数量(股)
        order_type: 订单类型 "MARKET" | "LIMIT" | "TICK"
        limit_price: 限价(LIMIT单必填, MARKET/TICK忽略)
    """

    symbol: str
    side: str
    quantity: Decimal
    order_type: str
    limit_price: Optional[Decimal] = None


@dataclass(frozen=True)
class OrderBookSnapshot:
    """5档盘口快照（frozen，纯值对象）

    Attributes:
        symbol: 标的代码
        ask_price: 5档卖价元组 (ask1, ask2, ask3, ask4, ask5) 升序
        bid_price: 5档买价元组 (bid1, bid2, bid3, bid4, bid5) 降序
        ask_vol: 5档卖量元组
        bid_vol: 5档买量元组
        last_price: 最新价
        timestamp: 时间戳
    """

    symbol: str
    ask_price: tuple[Decimal, ...]
    bid_price: tuple[Decimal, ...]
    ask_vol: tuple[Decimal, ...]
    bid_vol: tuple[Decimal, ...]
    last_price: Decimal
    timestamp: Any = None


@dataclass(frozen=True)
class TickSnapshot:
    """Tick快照（含5档盘口，frozen，纯值对象）

    对应 xtdata Tick 18字段标准化后的结构。

    Attributes:
        symbol: 标的代码
        timestamp: 时间戳
        last_price: 最新价
        open/high/low/prev_close: OHLC + 昨收
        amount: 成交额
        volume: 成交量
        ask_price/bid_price/ask_vol/bid_vol: 5档盘口
        stock_status: 股票状态(停牌/ST等)
        transaction_num: 成交笔数
    """

    symbol: str
    timestamp: Any
    last_price: Decimal
    open: Decimal
    high: Decimal
    low: Decimal
    prev_close: Decimal
    amount: Decimal
    volume: Decimal
    ask_price: tuple[Decimal, ...]
    bid_price: tuple[Decimal, ...]
    ask_vol: tuple[Decimal, ...]
    bid_vol: tuple[Decimal, ...]
    stock_status: int = 0
    transaction_num: int = 0

    def to_order_book(self) -> OrderBookSnapshot:
        """从Tick提取5档盘口快照"""
        return OrderBookSnapshot(
            symbol=self.symbol,
            ask_price=self.ask_price,
            bid_price=self.bid_price,
            ask_vol=self.ask_vol,
            bid_vol=self.bid_vol,
            last_price=self.last_price,
            timestamp=self.timestamp,
        )


@dataclass(frozen=True)
class MatchingFill:
    """撮合成交结果（frozen，纯值对象，回测=实盘一致）

    与 BacktestFill(回测专用, 含date) 和 Fill(实盘专用, 含fill_id) 解耦。
    matching_engine 将 MatchingFill 转换为 BacktestFill(加date)。
    MiniQmtBroker 将 MatchingFill 转换为 Fill(加fill_id)。

    Attributes:
        symbol: 标的代码
        side: 买卖方向 "BUY" | "SELL"
        quantity: 成交数量(股)
        price: 成交价格(已含滑点)
        commission: 手续费(佣金+印花税)
        slippage_cost: 滑点成本 = |fill_price - base_price| * quantity
        filled: 是否完全成交 False=未成交(限价单未触达)
    """

    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    commission: Decimal
    slippage_cost: Decimal
    filled: bool = True

    @property
    def total_cost(self) -> Decimal:
        """成交总成本(买入)或总收入(卖出)"""
        gross = self.quantity * self.price
        if self.side == "BUY":
            return gross + self.commission + self.slippage_cost
        return gross - self.commission - self.slippage_cost


class MatchingLogic:
    """共享撮合逻辑（纯函数式，回测=实盘一致性核心）

    被以下模块共同调用，保证撮合行为完全一致:
      - D_BACKTEST matching_engine.py (回测撮合)
      - D_EX_CORE miniqmt_broker.py (实盘撮合预演/校验)

    纯函数式保证:
      - 实例化后 config 不可变(frozen dataclass)
      - 撮合方法不修改 self 状态
      - 撮合方法不修改输入参数
      - 撮合方法不产生I/O，不访问外部状态
      - 相同输入永远产生相同输出

    Usage:
        logic = MatchingLogic(MatchingConfig(...))
        fill = logic.match_market_order(order, order_book)
        if fill.filled:
            # 应用成交结果
            ...

    撮合规则:
      - 市价单(MARKET): BUY→ask1价成交, SELL→bid1价成交, 应用滑点
      - 限价单(LIMIT): BUY: limit_price>=ask1→ask1成交, SELL: limit_price<=bid1→bid1成交, 否则不成交
      - Tick级(TICK): 市价单逐档消化(ask1→ask2→...→ask5), 流动性约束(单档成交量上限=该档vol)
    """

    def __init__(self, config: Optional[MatchingConfig] = None):
        """初始化撮合逻辑

        Args:
            config: 撮合配置(可选, 默认MatchingConfig默认值, frozen不可变)
        """
        self._config = config or MatchingConfig()

    @property
    def config(self) -> MatchingConfig:
        """撮合配置(只读)"""
        return self._config

    def match_market_order(
        self,
        order: MatchOrderInput,
        order_book: OrderBookSnapshot,
    ) -> MatchingFill:
        """市价单撮合（按盘口最优价成交）

        撮合规则:
          - BUY: 以 ask1(最低卖价) 成交
          - SELL: 以 bid1(最高买价) 成交
          - 应用滑点: BUY price*(1+bps/10000), SELL price*(1-bps/10000)
          - 计算手续费: 佣金 max(qty*price*rate, min) + 印花税(卖出)

        Args:
            order: 委托订单(MARKET类型)
            order_book: 5档盘口快照

        Returns:
            MatchingFill 成交结果(filled=True)

        Raises:
            MatchingLogicError: 盘口为空或side无效
        """
        self._validate_order(order, expected_type="MARKET")

        if order.side == "BUY":
            if not order_book.ask_price or order_book.ask_price[0] <= 0:
                raise MatchingLogicError(f"盘口无卖价无法买入: symbol={order.symbol}")
            base_price = order_book.ask_price[0]
        elif order.side == "SELL":
            if not order_book.bid_price or order_book.bid_price[0] <= 0:
                raise MatchingLogicError(f"盘口无买价无法卖出: symbol={order.symbol}")
            base_price = order_book.bid_price[0]
        else:
            raise MatchingLogicError(f"无效side: {order.side}, 必须为BUY或SELL")

        fill_price = self._apply_slippage(base_price, order.side)
        commission = self._calc_commission(order.quantity, fill_price, order.side)
        slippage_cost = abs(fill_price - base_price) * order.quantity

        return MatchingFill(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            slippage_cost=slippage_cost,
            filled=True,
        )

    def match_limit_order(
        self,
        order: MatchOrderInput,
        order_book: OrderBookSnapshot,
    ) -> MatchingFill:
        """限价单撮合（限价内成交，否则不成交）

        撮合规则:
          - BUY: limit_price >= ask1 → 以 ask1 成交(优于限价); 否则不成交
          - SELL: limit_price <= bid1 → 以 bid1 成交(优于限价); 否则不成交
          - 应用滑点(在成交价基础上)
          - 计算手续费

        Args:
            order: 委托订单(LIMIT类型, limit_price必填)
            order_book: 5档盘口快照

        Returns:
            MatchingFill 成交结果(filled=True=成交, filled=False=未成交)

        Raises:
            MatchingLogicError: limit_price未设置或side无效
        """
        self._validate_order(order, expected_type="LIMIT")

        if order.limit_price is None or order.limit_price <= 0:
            raise MatchingLogicError(f"限价单必须设置limit_price: symbol={order.symbol}")

        if order.side == "BUY":
            if not order_book.ask_price or order_book.ask_price[0] <= 0:
                # 盘口无卖价，不成交
                return self._unfilled(order)
            ask1 = order_book.ask_price[0]
            if order.limit_price < ask1:
                # 限价低于最低卖价，不成交
                return self._unfilled(order)
            base_price = ask1
        elif order.side == "SELL":
            if not order_book.bid_price or order_book.bid_price[0] <= 0:
                return self._unfilled(order)
            bid1 = order_book.bid_price[0]
            if order.limit_price > bid1:
                # 限价高于最高买价，不成交
                return self._unfilled(order)
            base_price = bid1
        else:
            raise MatchingLogicError(f"无效side: {order.side}, 必须为BUY或SELL")

        fill_price = self._apply_slippage(base_price, order.side)
        commission = self._calc_commission(order.quantity, fill_price, order.side)
        slippage_cost = abs(fill_price - base_price) * order.quantity

        return MatchingFill(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            slippage_cost=slippage_cost,
            filled=True,
        )

    def match_tick_order(
        self,
        order: MatchOrderInput,
        tick_data: TickSnapshot,
    ) -> MatchingFill:
        """Tick级5档撮合（做T专用，逐档消化，流动性约束）

        撮合规则:
          - BUY(市价): 逐档消化 ask1→ask2→...→ask5, 单档成交量上限=该档askVol
            - 若订单量>5档总卖量, 部分成交(成交量为5档总卖量)
          - SELL(市价): 逐档消化 bid1→bid2→...→bid5, 单档成交量上限=该档bidVol
          - 限价单: 在Tick盘口上按限价单规则撮合(调用match_limit_order)
          - 加权平均成交价 = sum(单档成交量 * 单档价格) / 总成交量
          - 应用滑点(在加权均价基础上)
          - 计算手续费

        Args:
            order: 委托订单(TICK类型, 市价或限价)
            tick_data: Tick快照(含5档盘口)

        Returns:
            MatchingFill 成交结果(filled=True=完全成交, filled=False=未成交或部分成交)

        Raises:
            MatchingLogicError: 5档盘口不完整或side无效
        """
        self._validate_order(order, expected_type="TICK")

        order_book = tick_data.to_order_book()
        self._validate_order_book(order_book)

        # 限价Tick单：委托给限价单撮合
        if order.limit_price is not None:
            return self.match_limit_order(
                MatchOrderInput(
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    order_type="LIMIT",
                    limit_price=order.limit_price,
                ),
                order_book,
            )

        # 市价Tick单：逐档消化
        remaining = order.quantity
        total_value = Decimal("0")
        filled_qty = Decimal("0")

        if order.side == "BUY":
            levels = list(zip(order_book.ask_price, order_book.ask_vol))
        elif order.side == "SELL":
            levels = list(zip(order_book.bid_price, order_book.bid_vol))
        else:
            raise MatchingLogicError(f"无效side: {order.side}, 必须为BUY或SELL")

        for price, vol in levels:
            if price <= 0 or vol <= 0:
                continue
            fill_qty = min(remaining, vol)
            total_value += fill_qty * price
            filled_qty += fill_qty
            remaining -= fill_qty
            if remaining <= 0:
                break

        if filled_qty <= 0:
            return self._unfilled(order)

        # 加权平均成交价
        base_price = total_value / filled_qty
        fill_price = self._apply_slippage(base_price, order.side)
        commission = self._calc_commission(filled_qty, fill_price, order.side)
        slippage_cost = abs(fill_price - base_price) * filled_qty

        return MatchingFill(
            symbol=order.symbol,
            side=order.side,
            quantity=filled_qty,
            price=fill_price,
            commission=commission,
            slippage_cost=slippage_cost,
            filled=(remaining <= 0),
        )

    def _apply_slippage(self, price: Decimal, side: str) -> Decimal:
        """应用滑点（纯函数）

        买入价 = price * (1 + slippage_bps/10000)
        卖出价 = price * (1 - slippage_bps/10000)

        Args:
            price: 基础价格
            side: 买卖方向

        Returns:
            含滑点的价格
        """
        slippage = price * self._config.slippage_bps / Decimal("10000")
        if side == "BUY":
            return price + slippage
        elif side == "SELL":
            return price - slippage
        else:
            raise MatchingLogicError(f"无效side: {side}, 必须为BUY或SELL")

    def _calc_commission(self, quantity: Decimal, price: Decimal, side: str) -> Decimal:
        """计算手续费（纯函数: 券商佣金 + 印花税）

        券商佣金: max(quantity * price * commission_rate, min_commission)
        印花税: 卖出时 quantity * price * stamp_tax_rate

        Args:
            quantity: 成交数量
            price: 成交价格
            side: 买卖方向

        Returns:
            总手续费
        """
        gross = quantity * price
        commission = gross * self._config.commission_rate
        if commission < self._config.min_commission:
            commission = self._config.min_commission
        if side == "SELL":
            commission += gross * self._config.stamp_tax_rate
        return commission

    def _unfilled(self, order: MatchOrderInput) -> MatchingFill:
        """生成未成交结果"""
        return MatchingFill(
            symbol=order.symbol,
            side=order.side,
            quantity=Decimal("0"),
            price=Decimal("0"),
            commission=Decimal("0"),
            slippage_cost=Decimal("0"),
            filled=False,
        )

    def _validate_order(self, order: MatchOrderInput, expected_type: str) -> None:
        """校验订单基本字段"""
        if order.quantity <= 0:
            raise MatchingLogicError(f"委托数量必须>0: got {order.quantity}")
        if order.side not in ("BUY", "SELL"):
            raise MatchingLogicError(f"无效side: {order.side}, 必须为BUY或SELL")
        if order.order_type != expected_type:
            raise MatchingLogicError(
                f"订单类型不匹配: 期望{expected_type}, got {order.order_type}"
            )

    def _validate_order_book(self, order_book: OrderBookSnapshot) -> None:
        """校验5档盘口完整性"""
        if len(order_book.ask_price) < 5 or len(order_book.bid_price) < 5:
            raise MatchingLogicError(
                f"5档盘口不完整: ask_price长度={len(order_book.ask_price)}, "
                f"bid_price长度={len(order_book.bid_price)}"
            )


__all__ = [
    "MatchingConfig",
    "MatchOrderInput",
    "OrderBookSnapshot",
    "TickSnapshot",
    "MatchingFill",
    "MatchingLogic",
    "MatchingLogicError",
]
