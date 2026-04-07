---
module_id: LAYERED_BACKTEST_001
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



# 分层回测框架
> **核心职责**: 分层回测方法和流程
> **职责边界**: 
> - ✅ 本文档负责：分层回测方法和流程相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容


> Layer 2: Alpha因子计算 - 分组测试、多空组合、收益单调性分�?

---

## 1. 框架概述

分层回测是验证因子有效性的核心方法，通过将股票按因子值分组，检验因子对股票收益率的区分能力�?

```
分层回测架构
├── 分组模块 (Grouper)
�?  ├── 等数量分�?
�?  ├── 等市值分�?
�?  └── 行业中性分�?
├── 组合构建 (Portfolio Builder)
�?  ├── 多空组合
�?  ├── 纯多头组�?
�?  └── 市场中性强组合
├── 收益分析 (Return Analyzer)
�?  ├── 分组收益
�?  ├── 累计收益
�?  └── Monotonicity检�?
└── 统计检�?(Statistical Test)
    ├── t检�?
    ├── ANOVA
    └── 因子有效性检�?
```

---

## 2. 分组模块

### 2.1 分组器基�?

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class GroupResult:
    """分组结果"""
    group_id: int
    stocks: List[str]
    weights: np.ndarray
    factor_values: np.ndarray
    start_date: str
    end_date: str


