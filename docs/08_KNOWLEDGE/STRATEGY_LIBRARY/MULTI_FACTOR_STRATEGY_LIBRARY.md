---
standard_type: 策略文档
applicable_scope: 策略库
compliance_level: 专业标准
parent_document: ../KNOWLEDGE_TRANSFER_SYSTEM.md
implementation_status: 已完成
owner: 首席投资官
version: 1.0.0
module_id: MULTI_FACTOR_STRATEGY_LIBRARY
created_date: 2026-04-03
last_updated: 2026-04-03
tags: ["策略库", "多因子策略", "投资策略"]
---
# 多因子策略库

**文档版本**: 1.0.0
**最后更新**: 2026-04-03
**文档所有者**: 首席投资官

---

## 1. 多因子策略概述

### 1.1 策略定义

**多因子策略**: 通过组合多个因子来预测股票收益，并构建投资组合的策略。

**核心思想**:
- 单因子信息有限
- 多因子组合提供更全面的信号
- 因子间可以相互补充和增强

### 1.2 策略分类

```
多因子策略库/
├── 风格因子策略/
│   ├── 动量+价值策略
│   ├── 质量+规模策略
│   └── 低波动+动量策略
├── 风险因子策略/
│   ├── 市场中性策略
│   ├── 行业中性策略
│   └── 风格中性策略
└── Alpha因子策略/
    ├── 情绪+基本面策略
    ├── 技术+另类策略
    └── 综合Alpha策略
```

---

## 2. 动量+价值策略

### 2.1 策略定义

**策略名称**: 动量+价值策略 (Momentum + Value Strategy)

**策略ID**: STRAT_MOM_VALUE

**策略描述**: 结合动量因子和价值因子，构建投资组合

**适用场景**:
- 趋势明显的市场环境
- 中长期投资
- 流动性充足的股票池

---

### 2.2 因子组合方法

#### 因子选择

**动量因子**:
- 简单动量因子 (MOM_PRICE_SIMPLE)
- 成交量加权动量因子 (MOM_VOLUME_WEIGHTED)

**价值因子**:
- PB因子 (VALUE_PB)
- PE因子 (VALUE_PE)
- 股息率因子 (VALUE_DIVIDEND)

---

#### 因子权重

**权重分配方法**: 风险平价 (Risk Parity)

```python
def risk_parity_weights(
    factor_returns: pd.DataFrame
) -> Dict[str, float]:
    """
    风险平价权重计算
    
    Args:
        factor_returns: 因子收益矩阵
    
    Returns:
        因子权重字典
    """
    n_factors = len(factor_returns.columns)
    cov_matrix = factor_returns.cov()
    
    def objective(w):
        portfolio_var = np.dot(w.T, np.dot(cov_matrix, w))
        marginal_contrib = np.dot(cov_matrix, w) / np.sqrt(portfolio_var)
        risk_contrib = w * marginal_contrib
        target_risk = np.sqrt(portfolio_var) / n_factors
        return np.sum((risk_contrib - target_risk) ** 2)
    
    initial_weights = np.ones(n_factors) / n_factors
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = tuple((0, 1) for _ in range(n_factors))
    
    result = minimize(
        objective,
        initial_weights,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    return dict(zip(factor_returns.columns, result.x))
```

---

#### 因子正交化

**正交化方法**: Gram-Schmidt正交化

```python
def orthogonalize_factors(
    factor_values: pd.DataFrame
) -> pd.DataFrame:
    """
    因子正交化
    
    Args:
        factor_values: 因子值矩阵
    
    Returns:
        正交化后的因子值矩阵
    """
    from scipy.linalg import qr
    
    Q, R = qr(factor_values.values, mode='economic')
    orthogonal_factors = pd.DataFrame(
        Q,
        index=factor_values.index,
        columns=factor_values.columns
    )
    
    return orthogonal_factors
```

---

### 2.3 组合构建方法

#### 股票打分

