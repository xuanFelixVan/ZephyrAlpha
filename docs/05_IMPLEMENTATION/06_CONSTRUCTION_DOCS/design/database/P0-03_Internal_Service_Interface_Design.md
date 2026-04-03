---
module_id: INTERNAL_API_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席蓝图架构�?
standard_type: 专业量化机构内部服务接口标准
applicable_scope: 全系统服务接�?
compliance_level: 专业机构标准
parent_document: P0-01_Database_Design_Document.md
implementation_status: 进行�?
---

# 内部服务接口设计（专业量化机构标准）

> 清风量化系统 v5.0 - 专业量化机构标准内部服务接口设计
> **架构模式**: 微服务架�?+ DDD领域驱动设计
> **接口协议**: RESTful API + gRPC
> **设计原则**: 接口先行、契约优先、松耦合、高内聚

## 📋 接口设计概述

### 服务架构分层

```
┌─────────────────────────────────────────────────────────────�?
�?                   应用�?(Application Layer)                �?
�? ┌──────────────�? ┌──────────────�? ┌──────────────�?     �?
�? �? 交易应用服务 �? �? 策略应用服务 �? �? 风控应用服务 �?     �?
�? └──────────────�? └──────────────�? └──────────────�?     �?
└─────────────────────────────────────────────────────────────�?
                            �?API Gateway
┌─────────────────────────────────────────────────────────────�?
�?                   服务�?(Service Layer)                    �?
�? ┌──────────────�? ┌──────────────�? ┌──────────────�?     �?
�? �? 账户服务     �? �? 持仓服务     �? �? 订单服务     �?     �?
�? �?AccountService�? │PositionService�? �?OrderService �?     �?
�? └──────────────�? └──────────────�? └──────────────�?     �?
�? ┌──────────────�? ┌──────────────�? ┌──────────────�?     �?
�? �? 交易服务     �? �? 信号服务     �? �? 引擎服务     �?     �?
�? �?TradeService �? │SignalService �? │EngineService �?     �?
�? └──────────────�? └──────────────�? └──────────────�?     �?
└─────────────────────────────────────────────────────────────�?
                            �?Repository Interface
┌─────────────────────────────────────────────────────────────�?
�?                   领域�?(Domain Layer)                     �?
�? ┌──────────────�? ┌──────────────�? ┌──────────────�?     �?
�? �? 账户聚合     �? �? 持仓聚合     �? �? 订单聚合     �?     �?
�? │AccountAggregate�?│PositionAggregate�?│OrderAggregate�?   �?
�? └──────────────�? └──────────────�? └──────────────�?     �?
�? ┌──────────────�? ┌──────────────�? ┌──────────────�?     �?
�? �? 交易聚合     �? �? 信号聚合     �? �? Saga聚合     �?     �?
�? │TradeAggregate �? │SignalAggregate�? │SagaAggregate �?     �?
�? └──────────────�? └──────────────�? └──────────────�?     �?
└─────────────────────────────────────────────────────────────�?
                            �?Repository Implementation
┌─────────────────────────────────────────────────────────────�?
�?                   基础设施�?(Infrastructure Layer)          �?
�? ┌──────────────�? ┌──────────────�? ┌──────────────�?     �?
�? �?PostgreSQL   �? �?   Redis     �? �?ClickHouse   �?     �?
�? �? (主数据库)   �? �? (实时缓存)  �? �?(时序数据)   �?     �?
�? └──────────────�? └──────────────�? └──────────────�?     �?
└─────────────────────────────────────────────────────────────�?
```

---

## 1. 账户服务接口 (AccountService)

### 1.1 服务概述

**服务名称**: AccountService  
**服务职责**: 账户管理、资金管理、账户快�? 
**依赖服务**: PositionService, OrderService  
**数据访问**: AccountRepository

### 1.2 接口定义

#### 1.2.1 创建账户

**接口路径**: `POST /api/v1/accounts`

