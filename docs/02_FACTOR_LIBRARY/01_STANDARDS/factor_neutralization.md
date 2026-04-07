﻿---
module_id: FACTOR_NEUTRALIZATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
responsibility:
  - 因子计算、因子库管理
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---
---



# 因子中性化处理
> **核心职责**: 因子中性化方法和标准，涉及因子中性化处理
> **职责边界**: 
> - ✅ 本文档负责：因子中性化方法和标准相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容


> 行业中性化、市值中性化、风格中性化
>
> **版本**: v1.0
> **更新**: 2026-03-28
> **优先?*: P1 - 核心模块
> **Layer**: Layer 2 (因子?
> **索引**: F.04.NEU.001

---

## 1. 概述

因子中性化是为了消除因子中混入的风格暴露，使因子反映真正独特的Alpha信息?

**常见中性化类型**?
- 行业中性化：消除行业偏?
- 市值中性化：消除大?小盘偏见
- 风格中性化：消除其他风格因子影?

---

## 2. 中性化方法

### 2.1 回归中性化

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class FactorNeutralizer:
    """因子中性化处理?""

    def neutralize(
        self,
        factor: pd.Series,
        style_factors: pd.DataFrame,
        market_cap: pd.Series = None
    ) -> pd.Series:
        """
        对因子进行风格中性化

        Parameters:
        -----------
        factor : pd.Series
            待中性化的因?
        style_factors : pd.DataFrame
            风格因子（如Barra风格因子?
        market_cap : pd.Series
            市值因?

        Returns:
        --------
        pd.Series: 中性化后的因子
        """
        # 合并所有控制变?
        controls = style_factors.copy()

        if market_cap is not None:
            controls['log_market_cap'] = np.log(market_cap)

        # 对齐数据
        aligned_factor, aligned_controls = factor.align(controls, join='inner')

        # 去除缺失?
        valid_idx = aligned_factor.notna() & aligned_controls.notna().all(axis=1)
        valid_factor = aligned_factor[valid_idx]
        valid_controls = aligned_controls[valid_idx]

        # 回归取残?
        residual = self._regression_residual(valid_factor, valid_controls)

        # 重建完整序列
        result = pd.Series(np.nan, index=factor.index)
        result[valid_idx] = residual

        return result

    def _regression_residual(
        self,
        y: pd.Series,
        X: pd.DataFrame
    ) -> pd.Series:
        """多元回归残差"""
        X_arr = np.column_stack([np.ones(len(X)), X.values])
        y_arr = y.values

        # 最小二?
        coeffs = np.linalg.lstsq(X_arr, y_arr, rcond=None)[0]

        # 预测?
        y_pred = X_arr @ coeffs

        # 残差
        return pd.Series(y_arr - y_pred, index=y.index)
```

---

## 3. 行业中性化

### 3.1 行业分类映射

```python
class IndustryNeutralizer:
    """行业中性化处理?""

    # 申万行业一级分?
    INDUSTRY_CODES = {
        801010: '农林牧渔',
        801020: '采掘',
        801030: '化工',
        801040: '钢铁',
        801050: '有色金属',
        801060: '电子',
        801070: '汽车',
        801080: '家用电器',
        801090: '食品饮料',
        801100: '纺织服装',
        801110: '轻工制?,
        801120: '医药生物',
        801130: '公用事业',
        801140: '交通运?,
        801150: '房地?,
        801160: '商业贸易',
        801170: '休闲服务',
        801180: '银行',
        801190: '非银金融',
        801200: '建筑材料',
        801210: '建筑装饰',
        801220: '电气设备',
        801230: '国防军工',
        801010: '计算?,
        801250: '传媒',
        801260: '通信'
    }

    def neutralize_by_industry(
        self,
        factor: pd.Series,
        industry: pd.Series
    ) -> pd.Series:
        """
        行业中性化：每行业内取因子排名百分位减均?

        Returns:
        --------
        pd.Series: 行业中性化后的因子
        """
        aligned_factor, aligned_industry = factor.align(industry, join='inner')

        # 计算每个行业的因子均?
        industry_means = aligned_factor.groupby(aligned_industry).transform('mean')

        # 残差 = 原始?- 行业均?
        neutralized = aligned_factor - industry_means

        return neutralized

    def neutralize_within_industry(
        self,
        factor: pd.Series,
        industry: pd.Series,
        style_controls: pd.DataFrame = None
    ) -> pd.Series:
        """
        行业内中性化：先行业内回归市值等风格因子，再在全市场回归行业哑变?
        """
        # 步骤1：行业内回归风格因子取残?
        if style_controls is not None:
            factor = self._within_industry_regression(factor, industry, style_controls)

        # 步骤2：全市场回归行业因子
        return self.neutralize_by_industry(factor, industry)

    def _within_industry_regression(
        self,
        factor: pd.Series,
        industry: pd.Series,
        style_controls: pd.DataFrame
    ) -> pd.Series:
        """行业内回归风格因?""
        aligned_factor, aligned_industry = factor.align(industry, join='inner')
        aligned_controls, _ = style_controls.align(aligned_factor, join='inner')

        result = pd.Series(np.nan, index=factor.index)

        for ind_code in aligned_industry.unique():
            ind_mask = aligned_industry == ind_code

            ind_factor = aligned_factor[ind_mask]
            ind_controls = aligned_controls[ind_mask]

            valid = ind_factor.notna() & ind_controls.notna().all(axis=1)

            if valid.sum() < 10:
                continue

            residual = self._regression_residual(
                ind_factor[valid],
                ind_controls[valid]
            )
            result[ind_mask & valid.index] = residual

        return result
```

---

## 4. 市值中性化

### 4.1 对数市值中性化

```python
class MarketCapNeutralizer:
    """市值中性化处理?""

    def neutralize(
        self,
        factor: pd.Series,
        market_cap: pd.Series
    ) -> pd.Series:
        """
        市值中性化：对数市值回归取残差

        Returns:
        --------
        pd.Series: 市值中性化后的因子
        """
        aligned_factor, aligned_mktcap = factor.align(market_cap, join='inner')

        # 对数市?
        log_mktcap = np.log(aligned_mktcap)

        # 回归
        valid = aligned_factor.notna() & log_mktcap.notna()
        residual = self._regression_residual(
            aligned_factor[valid],
            log_mktcap[valid].to_frame()
        )

        result = pd.Series(np.nan, index=factor.index)
        result[valid] = residual

        return result

    def _regression_residual(self, y: pd.Series, X: pd.DataFrame) -> pd.Series:
        X_arr = np.column_stack([np.ones(len(X)), X.values])
        y_arr = y.values
        coeffs = np.linalg.lstsq(X_arr, y_arr, rcond=None)[0]
        y_pred = X_arr @ coeffs
        return pd.Series(y_arr - y_pred, index=y.index)
```

---

## 5. Barra风格中性化

### 5.1 Barra CNE6风格因子

```python
class BarraNeutralizer:
    """Barra风格因子中性化"""

    # Barra CNE6 风格因子
    STYLE_FACTORS = [
        'size',           # 市值因?
        'beta',           # Beta因子
        'momentum',       # 动量因子
        'earning_yield',  # 盈利因子
        'volatility',     # 波动率因?
        'growth',         # 成长因子
        'value',          # 价值因?
        'leverage',       # 杠杆因子
        'liquiditiy',     # 流动性因?
        'dividend_yield'  # 股息率因?
    ]

    def neutralize(
        self,
        factor: pd.Series,
        barra_factors: pd.DataFrame,
        industry_dummies: pd.DataFrame = None
    ) -> pd.Series:
        """
        Barra风格中性化

        Parameters:
        -----------
        factor : pd.Series
            待中性化的因?
        barra_factors : pd.DataFrame
            Barra风格因子
        industry_dummies : pd.DataFrame
            行业哑变?

        Returns:
        --------
        pd.Series: 中性化后的因子
        """
        # 合并控制变量
        controls = barra_factors.copy()

        if industry_dummies is not None:
            controls = pd.concat([controls, industry_dummies], axis=1)

        # 回归中性化
        return FactorNeutralizer().neutralize(factor, controls)

    def create_industry_dummies(
        self,
        industry: pd.Series
    ) -> pd.DataFrame:
        """
        创建行业哑变?

        Returns:
        --------
        pd.DataFrame: 行业哑变量矩?
        """
        return pd.get_dummies(industry, prefix='ind', drop_first=True)
```

---

## 6. 标准化处?

### 6.1 中性化后标准化

```python
class NeutralizedFactorProcessor:
    """中性化因子处理?""

    def process(
        self,
        factor: pd.Series,
        industry: pd.Series = None,
        market_cap: pd.Series = None,
        barra_factors: pd.DataFrame = None
    ) -> pd.Series:
        """
        完整中性化处理流程

        流程?
        1. 去极?
        2. 缺失值填?
        3. 行业中性化
        4. 市值中性化
        5. 标准?
        """
        result = factor.copy()

        # 1. 去极值（3倍标准差?
        result = self._winsorize(result, n_std=3)

        # 2. 缺失值填充（行业均值）
        if industry is not None:
            aligned_industry, _ = industry.align(result, join='inner')
            result = result.fillna(result.groupby(aligned_industry).transform('mean'))
        result = result.fillna(result.mean())

        # 3. 行业中性化
        if industry is not None:
            result = IndustryNeutralizer().neutralize_by_industry(result, industry)

        # 4. 市值中性化
        if market_cap is not None:
            result = MarketCapNeutralizer().neutralize(result, market_cap)

        # 5. 标准?z-score)
        result = (result - result.mean()) / result.std()

        return result

    def _winsorize(self, series: pd.Series, n_std: float = 3) -> pd.Series:
        """去极值（3倍标准差截断?""
        mean = series.mean()
        std = series.std()

        upper = mean + n_std * std
        lower = mean - n_std * std

        return series.clip(lower, upper)
```

---

## 7. 配置模板

```yaml
# config/factor_neutralization.yaml
factor_neutralization:
  # 中性化步骤配置
  steps:
    - name: "winsorize"
      enabled: true
      params:
        n_std: 3

    - name: "fill_missing"
      enabled: true
      method: "industry_mean"

    - name: "industry_neutral"
      enabled: true
      method: "regression"  # regression | demean

    - name: "market_cap_neutral"
      enabled: true
      method: "log_regression"

    - name: "barra_style_neutral"
      enabled: false
      factors:
        - "size"
        - "beta"
        - "momentum"
        - "earning_yield"
        - "volatility"
        - "growth"
        - "value"

    - name: "standardize"
      enabled: true
      method: "zscore"

  # 行业分类
  industry:
    source: "sw"  # 申万一?
    level: 1      # 1??
```

---

## 8. 目录位置

```
02_FACTOR_LIBRARY/01_STANDARDS/
├── README.md
├── IC_ANALYSIS.md              # IC分析
├── FACTOR_PREPROCESSING.md     # 因子预处?
├── FACTOR_RETURN_ANALYSIS.md   # 因子收益率分?
└── FACTOR_NEUTRALIZATION.md   # 本文??
```

---

## 9. 接口定义

| 接口 | 说明 |
|------|------|
| **上游接口** | 因子计算引擎、因子预处理 |
| **下游接口** | 因子IC分析、因子收益率分析 |
| **输入格式** | factor: pd.Series, industry: pd.Series, market_cap: pd.Series |
| **输出格式** | pd.Series (中性化后的因子) |

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