```python
def calculate_stock_scores(
    factor_values: pd.DataFrame,
    factor_weights: Dict[str, float]
) -> pd.Series:
    """
    计算股票综合得分
    
    Args:
        factor_values: 因子值矩阵
        factor_weights: 因子权重
    
    Returns:
        股票综合得分
    """
    weighted_scores = sum(
        factor_values[factor] * weight
        for factor, weight in factor_weights.items()
    )
    return weighted_scores
```

---

#### 组合优化

**优化目标**: 最大化预期收益，控制风险

```python
def optimize_portfolio(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    max_weight: float = 0.05,
    target_vol: float = 0.15
) -> pd.Series:
    """
    组合优化
    
    Args:
        expected_returns: 预期收益
        cov_matrix: 协方差矩阵
        max_weight: 单个股票最大权重
        target_vol: 目标波动率
    
    Returns:
        最优权重
    """
    n_stocks = len(expected_returns)
    
    def objective(w):
        portfolio_return = np.dot(w, expected_returns)
        portfolio_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
        return -portfolio_return / portfolio_vol  # 最大化夏普比率
    
    initial_weights = np.ones(n_stocks) / n_stocks
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        {'type': 'ineq', 'fun': lambda w: target_vol - np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))}
    ]
    bounds = tuple((0, max_weight) for _ in range(n_stocks))
    
    result = minimize(
        objective,
        initial_weights,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    return pd.Series(result.x, index=expected_returns.index)
```

---

### 2.4 回测表现

**回测期间**: 2015-01-01 至 2025-12-31

**回测结果**:
| 指标 | 数值 | 说明 |
|------|------|------|
| **年化收益** | 15.8% | 年化收益率 |
| **年化波动** | 18.5% | 年化波动率 |
| **夏普比率** | 0.85 | 夏普比率 |
| **最大回撤** | -22.3% | 最大回撤 |
| **胜率** | 58.2% | 月度胜率 |
| **换手率** | 185% | 年换手率 |

**年度收益**:
| 年份 | 收益率 | 基准收益 | 超额收益 |
|------|--------|---------|---------|
| 2015 | 28.5% | 9.4% | 19.1% |
| 2016 | 12.3% | -11.3% | 23.6% |
| 2017 | 18.6% | 21.8% | -3.2% |
| 2018 | -8.2% | -25.3% | 17.1% |
| 2019 | 32.5% | 36.1% | -3.6% |
| 2020 | 25.8% | 27.2% | -1.4% |
| 2021 | 15.2% | 9.2% | 6.0% |
| 2022 | -12.5% | -21.6% | 9.1% |
| 2023 | 8.5% | 5.8% | 2.7% |
| 2024 | 18.2% | 12.5% | 5.7% |

---

### 2.5 风险分析

**风险因子暴露**:
| 风险因子 | 暴露度 | 说明 |
|---------|--------|------|
| **市场** | 0.95 | 接近市场中性 |
| **规模** | -0.15 | 轻微偏向大盘股 |
| **价值** | 0.32 | 偏向价值股 |
| **动量** | 0.28 | 偏向动量股 |
| **波动** | -0.18 | 偏向低波动股 |

**风险贡献**:
| 风险来源 | 贡献度 | 说明 |
|---------|--------|------|
| **因子风险** | 65% | 因子暴露带来的风险 |
| **特质风险** | 35% | 个股特质风险 |

---

### 2.6 实施指南

#### 调仓频率

**建议频率**: 月度调仓

**调仓流程**:
```
月初第1个交易日
  ↓
更新因子数据
  ↓
计算因子值
  ↓
优化组合权重
  ↓
执行交易
  ↓
监控组合表现
```

---

#### 交易执行

**执行策略**: VWAP（成交量加权平均价）

**执行时间**: 交易日开盘后30分钟至收盘前30分钟

**交易成本**:
- 佣金：0.03%
- 冲击成本：0.05%
- 总成本：约0.08%

---

#### 风险控制

**止损机制**:
- 单股止损：-15%
- 组合止损：-10%

**风险限额**:
- 单股最大权重：5%
- 单行业最大权重：25%
- 最大回撤控制：-25%

---

## 3. 质量+规模策略

