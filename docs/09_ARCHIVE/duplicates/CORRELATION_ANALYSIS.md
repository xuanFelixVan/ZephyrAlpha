---
module_id: 02_FACTOR_LIBRARY_04_DATA_SOURCE_001_ARCHIVED_1
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
z = 0.5 * np.log((1 + r) / (1 - r))
se = 1 / np.sqrt(n - 3)
z_alpha = stats.norm.ppf((1 + confidence) / 2)
z_lower = z - z_alpha * se
z_upper = z + z_alpha * se
r_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
r_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)
return r_lower, r_upper
```
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
z1 = 0.5 * np.log((1 + r1) / (1 - r1))
z2 = 0.5 * np.log((1 + r2) / (1 - r2))
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
responsibility:
- 管理因子库
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
