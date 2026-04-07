---
module_id: BARRA_STYLE_FACTORS
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: BARRA_STYLE_FACTORS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
responsibility:
  - 因子研究与管理框架设计与优化维护
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---
---



# T.03.RF001.Barra风格因子（A股适配版）
> **核心职责**: Barra风格因子体系定义（A股适配版），涉及风格因子
> **职责边界**: 
> - ✅ 本文档负责：Barra风格因子体系定义（A股适配版）相关内容
> - ❌ 本文档不负责：其他模块内容


> Barra风格因子体系（A股适配?
>
> **配套文档**?
> - 主文档：[../../INDEX.md](../../03_TRADING_TACTICS/INDEX.md)
> - 因子库索引：[../../04_DATA_SOURCE/iFind/FACTOR_MASTER_INDEX.md](02_FACTOR_LIBRARY/04_DATA_SOURCE/factor_master_index.md)
> - 风险因子：[风险因子 README](API_README.md)

***

## 1. 因子概述

| 属?| 内容 |
|------|------|
| 因子编号 | T.03.RF001 |
| 因子名称 | Barra风格因子（A股适配?|
| 因子类型 | 风险因子 |
| 因子数量 | 10?|
| 数据来源 | Baostock / AkShare |

**核心理念**：对标MSCI Barra全球机构标准，补充A股适用?0个核心风格因子，用于风险管理和因子归?

**适用场景**：组合风险控制、因子中性化、风险归因分?

***

## 2. 十大风格因子定义

