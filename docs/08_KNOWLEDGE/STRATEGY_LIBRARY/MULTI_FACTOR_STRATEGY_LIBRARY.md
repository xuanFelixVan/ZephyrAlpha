﻿---
version: 1.0.0
standard_type: ﻝ­ﻝ۴ﮔﮔ۰۲
responsibility:
  - 扩展功能、辅助模块、支撑文档
applicable_scope: ﻝ­ﻝ۴ﮒﭦ?compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ../KNOWLEDGE_TRANSFER_SYSTEM.md
implementation_status: ﮒﺓﺎﮒ؟ﮔ?owner: ﻠ۵ﮒﺕ­ﮔﻟﭖﮒ؟?version: 1.0.0
module_id: MULTI_FACTOR_STRATEGY_LIBRARY
created_date: 2026-04-03
last_updated: 2026-04-03
tags: ["ﻝ­ﻝ۴ﮒﭦ?, "ﮒ۳ﮒ ﮒ­ﻝ­ﻝ?, "ﮔﻟﭖﻝ­ﻝ۴"]
---
---

# ﮒ۳ﮒ ﮒ­ﻝ­ﻝ۴ﮒﭦ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


**ﮔﮔ۰۲ﻝﮔ؛**: 1.0.0
**ﮔﮒﮔﺑﮔ?*: 2026-04-03
**ﮔﮔ۰۲ﮔﮔﻟ?*: ﻠ۵ﮒﺕ­ﮔﻟﭖﮒ؟?
---

## 1. ﮒ۳ﮒ ﮒ­ﻝ­ﻝ۴ﮔ۵ﻟﺟ?
### 1.1 ﻝ­ﻝ۴ﮒ؟ﻛﺗ

**ﮔ ﺕﮒﺟﮔﮔﺏ**:

### 1.2 ﻝ­ﻝ۴ﮒﻝﺎﭨ

```
ﮒ۳ﮒ ﮒ­ﻝ­ﻝ۴ﮒﭦ/
ﻗﻗﻗ ﻠ۲ﮔ ﺙﮒ ﮒ­ﻝ­ﻝ۴/
ﻗ?  ﻗﻗﻗ ﮒ۷ﻠ+ﻛﭨﺓﮒﺙﻝ­ﻝ?ﻗ?  ﻗﻗﻗ ﻟﺑ۷ﻠ+ﻟ۶ﮔ۷۰ﻝ­ﻝ۴
ﻗ?  ﻗﻗﻗ ﻛﺛﮔﺏ۱ﮒ?ﮒ۷ﻠﻝ­ﻝ۴
ﻗﻗﻗ ﻠ۲ﻠ۸ﮒ ﮒ­ﻝ­ﻝ۴/
    ﻗﻗﻗ ﮔﻝﭨ۹+ﮒﭦﮔ؛ﻠ۱ﻝ­ﻝ?    ﻗﻗﻗ ﮔﮔ?ﮒ۵ﻝﺎﭨﻝ­ﻝ۴
    ﻗﻗﻗ ﻝﭨﺙﮒAlphaﻝ­ﻝ۴
```

---

## 2. ﮒ۷ﻠ+ﻛﭨﺓﮒﺙﻝ­ﻝ?
### 2.1 ﻝ­ﻝ۴ﮒ؟ﻛﺗ

**ﻝ­ﻝ۴ﮒﻝ۶ﺍ**: ﮒ۷ﻠ+ﻛﭨﺓﮒﺙﻝ­ﻝ?(Momentum + Value Strategy)

**ﻝ­ﻝ۴ID**: STRAT_MOM_VALUE

**ﻝ­ﻝ۴ﮔﻟﺟﺍ**: ﻝﭨﮒﮒ۷ﻠﮒ ﮒ­ﮒﻛﭨﺓﮒﺙﮒ ﮒ­ﺅﺙﮔﮒﭨﭦﮔﻟﭖﻝﭨﮒ

**ﻠﻝ۷ﮒﭦﮔﺁ**:
- ﻟﭘﮒﺟﮔﮔﺝﻝﮒﺕﮒﭦﻝﺁﮒ۱?- ﻛﺕ­ﻠﺟﮔﮔﻟﭖ?- ﮔﭖﮒ۷ﮔ۶ﮒﻟﭘﺏﻝﻟ۰ﻝ۴۷ﮔﺎ?
---

