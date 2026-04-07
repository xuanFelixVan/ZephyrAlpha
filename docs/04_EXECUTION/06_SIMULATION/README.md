---
module_id: README
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: EXEC_SIMULATION_README_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 说明文档、快速入门
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# 模拟交易系统
> **核心职责**: 模块说明和快速入门指南
> **职责边界**: 
> - ✅ 本文档负责：模块说明和快速入门指南相关内容
> - ❌ 本文档不负责：其他模块内容


> Layer 5: 交易执行 - 模拟环境、订单模拟、持仓管理、成交回?

---

## 1. 系统架构

```
模拟交易系统
├── 模拟环境管理?(Simulation Environment)
?  ├── 市场模拟?
?  ├── 订单模拟?
?  ├── 成交模拟?
?  └── 滑点模型
├── 持仓管理系统 (Position Manager)
?  ├── 持仓跟踪
?  ├── 成本计算
?  ├── 盈亏计算
?  └── 保证金计?
├── 订单执行模拟 (Order Execution)
?  ├── 市价单模?
?  ├── 限价单模?
?  ├── 条件单模?
?  └── 冰山订单模拟
├── 交易成本模型 (Cost Model)
?  ├── 佣金计算
?  ├── 印花税计?
?  ├── 滑点计算
?  └── 冲击成本模型
└── 结果记录?(Result Logger)
    ├── 成交记录
    ├── 持仓快照
    └── 每日结算
```

---

## 2. 核心数据结构

### 2.1 模拟环境配置

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from enum import Enum
import numpy as np


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"           # 市价?
    LIMIT = "limit"            # 限价?
    STOP = "stop"             # 止损?
    STOP_LIMIT = "stop_limit"  # 止损限价?


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """订单状?""
    PENDING = "pending"       # 待成?
    PARTIAL = "partial"       # 部分成交
    FILLED = "filled"         # 全部成交
    CANCELLED = "cancelled"   # 已取?
    REJECTED = "rejected"     # 已拒?
    EXPIRED = "expired"       # 已过?


class TimeInForce(Enum):
    """有效?""
    DAY = "day"               # 当日有效
    GTC = "gtc"              # 取消前有?
    IOC = "ioc"              # 立即成交或取?
    FOK = "fok"              # 全数成交或取?


