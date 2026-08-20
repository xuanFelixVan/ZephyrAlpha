# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.8.1
# [MODULE] zephyr.regime.features.lppl_detector
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] T4 疯狂期赶顶评估（独立函数，未接入 TRANSITION_CONFIG；T4 已有多维信号兜底）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] score∈[0,90]; 非正价格拒绝(ValueError); 序列不足 degraded(score=0 不抛); 纯 numpy lstsq 无外部 LPPL 库依赖
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非正价格->ValueError; 短序列->LPPLResult(degraded=True, score=0)
# [TESTS] tests/regime/features/test_lppl_detector.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.8.1 #T4 赶顶
# [ALGO_FLOW]
# I1: close 价格序列（index=日期；取末段多窗口拟合）
# F1: _lppl_fit_window（单窗口网格搜索：固定 (tc,m,ω) → y=A+B·dt^m+C1·dt^m·cos(ωln dt)+C2·dt^m·sin(ωln dt) 线性 lstsq，取 SSE 最小）
# F2: lppl_blowoff_score（多窗口拟合 → 五维评分映射：m/ω 经验区间 +20/+20，tc 中位≤20 日 +25，有效窗口占比>50% +15，tc 标准差<20 日 +10）
# O1: LPPLResult（score 0-90 + m/ω/tc 中位 + valid_window_ratio + degraded）
# [/ALGO_FLOW]
"""LPPL 赶顶检测（10_regime_detector_spec §4.8.1，T4 疯狂期）。

LPPL（Log-Periodic Power Law，Johansen & Sornette 学术源头，国金宏观 2026-06-14
实证 KOSPI/SOX）检测泡沫的超指数加速 + 对数周期震荡结构：

    ln E[p(t)] = A + B(tc-t)^m + C(tc-t)^m cos[ω ln(tc-t) - φ]

**实现路线（线性化技巧，无外部 LPPL 库依赖）**：固定 (tc, m, ω) 后模型对
(A, B, C1, C2) 线性——C cos(ω ln dt - φ) 展开为 C1 cos(ω ln dt) + C2 sin(ω ln dt)，
np.linalg.lstsq 直接解；网格搜索 (tc, m, ω) 取 SSE 最小。网格边界命中即
"边界解"（不计有效窗口，对应 §4.8.1 边界解比例信号）。

**有效窗口判定**：B<0（泡沫方向：价格向 tc 超指数加速）且拟合参数不落在网格
边界（m∈(0.1,0.9)、ω∈(5,15) 内部）且 tc 在未来 [1, tc_max] 交易日内。

**评分映射（§4.8.1 表，满分 90，T4 触发门槛 LPPL≥40）**：
  - 幂律加速：有效窗口 m 中位 ∈ (0.1, 0.9) → +20
  - 对数周期震荡：有效窗口 ω 中位 ∈ (5, 15) → +20
  - 临界时间：有效窗口 tc 中位距当前 ≤20 交易日 → +25
  - 稳健性：有效窗口占比 > 50% → +15
  - 预测集中度：有效窗口 tc 标准差 < 20 日 → +10

**范围声明**：独立函数，未接入 TRANSITION_CONFIG（T4 已有多维信号兜底——
RSI 极端/MACD 背离/斜率加速等，§4.8.2）；接入 T4 评分链需经配置评审。

依据: 10_regime_detector_spec §4.8.1
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = ["LPPLResult", "lppl_blowoff_score"]


@dataclass(frozen=True)
class LPPLResult:
    """LPPL 拟合评分结果（frozen 不可变）。

    Attributes:
        score: 五维评分合计 [0, 90]（T4 触发门槛 LPPL≥40）
        m_median: 有效窗口幂律指数中位（无有效窗口=None）
        omega_median: 有效窗口对数周期频率中位（无有效窗口=None）
        tc_median_days: 有效窗口临界时间中位（距序列末日交易日数，无有效窗口=None）
        tc_std_days: 有效窗口 tc 标准差（有效窗口<2=None）
        valid_window_ratio: 有效窗口占比 ∈[0,1]
        windows_evaluated: 实际拟合窗口数
        degraded: 数据不足降级（score=0）
    """

    score: float
    m_median: float | None
    omega_median: float | None
    tc_median_days: float | None
    tc_std_days: float | None
    valid_window_ratio: float
    windows_evaluated: int
    degraded: bool = False


def _lppl_fit_window(
    y: np.ndarray,
    m_grid: np.ndarray,
    omega_grid: np.ndarray,
    tc_ahead_grid: np.ndarray,
) -> tuple[float, float, float, float, bool]:
    """单窗口 LPPL 网格拟合（线性化 lstsq）。

    Returns:
        (best_m, best_omega, best_tc_ahead, best_B, is_boundary_solution)
        is_boundary_solution=True 表示最优解落在 m/ω/tc 网格边界（边界解，
        对应 §4.8.1"边界解比例"信号，不计入有效窗口）。
    """
    n = len(y)
    t = np.arange(1, n + 1, dtype=float)
    best = (np.inf, 0.0, 0.0, 0.0, 0.0, False)
    for tc_ahead in tc_ahead_grid:
        dt = (n + tc_ahead) - t  # > 0 恒成立
        ln_dt = np.log(dt)
        for m in m_grid:
            dt_m = dt**m
            f1 = dt_m
            for omega in omega_grid:
                f2 = dt_m * np.cos(omega * ln_dt)
                f3 = dt_m * np.sin(omega * ln_dt)
                x = np.column_stack([np.ones(n), f1, f2, f3])
                coef, residuals, *_ = np.linalg.lstsq(x, y, rcond=None)
                sse = float(residuals[0]) if len(residuals) else float(
                    np.sum((y - x @ coef) ** 2)
                )
                if sse < best[0]:
                    boundary = (
                        m in (m_grid[0], m_grid[-1])
                        or omega in (omega_grid[0], omega_grid[-1])
                        or tc_ahead in (tc_ahead_grid[0], tc_ahead_grid[-1])
                    )
                    best = (sse, m, omega, tc_ahead, float(coef[1]), boundary)
    _, m, omega, tc_ahead, b, boundary = best
    return m, omega, tc_ahead, b, boundary


def lppl_blowoff_score(
    close: pd.Series,
    windows: tuple[int, ...] = (60, 90, 120),
    m_range: tuple[float, float] = (0.1, 0.9),
    omega_range: tuple[float, float] = (5.0, 15.0),
    tc_max_ahead: int = 60,
    tc_proximity_days: float = 20.0,
    tc_std_days: float = 20.0,
) -> LPPLResult:
    """LPPL 赶顶检测评分（10 号 §4.8.1 五维映射）。

    Args:
        close: 价格序列（index=日期；取末段各窗口拟合，须全为正价格）。
        windows: 拟合窗口组（交易日）。
        m_range / omega_range: 经验区间（网格边界即区间端点，边界解不计有效窗口）。
        tc_max_ahead: tc 网格最远前瞻（交易日）。
        tc_proximity_days: 临界时间得分带（tc 中位 ≤ 此值 → +25）。
        tc_std_days: 预测集中度阈值（tc 标准差 < 此值 → +10）。

    Returns:
        LPPLResult；序列 < 最短窗口 → degraded（score=0）；无有效窗口 → score=0。
    """
    values = close.to_numpy(dtype=float)
    if (values <= 0).any() or np.isnan(values).any():
        raise ValueError("LPPL 要求全正价格序列（log 域拟合），含非正/NaN 值")
    usable = [w for w in windows if len(values) >= w]
    if not usable:
        return LPPLResult(0.0, None, None, None, None, 0.0, 0, degraded=True)

    y_all = np.log(values)
    m_grid = np.linspace(m_range[0], m_range[1], 9)
    omega_grid = np.linspace(omega_range[0], omega_range[1], 11)
    tc_ahead_grid = np.array([2, 5, 10, 15, 20, 25, 30, 40, 50, 60], dtype=float)
    tc_ahead_grid = tc_ahead_grid[tc_ahead_grid <= tc_max_ahead]

    fits = []
    for w in usable:
        m, omega, tc_ahead, b, boundary = _lppl_fit_window(
            y_all[-w:], m_grid, omega_grid, tc_ahead_grid
        )
        fits.append((m, omega, tc_ahead, b, boundary))

    n_windows = len(fits)
    # 有效窗口：泡沫方向 B<0 + 非边界解
    valid = [(m, o, tc) for m, o, tc, b, boundary in fits if b < 0 and not boundary]
    valid_ratio = len(valid) / n_windows
    if not valid:
        return LPPLResult(0.0, None, None, None, None, valid_ratio, n_windows)

    m_med = float(np.median([f[0] for f in valid]))
    omega_med = float(np.median([f[1] for f in valid]))
    tc_med = float(np.median([f[2] for f in valid]))
    tc_std = float(np.std([f[2] for f in valid])) if len(valid) >= 2 else None

    score = 0.0
    if m_range[0] < m_med < m_range[1]:
        score += 20
    if omega_range[0] < omega_med < omega_range[1]:
        score += 20
    if tc_med <= tc_proximity_days:
        score += 25
    if valid_ratio > 0.5:
        score += 15
    if tc_std is not None and tc_std < tc_std_days:
        score += 10
    return LPPLResult(score, m_med, omega_med, tc_med, tc_std, valid_ratio, n_windows)
