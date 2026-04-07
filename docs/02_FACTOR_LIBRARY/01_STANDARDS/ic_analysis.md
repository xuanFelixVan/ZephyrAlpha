---
module_id: IC_ANALYSIS
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - IC分析体系文档
---

﻿---
module_id: STANDARDS_IC_ANALYSIS_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 因子研究与管理框架设计与优化维护
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?---



# IC分析体系
> **核心职责**: IC分析方法和评估标准，涉及分析体系
> **职责边界**: 
> - ✅ 本文档负责：IC分析方法和评估标准相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容


> 信息系数(IC)分析方法与标?

---

## 1. IC概述

### 1.1 定义
IC（Information Coefficient）表示因子预测值与下期收益率的相关系数?

### 1.2 计算公式

$$IC = \text{corr}(Factor_{rank}, Return_{t+1})$$

---

## 2. IC指标体系

### 2.1 指标定义

| 指标 | 计算方法 | 说明 |
|------|----------|------|
| IC均?| mean(IC序列) | 因子预测能力 |
| IC标准?| std(IC序列) | 因子稳定?|
| ICIR | IC均?IC标准?| 风险调整后的IC |
| IC胜率 | IC>0的比?| 预测方向准确?|
| IC衰减?| 不同滞后期IC | 因子有效?|

### 2.2 IC评判标准

| ICIR范围 | 因子评价 |
|----------|----------|
| ICIR > 1.0 | 优秀 |
| 0.5 < ICIR ?1.0 | 良好 |
| 0.3 < ICIR ?0.5 | 一?|
| ICIR ?0.3 | 较差 |

---

## 3. IC分析流程

### 3.1 日频IC计算

```python
import pandas as pd
import numpy as np

def calculate_daily_ic(factor_df, return_df, lag=1):
    """
    计算日频IC

    Parameters:
    -----------
    factor_df : pd.DataFrame
        因子值，index为日期，columns为股票代?
    return_df : pd.DataFrame
        收益率，index为日期，columns为股票代?
    lag : int
        滞后期数

    Returns:
    --------
    pd.Series: IC序列
    """
    aligned_factor = factor_df.shift(lag)
    ic_series = []

    for date in aligned_factor.index:
        factor_rank = aligned_factor.loc[date].rank(pct=True)
        forward_return = return_df.loc[date] if date in return_df.index else None

        if forward_return is not None:
            ic = factor_rank.corr(forward_return, method='spearman')
            ic_series.append({'date': date, 'ic': ic})

    return pd.DataFrame(ic_series).set_index('date')['ic']
```

### 3.2 IC统计汇?

```python
def ic_statistics(ic_series):
    """IC统计汇?""
    return {
        'IC均?: ic_series.mean(),
        'IC标准?: ic_series.std(),
        'ICIR': ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0,
        'IC胜率': (ic_series > 0).mean(),
        'IC最大?: ic_series.max(),
        'IC最小?: ic_series.min(),
        'IC大于0.02比例': (ic_series.abs() > 0.02).mean()
    }
```

---

## 4. IC衰减分析

### 4.1 滞后期IC

| 滞后?| IC含义 |
|--------|--------|
| IC_1 | 1期滞后IC |
| IC_5 | 5期滞后IC |
| IC_10 | 10期滞后IC |

### 4.2 衰减评判

- IC_1 vs IC_5 衰减 < 30%：因子有效期较长
- IC_1 vs IC_10 衰减 > 50%：因子偏向短?

---

## 5. IC分析报告模板

```markdown
## {因子名称} IC分析报告

### 基本信息
- 因子ID: {ID}
- 分析区间: {start} - {end}
- 股票? {pool}
- 频率: {freq}

### IC统计

| 指标 | ?|
|------|-----|
| IC均?| {value} |
| IC标准?| {value} |
| ICIR | {value} |
| 胜率 | {value} |

### IC时序?
![IC时序图] (已移? path/to/ic_plot.png)

### 结论
- {conclusion}
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
