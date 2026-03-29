"""
核心基础类
定义清风量化交易系统的核心数据结构

主要类:
    Result - 统一返回格式
    Signal - 策略信号
    Order - 订单
    Position - 持仓
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from datetime import datetime


@dataclass
class Result:
    """统一返回格式

    用于函数返回值封装，提供成功/失败状态、数据和错误信息。

    属性:
        success: 是否成功
        data: 返回数据
        error: 错误信息
        metadata: 元数据

    示例:
        >>> result = Result(success=True, data={"price": 100.0})
        >>> if result.is_success:
        ...     print(result.data["price"])
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_success(self) -> bool:
        """检查是否成功"""
        return self.success

    @property
    def is_failure(self) -> bool:
        """检查是否失败"""
        return not self.success


@dataclass
class Signal:
    """策略信号

    表示策略产生的交易信号。

    属性:
        signal_id: 信号唯一标识
        strategy_id: 策略ID
        stock_code: 股票代码
        direction: 方向 ('long' 或 'short')
        strength: 信号强度 (0.0 - 1.0)
        entry_price: 入场价格
        timestamp: 信号时间戳
        metadata: 元数据
    """
    signal_id: str
    strategy_id: str
    stock_code: str
    direction: str
    strength: float
    entry_price: float
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.direction not in ("long", "short"):
            raise ValueError(f"direction must be 'long' or 'short', got '{self.direction}'")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"strength must be between 0.0 and 1.0, got {self.strength}")


@dataclass
class Order:
    """订单

    表示交易订单。

    属性:
        order_id: 订单唯一标识
        signal_id: 关联信号ID
        stock_code: 股票代码
        direction: 方向 ('buy' 或 'sell')
        order_type: 订单类型 ('market' 或 'limit')
        price: 订单价格
        quantity: 订单数量
        status: 订单状态 ('pending' | 'filled' | 'cancelled' | 'rejected')
        timestamp: 订单创建时间戳
        filled_price: 成交价格
        filled_quantity: 成交数量
    """
    order_id: str
    signal_id: str
    stock_code: str
    direction: str
    order_type: str
    price: float
    quantity: int
    status: str = 'pending'
    timestamp: datetime = None
    filled_price: float = None
    filled_quantity: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.direction not in ("buy", "sell"):
            raise ValueError(f"direction must be 'buy' or 'sell', got '{self.direction}'")
        if self.order_type not in ("market", "limit"):
            raise ValueError(f"order_type must be 'market' or 'limit', got '{self.order_type}'")
        if self.status not in ("pending", "filled", "cancelled", "rejected"):
            raise ValueError(f"Invalid status: {self.status}")
        if self.quantity <= 0:
            raise ValueError(f"quantity must be positive, got {self.quantity}")
        if self.price <= 0:
            raise ValueError(f"price must be positive, got {self.price}")


@dataclass
class Position:
    """持仓

    表示当前持仓信息。

    属性:
        stock_code: 股票代码
        quantity: 持仓数量
        avg_cost: 平均成本
        current_price: 当前价格
        unrealized_pnl: 浮动盈亏
        realized_pnl: 已实现盈亏
    """
    stock_code: str
    quantity: int
    avg_cost: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

    def __post_init__(self):
        self.unrealized_pnl = (self.current_price - self.avg_cost) * self.quantity

    @property
    def market_value(self) -> float:
        """市值"""
        return self.current_price * self.quantity

    @property
    def cost_value(self) -> float:
        """成本"""
        return self.avg_cost * self.quantity

    @property
    def pnl_pct(self) -> float:
        """盈亏比例"""
        if self.cost_value == 0:
            return 0.0
        return (self.current_price - self.avg_cost) / self.avg_cost
