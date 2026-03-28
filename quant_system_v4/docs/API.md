# API.md - 接口规格

> **版本**：v4.0
> **日期**：2026-03-28
> **状态**：设计阶段

---

## 1. 模块间接口

### 1.1 核心接口约定

```python
# 所有模块返回统一格式
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

    @property
    def is_success(self) -> bool:
        return self.success
```

### 1.2 因子计算接口

```python
# factor_calculator.calculate()
Result(
    success=True,
    data=pd.DataFrame,  # columns=[date, code, factor_value]
    metadata={
        'factor_id': str,
        'calculation_time': float,  # 秒
        'row_count': int
    }
)
```

### 1.3 策略信号接口

```python
@dataclass
class Signal:
    signal_id: str
    strategy_id: str
    stock_code: str
    direction: str  # 'long' | 'short'
    strength: float  # 0.0 - 1.0
    entry_price: float
    timestamp: datetime
    metadata: dict
```

### 1.4 订单接口

```python
@dataclass
class Order:
    order_id: str
    signal_id: str
    stock_code: str
    direction: str  # 'buy' | 'sell'
    order_type: str  # 'market' | 'limit'
    price: float
    quantity: int
    status: str  # 'pending' | 'filled' | 'cancelled'
    timestamp: datetime
```

---

## 2. REST API (可选)

### 2.1 路由设计

```
/api/v1/
├── status/                    # 系统状态
│   └── GET /status           # 获取系统状态
│
├── factors/                   # 因子操作
│   ├── GET /factors          # 列出因子
│   ├── GET /factors/{id}    # 获取因子详情
│   └── POST /factors/calculate # 计算因子
│
├── strategies/                # 策略操作
│   ├── GET /strategies       # 列出策略
│   ├── GET /strategies/{id} # 获取策略详情
│   ├── POST /strategies/run  # 运行策略
│   └── POST /strategies/{id}/backtest # 回测策略
│
├── backtest/                  # 回测操作
│   ├── POST /backtest        # 创建回测
│   ├── GET /backtest/{id}    # 获取回测结果
│   └── GET /backtest/{id}/report # 获取报告
│
└── portfolio/                # 组合操作
    ├── GET /positions        # 获取持仓
    └── GET /account          # 获取账户信息
```

### 2.2 API响应格式

```json
{
  "success": true,
  "data": {},
  "error": null,
  "timestamp": "2026-03-28T12:00:00Z"
}
```

---

## 3. 事件接口

```python
# 模块间通过事件通信
class Event:
    event_type: str
    source: str
    data: Any
    timestamp: datetime

# 事件类型
EVENT_TYPES = {
    'SIGNAL_GENERATED': '策略信号生成',
    'ORDER_SUBMITTED': '订单提交',
    'ORDER_FILLED': '订单成交',
    'POSITION_OPENED': '持仓开仓',
    'POSITION_CLOSED': '持仓平仓',
    'RISK_ALERT': '风险告警',
    'SYSTEM_ERROR': '系统错误'
}
```

---

## 4. 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 数据采集失败 |
| 1002 | 数据清洗失败 |
| 2001 | 因子计算失败 |
| 2002 | 因子不存在 |
| 3001 | 策略加载失败 |
| 3002 | 策略信号无效 |
| 4001 | 风险校验未通过 |
| 4002 | 仓位超限 |
| 5001 | 订单提交失败 |
| 5002 | 订单撤销失败 |

---

## 5. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 初始版本，接口规格设计 |
