"""
引擎适配器基类
定义统一的多引擎接口标准
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pandas as pd

from ..core.base import Result, Signal, Order as CoreOrder, Position as CorePosition


class OrderSide(str, Enum):
    """订单方向"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """订单类型"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


@dataclass
class UnifiedOrder:
    """统一订单格式"""
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"
    order_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """订单执行结果"""
    order_id: str
    symbol: str
    side: OrderSide
    filled_quantity: float
    filled_price: float
    commission: float
    timestamp: datetime
    status: str  # FILLED, PARTIALLY_FILLED, CANCELLED, REJECTED
    message: Optional[str] = None


@dataclass
class EngineConfig:
    """引擎配置"""
    engine_type: str
    config: Dict[str, Any]
    initial_capital: float = 1000000.0
    commission_rate: float = 0.0003  # 万三佣金
    min_commission: float = 5.0  # 最低5元
    slippage_rate: float = 0.0002  # 基础滑点率0.02%


class BaseEngineAdapter:
    """引擎适配器基类"""
    
    def __init__(self, config: EngineConfig):
        self.config = config
        self.initialized = False
        
    def initialize(self) -> Result:
        """初始化引擎"""
        raise NotImplementedError
        
    def shutdown(self) -> Result:
        """关闭引擎"""
        raise NotImplementedError
        
    def submit_order(self, order: UnifiedOrder) -> Result:
        """提交订单"""
        raise NotImplementedError
        
    def cancel_order(self, order_id: str) -> Result:
        """取消订单"""
        raise NotImplementedError
        
    def get_positions(self) -> Result[List[CorePosition]]:
        """获取持仓列表"""
        raise NotImplementedError
        
    def get_account_info(self) -> Result[Dict[str, Any]]:
        """获取账户信息"""
        raise NotImplementedError
        
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, 
                           frequency: str = "1d") -> Result[pd.DataFrame]:
        """获取历史数据"""
        raise NotImplementedError
        
    def run_backtest(self, strategy_class: Any, data: pd.DataFrame, 
                    **kwargs) -> Result[Dict[str, Any]]:
        """运行回测"""
        raise NotImplementedError
        
    def get_performance_metrics(self) -> Result[Dict[str, Any]]:
        """获取绩效指标"""
        raise NotImplementedError
        
    def is_ashare_compatible(self) -> bool:
        """是否支持A股规则"""
        return False
        
    def supports_order_type(self, order_type: OrderType) -> bool:
        """支持的订单类型"""
        return order_type in [OrderType.MARKET, OrderType.LIMIT]
        
    def calculate_commission(self, amount: float) -> float:
        """计算佣金"""
        commission = amount * self.config.commission_rate
        return max(commission, self.config.min_commission)
        
    def estimate_slippage(self, symbol: str, quantity: float, side: OrderSide) -> float:
        """估算滑点"""
        return self.config.slippage_rate