"""
核心基础类
"""
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime


@dataclass
class Result:
    """统一返回格式"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_success(self) -> bool:
        return self.success


@dataclass
class Signal:
    """策略信号"""
    signal_id: str
    strategy_id: str
    stock_code: str
    direction: str  # 'long' | 'short'
    strength: float  # 0.0 - 1.0
    entry_price: float
    timestamp: datetime
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Order:
    """订单"""
    order_id: str
    signal_id: str
    stock_code: str
    direction: str  # 'buy' | 'sell'
    order_type: str  # 'market' | 'limit'
    price: float
    quantity: int
    status: str = 'pending'  # 'pending' | 'filled' | 'cancelled'
    timestamp: datetime = None
    filled_price: float = None
    filled_quantity: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Position:
    """持仓"""
    stock_code: str
    quantity: int
    avg_cost: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

    def __post_init__(self):
        self.unrealized_pnl = (self.current_price - self.avg_cost) * self.quantity


class SystemException(Exception):
    """系统异常基类"""
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DataException(SystemException):
    """数据异常"""
    pass


class FactorException(SystemException):
    """因子异常"""
    pass


class StrategyException(SystemException):
    """策略异常"""
    pass


class RiskException(SystemException):
    """风险异常"""
    pass


class ExecutionException(SystemException):
    """执行异常"""
    pass
