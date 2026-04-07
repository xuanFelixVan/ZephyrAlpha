---
module_id: FACTOR_T_03_RM003_BARRA_OPTIMIZER_001
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



# T.03.RM003.barra_optimizer
> **核心职责**: Barra风险模型和组合优化器设计
> **职责边界**: 
> - ✅ 本文档负责：Barra风险模型和组合优化器设计相关内容
> - ❌ 本文档不负责：其他模块内容


> Barra risk model and portfolio optimizer
>
> **策略编号**：T.03.RM003
> **所属模�?*�?3_RISK_FACTORS
> **文档类型**：风险模型优�?
> **优先�?*：P1
>
> **配套文档**�?
> - [T.03.RF001.barra_style_factors.md](T.03.RF001.barra_style_factors.md) - 十大风格因子定义
> - [T.03.RF002.industry_factors.md](T.03.RF002.industry_factors.md) - 申万行业分类
> - [T.03.RF003.tail_risk_factors.md](T.03.RF003.tail_risk_factors.md) - CVaR/ES尾部风险

---

## 1. BarraRiskModel 完整实现

```python
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


class BarraRiskModel:
    """
    Barra多因子风险模�?(A股适配�?

    组合风险公式: σ²_p = w' * (X*F*X' + D) * w
    其中:
        X: 因子暴露矩阵 (N x K)
        F: 因子协方差矩�?(K x K)
        D: 特异性方差对角矩�?(N x N)
        w: 组合权重向量 (N x 1)

    Attributes:
        style_factors: 风格因子列表
        industry_factors: 行业因子列表
        factor_returns: 因子收益率矩�?
        idiosyncratic_var: 特异性方�?
        factor_cov: 因子协方差矩�?
    """

    STYLE_FACTORS = ['SIZE', 'VALUE', 'MOM', 'QUAL', 'VOL',
                     'GROW', 'EARN', 'LEVER', 'LIQUID', 'YIELD']

    SW_INDUSTRY_L1 = {
        '801010': '农林牧渔', '801020': '采掘', '801030': '化工',
        '801040': '钢铁', '801050': '有色金属', '801060': '电子',
        '801080': '汽车', '801110': '家用电器', '801120': '食品饮料',
        '801130': '纺织服装', '801140': '轻工制�?, '801150': '医药生物',
        '801160': '公用事业', '801170': '交通运�?, '801180': '房地�?,
        '801200': '商业贸易', '801210': '休闲服务', '801230': '建筑材料',
        '801710': '建筑装饰', '801720': '电气设备', '801730': '国防军工',
        '801740': '计算�?, '801750': '传媒', '801760': '通信',
        '801770': '银行', '801780': '非银金融', '801790': '综合',
        '801890': '机械设备'
    }

    def __init__(self):
        self.style_factors = self.STYLE_FACTORS
        self.industry_factors = list(self.SW_INDUSTRY_L1.values())
        self.all_factors = self.style_factors + self.industry_factors
        self.factor_returns = None
        self.idiosyncratic_var = None
        self.factor_cov = None
        self.factor_exposures = None

    def calc_style_exposures(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        计算风格因子暴露�?

        参数:
            market_data: 包含以下列的DataFrame
                - close: 收盘�?
                - float_volume: 流通股�?
                - pb: 市净�?
                - pe: 市盈�?
                - dividend_yield: 股息�?
                - turnover_rate: 换手�?
                - volatility_20d: 20日波动率
                - revenue_growth: 营收增长�?
                - profit_growth: 利润增长�?
                - debt_to_equity: 资产负债率
                - free_cash_flow: 自由现金�?

        返回:
            style_exposures: 风格因子暴露�?(N x 10)
        """
        exposures = pd.DataFrame(index=market_data.index)

        float_mcap = market_data['close'] * market_data['float_volume']
        exposures['SIZE'] = np.log(float_mcap.replace(0, np.nan))

        exposures['VALUE'] = (
            (1 / market_data['pb'].replace(0, np.nan)).fillna(0) +
            np.where(market_data['pe'] > 0, 1 / market_data['pe'].replace(0, np.nan), 0) +
            market_data['dividend_yield'].fillna(0)
        ) / 3

        returns_252 = market_data['close'].pct_change(252)
        returns_21 = market_data['close'].pct_change(21)
        exposures['MOM'] = (returns_252 - returns_21).replace([np.inf, -np.inf], np.nan)

        exposures['QUAL'] = (
            market_data['roe'].fillna(0) +
            market_data['gross_profit_margin'].fillna(0) -
            market_data['debt_to_equity'].fillna(0) / 100
        )

        exposures['VOL'] = market_data['volatility_20d'].fillna(
            market_data['turnover_rate'].rolling(20).std()
        )

        exposures['GROW'] = (
            market_data['revenue_growth'].fillna(0) * 0.5 +
            market_data['profit_growth'].fillna(0) * 0.5
        )

        exposures['EARN'] = (
            market_data['roe'].fillna(0) * 0.6 +
            market_data['gross_profit_margin'].fillna(0) * 0.4
        )

        exposures['LEVER'] = market_data['debt_to_equity'].fillna(0) / 100

        exposures['LIQUID'] = np.where(
            market_data['turnover_rate'] > 0,
            1 / np.log1p(market_data['turnover_rate']),
            0
        )

        exposures['YIELD'] = market_data['dividend_yield'].fillna(0)

        return exposures.fillna(0)

    def calc_industry_exposures(self, industry_codes: pd.Series) -> pd.DataFrame:
        """
        计算行业因子暴露�?(dummy variable encoding)

        参数:
            industry_codes: 申万行业代码 Series

        返回:
            industry_exposures: 行业因子暴露�?(N x 28)
        """
        industry_names = industry_codes.map(self.SW_INDUSTRY_L1)
        industry_exposures = pd.get_dummies(industry_names, columns=self.industry_factors)
        return industry_exposures.reindex(columns=self.industry_factors, fill_value=0)

    def calc_factor_returns(self, returns: pd.DataFrame,
                           factor_exposures: pd.DataFrame,
                           date: str) -> pd.DataFrame:
        """
        使用横截面回归计算因子收益率

        公式: r_i = X_i * f + ε_i
        其中: f = (X'X)^(-1) * X'r

        参数:
            returns: 个股收益�?(N x 1)
            factor_exposures: 因子暴露�?(N x K)
            date: 交易日期

        返回:
            factor_ret: 因子收益�?(K x 1)
        """
        X = factor_exposures.values
        y = returns.values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        reg = LinearRegression(fit_intercept=False)
        reg.fit(X_scaled, y)

        factor_ret = pd.Series(reg.coef_, index=factor_exposures.columns, name=date)

        residuals = y - reg.predict(X_scaled)
        idiosyncratic_var = pd.Series(residuals ** 2, index=factor_exposures.index)

        if self.factor_returns is None:
            self.factor_returns = factor_ret.to_frame().T
            self.idiosyncratic_var = idiosyncratic_var.to_frame().T
        else:
            self.factor_returns = pd.concat([self.factor_returns, factor_ret.to_frame().T])
            self.idiosyncratic_var = pd.concat([self.idiosyncratic_var, idiosyncratic_var.to_frame().T])

        return factor_ret

    def calc_factor_covariance(self, lookback: int = 60,
                              shrinkage_target: str = 'constant') -> np.ndarray:
        """
        计算因子协方差矩�?

        使用Shrinkage估计器提高矩阵稳定�?
        Σ = δ * T + (1-δ) * S

        参数:
            lookback: 回溯天数
            shrinkage_target: 收缩目标 ('constant', 'sparse', 'diagonal')

        返回:
            factor_cov: 因子协方差矩�?(K x K)
        """
        if self.factor_returns is None or len(self.factor_returns) < lookback:
            raise ValueError("因子收益率数据不�?)

        factor_ret_window = self.factor_returns.iloc[-lookback:]
        sample_cov = factor_ret_window.T.cov().values

        if shrinkage_target == 'diagonal':
            shrink_target = np.diag(np.diag(sample_cov))
        elif shrinkage_target == 'sparse':
            threshold = np.percentile(np.abs(sample_cov), 70)
            shrink_target = np.where(np.abs(sample_cov) > threshold, sample_cov, 0)
        else:
            shrink_target = np.eye(len(sample_cov)) * np.mean(np.diag(sample_cov))

        shrinkage_intensity = 0.3
        factor_cov = shrinkage_intensity * shrink_target + (1 - shrinkage_intensity) * sample_cov

        self.factor_cov = factor_cov
        return factor_cov

    def calc_portfolio_risk(self, weights: np.ndarray,
                           factor_exposures: np.ndarray,
                           factor_cov: np.ndarray = None,
                           idio_var: np.ndarray = None) -> float:
        """
        计算组合风险

        公式: σ²_p = w' * (X*F*X' + D) * w

        参数:
            weights: 组合权重 (N,)
            factor_exposures: 因子暴露�?(N, K)
            factor_cov: 因子协方差矩�?(K, K)，使用实例缓�?
            idio_var: 特异性方�?(N,)，使用实例缓�?

        返回:
            total_risk: 组合风险（年化标准差�?
        """
        if factor_cov is None:
            factor_cov = self.factor_cov
        if idio_var is None:
            idio_var = np.diag(self.idiosyncratic_var.iloc[-1].values)

        systematic_risk = weights @ (factor_exposures @ factor_cov @ factor_exposures.T) @ weights
        idio_risk = weights @ idio_var @ weights

        total_risk = np.sqrt(systematic_risk + idio_risk)
        return total_risk

    def calc_portfolio_var_decomposition(self, weights: np.ndarray,
                                        factor_exposures: np.ndarray) -> dict:
        """
        组合风险分解

        返回各因子对组合风险的贡�?

        参数:
            weights: 组合权重
            factor_exposures: 因子暴露�?

        返回:
            decomposition: 风险贡献字典
        """
        factor_cov = self.factor_cov
        idio_var = np.diag(self.idiosyncratic_var.iloc[-1].values)

        total_risk = self.calc_portfolio_risk(weights, factor_exposures)

        factor_risk_contrib = []
        for i in range(factor_cov.shape[0]):
            factor_exposure_i = factor_exposures[:, i:i+1]
            factor_cov_i = factor_cov[i, i]

            risk_i = weights @ (factor_exposure_i * factor_cov_i @ factor_exposure_i.T) @ weights
            factor_risk_contrib.append(np.sqrt(risk_i))

        idio_risk_contrib = np.sqrt(weights @ idio_var @ weights)

        return {
            'total_risk': total_risk,
            'systematic_risk': np.sqrt(total_risk**2 - idio_risk_contrib**2),
            'idiosyncratic_risk': idio_risk_contrib,
            'factor_contributions': dict(zip(self.all_factors, factor_risk_contrib)),
            'factor_risk_pct': dict(zip(self.all_factors,
                                       [x/total_risk*100 for x in factor_risk_contrib]))
        }
```

