---
module_id: P0_07_ORDER_MANAGEMENT_DETAILED_DESIGN
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - ﻟ۱ﮒﻝ۰ﻝﻟﺁ۵ﻝﭨﻟﺝﻟ۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﺅﺙ文档
---

﻿---
module_id: ORDER_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 系统实施与部署管理与优化维护
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻟ؟۱ﮒﻝ؟۰ﻝﮔﮒ
applicable_scope: ﻟ؟۱ﮒﮔﮒ۰ﮔ۷۰ﮒ
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﻟ؟۱ﮒﻝ؟۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﺅﺙ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﻟ؟۱ﮒﻝ؟۰ﻝﻟ؟ﺝﻟ؟۰
> **ﻟ؟ﺝﻟ؟۰ﮔ۷۰ﮒﺙ**: DDDﻠ۱ﮒﻠ۸ﺎﮒ۷ﻟ؟ﺝﻟ؟۰ + ﻝﭘﮔﮔﭦﮔ۷۰ﮒﺙ + Sagaﻛﭦﮒ۰
> **ﮔﺕﮒﺟﻟﻟﺑ۲**: ﻟ؟۱ﮒﻝﮒﺛﮒ۷ﮔﻝ؟۰ﻝﻙﻟ؟۱ﮒﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﮔ۴ﻟﺁ?

## ﻭ ﮔ۷۰ﮒﮔ۵ﻟﺟﺍ

