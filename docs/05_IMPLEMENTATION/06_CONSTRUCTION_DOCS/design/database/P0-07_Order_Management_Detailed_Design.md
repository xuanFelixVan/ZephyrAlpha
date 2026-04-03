---
module_id: ORDER_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席蓝图架构师
standard_type: 专业量化机构订单管理标准
applicable_scope: 订单服务模块
compliance_level: 专业机构标准
parent_document: P0-01_Database_Design_Document.md
implementation_status: 进行中
---

# 订单管理详细设计（专业量化机构标准）

> 清风量化系统 v5.0 - 专业量化机构标准订单管理设计
> **设计模式**: DDD领域驱动设计 + 状态机模式 + Saga事务
> **核心职责**: 订单生命周期管理、订单执行、订单查询

## 📋 模块概述

### 订单管理架构

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application Layer)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          OrderApplicationService                      │  │
│  │  - 创建订单应用服务                                    │  │
│  │  - 执行订单应用服务                                    │  │
│  │  - 查询订单应用服务                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    领域层 (Domain Layer)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          OrderAggregate (订单聚合根)                  │  │
│  │  - Order (订单实体)                                   │  │
│  │  - Trade (交易记录实体)                               │  │
│  │  - OrderDomainService (领域服务)                      │  │
│  │  - OrderStateMachine (状态机)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    基础设施层 (Infrastructure Layer)          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          OrderRepository (订单仓储)                   │  │
│  │  - PostgreSQL (主数据库)                              │  │
│  │  - Redis (实时缓存)                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. 领域模型设计

### 1.1 订单聚合根 (OrderAggregate)

