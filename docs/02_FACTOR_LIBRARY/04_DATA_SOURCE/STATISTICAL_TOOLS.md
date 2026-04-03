---
module_id: FACTOR_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 统计分析工具

> **模块编号**: M-STAT-001 (Statistical Analysis Tools)
> **版本**: 1.0
> **创建日期**: 2026-03-28
> **优先�?*: P1

---

## 1. 系统概述

### 1.1 目标
为量化研究提供基础的统计分析能力，支持描述性统计、分布分析、相关性分析等常用统计方法�?

### 1.2 功能范围

| 类别 | 功能 | 说明 |
|------|------|------|
| **描述性统�?* | 均值、中位数、众数、方差、标准差 | 数据基本特征 |
| **分布分析** | 偏度、峰度、分位数、分布拟�?| 数据分布形�?|
| **时间序列分析** | 收益率、波动率、滚动统�?| 金融时序特�?|
| **相关性分�?* | Pearson、Spearman、滚动相�?| 变量间关�?|

---

## 2. 描述性统�?

### 2.1 基础统计量计�?

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
            DescriptiveStats: 统计量对�?
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
        计算DataFrame多个列的描述性统�?

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
┌─────────────────────────────────�?
�?      描述性统计摘�?           �?
├─────────────────────────────────�?
�? 样本�?    {stats.count:>15,.0f} �?
�? 均�?      {stats.mean:>15.4f} �?
�? 标准�?    {stats.std:>15.4f} �?
�? 最小�?    {stats.min:>15.4f} �?
�? 25%分位:   {stats.q25:>15.4f} �?
�? 中位�?    {stats.q50:>15.4f} �?
�? 75%分位:   {stats.q75:>15.4f} �?
�? 最大�?    {stats.max:>15.4f} �?
�? 偏度:      {stats.skewness:>15.4f} �?
�? 峰度:      {stats.kurtosis:>15.4f} �?
└─────────────────────────────────�?
"""
```

### 2.2 收益率统�?

```python
class ReturnStatistics:
    """收益率统计分�?""

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
        计算对数收益�?
        r = ln(P_t / P_{t-1})
        """
        return np.log(prices / prices.shift(1))

    @staticmethod
    def annual_return(daily_return: pd.Series,
                      periods_per_year: int = 252) -> float:
        """
        年化收益�?

        参数:
            daily_return: 日收益率序列
            periods_per_year: 年化周期�?(股票默认252)
        """
        mean_daily = daily_return.mean()
        return (1 + mean_daily) ** periods_per_year - 1

    @staticmethod
    def annual_volatility(daily_return: pd.Series,
                          periods_per_year: int = 252) -> float:
        """
        年化波动�?

        参数:
            daily_return: 日收益率序列
            periods_per_year: 年化周期�?
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
        最大回�?

        返回:
            (最大回撤�? 最高点日期, 最低点日期)
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

### 3.1 分位数分�?

```python
class QuantileAnalysis:
    """分位数分�?""

    @staticmethod
    def compute_quantiles(series: pd.Series,
                         quantiles: List[float] = None) -> Dict:
        """
        计算分位�?

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
        基于IQR的异常值检�?

        参数:
            series: 数据
            factor: IQR倍数，默�?.5

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
        计算百分位排�?

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
    def fit_normal(cls, series: pd.Series) -> Tuple[float, float]:
        """
        拟合正态分�?

        返回:
            (mu, sigma)
        """
        return stats.norm.fit(series)

    @classmethod
    def fit_t(cls, series: pd.Series) -> Tuple[float, float, float]:
        """
        拟合t分布

        返回:
            (df, loc, scale)
        """
        return stats.t.fit(series)

    @classmethod
    def normality_test(series: pd.Series) -> Dict:
        """
        正态性检�?(Jarque-Bera)

        返回:
            (JB统计�? p�? 是否正�?
        """
        jb_stat, p_value = stats.jarque_bera(series)
        return {
            "jb_statistic": jb_stat,
            "p_value": p_value,
            "is_normal": p_value > 0.05
        }

    @classmethod
    def ks_test(cls, series: pd.Series,
                distribution: str = 'normal') -> Dict:
        """
        Kolmogorov-Smirnov检�?

        返回:
            (KS统计�? p�? 是否服从指定分布)
        """
        if distribution == 'normal':
            mu, sigma = cls.fit_normal(series)
            dist = stats.norm(mu, sigma)
        elif distribution == 't':
            params = cls.fit_t(series)
            dist = stats.t(*params)

        ks_stat, p_value = stats.kstest(series, dist.cdf)

        return {
            "ks_statistic": ks_stat,
            "p_value": p_value,
            f"is_{distribution}": p_value > 0.05
        }
```

