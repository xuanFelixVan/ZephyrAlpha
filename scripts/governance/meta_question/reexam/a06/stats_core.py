# [BLUEPRINT] MOD-METAQ-REEXAM-A06 | docs/_working/meta_question_answers/gaps/A06_MONEYFLOW_BACKFILL_workbook.md §3
# [MODULE] scripts.governance.meta_question.reexam.a06.stats_core
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] numpy; pandas; scipy.stats
# [CONSUMERS] scripts.governance.meta_question.reexam.a06.exam_a06（A06 族 6 问复考器）
# [STARTUP] imported（仅由复考器 import，无常驻进程）
# [MATURITY] testing
# [INVARIANTS] 纯函数零 IO：同输入必同输出（无随机数/无时钟/无全局态）；Newey-West 采用 Bartlett 核
#              且 lag=前瞻窗长（重叠窗 HAC 标准做法），实现与
#              .runtime/tmp/st-metaq-20260923/probes/stat_market_PQ-011x.py 逐式等价（复考须同口径）；
#              秩 IC 用截面平均秩 Pearson（= Spearman，含并列平均秩）；Chow 断点检验限截距断裂
#              （k=1，收益/IC 序列非平稳趋势项不建模，如实披露）；样本不足一律返回 nan/None，
#              禁静默填 0（0 会被读成"无相关"）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入空/短样本→返回 nan 或 None 并附 reason，不抛异常（复考器据此判 insufficient）；
#                  面板形状不一致→ValueError（编程错误须可见）
# [TESTS] python scripts/governance/meta_question/reexam/a06/exam_a06.py --selftest（合成数据闭式解比对）
# [A_module] module_id=MOD-METAQ-REEXAM-A06 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""A06 复考统计原语（纯函数）——Newey-West t / 单样本 t / 截面秩 IC / Chow 断点。

真源与口径对齐说明见文件头 [INVARIANTS]；本件不含任何数据访问，可独立重放。
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy import stats

__all__ = [
    "NAN",
    "chow_scan",
    "chow_test",
    "daily_rank_ic",
    "mean_ttest",
    "nw_tstat",
    "spearman_ic",
    "sub_period_ic",
]

NAN = float("nan")


def nw_tstat(x: Sequence[float] | np.ndarray | pd.Series, lag: int) -> float:
    """均值的 Newey-West HAC t（Bartlett 核，lag=l）——与 PQ-011x 探针逐式等价。

    Args:
        x: 观测序列（日频 IC 或日频收益均值序列）
        l: 滞后阶；重叠前瞻窗 IC 序列取 l=前瞻窗长，非重叠序列取 1

    Returns:
        t 值；有效样本 <10 或方差 ≤0 返回 nan。
    """
    v = np.asarray(pd.Series(x).dropna(), dtype=float)
    m = int(len(v))
    if m < 10:
        return NAN
    mu = float(v.mean())
    e = v - mu
    s = float((e * e).sum()) / m
    for l in range(1, max(0, int(lag)) + 1):
        gl = float((e[l:] * e[:-l]).sum()) / m
        s += 2.0 * (1.0 - l / (lag + 1.0)) * gl
    if s <= 0:
        return NAN
    var = s / m
    return float(mu / np.sqrt(var)) if var > 0 else NAN


def mean_ttest(x: Sequence[float] | np.ndarray | pd.Series) -> dict[str, float]:
    """单样本 t 检验 H0: mean=0（Welch 无关，双侧 p）。"""
    v = np.asarray(pd.Series(x).dropna(), dtype=float)
    n = int(len(v))
    if n < 3:
        return {"n": n, "mean": NAN, "std": NAN, "t": NAN, "p": NAN}
    sd = float(v.std(ddof=1))
    mean = float(v.mean())
    if sd <= 0:
        return {"n": n, "mean": mean, "std": 0.0, "t": NAN, "p": NAN}
    t = mean / (sd / np.sqrt(n))
    return {"n": n, "mean": mean, "std": sd, "t": float(t), "p": float(2.0 * stats.t.sf(abs(t), n - 1))}


def spearman_ic(x: pd.Series, y: pd.Series) -> float:
    """单截面 Spearman 秩 IC（并列取平均秩；<2 有效配对或常数列→nan）。"""
    a = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    if len(a) < 2 or a["x"].nunique() < 2 or a["y"].nunique() < 2:
        return NAN
    r = float(a["x"].corr(a["y"], method="spearman"))
    return r if np.isfinite(r) else NAN