**请求参数**:
```json
{
  "account_name": "默认模拟账户",
  "account_type": "simulation",
  "initial_capital": 1000000.0000,
  "broker": "华泰证券"
}
```

**响应结果**:
```json
{
  "code": 200,
  "message": "账户创建成功",
  "data": {
    "id": 1,
    "account_code": "ACC_20260402_001",
    "account_name": "默认模拟账户",
    "account_type": "simulation",
    "broker": "华泰证券",
    "initial_capital": 1000000.0000,
    "current_capital": 1000000.0000,
    "available_cash": 1000000.0000,
    "frozen_cash": 0.0000,
    "total_assets": 1000000.0000,
    "total_pnl": 0.0000,
    "max_drawdown": 0.000000,
    "status": "active",
    "created_at": "2026-04-02T10:00:00Z",
    "updated_at": "2026-04-02T10:00:00Z"
  }
}
```

**业务规则**:
1. 账户编码自动生成：ACC_YYYYMMDD_XXX
2. 初始资金必须 > 0
3. 实盘账户必须填写券商名称

---

#### 1.2.2 查询账户

**接口路径**: `GET /api/v1/accounts/{account_id}`

**请求参数**:
- `account_id`: 账户ID（路径参数）

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 1,
    "account_code": "ACC_20260402_001",
    "account_name": "默认模拟账户",
    "account_type": "simulation",
    "broker": "华泰证券",
    "initial_capital": 1000000.0000,
    "current_capital": 950000.0000,
    "available_cash": 750000.0000,
    "frozen_cash": 200000.0000,
    "total_assets": 1200000.0000,
    "total_pnl": 200000.0000,
    "max_drawdown": 0.050000,
    "status": "active",
    "created_at": "2026-04-02T10:00:00Z",
    "updated_at": "2026-04-02T15:30:00Z",
    "positions": [
      {
        "stock_code": "600000.SH",
        "stock_name": "浦发银行",
        "quantity": 10000,
        "market_value": 128000.0000
      }
    ]
  }
}
```

---

#### 1.2.3 查询账户列表

**接口路径**: `GET /api/v1/accounts`

**请求参数**:
- `account_type`: 账户类型（可选）
- `status`: 账户状态（可选）
- `page`: 页码（默�?�?
- `page_size`: 每页数量（默�?0�?

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "accounts": [
      {
        "id": 1,
        "account_code": "ACC_20260402_001",
        "account_name": "默认模拟账户",
        "account_type": "simulation",
        "total_assets": 1200000.0000,
        "total_pnl": 200000.0000,
        "status": "active"
      }
    ]
  }
}
```

---

#### 1.2.4 更新账户状�?

**接口路径**: `PUT /api/v1/accounts/{account_id}/status`

**请求参数**:
```json
{
  "status": "frozen",
  "reason": "风控触发"
}
```

**响应结果**:
```json
{
  "code": 200,
  "message": "状态更新成�?,
  "data": {
    "id": 1,
    "status": "frozen",
    "updated_at": "2026-04-02T16:00:00Z"
  }
}
```

**业务规则**:
1. 状态转换：active �?frozen �?closed
2. closed状态不可�?
3. 冻结账户时需要记录原�?

---

#### 1.2.5 查询账户快照

**接口路径**: `GET /api/v1/accounts/{account_id}/snapshots`

