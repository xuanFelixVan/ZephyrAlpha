# Barra风险优化器

> Barra风险模型与组合优化
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - JSON Schemas：[architecture/json-schemas.md](./architecture/json-schemas.md)

***

## 1. Barra风险模型基础

```python
class BarraRiskModel:
    """
    Barra风险模型
    包含风格因子 + 行业因子 + 特异性风险
    """

    def __init__(self):
        self.style_factors = [
            'SIZE', 'VALUE', 'MOM', 'QUAL', 'VOL',
            'GROW', 'EARN', 'LEVER', 'LIQUID', 'YIELD'
        ]

        self.industry_factors = list(SW_INDUSTRY_L1.keys())
        self.factor_returns = None
        self.idiosyncratic_var = None

    def calc_portfolio_risk(self, weights, factor_exposures):
        """
        计算组合风险
        公式: σ²_p = w' * (X*F*X' + D) * w
        """
        factor_cov = self.calc_factor_covariance()
        idio_var = self.idiosyncratic_var

        systematic_risk = weights @ (factor_exposures @ factor_cov @ factor_exposures.T) @ weights
        idio_risk = weights @ idio_var @ weights

        total_risk = np.sqrt(systematic_risk + idio_risk)

        return total_risk

    def calc_factor_covariance(self):
        """
        计算因子协方差矩阵
        使用Shrinkage估计器提高稳定性
        """
        factor_ret = self.factor_returns
        sample_cov = factor_ret.T.cov()

        shrinkage_target = np.diag(np.diag(sample_cov))
        shrinkage_intensity = 0.3

        factor_cov = shrinkage_intensity * shrinkage_target + (1 - shrinkage_intensity) * sample_cov

        return factor_cov
```

***

## 2. Barra优化器实现

```python
from scipy.optimize import minimize
import cvxpy as cp

class BarraOptimizer:
    """
    Barra优化器
    在控制风险的同时优化组合收益
    """

    def __init__(self, barra_model: BarraRiskModel):
        self.barra = barra_model

    def optimize(self, expected_returns, risk_aversion, constraints):
        """
        优化组合权重

        参数:
            expected_returns: 预期收益向量
            risk_aversion: 风险厌恶系数
            constraints: 优化约束
        """
        n = len(expected_returns)
        weights = cp.Variable(n)

        portfolio_return = expected_returns @ weights
        portfolio_risk = cp.quad_form(weights, self.barra.factor_cov)

        objective = cp.Maximize(portfolio_return - risk_aversion * portfolio_risk)

        constraints_list = [
            cp.sum(weights) == 1,
            weights >= 0,
        ]

        for constraint in constraints:
            constraints_list.append(constraint)

        problem = cp.Problem(objective, constraints_list)
        problem.solve(solver=cp.ECOS)

        return weights.value if problem.status == 'optimal' else None
```

***

## 3. Barra风险因子结构

| 因子类别 | 因子名称 | 说明 |
|----------|----------|------|
| 风格因子 | SIZE | 市值因子 |
| 风格因子 | VALUE | 价值因子 |
| 风格因子 | MOM | 动量因子 |
| 风格因子 | QUAL | 质量因子 |
| 风格因子 | VOL | 波动率因子 |
| 风格因子 | GROW | 成长因子 |
| 风格因子 | EARN | 盈利因子 |
| 风格因子 | LEVER | 杠杆因子 |
| 风格因子 | LIQUID | 流动性因子 |
| 风格因子 | YIELD | 收益因子 |
| 行业因子 | SW_INDUSTRY_L1 | 申万一级行业（28个） |
| 特异性风险 | IDIO | 个股特有风险 |

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录AM内容 |