@dataclass
class SimulatedOrder:
    """模拟订单"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None           # 限价单价?
    stop_price: Optional[float] = None       # 止损价格
    filled_quantity: int = 0
    avg_fill_price: float = 0
    status: OrderStatus = OrderStatus.PENDING
    time_in_force: TimeInForce = TimeInForce.DAY
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None


@dataclass
class SimulatedPosition:
    """模拟持仓"""
    symbol: str
    quantity: int
    avg_cost: float
    total_cost: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    today_quantity: int         # 今日买入数量
    today_pnl: float           # 今日盈亏


@dataclass
class SimulatedAccount:
    """模拟账户"""
    account_id: str
    cash: float
    total_value: float
    market_value: float
    total_pnl: float
    total_pnl_pct: float
    daily_pnl: float
    daily_pnl_pct: float
    positions: Dict[str, SimulatedPosition]
    available_cash: float
    margin_used: float
    leverage: float
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SimulationConfig:
    """模拟配置"""
    initial_cash: float = 1000000
    commission_rate: float = 0.0003      # 佣金万分?
    stamp_tax_rate: float = 0.001        # 印花税千分之1
    slippage_model: str = "percentage"   # 滑点模型
    slippage_rate: float = 0.0005        # 滑点?.05%
    market_impact_model: str = "square_root"  # 市场冲击模型
    fill_probability: float = 0.99       # 成交概率
    partial_fill_ratio: float = 0.5      # 部分成交比例
    simulate_halt: bool = True            # 模拟停牌
    simulate_limit_up: bool = True        # 模拟涨停
    simulate_limit_down: bool = True      # 模拟跌停
```

---

## 3. 市场模拟?

### 3.1 市场模拟器核?

```python
class MarketSimulator:
    """市场模拟?""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.current_price: Dict[str, float] = {}
        self.volume: Dict[str, int] = {}
        self.limit_up: Dict[str, float] = {}
        self.limit_down: Dict[str, float] = {}
        self.is_halted: Dict[str, bool] = {}

    def load_market_data(self, symbol: str, data: pd.DataFrame):
        """加载市场数据"""
        self.market_data[symbol] = data

        if len(data) > 0:
            latest = data.iloc[-1]
            self.current_price[symbol] = latest.get("close", 0)
            self.volume[symbol] = latest.get("volume", 0)

    def set_current_time(self, timestamp: datetime):
        """设置当前时间"""
        self.current_time = timestamp

        for symbol in self.market_data.keys():
            self._update_market_status(symbol)

    def _update_market_status(self, symbol: str):
        """更新市场状?""
        data = self.market_data.get(symbol)

        if data is None or len(data) == 0:
            return

        if self.current_time in data.index:
            bar = data.loc[self.current_time]
        else:
            bar = data.iloc[-1]

        self.current_price[symbol] = bar.get("close", 0)
        self.volume[symbol] = bar.get("volume", 0)

        prev_close = bar.get("preclose", bar.get("close", 0))

        if prev_close > 0:
            self.limit_up[symbol] = prev_close * 1.10
            self.limit_down[symbol] = prev_close * 0.90
        else:
            self.limit_up[symbol] = float("inf")
            self.limit_down[symbol] = 0

        self.is_halted[symbol] = bar.get("is_halted", False)

    def get_current_price(self, symbol: str) -> float:
        """获取当前价格"""
        return self.current_price.get(symbol, 0)

    def get_bid_ask(self, symbol: str) -> tuple:
        """获取买卖报价"""
        price = self.get_current_price(symbol)
        spread = price * 0.0002

        return price - spread / 2, price + spread / 2

    def can_trade(self, symbol: str, side: OrderSide) -> tuple:
        """检查是否可以交?

        返回:
            (can_trade, reason)
        """
        if symbol not in self.current_price:
            return False, "无市场数?

        if self.is_halted.get(symbol, False):
            return False, "股票停牌"

        price = self.current_price[symbol]

        if price <= 0:
            return False, "价格无效"

        if side == OrderSide.BUY:
            if price >= self.limit_up.get(symbol, float("inf")):
                return False, "涨停无法买入"
        else:
            if price <= self.limit_down.get(symbol, 0):
                return False, "跌停无法卖出"

        return True, ""

    def simulate_fill(
        self,
        order: SimulatedOrder,
        requested_price: float,
        requested_quantity: int
    ) -> tuple:
        """模拟成交

        返回:
            (filled_quantity, fill_price, status)
        """
        can_trade, reason = self.can_trade(order.symbol, order.side)

        if not can_trade:
            return 0, 0, OrderStatus.REJECTED, reason

        current_price = self.get_current_price(order.symbol)

        if order.order_type == OrderType.MARKET:
            fill_price = self._apply_slippage(current_price, order.side)
        elif order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and requested_price < current_price:
                return 0, 0, OrderStatus.PENDING, "价格过高"
            elif order.side == OrderSide.SELL and requested_price > current_price:
                return 0, 0, OrderStatus.PENDING, "价格过低"
            fill_price = min(requested_price, current_price) if order.side == OrderSide.BUY else max(requested_price, current_price)
        else:
            fill_price = current_price

        fill_prob = self.config.fill_probability

        if np.random.random() > fill_prob:
            return 0, 0, OrderStatus.PENDING, "成交概率未满?

        if np.random.random() < self.config.partial_fill_ratio:
            filled_qty = int(requested_quantity * np.random.uniform(0.3, 0.7))
            if filled_qty > 0:
                return filled_qty, fill_price, OrderStatus.PARTIAL, ""
            else:
                return 0, 0, OrderStatus.PENDING, "部分成交数量?"

        return requested_quantity, fill_price, OrderStatus.FILLED, ""

    def _apply_slippage(self, price: float, side: OrderSide) -> float:
        """应用滑点"""
        if self.config.slippage_model == "percentage":
            slippage = price * self.config.slippage_rate
        elif self.config.slippage_model == "fixed":
            slippage = self.config.slippage_rate
        else:
            slippage = 0

        return price + slippage if side == OrderSide.BUY else price - slippage
```

---

## 4. 订单执行模拟

### 4.1 订单模拟?

```python
class OrderSimulator:
    """订单模拟?""

    def __init__(
        self,
        market_simulator: MarketSimulator,
        config: SimulationConfig
    ):
        self.market = market_simulator
        self.config = config
        self.pending_orders: Dict[str, SimulatedOrder] = {}
        self.filled_orders: Dict[str, SimulatedOrder] = {}
        self.order_counter = 0

    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> SimulatedOrder:
        """提交订单"""
        self.order_counter += 1

        order = SimulatedOrder(
            order_id=f"SIM{self.order_counter:08d}",
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force
        )

        self.pending_orders[order.order_id] = order

        return order

    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        if order_id not in self.pending_orders:
            return False

        order = self.pending_orders[order_id]
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now()

        del self.pending_orders[order_id]

        return True

    def process_pending_orders(self, timestamp: datetime = None):
        """处理待成交订?""
        if timestamp is None:
            timestamp = datetime.now()

        self.market.set_current_time(timestamp)

        to_remove = []

        for order_id, order in self.pending_orders.items():
            if order.status != OrderStatus.PENDING:
                to_remove.append(order_id)
                continue

            price = order.price or self.market.get_current_price(order.symbol)

            filled_qty, fill_price, status, reason = self.market.simulate_fill(
                order, price, order.quantity - order.filled_quantity
            )

            if filled_qty > 0:
                order.filled_quantity += filled_qty
                order.avg_fill_price = (
                    (order.avg_fill_price * (order.filled_quantity - filled_qty) +
                     fill_price * filled_qty) / order.filled_quantity
                )
                order.status = status
                order.updated_at = timestamp

                if status == OrderStatus.FILLED:
                    order.filled_at = timestamp
                    to_remove.append(order_id)

            elif status in [OrderStatus.REJECTED, OrderStatus.CANCELLED]:
                order.status = status
                order.rejection_reason = reason
                order.updated_at = timestamp
                to_remove.append(order_id)

        for order_id in to_remove:
            if order_id in self.pending_orders:
                order = self.pending_orders.pop(order_id)
                self.filled_orders[order_id] = order

    def get_order(self, order_id: str) -> Optional[SimulatedOrder]:
        """获取订单"""
        return self.pending_orders.get(order_id) or self.filled_orders.get(order_id)

    def get_pending_orders(self, symbol: str = None) -> List[SimulatedOrder]:
        """获取待成交订?""
        orders = list(self.pending_orders.values())

        if symbol:
            orders = [o for o in orders if o.symbol == symbol]

        return orders
