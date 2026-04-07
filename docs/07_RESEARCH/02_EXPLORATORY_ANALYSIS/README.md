---
module_id: RESEARCH_EXPLORATORY_README_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构研究标准
applicable_scope: 量化研究实验
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
responsibility:
  - 说明文档、快速入门

---
---

# 探索性分析工�?
> **核心职责**: 模块说明和快速入门指南
> **职责边界**: 
> - ✅ 本文档负责：模块说明和快速入门指南相关内容
> - ❌ 本文档不负责：其他模块内容


> 统计分析、模式挖掘、可视化

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer -1
**索引**: 07_RESEARCH/02_EXPLORATORY_ANALYSIS

---

## 1. 统计分析工具

### 描述性统�?

```python
class DescriptiveStatistics:
    """描述性统计分�?""

    def analyze(self, series: pd.Series) -> dict:
        """计算描述性统�?""
        return {
            'mean': series.mean(),
            'median': series.median(),
            'std': series.std(),
            'skewness': series.skew(),
            'kurtosis': series.kurtosis(),
            'percentiles': series.quantile([0.25, 0.5, 0.75, 0.99])
        }
```

### 分布分析

```python
class DistributionAnalyzer:
    """分布分析工具"""

    def normality_test(self, series: pd.Series) -> dict:
        """正态性检�?""
        from scipy import stats
        return {
            'shapiro': stats.shapiro(series),
            'dagostino': stats.normaltest(series),
            'anderson': stats.anderson(series)
        }

    def qq_plot_data(self, series: pd.Series) -> list:
        """生成QQ图数�?""
        import numpy as np
        quantiles = np.percentile(series, range(0, 100))
        theoretical = stats.norm.ppf([i/100 for i in range(0, 100)])
        return list(zip(theoretical, quantiles))
```

### 稳定性分�?

```python
class StationarityTests:
    """平稳性检�?""

    def adf_test(self, series: pd.Series) -> dict:
        """ADF检�?""
        from statsmodels.tsa.stattools import adfuller
        result = adfuller(series)
        return {
            'statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4]
        }

    def kpss_test(self, series: pd.Series) -> dict:
        """KPSS检�?""
        from statsmodels.tsa.stattools import kpss
        result = kpss(series, regression='c')
        return {
            'statistic': result[0],
            'p_value': result[1]
        }
```

---

## 2. 相关性分�?

### 截面相关

```python
class CrossSectionalCorrelation:
    """截面相关性分�?""

    def correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """计算截面相关矩阵"""
        return returns.corr()

    def cluster_analysis(self, corr_matrix: pd.DataFrame, n_clusters: int):
        """聚类分析"""
        from scipy.cluster.hierarchy import linkage, fcluster
        dist = 1 - corr_matrix
        linkage_matrix = linkage(dist, method='average')
        return fcluster(linkage_matrix, n_clusters, criterion='maxclust')
```

### 滚动相关

```python
class RollingCorrelation:
    """滚动相关性分�?""

    def rolling_corr(self, series1: pd.Series, series2: pd.Series,
                     window: int = 20) -> pd.Series:
        """计算滚动窗口相关�?""
        return series1.rolling(window).corr(series2)
```

---

## 3. 深度模式挖掘

### 市场状态聚�?

```python
class MarketRegimeDetector:
    """市场状态识�?""

    def detect_regimes(self, features: pd.DataFrame,
                       n_regimes: int = 4) -> np.array:
        """使用GMM识别市场状�?""
        from sklearn.mixture import GaussianMixture
        gmm = GaussianMixture(n_components=n_regimes)
        return gmm.fit_predict(features)

    def describe_regime(self, data: pd.DataFrame, regime_id: int) -> dict:
        """描述市场状态特�?""
        regime_data = data[data['regime'] == regime_id]
        return {
            'avg_volatility': regime_data['volatility'].mean(),
            'avg_return': regime_data['return'].mean(),
            'label': self._regime_label(regime_id)
        }
```

### 季节性分�?

```python
class SeasonalityAnalyzer:
    """季节�?周期性分�?""

    def month_effect(self, returns: pd.Series) -> pd.DataFrame:
        """月份效应分析"""
        monthly = returns.groupby(returns.index.month).agg(['mean', 'std', 'count'])
        return monthly

    def day_of_week_effect(self, returns: pd.Series) -> pd.DataFrame:
        """星期效应分析"""
        dow = returns.groupby(returns.index.dayofweek).agg(['mean', 'std'])
        return dow

    def fourier_analysis(self, series: pd.Series, n_harmonics: int = 5):
        """傅里叶变换分析周�?""
        from scipy.fft import fft
        n = len(series)
        y = series.values
        fft_values = fft(y)[:n//2]
        frequencies = np.fft.fftfreq(n)[:n//2]
        return frequencies, np.abs(fft_values)
```

---

## 4. 因子穷举测试

```python
class FactorExhaustor:
    """因子穷举测试 - AI因子挖掘"""

    def exhaustive_search(self, data: pd.DataFrame,
                         factor_templates: list,
                         target: str = 'return_5d') -> list:
        """穷举测试简单因子组�?""
        results = []
        for template in factor_templates:
            factor = self._apply_template(template, data)
            ic = self._calculate_ic(factor, data[target])
            results.append({
                'template': template,
                'ic': ic,
                'rank_ic': self._calculate_rank_ic(factor, data[target])
            })
        return sorted(results, key=lambda x: x['rank_ic'], reverse=True)
```

---

## 索引

- 父目�? [07_RESEARCH/README.md](../README.md)
- 相关文档: [candle_patterns.md](../03_PATTERN_RECOGNITION/candle_patterns.md)