**请求参数**:
- `account_id`: 账户ID（路径参数）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）
- `page`: 页码（默�?�?
- `page_size`: 每页数量（默�?0�?

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 90,
    "page": 1,
    "page_size": 30,
    "snapshots": [
      {
        "snapshot_date": "2026-04-02",
        "total_assets": 1200000.0000,
        "available_cash": 750000.0000,
        "total_market_value": 450000.0000,
        "daily_pnl": 10000.0000,
        "daily_pnl_pct": 0.008400,
        "cumulative_pnl": 200000.0000,
        "cumulative_pnl_pct": 0.200000,
        "max_drawdown": 0.050000,
        "sharpe_ratio": 1.500000,
        "win_rate": 0.650000
      }
    ]
  }
}
```

---

### 1.3 Repository接口

#### 1.3.1 AccountRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from decimal import Decimal

class AccountRepository(ABC):
    """账户仓储接口"""
    
    @abstractmethod
    async def create(self, account: Account) -> Account:
        """创建账户"""
        pass
    
    @abstractmethod
    async def find_by_id(self, account_id: int) -> Optional[Account]:
        """根据ID查询账户"""
        pass
    
    @abstractmethod
    async def find_by_code(self, account_code: str) -> Optional[Account]:
        """根据编码查询账户"""
        pass
    
    @abstractmethod
    async def find_all(
        self,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Account]:
        """查询账户列表"""
        pass
    
    @abstractmethod
    async def update(self, account: Account) -> Account:
        """更新账户"""
        pass
    
    @abstractmethod
    async def update_status(
        self,
        account_id: int,
        status: str,
        reason: Optional[str] = None
    ) -> bool:
        """更新账户状�?""
        pass
    
    @abstractmethod
    async def update_capital(
        self,
        account_id: int,
        current_capital: Decimal,
        available_cash: Decimal,
        frozen_cash: Decimal,
        total_assets: Decimal
    ) -> bool:
        """更新账户资金"""
        pass
    
    @abstractmethod
    async def create_snapshot(self, snapshot: AccountSnapshot) -> AccountSnapshot:
        """创建账户快照"""
        pass
    
    @abstractmethod
    async def find_snapshots(
        self,
        account_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 30
    ) -> List[AccountSnapshot]:
        """查询账户快照"""
        pass
```

---

## 2. 持仓服务接口 (PositionService)

### 2.1 服务概述

**服务名称**: PositionService  
**服务职责**: 持仓管理、持仓查询、持仓历�? 
**依赖服务**: AccountService, TradeService  
**数据访问**: PositionRepository

### 2.2 接口定义

#### 2.2.1 查询持仓

**接口路径**: `GET /api/v1/accounts/{account_id}/positions`

**请求参数**:
- `account_id`: 账户ID（路径参数）
- `stock_code`: 股票代码（可选）

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total_market_value": 450000.0000,
    "positions": [
      {
        "id": 1,
        "stock_code": "600000.SH",
        "stock_name": "浦发银行",
        "exchange": "SH",
        "quantity": 10000,
        "available_quantity": 8000,
        "frozen_quantity": 2000,
        "avg_cost": 10.5000,
        "current_price": 12.8000,
        "market_value": 128000.0000,
        "unrealized_pnl": 23000.0000,
        "unrealized_pnl_pct": 0.219048,
        "realized_pnl": 5000.0000,
        "position_pct": 0.106667,
        "first_buy_date": "2026-01-15",
        "last_trade_date": "2026-04-02"
      }
    ]
  }
}
```

---

#### 2.2.2 查询持仓历史

**接口路径**: `GET /api/v1/positions/{position_id}/history`

**请求参数**:
- `position_id`: 持仓ID（路径参数）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）
- `change_type`: 变更类型（可选）
- `page`: 页码（默�?�?
- `page_size`: 每页数量（默�?0�?

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 15,
    "page": 1,
    "page_size": 50,
    "history": [
      {
        "id": 1,
        "position_id": 1,
        "stock_code": "600000.SH",
        "change_type": "buy",
        "quantity_before": 5000,
        "quantity_after": 10000,
        "quantity_change": 5000,
        "price": 11.2000,
        "amount": 56000.0000,
        "trade_id": 12345,
        "created_at": "2026-04-02T10:30:00Z"
      }
    ]
  }
}
```

---

### 2.3 Repository接口

#### 2.3.1 PositionRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from decimal import Decimal