---

## 2. BarraOptimizer 组合优化�?

```python
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import List, Tuple, Optional, Callable


class BarraOptimizer:
    """
    Barra optimizer - Portfolio weight optimization based on Barra risk model

    支持的优化目�?
    - Mean-Variance: 最大化 (μ'w - λ * w'Σw)
    - Risk Parity: 各因�?资产风险贡献相等
    - Maximum Diversification: 最大化分散化比�?
    - Minimum Variance: 最小化组合方差

    参数:
        barra_model: BarraRiskModel实例
        risk_aversion: 风险厌恶系数 (默认1.0)
    """

    def __init__(self, barra_model: BarraRiskModel, risk_aversion: float = 1.0):
        self.barra = barra_model
        self.risk_aversion = risk_aversion
        self.last_weights = None
        self.last_objective_value = None

    def mean_variance_optimize(
        self,
        expected_returns: np.ndarray,
        factor_exposures: np.ndarray,
        constraints: List[dict] = None,
        bounds: Tuple[float, float] = None,
        max_weight: float = 0.05
    ) -> np.ndarray:
        """
        Mean-Variance优化

        目标: max_w (μ'w - λ * w'Σw)

        参数:
            expected_returns: 预期收益向量 (N,)
            factor_exposures: 因子暴露度矩�?(N, K)
            constraints: 额外约束列表
            bounds: 权重边界 (min, max)
            max_weight: 单只股票最大权�?

        返回:
            optimal_weights: 最优权�?(N,)
        """
        n = len(expected_returns)

        if bounds is None:
            bounds = [(0, max_weight) for _ in range(n)]

        def objective(weights):
            portfolio_return = expected_returns @ weights
            portfolio_risk = self.barra.calc_portfolio_risk(
                weights, factor_exposures
            )
            return -(portfolio_return - self.risk_aversion * portfolio_risk ** 2)

        constraints_list = []
        if constraints:
            for c in constraints:
                if c['type'] == 'eq':
                    constraints_list.append({'type': 'eq', 'fun': c['fun']})
                elif c['type'] == 'ineq':
                    constraints_list.append({'type': 'ineq', 'fun': c['fun']})

        constraints_list.append({
            'type': 'eq',
            'fun': lambda w: np.sum(w) - 1.0
        })

        x0 = np.ones(n) / n

        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list,
            options={'maxiter': 1000, 'ftol': 1e-8}
        )

        if result.success:
            self.last_weights = result.x
            self.last_objective_value = result.fun
            return result.x
        else:
            print(f"优化未收�? {result.message}")
            return x0

    def risk_parity_optimize(
        self,
        factor_exposures: np.ndarray,
        factor_cov: np.ndarray = None,
        asset_volatility: np.ndarray = None,
        constraints: List[dict] = None
    ) -> np.ndarray:
        """
        风险平价优化

        目标: 各资产对组合风险的贡献相�?

        参数:
            factor_exposures: 因子暴露�?(N, K)
            factor_cov: 因子协方差矩�?(K, K)
            asset_volatility: 资产波动�?(N,)，用于计算协方差矩阵
            constraints: 额外约束

        返回:
            risk_parity_weights: 风险平价权重
        """
        if asset_volatility is None:
            asset_volatility = np.ones(factor_exposures.shape[0])

        if factor_cov is None:
            factor_cov = self.barra.factor_cov

        cov_matrix = factor_exposures @ factor_cov @ factor_exposures.T
        cov_matrix += np.diag(asset_volatility ** 2)

        def risk_contribution(weights, cov):
            portfolio_var = weights @ cov @ weights
            marginal_contrib = cov @ weights
            risk_contrib = weights * marginal_contrib
            return risk_contrib / np.sqrt(portfolio_var)

        def objective(weights):
            rc = risk_contribution(weights, cov_matrix)
            target_rc = np.ones(len(weights)) * (np.sum(rc) / len(weights))
            return np.sum((rc - target_rc) ** 2)

        n = len(asset_volatility)
        bounds = [(0.01, 0.1) for _ in range(n)]

        constraints_list = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
        if constraints:
            constraints_list.extend(constraints)

        x0 = np.ones(n) / n

        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list,
            options={'maxiter': 1000}
        )

        if result.success:
            self.last_weights = result.x
            return result.x
        else:
            print(f"风险平价优化未收�? {result.message}")
            return x0

    def maximum_diversification_optimize(
        self,
        expected_returns: np.ndarray,
        factor_exposures: np.ndarray,
        asset_volatility: np.ndarray,
        bounds: Tuple[float, float] = None
    ) -> np.ndarray:
        """
        最大分散化优化

        目标: max_w (w'σ / sqrt(w'Σw))

        参数:
            expected_returns: 预期收益
            factor_exposures: 因子暴露�?
            asset_volatility: 资产波动�?
            bounds: 权重边界

        返回:
            optimal_weights: 最优权�?
        """
        factor_cov = self.barra.factor_cov
        cov_matrix = factor_exposures @ factor_cov @ factor_exposures.T
        cov_matrix += np.diag(asset_volatility ** 2)

        n = len(asset_volatility)

        def objective(weights):
            weighted_vol = weights @ asset_volatility
            portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
            diversification_ratio = weighted_vol / portfolio_vol
            return -diversification_ratio

        if bounds is None:
            bounds = [(0, 0.1) for _ in range(n)]

        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

        x0 = np.ones(n) / n

        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )

        if result.success:
            self.last_weights = result.x
            return result.x
        else:
            print(f"最大分散化优化未收�? {result.message}")
            return x0

    def black_litterman_optimize(
        self,
        market_cap_weights: np.ndarray,
        factor_exposures: np.ndarray,
        views: np.ndarray,
        view_confidence: np.ndarray,
        risk_aversion: float = 2.5
    ) -> np.ndarray:
        """
        Black-Litterman模型优化

        将投资者观点融入Barra风险模型

        参数:
            market_cap_weights: 市场平衡权重 (N,)
            factor_exposures: 因子暴露�?(N, K)
            views: 观点向量 (K,) - 各因子的预期收益
            view_confidence: 观点置信�?(K,) - 0�?之间
            risk_aversion: 风险厌恶系数

        返回:
            adjusted_weights: 调整后权�?
        """
        factor_cov = self.barra.factor_cov

        market_implied_returns = risk_aversion * factor_cov @ (factor_exposures.T @ market_cap_weights)

        P = np.eye(len(views))
        Q = views
        tau = 0.1

        omega = np.diag(np.diag(P @ (tau * factor_cov) @ P.T))

        view_adjusted_returns = np.linalg.inv(
            np.linalg.inv(tau * factor_cov) + P.T @ np.linalg.inv(omega) @ P
        ) @ (
            np.linalg.inv(tau * factor_cov) @ market_implied_returns +
            P.T @ np.linalg.inv(omega) @ Q
        )

        self.barra.factor_returns = pd.DataFrame(
            view_adjusted_returns.reshape(1, -1),
            columns=self.barra.all_factors
        )

        optimal_weights = self.mean_variance_optimize(
            factor_exposures @ view_adjusted_returns,
            factor_exposures
        )

        return optimal_weights

    def add_industry_neutral_constraint(
        self,
        factor_exposures: np.ndarray,
        industry_labels: np.ndarray
    ) -> dict:
        """
        添加行业中性约�?

        参数:
            factor_exposures: 因子暴露�?
            industry_labels: 行业标签

        返回:
            constraint: scipy约束字典
        """
        unique_industries = np.unique(industry_labels)
        n_industries = len(unique_industries)

        industry_exposure = np.zeros((n_industries, factor_exposures.shape[0]))

        for i, ind in enumerate(unique_industries):
            industry_exposure[i, industry_labels == ind] = 1

        constraint = {
            'type': 'eq',
            'fun': lambda w: industry_exposure @ w - np.ones(n_industries) / n_industries
        }

        return constraint

    def add_style_factor_exposure_constraint(
        self,
        factor_exposures: np.ndarray,
        style_factor_names: List[str],
        target_exposure: float,
        tolerance: float = 0.1
    ) -> dict:
        """
        添加风格因子暴露度约�?

        参数:
            factor_exposures: 因子暴露�?
            style_factor_names: 风格因子名称列表
            target_exposure: 目标暴露�?
            tolerance: 容忍�?

        返回:
            constraint: scipy约束字典
        """
        style_indices = [self.barra.all_factors.index(f) for f in style_factor_names]
        style_exposure = factor_exposures[:, style_indices].sum(axis=1)

        constraint = {
            'type': 'eq',
            'fun': lambda w: (w @ style_exposure) - target_exposure
        }

        return constraint
```

