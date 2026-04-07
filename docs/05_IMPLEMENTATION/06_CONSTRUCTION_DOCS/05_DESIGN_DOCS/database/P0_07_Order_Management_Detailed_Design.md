---
module_id: P0_07_ORDER_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 订单生命周期管理
  - 订单执行
  - 订单查询
layer: Layer 5.2 (组合优化)
---

# 订单管理详细设计

## 核心定位

负责订单全生命周期管理，包括订单创建、订单执行、订单查询、订单撤销等功能，支持多种订单类型和执行策略。

> **职责边界**:
> - ✅ 本文档负责：订单创建、订单执行、订单查询、订单撤销、订单状态管理
> - ❌ 本文档不负责：账户管理、资金划转、风险控制

## 设计目标

### 主要目标

1. **订单统一管理**: 支持多种订单类型(限价、市价、条件单等)
2. **执行策略支持**: 支持TWAP、VWAP、POV等多种执行策略
3. **状态机管理**: 严格的订单状态流转控制
4. **交易记录追踪**: 完整的交易记录和审计日志

### 质量目标

- 订单执行成功率: ≥99.9%
- 订单状态一致性: 100%
- 交易记录完整性: 100%

## 核心功能

### 订单管理特有功能

1. **订单创建服务**: 支持多种订单类型创建
2. **订单执行服务**: 智能路由、分批执行
3. **订单撤销服务**: 支持部分撤销和全部撤销
4. **订单查询服务**: 订单状态、成交明细查询
5. **订单状态机**: 状态流转控制和异常处理

### 领域模型

```python
class Order:
    """订单实体"""
    order_id: str            # 订单ID
    account_id: str          # 账户ID
    symbol: str              # 证券代码
    direction: OrderDirection # 买卖方向
    order_type: OrderType    # 订单类型
    quantity: Decimal        # 委托数量
    price: Decimal           # 委托价格
    filled_quantity: Decimal # 成交数量
    status: OrderStatus      # 订单状态
    created_at: datetime     # 创建时间
    updated_at: datetime     # 更新时间

class Trade:
    """交易记录实体"""
    trade_id: str            # 交易ID
    order_id: str            # 订单ID
    quantity: Decimal        # 成交数量
    price: Decimal           # 成交价格
    trade_time: datetime     # 成交时间
```

## 接口设计

### 订单应用服务接口

```python
class OrderApplicationService:
    """订单应用服务"""
    
    def create_order(self, request: CreateOrderRequest) -> Order:
        """创建订单"""
        pass
    
    def execute_order(self, order_id: str) -> List[Trade]:
        """执行订单"""
        pass
    
    def cancel_order(self, order_id: str, quantity: Decimal = None) -> None:
        """撤销订单"""
        pass
    
    def query_order(self, order_id: str) -> Order:
        """查询订单"""
        pass
    
    def query_trades(self, order_id: str) -> List[Trade]:
        """查询成交记录"""
        pass
```

## 状态机设计

### 订单状态流转

```
[新建] -> [待审核] -> [已审核] -> [待执行] -> [执行中] -> [已完成]
    |          |          |          |          |
    v          v          v          v          v
 [已撤销]   [已拒绝]   [已撤销]   [已撤销]   [部分成交]
```

## 数据库设计

### 订单表 (orders)

| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | VARCHAR(32) | 订单ID (主键) |
| account_id | VARCHAR(32) | 账户ID |
| symbol | VARCHAR(20) | 证券代码 |
| direction | VARCHAR(10) | 买卖方向 |
| order_type | VARCHAR(20) | 订单类型 |
| quantity | DECIMAL(20,4) | 委托数量 |
| price | DECIMAL(20,4) | 委托价格 |
| filled_quantity | DECIMAL(20,4) | 成交数量 |
| status | VARCHAR(20) | 订单状态 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 交易记录表 (trades)

| 字段 | 类型 | 说明 |
|------|------|------|
| trade_id | VARCHAR(32) | 交易ID (主键) |
| order_id | VARCHAR(32) | 订单ID |
| quantity | DECIMAL(20,4) | 成交数量 |
| price | DECIMAL(20,4) | 成交价格 |
| trade_time | TIMESTAMP | 成交时间 |

---

**最后更新**: 2026-04-07