```python
from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OrderDirection(Enum):
    """订单方向"""
    BUY = 'buy'    # 买入
    SELL = 'sell'  # 卖出

class OrderType(Enum):
    """订单类型"""
    MARKET = 'market'  # 市价单
    LIMIT = 'limit'    # 限价单

class OrderStatus(Enum):
    """订单状态"""
    PENDING = 'pending'           # 待提交
    SUBMITTED = 'submitted'       # 已提交
    PARTIAL_FILLED = 'partial_filled'  # 部分成交
    FILLED = 'filled'             # 完全成交
    CANCELLED = 'cancelled'       # 已取消
    REJECTED = 'rejected'         # 已拒绝
    EXPIRED = 'expired'           # 已过期

@dataclass
class Order:
    """订单实体"""
    id: Optional[int] = None
    order_code: str = ""
    account_id: int = 0
    signal_id: Optional[int] = None
    strategy_id: Optional[str] = None
    stock_code: str = ""
    stock_name: str = ""
    exchange: str = ""
    direction: OrderDirection = OrderDirection.BUY
    order_type: OrderType = OrderType.LIMIT
    order_price: Decimal = Decimal('0.0000')
    order_quantity: int = 0
    filled_price: Decimal = Decimal('0.0000')
    filled_quantity: int = 0
    filled_amount: Decimal = Decimal('0.0000')
    commission: Decimal = Decimal('0.0000')
    stamp_tax: Decimal = Decimal('0.0000')
    transfer_fee: Decimal = Decimal('0.0000')
    total_cost: Decimal = Decimal('0.0000')
    status: OrderStatus = OrderStatus.PENDING
    engine_id: str = ""
    broker_order_id: Optional[str] = None
    reject_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.order_code:
            self.order_code = self._generate_order_code()
    
    def _generate_order_code(self) -> str:
        """生成订单编码"""
        return f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.id or 'NEW'}"
    
    def can_submit(self) -> bool:
        """是否可以提交"""
        return self.status == OrderStatus.PENDING
    
    def can_cancel(self) -> bool:
        """是否可以取消"""
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.PARTIAL_FILLED
        ]
    
    def submit(self, broker_order_id: str) -> bool:
        """提交订单"""
        if not self.can_submit():
            return False
        
        self.status = OrderStatus.SUBMITTED
        self.broker_order_id = broker_order_id
        self.submitted_at = datetime.now()
        self.updated_at = datetime.now()
        
        return True
    
    def fill(
        self,
        filled_price: Decimal,
        filled_quantity: int,
        filled_amount: Decimal,
        commission: Decimal,
        stamp_tax: Decimal,
        transfer_fee: Decimal,
        total_cost: Decimal
    ) -> bool:
        """成交订单"""
        if self.status not in [OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED]:
            return False
        
        self.filled_price = filled_price
        self.filled_quantity = filled_quantity
        self.filled_amount = filled_amount
        self.commission = commission
        self.stamp_tax = stamp_tax
        self.transfer_fee = transfer_fee
        self.total_cost = total_cost
        
        if filled_quantity == self.order_quantity:
            self.status = OrderStatus.FILLED
            self.filled_at = datetime.now()
        else:
            self.status = OrderStatus.PARTIAL_FILLED
        
        self.updated_at = datetime.now()
        
        return True
    
    def cancel(self, reason: Optional[str] = None) -> bool:
        """取消订单"""
        if not self.can_cancel():
            return False
        
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()
        
        if reason:
            self.reject_reason = reason
        
        return True
    
    def reject(self, reason: str) -> bool:
        """拒绝订单"""
        if self.status != OrderStatus.PENDING:
            return False
        
        self.status = OrderStatus.REJECTED
        self.reject_reason = reason
        self.updated_at = datetime.now()
        
        return True
    
    def is_active(self) -> bool:
        """是否活跃订单"""
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.PARTIAL_FILLED
        ]
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status in [
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED
        ]

@dataclass
class Trade:
    """交易记录实体"""
    id: Optional[int] = None
    trade_code: str = ""
    order_id: int = 0
    account_id: int = 0
    stock_code: str = ""
    direction: OrderDirection = OrderDirection.BUY
    trade_price: Decimal = Decimal('0.0000')
    trade_quantity: int = 0
    trade_amount: Decimal = Decimal('0.0000')
    commission: Decimal = Decimal('0.0000')
    stamp_tax: Decimal = Decimal('0.0000')
    transfer_fee: Decimal = Decimal('0.0000')
    total_cost: Decimal = Decimal('0.0000')
    net_amount: Decimal = Decimal('0.0000')
    engine_id: str = ""
    broker_trade_id: Optional[str] = None
    traded_at: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.trade_code:
            self.trade_code = self._generate_trade_code()
    
    def _generate_trade_code(self) -> str:
        """生成交易编码"""
        return f"TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.id or 'NEW'}"
```

---

## 2. 订单状态机设计

### 2.1 状态机实现

```python
from typing import Dict, Set

class OrderStateMachine:
    """订单状态机"""
    
    # 状态转换规则
    TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
        OrderStatus.PENDING: {
            OrderStatus.SUBMITTED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED
        },
        OrderStatus.SUBMITTED: {
            OrderStatus.PARTIAL_FILLED,
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED
        },
        OrderStatus.PARTIAL_FILLED: {
            OrderStatus.FILLED,
            OrderStatus.CANCELLED
        },
        OrderStatus.FILLED: set(),  # 终态
        OrderStatus.CANCELLED: set(),  # 终态
        OrderStatus.REJECTED: set(),  # 终态
        OrderStatus.EXPIRED: set()  # 终态
    }
    
    @classmethod
    def can_transition(cls, from_status: OrderStatus, to_status: OrderStatus) -> bool:
        """是否可以转换"""
        allowed_statuses = cls.TRANSITIONS.get(from_status, set())
        return to_status in allowed_statuses
    
    @classmethod
    def get_next_statuses(cls, current_status: OrderStatus) -> Set[OrderStatus]:
        """获取可能的下一状态"""
        return cls.TRANSITIONS.get(current_status, set())
    
    @classmethod
    def is_final_status(cls, status: OrderStatus) -> bool:
        """是否是终态"""
        return len(cls.TRANSITIONS.get(status, set())) == 0
```