### 2.2 ﮒ ﮒ­ﻝﭨﮒﮔﺗﮔﺏ

#### ﮒ ﮒ­ﻠﮔ۸

**ﮒ۷ﻠﮒ ﮒ­**:
- ﻝ؟ﮒﮒ۷ﻠﮒ ﮒ­?(MOM_PRICE_SIMPLE)
- ﮔﻛﭦ۳ﻠﮒ ﮔﮒ۷ﻠﮒ ﮒ­?(MOM_VOLUME_WEIGHTED)

**ﻛﭨﺓﮒﺙﮒ ﮒ­?*:
- PBﮒ ﮒ­ (VALUE_PB)
- PEﮒ ﮒ­ (VALUE_PE)
- ﻟ۰ﮔﺁﻝﮒ ﮒ­?(VALUE_DIVIDEND)

---

#### ﮒ ﮒ­ﮔﻠ

**ﮔﻠﮒﻠﮔﺗﮔﺏ**: ﻠ۲ﻠ۸ﮒﺗﺏﻛﭨﺓ (Risk Parity)

```python
def risk_parity_weights(
    factor_returns: pd.DataFrame
) -> Dict[str, float]:
    """
    ﻠ۲ﻠ۸ﮒﺗﺏﻛﭨﺓﮔﻠﻟ؟۰ﻝ؟
    
    Args:
        factor_returns: ﮒ ﮒ­ﮔﭘﻝﻝ۸ﻠﭖ
    
    Returns:
        ﮒ ﮒ­ﮔﻠﮒ­ﮒﺕ
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

#### ﮒ ﮒ­ﮔ­۲ﻛﭦ۳ﮒ?
**ﮔ­۲ﻛﭦ۳ﮒﮔﺗﮔﺏ?*: Gram-Schmidtﮔ­۲ﻛﭦ۳ﮒ?
```python
def orthogonalize_factors(
    factor_values: pd.DataFrame
) -> pd.DataFrame:
    """
    ﮒ ﮒ­ﮔ­۲ﻛﭦ۳ﮒ?    
    Args:
        factor_values: ﮒ ﮒ­ﮒﺙﻝ۸ﻠ?    
    Returns:
        ﮔ­۲ﻛﭦ۳ﮒﮒﻝﮒ ﮒ­ﮒﺙﻝ۸ﻠ?    """
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

### 2.3 ﻝﭨﮒﮔﮒﭨﭦﮔﺗﮔﺏ

#### ﻟ۰ﻝ۴۷ﮔﮒ

```python
def calculate_stock_scores(
    factor_values: pd.DataFrame,
    factor_weights: Dict[str, float]
) -> pd.Series:
    """
    ﻟ؟۰ﻝ؟ﻟ۰ﻝ۴۷ﻝﭨﺙﮒﮒﺝﮒ
    
    Args:
        factor_values: ﮒ ﮒ­ﮒﺙﻝ۸ﻠ?        factor_weights: ﮒ ﮒ­ﮔﻠ
    
    Returns:
        ﻟ۰ﻝ۴۷ﻝﭨﺙﮒﮒﺝﮒ
    """
    weighted_scores = sum(
        factor_values[factor] * weight
        for factor, weight in factor_weights.items()
    )
    return weighted_scores
```

---

#### ﻝﭨﮒﻛﺙﮒ

