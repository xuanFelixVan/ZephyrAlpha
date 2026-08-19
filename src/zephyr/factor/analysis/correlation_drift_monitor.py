# [BLUEPRINT] 23_strategy_correlation_validation.md §5.4 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/
# [MODULE] zephyr.factor.analysis.correlation_drift_monitor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] G07 上线后相关性漂移持续监控（复用 deadman/reconciler 监控风格, 函数级）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数无IO; CUSUM只检上行漂移(S⁺单边); σ=0降级不告警; PSI分箱基于基线分位
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空序列->ValueError; σ=0/常数基线->degraded标记不告警
# [TESTS] tests/factor/test_correlation_drift_monitor.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 滚动63日Spearman ρ_t序列(每策略对) + 基线ρ₀(block-bootstrap验证基线) + 可选基线/近期分布
# F1: CUSUM S⁺ₜ=max(0,S⁺ₜ₋₁+(ρ_t−ρ₀)−k), k=0.5σ, h=4σ(~0.5次/年误报, 检测延迟~50交易日)
# F2: PSI=Σ(recent%−base%)·ln(recent%/base%), >0.2调查/>0.4告警(quantile分箱+eps兜底)
# A1: compute_rolling_spearman(窗口内秩相关, 逐窗重排名精确版)
# A2: cusum_upper_alarm(单边CUSUM→告警/首个告警位/S⁺轨迹/degraded)
# A3: population_stability_index(基线vs近期ρ分布PSI)
# A4: assess_pair_drift(单对一站式: CUSUM主检测+PSI辅助→PairDriftReport)
# O1: CusumResult / PSI值 / PairDriftReport(cusum_alarm+psi_level+degraded)
# [/ALGO_FLOW]
"""D_FACTOR — G07 §5.4 相关性漂移监控（上线后持续，函数级）

§3.2 block-bootstrap 验证施工前静态相关性；上线后相关性会漂移（regime 变化/
拥挤度上升/共同因子暴露变化），<0.6 的组合可能漂到 >0.8——分散假设静默失效。

  - CUSUM on rolling correlation（主检测器，MathAndMarkets 2026-02 参数
    k=0.5σ/h=4σ，~0.5 次/年误报、检测延迟 ~50 交易日；A 股打板波动更大，
    参数待首批实盘标定——memo §6 待裁定）
  - PSI on correlation distribution（辅助，stockalpha 2026-02：>0.2 调查 / >0.4 告警）
  - 分级响应（告警→权重×0.5→停新入场→重跑 block-bootstrap）由调用方编排，
    本模块只产出检测结论；复用 deadman/reconciler 基础设施风格（轻量状态机 +
    dataclass 报告 + degraded 降级标记），不新建独立监控系统。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

__all__ = [
    "CUSUM_H_SIGMA",
    "CUSUM_K_SIGMA",
    "DEFAULT_ROLLING_WINDOW",
    "PSI_ALERT",
    "PSI_INVESTIGATE",
    "CusumResult",
    "PairDriftReport",
    "PsiLevel",
    "assess_pair_drift",
    "compute_rolling_spearman",
    "cusum_upper_alarm",
    "population_stability_index",
]

#: 滚动相关默认窗口（23 号 memo §5.4: 63 日）
DEFAULT_ROLLING_WINDOW = 63
#: CUSUM 参数（MathAndMarkets 2026-02 经验值；k=0.5σ / h=4σ）
CUSUM_K_SIGMA = 0.5
CUSUM_H_SIGMA = 4.0
#: PSI 阈值（stockalpha 2026-02：>0.2 调查 / >0.4 告警）
PSI_INVESTIGATE = 0.2
PSI_ALERT = 0.4
#: PSI 分箱零占比兜底
_PSI_EPS = 1e-6


class PsiLevel(str, Enum):
    """PSI 分级（严重度递增）。"""

    STABLE = "STABLE"
    INVESTIGATE = "INVESTIGATE"
    ALERT = "ALERT"


@dataclass(frozen=True)
class CusumResult:
    """CUSUM 检测结果（不可变）。

    Attributes:
        alarm: 是否触发告警（S⁺ > h 至少一次）
        first_alarm_pos: 首个告警位置（ρ 序列内整数位置；无告警 None）
        s_plus: S⁺ 轨迹 Series（与输入同 index）
        k/h: 实际使用的偏移量与阈值
        degraded: σ=0/样本不足降级（无法检测，不告警）
    """

    alarm: bool
    first_alarm_pos: int | None
    s_plus: pd.Series
    k: float
    h: float
    degraded: bool = False


@dataclass(frozen=True)
class PairDriftReport:
    """单策略对漂移报告（不可变）。

    Attributes:
        cusum: CUSUM 主检测结果
        psi: 基线 vs 近期 ρ 分布 PSI（未给分布时 None）
        psi_level: PSI 分级（未给分布时 STABLE）
        drift_detected: 综合判定（CUSUM 告警 或 PSI≥ALERT）
    """

    cusum: CusumResult
    psi: float | None
    psi_level: PsiLevel
    drift_detected: bool


def _spearman_1d(x: np.ndarray, y: np.ndarray) -> float:
    """两等长一维数组的 Spearman 秩相关（窗口内重排名，常数窗返回 nan）。"""
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    sx, sy = rx.std(), ry.std()
    if sx == 0.0 or sy == 0.0:
        return float("nan")
    return float(((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy))


def compute_rolling_spearman(
    series_a: pd.Series, series_b: pd.Series, window: int = DEFAULT_ROLLING_WINDOW
) -> pd.Series:
    """滚动 Spearman ρ_t（每窗口内重排名的精确版，非全样本排名的 Pearson 近似）。

    Args:
        series_a/series_b: 收益率序列（按 index 交集对齐）
        window: 滚动窗口（默认 63 交易日）

    Returns:
        ρ_t Series（前 window−1 位为 NaN；常数窗为 NaN）

    Raises:
        ValueError: window<2 / 对齐后样本不足
    """
    if window < 2:
        raise ValueError(f"window 必须 >=2, got {window}")
    aligned = pd.concat([series_a, series_b], axis=1).dropna()
    if len(aligned) < window:
        raise ValueError(f"对齐后样本 {len(aligned)} < window {window}")
    a = aligned.iloc[:, 0].to_numpy(dtype=float)
    b = aligned.iloc[:, 1].to_numpy(dtype=float)
    out = np.full(len(aligned), np.nan)
    for end in range(window, len(aligned) + 1):
        out[end - 1] = _spearman_1d(a[end - window : end], b[end - window : end])
    return pd.Series(out, index=aligned.index)


def cusum_upper_alarm(
    rho_series: pd.Series,
    baseline_rho: float,
    k: float | None = None,
    h: float | None = None,
    sigma: float | None = None,
) -> CusumResult:
    """单边上行 CUSUM：S⁺ₜ=max(0, S⁺ₜ₋₁+(ρ_t−ρ₀)−k)，S⁺>h 告警。

    只检测相关性**结构性上升**（分散失效方向）；NaN ρ（滚动窗口预热段）跳过。

    Args:
        rho_series: 滚动相关 ρ_t 序列
        baseline_rho: 验证基线 ρ₀（block-bootstrap 产出）
        k: 偏移量（None=0.5σ）
        h: 告警阈值（None=4σ）
        sigma: ρ_t 标准差（None=序列 std(ddof=1)；σ=0→degraded 不告警）

    Returns:
        CusumResult

    Raises:
        ValueError: 空序列
    """
    if rho_series is None or len(rho_series) == 0:
        raise ValueError("rho_series 不能为空")
    valid = rho_series.dropna()
    sig = float(valid.std(ddof=1)) if sigma is None else float(sigma)
    if not math.isfinite(sig) or sig <= 0.0 or len(valid) < 2:
        nan_track = pd.Series(np.nan, index=rho_series.index)
        return CusumResult(False, None, nan_track, 0.0, 0.0, degraded=True)
    k_eff = CUSUM_K_SIGMA * sig if k is None else k
    h_eff = CUSUM_H_SIGMA * sig if h is None else h

    s_plus = pd.Series(np.nan, index=rho_series.index, dtype=float)
    s = 0.0
    first_alarm: int | None = None
    for pos, (idx, rho) in enumerate(rho_series.items()):
        if math.isnan(rho):
            continue
        s = max(0.0, s + (float(rho) - baseline_rho) - k_eff)
        s_plus.loc[idx] = s
        if first_alarm is None and s > h_eff:
            first_alarm = pos
    return CusumResult(first_alarm is not None, first_alarm, s_plus, k_eff, h_eff)


def population_stability_index(
    baseline: list[float] | np.ndarray | pd.Series,
    recent: list[float] | np.ndarray | pd.Series,
    n_bins: int = 10,
) -> float:
    """PSI（Population Stability Index）：基线 vs 近期 ρ 分布漂移度。

    分箱取基线分位数边界（等频）；占比 <eps 以 eps 兜底。常数基线（分位边界
    全部相同）退化为 0.0（无分布差异可测）。

    Args:
        baseline: 基线期 ρ 样本
        recent: 近期 ρ 样本（如近 63 日）
        n_bins: 分箱数（默认 10）

    Returns:
        PSI ≥0（>0.2 调查 / >0.4 告警）

    Raises:
        ValueError: 空输入 / n_bins<2
    """
    base = np.asarray(list(baseline), dtype=float)
    rec = np.asarray(list(recent), dtype=float)
    base = base[np.isfinite(base)]
    rec = rec[np.isfinite(rec)]
    if len(base) == 0 or len(rec) == 0:
        raise ValueError("baseline/recent 不能为空")
    if n_bins < 2:
        raise ValueError(f"n_bins 必须 >=2, got {n_bins}")
    edges = np.unique(np.quantile(base, np.linspace(0, 1, n_bins + 1)))
    if len(edges) < 2:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    base_prop = np.histogram(base, bins=edges)[0] / len(base)
    rec_prop = np.histogram(rec, bins=edges)[0] / len(rec)
    base_prop = np.clip(base_prop, _PSI_EPS, None)
    rec_prop = np.clip(rec_prop, _PSI_EPS, None)
    return float(np.sum((rec_prop - base_prop) * np.log(rec_prop / base_prop)))


def assess_pair_drift(
    rho_series: pd.Series,
    baseline_rho: float,
    baseline_dist: list[float] | np.ndarray | pd.Series | None = None,
    recent_dist: list[float] | np.ndarray | pd.Series | None = None,
    *,
    k: float | None = None,
    h: float | None = None,
    sigma: float | None = None,
    n_bins: int = 10,
) -> PairDriftReport:
    """单策略对一站式漂移评估：CUSUM 主检测 + PSI 辅助。

    Args:
        rho_series: 滚动相关 ρ_t（compute_rolling_spearman 产出）
        baseline_rho: block-bootstrap 验证基线 ρ₀
        baseline_dist/recent_dist: 基线期/近期 ρ 分布样本（PSI；给全才算）
        k/h/sigma: CUSUM 参数覆盖（None=默认 0.5σ/4σ/序列 std）
        n_bins: PSI 分箱数

    Returns:
        PairDriftReport（drift_detected = CUSUM 告警 或 PSI≥0.4）
    """
    cusum = cusum_upper_alarm(rho_series, baseline_rho, k=k, h=h, sigma=sigma)
    psi: float | None = None
    psi_level = PsiLevel.STABLE
    if baseline_dist is not None and recent_dist is not None:
        psi = population_stability_index(baseline_dist, recent_dist, n_bins=n_bins)
        psi_level = (
            PsiLevel.ALERT
            if psi > PSI_ALERT
            else (PsiLevel.INVESTIGATE if psi > PSI_INVESTIGATE else PsiLevel.STABLE)
        )
    return PairDriftReport(
        cusum=cusum,
        psi=psi,
        psi_level=psi_level,
        drift_detected=cusum.alarm or psi_level is PsiLevel.ALERT,
    )
