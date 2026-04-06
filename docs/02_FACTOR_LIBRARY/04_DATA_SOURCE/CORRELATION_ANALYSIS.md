---
module_id: FACTOR_相关性分析_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
module_id: DATA_CORRELATION_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-06
owner: 首席文档架构师
standard_type: 分析工具文档
applicable_scope: 相关性分析
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 进行中
---

# 相关性分析

## 文档职责说明

**本文档职责**: 深度相关性分析方法
- 偏相关分析实现
- 条件相关性分析
- 相关性统计检验

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 统计分析工具 | [STATISTICAL_TOOLS.md](./STATISTICAL_TOOLS.md) | 基础层 | 基础统计分析工具 |
| 数据源索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: 高级相关性分析方法
- ❌ 本文档不负责: 基础统计分析（由 STATISTICAL_TOOLS.md 负责）

> **模块编号**: M-CORR-001 (Correlation Analysis)
> **版本**: 1.0
> **创建日期**: 2026-03-28
> **优先级**: P1
> **依赖**: STATISTICAL_TOOLS.md

---

## 1. 概述

本文档是统计分析工具的补充，专注于**深入的相关性分析**方法，包括偏相关、条件相关、协整检验等高级主题。

> 基础相关系数计算请参考 [STATISTICAL_TOOLS.md](STATISTICAL_TOOLS.md) 中的 `CorrelationAnalysis` 类。

---

## 2. 偏相关分析

### 2.1 概念

偏相关（Partial Correlation）是指在控制其他变量影响后，两个变量之间的相关程度。

```
r_XY|Z = (r_XY - r_XZ * r_YZ) / sqrt((1-r_XZ²)(1-r_YZ²))
```

### 2.2 实现

```python
from typing import List
import pandas as pd
import numpy as np

class PartialCorrelation:
    """偏相关分析"""

    @staticmethod
    def compute(x: pd.Series,
               y: pd.Series,
               control_vars: List[pd.Series]) -> float:
        """
        计算偏相关系数

        参数:
            x: 变量X
            y: 变量Y
            control_vars: 控制变量列表

        返回:
            偏相关系数
        """
        from scipy import stats

        n = len(x)
        k = len(control_vars)

        if k == 0:
            return x.corr(y)

        # 构建设计矩阵
        X = np.column_stack([x.values] + [c.values for c in control_vars])

        # 残差化
        def residualize(series):
            from sklearn.linear_model import LinearRegression
            reg = LinearRegression()
            reg.fit(X, series.values)
            return series.values - reg.predict(X)

        x_resid = residualize(x)
        y_resid = residualize(y)

        # 计算残差的相关
        return np.corrcoef(x_resid, y_resid)[0, 1]

    @classmethod
    def compute_matrix(cls,
                      data: pd.DataFrame,
                      control_cols: List[str] = None) -> pd.DataFrame:
        """
        计算偏相关矩阵

        参数:
            data: 数据DataFrame
            control_cols: 控制变量列表，None表示计算简单相关
        """
        cols = data.columns.tolist()
        n = len(cols)
        result = pd.DataFrame(np.zeros((n, n)), index=cols, columns=cols)

        for i, col1 in enumerate(cols):
            for j, col2 in enumerate(cols):
                if i == j:
                    result.loc[col1, col2] = 1.0
                elif j > i:
                    if control_cols:
                        control_vars = [data[c] for c in control_cols]
                        pc = cls.compute(data[col1], data[col2], control_vars)
                    else:
                        pc = data[col1].corr(data[col2])
                    result.loc[col1, col2] = pc
                    result.loc[col2, col1] = pc

        return result
```

---

## 3. 条件相关性

### 3.1 概念

条件相关性（Conditional Correlation）分析在不同条件（或分组）下相关性的变化。

### 3.2 实现

