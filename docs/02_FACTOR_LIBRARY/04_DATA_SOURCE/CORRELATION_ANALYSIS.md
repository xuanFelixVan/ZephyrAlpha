# 相关性分析

> **模块编号**: M-CORR-001 (Correlation Analysis)
> **版本**: 1.0
> **创建日期**: 2026-03-28
> **优先级**: P1
> **依赖**: STATISTICAL_TOOLS.md

---

## 1. 概述

本文档是统计分析工具的补充，专注于**深入的相关性分析**方法，包括偏相关、条件相关、协整检验等高级主题。

> 基础相关系数计算请参考 [STATISTICAL_TOOLS.md](STATISTICAL_TOOLS.md) 中的 `CorrelationAnalysis` 类。

---

## 2. 偏相关分析

### 2.1 概念

偏相关（Partial Correlation）是指在控制其他变量影响后，两个变量之间的相关程度。

```
r_XY|Z = (r_XY - r_XZ * r_YZ) / sqrt((1-r_XZ²)(1-r_YZ²))
```

### 2.2 实现

```python
from typing import List
import pandas as pd
import numpy as np

class PartialCorrelation:
    """偏相关分析"""

    @staticmethod
    def compute(x: pd.Series,
               y: pd.Series,
               control_vars: List[pd.Series]) -> float:
        """
        计算偏相关系数

        参数:
            x: 变量X
            y: 变量Y
            control_vars: 控制变量列表

        返回:
            偏相关系数
        """
        from scipy import stats

        n = len(x)
        k = len(control_vars)

        if k == 0:
            return x.corr(y)

        # 构建设计矩阵
        X = np.column_stack([x.values] + [c.values for c in control_vars])

        # 残差化
        def residualize(series):
            from sklearn.linear_model import LinearRegression
            reg = LinearRegression()
            reg.fit(X, series.values)
            return series.values - reg.predict(X)

        x_resid = residualize(x)
        y_resid = residualize(y)

        # 计算残差的相关
        return np.corrcoef(x_resid, y_resid)[0, 1]

    @classmethod
    def compute_matrix(cls,
                      data: pd.DataFrame,
                      control_cols: List[str] = None) -> pd.DataFrame:
        """
        计算偏相关矩阵

        参数:
            data: 数据DataFrame
            control_cols: 控制变量列表，None表示计算简单相关
        """
        cols = data.columns.tolist()
        n = len(cols)
        result = pd.DataFrame(np.zeros((n, n)), index=cols, columns=cols)

        for i, col1 in enumerate(cols):
            for j, col2 in enumerate(cols):
                if i == j:
                    result.loc[col1, col2] = 1.0
                elif j > i:
                    if control_cols:
                        control_vars = [data[c] for c in control_cols]
                        pc = cls.compute(data[col1], data[col2], control_vars)
                    else:
                        pc = data[col1].corr(data[col2])
                    result.loc[col1, col2] = pc
                    result.loc[col2, col1] = pc

        return result
```

---

## 3. 条件相关性

### 3.1 概念

条件相关性（Conditional Correlation）分析在不同条件（或分组）下相关性的变化。

### 3.2 实现

```python
class ConditionalCorrelation:
    """条件相关性分析"""

    @staticmethod
    def by_quantile(data: pd.DataFrame,
                   x: str,
                   y: str,
                   condition_var: str,
                   n_quantiles: int = 3) -> pd.DataFrame:
        """
        按分位数分组计算相关性

        参数:
            data: 数据
            x, y: 相关变量
            condition_var: 条件变量
            n_quantiles: 分组数

        返回:
            各分位数组的相关性
        """
        results = []
        labels = [f'Q{i+1}' for i in range(n_quantiles)]
        quantile_labels = pd.qcut(data[condition_var], q=n_quantiles, labels=labels)

        for label in labels:
            subset = data[quantile_labels == label]
            if len(subset) > 5:
                corr = subset[x].corr(subset[y])
                results.append({
                    'condition_quantile': label,
                    'correlation': corr,
                    'sample_size': len(subset),
                    'significant': abs(corr) > 2 / np.sqrt(len(subset))
                })

        return pd.DataFrame(results)

    @staticmethod
    def rolling_correlation_stability(x: pd.Series,
                                      y: pd.Series,
                                      window: int = 60) -> Dict:
        """
        滚动相关性稳定性分析

        返回:
            {mean_corr, std_corr, stability_ratio, cv}
        """
        roll_corr = x.rolling(window).corr(y)

        mean_corr = roll_corr.mean()
        std_corr = roll_corr.std()
        stability_ratio = mean_corr / std_corr if std_corr > 0 else np.inf
        cv = std_corr / abs(mean_corr) if mean_corr != 0 else np.inf

        return {
            'mean_correlation': mean_corr,
            'std_correlation': std_corr,
            'stability_ratio': stability_ratio,
            'coefficient_of_variation': cv,
            'rolling_correlation': roll_corr,
            'is_stable': cv < 0.5  # CV < 0.5 认为稳定
        }
```

