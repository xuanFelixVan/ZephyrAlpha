# [BLUEPRINT] 23_strategy_correlation_validation.md §3.1① | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/
# [MODULE] zephyr.factor.analysis.correlation_preprocessing
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] zephyr.factor.analysis.correlation_block_bootstrap; zephyr.factor.analysis.correlation_sentiment_stratifier; zephyr.pf_alloc.core.strategy_correlation_gate(上游生产者)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数无IO; 对数收益率统一口径; 交易日对齐只交集禁前向填充; 异常值只标注不剔除
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->ValueError; 常数序列ADF->degraded标记; 对齐后为空->ValueError
# [TESTS] tests/factor/test_correlation_preprocessing.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 策略净值/价格序列 nav_map(dict[str, Series])
# F1: 对数收益率 r_t=ln(P_t/P_{t-1})(时间可加, 混用算术/对数致Pearson低估0.07-0.12)
# F2: ADF平稳性(自实现OLS+MacKinnon临界值插值, statsmodels非项目依赖, 同bhy_fdr纯numpy先例)
# F3: Modified Z-score异常值标注(MAD法, |M|>3.5, 不剔除, Spearman天然抗)
# A1: preprocess_strategy_returns(对数化+ADF+异常值标注+交易日交集对齐)
# A2: compute_strategy_correlation(策略级Pearson+Spearman双版本矩阵)
# O1: PreprocessResult(aligned_log_returns + adf + outliers) / 双版本相关矩阵
# [/ALGO_FLOW]
"""
D_FACTOR — G07 策略相关性验证·数据预处理 pipeline（23 号 memo §3.1①）

强制四步防伪相关（CSDN 2026-03 实证 38.6% 序列非平稳→伪相关率 61.2%）：
  1. 对数收益率统一 r_t=ln(P_t/P_{t-1})
  2. ADF 平稳性检验（p<0.05 才算 Pearson；非平稳标注 stationarity_warning）
  3. Modified Z-score 异常值标注（MAD 法，只标注不剔除）
  4. 交易日对齐（有效交易日交集，禁前向填充——前向填充使滚动相关标准差降 23%）

相关性必须用 PnL stream（收益率序列），禁用 binary 信号序列（tetrachoric 效应
使 binary 估计高估分散 56%，Soloviov 2026）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: prices 参数
#   fields: 参数 prices，类型注解 pd.Series
#   code: correlation_preprocessing.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: series 参数
#   fields: 参数 series，类型注解 pd.Series
#   code: correlation_preprocessing.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_lags 参数
#   fields: 参数 max_lags，类型注解 int | None
#   code: correlation_preprocessing.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: threshold 参数
#   fields: 参数 threshold，类型注解 float
#   code: correlation_preprocessing.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① to_log_returns
#   name_en: to_log_returns
#   intro: 对数收益率 r_t=ln(P_t/P_{t-1})。
#   desc: 对数收益率 r_t=ln(P_t/P_{t-1})。 Args: prices: 价格/净值序列（必须全为正，index 时间升序） Returns: 对数收益率序列（首期为 N…；源码 L211-L228
#   inputs: prices
#   outputs: pd.Series
# - id: A2
#   name_zh: ② adf_test
#   name_en: adf_test
#   intro: ADF 平稳性检验（含常数项、无趋势，自实现 OLS，statsmodels 非项目依赖）。
#   desc: ADF 平稳性检验（含常数项、无趋势，自实现 OLS，statsmodels 非项目依赖）。 回归：Δy_t = α + β·y_{t-1} + Σ_{i=1..L} γ_i·Δ…；源码 L244-L289
#   inputs: series max_lags
#   outputs: ADFTestResult
# - id: A3
#   name_zh: ③ modified_zscore_flags
#   name_en: modified_zscore_flags
#   intro: Modified Z-score 异常值标注（Iglewicz-Hoaglin，MAD 法，只标注不剔除）。
#   desc: Modified Z-score 异常值标注（Iglewicz-Hoaglin，MAD 法，只标注不剔除）。 M_i = 0.6745·(x_i − median)/MAD，|M…；源码 L292-L311
#   inputs: series threshold
#   outputs: pd.Series
# - id: A4
#   name_zh: ④ align_trading_days
#   name_en: align_trading_days
#   intro: 交易日对齐：仅保留所有策略均有值的日期交集，禁前向填充。
#   desc: 交易日对齐：仅保留所有策略均有值的日期交集，禁前向填充。 Args: returns_map: 策略名 → 收益率序列 Returns: 对齐面板 DataFrame（index…；源码 L314-L332
#   inputs: returns_map
#   outputs: pd.DataFrame
# - id: A5
#   name_zh: ⑤ preprocess_strategy_returns
#   name_en: preprocess_strategy_returns
#   intro: 预处理 pipeline：对数化 → ADF → 异常值标注 → 交易日交集对齐。
#   desc: 预处理 pipeline：对数化 → ADF → 异常值标注 → 交易日交集对齐。 Args: nav_map: 策略名 → 净值/价格序列 adf_max_lags: ADF…；源码 L335-L357
#   inputs: nav_map adf_max_lags outlier_threshold
#   outputs: PreprocessResult
# - id: A6
#   name_zh: ⑥ compute_strategy_correlation
#   name_en: compute_strategy_correlation
#   intro: 策略级 Pearson + Spearman 双版本相关矩阵（23 号 memo §3.1①）。
#   desc: 策略级 Pearson + Spearman 双版本相关矩阵（23 号 memo §3.1①）。 Pearson 对齐门禁 MOD-PA-004 消费口径；Spearman 抗打…；源码 L360-L387
#   inputs: returns_panel methods
#   outputs: dict[str, pd.DataFrame]
#   （注：A6 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: pd.Series
#   name_en: pd.Series
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.factor.analysis.correlation_block_bootstrap; zephyr.factor.analysis.corr…
# - id: O2
#   name_zh: ADFTestResult
#   name_en: ADFTestResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.factor.analysis.correlation_block_bootstrap; zephyr.factor.analysis.corr…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

__all__ = [
    "ADFSignificance",
    "ADFTestResult",
    "PreprocessResult",
    "adf_test",
    "align_trading_days",
    "compute_strategy_correlation",
    "modified_zscore_flags",
    "preprocess_strategy_returns",
    "to_log_returns",
]

#: ADF 判定平稳的 p 值阈值（23 号 memo §3.1①: p<0.05 才算 Pearson）
ADF_STATIONARY_P = 0.05
#: Modified Z-score 异常值阈值（Iglewicz-Hoaglin 3.5）
MODIFIED_ZSCORE_THRESHOLD = 3.5
#: ADF 最少样本数（低于此数回归无意义）
ADF_MIN_OBS = 10

# MacKinnon 渐近临界值（含常数项、无趋势 τ_c），决策临界区锚定公开精确值：
# 1% −3.43035 / 5% −2.86154 / 10% −2.56677；中位参考 −1.95（tau_star）。
# p 值由 log(p) 对 τ 分段线性插值近似，仅供 p<0.05 门禁判定，非精确分布。
_MACKINNON_TAU_P: tuple[tuple[float, float], ...] = (
    (-3.43035, 0.01),
    (-3.12000, 0.025),
    (-2.86154, 0.05),
    (-2.56677, 0.10),
    (-1.95000, 0.50),
)


class ADFSignificance:
    """ADF 退化标记常量。"""

    OK = "ok"
    CONSTANT_SERIES = "constant_series"
    INSUFFICIENT_SAMPLE = "insufficient_sample"


@dataclass(frozen=True)
class ADFTestResult:
    """ADF 检验结果（不可变）。

    Attributes:
        adf_stat: ADF τ 统计量（退化时为 nan）
        p_value: MacKinnon 插值近似 p 值（退化时 1.0，保守判非平稳）
        n_lags: 使用的滞后阶数（Schwert 规则 int(12·(n/100)^0.25)，上限 12）
        n_obs: 有效样本数
        is_stationary: p_value < 0.05
        note: 退化标记（ok / constant_series / insufficient_sample）
    """

    adf_stat: float
    p_value: float
    n_lags: int
    n_obs: int
    is_stationary: bool
    note: str = ADFSignificance.OK


@dataclass(frozen=True)
class PreprocessResult:
    """预处理产出（不可变）。

    Attributes:
        aligned_log_returns: 对齐后的对数收益率面板（index=交集交易日，columns=策略）
        adf: 策略 → ADFTestResult
        outliers: 策略 → 异常值布尔掩码（与对齐后面板同 index）
        stationarity_warnings: ADF 非平稳/退化的策略名列表（Pearson 慎用）
    """

    aligned_log_returns: pd.DataFrame
    adf: dict[str, ADFTestResult]
    outliers: dict[str, pd.Series]
    stationarity_warnings: list[str] = field(default_factory=list)


def to_log_returns(prices: pd.Series) -> pd.Series:
    """对数收益率 r_t=ln(P_t/P_{t-1})。

    Args:
        prices: 价格/净值序列（必须全为正，index 时间升序）

    Returns:
        对数收益率序列（首期为 NaN，由调用方对齐时丢弃）

    Raises:
        ValueError: 空序列或含非正值
    """
    if prices is None or len(prices) == 0:
        raise ValueError("prices 不能为空")
    values = prices.to_numpy(dtype=float)
    if np.any(values <= 0):
        raise ValueError("价格/净值必须全为正才能取对数")
    return pd.Series(np.log(values / np.roll(values, 1))[1:], index=prices.index[1:])


def _mackinnon_p_approx(tau: float) -> float:
    """MacKinnon 临界值表 log(p)-τ 分段线性插值近似 p 值。"""
    pts = _MACKINNON_TAU_P
    if tau <= pts[0][0]:  # 左尾外推后封顶下限
        slope = (math.log(pts[1][1]) - math.log(pts[0][1])) / (pts[1][0] - pts[0][0])
        return max(1e-4, math.exp(math.log(pts[0][1]) + slope * (tau - pts[0][0])))
    for (t0, p0), (t1, p1) in itertools.pairwise(pts):
        if t0 <= tau <= t1:
            w = (tau - t0) / (t1 - t0)
            return math.exp(math.log(p0) + w * (math.log(p1) - math.log(p0)))
    return 1.0  # τ 大于中位参考点 → 明显非平稳


def adf_test(series: pd.Series, max_lags: int | None = None) -> ADFTestResult:
    """ADF 平稳性检验（含常数项、无趋势，自实现 OLS，statsmodels 非项目依赖）。

    回归：Δy_t = α + β·y_{t-1} + Σ_{i=1..L} γ_i·Δy_{t-i} + ε_t，τ = β̂/se(β̂)。
    p 值为 MacKinnon 临界值插值近似（决策临界区 τ≈−2.86 锚定公开精确值）。

    Args:
        series: 收益率序列（NaN 自动丢弃）
        max_lags: 滞后阶数，None=Schwert 规则 min(12, int(12·(n/100)^0.25))

    Returns:
        ADFTestResult；常数序列/样本不足为退化（is_stationary=False + note）
    """
    y = pd.Series(series).dropna().to_numpy(dtype=float)
    n = len(y)
    if n < ADF_MIN_OBS:
        return ADFTestResult(float("nan"), 1.0, 0, n, False, ADFSignificance.INSUFFICIENT_SAMPLE)
    if float(np.std(y)) == 0.0:
        return ADFTestResult(float("nan"), 1.0, 0, n, False, ADFSignificance.CONSTANT_SERIES)

    lags = max_lags if max_lags is not None else min(12, int(12.0 * (n / 100.0) ** 0.25))
    lags = max(0, min(lags, (n - 4) // 2))  # 保证 n_eff > 回归元数
    dy = np.diff(y)
    n_eff = n - 1 - lags
    cols = [np.ones(n_eff), y[lags : n - 1]]
    for j in range(1, lags + 1):
        cols.append(dy[lags - j : n - 1 - j])
    x = np.column_stack(cols)
    dep = dy[lags:]
    try:
        beta, residuals, _, _ = np.linalg.lstsq(x, dep, rcond=None)
    except np.linalg.LinAlgError:
        return ADFTestResult(float("nan"), 1.0, lags, n, False, ADFSignificance.CONSTANT_SERIES)
    resid = dep - x @ beta
    dof = n_eff - x.shape[1]
    sigma2 = float(resid @ resid) / dof if dof > 0 else float("nan")
    try:
        cov_beta = sigma2 * np.linalg.inv(x.T @ x)
        se = math.sqrt(cov_beta[1, 1])
    except (np.linalg.LinAlgError, ValueError):
        se = float("nan")
    if not math.isfinite(se) or se <= 0:
        return ADFTestResult(float("nan"), 1.0, lags, n, False, ADFSignificance.CONSTANT_SERIES)
    tau = float(beta[1]) / se
    p_value = _mackinnon_p_approx(tau)
    return ADFTestResult(tau, p_value, lags, n, p_value < ADF_STATIONARY_P)


def modified_zscore_flags(series: pd.Series, threshold: float = MODIFIED_ZSCORE_THRESHOLD) -> pd.Series:
    """Modified Z-score 异常值标注（Iglewicz-Hoaglin，MAD 法，只标注不剔除）。

    M_i = 0.6745·(x_i − median)/MAD，|M_i| > threshold(默认3.5) 记异常。
    MAD=0（如常数序列）→ 全部非异常（无离群可判）。

    Args:
        series: 收益率序列
        threshold: 异常阈值，默认 3.5

    Returns:
        与输入同 index 的布尔 Series（True=异常值）
    """
    values = pd.Series(series).to_numpy(dtype=float)
    median = float(np.nanmedian(values))
    mad = float(np.nanmedian(np.abs(values - median)))
    if mad == 0.0:
        return pd.Series(False, index=series.index)
    mz = 0.6745 * (values - median) / mad
    return pd.Series(np.abs(mz) > threshold, index=series.index)


def align_trading_days(returns_map: dict[str, pd.Series]) -> pd.DataFrame:
    """交易日对齐：仅保留所有策略均有值的日期交集，禁前向填充。

    Args:
        returns_map: 策略名 → 收益率序列

    Returns:
        对齐面板 DataFrame（index=交集交易日升序，columns=策略名）

    Raises:
        ValueError: 空输入或对齐后无共同交易日
    """
    if not returns_map:
        raise ValueError("returns_map 不能为空")
    panel = pd.DataFrame(returns_map)
    aligned = panel.dropna(axis=0, how="any").sort_index()
    if aligned.empty:
        raise ValueError("交易日对齐后无共同交易日（交集为空）")
    return aligned


def preprocess_strategy_returns(
    nav_map: dict[str, pd.Series],
    adf_max_lags: int | None = None,
    outlier_threshold: float = MODIFIED_ZSCORE_THRESHOLD,
) -> PreprocessResult:
    """预处理 pipeline：对数化 → ADF → 异常值标注 → 交易日交集对齐。

    Args:
        nav_map: 策略名 → 净值/价格序列
        adf_max_lags: ADF 滞后阶数（None=Schwert 自动）
        outlier_threshold: Modified Z-score 阈值

    Returns:
        PreprocessResult（aligned_log_returns/adf/outliers/stationarity_warnings）
    """
    if not nav_map:
        raise ValueError("nav_map 不能为空")
    log_returns = {name: to_log_returns(nav) for name, nav in nav_map.items()}
    adf = {name: adf_test(r, max_lags=adf_max_lags) for name, r in log_returns.items()}
    aligned = align_trading_days(log_returns)
    outliers = {name: modified_zscore_flags(aligned[name], threshold=outlier_threshold) for name in aligned.columns}
    warnings = [name for name, r in adf.items() if not r.is_stationary]
    return PreprocessResult(aligned, adf, outliers, warnings)


def compute_strategy_correlation(
    returns_panel: pd.DataFrame, methods: tuple[str, ...] = ("pearson", "spearman")
) -> dict[str, pd.DataFrame]:
    """策略级 Pearson + Spearman 双版本相关矩阵（23 号 memo §3.1①）。

    Pearson 对齐门禁 MOD-PA-004 消费口径；Spearman 抗打板极端收益率。
    两者差异大时以 Spearman 为准并标注（调用方职责）。

    Args:
        returns_panel: 对齐后的收益率面板（index=交易日，columns=策略）
        methods: 相关方法子集（"pearson"/"spearman"）

    Returns:
        {method: 对称相关矩阵 DataFrame}

    Raises:
        ValueError: 面板为空/非 2 维/方法不支持
    """
    if returns_panel is None or returns_panel.empty:
        raise ValueError("returns_panel 不能为空")
    if returns_panel.ndim != 2 or returns_panel.shape[1] < 1:
        raise ValueError("returns_panel 必须为 2 维面板")
    result: dict[str, pd.DataFrame] = {}
    for method in methods:
        if method not in ("pearson", "spearman"):
            raise ValueError(f"不支持的相关方法: {method}（支持 pearson/spearman）")
        result[method] = returns_panel.corr(method=method)
    return result
