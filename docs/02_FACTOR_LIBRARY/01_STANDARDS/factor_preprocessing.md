---
module_id: FACTOR_PREPROCESSING_001
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
module_id: STANDARDS_PREPROCESSING_001
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

# 因子预处理方�?

> 因子标准化处理流�?

---

## 1. 预处理流�?

```
原始因子 �?缺失值处�?�?异常值处�?�?标准�?�?因子�?
```

---

## 2. 缺失值处�?

### 2.1 处理方法

| 方法 | 适用场景 | 实现 |
|------|----------|------|
| 删除�?| 缺失比例>30% | dropna |
| 填充�?| 缺失比例<30% | fillna |
| 中位数填�?| 非极端值因�?| median |
| 前后均值填�?| 时序连续因子 | ffill/bfill |
| 行业均值填�?| 存在行业差异 | groupby median |

### 2.2 Python实现

```python
def handle_missing_values(factor_data, method='median', threshold=0.3):
    """
    处理缺失�?

    Parameters:
    -----------
    factor_data : pd.DataFrame
        因子数据
    method : str
        处理方法: 'drop', 'median', 'mean', 'ffill', 'industry_median'
    threshold : float
        缺失比例阈值，超过则删�?
    """
    missing_ratio = factor_data.isna().mean()

    if missing_ratio > threshold:
        return factor_data.dropna(axis=1)

    if method == 'median':
        return factor_data.fillna(factor_data.median())
    elif method == 'mean':
        return factor_data.fillna(factor_data.mean())
    elif method == 'ffill':
        return factor_data.fillna(method='ffill').fillna(method='bfill')
    elif method == 'industry_median':
        if 'industry' in factor_data.columns:
            return factor_data.groupby('industry').transform(
                lambda x: x.fillna(x.median())
            )

    return factor_data
```

---

## 3. 异常值处�?

### 3.1 检测方�?

| 方法 | 说明 | 阈�?|
|------|------|------|
| 3σ原则 | 正态分布假�?| mean±3*std |
| MAD | 绝对中位数法 | median±3*MAD |
| 分位�?| 非参数方�?| 1%�?9%分位 |

### 3.2 Python实现

```python
def handle_outliers(factor_data, method='mad', k=3):
    """
    处理异常�?

    Parameters:
    -----------
    factor_data : pd.Series
        因子数据
    method : str
        处理方法: 'mad', 'sigma', 'quantile'
    k : float
        异常值倍数
    """
    if method == 'sigma':
        mean = factor_data.mean()
        std = factor_data.std()
        lower = mean - k * std
        upper = mean + k * std

    elif method == 'mad':
        median = factor_data.median()
        mad = (factor_data - median).abs().median()
        lower = median - k * mad
        upper = median + k * mad

    elif method == 'quantile':
        lower = factor_data.quantile(0.01)
        upper = factor_data.quantile(0.99)

    return factor_data.clip(lower, upper)
```

---

## 4. 标准化处�?

### 4.1 常用方法

| 方法 | 公式 | 特点 |
|------|------|------|
| Z-score | (x-mean)/std | 均�?，标准差1 |
| Min-Max | (x-min)/(max-min) | 归一化到[0,1] |
| Rank | rank(x)/n | 分位数映�?|
|的行业中性化 | x - groupby_mean | 消除行业偏向 |

### 4.2 Python实现

```python
def standardize_factor(factor_data, method='zscore', groupby=None):
    """
    因子标准�?

    Parameters:
    -----------
    factor_data : pd.Series
        因子数据
    method : str
        标准化方�? 'zscore', 'minmax', 'rank', 'industry_neutral'
    groupby : str
        分组列名（如行业�?
    """
    if method == 'zscore':
        return (factor_data - factor_data.mean()) / factor_data.std()

    elif method == 'minmax':
        return (factor_data - factor_data.min()) / (factor_data.max() - factor_data.min())

    elif method == 'rank':
        return factor_data.rank(pct=True)

    elif method == 'industry_neutral':
        if groupby:
            return factor_data - factor_data.groupby(groupby).transform('mean')
        return factor_data - factor_data.mean()

    return factor_data
```

---

## 5. 预处理配�?

```python
PREPROCESSING_CONFIG = {
    'missing_values': {
        'method': 'median',
        'threshold': 0.3
    },
    'outliers': {
        'method': 'mad',
        'k': 3
    },
    'standardization': {
        'method': 'zscore',
        'groupby': 'industry'
    }
}
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
