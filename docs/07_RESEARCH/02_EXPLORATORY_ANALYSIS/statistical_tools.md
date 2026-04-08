---
module_id: RESEARCH_STATISTICAL_TOOLS_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: '2026-04-07'
owner: 首席文档架构?
responsibility:
- 07 RESEARCH模块文档管理与维护
standard_type: 专业量化机构研究标准
applicable_scope: 量化研究实验
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# 探索性分?- 统计分析工具
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 数据探索阶段的基本统计分析工具集

---

## 1. 统计分析工具

### 1.1 描述性统?

```python
import pandas as pd
import numpy as np
from scipy import stats

def descriptive_statistics(series: pd.Series) -> dict:
    """计算描述性统?""
    return {
        'count': len(series),
        'mean': series.mean(),
        'std': series.std(),
        'min': series.min(),
        'q25': series.quantile(0.25),
        'median': series.median(),
        'q75': series.quantile(0.75),
        'max': series.max(),
        'skewness': series.skew(),
        'kurtosis': series.kurtosis(),
        'cv': series.std() / series.mean() if series.mean() != 0 else np.nan
    }
```

### 1.2 分布分析

```python
def distribution_analysis(series: pd.Series) -> dict:
    """分布分析"""
    # 正态性检?
    _, p_value_shapiro = stats.shapiro(series.dropna())

    # Kolmogorov-Smirnov 检?
    _, p_value_kstest = stats.kstest(series.dropna(), 'norm')

    # QQ图数?
    theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, 100))
    sample_quantiles = series.dropna().quantile(np.linspace(0.01, 0.99, 100))

    return {
        'normality_shapiro_pvalue': p_value_shapiro,
        'normality_ks_pvalue': p_value_kstest,
        'is_normal': p_value_shapiro > 0.05,
        'theoretical_quantiles': theoretical_quantiles,
        'sample_quantiles': sample_quantiles
    }
```

---

## 2. 稳定性分?

### 2.1 平稳性检查

```python
from statsmodels.tsa.stattools import adfuller, kpss

def stationarity_tests(series: pd.Series) -> dict:
    """平稳性检?""
    # ADF 检?
    adf_result = adfuller(series.dropna(), autolag='AIC')

    # KPSS 检?
    kpss_result = kpss(series.dropna(), regression='c', nlags='auto')

    return {
        'adf_statistic': adf_result[0],
        'adf_pvalue': adf_result[1],
        'adf_is_stationary': adf_result[1] < 0.05,
        'kpss_statistic': kpss_result[0],
        'kpss_pvalue': kpss_result[1],
        'kpss_is_stationary': kpss_result[1] > 0.05
    }
```

### 2.2 滚动统计

```python
def rolling_statistics(series: pd.Series, window: int = 20) -> pd.DataFrame:
    """滚动统计"""
    return pd.DataFrame({
        'value': series,
        'rolling_mean': series.rolling(window).mean(),
        'rolling_std': series.rolling(window).std(),
        'rolling_zscore': (series - series.rolling(window).mean()) / series.rolling(window).std()
    })
```

---

## 3. 相关性分?

### 3.1 截面相关?

```python
def cross_section_correlation(returns_df: pd.DataFrame) -> pd.DataFrame:
    """截面相关性矩?""
    return returns_df.corr()
```

### 3.2 时间序列相关性（交叉相关?

```python
from scipy.signal import correlate

def cross_correlation(series1: pd.Series, series2: pd.Series, max_lag: int = 20) -> dict:
    """交叉相关分析"""
    correlations = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            corr = series1.iloc[-lag:].corr(series2.iloc[:lag])
        elif lag > 0:
            corr = series1.iloc[:-lag].corr(series2.iloc[lag:])
        else:
            corr = series1.corr(series2)
        correlations[lag] = corr

    return {
        'lag_correlations': correlations,
        'max_lag': max(correlations, key=correlations.get),
        'max_correlation': max(correlations.values())
    }
```

---

## 4. 输出格式

```python
class AnalysisReport:
    """分析报告生成"""

    def __init__(self, name: str):
        self.name = name
        self.sections = []

    def add_section(self, title: str, content: dict):
        self.sections.append({'title': title, 'content': content})

    def to_markdown(self) -> str:
        """输出 Markdown 格式"""
        md = f"# {self.name}\n\n"
        for section in self.sections:
            md += f"## {section['title']}\n\n"
            md += self._format_dict(section['content'])
            md += "\n\n"
        return md

    def _format_dict(self, d: dict) -> str:
        md = ""
        for k, v in d.items():
            if isinstance(v, (int, float)):
                md += f"- **{k}**: {v:.4f}\n"
            else:
                md += f"- **{k}**: {v}\n"
        return md
```

---

**版本**: 1.0 | **更新**: 2026-03-28
