# [BLUEPRINT] 23_strategy_correlation_validation.md §3.1⑤第4部分 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/
# [MODULE] zephyr.factor.analysis.correlation_neff
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] G07 策略相关性验证报告（组合层有效下注数）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数无IO; 收缩矩阵对称半正定; alpha∈[0,1]; Neff=(Σλ)²/Σλ²∈[1,N]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 常数列/含NaN/列数<1/样本<2->ValueError
# [TESTS] tests/factor/test_correlation_neff.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 对齐收益率面板(T×k)
# F1: Ledoit-Wolf收缩(标准化→S=相关矩阵, 目标F=I; d²=||S−I||²_F/p, b̄²=(1/pT²)Σ||z_tz_tᵀ−S||²_F, α=min(b̄²,d²)/d²)
# F2: α双重用途(收缩强度本身=组合相关结构噪声信号; α大即使Neff≥3也应警惕)
# A1: ledoit_wolf_shrinkage(闭式最优α→S*=(1−α)S+αI, 保证正定稳定特征值)
# A2: effective_bets(特征值分解Neff=(Σλ)²/Σλ²; 等相关近似N/(1+(N−1)ρ̄)仅辅助)
# O1: ShrinkageResult(shrunk_corr+alpha) / NeffResult(neff+alpha+eigenvalues+neff_equicorr)
# [/ALGO_FLOW]
"""D_FACTOR — G07 组合层有效下注数 Neff 引擎（23 号 memo §3.1⑤）

Neff=(Σλ)²/Σλ² 衡量组合真正有多少独立风险方向——两两相关都 <0.6 但 Neff<3
仍危险（5 策略实际只有 <3 个独立下注，stockalpha 2026-02）。

数值稳定性前置（Ledoit-Wolf 收缩，metricgate 2026-03）：5 策略高度相关时
（正是本验证要检测的情况）样本相关矩阵近奇异、最小特征值≈0、特征值分解不稳定；
先收缩 S*=(1−α)S+αI（闭式最优 α）再分解。

自洽性说明（memo v1.4.1）：收缩后 Neff 偏乐观（收缩拉高最小特征值），Neff<3
判据需结合 α 共读——α 大（重收缩）即使 Neff≥3 也应警惕；α 小+Neff≥3 才稳健。
等相关近似 Neff≈N/(1+(N−1)ρ̄) 仅辅助（Soloviov 2026 警告 PnL stream 偏差
−56%~+91%），以特征值分解为准。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = [
    "NeffResult",
    "ShrinkageResult",
    "effective_bets",
    "equicorrelation_neff",
    "ledoit_wolf_shrinkage",
]

#: 特征值数值负零裁剪容差
_EIG_CLIP = 1e-12


@dataclass(frozen=True)
class ShrinkageResult:
    """Ledoit-Wolf 收缩结果（不可变）。

    Attributes:
        shrunk_corr: 收缩后相关矩阵（对称半正定，ndarray k×k）
        alpha: 闭式最优收缩强度 ∈[0,1]（α 大=噪声大/相关结构弱）
        sample_corr: 原始样本相关矩阵
    """

    shrunk_corr: np.ndarray
    alpha: float
    sample_corr: np.ndarray


@dataclass(frozen=True)
class NeffResult:
    """Neff 计算结果（不可变）。

    Attributes:
        neff: 有效下注数 (Σλ)²/Σλ² ∈[1,N]
        alpha: Ledoit-Wolf 收缩强度（shrink=False 时 0.0）
        eigenvalues: 收缩后矩阵特征值（升序，数值负零已裁剪）
        neff_equicorr: 等相关近似 N/(1+(N−1)ρ̄)（仅辅助对照）
        n_assets: 策略数 N
    """

    neff: float
    alpha: float
    eigenvalues: np.ndarray
    neff_equicorr: float
    n_assets: int


def _as_panel(panel: pd.DataFrame | np.ndarray) -> np.ndarray:
    x = panel.to_numpy(dtype=float) if isinstance(panel, pd.DataFrame) else np.asarray(panel, dtype=float)
    if x.ndim != 2 or x.shape[1] < 1:
        raise ValueError("panel 必须为 2 维 (T×k)")
    if x.shape[0] < 2:
        raise ValueError(f"样本不足: T={x.shape[0]} < 2")
    if np.isnan(x).any():
        raise ValueError("panel 含 NaN——请先交易日对齐（correlation_preprocessing）")
    return x


def _standardize(x: np.ndarray) -> np.ndarray:
    """列标准化（ddof=0），使 ZᵀZ/T 恰为样本相关矩阵。常数列拒绝。"""
    std = x.std(axis=0)
    if (std == 0.0).any():
        raise ValueError("存在常数列（方差为 0），相关矩阵无定义")
    return (x - x.mean(axis=0)) / std


def ledoit_wolf_shrinkage(panel: pd.DataFrame | np.ndarray) -> ShrinkageResult:
    """Ledoit-Wolf 闭式最优收缩（相关矩阵版，目标 F=I）。

    S*=（1−α)S+αI；d²=||S−I||²_F/p；b̄²=(1/(pT²))Σ_t||z_tz_tᵀ−S||²_F；
    α=min(b̄²,d²)/d² ∈[0,1]。利用 ||z_tz_tᵀ−S||²_F=(z_tᵀz_t)²−2z_tᵀSz_t+||S||²_F
    向量化，避免显式构造 T 个 k×k 矩阵。

    Args:
        panel: T×k 对齐收益率面板

    Returns:
        ShrinkageResult
    """
    x = _as_panel(panel)
    z = _standardize(x)
    t, p = z.shape
    s = (z.T @ z) / t  # 样本相关矩阵
    if p == 1:
        return ShrinkageResult(s.copy(), 0.0, s)
    diff = s - np.eye(p)
    d2 = float((diff * diff).sum()) / p  # ||S−I||²_F / p
    if d2 <= 0.0:  # S 已是单位阵 → 无需收缩
        return ShrinkageResult(s.copy(), 0.0, s)
    z_norm2 = (z * z).sum(axis=1)  # z_tᵀz_t
    zsz = np.einsum("ti,ij,tj->t", z, s, z)
    s_frob2 = float((s * s).sum())
    b_bar2 = float((z_norm2 * z_norm2).sum() - 2.0 * zsz.sum() + t * s_frob2) / (p * t * t)
    b2 = min(max(b_bar2, 0.0), d2)
    alpha = b2 / d2
    shrunk = (1.0 - alpha) * s + alpha * np.eye(p)
    return ShrinkageResult(shrunk, alpha, s)


def equicorrelation_neff(corr: np.ndarray) -> float:
    """等相关近似 Neff≈N/(1+(N−1)ρ̄)（ρ̄=平均两两相关，仅辅助对照）。

    Soloviov 2026 警告 PnL stream 偏差随共同因子载荷 β 从 −56% 到 +91%，
    结论以特征值分解 Neff 为准。
    """
    c = np.asarray(corr, dtype=float)
    n = c.shape[0]
    if n < 2:
        return 1.0
    off = c[~np.eye(n, dtype=bool)]
    rho_bar = float(off.mean())
    denom = 1.0 + (n - 1) * rho_bar
    if abs(denom) < _EIG_CLIP:
        return float("nan")
    return n / denom


def effective_bets(
    panel: pd.DataFrame | np.ndarray, shrink: bool = True
) -> NeffResult:
    """组合层有效下注数 Neff=(Σλ)²/Σλ²（特征值分解，可选 LW 收缩前置）。

    Args:
        panel: T×k 对齐收益率面板
        shrink: 是否先做 Ledoit-Wolf 收缩（默认 True，memo §3.1⑤ 强制前置）

    Returns:
        NeffResult（neff/alpha/eigenvalues/neff_equicorr/n_assets）
    """
    x = _as_panel(panel)
    t, p = x.shape
    if p == 1:
        return NeffResult(1.0, 0.0, np.array([1.0]), 1.0, 1)
    if shrink:
        shr = ledoit_wolf_shrinkage(x)
        mat, alpha, sample = shr.shrunk_corr, shr.alpha, shr.sample_corr
    else:
        z = _standardize(x)
        sample = (z.T @ z) / t
        mat, alpha = sample, 0.0
    eigvals = np.linalg.eigvalsh(mat)
    eigvals = np.where(eigvals < 0.0, 0.0, eigvals)  # 数值负零裁剪（保持 PSD 语义）
    sum_sq = float(eigvals @ eigvals)
    neff = float(eigvals.sum()) ** 2 / sum_sq if sum_sq > 0 else float("nan")
    return NeffResult(neff, alpha, eigvals, equicorrelation_neff(sample), p)
