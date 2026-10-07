# [BLUEPRINT] MOD-BT-LAGVAL | docs/03_modules/_domain_backtest/blueprint.md（G-C.4 lead-lag 统计验证器，P2 观察轨）
# [MODULE] scripts.backtest.lead_lag_validator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.factor.analysis.bhy_fdr（全仓唯一 BH/BHY FDR 真源，禁自写第二份）；numpy
# [CONSUMERS] 观察轨报告消费（G-C 主体排产后）；tests/backtest/test_lead_lag_validator.py
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] 观察轨 P2：不接生产、不作策略结论、结论无论正负都保留（negative_result_promise 口径）；FDR 校正零自写——委托 zephyr.factor.analysis.bhy_fdr（Curme 2015 lead-lag 网络 Bonferroni/FDR 口径）；p 值用 Fisher z 变换正态近似（n≥10 有效域，如实披露非精确 t 分布）；窗稳定性=分半/多窗逐窗复检（滚动重考口径，与 grid_stats_engine.half_split_reexam 同纪律：事件触发、禁 cron）
# [MODIFY-GUARD] tests/backtest/test_lead_lag_validator.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LeadLagValidationError(输入过短/长度不齐/FDR 非法)
# [TESTS] tests/backtest/test_lead_lag_validator.py
# [TTL] permanent
"""D_BACKTEST — G-C.4 lead-lag 统计验证器（观察轨最小实现，P2）。

规格=ext_01_revised_construction_plan.md G-C.4 行：对"小级别领先大级别"做统计
验证——滞后相关矩阵 + 多重检验校正（FDR）+ 分层窗对比（Curme 口径）。
学术证据：Curme et al. (2015)（lead-lag 网络 Bonferroni/FDR 校正）；
Fang et al. (2025)（A股 1283 只，细尺度领先更显著），见学术案卷 §3.1/§3.3。

产出契约（验证报告，dict）：
    每对 (pair)：逐 lag 相关系数 + p 值 → 全族 (pair×lag) 过 BHY FDR
    （arbitrary_dependence=True，lead-lag 检验族内强相关，Curme 口径）
    → 显著 lag 集 + 最优 lag + 分窗稳定性（逐窗最优 lag 符号一致占比）。
    **负结果对原样保留在报告里**（不显著≠删除——负结果台账纪律）。

观察轨边界：本件零生产接线（无 main 点火、无 tasks 注册、无 DB 写），
正式进 G-C 主体需 Owner 排产；滚动重考排程=消费方事件触发（禁 cron/Timer）。

Usage:
    from scripts.backtest.lead_lag_validator import validate_pairs

    report = validate_pairs({"m1_lead_d1": (leader_series, follower_series)}, max_lag=5)
    # report["pairs"]["m1_lead_d1"]["significant_lags"] / ["best_lag"] / ["window_stability"]

"""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Mapping, Sequence

import numpy as np

from zephyr.factor.analysis.bhy_fdr import bhy_fdr

#: 滞后相关有效样本下限（Fisher z 近似 n≥10 有效域）
MIN_OBS_PER_PAIR: int = 10

#: 分窗稳定性默认窗数（Curme 口径分层窗对比；2002→2012 漂移检测先例）
DEFAULT_N_WINDOWS: int = 2

_NORM = NormalDist()


class LeadLagValidationError(Exception):
    """lead-lag 验证器输入非法。"""