---

## 4. 时间序列分析

### 4.1 滚动统计

```python
class RollingStatistics:
    """滚动统计工具"""

    @staticmethod
    def rolling_mean(series: pd.Series,
                    window: int) -> pd.Series:
        """滚动均�?""
        return series.rolling(window).mean()

    @staticmethod
    def rolling_std(series: pd.Series,
                   window: int) -> pd.Series:
        """滚动标准�?""
        return series.rolling(window).std()

    @staticmethod
    def rolling_sharpe(returns: pd.Series,
                      window: int = 252,
                      risk_free_rate: float = 0.0) -> pd.Series:
        """
        滚动夏普比率

        参数:
            returns: 收益率序�?
            window: 窗口�?
            risk_free_rate: 年化无风险利�?
        """
        excess = returns - risk_free_rate / 252
        roll_mean = excess.rolling(window).mean()
        roll_std = excess.rolling(window).std()
        return roll_mean / roll_std * np.sqrt(252)

    @staticmethod
    def rolling_max(series: pd.Series,
                   window: int) -> pd.Series:
        """滚动最大�?""
        return series.rolling(window).max()

    @staticmethod
    def rolling_min(series: pd.Series,
                   window: int) -> pd.Series:
        """滚动最小�?""
        return series.rolling(window).min()

    @staticmethod
    def rolling_zscore(series: pd.Series,
                      window: int) -> pd.Series:
        """
        滚动Z-Score

        Z = (X - μ) / σ
        """
        roll_mean = series.rolling(window).mean()
        roll_std = series.rolling(window).std()
        return (series - roll_mean) / roll_std
```

### 4.2 趋势检�?

```python
class TrendDetection:
    """趋势检测工�?""

    @staticmethod
    def linear_trend(series: pd.Series) -> Dict:
        """
        线性趋势拟�?

        返回:
            {slope, intercept, r_value, p_value}
        """
        x = np.arange(len(series))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, series)

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "trend": "up" if slope > 0 and p_value < 0.05 else
                     "down" if slope < 0 and p_value < 0.05 else "flat"
        }

    @staticmethod
    def rolling_trend(series: pd.Series,
                     window: int = 20) -> pd.Series:
        """
        滚动趋势判断

        返回:
            滚动窗口内的趋势方向
        """
        def trend_direction(x):
            slope, _, r, p, _ = stats.linregress(np.arange(len(x)), x)
            if p > 0.05:
                return 0  # 无显著趋�?
            return 1 if slope > 0 else -1

        return series.rolling(window).apply(trend_direction)

    @staticmethod
    def zscore_crossover(series: pd.Series,
                        window: int = 20,
                        upper_threshold: float = 2.0,
                        lower_threshold: float = -2.0) -> pd.DataFrame:
        """
        Z-Score穿越检�?
        用于均值回归策�?

        返回:
            DataFrame with zscore and signals
        """
        roll_mean = series.rolling(window).mean()
        roll_std = series.rolling(window).std()
        zscore = (series - roll_mean) / roll_std

        signals = pd.DataFrame(index=series.index)
        signals['zscore'] = zscore
        signals['signal'] = 0
        signals.loc[zscore > upper_threshold, 'signal'] = -1  # 超买
        signals.loc[zscore < lower_threshold, 'signal'] = 1   # 超卖

        return signals
```

---

## 5. 相关性分�?

### 5.1 相关系数计算

```python
class CorrelationAnalysis:
    """相关性分析工�?""

    @staticmethod
    def pearson_corr(x: pd.Series,
                    y: pd.Series) -> float:
        """Pearson相关系数"""
        return x.corr(y)

    @staticmethod
    def spearman_corr(x: pd.Series,
                     y: pd.Series) -> float:
        """Spearman秩相关系�?""
        return x.corr(y, method='spearman')

    @staticmethod
    def kendall_corr(x: pd.Series,
                    y: pd.Series) -> float:
        """Kendall Tau相关系数"""
        return x.corr(y, method='kendall')

    @classmethod
    def correlation_matrix(cls,
                          data: pd.DataFrame,
                          method: str = 'pearson') -> pd.DataFrame:
        """
        计算相关矩阵

        参数:
            data: DataFrame
            method: 'pearson', 'spearman', 'kendall'
        """
        return data.corr(method=method)

    @staticmethod
    def rolling_correlation(x: pd.Series,
                            y: pd.Series,
                            window: int = 60) -> pd.Series:
        """
        滚动相关�?

        参数:
            x, y: 两个时间序列
            window: 滚动窗口
        """
        return x.rolling(window).corr(y)
```

