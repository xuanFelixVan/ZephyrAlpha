---
module_id: EXECUTION_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 交易成本分析 (TCA)

> 交易成本分析、执行算法与性能评估

---

## 1. 交易成本组成

| 成本类型 | 说明 | 典型�?|
|---------|------|--------|
| 佣金 | 券商收取 | 万三 (0.03%) |
| 印花�?| 卖出时收�?| 千一 (0.1%) |
| 过户�?| 沪市收取 | �?.1 |
| 冲击成本 | 大单对市场的影响 | 0.01%-0.5% |
| 价差成本 | 买卖价差 | 0.01%-0.1% |
| 机会成本 | 未成交损�?| 可变 |

---

## 2. TCA 计算

```python
import pandas as pd
import numpy as np

class TCACalculator:
    """交易成本分析�?""

    def __init__(self, commission_rate: float = 0.0003, stamp_tax: float = 0.001):
        self.commission_rate = commission_rate
        self.stamp_tax = stamp_tax

    def calculate_single_trade_cost(
        self,
        symbol: str,
        direction: str,
        quantity: int,
        execution_price: float,
        arrival_price: float
    ) -> dict:
        """计算单笔交易成本

        参数�?
            symbol: 股票代码
            direction: 'buy' or 'sell'
            quantity: 成交�?
            execution_price: 执行价格
            arrival_price: 到达价格（决策参考价�?

        返回�?
            成本分解
        """
        notional = quantity * execution_price

        # 佣金
        commission = notional * self.commission_rate

        # 印花税（仅卖出）
        tax = notional * self.stamp_tax if direction == 'sell' else 0

        # 冲击成本
        if direction == 'buy':
            market_impact = (execution_price - arrival_price) / arrival_price
        else:
            market_impact = (arrival_price - execution_price) / arrival_price

        impact_cost = abs(market_impact) * notional

        # 总成�?
        total_cost = commission + tax + impact_cost
        total_cost_bps = (total_cost / notional) * 10000

        return {
            'symbol': symbol,
            'direction': direction,
            'quantity': quantity,
            'execution_price': execution_price,
            'arrival_price': arrival_price,
            'notional': notional,
            'commission': commission,
            'commission_bps': commission / notional * 10000,
            'stamp_tax': tax,
            'stamp_tax_bps': tax / notional * 10000,
            'market_impact': abs(market_impact),
            'market_impact_bps': abs(market_impact) * 10000,
            'total_cost': total_cost,
            'total_cost_bps': total_cost_bps
        }

    def calculate_period_tca(
        self,
        trades: pd.DataFrame
    ) -> dict:
        """计算周期TCA报告

        参数�?
            trades: 交易记录DataFrame

        返回�?
            TCA统计
        """
        total_cost = trades['total_cost'].sum()
        total_notional = trades['notional'].sum()

        buy_trades = trades[trades['direction'] == 'buy']
        sell_trades = trades[trades['direction'] == 'sell']

        return {
            'period': f"{trades['date'].min()} to {trades['date'].max()}",
            'total_trades': len(trades),
            'total_notional': total_notional,
            'total_cost': total_cost,
            'avg_cost_bps': total_cost / total_notional * 10000,
            'buy_count': len(buy_trades),
            'sell_count': len(sell_trades),
            'avg_buy_cost_bps': buy_trades['total_cost_bps'].mean() if len(buy_trades) > 0 else 0,
            'avg_sell_cost_bps': sell_trades['total_cost_bps'].mean() if len(sell_trades) > 0 else 0,
            'implementation_shortfall': self._calc_implementation_shortfall(trades)
        }

    def _calc_implementation_shortfall(self, trades: pd.DataFrame) -> float:
        """计算实现缺口 (Implementation Shortfall)

        IS = (执行价格 - 决策价格) / 决策价格 * direction
        """
        signed_impact = []
        for _, trade in trades.iterrows():
            if trade['direction'] == 'buy':
                impact = (trade['execution_price'] - trade['arrival_price']) / trade['arrival_price']
            else:
                impact = (trade['arrival_price'] - trade['execution_price']) / trade['arrival_price']
            signed_impact.append(impact * trade['notional'])

        return sum(signed_impact)
```

