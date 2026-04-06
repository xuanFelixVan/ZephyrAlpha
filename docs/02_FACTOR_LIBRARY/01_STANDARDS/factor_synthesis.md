---
module_id: FACTOR_SYNTHESIS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---


# 因子合成方法

> 多因子合成技�?

---

## 1. 合成目的

- 降低因子冗余�?
- 提高因子稳定�?
- 增强预测能力

---

## 2. 常用合成方法

### 2.1 等权合成

最简单的合成方法，所有因子权重相等�?

$$Composite = \frac{1}{n}\sum_{i=1}^{n} Factor_i$$

```python
def equal_weight合成(factors):
    """等权合成"""
    return factors.mean(axis=1)
```

### 2.2 IC加权合成

根据IC表现分配权重�?

$$w_i = \frac{IC_i}{\sum_{j}IC_j}$$

```python
def ic_weight合成(factors, ic_series):
    """IC加权合成"""
    weights = ic_series / ic_series.sum()
    return (factors * weights).sum(axis=1)
```

### 2.3 最大化ICIR合成

优化权重使组合ICIR最大�?

```python
from scipy.optimize import minimize

def optimize_icir_weights(factors, returns):
    """优化权重使ICIR最�?""
    n = factors.shape[1]

    def neg_icir(weights):
        composite = (factors * weights).sum(axis=1)
        ic = composite.corr(returns)
        icir = ic / returns.std()
        return -icir

    constraints = {'type': 'eq', 'fun': lambda w: sum(w) - 1}
    bounds = [(0, 1) for _ in range(n)]
    initial_weights = [1/n] * n

    result = minimize(neg_icir, initial_weights, method='SLSQP',
                     bounds=bounds, constraints=constraints)

    return result.x if result.success else initial_weights
```

### 2.4 因子正交�?

去除因子间的共线性�?

```python
def orthogonalize_factors(factor_matrix, base_factor):
    """因子对base_factor正交�?""
    from sklearn.linear_model import LinearRegression

    X = base_factor.values.reshape(-1, 1)
    Y = factor_matrix.values

    model = LinearRegression()
    model.fit(X, Y)

    residuals = Y - model.predict(X)
    return pd.DataFrame(residuals, index=factor_matrix.index, columns=factor_matrix.columns)
```

---

## 3. 合成评估

### 3.1 评估指标

| 指标 | 说明 |
|------|------|
| IC均�?| 合成因子IC |
| ICIR | 风险调整IC |
| 相关系数 | 与成分因子相关�?|
| 因子数量 | 有效因子数量 |

### 3.2 评估流程

```python
def evaluate_synthesis(factors, returns, weights=None):
    """评估合成效果"""
    if weights is None:
        weights = [1/len(factors)] * len(factors)

    composite = sum(f * w for f, w in zip(factors, weights))

    return {
        'IC': composite.corr(returns),
        'ICIR': composite.corr(returns) / returns.std(),
        'corr_with_components': [composite.corr(f) for f in factors]
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