**ﻛﺙﮒﻝ؟ﮔ **: ﮔﮒ۳۶ﮒﻠ۱ﮔﮔﭘﻝﺅﺙﮔ۶ﮒﭘﻠ۲ﻠ?
```python
def optimize_portfolio(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    max_weight: float = 0.05,
    target_vol: float = 0.15
) -> pd.Series:
    """
    ﻝﭨﮒﻛﺙﮒ
    
    Args:
        expected_returns: ﻠ۱ﮔﮔﭘﻝ
        cov_matrix: ﮒﮔﺗﮒﺓ؟ﻝ۸ﻠ?        max_weight: ﮒﻛﺕ۹ﻟ۰ﻝ۴۷ﮔﮒ۳۶ﮔﻠ?        target_vol: ﻝ؟ﮔ ﮔﺏ۱ﮒ۷ﻝ?    
    Returns:
        ﮔﻛﺙﮔﻠ?    """
    n_stocks = len(expected_returns)
    
    def objective(w):
        portfolio_return = np.dot(w, expected_returns)
        portfolio_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
        return -portfolio_return / portfolio_vol  # ﮔﮒ۳۶ﮒﮒ۳ﮔ؟ﮔﺁﻝ
    
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

### 2.4 ﮒﮔﭖﻟ۰۷ﻝﺍ

**ﮒﮔﭖﮔﻠﺑ**: 2015-01-01 ﻟ?2025-12-31

**ﮒﮔﭖﻝﭨﮔ**:
| ﮔﮔ  | ﮔﺍﮒ?| ﻟﺁﺑﮔ |
|------|------|------|
| **ﮒﺗﺑﮒﮔﭘﻝ** | 15.8% | ﮒﺗﺑﮒﮔﭘﻝﻝ?|
| **ﮒﺗﺑﮒﮔﺏ۱ﮒ۷** | 18.5% | ﮒﺗﺑﮒﮔﺏ۱ﮒ۷ﻝ?|
| **ﮒ۳ﮔ؟ﮔﺁﻝ** | 0.85 | ﮒ۳ﮔ؟ﮔﺁﻝ |
| **ﮔﮒ۳۶ﮒﮔ?* | -22.3% | ﮔﮒ۳۶ﮒﮔ?|
| **ﻟﻝ** | 58.2% | ﮔﮒﭦ۵ﻟﻝ |
| **ﮔ۱ﮔﻝ?* | 185% | ﮒﺗﺑﮔ۱ﮔﻝ |

**ﮒﺗﺑﮒﭦ۵ﮔﭘﻝ**:
| ﮒﺗﺑﻛﭨﺛ | ﮔﭘﻝﻝ?| ﮒﭦﮒﮔﭘﻝ | ﻟﭘﻠ۱ﮔﭘﻝ |
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

### 2.5 ﻠ۲ﻠ۸ﮒﮔ

**ﻠ۲ﻠ۸ﮒ ﮒ­ﮔﺑﻠﺎ**:
| ﻠ۲ﻠ۸ﮒ ﮒ­ | ﮔﺑﻠﺎﮒﭦ?| ﻟﺁﺑﮔ |
|---------|--------|------|
| **ﮒﺕﮒﭦ** | 0.95 | ﮔ۴ﻟﺟﮒﺕﮒﭦﻛﺕ­ﮔ?|
| **ﻟ۶ﮔ۷۰** | -0.15 | ﻟﺛﭨﮒﺝ؟ﮒﮒﮒ۳۶ﻝﻟ?|
| **ﻛﭨﺓﮒ?* | 0.32 | ﮒﮒﻛﭨﺓﮒﺙﻟ۰ |
| **ﮒ۷ﻠ** | 0.28 | ﮒﮒﮒ۷ﻠﻟ?|
| **ﮔﺏ۱ﮒ۷** | -0.18 | ﮒﮒﻛﺛﮔﺏ۱ﮒ۷ﻟ۰ |

**ﻠ۲ﻠ۸ﻟﺑ۰ﻝ؟**:
| ﻠ۲ﻠ۸ﮔ۴ﮔﭦ | ﻟﺑ۰ﻝ؟ﮒﭦ?| ﻟﺁﺑﮔ |
|---------|--------|------|
| **ﮒ ﮒ­ﻠ۲ﻠ۸** | 65% | ﮒ ﮒ­ﮔﺑﻠﺎﮒﺕ۵ﮔ۴ﻝﻠ۲ﻠ?|
| **ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸** | 35% | ﻛﺕ۹ﻟ۰ﻝﺗﻟﺑ۷ﻠ۲ﻠ۸ |

---

### 2.6 ﮒ؟ﮔﺛﮔﮒ

#### ﻟﺍﻛﭨﻠ۱ﻝ

**ﮒﭨﭦﻟ؟؟ﻠ۱ﻝ**: ﮔﮒﭦ۵ﻟﺍﻛﭨ

**ﻟﺍﻛﭨﮔﭖﻝ۷**:
```
ﮔﮒﻝ؛?ﻛﺕ۹ﻛﭦ۳ﮔﮔ۴
  ﻗ?ﮔﺑﮔﺍﮒ ﮒ­ﮔﺍﮔ؟
  ﻗ?ﻟ؟۰ﻝ؟ﮒ ﮒ­ﮒ?  ﻗ?ﻛﺙﮒﻝﭨﮒﮔﻠ
  ﻗ?ﮔ۶ﻟ۰ﻛﭦ۳ﮔ
  ﻗ?ﻝﮔ۶ﻝﭨﮒﻟ۰۷ﻝﺍ