class PositionRepository(ABC):
    """持仓仓储接口"""
    
    @abstractmethod
    async def create(self, position: Position) -> Position:
        """创建持仓"""
        pass
    
    @abstractmethod
    async def find_by_id(self, position_id: int) -> Optional[Position]:
        """根据ID查询持仓"""
        pass
    
    @abstractmethod
    async def find_by_account_and_stock(
        self,
        account_id: int,
        stock_code: str
    ) -> Optional[Position]:
        """根据账户和股票查询持�?""
        pass
    
    @abstractmethod
    async def find_by_account(
        self,
        account_id: int,
        stock_code: Optional[str] = None
    ) -> List[Position]:
        """查询账户持仓"""
        pass
    
    @abstractmethod
    async def update(self, position: Position) -> Position:
        """更新持仓"""
        pass
    
    @abstractmethod
    async def update_quantity(
        self,
        position_id: int,
        quantity: int,
        available_quantity: int,
        frozen_quantity: int,
        avg_cost: Decimal
    ) -> bool:
        """更新持仓数量"""
        pass
    
    @abstractmethod
    async def update_price(
        self,
        position_id: int,
        current_price: Decimal,
        market_value: Decimal,
        unrealized_pnl: Decimal,
        unrealized_pnl_pct: Decimal
    ) -> bool:
        """更新持仓价格"""
        pass
    
    @abstractmethod
    async def create_history(self, history: PositionHistory) -> PositionHistory:
        """创建持仓历史"""
        pass
    
    @abstractmethod
    async def find_history(
        self,
        position_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        change_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> List[PositionHistory]:
        """查询持仓历史"""
        pass
```

---

## 3. 订单服务接口 (OrderService)

### 3.1 服务概述

**服务名称**: OrderService  
**服务职责**: 订单管理、订单执行、订单查�? 
**依赖服务**: AccountService, PositionService, EngineService  
**数据访问**: OrderRepository

### 3.2 接口定义

#### 3.2.1 创建订单

**接口路径**: `POST /api/v1/orders`

**请求参数**:
```json
{
  "account_id": 1,
  "signal_id": 100,
  "strategy_id": "STRAT_001",
  "stock_code": "600000.SH",
  "exchange": "SH",
  "direction": "buy",
  "order_type": "limit",
  "order_price": 12.5000,
  "order_quantity": 10000,
  "engine_id": "VNPY_001"
}
```

**响应结果**:
```json
{
  "code": 200,
  "message": "订单创建成功",
  "data": {
    "id": 1,
    "order_code": "ORD_20260402_001",
    "account_id": 1,
    "signal_id": 100,
    "strategy_id": "STRAT_001",
    "stock_code": "600000.SH",
    "stock_name": "浦发银行",
    "exchange": "SH",
    "direction": "buy",
    "order_type": "limit",
    "order_price": 12.5000,
    "order_quantity": 10000,
    "filled_quantity": 0,
    "filled_amount": 0.0000,
    "status": "pending",
    "engine_id": "VNPY_001",
    "created_at": "2026-04-02T10:00:00Z",
    "updated_at": "2026-04-02T10:00:00Z"
  }
}
```

**业务规则**:
1. 订单编码自动生成：ORD_YYYYMMDD_XXX
2. 买入订单：检查可用资金是否充�?
3. 卖出订单：检查可用持仓是否充�?
4. 风控检查：调用RiskService进行风控检�?

---

#### 3.2.2 提交订单

**接口路径**: `POST /api/v1/orders/{order_id}/submit`

**请求参数**:
- `order_id`: 订单ID（路径参数）

**响应结果**:
```json
{
  "code": 200,
  "message": "订单提交成功",
  "data": {
    "id": 1,
    "order_code": "ORD_20260402_001",
    "status": "submitted",
    "broker_order_id": "123456789",
    "engine_id": "VNPY_001",
    "submitted_at": "2026-04-02T10:01:00Z"
  }
}
```

**业务规则**:
1. 只有pending状态的订单可以提交
2. 提交前进行风控检�?
3. 提交后冻结资金或持仓
4. 调用EngineService执行订单

---

#### 3.2.3 取消订单

**接口路径**: `POST /api/v1/orders/{order_id}/cancel`

**请求参数**:
- `order_id`: 订单ID（路径参数）

**响应结果**:
```json
{
  "code": 200,
  "message": "订单取消成功",
  "data": {
    "id": 1,
    "order_code": "ORD_20260402_001",
    "status": "cancelled",
    "cancelled_at": "2026-04-02T10:05:00Z"
  }
}
```

**业务规则**:
1. 只有pending或submitted状态的订单可以取消
2. 取消后释放冻结的资金或持�?
3. 调用EngineService取消订单

---

#### 3.2.4 查询订单

**接口路径**: `GET /api/v1/orders/{order_id}`

**请求参数**:
- `order_id`: 订单ID（路径参数）

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 1,
    "order_code": "ORD_20260402_001",
    "account_id": 1,
    "signal_id": 100,
    "strategy_id": "STRAT_001",
    "stock_code": "600000.SH",
    "stock_name": "浦发银行",
    "exchange": "SH",
    "direction": "buy",
    "order_type": "limit",
    "order_price": 12.5000,
    "order_quantity": 10000,
    "filled_price": 12.4800,
    "filled_quantity": 10000,
    "filled_amount": 124800.0000,
    "commission": 62.4000,
    "stamp_tax": 0.0000,
    "transfer_fee": 12.4800,
    "total_cost": 124874.8800,
    "status": "filled",
    "engine_id": "VNPY_001",
    "broker_order_id": "123456789",
    "created_at": "2026-04-02T10:00:00Z",
    "updated_at": "2026-04-02T10:05:00Z",
    "filled_at": "2026-04-02T10:05:00Z"
  }
}
```

---

#### 3.2.5 查询订单列表

**接口路径**: `GET /api/v1/orders`

**请求参数**:
- `account_id`: 账户ID（可选）
- `stock_code`: 股票代码（可选）
- `status`: 订单状态（可选）
- `direction`: 交易方向（可选）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）
- `page`: 页码（默�?�?
- `page_size`: 每页数量（默�?0�?

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "orders": [
      {
        "id": 1,
        "order_code": "ORD_20260402_001",
        "account_id": 1,
        "stock_code": "600000.SH",
        "stock_name": "浦发银行",
        "direction": "buy",
        "order_type": "limit",
        "order_price": 12.5000,
        "order_quantity": 10000,
        "filled_quantity": 10000,
        "filled_amount": 124800.0000,
        "status": "filled",
        "created_at": "2026-04-02T10:00:00Z"
      }
    ]
  }
}
```

---

### 3.3 Repository接口

#### 3.3.1 OrderRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class OrderRepository(ABC):
    """订单仓储接口"""
    
    @abstractmethod
    async def create(self, order: Order) -> Order:
        """创建订单"""
        pass
    
    @abstractmethod
    async def find_by_id(self, order_id: int) -> Optional[Order]:
        """根据ID查询订单"""
        pass
    
    @abstractmethod
    async def find_by_code(self, order_code: str) -> Optional[Order]:
        """根据编码查询订单"""
        pass
    
    @abstractmethod
    async def find_all(
        self,
        account_id: Optional[int] = None,
        stock_code: Optional[str] = None,
        status: Optional[str] = None,
        direction: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Order]:
        """查询订单列表"""
        pass
    
    @abstractmethod
    async def update(self, order: Order) -> Order:
        """更新订单"""
        pass
    
    @abstractmethod
    async def update_status(
        self,
        order_id: int,
        status: str,
        reject_reason: Optional[str] = None
    ) -> bool:
        """更新订单状�?""
        pass
    
    @abstractmethod
    async def update_fill(
        self,
        order_id: int,
        filled_price: Decimal,
        filled_quantity: int,
        filled_amount: Decimal,
        commission: Decimal,
        stamp_tax: Decimal,
        transfer_fee: Decimal,
        total_cost: Decimal
    ) -> bool:
        """更新订单成交信息"""
        pass
    
    @abstractmethod
    async def find_active_orders(
        self,
        account_id: int,
        stock_code: Optional[str] = None
    ) -> List[Order]:
        """查询活跃订单"""
        pass