class BaseGrouper(ABC):
    """分组器基�?""

    def __init__(self, n_groups: int = 10):
        self.n_groups = n_groups

    @abstractmethod
    def group(
        self,
        factor_values: pd.Series,
        stock_returns: pd.DataFrame,
        market_caps: Optional[pd.Series] = None,
        industries: Optional[pd.Series] = None
    ) -> List[GroupResult]:
        """执行分组

        参数:
            factor_values: 因子�?(index=stock_code)
            stock_returns: 股票收益�?(index=date, columns=stock_code)
            market_caps: 市�?(index=stock_code)
            industries: 行业分类 (index=stock_code)

        返回:
            分组结果列表
        """
        pass

    def _create_weights(
        self,
        stocks: List[str],
        market_caps: Optional[pd.Series] = None,
        method: str = "equal"
    ) -> np.ndarray:
        """创建权重

        参数:
            stocks: 股票列表
            market_caps: 市�?
            method: 权重方法 ('equal', 'value_weighted')
        """
        n = len(stocks)

        if method == "equal":
            return np.ones(n) / n
        elif method == "value_weighted" and market_caps is not None:
            caps = np.array([market_caps.get(s, 1) for s in stocks])
            return caps / caps.sum()
        else:
            return np.ones(n) / n
```

### 2.2 常用分组器实�?

```python
class EqualNumberGrouper(BaseGrouper):
    """等数量分�?""

    def group(
        self,
        factor_values: pd.Series,
        stock_returns: pd.DataFrame,
        market_caps: Optional[pd.Series] = None,
        industries: Optional[pd.Series] = None
    ) -> List[GroupResult]:
        """按因子值排序，等数量分入各�?""

        valid_stocks = factor_values.dropna().index.tolist()
        sorted_stocks = valid_stocks[np.argsort(factor_values[valid_stocks].values)]

        n_per_group = len(sorted_stocks) // self.n_groups
        results = []

        for i in range(self.n_groups):
            start_idx = i * n_per_group
            end_idx = start_idx + n_per_group if i < self.n_groups - 1 else len(sorted_stocks)

            group_stocks = sorted_stocks[start_idx:end_idx]

            weights = self._create_weights(group_stocks, market_caps, "equal")

            results.append(GroupResult(
                group_id=i + 1,
                stocks=group_stocks,
                weights=weights,
                factor_values=factor_values[group_stocks].values,
                start_date=stock_returns.index.min(),
                end_date=stock_returns.index.max()
            ))

        return results


class EqualMarketCapGrouper(BaseGrouper):
    """等市值分�?""

    def group(
        self,
        factor_values: pd.Series,
        stock_returns: pd.DataFrame,
        market_caps: Optional[pd.Series] = None,
        industries: Optional[pd.Series] = None
    ) -> List[GroupResult]:
        """按市值加权分组，使每组市值接�?""

        if market_caps is None:
            raise ValueError("Market caps required for EqualMarketCapGrouper")

        valid_stocks = factor_values.dropna().index.tolist()
        sorted_stocks = valid_stocks[np.argsort(factor_values[valid_stocks].values)]

        results = []
        target_cap_per_group = market_caps[sorted_stocks].sum() / self.n_groups

        current_group = []
        current_cap = 0

        for stock in sorted_stocks:
            stock_cap = market_caps.get(stock, 0)
            current_group.append(stock)
            current_cap += stock_cap

            if len(current_group) >= 5 and current_cap >= target_cap_per_group:
                weights = self._create_weights(current_group, market_caps, "value_weighted")

                results.append(GroupResult(
                    group_id=len(results) + 1,
                    stocks=current_group,
                    weights=weights,
                    factor_values=factor_values[current_group].values,
                    start_date=stock_returns.index.min(),
                    end_date=stock_returns.index.max()
                ))

                current_group = []
                current_cap = 0

        if current_group:
            weights = self._create_weights(current_group, market_caps, "value_weighted")
            results.append(GroupResult(
                group_id=len(results) + 1,
                stocks=current_group,
                weights=weights,
                factor_values=factor_values[current_group].values,
                start_date=stock_returns.index.min(),
                end_date=stock_returns.index.max()
            ))

        return results


class IndustryNeutralGrouper(BaseGrouper):
    """行业中性分�?""

    def __init__(self, n_groups: int = 10):
        super().__init__(n_groups)
        self.base_grouper = EqualNumberGrouper(n_groups)

    def group(
        self,
        factor_values: pd.Series,
        stock_returns: pd.DataFrame,
        market_caps: Optional[pd.Series] = None,
        industries: Optional[pd.Series] = None
    ) -> List[GroupResult]:
        """在每个行业内分组，然后合�?""

        if industries is None:
            raise ValueError("Industries required for IndustryNeutralGrouper")

        all_results = []

        for industry, group_stocks in industries.groupby(industries):
            industry_factors = factor_values[group_stocks]

            if len(industry_stocks) < self.n_groups:
                continue

            industry_returns = stock_returns[group_stocks]
            industry_caps = market_caps[group_stocks] if market_caps is not None else None

            group_results = self.base_grouper.group(
                industry_factors,
                industry_returns,
                industry_caps
            )

            all_results.extend(group_results)

        return sorted(all_results, key=lambda x: x.group_id)
```

---

## 3. 组合构建模块

### 3.1 组合构建�?

```python
class PortfolioBuilder:
    """组合构建�?""

    def __init__(self):
        self.rebalance_frequency = "monthly"

    def build_long_short_portfolio(
        self,
        groups: List[GroupResult],
        long_group: int = 10,
        short_group: int = 1,
        hedge_ratio: float = 1.0
    ) -> Dict:
        """构建多空组合

        参数:
            groups: 分组结果
            long_group: 做多组号 (默认最高因子值组=10)
            short_group: 做空组号 (默认最低因子值组=1)
            hedge_ratio: 对冲比例

        返回:
            多空组合
        """
        long_portfolio = groups[long_group - 1]
        short_portfolio = groups[short_group - 1]

        long_weights = long_portfolio.weights
        short_weights = short_portfolio.weights * hedge_ratio

        return {
            "long_stocks": long_portfolio.stocks,
            "long_weights": long_weights,
            "short_stocks": short_portfolio.stocks,
            "short_weights": short_weights,
            "net_exposure": long_weights.sum() - short_weights.sum()
        }

    def build_long_only_portfolio(
        self,
        groups: List[GroupResult],
        top_groups: List[int] = None,
        bottom_groups: List[int] = None
    ) -> Dict:
        """构建纯多头组�?

        参数:
            groups: 分组结果
            top_groups: 入选组号列�?
            bottom_groups: 排除组号列表
        """
        if top_groups is None:
            top_groups = [9, 10]

        selected_stocks = []
        selected_weights = []

        for g in top_groups:
            if 0 < g <= len(groups):
                selected_stocks.extend(groups[g - 1].stocks)

        weights = np.ones(len(selected_stocks)) / len(selected_stocks)

        return {
            "stocks": selected_stocks,
            "weights": weights
        }

    def build_market_neutral_portfolio(
        self,
        groups: List[GroupResult],
        factor: pd.Series,
        market_exposure_limit: float = 0.1
    ) -> Dict:
        """构建市场中性强组合"""
        pass
```

---

## 4. 收益分析模块

### 4.1 分组收益分析

```python
@dataclass
class GroupReturn:
    """分组收益"""
    group_id: int
    period: str
    return_value: float
    cumulative_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float