### 5.2 相关性分析报�?

```python
class CorrelationReport:
    """相关性分析报�?""

    @staticmethod
    def generate_report(data: pd.DataFrame,
                       target: str,
                       method: str = 'pearson') -> pd.DataFrame:
        """
        生成与目标变量的相关性报�?

        参数:
            data: 数据DataFrame
            target: 目标变量�?
            method: 相关系数方法

        返回:
            DataFrame: 包含相关系数和p�?
        """
        results = []

        for col in data.columns:
            if col == target:
                continue

            if data[col].dtype in [np.float64, np.int64]:
                corr = data[col].corr(data[target], method=method)

                # 计算p�?
                n = len(data)
                t_stat = corr * np.sqrt(n - 2) / np.sqrt(1 - corr ** 2)
                p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))

                results.append({
                    'variable': col,
                    'correlation': corr,
                    'abs_correlation': abs(corr),
                    'p_value': p_value,
                    'significant': p_value < 0.05
                })

        df = pd.DataFrame(results)
        df.sort_values('abs_correlation', ascending=False, inplace=True)
        return df

    @staticmethod
    def heatmap_data(data: pd.DataFrame,
                    threshold: float = 0.5) -> pd.DataFrame:
        """
        生成相关性热力图数据
        只保留相关性超过阈值的变量�?
        """
        corr = data.corr()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

        # 找到高相关的变量�?
        high_corr = [
            (col, row, upper.loc[row, col])
            for col in upper.columns
            for row in upper.index
            if abs(upper.loc[row, col]) > threshold
        ]

        return pd.DataFrame(high_corr, columns=['var1', 'var2', 'correlation'])
```

---

## 6. 组合统计分析

### 6.1 多因子分�?

```python
class FactorStatistics:
    """因子统计分析"""

    @staticmethod
    def factor_returns(factor: pd.Series,
                      returns: pd.Series,
                      quantiles: int = 5) -> pd.DataFrame:
        """
        计算因子分位数组合收�?

        参数:
            factor: 因子�?
            returns: 收益�?
            quantiles: 分组�?

        返回:
            DataFrame: 各分位数组合的收益统�?
        """
        # 按因子值分�?
        labels = [f'Q{i+1}' for i in range(quantiles)]
        factor_quantiles = pd.qcut(factor, q=quantiles, labels=labels)

        results = []
        for q in labels:
            q_returns = returns[factor_quantiles == q]
            results.append({
                'quantile': q,
                'mean': q_returns.mean(),
                'std': q_returns.std(),
                'count': len(q_returns),
                'annual_return': q_returns.mean() * 252,
                'annual_vol': q_returns.std() * np.sqrt(252)
            })

        return pd.DataFrame(results)

    @staticmethod
    def factor_ic(factor: pd.Series,
                 returns: pd.Series,
                 method: str = 'pearson') -> Dict:
        """
        计算因子IC (Information Coefficient)

        IC = corr(factor, forward_return)

        参数:
            factor: 因子�?
            returns: 下期收益
            method: 'pearson' or 'spearman'

        返回:
            {ic_mean, ic_std, ic_ir, ic_series}
        """
        if method == 'pearson':
            ic_series = factor.rolling(20).corr(returns)
        else:
            ic_series = factor.rolling(20).corr(returns, method='spearman')

        return {
            'ic_mean': ic_series.mean(),
            'ic_std': ic_series.std(),
            'ic_ir': ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0,
            'ic_series': ic_series
        }
```

### 6.2 滚动分析