def daily_rank_ic(
    factor_panel: pd.DataFrame,
    ret_panel: pd.DataFrame,
    min_names: int = 300,
) -> pd.Series:
    """逐日截面秩 IC 序列（向量化 Pearson-on-percentile-ranks == Spearman）。

    与 PQ-011x 探针实现逐式一致（rank(axis=1, pct=True) 去均值后相关），
    仅在 factor 与 ret 同时非空且当日有效名数 ≥ min_names 时产出。
    """
    if not factor_panel.index.equals(ret_panel.index):
        ret_panel = ret_panel.reindex(index=factor_panel.index, columns=factor_panel.columns)
    valid = factor_panel.notna() & ret_panel.notna()
    fx = factor_panel.where(valid).rank(axis=1, pct=True)
    ry = ret_panel.where(valid).rank(axis=1, pct=True)
    fx = fx.sub(fx.mean(axis=1), axis=0)
    ry = ry.sub(ry.mean(axis=1), axis=0)
    num = (fx * ry).sum(axis=1)
    den = np.sqrt((fx * fx).sum(axis=1) * (ry * ry).sum(axis=1))
    ic = (num / den).replace([np.inf, -np.inf], NAN)
    cnt = valid.sum(axis=1)
    ic = ic.where(cnt >= min_names)
    return ic.dropna()


def sub_period_ic(
    ic: pd.Series,
    spans: Sequence[tuple[str, str, str]],
) -> dict[str, dict[str, float]]:
    """按 [start,end] 闭区间窗计子样本 IC 均值与样本量（spans=(名称, start, end)）。"""
    out: dict[str, dict[str, float]] = {}
    s = ic.copy()
    s.index = pd.to_datetime(s.index)
    for name, a, b in spans:
        seg = s[(s.index >= pd.Timestamp(a)) & (s.index <= pd.Timestamp(b))]
        out[name] = {
            "start": a,
            "end": b,
            "n_days": int(len(seg)),
            "ic_mean": float(seg.mean()) if len(seg) else NAN,
            "ic_pos_share": float((seg > 0).mean()) if len(seg) else NAN,
        }
    return out


def _rss(y: np.ndarray) -> float:
    return float(((y - y.mean()) ** 2).sum()) if len(y) > 1 else 0.0


def chow_test(y: Sequence[float] | np.ndarray, split: int, k: int = 1) -> dict[str, float]:
    """Chow 断点检验（截距断裂，k=1 约束）：H0=断点前后均值相同。

    Args:
        y: 有序观测序列（时间序）
        split: 第二段起点下标（第一段 y[:split]，第二段 y[split:]）
        k: 模型参数量（截距模型=1）

    Returns:
        {n, n1, n2, f, p, mean_1, mean_2, diff}；样本不足或退化→f/p=nan。
    """
    v = np.asarray(pd.Series(y).dropna(), dtype=float)
    n = int(len(v))
    i = int(split)
    if n < 4 * k or i < 2 * k or n - i < 2 * k:
        return {"n": n, "n1": i, "n2": n - i, "f": NAN, "p": NAN, "mean_1": NAN, "mean_2": NAN, "diff": NAN}
    y1, y2 = v[:i], v[i:]
    rss1, rss2, rss0 = _rss(y1), _rss(y2), _rss(v)
    denom = (rss1 + rss2) / (n - 2 * k)
    if denom <= 0:
        f = NAN
    else:
        f = float(((rss0 - (rss1 + rss2)) / k) / denom)
    p = float(stats.f.sf(f, k, n - 2 * k)) if np.isfinite(f) else NAN
    return {
        "n": n,
        "n1": i,
        "n2": n - i,
        "f": f,
        "p": p,
        "mean_1": float(y1.mean()),
        "mean_2": float(y2.mean()),
        "diff": float(y2.mean() - y1.mean()),
    }


def chow_scan(y: Sequence[float] | np.ndarray, min_seg_frac: float = 0.15, k: int = 1) -> dict[str, float]:
    """全候选断点扫描取最大 F（断点位置内生化，避免人为挑日期）+ Bonferroni 校正 p。"""
    v = np.asarray(pd.Series(y).dropna(), dtype=float)
    n = int(len(v))
    lo = max(int(np.ceil(min_seg_frac * n)), 2 * k)
    hi = n - lo
    best_f, best_i, ncand = NAN, -1, 0
    for i in range(lo, hi + 1):
        r = chow_test(v, i, k)
        if not np.isfinite(r["f"]):
            continue
        ncand += 1
        if not np.isfinite(best_f) or r["f"] > best_f:
            best_f, best_i = r["f"], i
    if ncand == 0:
        return {"best_split_index": -1, "best_f": NAN, "best_p_raw": NAN, "best_p_bonf": NAN, "n_candidates": 0}
    p_raw = float(stats.f.sf(best_f, k, n - 2 * k))
    return {
        "best_split_index": best_i,
        "best_split_pos_share": round(best_i / n, 4),
        "best_f": best_f,
        "best_p_raw": p_raw,
        "best_p_bonf": min(1.0, p_raw * ncand),
        "n_candidates": ncand,
    }
