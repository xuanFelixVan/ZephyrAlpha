---

## 3. 合成评估

### 3.1 评估指标

| 指标 | 说明 |
|------|------|
| IC均?| 合成因子IC |
| ICIR | 风险调整IC |
| 相关系数 | 与成分因子相关?|
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