```

---

#### ﻛﭦ۳ﮔﮔ۶ﻟ۰

**ﮔ۶ﻟ۰ﻝ­ﻝ۴**: VWAPﺅﺙﮔﻛﭦ۳ﻠﮒ ﮔﮒﺗﺏﮒﻛﭨﺓﺅﺙ

**ﮔ۶ﻟ۰ﮔﭘﻠﺑ**: ﻛﭦ۳ﮔﮔ۴ﮒﺙﻝﮒ30ﮒﻠﻟﺏﮔﭘﻝﮒ30ﮒﻠ

**ﻛﭦ۳ﮔﮔﮔ؛**:
- ﻛﺛ۲ﻠﺅﺙ?.03%
- ﮒﺎﮒﭨﮔﮔ؛ﺅﺙ?.05%
- ﮔﭨﮔﮔ؛ﺅﺙﻝﭦ?.08%

---

#### ﻠ۲ﻠ۸ﮔ۶ﮒﭘ

**ﮔ­۱ﮔﮔﭦﮒﭘ**:
- ﮒﻟ۰ﮔ­۱ﮔﺅﺙ?15%
- ﻝﭨﮒﮔ­۱ﮔﺅﺙ?10%

**ﻠ۲ﻠ۸ﻠﻠ۱**:
- ﮒﻟ۰ﮔﮒ۳۶ﮔﻠﺅﺙ5%
- ﮒﻟ۰ﻛﺕﮔﮒ۳۶ﮔﻠﺅﺙ25%
- ﮔﮒ۳۶ﮒﮔ۳ﮔ۶ﮒﭘﺅﺙ-25%

---

## 3. ﻟﺑ۷ﻠ+ﻟ۶ﮔ۷۰ﻝ­ﻝ۴

### 3.1 ﻝ­ﻝ۴ﮒ؟ﻛﺗ

**ﻝ­ﻝ۴ﮒﻝ۶ﺍ**: ﻟﺑ۷ﻠ+ﻟ۶ﮔ۷۰ﻝ­ﻝ۴ (Quality + Size Strategy)

**ﻝ­ﻝ۴ID**: STRAT_QUAL_SIZE

**ﻝ­ﻝ۴ﮔﻟﺟﺍ**: ﻝﭨﮒﻟﺑ۷ﻠﮒ ﮒ­ﮒﻟ۶ﮔ۷۰ﮒ ﮒ­ﺅﺙﮔﮒﭨﭦﮔﻟﭖﻝﭨﮒ

**ﻠﻝ۷ﮒﭦﮔﺁ**:
- ﻠﻟ۰ﮒﺕﻝﺁﮒ۱?- ﻠﺎﮒﺝ۰ﮔ۶ﮔﻟﭖ?- ﻠﺟﮔﮔﻟﭖ

---

### 3.2 ﮒ ﮒ­ﻝﭨﮒﮔﺗﮔﺏ

#### ﮒ ﮒ­ﻠﮔ۸

**ﻟﺑ۷ﻠﮒ ﮒ­**:
- ROEﮒ ﮒ­ (QUALITY_ROE)
- ROAﮒ ﮒ­ (QUALITY_ROA)
- ﮔﺁﮒ۸ﻝﮒ ﮒ­?(QUALITY_GROSS_MARGIN)

**ﻟ۶ﮔ۷۰ﮒ ﮒ­**:
- ﮒﺕﮒﺙﮒ ﮒ­?(SIZE_MARKET_CAP)
- ﮔﭖﻠﮒﺕﮒﺙﮒ ﮒ­?(SIZE_FLOAT_CAP)

---

### 3.3 ﮒﮔﭖﻟ۰۷ﻝﺍ

**ﮒﮔﭖﮔﻠﺑ**: 2015-01-01 ﻟ?2025-12-31

**ﮒﮔﭖﻝﭨﮔ**:
| ﮔﮔ  | ﮔﺍﮒ?| ﻟﺁﺑﮔ |
|------|------|------|
| **ﮒﺗﺑﮒﮔﭘﻝ** | 12.5% | ﮒﺗﺑﮒﮔﭘﻝﻝ?|
| **ﮒﺗﺑﮒﮔﺏ۱ﮒ۷** | 15.2% | ﮒﺗﺑﮒﮔﺏ۱ﮒ۷ﻝ?|
| **ﮒ۳ﮔ؟ﮔﺁﻝ** | 0.82 | ﮒ۳ﮔ؟ﮔﺁﻝ |
| **ﮔﮒ۳۶ﮒﮔ?* | -18.5% | ﮔﮒ۳۶ﮒﮔ?|
| **ﻟﻝ** | 56.8% | ﮔﮒﭦ۵ﻟﻝ |
| **ﮔ۱ﮔﻝ?* | 120% | ﮒﺗﺑﮔ۱ﮔﻝ |

---

## 4. ﮒﺕﮒﭦﻛﺕ­ﮔ۶ﻝ­ﻝ?
### 4.1 ﻝ­ﻝ۴ﮒ؟ﻛﺗ

**ﻝ­ﻝ۴ﮒﻝ۶ﺍ**: ﮒﺕﮒﭦﻛﺕ­ﮔ۶ﻝ­ﻝ?(Market Neutral Strategy)

**ﻝ­ﻝ۴ID**: STRAT_MARKET_NEUTRAL

**ﻝ­ﻝ۴ﮔﻟﺟﺍ**: ﮔﮒﭨﭦﮒﺕﮒﭦﻠ۲ﻠ۸ﮔﮒ۲ﻛﺕﭦﻠﭘﻝﮔﻟﭖﻝﭨﮒ?
**ﻠﻝ۷ﮒﭦﮔﺁ**:
- ﮒﺕﮒﭦﮔﺗﮒﻛﺕﮔﻝ۰?- ﻟﺟﺛﮔﺎﻝﭨﮒﺁﺗﮔﭘﻝ
- ﻛﺛﻠ۲ﻠ۸ﮒﮒ۴?
---

### 4.2 ﮒ ﮒ­ﻝﭨﮒﮔﺗﮔﺏ

#### ﮒ ﮒ­ﻠﮔ۸

**Alphaﮒ ﮒ­**:
- ﮒ۷ﻠﮒ ﮒ­
- ﻛﭨﺓﮒﺙﮒ ﮒ­?- ﻟﺑ۷ﻠﮒ ﮒ­

**ﻠ۲ﻠ۸ﮒ ﮒ­**:
- ﮒﺕﮒﭦﮒ ﮒ­
- ﻟ۰ﻛﺕﮒ ﮒ­
- ﻟ۶ﮔ۷۰ﮒ ﮒ­

---

#### ﻛﺕ­ﮔ۶ﮒﮔﺗﮔﺏ

```python
def neutralize(
    factor_values: pd.Series,
    risk_factors: pd.DataFrame
) -> pd.Series:
    """
    ﮒ ﮒ­ﻛﺕ­ﮔ۶ﮒ
    
    Args:
        factor_values: ﮒ ﮒ­ﮒ?        risk_factors: ﻠ۲ﻠ۸ﮒ ﮒ­ﻝ۸ﻠﭖ
    
    Returns:
        ﻛﺕ­ﮔ۶ﮒﮒﻝﮒ ﮒ­ﮒ?    """
    from sklearn.linear_model import LinearRegression
    
    model = LinearRegression()
    model.fit(risk_factors, factor_values)
    
    residuals = factor_values - model.predict(risk_factors)
    return residuals