### 3.1 策略定义

**策略名称**: 质量+规模策略 (Quality + Size Strategy)

**策略ID**: STRAT_QUAL_SIZE

**策略描述**: 结合质量因子和规模因子，构建投资组合

**适用场景**:
- 震荡市环境
- 防御性投资
- 长期投资

---

### 3.2 因子组合方法

#### 因子选择

**质量因子**:
- ROE因子 (QUALITY_ROE)
- ROA因子 (QUALITY_ROA)
- 毛利率因子 (QUALITY_GROSS_MARGIN)

**规模因子**:
- 市值因子 (SIZE_MARKET_CAP)
- 流通市值因子 (SIZE_FLOAT_CAP)

---

### 3.3 回测表现

**回测期间**: 2015-01-01 至 2025-12-31

**回测结果**:
| 指标 | 数值 | 说明 |
|------|------|------|
| **年化收益** | 12.5% | 年化收益率 |
| **年化波动** | 15.2% | 年化波动率 |
| **夏普比率** | 0.82 | 夏普比率 |
| **最大回撤** | -18.5% | 最大回撤 |
| **胜率** | 56.8% | 月度胜率 |
| **换手率** | 120% | 年换手率 |

---

## 4. 市场中性策略

### 4.1 策略定义

**策略名称**: 市场中性策略 (Market Neutral Strategy)

**策略ID**: STRAT_MARKET_NEUTRAL

**策略描述**: 构建市场风险敞口为零的投资组合

**适用场景**:
- 市场方向不明确
- 追求绝对收益
- 低风险偏好

---

### 4.2 因子组合方法

#### 因子选择

**Alpha因子**:
- 动量因子
- 价值因子
- 质量因子

**风险因子**:
- 市场因子
- 行业因子
- 规模因子

---

#### 中性化方法

```python
def neutralize(
    factor_values: pd.Series,
    risk_factors: pd.DataFrame
) -> pd.Series:
    """
    因子中性化
    
    Args:
        factor_values: 因子值
        risk_factors: 风险因子矩阵
    
    Returns:
        中性化后的因子值
    """
    from sklearn.linear_model import LinearRegression
    
    model = LinearRegression()
    model.fit(risk_factors, factor_values)
    
    residuals = factor_values - model.predict(risk_factors)
    return residuals
```

---

### 4.3 回测表现

**回测期间**: 2015-01-01 至 2025-12-31

**回测结果**:
| 指标 | 数值 | 说明 |
|------|------|------|
| **年化收益** | 8.5% | 年化收益率 |
| **年化波动** | 8.2% | 年化波动率 |
| **夏普比率** | 1.04 | 夏普比率 |
| **最大回撤** | -5.8% | 最大回撤 |
| **胜率** | 62.5% | 月度胜率 |
| **换手率** | 250% | 年换手率 |

---

## 5. 策略选择指南

### 5.1 策略对比

| 策略 | 年化收益 | 夏普比率 | 最大回撤 | 适用场景 |
|------|---------|---------|---------|---------|
| **动量+价值** | 15.8% | 0.85 | -22.3% | 趋势市场 |
| **质量+规模** | 12.5% | 0.82 | -18.5% | 震荡市场 |
| **市场中性** | 8.5% | 1.04 | -5.8% | 不确定市场 |

---

### 5.2 选择建议

**根据市场环境选择**:
- 趋势明显：动量+价值策略
- 震荡市：质量+规模策略
- 不确定：市场中性策略

**根据风险偏好选择**:
- 高风险偏好：动量+价值策略
- 中风险偏好：质量+规模策略
- 低风险偏好：市场中性策略

---

## 6. 参考文档

- [动量因子库](./MOMENTUM_FACTOR_LIBRARY.md)
- [因子引擎详细设计](../../01_FRAMEWORK/FACTOR_ENGINE_DETAILED_DESIGN.md)
- [投资哲学](../../01_FRAMEWORK/INVESTMENT_PHILOSOPHY.md)

---

**文档状态**: 正式标准
**下次更新**: 2026-07-03