| 因子名称 | 英文?| 计算方法 | A股适用?|
|:---------|:-------|:---------|:----------|
| **规模因子** | SIZE | Ln(流通市? | ?直接使用 |
| **价值因?* | VALUE | PB倒数 + PE倒数 + 股息?| ?直接使用 |
| **动量因子** | MOM | 过去12个月收益率（剔除最?个月?| ?直接使用 |
| **质量因子** | QUAL | ROE + ROA + 资产负债率 | ?直接使用 |
| **低波动因?* | VOL | 过去252日收益波动率倒数 | ?直接使用 |
| **成长因子** | GROW | 净利润增?+ 营收增?| ?直接使用 |
| **盈利因子** | EARN | 毛利?+ 净利率 | ?直接使用 |
| **杠杆因子** | LEVER | 资产负债率 + 权益乘数 | ?直接使用 |
| **流动性因?* | LIQUID | 日均成交?流通市?| ?直接使用 |
| **股息因子** | YIELD | ?2个月股息?| ?直接使用 |

***

## 3. 因子计算公式

### 3.1 规模因子（SIZE?

```python
def calc_size_factor(stock_df):
    """
    规模因子：Ln(流通市?

    Returns:
        float: 市值对数?
    """
    float_market_cap = stock_df['close'] * stock_df['float_volume']
    size_factor = np.log(float_market_cap)
    return size_factor

def neutralize_size(factor_value, market_cap):
    """
    市值中性化处理

    使用市值对因子进行回归，残差作为中性化后的因子?
    """
    from sklearn.linear_model import LinearRegression

    X = np.log(market_cap).values.reshape(-1, 1)
    y = factor_value.values
    lr = LinearRegression()
    lr.fit(X, y)
    residual = y - lr.predict(X)
    return residual
```

### 3.2 价值因子（VALUE?

```python
def calc_value_factor(stock_df):
    """
    价值因子：PB倒数 + PE倒数 + 股息?

    Returns:
        float: 合成价值因?
    """
    pb_inverse = 1 / stock_df['pb']
    pe_inverse = np.where(stock_df['pe'] > 0, 1 / stock_df['pe'], 0)
    dividend_yield = stock_df['dividend_yield']

    value_factor = (pb_inverse + pe_inverse + dividend_yield) / 3

    return value_factor
```

### 3.3 动量因子（MOM?

```python
def calc_momentum_factor(price_df, lookback=252, skip=20):
    """
    动量因子：过?2个月收益率（剔除最?个月?

    注意：A股有涨跌停限制，需特殊处理

    Returns:
        DataFrame: 动量因子值（标准化）
    """
    cum_ret = price_df['close'] / price_df['close'].shift(lookback - skip)
    cum_ret = cum_ret.shift(skip)
    mom_factor = (cum_ret - cum_ret.mean()) / cum_ret.std()

    return mom_factor
```

### 3.4 质量因子（QUAL?

```python
def calc_quality_factor(fundamental_df):
    """
    质量因子：ROE + ROA + 资产负债率

    Returns:
        float: 合成质量因子
    """
    roe = fundamental_df['net_profit'] / fundamental_df['equity']
    roa = fundamental_df['net_profit'] / fundamental_df['total_assets']
    leverage = -fundamental_df['total_liabilities'] / fundamental_df['total_assets']

    quality_factor = (roe + roa + leverage) / 3

    return quality_factor
```

### 3.5 低波动因子（VOL?

```python
def calc_low_volatility_factor(price_df, lookback=252):
    """
    低波动因子：波动率倒数

    Returns:
        float: 低波动因子（负值，与收益正相关?
    """
    daily_returns = price_df['close'].pct_change()
    historical_vol = daily_returns.rolling(lookback).std()
    low_vol_factor = -1 / historical_vol

    return low_vol_factor
```

### 3.6 成长因子（GROW?

```python
def calc_growth_factor(fundamental_df):
    """
    成长因子：净利润增?+ 营收增?

    Returns:
        float: 合成成长因子
    """
    net_profit_growth = (
        (fundamental_df['net_profit'] - fundamental_df['net_profit'].shift(4)) /
        fundamental_df['net_profit'].shift(4)
    )

    revenue_growth = (
        (fundamental_df['revenue'] - fundamental_df['revenue'].shift(4)) /
        fundamental_df['revenue'].shift(4)
    )

    growth_factor = (net_profit_growth + revenue_growth) / 2

    return growth_factor
```

### 3.7 盈利因子（EARN?

```python
def calc_earnings_factor(fundamental_df):
    """
    盈利因子：毛利率 + 净利率

    Returns:
        float: 合成盈利因子
    """
    gross_margin = (
        (fundamental_df['revenue'] - fundamental_df['cost']) /
        fundamental_df['revenue']
    )

    net_margin = fundamental_df['net_profit'] / fundamental_df['revenue']

    earnings_factor = (gross_margin + net_margin) / 2

    return earnings_factor
```

### 3.8 杠杆因子（LEVER?

```python
def calc_leverage_factor(fundamental_df):
    """
    杠杆因子：资产负债率 + 权益乘数（负向）

    Returns:
        float: 杠杆因子（负向指标）
    """
    debt_ratio = fundamental_df['total_liabilities'] / fundamental_df['total_assets']
    equity_multiplier = fundamental_df['total_assets'] / fundamental_df['equity']
    leverage_factor = -(debt_ratio + equity_multiplier) / 2

    return leverage_factor
```

### 3.9 流动性因子（LIQUID?

```python
def calc_liquidity_factor(trading_df, lookback=20):
    """
    流动性因子：日均成交?/ 流通市?

    Returns:
        float: 流动性因?
    """
    avg_daily_amount = trading_df['amount'].rolling(lookback).mean()
    float_market_cap = trading_df['close'] * trading_df['float_volume']
    liquidity_factor = avg_daily_amount / float_market_cap

    return liquidity_factor
```

### 3.10 股息因子（YIELD?

```python
def calc_dividend_factor(stock_df):
    """
    股息因子：近12个月股息?

    Returns:
        float: 股息因子
    """
    dividend_yield = stock_df['dividend_yield_ttm']
    return dividend_yield
```

***

## 4. 因子权重配置

| 因子 | 推荐权重 | 权重说明 |
|:-----|:---------|:---------|
| SIZE | 5% | 规模分散?|
| VALUE | 15% | 价值投资核?|
| MOM | 20% | 动量效应最?|
| QUAL | 15% | 质量选股核心 |
| VOL | 10% | 低波动稳?|
| GROW | 10% | 成长性配?|
| EARN | 5% | 盈利辅助 |
| LEVER | 5% | 杠杆参?|
| LIQUID | 10% | 流动性风?|
| YIELD | 5% | 股息收益 |

***

## 5. 因子正交化处?

```python
def orthogonalize_factors(factor_df, factor_list):
    """
    因子正交化处?

    按Barra标准依次正交化，后验因子对先验因子正?
    """
    from sklearn.linear_model import LinearRegression

    result_df = factor_df.copy()

    ortho_order = [
        'SIZE', 'VALUE', 'MOM', 'QUAL', 'VOL',
        'GROW', 'EARN', 'LEVER', 'LIQUID', 'YIELD'
    ]

    for i, factor in enumerate(ortho_order):
        if factor not in factor_list:
            continue

        for j in range(i + 1, len(ortho_order)):
            next_factor = ortho_order[j]
            if next_factor not in factor_list:
                continue

            X = result_df[factor].values.reshape(-1, 1)
            y = result_df[next_factor].values

            lr = LinearRegression()
            lr.fit(X, y)
            residual = y - lr.predict(X)

            result_df[next_factor] = residual

    return result_df
```

***

## 6. Python实现

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class BarraStyleFactors:
    """
    Barra风格因子计算器（A股适配版）
    对标MSCI Barra全球机构标准
    """

    FACTORS = ['SIZE', 'VALUE', 'MOM', 'QUAL', 'VOL',
               'GROW', 'EARN', 'LEVER', 'LIQUID', 'YIELD']

    DEFAULT_WEIGHTS = {
        'SIZE': 0.05,
        'VALUE': 0.15,
        'MOM': 0.20,
        'QUAL': 0.15,
        'VOL': 0.10,
        'GROW': 0.10,
        'EARN': 0.05,
        'LEVER': 0.05,
        'LIQUID': 0.10,
        'YIELD': 0.05
    }

    def __init__(self):
        self.name = "Barra风格因子"
        self.factor_code = "T.03.RF001"

    def calculate_all_factors(
        self,
        price_df: pd.DataFrame,
        fundamental_df: pd.DataFrame,
        trading_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        计算所有风格因?

        Parameters:
            price_df: 价格数据（包含OHLCV?
            fundamental_df: 财务数据
            trading_df: 交易数据

        Returns:
            DataFrame: 各因子?
        """
        factors = {}

        factors['SIZE'] = self.calc_size_factor(trading_df)
        factors['VALUE'] = self.calc_value_factor(fundamental_df)
        factors['MOM'] = self.calc_momentum_factor(price_df)
        factors['QUAL'] = self.calc_quality_factor(fundamental_df)
        factors['VOL'] = self.calc_low_volatility_factor(price_df)
        factors['GROW'] = self.calc_growth_factor(fundamental_df)
        factors['EARN'] = self.calc_earnings_factor(fundamental_df)
        factors['LEVER'] = self.calc_leverage_factor(fundamental_df)
        factors['LIQUID'] = self.calc_liquidity_factor(trading_df)
        factors['YIELD'] = self.calc_dividend_factor(fundamental_df)

        return pd.DataFrame(factors)

    def calc_size_factor(self, df: pd.DataFrame) -> pd.Series:
        """规模因子"""
        float_market_cap = df['close'] * df['float_volume']
        return np.log(float_market_cap)

    def calc_value_factor(self, df: pd.DataFrame) -> pd.Series:
        """价值因?""
        pb_inverse = 1 / df['pb'].replace(0, np.nan)
        pe_inverse = np.where(df['pe'] > 0, 1 / df['pe'].replace(0, np.nan), 0)
        dividend_yield = df['dividend_yield']
        return (pb_inverse.fillna(0) + pe_inverse + dividend_yield.fillna(0)) / 3

    def calc_momentum_factor(self, df: pd.DataFrame, lookback=252, skip=20) -> pd.Series:
        """动量因子"""
        cum_ret = df['close'] / df['close'].shift(lookback - skip)
        cum_ret = cum_ret.shift(skip)
        return (cum_ret - cum_ret.mean()) / cum_ret.std()

    def calc_quality_factor(self, df: pd.DataFrame) -> pd.Series:
        """质量因子"""
        roe = df['net_profit'] / df['equity'].replace(0, np.nan)
        roa = df['net_profit'] / df['total_assets'].replace(0, np.nan)
        leverage = -df['total_liabilities'] / df['total_assets'].replace(0, np.nan)
        return (roe.fillna(0) + roa.fillna(0) + leverage.fillna(0)) / 3

    def calc_low_volatility_factor(self, df: pd.DataFrame, lookback=252) -> pd.Series:
        """低波动因?""
        daily_returns = df['close'].pct_change()
        historical_vol = daily_returns.rolling(lookback).std()
        return -1 / historical_vol

    def calc_growth_factor(self, df: pd.DataFrame) -> pd.Series:
        """成长因子"""
        net_profit_growth = (
            (df['net_profit'] - df['net_profit'].shift(4)) /
            df['net_profit'].shift(4).replace(0, np.nan)
        )
        revenue_growth = (
            (df['revenue'] - df['revenue'].shift(4)) /
            df['revenue'].shift(4).replace(0, np.nan)
        )
        return (net_profit_growth.fillna(0) + revenue_growth.fillna(0)) / 2

    def calc_earnings_factor(self, df: pd.DataFrame) -> pd.Series:
        """盈利因子"""
        gross_margin = (
            (df['revenue'] - df['cost']) /
            df['revenue'].replace(0, np.nan)
        )
        net_margin = df['net_profit'] / df['revenue'].replace(0, np.nan)
        return (gross_margin.fillna(0) + net_margin.fillna(0)) / 2

    def calc_leverage_factor(self, df: pd.DataFrame) -> pd.Series:
        """杠杆因子"""
        debt_ratio = df['total_liabilities'] / df['total_assets'].replace(0, np.nan)
        equity_multiplier = df['total_assets'] / df['equity'].replace(0, np.nan)
        return -(debt_ratio.fillna(0) + equity_multiplier.fillna(0)) / 2

    def calc_liquidity_factor(self, df: pd.DataFrame, lookback=20) -> pd.Series:
        """流动性因?""
        avg_daily_amount = df['amount'].rolling(lookback).mean()
        float_market_cap = df['close'] * df['float_volume']
        return avg_daily_amount / float_market_cap

    def calc_dividend_factor(self, df: pd.DataFrame) -> pd.Series:
        """股息因子"""
        return df['dividend_yield_ttm'].fillna(0)
```

***

## 7. 使用示例

```python
# 初始?
barra = BarraStyleFactors()

# 计算所有因?
factors_df = barra.calculate_all_factors(
    price_df=price_data,
    fundamental_df=fundamental_data,
    trading_df=trading_data
)

# 正交化处?
orthogonalized = orthogonalize_factors(factors_df, BarraStyleFactors.FACTORS)

# 标准?
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
factors_standardized = scaler.fit_transform(orthogonalized)

print(f"因子数量: {len(BarraStyleFactors.FACTORS)}")
print(f"因子列表: {BarraStyleFactors.FACTORS}")
```

***

## 8. IC/IR验证

```python
def calc_factor_ic(factor_df, return_df, lookback=12):
    """
    计算因子IC值（信息系数?

    IC = correlation(factor, forward_return)
    """
    from scipy.stats import spearmanr

    ic_list = []
    for date in factor_df.index[lookback:]:
        factor = factor_df.loc[:date].iloc[-1]
        forward_ret = return_df.loc[date]

        ic, _ = spearmanr(factor.dropna(), forward_ret.dropna())
        ic_list.append({'date': date, 'ic': ic})

    return pd.DataFrame(ic_list)

def calc_factor_ir(factor_df, return_df, lookback=12, half_life=6):
    """
    计算因子IR值（信息比率?

    IR = mean(IC) / std(IC)
    """
    ic_series = calc_factor_ic(factor_df, return_df, lookback)['ic']

    ic_mean = ic_series.ewm(halflife=half_life).mean().iloc[-1]
    ic_std = ic_series.ewm(halflife=half_life).std().iloc[-1]

    ir = ic_mean / ic_std if ic_std != 0 else 0

    return ir
```

**IC/IR评判标准**?
| IC | IR | 评价 |
|----|-----|------|
| >0.05 | >0.5 | 优秀 |
| 0.03-0.05 | 0.3-0.5 | 良好 |
| 0.01-0.03 | 0.1-0.3 | 一?|
| <0.01 | <0.1 | 失效 |

***

## 9. 注意事项

1. **数据处理**：负PE/零PE需要特殊处?
2. **缺失?*：使用前fillna(0)处理
3. **标准?*：多因子合成前需要Z-score标准?
4. **中性化**：市值中性化是Barra标准流程

***

## 10. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本，整合附录AF Barra风格因子体系 |

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
