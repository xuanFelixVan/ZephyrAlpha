"""
交易实体类
定义交易相关的核心数据结构

主要类:
    Signal - 策略信号
    Order - 订单
    Position - 持仓
"""
from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime

from src.core.validators import (
    validate_direction,
    validate_order_type,
    validate_order_status,
    validate_positive,
    validate_range,
    validate_stock_code,
)


@dataclass
class Signal:
    """
    策略信号
    
    表示策略产生的交易信号，包含信号的基本信息和元数据。
    
    属性:
        signal_id: 信号唯一标识符
        strategy_id: 产生信号的策略ID
        stock_code: 股票代码 (格式: XXXXXX.SH/SZ)
        direction: 交易方向 ('long' 多头 或 'short' 空头)
        strength: 信号强度 (0.0 - 1.0，1.0表示最强)
        entry_price: 建议入场价格
        timestamp: 信号产生的时间戳
        metadata: 元数据字典，可包含额外信息
    
    示例:
        >>> signal = Signal(
        ...     signal_id='SIG_20260402_001',
        ...     strategy_id='STRAT_001',
        ...     stock_code='000001.SZ',
        ...     direction='long',
        ...     strength=0.8,
        ...     entry_price=10.5,
        ...     timestamp=datetime.now()
        ... )
        >>> signal.direction
        'long'
    
    注意:
        - direction必须是'long'或'short'
        - strength必须在0.0到1.0之间
        - stock_code格式必须为'XXXXXX.EXCHANGE'
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
        """初始化后验证"""
        if self.metadata is None:
            self.metadata = {}
        
        # 验证方向
        self.direction = validate_direction(self.direction, ('long', 'short'))
        
        # 验证强度
        self.strength = validate_range(self.strength, 0.0, 1.0, 'strength')
        
        # 验证股票代码
        self.stock_code = validate_stock_code(self.stock_code)
        
        # 验证入场价格
        self.entry_price = validate_positive(self.entry_price, 'entry_price')


@dataclass
class Order:
    """
    交易订单
    
    表示交易订单的完整生命周期，从创建到成交。
    
    属性:
        order_id: 订单唯一标识符
        signal_id: 关联的信号ID
        stock_code: 股票代码 (格式: XXXXXX.SH/SZ)
        direction: 交易方向 ('buy' 买入 或 'sell' 卖出)
        order_type: 订单类型 ('market' 市价单 或 'limit' 限价单)
        price: 订单价格 (限价单为限价，市价单为参考价)
        quantity: 订单数量 (股数，必须是正整数)
        status: 订单状态 ('pending' | 'filled' | 'cancelled' | 'rejected')
        timestamp: 订单创建时间戳
        filled_price: 成交价格 (订单成交后填充)
        filled_quantity: 成交数量 (订单成交后填充)
    
    示例:
        >>> order = Order(
        ...     order_id='ORD_20260402_001',
        ...     signal_id='SIG_20260402_001',
        ...     stock_code='000001.SZ',
        ...     direction='buy',
        ...     order_type='limit',
        ...     price=10.5,
        ...     quantity=1000
        ... )
        >>> order.status
        'pending'
    
    注意:
        - direction必须是'buy'或'sell'
        - order_type必须是'market'或'limit'
        - status必须是'pending', 'filled', 'cancelled', 'rejected'之一
        - quantity必须是正整数
        - price必须是正数
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
        """初始化后验证"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # 验证方向
        self.direction = validate_direction(self.direction, ('buy', 'sell'))
        
        # 验证订单类型
        self.order_type = validate_order_type(self.order_type)
        
        # 验证状态
        self.status = validate_order_status(self.status)
        
        # 验证数量
        self.quantity = int(validate_positive(self.quantity, 'quantity'))
        
        # 验证价格
        self.price = validate_positive(self.price, 'price')
        
        # 验证股票代码
        self.stock_code = validate_stock_code(self.stock_code)

    def is_active(self) -> bool:
        """检查订单是否活跃（未完成）"""
        return self.status in ('pending',)

    def is_completed(self) -> bool:
        """检查订单是否已完成"""
        return self.status in ('filled', 'cancelled', 'rejected')

    def fill(self, filled_price: float, filled_quantity: int) -> None:
        """
        填充订单成交信息
        
        参数:
            filled_price: 成交价格
            filled_quantity: 成交数量
        """
        self.filled_price = filled_price
        self.filled_quantity = filled_quantity
        self.status = 'filled'


@dataclass
class Position:
    """
    持仓信息
    
    表示当前持有的股票仓位和盈亏情况。
    
    属性:
        stock_code: 股票代码 (格式: XXXXXX.SH/SZ)
        quantity: 持仓数量 (股数)
        avg_cost: 平均持仓成本 (每股成本)
        current_price: 当前市场价格
        unrealized_pnl: 浮动盈亏 (自动计算)
        realized_pnl: 已实现盈亏
    
    计算属性:
        market_value: 市值 (当前价格 × 持仓数量)
        cost_value: 成本 (平均成本 × 持仓数量)
        pnl_pct: 盈亏比例 ((当前价格 - 平均成本) / 平均成本)
    
    示例:
        >>> position = Position(
        ...     stock_code='000001.SZ',
        ...     quantity=1000,
        ...     avg_cost=10.0,
        ...     current_price=11.0
        ... )
        >>> position.market_value
        11000.0
        >>> position.unrealized_pnl
        1000.0
        >>> position.pnl_pct
        0.1  # 10%盈利
    
    注意:
        - quantity必须是正整数
        - avg_cost和current_price必须是正数
        - unrealized_pnl在初始化时自动计算
    """
    stock_code: str
    quantity: int
    avg_cost: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

    def __post_init__(self):
        """初始化后计算浮动盈亏"""
        # 验证数量
        self.quantity = int(validate_positive(self.quantity, 'quantity'))
        
        # 验证成本和价格
        self.avg_cost = validate_positive(self.avg_cost, 'avg_cost')
        self.current_price = validate_positive(self.current_price, 'current_price')
        
        # 验证股票代码
        self.stock_code = validate_stock_code(self.stock_code)
        
        # 计算浮动盈亏
        self.unrealized_pnl = (self.current_price - self.avg_cost) * self.quantity

    @property
    def market_value(self) -> float:
        """
        当前市值
        
        返回:
            float: 持仓的当前市场价值
        """
        return self.current_price * self.quantity

    @property
    def cost_value(self) -> float:
        """
        持仓成本
        
        返回:
            float: 持仓的总成本
        """
        return self.avg_cost * self.quantity

    @property
    def pnl_pct(self) -> float:
        """
        盈亏比例
        
        返回:
            float: 盈亏比例 (0.1表示10%盈利，-0.1表示10%亏损)
        """
        if self.cost_value == 0:
            return 0.0
        return (self.current_price - self.avg_cost) / self.avg_cost

    def update_price(self, new_price: float) -> None:
        """
        更新当前价格并重新计算浮动盈亏
        
        参数:
            new_price: 新的市场价格
        """
        self.current_price = validate_positive(new_price, 'current_price')
        self.unrealized_pnl = (self.current_price - self.avg_cost) * self.quantity

    def add_position(self, quantity: int, price: float) -> None:
        """
        增加持仓
        
        参数:
            quantity: 增加的数量
            price: 增加的成本价格
        """
        quantity = int(validate_positive(quantity, 'quantity'))
        price = validate_positive(price, 'price')
        
        # 计算新的平均成本
        total_cost = self.cost_value + (price * quantity)
        total_quantity = self.quantity + quantity
        self.avg_cost = total_cost / total_quantity
        self.quantity = total_quantity
        
        # 重新计算浮动盈亏
        self.unrealized_pnl = (self.current_price - self.avg_cost) * self.quantity

    def reduce_position(self, quantity: int, price: float) -> None:
        """
        减少持仓
        
        参数:
            quantity: 减少的数量
            price: 卖出价格
        """
        quantity = int(validate_positive(quantity, 'quantity'))
        price = validate_positive(price, 'price')
        
        if quantity > self.quantity:
            raise ValueError(f"Cannot reduce {quantity} shares, only {self.quantity} available")
        
        # 计算已实现盈亏
        realized = (price - self.avg_cost) * quantity
        self.realized_pnl += realized
        
        # 减少持仓
        self.quantity -= quantity
        
        # 重新计算浮动盈亏
        self.unrealized_pnl = (self.current_price - self.avg_cost) * self.quantity
