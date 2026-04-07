---


module_id: 02_FACTOR_LIBRARY_04_DATA_SOURCE_001


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

responsibility:
  - 管理因子库
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
