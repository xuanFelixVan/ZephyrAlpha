---
module_id: DATA_STAT_TOOLS_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-06
owner: 首席文档架构师
standard_type: 分析工具文档
applicable_scope: 统计分析工具
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 进行中
---

# 统计分析工具

## 文档职责说明

**本文档职责**: 统计分析工具定义
- 提供描述性统计分析能力
- 支持分布分析和时间序列分析
- 实现相关性分析方法

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 相关性分析 | [CORRELATION_ANALYSIS.md](./CORRELATION_ANALYSIS.md) | 扩展层 | 深度相关性分析 |
| 数据源索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: 基础统计分析工具定义
- ❌ 本文档不负责: 高级相关性分析（由 CORRELATION_ANALYSIS.md 负责）

> **模块编号**: M-STAT-001 (Statistical Analysis Tools)
> **版本**: 1.0
> **创建日期**: 2026-03-28
> **优先级**: P1

---

## 1. 系统概述

### 1.1 目标
为量化研究提供基础的统计分析能力，支持描述性统计、分布分析、相关性分析等常用统计方法。

### 1.2 功能范围

| 类别 | 功能 | 说明 |
|------|------|------|
| **描述性统计** | 均值、中位数、众数、方差、标准差 | 数据基本特征 |
| **分布分析** | 偏度、峰度、分位数、分布拟合 | 数据分布形态 |
| **时间序列分析** | 收益率、波动率、滚动统计 | 金融时序特征 |
| **相关性分析** | Pearson、Spearman、滚动相关 | 变量间关系 |

---

## 2. 描述性统计

### 2.1 基础统计量计算

```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

@dataclass
class DescriptiveStats:
    """描述性统计量"""
    count: int
    mean: float
    std: float
    min: float
    q25: float
    q50: float
    q75: float
    max: float
    skewness: float
    kurtosis: float

    def to_dict(self) -> Dict:
        return {
            "count": self.count,
            "mean": self.mean,
            "std": self.std,
            "min": self.min,
            "q25": self.q25,
            "q50": self.q50,
            "q75": self.q75,
            "max": self.max,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis
        }

class DescriptiveStatistics:
    """描述性统计分析器"""

    @staticmethod
    def compute(series: pd.Series) -> DescriptiveStats:
        """
        计算描述性统计量

        参数:
            series: 输入数据

        返回:
            DescriptiveStats: 统计量对象
        """
        return DescriptiveStats(
            count=len(series),
            mean=series.mean(),
            std=series.std(),
            min=series.min(),
            q25=series.quantile(0.25),
            q50=series.quantile(0.50),
            q75=series.quantile(0.75),
            max=series.max(),
            skewness=series.skew(),
            kurtosis=series.kurt()
        )

    @classmethod
    def compute_dataframe(cls, df: pd.DataFrame,
                          columns: List[str] = None) -> pd.DataFrame:
        """
        计算DataFrame多个列的描述性统计

        返回:
            DataFrame: 行是统计量，列是变量
        """
        cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
        result = pd.DataFrame(index=[c for c in dir(DescriptiveStats) if not c.startswith('_')])

        for col in cols:
            stats = cls.compute(df[col])
            result[col] = [getattr(stats, c) for c in result.index]

        return result

    @staticmethod
    def summary(series: pd.Series) -> str:
        """生成简洁的统计摘要"""
        stats = DescriptiveStatistics.compute(series)
        return f"""
┌─────────────────────────────────┐
│      描述性统计摘要             │
├─────────────────────────────────┤
│ 样本数:    {stats.count:>15,.0f} │
│ 均值:      {stats.mean:>15.4f} │
│ 标准差:    {stats.std:>15.4f} │
│ 最小值:    {stats.min:>15.4f} │
│ 25%分位:   {stats.q25:>15.4f} │
│ 中位数:    {stats.q50:>15.4f} │
│ 75%分位:   {stats.q75:>15.4f} │
│ 最大值:    {stats.max:>15.4f} │
│ 偏度:      {stats.skewness:>15.4f} │
│ 峰度:      {stats.kurtosis:>15.4f} │
└─────────────────────────────────┘
"""
```

### 2.2 收益率统计

