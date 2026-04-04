---
module_id: EXECUTION_ORDER_ALGO_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-04
owner: 首席文档架构�?
standard_type: 专业量化机构文档
applicable_scope: 订单生成算法
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 订单生成算法

> TWAP、VWAP、冲击成本模�?

**版本**: v1.0
**更新**: 2026-04-04
**层级**: 执行�?(Layer 4)
**索引**: 04_EXECUTION/01_ORDER_EXECUTION/ORDER_GENERATION_ALGORITHMS.md
**说明**: 本文档从 03_TRADING_TACTICS/07_ORDER_GENERATION/ 移动至此，因其属于执行层内容

---

## 1. 订单生成概述

订单生成是AI执行的核心模块：

| 角色 | 职责 |
|------|------|
| **�?* | 最终交易授�?|
| **AI** | 生成最优订单、执行算�?|

---

## 2. 订单类型

### 2.1 市价�?

```python
class MarketOrder:
    """市价�?""
    symbol: str
    quantity: int
    direction: str  # 'buy' / 'sell'
```

### 2.2 限价�?

```python
class LimitOrder:
    """限价�?""
    symbol: str
    quantity: int
    price: float
    direction: str
```

### 2.3 条件�?

```python
class ConditionalOrder:
    """条件�?""
    symbol: str
    quantity: int
    condition_type: str  # 'stop_loss' / 'take_profit' / 'trailing'
    trigger_price: float
```

---

## 3. 执行算法

### 3.1 TWAP (时间加权平均价格)

```python
class TWAPExecutor:
    """TWAP执行算法"""

    def __init__(self, total_quantity: int, duration_minutes: int = 60):
        self.total_quantity = total_quantity
        self.duration = duration_minutes
        self.slice_interval = duration_minutes // 10  # 10个切�?

    def generate_slices(self) -> List[OrderSlice]:
        """生成订单切片"""
        slice_size = self.total_quantity // 10
        slices = []
        for i in range(10):
            slices.append(OrderSlice(
                quantity=slice_size,
                start_time=self._get_slice_start(i),
                end_time=self._get_slice_end(i)
            ))
        return slices

    def _get_slice_start(self, slice_idx: int) -> datetime:
        """获取切片开始时�?""
        return self.start_time + timedelta(minutes=slice_idx * self.slice_interval)

    def _get_slice_end(self, slice_idx: int) -> datetime:
        """获取切片结束时间"""
        return self.start_time + timedelta(minutes=(slice_idx + 1) * self.slice_interval)
```

### 3.2 VWAP (成交量加权平均价�?

```python
class VWAPExecutor:
    """VWAP执行算法"""

    def __init__(self, total_quantity: int, expected_participation: float = 0.1):
        self.total_quantity = total_quantity
        self.expected_participation = expected_participation  # 预期占比市场成交�?

    def calculate_target_quantity(self, bar_volume: int, current_time: datetime) -> int:
        """根据VWAP基准计算目标数量"""
        # 使用历史VWAP曲线作为基准
        vwap_profile = self._get_vwap_profile(current_time)
        target_qty = int(bar_volume * self.expected_participation * vwap_profile)
        return min(target_qty, self.remaining_quantity)
```

### 3.3 冲击成本模型

```python
class ImpactCostModel:
    """冲击成本模型"""

    def __init__(self, market_impact_coeff: float = 0.1):
        self.coeff = market_impact_coeff

    def estimate_impact(self, order_quantity: int, daily_volume: int,
                       volatility: float) -> float:
        """估算冲击成本"""
        participation_rate = order_quantity / daily_volume
        # Almgren-Chriss模型
        impact = self.coeff * volatility * participation_rate ** 0.6
        return impact

    def optimize_order_schedule(self, total_quantity: int,
                               daily_volume: int,
                               volatility: float) -> List[int]:
        """优化订单调度"""
        # 使用冲击成本模型找到最优调�?
        n_slices = 10
        base_qty = total_quantity // n_slices
        schedule = []

        for i in range(n_slices):
            # 早期激进、后期保�?
            participation = min(0.2, daily_volume * 0.1 * (1 - i/n_slices))
            qty = min(base_qty, int(participation * daily_volume))
            schedule.append(qty)

        return schedule
```

### 3.4 大单拆分

```python
class OrderSlicer:
    """大单拆分逻辑"""

    def __init__(self, threshold_pct: float = 0.01):
        self.threshold_pct = threshold_pct  # 超过市场成交1%认为是大�?

    def should_slice(self, quantity: int, daily_volume: int) -> bool:
        """判断是否需要拆�?""
        return (quantity / daily_volume) > self.threshold_pct

    def slice_order(self, order: Order, n_slices: int = 10) -> List[Order]:
        """拆分订单"""
        if not self.should_slice(order.quantity, order.daily_volume):
            return [order]

        slice_size = order.quantity // n_slices
        slices = []
        for i in range(n_slices):
            slices.append(Order(
                symbol=order.symbol,
                quantity=slice_size if i < n_slices - 1 else order.quantity - slice_size * (n_slices - 1),
                direction=order.direction,
                order_type='limit',  # 使用限价单减少冲�?
                price=self._get_slice_price(order, i, n_slices)
            ))
        return slices
```

---

## 4. 订单优化�?

```python
class OrderOptimizer:
    """订单优化�?""

    def __init__(self, executor: str = 'twap'):
        self.executor = executor

    def optimize(self, order: Order, market_data: MarketData) -> OrderPlan:
        """生成最优订单执行计�?""
        if self.executor == 'twap':
            exec_algo = TWAPExecutor(order.quantity)
        elif self.executor == 'vwap':
            exec_algo = VWAPExecutor(order.quantity)
        else:
            exec_algo = ImpactCostOptimizer(order.quantity)

        return OrderPlan(
            order=order,
            schedule=exec_algo.generate_slices(),
            estimated_cost=exec_algo.estimate_cost(market_data),
            execution_window=exec_algo.get_window()
        )
```

---

## 5. 层级关系

```
Layer 4 (执行�?
    �?上游
Layer 3 (策略�? �?仓位计算
Layer 5 (监控�? �?执行监控
    �?下游
```

---

## 索引

- 父目�? [03_TRADING_TACTICS/README.md](../README.md)
- 上游: [06_POSITION_MANAGEMENT/README.md](../06_POSITION_MANAGEMENT/README.md)
- 下游: 