```

---

## 5. 持仓管理

### 5.1 持仓管理?

```python
class PositionManager:
    """持仓管理?""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.positions: Dict[str, SimulatedPosition] = {}
        self.initial_cash = config.initial_cash

    def update_position_from_trade(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        price: float
    ):
        """根据成交更新持仓"""
        if side == OrderSide.BUY:
            self._add_position(symbol, quantity, price)
        else:
            self._reduce_position(symbol, quantity, price)

    def _add_position(
        self,
        symbol: str,
        quantity: int,
        price: float
    ):
        """增加持仓"""
        cost = quantity * price

        if symbol in self.positions:
            pos = self.positions[symbol]
            new_quantity = pos.quantity + quantity
            new_cost = pos.total_cost + cost

            pos.quantity = new_quantity
            pos.avg_cost = new_cost / new_quantity
            pos.total_cost = new_cost
            pos.today_quantity += quantity

        else:
            self.positions[symbol] = SimulatedPosition(
                symbol=symbol,
                quantity=quantity,
                avg_cost=price,
                total_cost=cost,
                market_value=0,
                unrealized_pnl=0,
                realized_pnl=0,
                today_quantity=quantity,
                today_pnl=0
            )

    def _reduce_position(
        self,
        symbol: str,
        quantity: int,
        price: float
    ):
        """减少持仓"""
        if symbol not in self.positions:
            return

        pos = self.positions[symbol]

        sell_cost = quantity * price
        avg_cost_value = pos.avg_cost * quantity

        realized_pnl = sell_cost - avg_cost_value

        pos.quantity -= quantity
        pos.total_cost -= avg_cost_value
        pos.realized_pnl += realized_pnl

        if pos.quantity == 0:
            del self.positions[symbol]

    def update_market_value(self, symbol: str, current_price: float):
        """更新市?""
        if symbol in self.positions:
            pos = self.positions[symbol]
            pos.market_value = pos.quantity * current_price
            pos.unrealized_pnl = pos.market_value - pos.total_cost

    def update_all_market_values(self, prices: Dict[str, float]):
        """更新所有持仓市?""
        for symbol, price in prices.items():
            self.update_market_value(symbol, price)

    def get_position(self, symbol: str) -> Optional[SimulatedPosition]:
        """获取持仓"""
        return self.positions.get(symbol)

    def get_all_positions(self) -> Dict[str, SimulatedPosition]:
        """获取所有持?""
        return self.positions.copy()

    def get_total_market_value(self) -> float:
        """获取总市?""
        return sum(pos.market_value for pos in self.positions.values())

    def get_total_realized_pnl(self) -> float:
        """获取总已实现盈亏"""
        return sum(pos.realized_pnl for pos in self.positions.values())

    def calculate_position_summary(self) -> Dict:
        """计算持仓汇?""
        positions_list = []

        for symbol, pos in self.positions.items():
            positions_list.append({
                "symbol": symbol,
                "quantity": pos.quantity,
                "avg_cost": pos.avg_cost,
                "market_value": pos.market_value,
                "unrealized_pnl": pos.unrealized_pnl,
                "unrealized_pnl_pct": pos.unrealized_pnl / pos.total_cost if pos.total_cost > 0 else 0,
                "today_quantity": pos.today_quantity
            })

        return {
            "total_positions": len(self.positions),
            "total_market_value": self.get_total_market_value(),
            "total_realized_pnl": self.get_total_realized_pnl(),
            "positions": positions_list
        }