```python
class ConditionalCorrelation:
    """条件相关性分析"""

    @staticmethod
    def by_quantile(data: pd.DataFrame,
                   x: str,
                   y: str,
                   condition_var: str,
                   n_quantiles: int = 3) -> pd.DataFrame:
        """
        按分位数分组计算相关性

        参数:
            data: 数据
            x, y: 相关变量
            condition_var: 条件变量
            n_quantiles: 分组数

        返回:
            各分位数组的相关性
        """
        results = []
        labels = [f'Q{i+1}' for i in range(n_quantiles)]
        quantile_labels = pd.qcut(data[condition_var], q=n_quantiles, labels=labels)

        for label in labels:
            subset = data[quantile_labels == label]
            if len(subset) > 5:
                corr = subset[x].corr(subset[y])
                results.append({
                    'condition_quantile': label,
                    'correlation': corr,
                    'sample_size': len(subset),
                    'significant': abs(corr) > 2 / np.sqrt(len(subset))
                })

        return pd.DataFrame(results)

    @staticmethod
    def rolling_correlation_stability(x: pd.Series,
                                      y: pd.Series,
                                      window: int = 60) -> Dict:
        """
        滚动相关性稳定性分析

        返回:
            {mean_corr, std_corr, stability_ratio, cv}
        """
        roll_corr = x.rolling(window).corr(y)

        mean_corr = roll_corr.mean()
        std_corr = roll_corr.std()
        stability_ratio = mean_corr / std_corr if std_corr > 0 else np.inf
        cv = std_corr / abs(mean_corr) if mean_corr != 0 else np.inf

        return {
            'mean_correlation': mean_corr,
            'std_correlation': std_corr,
            'stability_ratio': stability_ratio,
            'coefficient_of_variation': cv,
            'rolling_correlation': roll_corr,
            'is_stable': cv < 0.5
        }
```

---

## 4. 相关性检验

### 4.1 相关系数显著性检验

```python
class CorrelationTest:
    """相关性统计检验"""

    @staticmethod
    def pearson_test(x: pd.Series,
                    y: pd.Series) -> Dict:
        """
        Pearson相关性的t检验

        H0: ρ = 0 (无线性相关)
        """
        n = len(x)
        r = x.corr(y)

        # t = r * sqrt(n-2) / sqrt(1-r²)
        t_stat = r * np.sqrt(n - 2) / np.sqrt(1 - r ** 2)

        from scipy import stats
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))

        return {
            'correlation': r,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant_005': p_value < 0.05,
            'significant_001': p_value < 0.01,
            'n_samples': n
        }

    @staticmethod
    def spearman_test(x: pd.Series,
                     y: pd.Series) -> Dict:
        """
        Spearman相关的符号检验
        """
        from scipy import stats
        corr, p_value = stats.spearmanr(x, y)

        return {
            'correlation': corr,
            'p_value': p_value,
            'significant_005': p_value < 0.05,
            'n_samples': len(x)
        }

    @staticmethod
    def correlation_confidence_interval(r: float,
                                       n: int,
                                       confidence: float = 0.95) -> Tuple[float, float]:
        """
        Pearson相关系数的置信区间(Fisher Z变换)

        参数:
            r: 相关系数
            n: 样本数
            confidence: 置信水平
        """
        from scipy import stats

        # Fisher Z变换
        z = 0.5 * np.log((1 + r) / (1 - r))
        se = 1 / np.sqrt(n - 3)

        # 置信区间
        z_alpha = stats.norm.ppf((1 + confidence) / 2)
        z_lower = z - z_alpha * se
        z_upper = z + z_alpha * se

        # 逆变换
        r_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
        r_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)

        return r_lower, r_upper
```

### 4.2 相关性差异检验

```python
class CorrelationDifferenceTest:
    """两个相关系数的差异检验"""

    @staticmethod
    def compare_correlations(r1: float,
                            n1: int,
                            r2: float,
                            n2: int) -> Dict:
        """
        检验两个相关系数是否有显著差异

        使用Fisher Z变换
        """
        from scipy import stats

        # Fisher Z变换
        z1 = 0.5 * np.log((1 + r1) / (1 - r1))
        z2 = 0.5 * np.log((1 + r2) / (1 - r2))

        # Z统计量
        se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
        z_diff = (z1 - z2) / se

        p_value = 2 * (1 - stats.norm.cdf(abs(z_diff)))

        return {
            'r1': r1,
            'r2': r2,
            'z_statistic': z_diff,
            'p_value': p_value,
            'significant_005': p_value < 0.05,
            'n1': n1,
            'n2': n2
        }
```

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