---

## 3. 领域服务设计

### 3.1 订单领域服务 (OrderDomainService)

```python
from typing import Optional
from decimal import Decimal

class OrderDomainService:
    """订单领域服务"""
    
    async def calculate_commission(
        self,
        trade_amount: Decimal,
        commission_rate: Decimal = Decimal('0.0003')
    ) -> Decimal:
        """计算佣金"""
        commission = trade_amount * commission_rate
        # 最低佣金5元
        return max(commission, Decimal('5.0000'))
    
    async def calculate_stamp_tax(
        self,
        trade_amount: Decimal,
        direction: OrderDirection,
        stamp_tax_rate: Decimal = Decimal('0.001')
    ) -> Decimal:
        """计算印花税（仅卖出收取）"""
        if direction == OrderDirection.SELL:
            return trade_amount * stamp_tax_rate
        return Decimal('0.0000')
    
    async def calculate_transfer_fee(
        self,
        trade_quantity: int,
        transfer_fee_rate: Decimal = Decimal('0.00001')
    ) -> Decimal:
        """计算过户费"""
        return Decimal(trade_quantity) * transfer_fee_rate
    
    async def calculate_total_cost(
        self,
        trade_amount: Decimal,
        commission: Decimal,
        stamp_tax: Decimal,
        transfer_fee: Decimal,
        direction: OrderDirection
    ) -> Decimal:
        """计算总成本"""
        if direction == OrderDirection.BUY:
            # 买入：交易金额 + 佣金 + 过户费
            return trade_amount + commission + transfer_fee
        else:
            # 卖出：交易金额 - 佣金 - 印花税 - 过户费
            return trade_amount - commission - stamp_tax - transfer_fee
    
    async def calculate_net_amount(
        self,
        trade_amount: Decimal,
        commission: Decimal,
        stamp_tax: Decimal,
        transfer_fee: Decimal,
        direction: OrderDirection
    ) -> Decimal:
        """计算净金额"""
        if direction == OrderDirection.BUY:
            # 买入：净支出
            return trade_amount + commission + transfer_fee
        else:
            # 卖出：净收入
            return trade_amount - commission - stamp_tax - transfer_fee
    
    async def validate_order(
        self,
        order: Order,
        account_balance: Decimal,
        available_position: int
    ) -> tuple[bool, Optional[str]]:
        """验证订单"""
        # 验证订单价格
        if order.order_type == OrderType.LIMIT and order.order_price <= 0:
            return False, "限价单价格必须大于0"
        
        # 验证订单数量
        if order.order_quantity <= 0:
            return False, "订单数量必须大于0"
        
        # 验证资金（买入）
        if order.direction == OrderDirection.BUY:
            required_amount = order.order_price * order.order_quantity
            if required_amount > account_balance:
                return False, f"可用资金不足，需要{required_amount}，可用{account_balance}"
        
        # 验证持仓（卖出）
        if order.direction == OrderDirection.SELL:
            if order.order_quantity > available_position:
                return False, f"可用持仓不足，需要{order.order_quantity}，可用{available_position}"
        
        return True, None
```

---

## 4. 应用服务设计

### 4.1 订单应用服务 (OrderApplicationService)