```

---

## 6. 交易成本计算

### 6.1 成本计算?

```python
class CostCalculator:
    """交易成本计算?""

    def __init__(self, config: SimulationConfig):
        self.config = config

    def calculate_commission(
        self,
        side: OrderSide,
        quantity: int,
        price: float
    ) -> float:
        """计算佣金"""
        trade_value = quantity * price

        commission = trade_value * self.config.commission_rate

        min_commission = max(5, trade_value * 0.00005)

        return max(commission, min_commission)

    def calculate_stamp_tax(
        self,
        side: OrderSide,
        quantity: int,
        price: float
    ) -> float:
        """计算印花税（仅卖出时收取?""
        if side == OrderSide.BUY:
            return 0

        trade_value = quantity * price
        return trade_value * self.config.stamp_tax_rate

    def calculate_slippage(
        self,
        side: OrderSide,
        quantity: int,
        price: float
    ) -> float:
        """计算滑点成本"""
        if self.config.slippage_model == "percentage":
            slippage = price * self.config.slippage_rate
        elif self.config.slippage_model == "fixed":
            slippage = self.config.slippage_rate
        else:
            slippage = 0

        return quantity * slippage

    def calculate_market_impact(
        self,
        side: OrderSide,
        quantity: int,
        price: float,
        daily_volume: int
    ) -> float:
        """计算市场冲击成本"""
        if daily_volume <= 0:
            return 0

        participation_rate = quantity / daily_volume

        if self.config.market_impact_model == "square_root":
            impact = price * 0.1 * np.sqrt(participation_rate)
        elif self.config.market_impact_model == "linear":
            impact = price * 0.05 * participation_rate
        else:
            impact = 0

        return quantity * impact

    def calculate_total_cost(
        self,
        side: OrderSide,
        quantity: int,
        price: float,
        daily_volume: int = 0
    ) -> Dict[str, float]:
        """计算总成?""
        commission = self.calculate_commission(side, quantity, price)
        stamp_tax = self.calculate_stamp_tax(side, quantity, price)
        slippage = self.calculate_slippage(side, quantity, price)
        market_impact = self.calculate_market_impact(side, quantity, price, daily_volume)

        total_cost = commission + stamp_tax + slippage + market_impact
        total_cost_pct = total_cost / (quantity * price) if quantity * price > 0 else 0

        return {
            "commission": commission,
            "stamp_tax": stamp_tax,
            "slippage": slippage,
            "market_impact": market_impact,
            "total_cost": total_cost,
            "total_cost_pct": total_cost_pct
        }
```

---

## 7. 模拟交易引擎

### 7.1 主引?

```python
class SimulationEngine:
    """模拟交易引擎"""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.market = MarketSimulator(config)
        self.order_simulator = OrderSimulator(self.market, config)
        self.position_manager = PositionManager(config)
        self.cost_calculator = CostCalculator(config)

        self.cash = config.initial_cash
        self.initial_cash = config.initial_cash

        self.trade_history: List[Dict] = []
        self.daily_summary: List[Dict] = []

    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None
    ) -> SimulatedOrder:
        """提交订单"""
        return self.order_simulator.submit_order(
            symbol, side, order_type, quantity, price
        )

    def process_trading_cycle(self, timestamp: datetime = None):
        """处理交易周期"""
        self.order_simulator.process_pending_orders(timestamp)

        self._process_filled_orders(timestamp)

        self._update_account_value()

    def _process_filled_orders(self, timestamp: datetime):
        """处理成交订单"""
        for order in self.order_simulator.filled_orders.values():
            if order.status == OrderStatus.FILLED and order.filled_quantity > 0:

                cost = self.cost_calculator.calculate_total_cost(
                    order.side,
                    order.filled_quantity,
                    order.avg_fill_price
                )

                trade_value = order.filled_quantity * order.avg_fill_price

                if order.side == OrderSide.BUY:
                    self.cash -= (trade_value + cost["total_cost"])
                else:
                    self.cash += (trade_value - cost["total_cost"])

                self.position_manager.update_position_from_trade(
                    order.symbol,
                    order.side,
                    order.filled_quantity,
                    order.avg_fill_price
                )

                self.trade_history.append({
                    "order_id": order.order_id,
                    "timestamp": timestamp or order.filled_at,
                    "symbol": order.symbol,
                    "side": order.side.value,
                    "quantity": order.filled_quantity,
                    "price": order.avg_fill_price,
                    "trade_value": trade_value,
                    "commission": cost["commission"],
                    "stamp_tax": cost["stamp_tax"],
                    "slippage": cost["slippage"],
                    "total_cost": cost["total_cost"]
                })

    def _update_account_value(self):
        """更新账户价?""
        for symbol, pos in self.position_manager.positions.items():
            price = self.market.get_current_price(symbol)
            self.position_manager.update_market_value(symbol, price)

    def get_account_summary(self) -> SimulatedAccount:
        """获取账户摘要"""
        market_value = self.position_manager.get_total_market_value()
        realized_pnl = self.position_manager.get_total_realized_pnl()

        total_value = self.cash + market_value
        total_pnl = total_value - self.initial_cash
        total_pnl_pct = total_pnl / self.initial_cash

        return SimulatedAccount(
            account_id="SIM001",
            cash=self.cash,
            total_value=total_value,
            market_value=market_value,
            total_pnl=total_pnl,
            total_pnl_pct=total_pnl_pct,
            daily_pnl=0,
            daily_pnl_pct=0,
            positions=self.position_manager.get_all_positions(),
            available_cash=self.cash,
            margin_used=0,
            leverage=0
        )

    def generate_daily_report(self, date: date) -> str:
        """生成每日报告"""
        day_trades = [t for t in self.trade_history
                     if pd.to_datetime(t["timestamp"]).date() == date]

        account = self.get_account_summary()

        lines = [
            "=" * 80,
            f"模拟交易日报 - {date}",
            "=" * 80,
            "",
            "账户概况:",
            f"  总资? {account.total_value:,.2f}",
            f"  现金: {account.cash:,.2f}",
            f"  持仓市? {account.market_value:,.2f}",
            f"  总盈? {account.total_pnl:,.2f} ({account.total_pnl_pct:.2%})",
            "",
            "持仓明细:",
        ]

        for symbol, pos in account.positions.items():
            lines.append(
                f"  {symbol}: {pos.quantity}? "
                f"成本价{pos.avg_cost:.2f}, "
                f"现价{self.market.get_current_price(symbol):.2f}, "
                f"浮盈{pos.unrealized_pnl:,.2f}"
            )

        lines.append("")
        lines.append(f"今日成交: {len(day_trades)}?)

        return "\n".join(lines)
```

---

## 8. 使用示例

```python
def example_simulation():
    """模拟交易使用示例"""

    config = SimulationConfig(
        initial_cash=1000000,
        commission_rate=0.0003,
        stamp_tax_rate=0.001,
        slippage_rate=0.0005
    )

    engine = SimulationEngine(config)

    engine.market.load_market_data(
        "000001.SZ",
        pd.read_csv("000001.SZ.csv", parse_dates=True, index_col=0)
    )

    for i in range(10):
        timestamp = pd.Timestamp("2025-01-01") + pd.Timedelta(days=i)

        engine.market.set_current_time(timestamp)
        engine.process_trading_cycle(timestamp)

        if i == 2:
            engine.submit_order(
                symbol="000001.SZ",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=1000,
                price=10.5
            )

    account = engine.get_account_summary()

    print(f"总资? {account.total_value:,.2f}")
    print(f"总盈? {account.total_pnl:,.2f} ({account.total_pnl_pct:.2%})")
```

---

**版本**: 1.0
**更新**: 2026-03-28
**Layer**: Layer 5 (交易执行)
**索引**: BLUEPRINTS.md ?模拟交易蓝图
**上游接口**: StrategyEngine (M03), BacktestEngine (M15)
**下游接口**: RiskMonitor (M07), TradeExecutor (M06)

---

## 9. 多引擎架构扩?

为满足不同场景的模拟交易需求，系统设计了多引擎架构，支持三种主流开源交易引擎：

### 9.1 支持的引?

| 引擎 | 定位 | 适用场景 | 详细设计 |
|------|------|----------|----------|
| **vn.py** | 生产级主引擎 | A股实?模拟、机构级交易 |  |
| **RQAlpha** | 专业回测引擎 | A股深度回测、策略研?|  |
| **Backtrader** | 功能补充引擎 | 多资产测试、高级订单类?|  |

### 9.2 统一接口设计

所有引擎通过统一接口层进行适配，提供一致的API?
- 统一订单模型 (`UnifiedOrder`)
- 抽象引擎接口 (`BaseEngineAdapter`)
- 引擎工厂模式 (`EngineFactory`)
- 多引擎协同器 (`MultiEngine`)

详细设计参见?

### 9.3 引擎切换策略

系统支持动态引擎切换，根据场景自动选择最佳引擎：
- **A股实盘模?*: vn.py仿真引擎（默认）
- **策略研究回测**: RQAlpha专业回测引擎
- **多资产测?*: Backtrader引擎
- **故障转移**: 主引擎失败时自动切换到备份引?

详细配置参见?

### 9.4 完整多引擎蓝?

完整的多引擎架构设计、实施路线图、性能测试方案详见?
**[MULTI_ENGINE_BLUEPRINT.md](04_EXECUTION/06_SIMULATION/MULTI_ENGINE_BLUEPRINT.md)**