---

## 4. 相关性检验

### 4.1 相关系数显著性检验

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

        # t = r * sqrt(n-2) / sqrt(1-r²)
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
        Pearson相关系数的置信区间 (Fisher Z变换)

        参数:
            r: 相关系数
            n: 样本量
            confidence: 置信水平
        """
        from scipy import stats

        # Fisher Z变换
        z = 0.5 * np.log((1 + r) / (1 - r))
        se = 1 / np.sqrt(n - 3)

        # 置信区间
        z_alpha = stats.norm.ppf((1 + confidence) / 2)
        z_lower = z - z_alpha * se
        z_upper = z + z_alpha * se

        # 逆变换
        r_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
        r_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)

        return r_lower, r_upper
```

### 4.2 相关性差异检验

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

        # Fisher Z变换
        z1 = 0.5 * np.log((1 + r1) / (1 - r1))
        z2 = 0.5 * np.log((1 + r2) / (1 - r2))

        # Z统计量
        se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
        z_stat = (z1 - z2) / se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

        return {
            'z_statistic': z_stat,
            'p_value': p_value,
            'significant_005': p_value < 0.05,
            'significant_001': p_value < 0.01,
            'interpretation': '相关系数显著不同' if p_value < 0.05 else '相关系数无显著差异'
        }
```

---

## 5. 协整检验

### 5.1 概念

协整（Cointegration）检验两个非平稳时间序列之间是否存在长期均衡关系。

### 5.2 实现

```python
class CointegrationTest:
    """协整检验"""

    @staticmethod
    def engle_granger(y: pd.Series,
                     x: pd.Series) -> Dict:
        """
        Engle-Granger两步法协整检验

        步骤1: OLS回归 y = α + βx + ε
        步骤2: 检验ε的平稳性(ADF)
        """
        from statsmodels.tsa.stattools import adfuller

        # 步骤1: OLS回归
        import statsmodels.api as sm
        X = sm.add_constant(x)
        model = sm.OLS(y, X).fit()

        # 步骤2: 残差平稳性
        residuals = model.resid
        adf_result = adfuller(residuals, autolag='AIC')

        # 计算t统计量
        # H0: β = 1 (不存在协整)
        beta = model.params[x.name]
        se = model.bse[x.name]
        t_stat = (beta - 1) / se

        return {
            'hedge_ratio': beta,
            'intercept': model.params['const'],
            'adf_statistic': adf_result[0],
            'p_value': adf_result[1],
            'is_cointegrated': adf_result[1] < 0.05,
            'residuals': residuals,
            'regression_summary': model.summary()
        }

    @staticmethod
    def johansen(data: pd.DataFrame,
                det_order: int = 0,
                k_ar_diff: int = 1) -> Dict:
        """
        Johansen协整检验

        参数:
            data: 多变量时间序列
            det_order: 确定性项 (0=none, 1=constant, 2=trend)
            k_ar_diff: 差分滞后阶数

        返回:
            特征值迹检验和最大特征值检验结果
        """
        from statsmodels.tsa.vector_ar.vecm import coint_johansen

        result = coint_johansen(data, det_order, k_ar_diff)

        return {
            'eigenvalues': result.eig,
            'trace_stat': result.lr1,
            'trace_cvt': result.cvt[:, 1],  # 5%临界值
            'max_eigen_stat': result.lr2,
            'max_eigen_cvt': result.cvm[:, 1],  # 5%临界值
            'trace_reject': result.lr1 > result.cvt[:, 1],  # 是否拒绝H0
            'eigen_reject': result.lr2 > result.cvm[:, 1]
        }
```

### 5.3 协整对交易

```python
class CointegrationPairTrading:
    """协整配对交易"""

    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
        self.hedge_ratio = None
        self.spread = None

    def fit(self, price1: pd.Series, price2: pd.Series):
        """
        拟合配对
        """
        test_result = CointegrationTest.engle_granger(price1, price2)

        self.hedge_ratio = test_result['hedge_ratio']
        self.spread = price1 - self.hedge_ratio * price2

        return test_result

    def generate_signals(self,
                        price1: pd.Series,
                        price2: pd.Series,
                        window: int = 20) -> pd.DataFrame:
        """
        生成交易信号

        基于Z-Score均值回归
        """
        spread = price1 - self.hedge_ratio * price2
        zscore = (spread - spread.rolling(window).mean()) / spread.rolling(window).std()

        signals = pd.DataFrame(index=price1.index)
        signals['spread'] = spread
        signals['zscore'] = zscore
        signals['signal'] = 0

        # Z-Score均值回归策略
        signals.loc[zscore < -2, 'signal'] = 1   # 做多价差 (spread被低估)
        signals.loc[zscore > 2, 'signal'] = -1  # 做空价差
        signals.loc[abs(zscore) < 0.5, 'signal'] = 0  # 平仓

        return signals
```

---

## 6. 相关性衰减分析

### 6.1 相关性衰减检测

```python
class CorrelationDecayAnalysis:
    """相关性衰减分析"""

    @staticmethod
    def decay_over_lags(x: pd.Series,
                       y: pd.Series,
                       max_lag: int = 20) -> pd.DataFrame:
        """
        分析不同滞后期的相关性

        参数:
            x, y: 时间序列
            max_lag: 最大滞后期

        返回:
            各滞后期的相关系数
        """
        results = []

        for lag in range(0, max_lag + 1):
            if lag == 0:
                corr = x.corr(y)
            else:
                corr = x.iloc[:-lag].corr(y.iloc[lag:])

            results.append({
                'lag': lag,
                'correlation': corr,
                'abs_correlation': abs(corr)
            })

        return pd.DataFrame(results)

    @staticmethod
    def optimal_lag(x: pd.Series,
                   y: pd.Series,
                   max_lag: int = 20) -> int:
        """
        找到最优滞后期
        """
        decay = CorrelationDecayAnalysis.decay_over_lags(x, y, max_lag)
        optimal_idx = decay['abs_correlation'].idxmax()
        return decay.loc[optimal_idx, 'lag']
```

### 6.2 相关性预测

```python
class CorrelationForecasting:
    """相关性预测"""

    @staticmethod
    def predict_next_correlation(roll_corr: pd.Series,
                                 horizon: int = 1) -> float:
        """
        基于历史滚动相关预测未来相关性
        使用简单指数平滑
        """
        return roll_corr.ewm(span=20).mean().iloc[-1]

    @staticmethod
    def correlation regimes(roll_corr: pd.Series,
                           threshold: float = 0.5) -> pd.Series:
        """
        识别相关性 regime
        高相关 vs 低相关
        """
        return pd.Series(
            ['high' if c > threshold else 'low' for c in roll_corr],
            index=roll_corr.index
        )
```

---

## 7. 高维相关性

### 7.1 相关矩阵分解

```python
class CorrelationDecomposition:
    """相关矩阵分解"""

    @staticmethod
    def eigen_decomposition(corr_matrix: pd.DataFrame) -> Dict:
        """
        相关矩阵的特征值分解

        返回:
            特征值、方差解释比例、因子载荷
        """
        eigenvalues, eigenvectors = np.linalg.eigh(corr_matrix)

        # 排序
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        variance_explained = eigenvalues / eigenvalues.sum()
        cumulative_variance = np.cumsum(variance_explained)

        return {
            'eigenvalues': eigenvalues,
            'variance_explained': variance_explained,
            'cumulative_variance': cumulative_variance,
            'eigenvectors': eigenvectors,
            'n_factors_90': np.argmax(cumulative_variance >= 0.9) + 1,  # 解释90%方差所需因子数
            'n_factors_95': np.argmax(cumulative_variance >= 0.95) + 1
        }

    @staticmethod
    def clustering_by_correlation(data: pd.DataFrame,
                                  n_clusters: int = 3) -> pd.Series:
        """
        基于相关性聚类
        """
        from sklearn.cluster import AgglomerativeClustering

        corr_matrix = data.corr()
        distance_matrix = 1 - corr_matrix.abs()

        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric='precomputed',
            linkage='average'
        )

        labels = clustering.fit_predict(distance_matrix)

        return pd.Series(labels, index=data.columns, name='cluster')
```

---

## 8. 使用示例

```python
# 1. 偏相关分析
from statsmodels.regression.linear_model import OLS

# 计算控制GDP后的 PE与收益率偏相关
partial_corr = PartialCorrelation.compute(
    df['pe_ratio'],
    df['return'],
    [df['gdp_growth']]
)

# 2. 协整套利
pair = CointegrationPairTrading()
test = pair.fit(price_a, price_b)
signals = pair.generate_signals(price_a, price_b)

# 3. 相关性衰减
decay = CorrelationDecayAnalysis.decay_over_lags(factor1, returns, max_lag=20)
optimal_lag = CorrelationDecayAnalysis.optimal_lag(factor1, returns)

# 4. 相关性regime分析
roll_corr = df['factor'].rolling(60).corr(df['return'])
regimes = CorrelationForecasting.correlation_regimes(roll_corr, threshold=0.3)
```

---

## 9. 配置

```yaml
# config/correlation_analysis.yaml
correlation_analysis:
  partial_correlation:
    method: OLS  # OLS或linear_model

  cointegration:
    significance_level: 0.05
    max_ar_diff: 4

  pair_trading:
    entry_threshold: 2.0    # Z-Score入场阈值
    exit_threshold: 0.5    # Z-Score出场阈值
    lookback_window: 20     # 滚动窗口

  regimes:
    high_corr_threshold: 0.5
    low_corr_threshold: 0.2
```

---

**版本**: 1.0
**更新**: 2026-03-28
**状态**: 草稿