### ﻟ؟۱ﮒﻝ؟۰ﻝﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﭦﻝ۷ﮒﺎ?(Application Layer)                ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         OrderApplicationService                      ﻗ? ﻗ?
ﻗ? ﻗ? - ﮒﮒﭨﭦﻟ؟۱ﮒﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗ? - ﮔ۶ﻟ۰ﻟ؟۱ﮒﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗ? - ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻠ۱ﮒﮒﺎ?(Domain Layer)                     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         OrderAggregate (ﻟ؟۱ﮒﻟﮒﮔ?                  ﻗ? ﻗ?
ﻗ? ﻗ? - Order (ﻟ؟۱ﮒﮒ؟ﻛﺛ)                                   ﻗ? ﻗ?
ﻗ? ﻗ? - Trade (ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﮒ؟ﻛﺛ)                               ﻗ? ﻗ?
ﻗ? ﻗ? - OrderDomainService (ﻠ۱ﮒﮔﮒ۰)                      ﻗ? ﻗ?
ﻗ? ﻗ? - OrderStateMachine (ﻝﭘﮔﮔﭦ)                         ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﮒﺎ?(Infrastructure Layer)          ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         OrderRepository (ﻟ؟۱ﮒﻛﭨﮒ۷)                   ﻗ? ﻗ?
ﻗ? ﻗ? - PostgreSQL (ﻛﺕﭨﮔﺍﮔ؟ﮒﭦ)                              ﻗ? ﻗ?
ﻗ? ﻗ? - Redis (ﮒ؟ﮔﭘﻝﺙﮒ)                                   ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 1. ﻠ۱ﮒﮔ۷۰ﮒﻟ؟ﺝﻟ؟۰

### 1.1 ﻟ؟۱ﮒﻟﮒﮔ?(OrderAggregate)

```python
from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OrderDirection(Enum):
    """ﻟ؟۱ﮒﮔﺗﮒ"""
    BUY = 'buy'    # ﻛﺗﺍﮒ۴
    SELL = 'sell'  # ﮒﮒﭦ

class OrderType(Enum):
    """ﻟ؟۱ﮒﻝﺎﭨﮒ"""
    MARKET = 'market'  # ﮒﺕﻛﭨﺓﮒ?
    LIMIT = 'limit'    # ﻠﻛﭨﺓﮒ?

class OrderStatus(Enum):
    """ﻟ؟۱ﮒﻝﭘﮔ?""
    PENDING = 'pending'           # ﮒﺝﮔﻛﭦ?
    SUBMITTED = 'submitted'       # ﮒﺓﺎﮔﻛﭦ?
    PARTIAL_FILLED = 'partial_filled'  # ﻠ۷ﮒﮔﻛﭦ۳
    FILLED = 'filled'             # ﮒ؟ﮒ۷ﮔﻛﭦ۳
    CANCELLED = 'cancelled'       # ﮒﺓﺎﮒﮔﭘ?
    REJECTED = 'rejected'         # ﮒﺓﺎﮔﻝﭨ?
    EXPIRED = 'expired'           # ﮒﺓﺎﻟﺟﮔ?

@dataclass
class Order:
    """ﻟ؟۱ﮒﮒ؟ﻛﺛ"""
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
        """ﮒﮒ۶ﮒﮒﮒ۳ﻝ"""
        if not self.order_code:
            self.order_code = self._generate_order_code()
    
    def _generate_order_code(self) -> str:
"""ﻝﮔﻟ؟۱ﮒﻝﺙﻝ"""
        return f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.id or 'NEW'}"
    
    def can_submit(self) -> bool:
        """ﮔﺁﮒ۵ﮒﺁﻛﭨ۴ﮔﻛﭦ۳"""
        return self.status == OrderStatus.PENDING
    
    def can_cancel(self) -> bool:
        """ﮔﺁﮒ۵ﮒﺁﻛﭨ۴ﮒﮔﭘ"""
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.PARTIAL_FILLED
        ]
    
    def submit(self, broker_order_id: str) -> bool:
        """ﮔﻛﭦ۳ﻟ؟۱ﮒ"""
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
        """ﮔﻛﭦ۳ﻟ؟۱ﮒ"""
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
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        if not self.can_cancel():
            return False
        
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()
        
        if reason:
            self.reject_reason = reason
        
        return True
    
    def reject(self, reason: str) -> bool:
        """ﮔﻝﭨﻟ؟۱ﮒ"""
        if self.status != OrderStatus.PENDING:
            return False
        
        self.status = OrderStatus.REJECTED
        self.reject_reason = reason
        self.updated_at = datetime.now()
        
        return True
    
    def is_active(self) -> bool:
        """ﮔﺁﮒ۵ﮔﺑﭨﻟﺓﻟ؟۱ﮒ"""
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.PARTIAL_FILLED
        ]
    
    def is_completed(self) -> bool:
        """ﮔﺁﮒ۵ﮒﺓﺎﮒ؟ﮔ?""
        return self.status in [
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED
        ]

@dataclass
class Trade:
    """ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﮒ؟ﻛﺛ"""
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
        """ﮒﮒ۶ﮒﮒﮒ۳ﻝ"""
        if not self.trade_code:
            self.trade_code = self._generate_trade_code()
    
    def _generate_trade_code(self) -> str:
"""ﻝﮔﻛﭦ۳ﮔﻝﺙﻝ"""
        return f"TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.id or 'NEW'}"
```

---

## 2. ﻟ؟۱ﮒﻝﭘﮔﮔﭦﻟ؟ﺝﻟ؟۰

### 2.1 ﻝﭘﮔﮔﭦﮒ؟ﻝﺍ

```python
from typing import Dict, Set

class OrderStateMachine:
    """ﻟ؟۱ﮒﻝﭘﮔﮔﭦ"""
    
    # ﻝﭘﮔﻟﺛ؛ﮔ۱ﻟ۶ﮒ?
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
        OrderStatus.FILLED: set(),  # ﻝﭨﮔ?
        OrderStatus.CANCELLED: set(),  # ﻝﭨﮔ?
        OrderStatus.REJECTED: set(),  # ﻝﭨﮔ?
        OrderStatus.EXPIRED: set()  # ﻝﭨﮔ?
    }
    
    @classmethod
    def can_transition(cls, from_status: OrderStatus, to_status: OrderStatus) -> bool:
        """ﮔﺁﮒ۵ﮒﺁﻛﭨ۴ﻟﺛ؛ﮔ۱"""
        allowed_statuses = cls.TRANSITIONS.get(from_status, set())
        return to_status in allowed_statuses
    
    @classmethod
    def get_next_statuses(cls, current_status: OrderStatus) -> Set[OrderStatus]:
        """ﻟﺓﮒﮒﺁﻟﺛﻝﻛﺕﻛﺕﻝﭘﮔ?""
        return cls.TRANSITIONS.get(current_status, set())
    
    @classmethod
    def is_final_status(cls, status: OrderStatus) -> bool:
        """ﮔﺁﮒ۵ﮔﺁﻝﭨﮔ?""
        return len(cls.TRANSITIONS.get(status, set())) == 0
```

---

## 3. ﻠ۱ﮒﮔﮒ۰ﻟ؟ﺝﻟ؟۰

### 3.1 ﻟ؟۱ﮒﻠ۱ﮒﮔﮒ۰ (OrderDomainService)

```python
from typing import Optional
from decimal import Decimal

class OrderDomainService:
    """ﻟ؟۱ﮒﻠ۱ﮒﮔﮒ۰"""
    
    async def calculate_commission(
        self,
        trade_amount: Decimal,
        commission_rate: Decimal = Decimal('0.0003')
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻛﺛ۲ﻠ"""
        commission = trade_amount * commission_rate
        # ﮔﻛﺛﻛﺛ۲ﻠ?ﮒ?
        return max(commission, Decimal('5.0000'))
    
    async def calculate_stamp_tax(
        self,
        trade_amount: Decimal,
        direction: OrderDirection,
        stamp_tax_rate: Decimal = Decimal('0.001')
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮒﺍﻟﺎﻝ۷ﺅﺙﻛﭨﮒﮒﭦﮔﭘﮒﺅﺙ"""
        if direction == OrderDirection.SELL:
            return trade_amount * stamp_tax_rate
        return Decimal('0.0000')
    
    async def calculate_transfer_fee(
        self,
        trade_quantity: int,
        transfer_fee_rate: Decimal = Decimal('0.00001')
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻟﺟﮔﺓﻟﺑ?""
        return Decimal(trade_quantity) * transfer_fee_rate
    
    async def calculate_total_cost(
        self,
        trade_amount: Decimal,
        commission: Decimal,
        stamp_tax: Decimal,
        transfer_fee: Decimal,
        direction: OrderDirection
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔﭨﮔﮔ?""
        if direction == OrderDirection.BUY:
            # ﻛﺗﺍﮒ۴ﺅﺙﻛﭦ۳ﮔﻠﻠ۱?+ ﻛﺛ۲ﻠ + ﻟﺟﮔﺓﻟﺑ?
            return trade_amount + commission + transfer_fee
        else:
            # ﮒﮒﭦﺅﺙﻛﭦ۳ﮔﻠﻠ۱?- ﻛﺛ۲ﻠ - ﮒﺍﻟﺎﻝ۷?- ﻟﺟﮔﺓﻟﺑ?
            return trade_amount - commission - stamp_tax - transfer_fee
    
    async def calculate_net_amount(
        self,
        trade_amount: Decimal,
        commission: Decimal,
        stamp_tax: Decimal,
        transfer_fee: Decimal,
        direction: OrderDirection
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮒﻠﻠ۱"""
        if direction == OrderDirection.BUY:
            # ﻛﺗﺍﮒ۴ﺅﺙﮒﮔﺁﮒﭦ
            return trade_amount + commission + transfer_fee
        else:
            # ﮒﮒﭦﺅﺙﮒﮔﭘﮒ۴
            return trade_amount - commission - stamp_tax - transfer_fee
    
    async def validate_order(
        self,
        order: Order,
        account_balance: Decimal,
        available_position: int
    ) -> tuple[bool, Optional[str]]:
        """ﻠ۹ﻟﺁﻟ؟۱ﮒ"""
# ﻠ۹ﻟﺁﻟ؟۱ﮒﻛﭨﺓﮔﺙ
        if order.order_type == OrderType.LIMIT and order.order_price <= 0:
return False, "ﻠﻛﭨﺓﮒﻛﭨﺓﮔﺙﮒﺟﻠ۰ﭨﮒ۳۶ﻛﭦ?"
        
        # ﻠ۹ﻟﺁﻟ؟۱ﮒﮔﺍﻠ
        if order.order_quantity <= 0:
            return False, "ﻟ؟۱ﮒﮔﺍﻠﮒﺟﻠ۰ﭨﮒ۳۶ﻛﭦ0"
        
        # ﻠ۹ﻟﺁﻟﭖﻠﺅﺙﻛﺗﺍﮒ۴ﺅﺙ
        if order.direction == OrderDirection.BUY:
            required_amount = order.order_price * order.order_quantity
            if required_amount > account_balance:
                return False, f"ﮒﺁﻝ۷ﻟﭖﻠﻛﺕﻟﭘﺏﺅﺙﻠﻟ۵{required_amount}ﺅﺙﮒﺁﻝ۷{account_balance}"
        
        # ﻠ۹ﻟﺁﮔﻛﭨﺅﺙﮒﮒﭦﺅﺙ
        if order.direction == OrderDirection.SELL:
            if order.order_quantity > available_position:
                return False, f"ﮒﺁﻝ۷ﮔﻛﭨﻛﺕﻟﭘﺏﺅﺙﻠﻟ۵{order.order_quantity}ﺅﺙﮒﺁﻝ۷{available_position}"
        
        return True, None
```

---

## 4. ﮒﭦﻝ۷ﮔﮒ۰ﻟ؟ﺝﻟ؟۰

### 4.1 ﻟ؟۱ﮒﮒﭦﻝ۷ﮔﮒ۰ (OrderApplicationService)

```python
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date

class OrderApplicationService:
    """ﻟ؟۱ﮒﮒﭦﻝ۷ﮔﮒ۰"""
    
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        # ﮒﮒﭨﭦﻟ؟۱ﮒﮒ؟ﻛﺛ
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
        
        # ﻠ۹ﻟﺁﻟ؟۱ﮒ
        account = await self.account_service.get_account(account_id)
        if not account:
raise ValueError(f"ﻟﺑ۵ﮔﺓﻛﺕﮒﮒ? {account_id}")
        
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
        
# ﻛﺟﮒﻟ؟۱ﮒ
        order = await self.order_repository.create(order)
        
        # ﮒﮒﺕﻟ؟۱ﮒﮒﮒﭨﭦﻛﭦﻛﭨﭘ
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
        """ﮔﻛﭦ۳ﻟ؟۱ﮒ"""
        # ﻟﺓﮒﻟ؟۱ﮒ
        order = await self.order_repository.find_by_id(order_id)
        
        if not order:
raise ValueError(f"ﻟ؟۱ﮒﻛﺕﮒﮒ? {order_id}")
        
        if not order.can_submit():
            raise ValueError(f"ﻟ؟۱ﮒﻝﭘﮔﻛﺕﮒﻟ؟ﺕﮔﻛﭦ۳: {order.status.value}")
        
        # ﮒﮒﭨﭦﮒﺗﭘﮒﺁﮒ۷Saga
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
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        # ﻟﺓﮒﻟ؟۱ﮒ
        order = await self.order_repository.find_by_id(order_id)
        
        if not order:
            return False
        
        if not order.can_cancel():
            return False
        
        # ﮒ۵ﮔﮒﺓﺎﮔﻛﭦ۳ﮒﺍﮒﺙﮔﺅﺙﮒﻛﭨﮒﺙﮔﮒﮔﭘ?
        if order.broker_order_id:
            engine = self.engine_manager.get_engine(order.engine_id)
            if engine:
                success = await engine.cancel_order(order.broker_order_id)
                if not success:
                    return False
        
        # ﮒﮔﭘﻟ؟۱ﮒ
        order.cancel(reason)
        await self.order_repository.update(order)
        
        # ﻠﮔﺝﮒﭨﻝﭨﻝﻟﭖﻠﮔﮔﻛﭨ
        if order.direction == OrderDirection.BUY:
            frozen_amount = order.order_price * order.order_quantity
            await self.account_service.unfreeze_cash(order.account_id, frozen_amount)
        else:
            await self.position_service.unfreeze_position(
                order.account_id,
                order.stock_code,
                order.order_quantity
            )
        
        # ﮒﮒﺕﻟ؟۱ﮒﮒﮔﭘﻛﭦﻛﭨﭘ
        await self.event_publisher.publish({
            'event_type': 'OrderCancelled',
            'order_id': order.id,
            'order_code': order.order_code,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
    
    async def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """ﻟﺓﮒﻟ؟۱ﮒ"""
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
        """ﻟﺓﮒﻟ؟۱ﮒﮒﻟ۰۷"""
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒSaga"""
        # TODO: ﮒ؟ﻝﺍﻟ؟۱ﮒSagaﮒﮒﭨﭦﻠﭨﻟﺝ
        pass
```

---

## 5. ﮔ۶ﻟﺛﻛﺕﻝﮔ?

### 5.1 ﮔ۶ﻟﺛﮔﮔ

| ﮔﻛﺛ | ﮒﮒﭦﮔﭘﻠﺑ | ﮒ۳ﮔﺏ۷ |
|------|----------|------|
| **ﮒﮒﭨﭦﻟ؟۱ﮒ** | < 200ms | ﮒﮒ،ﻠ۹ﻟﺁﮒﮔﺍﮔ؟ﮒﭦﮒﮒ۴ |
| **ﮔﻛﭦ۳ﻟ؟۱ﮒ** | < 500ms | ﮒﮒ،Sagaﮒﺁﮒ۷ |
| **ﮒﮔﭘﻟ؟۱ﮒ** | < 500ms | ﮒﮒ،ﮒﺙﮔﮒﮔﭘ |
| **ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ** | < 100ms | Redisﻝﺙﮒﮒﺛﻛﺕ |

### 5.2 ﻝﮔ۶ﮔﮔ

```python
class OrderMonitor:
    """ﻟ؟۱ﮒﻝﮔ۶"""
    
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
        """ﻟ؟ﺍﮒﺛﻟ؟۱ﮒﮒﮒﭨﭦ"""
        self.metrics['total_orders'] += 1
        
        if order.status == OrderStatus.PENDING:
            self.metrics['pending_orders'] += 1
    
    async def record_order_fill(self, order: Order) -> None:
        """ﻟ؟ﺍﮒﺛﻟ؟۱ﮒﮔﻛﭦ۳"""
        self.metrics['filled_orders'] += 1
        
        if order.submitted_at and order.filled_at:
            fill_time = (order.filled_at - order.submitted_at).total_seconds()
            # ﮔﺑﮔﺍﮒﺗﺏﮒﮔﻛﭦ۳ﮔﭘﻠﺑ
            self.metrics['avg_fill_time'] = (
                (self.metrics['avg_fill_time'] * (self.metrics['filled_orders'] - 1) + fill_time)
                / self.metrics['filled_orders']
            )
        
        # ﮔﺑﮔﺍﮔﻛﭦ۳ﻝ?
        self.metrics['fill_rate'] = (
            self.metrics['filled_orders'] / self.metrics['total_orders']
            if self.metrics['total_orders'] > 0 else 0
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
"""ﻟﺓﮒﻝﮔ۶ﮔﮔ"""
        return self.metrics
```

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 
**ﮒ۷ﻠ۷ﻛﭨﭨﮒ۰ﮒ؟ﮔﺅﺙ?*