def _to_array(x: Sequence[float] | np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    if arr.size == 0:
        raise LeadLagValidationError("空序列")
    if not np.isfinite(arr).all():
        raise LeadLagValidationError("序列含 NaN/Inf（禁静默剔除——数据治理归调用方）")
    return arr


def lagged_correlation(
    leader: Sequence[float] | np.ndarray,
    follower: Sequence[float] | np.ndarray,
    max_lag: int,
) -> dict[int, float]:
    """滞后相关：corr(leader_t, follower_{t+k})，k=0..max_lag（正 k=leader 领先 k 期）。"""
    a = _to_array(leader)
    b = _to_array(follower)
    if a.size != b.size:
        raise LeadLagValidationError(f"长度不齐: leader={a.size} follower={b.size}")
    if max_lag < 0:
        raise LeadLagValidationError(f"max_lag 非法: {max_lag}")
    if a.size - max_lag < MIN_OBS_PER_PAIR:
        raise LeadLagValidationError(f"有效重叠样本 {a.size - max_lag} < {MIN_OBS_PER_PAIR}（Fisher z 有效域）")
    out: dict[int, float] = {}
    for k in range(max_lag + 1):
        x, y = a[: a.size - k], b[k:]
        sx, sy = x.std(), y.std()
        if sx <= 0.0 or sy <= 0.0:
            out[k] = float("nan")
            continue
        out[k] = float(np.corrcoef(x, y)[0, 1])
    return out


def _corr_pvalue(r: float, n: int) -> float:
    """Pearson 相关 p 值（Fisher z 变换正态近似：z=arctanh(r)·√(n−3)，双侧）。

    如实披露：非精确 t 分布；n≥10 时近似偏差对 FDR 排序影响可忽略（观察轨够用）。
    """
    if not math.isfinite(r) or n < 4 or abs(r) >= 1.0:
        return 1.0 if not math.isfinite(r) else 0.0 if abs(r) >= 1.0 else 1.0
    z = math.atanh(r) * math.sqrt(n - 3)
    return float(2.0 * (1.0 - _NORM.cdf(abs(z))))


def validate_pairs(
    pairs: Mapping[str, tuple[Sequence[float], Sequence[float]]],
    *,
    max_lag: int,
    fdr_q: float = 0.10,
    n_windows: int = DEFAULT_N_WINDOWS,
) -> dict:
    """lead-lag 验证主入口（G-C.4 观察轨报告）。

    Args:
        pairs: pair_id → (leader 序列, follower 序列)（等长逐期对齐，治理归调用方）
        max_lag: 最大领先期数（k=0..max_lag 全部入族）
        fdr_q: FDR 控制水平（默认 0.10，BHY 任意依赖稳健——Curme 2015 口径）
        n_windows: 稳定性分窗数（默认 2=分半窗，滚动重考口径）

    Returns:
        报告 dict：{"pairs": {pid: {...}}, "family": {...}}；**不显著对原样保留**。
    """
    if not pairs:
        raise LeadLagValidationError("pairs 为空")
    entries: list[dict] = []  # 族成员：(pid, lag, r, n_eff, p)
    per_pair_raw: dict[str, dict[int, float]] = {}
    for pid, (leader, follower) in pairs.items():
        corr = lagged_correlation(leader, follower, max_lag)
        per_pair_raw[str(pid)] = corr
        a = _to_array(leader)
        for k, r in corr.items():
            n_eff = a.size - k
            entries.append({"pid": str(pid), "lag": k, "r": r, "n_eff": n_eff, "p": _corr_pvalue(r, n_eff)})

    # 全族 (pair×lag) BHY FDR（Curme 2015：lead-lag 网络族内相关→任意依赖稳健口径）
    fdr = bhy_fdr([e["p"] for e in entries], q=fdr_q, arbitrary_dependence=True)
    for e, rej in zip(entries, fdr.rejected, strict=True):
        e["rejected"] = bool(rej)

    report_pairs: dict[str, dict] = {}
    for pid_raw, (leader_raw, follower_raw) in pairs.items():
        pid = str(pid_raw)
        corr = per_pair_raw[pid]
        rows = [e for e in entries if e["pid"] == pid]
        sig_lags = sorted(e["lag"] for e in rows if e["rejected"])
        finite = {k: r for k, r in corr.items() if math.isfinite(r)}
        best_lag = max(finite, key=lambda k: abs(finite[k])) if finite else None
        # 分窗稳定性：逐窗复检最优 lag 的符号一致性（漂移=窗间翻号，Curme 2002→2012 先例）
        leader_arr = _to_array(leader_raw)
        follower_arr = _to_array(follower_raw)
        window_signs: list[int] = []
        if best_lag is not None and n_windows >= 2:
            wsize = leader_arr.size // n_windows
            for w in range(n_windows):
                lo, hi = w * wsize, (w + 1) * wsize if w < n_windows - 1 else leader_arr.size
                if hi - best_lag - lo < MIN_OBS_PER_PAIR:
                    continue
                x = leader_arr[lo : hi - best_lag]
                y = follower_arr[lo + best_lag : hi]
                sx, sy = x.std(), y.std()
                if sx > 0 and sy > 0:
                    window_signs.append(int(np.corrcoef(x, y)[0, 1] > 0))
        agree = 0.0
        if window_signs:
            agree = max(sum(window_signs), len(window_signs) - sum(window_signs)) / len(window_signs)
        report_pairs[pid] = {
            "lagged_corr": corr,
            "p_values": {e["lag"]: e["p"] for e in rows},
            "significant_lags": sig_lags,
            "best_lag": best_lag,
            "best_corr": finite.get(best_lag) if best_lag is not None else None,
            "window_stability": agree,
            "status": "SIGNIFICANT" if sig_lags else "NOT_SIGNIFICANT",  # 负结果原样保留
        }
    return {
        "pairs": report_pairs,
        "family": {
            "m_tests": len(entries),
            "fdr_q": float(fdr.q),
            "n_rejected": int(fdr.n_rejected),
            "caliber": "BHY arbitrary-dependence FDR（Curme 2015 lead-lag 网络口径）；p=Fisher z 正态近似",
        },
    }


__all__ = [
    "DEFAULT_N_WINDOWS",
    "MIN_OBS_PER_PAIR",
    "LeadLagValidationError",
    "lagged_correlation",
    "validate_pairs",
]