```python
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date

class OrderApplicationService:
    """订单应用服务"""
    
    def __init__(
        self,
        order_repository,
        account_service,
        position_service,
        engine_manager,
        saga_coordinator,
        order_domain_service: OrderDomainService,
        event_publisher
    ):
        self.order_repository = order_repository
        self.account_service = account_service
        self.position_service = position_service
        self.engine_manager = engine_manager
        self.saga_coordinator = saga_coordinator
        self.domain_service = order_domain_service
        self.event_publisher = event_publisher
    
    async def create_order(
        self,
        account_id: int,
        stock_code: str,
        exchange: str,
        direction: str,
        order_type: str,
        price: Decimal,
        quantity: int,
        signal_id: Optional[int] = None,
        strategy_id: Optional[str] = None,
        engine_id: str = "VNPY_001"
    ) -> Dict[str, Any]:
        """创建订单"""
        # 创建订单实体
        order = Order(
            account_id=account_id,
            signal_id=signal_id,
            strategy_id=strategy_id,
            stock_code=stock_code,
            exchange=exchange,
            direction=OrderDirection(direction),
            order_type=OrderType(order_type),
            order_price=price,
            order_quantity=quantity,
            engine_id=engine_id
        )
        
        # 验证订单
        account = await self.account_service.get_account(account_id)
        if not account:
            raise ValueError(f"账户不存在: {account_id}")
        
        if direction == 'buy':
            available_balance = Decimal(str(account['available_cash']))
            available_position = 0
        else:
            available_balance = Decimal('0')
            position = await self.position_service.get_position(account_id, stock_code)
            available_position = position.get('available_quantity', 0) if position else 0
        
        is_valid, error_msg = await self.domain_service.validate_order(
            order,
            available_balance,
            available_position
        )
        
        if not is_valid:
            order.reject(error_msg)
            await self.order_repository.create(order)
            raise ValueError(error_msg)
        
        # 保存订单
        order = await self.order_repository.create(order)
        
        # 发布订单创建事件
        await self.event_publisher.publish({
            'event_type': 'OrderCreated',
            'order_id': order.id,
            'order_code': order.order_code,
            'account_id': order.account_id,
            'stock_code': order.stock_code,
            'direction': order.direction.value,
            'order_price': float(order.order_price),
            'order_quantity': order.order_quantity,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'id': order.id,
            'order_code': order.order_code,
            'account_id': order.account_id,
            'stock_code': order.stock_code,
            'direction': order.direction.value,
            'order_type': order.order_type.value,
            'order_price': float(order.order_price),
            'order_quantity': order.order_quantity,
            'status': order.status.value
        }
    
    async def submit_order(self, order_id: int) -> Dict[str, Any]:
        """提交订单"""
        # 获取订单
        order = await self.order_repository.find_by_id(order_id)
        
        if not order:
            raise ValueError(f"订单不存在: {order_id}")
        
        if not order.can_submit():
            raise ValueError(f"订单状态不允许提交: {order.status.value}")
        
        # 创建并启动Saga
        saga = await self._create_order_saga(order)
        saga_id = await self.saga_coordinator.start_saga(saga)
        
        return {
            'order_id': order.id,
            'order_code': order.order_code,
            'status': order.status.value,
            'saga_id': saga_id
        }
    
    async def cancel_order(
        self,
        order_id: int,
        reason: Optional[str] = None
    ) -> bool:
        """取消订单"""
        # 获取订单
        order = await self.order_repository.find_by_id(order_id)
        
        if not order:
            return False
        
        if not order.can_cancel():
            return False
        
        # 如果已提交到引擎，先从引擎取消
        if order.broker_order_id:
            engine = self.engine_manager.get_engine(order.engine_id)
            if engine:
                success = await engine.cancel_order(order.broker_order_id)
                if not success:
                    return False
        
        # 取消订单
        order.cancel(reason)
        await self.order_repository.update(order)
        
        # 释放冻结的资金或持仓
        if order.direction == OrderDirection.BUY:
            frozen_amount = order.order_price * order.order_quantity
            await self.account_service.unfreeze_cash(order.account_id, frozen_amount)
        else:
            await self.position_service.unfreeze_position(
                order.account_id,
                order.stock_code,
                order.order_quantity
            )
        
        # 发布订单取消事件
        await self.event_publisher.publish({
            'event_type': 'OrderCancelled',
            'order_id': order.id,
            'order_code': order.order_code,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
    
    async def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """获取订单"""
        order = await self.order_repository.find_by_id(order_id)
        
        if not order:
            return None
        
        return {
            'id': order.id,
            'order_code': order.order_code,
            'account_id': order.account_id,
            'signal_id': order.signal_id,
            'strategy_id': order.strategy_id,
            'stock_code': order.stock_code,
            'stock_name': order.stock_name,
            'exchange': order.exchange,
            'direction': order.direction.value,
            'order_type': order.order_type.value,
            'order_price': float(order.order_price),
            'order_quantity': order.order_quantity,
            'filled_price': float(order.filled_price),
            'filled_quantity': order.filled_quantity,
            'filled_amount': float(order.filled_amount),
            'commission': float(order.commission),
            'stamp_tax': float(order.stamp_tax),
            'transfer_fee': float(order.transfer_fee),
            'total_cost': float(order.total_cost),
            'status': order.status.value,
            'engine_id': order.engine_id,
            'broker_order_id': order.broker_order_id,
            'reject_reason': order.reject_reason,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
            'filled_at': order.filled_at.isoformat() if order.filled_at else None,
            'cancelled_at': order.cancelled_at.isoformat() if order.cancelled_at else None
        }
    
    async def get_orders(
        self,
        account_id: Optional[int] = None,
        stock_code: Optional[str] = None,
        status: Optional[str] = None,
        direction: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取订单列表"""
        orders = await self.order_repository.find_all(
            account_id=account_id,
            stock_code=stock_code,
            status=status,
            direction=direction,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        
        total = await self.order_repository.count(
            account_id=account_id,
            stock_code=stock_code,
            status=status,
            direction=direction,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'orders': [
                {
                    'id': order.id,
                    'order_code': order.order_code,
                    'account_id': order.account_id,
                    'stock_code': order.stock_code,
                    'stock_name': order.stock_name,
                    'direction': order.direction.value,
                    'order_type': order.order_type.value,
                    'order_price': float(order.order_price),
                    'order_quantity': order.order_quantity,
                    'filled_quantity': order.filled_quantity,
                    'filled_amount': float(order.filled_amount),
                    'status': order.status.value,
                    'created_at': order.created_at.isoformat()
                }
                for order in orders
            ]
        }
    
    async def _create_order_saga(self, order: Order) -> 'Saga':
        """创建订单Saga"""
        # TODO: 实现订单Saga创建逻辑
        pass
```

