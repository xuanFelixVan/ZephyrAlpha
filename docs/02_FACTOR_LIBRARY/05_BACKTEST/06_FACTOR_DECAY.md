---
module_id: FACTOR_DECAY_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---


# 因子衰减分析

> 因子有效性监控与衰减预警

---

## 1. 因子衰减分析

### 1.1 衰减曲线计算

```python
import pandas as pd
import numpy as np
from scipy import stats

def calculate_decay_curve(
    factor: pd.Series,
    returns: pd.Series,
    max_holding_periods: int = 20
) -> pd.DataFrame:
    """计算因子在不同持有期的IC衰减

    参数�?
        factor: 因子�?
        returns: 收益率序�?
        max_holding_periods: 最大持有期（天数）

    返回�?
        包含各期IC值的DataFrame
    """
    decay_data = []

    for period in range(1, max_holding_periods + 1):
        # 计算前向收益
        forward_returns = returns.shift(-period)

        # 计算截面相关�?
        valid_idx = factor.notna() & forward_returns.notna()
        if valid_idx.sum() > 30:
            ic = factor[valid_idx].corr(forward_returns[valid_idx])
            decay_data.append({
                'holding_period': period,
                'ic': ic,
                'sample_size': valid_idx.sum()
            })

    return pd.DataFrame(decay_data)
```

### 1.2 衰减指标

```python
def decay_metrics(decay_df: pd.DataFrame) -> dict:
    """计算衰减指标"""
    ic_values = decay_df['ic'].values

    return {
        'ic_day1': ic_values[0] if len(ic_values) > 0 else 0,
        'ic_day5': ic_values[4] if len(ic_values) > 4 else 0,
        'ic_day10': ic_values[9] if len(ic_values) > 9 else 0,
        'decay_rate_5d': (ic_values[0] - ic_values[4]) / ic_values[0] if ic_values[0] != 0 else 0,
        'decay_rate_10d': (ic_values[0] - ic_values[9]) / ic_values[0] if ic_values[0] != 0 else 0,
        'half_life': find_half_life(ic_values)
    }

def find_half_life(ic_values: np.ndarray) -> int:
    """找到IC衰减到一半的持有�?""
    initial_ic = ic_values[0]
    if initial_ic == 0:
        return 0

    for i, ic in enumerate(ic_values):
        if abs(ic) < abs(initial_ic) / 2:
            return i + 1
    return len(ic_values)
```

---

## 2. 因子换手率分�?

```python
def turnover_analysis(
    factor_quantiles: pd.DataFrame,
    period: int = 1
) -> pd.DataFrame:
    """计算因子组合换手�?

    参数�?
        factor_quantiles: 因子分位数（每期为一行）
        period: 持有周期（天�?

    返回�?
        换手率数据框
    """
    turnovers = []

    for i in range(period, len(factor_quantiles)):
        prev_quantile = factor_quantiles.iloc[i - period]
        curr_quantile = factor_quantiles.iloc[i]

        # 计算持仓变化
        diff = (curr_quantile != prev_quantile).sum()
        turnover = diff / len(prev_quantile)

        turnovers.append({
            'period': i,
            'turnover': turnover,
            'new_positions': diff
        })

    return pd.DataFrame(turnovers)
```

---

## 3. 因子有效性监控面�?

```python
class FactorMonitor:
    """因子有效性监�?""

    def __init__(self, factor_id: str):
        self.factor_id = factor_id
        self.history = []

    def daily_update(
        self,
        ic_value: float,
        returns: pd.Series,
        factor_values: pd.Series
    ):
        """每日更新因子状�?""
        self.history.append({
            'date': pd.Timestamp.now(),
            'ic': ic_value,
            'ic_ir': ic_value / returns.std() if returns.std() > 0 else 0,
            'turnover': self._calc_turnover(factor_values)
        })

    def check_alert(self, threshold_icir: float = 0.5) -> dict:
        """检查是否需要告�?""
        recent = pd.DataFrame(self.history[-20:])  # 最�?0�?

        if len(recent) < 10:
            return {'alert': False}

        avg_icir = recent['ic_ir'].mean()

        return {
            'alert': avg_icir < threshold_icir,
            'avg_icir_20d': avg_icir,
            'threshold': threshold_icir,
            'recommendation': 'reduce_weight' if avg_icir < threshold_icir else 'maintain'
        }

    def _calc_turnover(self, factor_values: pd.Series) -> float:
        """计算换手�?""
        if len(self.history) == 0:
            return 0.0

        prev_factor = pd.Series(self.history[-1].get('factor_values', []))
        if len(prev_factor) == len(factor_values):
            return (factor_values != prev_factor).mean()
        return 0.0
```

---

## 4. IC 统计指标

| 指标 | 计算方法 | 健康阈�?|
|------|---------|---------|
| IC均�?| $mean(IC)$ | > 0.02 |
| IC标准�?| $std(IC)$ | 越小越好 |
| ICIR | $IC_{mean} / IC_{std}$ | > 0.5 |
| IC胜率 | $IC > 0$ 的比�?| > 55% |
| t统计�?| $IC_{mean} / (IC_{std} / \sqrt{N})$ | > 2.0 |

---

## 5. 告警规则

```yaml
factor_alerts:
  icir_threshold:
    warning: 0.5
    critical: 0.3

  decay_rate_threshold:
    warning: 0.3  # 5日衰减超�?0%
    critical: 0.5  # 5日衰减超�?0%

  turnover_threshold:
    warning: 0.5  # 日换手率超过50%
    critical: 0.8
```

---

**版本**: 1.0 | **更新**: 2026-03-28

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