class ReturnAnalyzer:
    """收益分析�?""

    def __init__(self, risk_free_rate: float = 0.03):
        self.risk_free_rate = risk_free_rate

    def calculate_group_returns(
        self,
        groups: List[GroupResult],
        stock_returns: pd.DataFrame,
        weights_list: List[np.ndarray] = None
    ) -> List[GroupReturn]:
        """计算各分组收�?""

        if weights_list is None:
            weights_list = [g.weights for g in groups]

        results = []

        for i, (group, weights) in enumerate(zip(groups, weights_list)):
            stocks = group.stocks

            if not stocks:
                continue

            period_returns = stock_returns[stocks].loc[group.start_date:group.end_date]

            if len(period_returns) == 0:
                continue

            portfolio_returns = (period_returns * weights).sum(axis=1)

            total_return = (1 + portfolio_returns).prod() - 1
            volatility = portfolio_returns.std() * np.sqrt(252)
            sharpe = (portfolio_returns.mean() * 252 - self.risk_free_rate) / volatility if volatility > 0 else 0

            cumulative = (1 + portfolio_returns).cumprod()
            max_dd = (cumulative / cumulative.cummax() - 1).min()

            results.append(GroupReturn(
                group_id=i + 1,
                period=f"{group.start_date} to {group.end_date}",
                return_value=total_return,
                cumulative_return=total_return,
                volatility=volatility,
                sharpe_ratio=sharpe,
                max_drawdown=max_dd
            ))

        return results

    def analyze_monotonicity(
        self,
        group_returns: List[GroupReturn]
    ) -> Dict:
        """分析收益单调�?

        返回:
            单调性分析结�?
        """
        returns = [g.return_value for g in group_returns]
        groups = [g.group_id for g in group_returns]

        spearman_corr = pd.Series(returns).corr(pd.Series(groups), method="spearman")

        is_monotonic = all(
            returns[i] >= returns[i+1] for i in range(len(returns)-1)
        )

        monotonic_decrease = all(
            returns[i] <= returns[i+1] for i in range(len(returns)-1)
        )

        return {
            "is_monotonic_increasing": is_monotonic,
            "is_monotonic_decreasing": monotonic_decrease,
            "spearman_correlation": spearman_corr,
            "top_bottom_spread": returns[-1] - returns[0] if len(returns) > 0 else 0,
            "returns_by_group": dict(zip(groups, returns))
        }

    def generate_returns_report(
        self,
        group_returns: List[GroupReturn],
        monotonicity: Dict
    ) -> str:
        """生成分组收益报告"""
        lines = ["=" * 80, "分层回测收益报告", "=" * 80, ""]

        lines.append("分组收益:")
        lines.append("-" * 80)
        lines.append(f"{'组号':<8}{'收益�?:<12}{'年化波动':<12}{'夏普比率':<12}{'最大回�?:<12}")
        lines.append("-" * 80)

        for g in group_returns:
            lines.append(
                f"{g.group_id:<8}{g.return_value:>10.2%}  "
                f"{g.volatility:>10.2%}  {g.sharpe_ratio:>10.2f}  {g.max_drawdown:>10.2%}"
            )

        lines.append("-" * 80)

        lines.append("")
        lines.append("单调性分�?")
        lines.append(f"  斯皮尔曼相关系数: {monotonicity['spearman_correlation']:.4f}")
        lines.append(f"  多头-空头利差: {monotonicity['top_bottom_spread']:.2%}")
        lines.append(f"  是否单调递增: {'�? if monotonicity['is_monotonic_increasing'] else '�?}")

        return "\n".join(lines)
```

---

## 5. 统计检验模�?

### 5.1 因子有效性检�?

```python
from scipy import stats