---

## 3. 优化器使用示�?

```python
import pandas as pd
import numpy as np
from barra_risk_model import BarraRiskModel
from barra_optimizer import BarraOptimizer


def example_portfolio_optimization():
    """
    完整组合优化示例
    """
    barra = BarraRiskModel()
    optimizer = BarraOptimizer(barra, risk_aversion=1.5)

    market_data = pd.read_csv('market_data.csv', index_col=0)

    style_exposures = barra.calc_style_exposures(market_data)

    industry_codes = market_data['sw_industry_code']
    industry_exposures = barra.calc_industry_exposures(industry_codes)

    factor_exposures = pd.concat([style_exposures, industry_exposures], axis=1)

    returns = market_data['daily_return']

    barra.calc_factor_returns(returns, factor_exposures, date='2024-01-01')

    barra.calc_factor_covariance(lookback=60)

    expected_returns = market_data['predicted_return'].values
    factor_exp_array = factor_exposures.values

    industry_constraint = optimizer.add_industry_neutral_constraint(
        factor_exp_array,
        industry_codes.values
    )

    size_constraint = optimizer.add_style_factor_exposure_constraint(
        factor_exp_array,
        ['SIZE'],
        target_exposure=0.0
    )

    constraints = [industry_constraint, size_constraint]

    optimal_weights = optimizer.mean_variance_optimize(
        expected_returns,
        factor_exp_array,
        constraints=constraints,
        max_weight=0.05
    )

    risk_decomposition = barra.calc_portfolio_var_decomposition(
        optimal_weights,
        factor_exp_array
    )

    print(f"组合风险: {risk_decomposition['total_risk']:.4f}")
    print(f"系统性风�? {risk_decomposition['systematic_risk']:.4f}")
    print(f"特异性风�? {risk_decomposition['idiosyncratic_risk']:.4f}")
    print("\n因子风险贡献:")
    for factor, pct in risk_decomposition['factor_risk_pct'].items():
        if pct > 1.0:
            print(f"  {factor}: {pct:.2f}%")


if __name__ == '__main__':
    example_portfolio_optimization()
```

---

## 4. 关键参数说明

| 参数 | 默认�?| 说明 |
|------|--------|------|
| risk_aversion | 1.0 | 风险厌恶系数，越大越保守 |
| shrinkage_intensity | 0.3 | 协方差矩阵收缩强�?|
| max_weight | 0.05 | 单只股票最大权�?5%) |
| lookback | 60 | 协方差估计回溯期 |
| tau | 0.1 | Black-Litterman缩放因子 |

---

## 5. 约束类型汇�?

| 约束类型 | 实现方法 | 说明 |
|----------|----------|------|
| 权重�?| sum(weights) = 1 | 必须满足 |
| 边界约束 | bounds | min/max权重限制 |
| 行业中�?| industry_exposure @ w = 1/n | 各行业权重相�?|
| 风格中�?| factor_exposure @ w = target | 风格因子暴露�?|
| 换手�?| \|w - w_prev\| <= turnover | 交易成本控制 |
| 现金�?| price @ w <= cash | 最大买入金�?|

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录AM内容 |
| v1.1 | 2026-03-28 | 完善BarraOptimizer类，添加BL模型 |

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