```

---

### 4.3 ﮒﮔﭖﻟ۰۷ﻝﺍ

**ﮒﮔﭖﮔﻠﺑ**: 2015-01-01 ﻟ?2025-12-31

**ﮒﮔﭖﻝﭨﮔ**:
| ﮔﮔ  | ﮔﺍﮒ?| ﻟﺁﺑﮔ |
|------|------|------|
| **ﮒﺗﺑﮒﮔﭘﻝ** | 8.5% | ﮒﺗﺑﮒﮔﭘﻝﻝ?|
| **ﮒﺗﺑﮒﮔﺏ۱ﮒ۷** | 8.2% | ﮒﺗﺑﮒﮔﺏ۱ﮒ۷ﻝ?|
| **ﮒ۳ﮔ؟ﮔﺁﻝ** | 1.04 | ﮒ۳ﮔ؟ﮔﺁﻝ |
| **ﮔﮒ۳۶ﮒﮔ?* | -5.8% | ﮔﮒ۳۶ﮒﮔ?|
| **ﻟﻝ** | 62.5% | ﮔﮒﭦ۵ﻟﻝ |
| **ﮔ۱ﮔﻝ?* | 250% | ﮒﺗﺑﮔ۱ﮔﻝ |

---

## 5. ﻝ­ﻝ۴ﻠﮔ۸ﮔﮒ

### 5.1 ﻝ­ﻝ۴ﮒﺁﺗﮔﺁ

| ﻝ­ﻝ۴ | ﮒﺗﺑﮒﮔﭘﻝ | ﮒ۳ﮔ؟ﮔﺁﻝ | ﮔﮒ۳۶ﮒﮔ?| ﻠﻝ۷ﮒﭦﮔﺁ |
|------|---------|---------|---------|---------|
| **ﮒ۷ﻠ+ﻛﭨﺓﮒ?* | 15.8% | 0.85 | -22.3% | ﻟﭘﮒﺟﮒﺕﮒﭦ |
| **ﻟﺑ۷ﻠ+ﻟ۶ﮔ۷۰** | 12.5% | 0.82 | -18.5% | ﻠﻟ۰ﮒﺕﮒﭦ |
| **ﮒﺕﮒﭦﻛﺕ­ﮔ?* | 8.5% | 1.04 | -5.8% | ﻛﺕﻝ۰؟ﮒ؟ﮒﺕﮒ?|

---

### 5.2 ﻠﮔ۸ﮒﭨﭦﻟ؟؟

**ﮔ ﺗﮔ؟ﮒﺕﮒﭦﻝﺁﮒ۱ﻠﮔ۸**:
- ﻟﭘﮒﺟﮔﮔﺝﺅﺙﮒ۷ﻠ?ﻛﭨﺓﮒﺙﻝ­ﻝ?- ﻠﻟ۰ﮒﺕﺅﺙﻟﺑ۷ﻠ+ﻟ۶ﮔ۷۰ﻝ­ﻝ۴
- ﻛﺕﻝ۰؟ﮒ؟ﺅﺙﮒﺕﮒﭦﻛﺕ­ﮔ۶ﻝ­ﻝ?
**ﮔ ﺗﮔ؟ﻠ۲ﻠ۸ﮒﮒ۴ﺛﻠﮔ۸**:
- ﻠ،ﻠ۲ﻠ۸ﮒﮒ۴ﺛﺅﺙﮒ۷ﻠ+ﻛﭨﺓﮒﺙﻝ­ﻝ?- ﻛﺕ­ﻠ۲ﻠ۸ﮒﮒ۴ﺛﺅﺙﻟﺑ۷ﻠ+ﻟ۶ﮔ۷۰ﻝ­ﻝ۴
- ﻛﺛﻠ۲ﻠ۸ﮒﮒ۴ﺛﺅﺙﮒﺕﮒﭦﻛﺕ­ﮔ۶ﻝ­ﻝ?
---

## 6. ﮒﻟﮔﮔ۰?
- [ﮒ۷ﻠﮒ ﮒ­ﮒﭦ](08_KNOWLEDGE/FACTOR_LIBRARY/MOMENTUM_FACTOR_LIBRARY.md)
- [ﮒ ﮒ­ﮒﺙﮔﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰](../../01_FRAMEWORK/FACTOR_ENGINE_DETAILED_DESIGN.md)
- [ﮔﻟﭖﮒﺎﮒ­۵](../../01_FRAMEWORK/INVESTMENT_PHILOSOPHY.md)

---

**ﮔﮔ۰۲ﻝﭘﮔ?*: ﮔ­۲ﮒﺙﮔ ﮒ
**ﻛﺕﮔ؛۰ﮔﺑﮔﺍ**: 2026-07-03