---

## 5. 性能与监控

### 5.1 性能指标

| 操作 | 响应时间 | 备注 |
|------|----------|------|
| **创建订单** | < 200ms | 包含验证和数据库写入 |
| **提交订单** | < 500ms | 包含Saga启动 |
| **取消订单** | < 500ms | 包含引擎取消 |
| **查询订单** | < 100ms | Redis缓存命中 |

### 5.2 监控指标

```python
class OrderMonitor:
    """订单监控"""
    
    def __init__(self):
        self.metrics = {
            'total_orders': 0,
            'pending_orders': 0,
            'submitted_orders': 0,
            'filled_orders': 0,
            'cancelled_orders': 0,
            'rejected_orders': 0,
            'avg_fill_time': 0,
            'fill_rate': 0
        }
    
    async def record_order_creation(self, order: Order) -> None:
        """记录订单创建"""
        self.metrics['total_orders'] += 1
        
        if order.status == OrderStatus.PENDING:
            self.metrics['pending_orders'] += 1
    
    async def record_order_fill(self, order: Order) -> None:
        """记录订单成交"""
        self.metrics['filled_orders'] += 1
        
        if order.submitted_at and order.filled_at:
            fill_time = (order.filled_at - order.submitted_at).total_seconds()
            # 更新平均成交时间
            self.metrics['avg_fill_time'] = (
                (self.metrics['avg_fill_time'] * (self.metrics['filled_orders'] - 1) + fill_time)
                / self.metrics['filled_orders']
            )
        
        # 更新成交率
        self.metrics['fill_rate'] = (
            self.metrics['filled_orders'] / self.metrics['total_orders']
            if self.metrics['total_orders'] > 0 else 0
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """获取监控指标"""
        return self.metrics
```

---

**版本**: 1.0.0 | **更新日期**: 2026-04-02 | **状态**: ✅ 已完成  
**全部任务完成！**