```python
class RollingAnalysis:
    """滚动分析工具"""

    @staticmethod
    def rolling_metrics(returns: pd.Series,
                       window: int = 252) -> pd.DataFrame:
        """
        计算滚动性能指标

        参数:
            returns: 收益率序�?
            window: 滚动窗口

        返回:
            DataFrame: 包含滚动收益、波动率、夏普比率、最大回�?
        """
        df = pd.DataFrame(index=returns.index)

        df['rolling_return'] = returns.rolling(window).mean() * 252
        df['rolling_vol'] = returns.rolling(window).std() * np.sqrt(252)
        df['rolling_sharpe'] = df['rolling_return'] / df['rolling_vol']

        # 滚动最大回�?
        prices = (1 + returns).cumprod()
        rolling_max = prices.rolling(window).max()
        drawdown = (prices - rolling_max) / rolling_max
        df['rolling_mdd'] = drawdown.rolling(window).min()

        return df

    @staticmethod
    def expanding_metrics(returns: pd.Series) -> pd.DataFrame:
        """
        扩展窗口指标 (从开始到当前)
        """
        df = pd.DataFrame(index=returns.index)

        df['cumulative_return'] = (1 + returns).cumprod() - 1
        df['expanding_mean'] = returns.expanding().mean() * 252
        df['expanding_std'] = returns.expanding().std() * np.sqrt(252)
        df['expanding_sharpe'] = df['expanding_mean'] / df['expanding_std']

        return df
```

---

## 7. 统计检�?

### 7.1 常用检�?

```python
class StatisticalTests:
    """统计检验工�?""

    @staticmethod
    def t_test(sample1: pd.Series,
              sample2: pd.Series,
              equal_var: bool = False) -> Dict:
        """
        独立样本t检�?

        检验两组均值是否显著不�?
        """
        t_stat, p_value = stats.ttest_ind(sample1, sample2, equal_var=equal_var)

        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'interpretation': '均值显著不�? if p_value < 0.05 else '均值无显著差异'
        }

    @staticmethod
    def mann_whitney_test(sample1: pd.Series,
                         sample2: pd.Series) -> Dict:
        """
        Mann-Whitney U检�?(非参�?

        不要求正态分布假�?
        """
        statistic, p_value = stats.mannwhitneyu(sample1, sample2)

        return {
            'u_statistic': statistic,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    @staticmethod
    def stationarity_test(series: pd.Series) -> Dict:
        """
        ADF平稳性检�?

        检验时间序列是否平�?
        """
        result = stats.zivot_andrews(series) if hasattr(stats, 'zivot_andrews') \
                 else None

        # 使用adfuller
        from statsmodels.tsa.stattools import adfuller
        adf_result = adfuller(series, autolag='AIC')

        return {
            'adf_statistic': adf_result[0],
            'p_value': adf_result[1],
            'used_lag': adf_result[2],
            'is_stationary': adf_result[1] < 0.05
        }

    @staticmethod
    def autocorrelation_test(series: pd.Series,
                            lags: int = 10) -> pd.DataFrame:
        """
        自相关性检�?(Ljung-Box)

        检验序列是否存在自相关
        """
        from statsmodels.stats.diagnostic import acorr_ljungbox

        result = acorr_ljungbox(series, lags=lags, return_df=True)

        return result
```

---

## 8. 快速使用示�?

```python
# 1. 描述性统�?
stats = DescriptiveStatistics.compute(df['close'])
print(stats.to_dict())

# 2. 收益率分�?
returns = ReturnStatistics.log_return(df['close'])
annual_ret = ReturnStatistics.annual_return(returns)
annual_vol = ReturnStatistics.annual_volatility(returns)
sharpe = ReturnStatistics.sharpe_ratio(returns)

# 3. 滚动分析
rolling = RollingAnalysis.rolling_metrics(returns, window=60)

# 4. 相关�?
corr_report = CorrelationReport.generate_report(factor_df, target='forward_return')
high_corr = CorrelationReport.heatmap_data(factor_df, threshold=0.7)

# 5. 因子IC
ic_result = FactorStatistics.factor_ic(factor, forward_returns)
```

---

## 9. 配置

```yaml
# config/statistical_analysis.yaml
statistical_analysis:
  rolling_window: 60
  annualization_factor: 252

  correlation:
    default_method: spearman
    significance_threshold: 0.05

  outlier:
    iqr_factor: 1.5
    zscore_threshold: 3.0

  factor_analysis:
    quantile_groups: 5
    ic_rolling_window: 20
```

---

**版本**: 1.0
**更新**: 2026-03-28
**状�?*: 草稿