```

---

## 4. 交易服务接口 (TradeService)

### 4.1 服务概述

**服务名称**: TradeService  
**服务职责**: 交易记录管理、交易查询、交易统�? 
**依赖服务**: OrderService, PositionService  
**数据访问**: TradeRepository

### 4.2 接口定义

#### 4.2.1 创建交易记录

**接口路径**: `POST /api/v1/trades`

**请求参数**:
```json
{
  "order_id": 1,
  "account_id": 1,
  "stock_code": "600000.SH",
  "direction": "buy",
  "trade_price": 12.4800,
  "trade_quantity": 10000,
  "trade_amount": 124800.0000,
  "commission": 62.4000,
  "stamp_tax": 0.0000,
  "transfer_fee": 12.4800,
  "total_cost": 124874.8800,
  "net_amount": 124874.8800,
  "engine_id": "VNPY_001",
  "broker_trade_id": "987654321",
  "traded_at": "2026-04-02T10:05:00Z"
}
```

**响应结果**:
```json
{
  "code": 200,
  "message": "交易记录创建成功",
  "data": {
    "id": 1,
    "trade_code": "TRD_20260402_001",
    "order_id": 1,
    "account_id": 1,
    "stock_code": "600000.SH",
    "direction": "buy",
    "trade_price": 12.4800,
    "trade_quantity": 10000,
    "trade_amount": 124800.0000,
    "commission": 62.4000,
    "stamp_tax": 0.0000,
    "transfer_fee": 12.4800,
    "total_cost": 124874.8800,
    "net_amount": 124874.8800,
    "engine_id": "VNPY_001",
    "broker_trade_id": "987654321",
    "traded_at": "2026-04-02T10:05:00Z",
    "created_at": "2026-04-02T10:05:00Z"
  }
}
```

---

#### 4.2.2 查询交易记录

**接口路径**: `GET /api/v1/trades/{trade_id}`

**请求参数**:
- `trade_id`: 交易ID（路径参数）

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 1,
    "trade_code": "TRD_20260402_001",
    "order_id": 1,
    "account_id": 1,
    "stock_code": "600000.SH",
    "direction": "buy",
    "trade_price": 12.4800,
    "trade_quantity": 10000,
    "trade_amount": 124800.0000,
    "commission": 62.4000,
    "stamp_tax": 0.0000,
    "transfer_fee": 12.4800,
    "total_cost": 124874.8800,
    "net_amount": 124874.8800,
    "engine_id": "VNPY_001",
    "broker_trade_id": "987654321",
    "traded_at": "2026-04-02T10:05:00Z",
    "created_at": "2026-04-02T10:05:00Z"
  }
}
```