```python
class ReturnStatistics:
    """收益率统计分析"""

    @staticmethod
    def simple_return(prices: pd.Series) -> pd.Series:
        """
        计算简单收益率
        R = (P_t - P_{t-1}) / P_{t-1}
        """
        return prices.pct_change()

    @staticmethod
    def log_return(prices: pd.Series) -> pd.Series:
        """
        计算对数收益率
        r = ln(P_t / P_{t-1})
        """
        return np.log(prices / prices.shift(1))

    @staticmethod
    def annual_return(daily_return: pd.Series,
                      periods_per_year: int = 252) -> float:
        """
        年化收益率

        参数:
            daily_return: 日收益率序列
            periods_per_year: 年化周期数(股票默认252)
        """
        mean_daily = daily_return.mean()
        return (1 + mean_daily) ** periods_per_year - 1

    @staticmethod
    def annual_volatility(daily_return: pd.Series,
                          periods_per_year: int = 252) -> float:
        """
        年化波动率

        参数:
            daily_return: 日收益率序列
            periods_per_year: 年化周期数
        """
        return daily_return.std() * np.sqrt(periods_per_year)

    @staticmethod
    def sharpe_ratio(returns: pd.Series,
                     risk_free_rate: float = 0.0,
                     periods_per_year: int = 252) -> float:
        """
        夏普比率

        SR = (E[R_p] - R_f) / σ_p
        """
        excess_return = returns.mean() - risk_free_rate / periods_per_year
        return excess_return * np.sqrt(periods_per_year) / returns.std()

    @staticmethod
    def max_drawdown(prices: pd.Series) -> Tuple[float, str, str]:
        """
        最大回撤

        返回:
            (最大回撤值, 最高点日期, 最低点日期)
        """
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        max_dd = drawdown.min()
        max_dd_idx = drawdown.idxmin()

        # 找到最高点
        peak_idx = prices[:max_dd_idx].idxmax()

        return max_dd, str(peak_idx), str(max_dd_idx)
```

---

## 3. 分布分析

### 3.1 分位数分析

```python
class QuantileAnalysis:
    """分位数分析"""

    @staticmethod
    def compute_quantiles(series: pd.Series,
                         quantiles: List[float] = None) -> Dict:
        """
        计算分位数

        参数:
            series: 数据
            quantiles: 分位数列表，默认 [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
        """
        if quantiles is None:
            quantiles = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]

        return {q: series.quantile(q) for q in quantiles}

    @staticmethod
    def iqr_outliers(series: pd.Series,
                    factor: float = 1.5) -> Tuple[pd.Series, pd.Series]:
        """
        基于IQR的异常值检测

        参数:
            series: 数据
            factor: IQR倍数，默认1.5

        返回:
            (下界异常, 上界异常)
        """
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - factor * IQR
        upper = Q3 + factor * IQR

        return series < lower, series > upper

    @staticmethod
    def percentile_rank(series: pd.Series,
                      window: int = None) -> pd.Series:
        """
        计算百分位排名

        参数:
            series: 数据
            window: 滚动窗口，如不指定则全局计算
        """
        if window:
            return series.rolling(window).apply(
                lambda x: pd.Series(x).rank(pct=True).iloc[-1]
            )
        return series.rank(pct=True)
```

### 3.2 分布拟合

```python
from scipy import stats

class DistributionFitter:
    """分布拟合工具"""

    DISTRIBUTIONS = {
        'normal': stats.norm,
        't': stats.t,
        'laplace': stats.laplace,
        'cauchy': stats.cauchy
    }

    @classmethod
    def fit(cls, data: pd.Series, distribution: str = 'normal') -> Dict:
        """
        拟合分布

        参数:
            data: 数据
            distribution: 分布类型

        返回:
            拟合参数和统计量
        """
        dist = cls.DISTRIBUTIONS.get(distribution)
        if dist is None:
            raise ValueError(f"不支持的分布: {distribution}")

        params = dist.fit(data)
        ks_stat, ks_pvalue = stats.kstest(data, distribution, args=params)

        return {
            'distribution': distribution,
            'params': params,
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pvalue,
            'fit_good': ks_pvalue > 0.05
        }
```

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