class StatisticalTester:
    """统计检验器"""

    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level

    def t_test_group_return(
        self,
        portfolio_returns: pd.Series,
        benchmark: float = 0
    ) -> Dict:
        """单样本t检�?

        检验组合收益是否显著不同于基准

        返回:
            t检验结�?
        """
        returns = portfolio_returns.dropna()

        if len(returns) < 2:
            return {"error": "Insufficient data"}

        t_stat, p_value = stats.ttest_1samp(returns, benchmark)

        return {
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < (1 - self.confidence_level),
            "mean_return": returns.mean(),
            "std_error": returns.std() / np.sqrt(len(returns))
        }

    def cross_sectional_regression(
        self,
        factor_values: pd.DataFrame,
        stock_returns: pd.Series,
        risk_factors: pd.DataFrame = None
    ) -> Dict:
        """横截面回归分�?

        检验因子收益率的显著�?

        参数:
            factor_values: 因子�?(index=date, columns=factor_names)
            stock_returns: 股票收益�?
            risk_factors: 风险因子

        返回:
            回归结果
        """
        valid_idx = factor_values.dropna().index.intersection(stock_returns.dropna().index)

        if len(valid_idx) < 30:
            return {"error": "Insufficient observations"}

        X = factor_values.loc[valid_idx].values
        y = stock_returns.loc[valid_idx].values

        if risk_factors is not None:
            X = np.column_stack([X, risk_factors.loc[valid_idx].values])

        X = np.column_stack([np.ones(len(X)), X])

        try:
            beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)

            y_pred = X @ beta
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - y.mean()) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

            n = len(y)
            k = X.shape[1]
            mse = ss_res / (n - k)
            se = np.sqrt(mse * np.diag(np.linalg.inv(X.T @ X)))

            t_stats = beta / se
            p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - k))

            return {
                "coefficients": beta[1:],
                "t_statistics": t_stats[1:],
                "p_values": p_values[1:],
                "r_squared": r_squared,
                "n_observations": n
            }

        except Exception as e:
            return {"error": str(e)}

    def factor_returns_test(
        self,
        factor_values: pd.Series,
        stock_returns: pd.DataFrame,
        holding_period: int = 1
    ) -> pd.DataFrame:
        """计算并检验因子收益率

        参数:
            factor_values: 因子�?
            stock_returns: 股票收益
            holding_period: 持有�?

        返回:
            因子收益率时间序�?
        """
        factor_df = factor_values.to_frame("factor")
        merged = stock_returns.join(factor_df, how="inner")

        merged = merged.dropna()

        if len(merged) < 30:
            return pd.DataFrame()

        factor_returns = []

        for i in range(0, len(merged) - holding_period, holding_period):
            period_data = merged.iloc[i:i + holding_period]

            factor_quantile = pd.qcut(
                period_data["factor"],
                q=5,
                labels=False,
                duplicates="drop"
            )

            quantile_returns = period_data.assign(quantile=factor_quantile).groupby("quantile")[stock_returns.columns[0]].mean()

            long_short = quantile_returns.iloc[-1] - quantile_returns.iloc[0]
            factor_returns.append(long_short)

        return pd.Series(factor_returns, name="factor_return")

    def garch_volatility_test(
        self,
        returns: pd.Series
    ) -> Dict:
        """GARCH波动率模型检�?""
        from arch import arch_model

        try:
            model = arch_model(returns * 100, vol="Garch", p=1, q=1)
            result = model.fit(disp="off")

            return {
                "omega": result.params.get("omega", 0),
                "alpha": result.params.get("alpha[1]", 0),
                "beta": result.params.get("beta[1]", 0),
                "persistence": result.params.get("alpha[1]", 0) + result.params.get("beta[1]", 0),
                "aic": result.aic,
                "bic": result.bic
            }

        except Exception as e:
            return {"error": str(e)}
```

---

## 6. 使用示例

### 6.1 完整分层回测流程

```python
def run_layered_backtest():
    """执行分层回测"""

    datahub = DataHub()
    factor_calc = FactorCalculator()

    stocks = datahub.get_stock_list(date="2025-01-01")
    ohlcv = datahub.get_ohlcv(stocks, "2025-01-01", "2025-12-31")

    factor = factor_calc.calculate("ALPHA_001", ohlcv)

    returns = ohlcv.pct_change().dropna()

    grouper = EqualNumberGrouper(n_groups=10)
    groups = grouper.group(factor, returns)

    builder = PortfolioBuilder()
    ls_portfolio = builder.build_long_short_portfolio(
        groups,
        long_group=10,
        short_group=1
    )

    analyzer = ReturnAnalyzer()
    group_returns = analyzer.calculate_group_returns(groups, returns)
    monotonicity = analyzer.analyze_monotonicity(group_returns)

    tester = StatisticalTester()

    print(analyzer.generate_returns_report(group_returns, monotonicity))

    for group in group_returns:
        test_result = tester.t_test_group_return(
            returns[group.stocks].mean(axis=1)
        )
        print(f"Group {group.group_id}: t={test_result.get('t_statistic', 0):.2f}, p={test_result.get('p_value', 1):.4f}")
```

---

**版本**: 1.0
**更新**: 2026-03-28
**Layer**: Layer 2 (Alpha因子计算)
**索引**: BLUEPRINTS.md �?因子验证框架蓝图
**上游接口**: FactorCalculator (M02), DataHub (M01)
**下游接口**: FactorLibrary (M02.5), StrategyEngine (M03)

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