---

#### 4.2.3 查询交易记录列表

**接口路径**: `GET /api/v1/trades`

**请求参数**:
- `account_id`: 账户ID（可选）
- `stock_code`: 股票代码（可选）
- `direction`: 交易方向（可选）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）
- `page`: 页码（默�?�?
- `page_size`: 每页数量（默�?0�?

**响应结果**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "trades": [
      {
        "id": 1,
        "trade_code": "TRD_20260402_001",
        "order_id": 1,
        "account_id": 1,
        "stock_code": "600000.SH",
        "direction": "buy",
        "trade_price": 12.4800,
        "trade_quantity": 10000,
        "trade_amount": 124800.0000,
        "total_cost": 124874.8800,
        "traded_at": "2026-04-02T10:05:00Z"
      }
    ]
  }
}
```

---

### 4.3 Repository接口

#### 4.3.1 TradeRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class TradeRepository(ABC):
    """交易记录仓储接口"""
    
    @abstractmethod
    async def create(self, trade: Trade) -> Trade:
        """创建交易记录"""
        pass
    
    @abstractmethod
    async def find_by_id(self, trade_id: int) -> Optional[Trade]:
        """根据ID查询交易记录"""
        pass
    
    @abstractmethod
    async def find_by_code(self, trade_code: str) -> Optional[Trade]:
        """根据编码查询交易记录"""
        pass
    
    @abstractmethod
    async def find_all(
        self,
        account_id: Optional[int] = None,
        stock_code: Optional[str] = None,
        direction: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Trade]:
        """查询交易记录列表"""
        pass
    
    @abstractmethod
    async def find_by_order(self, order_id: int) -> List[Trade]:
        """根据订单查询交易记录"""
        pass
    
    @abstractmethod
    async def calculate_statistics(
        self,
        account_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """计算交易统计"""
        pass
```

