---
module_id: 07_RESEARCH_02_EXPLORATORY_ANALYSIS_CORRELATION_ANALYSIS
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 相关性分文档
---

﻿---
module_id: RESEARCH_CORRELATION_ANALYSIS_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
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


# 相关性分?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 因子、资产、市场的相关性分析工?
>
> **版本**: v1.0
> **更新**: 2026-03-28
> **优先?*: P1 - 核心模块
> **Layer**: Layer 1 (分析?
> **索引**: R.02.EDA.002

---

## 1. 概述

相关性分析是量化研究的基础工具，用于：
- 因子间的相关性分析（避免因子冗余?
- 资产间的相关性分析（组合构建?
- 时间序列的领先滞后关系（择时信号?

---

## 2. 相关性类?

| 类型 | 说明 | 应用场景 |
|------|------|----------|
| 截面相关?| 同一时间点不同资产的相关?| 因子相关性、资产配?|
| 时序相关?| 同一资产不同时间的相关?| 趋势识别、自相关检?|
| 交叉相关?| 两个时间序列的领先滞后关?| 择时信号、因果分?|
| 滚动相关?| 滚动窗口内的动态相关?| 相关性稳定性分?|

---

## 3. 截面相关?

### 3.1 计算方法

```python
import pandas as pd
import numpy as np

class CrossSectionalCorrelation:
    """截面相关性分?""

    def calculate(
        self,
        data: pd.DataFrame,
        method: str = 'spearman'
    ) -> pd.DataFrame:
        """
        计算截面相关性矩?

        Parameters:
        -----------
        data : pd.DataFrame
            ?日期，列=资产/因子代码
        method : str
            'spearman' ?'pearson'

        Returns:
        --------
        pd.DataFrame: 相关性矩?
        """
        return data.corr(method=method)
```

### 3.2 因子相关性分?

```python
class FactorCorrelationAnalyzer:
    """因子相关性分析器"""

    def analyze_factor_correlation(
        self,
        factor_data: dict,
        threshold: float = 0.8
    ) -> dict:
        """
        分析因子相关性，找出高相关因子对

        Parameters:
        -----------
        factor_data : dict
            {因子? 因子值DataFrame}
        threshold : float
            高相关阈?

        Returns:
        --------
        dict: {高相关对: 相关系数}
        """
        # 构建因子矩阵
        factor_matrix = pd.DataFrame(factor_data)

        # 计算相关性矩?
        corr_matrix = factor_matrix.corr(method='spearman')

        # 找出高相关对
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    high_corr_pairs.append({
                        'factor1': corr_matrix.columns[i],
                        'factor2': corr_matrix.columns[j],
                        'correlation': corr_value
                    })

        return {
            'correlation_matrix': corr_matrix,
            'high_correlation_pairs': high_corr_pairs
        }
```

---

## 4. 时间序列相关?

### 4.1 交叉相关计算

```python
class TimeSeriesCorrelation:
    """时间序列相关性分?""

    def cross_correlation(
        self,
        series1: pd.Series,
        series2: pd.Series,
        max_lag: int = 20
    ) -> pd.Series:
        """
        计算两个时间序列的交叉相关（领先滞后关系?

        Parameters:
        -----------
        series1 : pd.Series
            第一个时间序?
        series2 : pd.Series
            第二个时间序?
        max_lag : int
            最大滞后阶?

        Returns:
        --------
        pd.Series: 各滞后阶数的相关系数
        """
        correlations = {}
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                corr = series1.iloc[-lag:].corr(series2.iloc[:lag].values)
            elif lag > 0:
                corr = series1.iloc[:-lag].corr(series2.iloc[lag:].values)
            else:
                corr = series1.corr(series2)
            correlations[lag] = corr

        return pd.Series(correlations)

    def find_lead_lag(
        self,
        series1: pd.Series,
        series2: pd.Series,
        max_lag: int = 20
    ) -> dict:
        """
        判断两个序列的领先滞后关?

        Returns:
        --------
        dict: {'lead': series1领先多少? 'lag': series1滞后多少期}
        """
        cross_corr = self.cross_correlation(series1, series2, max_lag)
        best_lag = cross_corr.abs().idxmax()
        best_corr = cross_corr[best_lag]

        return {
            'best_lag': best_lag,
            'best_correlation': best_corr,
            'relationship': 'series1 leads series2' if best_lag < 0 else
                           'series2 leads series1' if best_lag > 0 else
                           'contemporaneous'
        }
```

---

## 5. 滚动相关?

### 5.1 滚动相关计算

```python
class RollingCorrelation:
    """滚动相关性分?""

    def calculate_rolling_correlation(
        self,
        series1: pd.Series,
        series2: pd.Series,
        window: int = 60
    ) -> pd.Series:
        """
        计算滚动相关?

        Parameters:
        -----------
        series1 : pd.Series
        series2 : pd.Series
        window : int
            滚动窗口大小

        Returns:
        --------
        pd.Series: 滚动相关系数序列
        """
        return series1.rolling(window).corr(series2)

    def analyze_correlation_stability(
        self,
        series1: pd.Series,
        series2: pd.Series,
        window: int = 60
    ) -> dict:
        """
        分析相关性的稳定?

        Returns:
        --------
        dict: {均? 标准? 最小? 最大? 稳定性评分}
        """
        rolling_corr = self.calculate_rolling_correlation(series1, series2, window)

        return {
            'mean': rolling_corr.mean(),
            'std': rolling_corr.std(),
            'min': rolling_corr.min(),
            'max': rolling_corr.max(),
            'stability_score': rolling_corr.mean() / rolling_corr.std() if rolling_corr.std() > 0 else 0,
            'is_stable': rolling_corr.std() < 0.3
        }
```

---

## 6. 相关性矩阵可视化

### 6.1 热力图数?

```python
class CorrelationHeatmap:
    """相关性热力图数据生成?""

    def prepare_heatmap_data(
        self,
        data: pd.DataFrame,
        labels: list = None
    ) -> dict:
        """
        生成热力图所需数据

        Returns:
        --------
        dict: {matrix: [[]], labels: [], colorscale: str}
        """
        corr_matrix = data.corr(method='spearman')

        return {
            'matrix': corr_matrix.values.tolist(),
            'labels': labels if labels else corr_matrix.columns.tolist(),
            'colorscale': 'RdBu',  # 红蓝配色
            'zmid': 0  # 中心?
        }
```

---

## 7. 因子正交?

### 7.1 Gram-Schmidt正交?

```python
class FactorOrthogonalization:
    """因子正交化处?""

    def gram_schmidt(
        self,
        factors: pd.DataFrame,
        reference_factor: str = None
    ) -> pd.DataFrame:
        """
        对因子进行正交化处理

        Parameters:
        -----------
        factors : pd.DataFrame
            因子矩阵
        reference_factor : str
            参考因子（其他因子对其正交化）

        Returns:
        --------
        pd.DataFrame: 正交化后的因子矩?
        """
        orthogonalized = factors.copy()

        if reference_factor and reference_factor in factors.columns:
            # 对除参考因子外的所有因子进行正交化
            reference = factors[reference_factor].values

            for col in factors.columns:
                if col == reference_factor:
                    continue

                # 计算正交分量
                factor = factors[col].values
                projection = np.multiply(
                    np.dot(factor, reference) / np.dot(reference, reference),
                    reference
                )
                orthogonalized[col] = factor - projection

        return orthogonalized

    def sequential_orthogonalization(
        self,
        factors: pd.DataFrame
    ) -> pd.DataFrame:
        """
        顺序正交化（每个因子对前面所有因子正交）

        Returns:
        --------
        pd.DataFrame: 正交化后的因子矩?
        """
        orthogonalized = pd.DataFrame(
            index=factors.index,
            columns=factors.columns
        )

        for i, col in enumerate(factors.columns):
            if i == 0:
                orthogonalized[col] = factors[col]
            else:
                # 对前面已正交化因子回归，取残?
                reference_cols = factors.columns[:i]
                reference_data = orthogonalized[reference_cols]

                # 多元回归残差
                residual = self._regression_residual(
                    factors[col],
                    reference_data
                )
                orthogonalized[col] = residual

        return orthogonalized

    def _regression_residual(
        self,
        y: pd.Series,
        X: pd.DataFrame
    ) -> pd.Series:
        """计算回归残差"""
        from numpy.linalg import lstsq

        X_arr = np.column_stack([np.ones(len(X)), X.values])
        y_arr = y.values

        # 最小二乘解
        coeffs, _, _, _ = lstsq(X_arr, y_arr, rcond=None)

        # 预测?
        y_pred = X_arr @ coeffs

        # 残差
        return pd.Series(y_arr - y_pred, index=y.index)
```

---

## 8. 配置模板

```yaml
# config/correlation_analysis.yaml
correlation_analysis:
  # 截面相关性配?
  cross_sectional:
    method: "spearman"          # spearman | pearson
    high_threshold: 0.8         # 高相关阈?
    warning_threshold: 0.6      # 警告阈?

  # 滚动相关性配?
  rolling:
    window: 60                  # 滚动窗口
    min_periods: 30             # 最小样本数
    stability_threshold: 0.3    # 稳定性阈?

  # 正交化配?
  orthogonalization:
    method: "gram_schmidt"      # gram_schmidt | sequential
    reference_factor: "MARKET_CAP"  # 参考因?

  # 交叉相关配置
  cross_correlation:
    max_lag: 20                 # 最大滞后阶?
    significance_level: 0.05    # 显著性水?
```

---

## 9. 目录位置

```
07_RESEARCH/02_EXPLORATORY_ANALYSIS/
├── README.md
├── statistical_tools.md         # 统计分析工具
├── correlation_analysis.md     # 本文??
└── pattern_mining.md          # 模式挖掘(待创?
```

---

## 10. 接口定义

| 接口 | 说明 |
|------|------|
| **上游接口** | DataHub、因子计算引?|
| **下游接口** | 因子合成、组合优化、风险分?|
| **输入格式** | pd.DataFrame (date x asset/factor) |
| **输出格式** | pd.DataFrame (相关性矩? |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |
