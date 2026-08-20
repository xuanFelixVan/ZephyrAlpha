# [BLUEPRINT] 23_strategy_correlation_validation.md §3.2 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/
# [MODULE] zephyr.factor.analysis.correlation_block_bootstrap
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] G07 策略相关性验证报告（施工前一次性）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数无IO; 多元同步行重采样(同一时间block对所有策略); 块长几何分布环绕索引; 禁止各列独立重采样(破坏同期相关)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 样本不足(<MIN_OBS)/列数<2->ValueError; 常数列PPW退化为b=1
# [TESTS] tests/factor/test_correlation_block_bootstrap.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 对齐收益率面板(T×k) + n_bootstrap(默认2000) + threshold(默认0.6战略级)
# F1: PPW b.star自动块长(Patton-Politis-White 2009: mhat显著滞后判定+flat-top窗Ghat/DSBhat)
# F2: stationary bootstrap索引(块长L~Geometric(1/b), 起点均匀, 环绕, 对齐walk_forward单变量版模式)
# A1: ppw_block_size(逐列b*取max, 钳[1,Bmax], Bmax=ceil(min(3√n,n/3)))
# A2: stationary_bootstrap_indices(生成长度T环绕索引一次, 全列共用=行重采样)
# A3: bootstrap_correlation_ci(2000×重采样→每对Pearson/Spearman的90%CI+P(ρ>0.6); Fisher z参数CI互验, 不一致以bootstrap为准)
# O1: BootstrapCIResult(per-pair CI/概率/点估计/块长)
# [/ALGO_FLOW]
"""D_FACTOR — G07 multivariate stationary block-bootstrap 引擎（23 号 memo §3.2）

Politis-Romano stationary bootstrap（块长几何分布）+ Patton-Politis-White (2009)
自动块长选择（b.star，估计值在真实最优 90%-110%），2000× **同步行重采样**——
同一时间 block 对所有策略同步重采样，保留 cross-sectional 同期相关结构
（tsbootstrap 2026-07 / SignalY 2026-02：各自独立重采样会破坏联合分布使 CI 失效）。

用途：每对策略相关性的 90% CI + P(ρ>0.6)，并与 Fisher z-transform 参数 CI 互验
（两者一致则结论稳健；不一致以 block-bootstrap 为准，因其不假设正态）。

与 walk_forward.whites_reality_check 的关系：既有实现为单变量（White RC 差分序列
专用），本模块为多元同步版（memo §7"复用还是新建"裁定：新建，复用其块生成模式）。
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = [
    "MIN_OBS",
    "BootstrapCIResult",
    "PairBootstrapCI",
    "bootstrap_correlation_ci",
    "fisher_z_ci",
    "ppw_block_size",
    "stationary_bootstrap_indices",
]

#: bootstrap 最小样本数（低于此数块重采样无意义）
MIN_OBS = 8
#: 默认重采样次数（Morwane 同量级 small project 验证通过；一次性施工前验证非 runtime）
DEFAULT_N_BOOTSTRAP = 2000
#: 战略级重新审视阈值（23 号 memo §3.1③；与门禁运营级 0.85/0.90 互补）
DEFAULT_CORR_THRESHOLD = 0.6
#: qnorm(0.975)，PPW 显著性临界常数
_QNORM_975 = 1.959963984540054


@dataclass(frozen=True)
class PairBootstrapCI:
    """单对策略相关性的 bootstrap 置信区间（不可变）。

    Attributes:
        point: 原始面板点估计
        ci_lower/ci_upper: bootstrap 百分位 CI
        prob_above_threshold: bootstrap 分布中 ρ>threshold 的频率
        fisher_ci_lower/fisher_ci_upper: Fisher z 参数 CI（互验用）
    """

    point: float
    ci_lower: float
    ci_upper: float
    prob_above_threshold: float
    fisher_ci_lower: float
    fisher_ci_upper: float


@dataclass(frozen=True)
class BootstrapCIResult:
    """bootstrap 相关矩阵 CI 结果（不可变）。

    Attributes:
        pearson/spearman: (策略A, 策略B) → PairBootstrapCI（仅 i<j 对）
        block_size: 实际使用的平均块长（PPW 自动或调用方指定）
        n_bootstrap: 重采样次数
        n_obs: 样本量 T
        confidence: CI 置信度（默认 0.90）
        threshold: 战略级阈值（默认 0.6）
    """

    pearson: dict[tuple[str, str], PairBootstrapCI]
    spearman: dict[tuple[str, str], PairBootstrapCI]
    block_size: int
    n_bootstrap: int
    n_obs: int
    confidence: float
    threshold: float


def _flat_top_lam(s: np.ndarray) -> np.ndarray:
    """Politis-Romano (1995) flat-top 滞后窗：|s|<0.5→1；0.5≤|s|≤1→2(1−|s|)；否则 0。"""
    a = np.abs(s)
    return np.where(a < 0.5, 1.0, np.where(a <= 1.0, 2.0 * (1.0 - a), 0.0))


def _autocovariances(x: np.ndarray, max_lag: int) -> np.ndarray:
    """R(k), k=0..max_lag（分母 n，与 R acf type="covariance" 一致）。"""
    n = len(x)
    xc = x - x.mean()
    out = np.empty(max_lag + 1)
    for k in range(max_lag + 1):
        out[k] = float(xc[k:] @ xc[: n - k]) / n
    return out


def _ppw_block_size_1d(x: np.ndarray) -> int:
    """Patton-Politis-White (2009) b.star 单列最优块长（stationary bootstrap 版）。

    步骤（对齐 R np::b.star）：
      Kn=max(5,⌈log10 n⌉)；mmax=⌈√n⌉+Kn；Bmax=⌈min(3√n, n/3)⌉；c=qnorm(0.975)
      mhat=首个使后续 Kn 个自相关系数全部不显著(|ρ|<c·√(log10 n /n))的滞后
      M=min(2·mhat, mmax)；Ghat=Σ λ(k/M)|k|R(k)；DSB=2·(Σ λ(k/M)R(k))²
      b*=(2·Ghat²/DSB)^{1/3}·n^{1/3}，钳 [1, Bmax]
    常数列（零方差）退化为 1。
    """
    n = len(x)
    b_max = int(math.ceil(min(3.0 * math.sqrt(n), n / 3.0)))
    if float(np.std(x)) == 0.0:
        return 1
    kn = max(5, int(math.ceil(math.log10(n))))
    mmax = int(math.ceil(math.sqrt(n))) + kn
    rho = _autocovariances(x, mmax)
    r0 = rho[0]
    rho = rho[1:] / r0  # ρ(1)..ρ(mmax)
    crit = _QNORM_975 * math.sqrt(math.log10(n) / n)

    mhat = 0
    n_runs = mmax - kn + 1
    for j in range(n_runs):  # j 为 0 基，对应滞后 j+1
        if int(np.sum(np.abs(rho[j : j + kn]) < crit)) == kn:
            mhat = j + 1
            break
    if mhat == 0:
        sig = np.nonzero(np.abs(rho) > crit)[0]
        mhat = int(sig[0] + 1) if len(sig) == 1 else (int(sig[-1] + 1) if len(sig) > 1 else 1)

    m = min(2 * mhat, mmax)
    r_k = _autocovariances(x, m)
    kk = np.arange(1, m + 1, dtype=float)
    lam = _flat_top_lam(kk / m)
    ghat = 2.0 * float(np.sum(lam * kk * r_k[1:]))  # |0|·R(0)=0，双侧对称 ×2
    dsb = 2.0 * (r_k[0] + 2.0 * float(np.sum(lam * r_k[1:]))) ** 2
    if dsb <= 0.0:
        return 1
    b_star = ((2.0 * ghat * ghat) / dsb) ** (1.0 / 3.0) * n ** (1.0 / 3.0)
    return max(1, min(b_max, int(round(b_star))))


def ppw_block_size(panel: pd.DataFrame | np.ndarray) -> int:
    """多元面板 PPW 自动块长：逐列 b.star 取 max（保留最强记忆列的依赖结构）。

    Args:
        panel: T×k 对齐收益率面板（DataFrame 或 ndarray）

    Returns:
        整数平均块长 ≥1
    """
    x = panel.to_numpy(dtype=float) if isinstance(panel, pd.DataFrame) else np.asarray(panel, dtype=float)
    if x.ndim != 2 or x.shape[1] < 1:
        raise ValueError("panel 必须为 2 维 (T×k)")
    if x.shape[0] < MIN_OBS:
        raise ValueError(f"样本不足: T={x.shape[0]} < {MIN_OBS}")
    return max(_ppw_block_size_1d(x[:, j]) for j in range(x.shape[1]))


def stationary_bootstrap_indices(n: int, avg_block_size: int, rng: np.random.Generator) -> np.ndarray:
    """Stationary bootstrap 环绕索引（Politis-Romano 1994）。

    块长 L~Geometric(p=1/avg_block)，块起点均匀随机，索引环绕（块可跨界）。
    全列共用同一索引序列即多元同步行重采样。

    Args:
        n: 样本长度 T
        avg_block_size: 平均块长（≥1）
        rng: numpy 随机数生成器（调用方持 seed 保证可复现）

    Returns:
        长度 n 的整数索引数组
    """
    if n < 1:
        raise ValueError(f"n 必须 >=1, got {n}")
    p_block = 1.0 / max(int(avg_block_size), 1)
    out = np.empty(n, dtype=np.int64)
    pos = 0
    while pos < n:
        block_len = int(rng.geometric(p_block))
        start = int(rng.integers(0, n))
        for j in range(block_len):
            if pos >= n:
                break
            out[pos] = (start + j) % n
            pos += 1
    return out


def fisher_z_ci(rho: float, n: int, confidence: float = 0.90) -> tuple[float, float]:
    """Fisher z-transform 参数 CI：z=atanh(ρ)~N(0, 1/(n−3))，CI=tanh(z±z_α/√(n−3))。

    与 block-bootstrap 非参数 CI 互验；不一致时以 bootstrap 为准（不假设正态）。
    |ρ|≥1 时 z 无定义，钳到 ±0.999999。
    """
    if n <= 3:
        raise ValueError(f"Fisher z 要求 n>3, got {n}")
    rho_c = max(-0.999999, min(0.999999, rho))
    z = math.atanh(rho_c)
    z_alpha = _norm_ppf((1.0 + confidence) / 2.0)
    half = z_alpha / math.sqrt(n - 3)
    return math.tanh(z - half), math.tanh(z + half)


def _norm_ppf(p: float) -> float:
    """标准正态逆 CDF（Acklam 有理逼近，避免 scipy 依赖）。"""
    a = [
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    ]
    b = [
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    ]
    c = [
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    ]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00, 3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    q = p - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5])
        * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )


def _rank_columns(x: np.ndarray) -> np.ndarray:
    """逐列秩变换（argsort 二次法；并列任意破序——日度浮点收益率并列罕见）。"""
    return np.argsort(np.argsort(x, axis=0), axis=0).astype(float)


def _pair_corr_stats(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pearson/Spearman 相关矩阵（Spearman=列秩变换后的 Pearson）。"""
    pearson = np.corrcoef(x, rowvar=False)
    spearman = np.corrcoef(_rank_columns(x), rowvar=False)
    return pearson, spearman


def bootstrap_correlation_ci(
    returns_panel: pd.DataFrame,
    n_bootstrap: int = DEFAULT_N_BOOTSTRAP,
    block_size: int = 0,
    confidence: float = 0.90,
    threshold: float = DEFAULT_CORR_THRESHOLD,
    seed: int | None = None,
) -> BootstrapCIResult:
    """Multivariate stationary block-bootstrap 相关性 90% CI + P(ρ>threshold)。

    每次重采样生成一次环绕索引并同步应用于所有列（行重采样），保留策略间
    同期相关结构；Pearson/Spearman 双版本；Fisher z 参数 CI 随附互验。

    Args:
        returns_panel: 对齐收益率面板（T×k，建议先经 correlation_preprocessing）
        n_bootstrap: 重采样次数（默认 2000，23 号 memo §3.2）
        block_size: 平均块长，0=PPW 自动（Patton-Politis-White 2009）
        confidence: CI 置信度（默认 0.90）
        threshold: 战略级相关阈值（默认 0.6，memo §3.1③）
        seed: 随机种子（None=不可复现）

    Returns:
        BootstrapCIResult

    Raises:
        ValueError: 列数<2 / 样本不足(T<MIN_OBS) / 含 NaN / n_bootstrap<1
    """
    if returns_panel is None or returns_panel.ndim != 2 or returns_panel.shape[1] < 2:
        raise ValueError("returns_panel 必须为 T×k 面板且 k>=2")
    if returns_panel.isna().any().any():
        raise ValueError("returns_panel 含 NaN——请先交易日对齐（correlation_preprocessing）")
    if n_bootstrap < 1:
        raise ValueError(f"n_bootstrap 必须 >=1, got {n_bootstrap}")
    x = returns_panel.to_numpy(dtype=float)
    t, k = x.shape
    if t < MIN_OBS:
        raise ValueError(f"bootstrap 样本不足: T={t} < {MIN_OBS}")
    b = block_size if block_size > 0 else ppw_block_size(x)

    names = list(returns_panel.columns)
    pairs = [(i, j) for i in range(k) for j in range(i + 1, k)]
    boot_p = np.empty((n_bootstrap, len(pairs)))
    boot_s = np.empty((n_bootstrap, len(pairs)))
    rng = np.random.default_rng(seed)
    for rep in range(n_bootstrap):
        idx = stationary_bootstrap_indices(t, b, rng)
        pm, sm = _pair_corr_stats(x[idx])
        for pi, (i, j) in enumerate(pairs):
            boot_p[rep, pi] = pm[i, j]
            boot_s[rep, pi] = sm[i, j]

    pm0, sm0 = _pair_corr_stats(x)
    alpha = (1.0 - confidence) / 2.0

    def _build(dist: np.ndarray, point_mat: np.ndarray) -> dict[tuple[str, str], PairBootstrapCI]:
        out: dict[tuple[str, str], PairBootstrapCI] = {}
        for pi, (i, j) in enumerate(pairs):
            col = dist[:, pi]
            col = col[np.isfinite(col)]
            point = float(point_mat[i, j])
            lo, hi = (
                (float(np.quantile(col, alpha)), float(np.quantile(col, 1 - alpha)))
                if len(col)
                else (float("nan"), float("nan"))
            )
            prob = float(np.mean(col > threshold)) if len(col) else float("nan")
            fz_lo, fz_hi = fisher_z_ci(point, t, confidence)
            out[(names[i], names[j])] = PairBootstrapCI(point, lo, hi, prob, fz_lo, fz_hi)
        return out

    return BootstrapCIResult(
        pearson=_build(boot_p, pm0),
        spearman=_build(boot_s, sm0),
        block_size=b,
        n_bootstrap=n_bootstrap,
        n_obs=t,
        confidence=confidence,
        threshold=threshold,
    )