---

## 5. 接口通用规范

### 5.1 响应格式

**成功响应**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 业务数据
  }
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "参数错误",
  "error": {
    "field": "account_id",
    "reason": "账户ID不存�?
  }
}
```

### 5.2 错误码定�?

| 错误�?| 说明 | 示例 |
|--------|------|------|
| **200** | 成功 | 操作成功 |
| **400** | 参数错误 | 参数缺失或格式错�?|
| **401** | 未授�?| 未登录或token过期 |
| **403** | 无权�?| 无操作权�?|
| **404** | 资源不存�?| 账户不存�?|
| **409** | 业务冲突 | 账户已存�?|
| **500** | 服务器错�?| 系统内部错误 |

### 5.3 分页规范

**请求参数**:
- `page`: 页码（从1开始）
- `page_size`: 每页数量（默�?0，最�?00�?

**响应格式**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": []
  }
}
```

### 5.4 时间格式

- **日期**: `YYYY-MM-DD` (�? 2026-04-02)
- **时间�?*: `YYYY-MM-DDTHH:MM:SSZ` (�? 2026-04-02T10:00:00Z)
- **时区**: UTC

### 5.5 金额格式

- **精度**: 4位小数（DECIMAL(20,4)�?
- **单位**: 元（人民币）
- **示例**: 1000000.0000

---

## 6. 性能要求

### 6.1 响应时间

| 接口类型 | 响应时间要求 | 备注 |
|----------|--------------|------|
| **查询接口** | < 200ms | 简单查�?|
| **列表接口** | < 500ms | 分页查询 |
| **创建接口** | < 300ms | 数据写入 |
| **更新接口** | < 300ms | 数据更新 |
| **统计接口** | < 1000ms | 复杂计算 |

### 6.2 并发要求

- **并发用户�?*: 100
- **QPS**: 1000
- **TPS**: 500

### 6.3 缓存策略

| 数据类型 | 缓存时间 | 缓存策略 |
|----------|----------|----------|
| **账户信息** | 5分钟 | Redis缓存 |
| **持仓信息** | 1分钟 | Redis缓存 |
| **订单信息** | 不缓�?| 实时查询 |
| **交易记录** | 不缓�?| 实时查询 |

---

## 7. 安全要求

### 7.1 认证授权

- **认证方式**: JWT Token
- **Token有效�?*: 2小时
- **刷新Token**: 7�?

### 7.2 数据加密

- **传输加密**: HTTPS
- **敏感数据**: AES加密存储
- **密码**: BCrypt哈希

### 7.3 访问控制

- **RBAC**: 基于角色的访问控�?
- **权限粒度**: 接口级别
- **审计日志**: 记录所有操�?

---

**版本**: 1.0.0 | **更新日期**: 2026-04-02 | **状�?*: �?已完�? 
**下一�?*: P0-4 第三方接口集成设