---

## 3. VWAP 分析

```python
class VWAPAnalyzer:
    """VWAP 分析"""

    def calculate_vwap(self, trades: pd.DataFrame) -> float:
        """计算成交VWAP"""
        return (trades['price'] * trades['quantity']).sum() / trades['quantity'].sum()

    def compare_to_vwap(
        self,
        trades: pd.DataFrame,
        market_vwap: float
    ) -> dict:
        """与市场VWAP对比

        参数�?
            trades: 交易记录
            market_vwap: 市场VWAP

        返回�?
            对比结果
        """
        executed_vwap = self.calculate_vwap(trades)
        direction = trades['direction'].iloc[0]

        if direction == 'buy':
            vwap_difference = (executed_vwap - market_vwap) / market_vwap
        else:
            vwap_difference = (market_vwap - executed_vwap) / market_vwap

        return {
            'executed_vwap': executed_vwap,
            'market_vwap': market_vwap,
            'vwap_difference_bps': vwap_difference * 10000,
            'executed_vwap_better': vwap_difference < 0 if direction == 'buy' else vwap_difference > 0
        }
```

---

## 4. 执行算法分析

```python
class ExecutionAnalyzer:
    """执行算法效果分析"""

    def analyze_twap_execution(
        self,
        scheduled_slices: list,
        executed_trades: pd.DataFrame
    ) -> dict:
        """分析TWAP执行效果"""
        total_scheduled = sum(s['quantity'] for s in scheduled_slices)
        total_executed = executed_trades['quantity'].sum()
        execution_ratio = total_executed / total_scheduled if total_scheduled > 0 else 0

        # 时间执行偏差
        scheduled_times = [s['time'] for s in scheduled_slices]
        actual_times = executed_trades['exec_time'].tolist()

        return {
            'execution_ratio': execution_ratio,
            'completion_rate': execution_ratio * 100,
            'scheduled_slices': len(scheduled_slices),
            'executed_slices': len(executed_trades),
            'under_execution_reason': 'market_movement' if execution_ratio < 0.95 else None
        }

    def analyze_vwap_execution(
        self,
        trades: pd.DataFrame,
        expected_participation_rate: float
    ) -> dict:
        """分析VWAP执行效果"""
        executed_vwap = self.calculate_vwap(trades)
        total_volume = trades['quantity'].sum()
        avg_market_volume = trades['market_volume'].mean()

        actual_participation = total_volume / (avg_market_volume * len(trades))

        return {
            'executed_vwap': executed_vwap,
            'expected_participation': expected_participation_rate,
            'actual_participation': actual_participation,
            'participation_deviation': abs(actual_participation - expected_participation_rate),
            'is_under_traded': actual_participation < expected_participation_rate * 0.8
        }
```

---

## 5. TCA 报告模板

```yaml
tca_report:
  period: "2026-03-01 to 2026-03-28"
  summary:
    total_trades: 150
    total_notional: 50000000
    total_cost: 125000
    avg_cost_bps: 25.0
    implementation_shortfall: 0.03

  by_direction:
    buy:
      count: 80
      notional: 28000000
      avg_cost_bps: 22.5
    sell:
      count: 70
      notional: 22000000
      avg_cost_bps: 28.0

  by_strategy:
    S001_trend:
      count: 50
      avg_cost_bps: 20.0
    S002_mean_reversion:
      count: 60
      avg_cost_bps: 25.0

  benchmarks:
    market_vwap: "beat by 5 bps"
    arrival_price: "beat by 8 bps"
```

---

**版本**: 1.0 | **更新**: 2026-03-28
