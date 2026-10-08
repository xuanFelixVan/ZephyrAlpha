# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/mining/cyc_conditional_prereg_v1.md | CYC族条件变量考场（判据冻结实现，禁改口径）
# [MODULE] scripts.backtest.fexam.conditional_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; statsmodels; scipy(经pandas spearman); 标准库 json argparse pathlib datetime
# [CONSUMERS] tests/backtest/fexam/test_conditional_exam.py; docs/_working/fexam/indicator_conditional_exam_scores_v1.yaml(产出)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 判据唯一真源=预注册卡 cyc_conditional_prereg_v1.md（commit dfcc8ec9，裁定#489①）：层切点/HAC lag=10/Bonferroni 族/判活逻辑全部照卡硬编码，禁参数化改口；一次窗口语义（考试窗恰跑一次）；CH 只读经 ch_data（TableRegistry 表名常量）；层有效性计数只看缺失掩码不看收益值（解盲纪律）；产物落 docs/_working/fexam/（卡 §9.3 schema 冻结）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达→CHAccessError 上抛；基线双废/指标 VOID→照卡写 VOID 产出不抛；statsmodels 缺席→ImportError 上抛（禁手搓 HAC 替代卡定调用）
# [TESTS] tests/backtest/fexam/test_conditional_exam.py（合成已知真值：相位分桶/宽度阈值/N_fam 冻结/HAC 统计量恢复）
# [MODIFY-GUARD] docs/_working/matrix_campaign/mining/cyc_conditional_prereg_v1.md §9.4 禁改清单（改任何一项=本卡作废须新预注册）
# create-guard-not-dup: CYC 族条件变量考场专用（分层增益 HAC 检验；与 ic_exam 的方向 IC 及格线考场科目不同、零功能交集）
"""conditional_exam — CYC 族条件变量考场（裁定#489①；预注册卡判据冻结实现）。

科目：条件增益（层间 IC 异质性），非方向预测。基线=20 日动量 B1（备用 5 日反转 B2），
指标只当"相位分层条件"。判活=名下 ≥1 层间对比 p_adj<0.05（Bonferroni，族=4 指标全部
有效层两两对比，预期 N_fam=11）且 max_s|mu_s|>|mu_all| 且各有效层 ≥30 有效日。
考试窗=2025-10-09..2026-09-30（一次定生死）；参照窗 2024-10-08..2025-09-30 report-only。
实现顺序=卡 §9.2 唯一合法步序：装载数据→基线有效性→层有效性计数冻结 N_fam→解盲检验。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
_FEXAM = Path(__file__).resolve().parent
if str(_FEXAM) not in sys.path:
    sys.path.insert(0, str(_FEXAM))

import ch_data  # noqa: E402

from zephyr.shared.utils.time_utils import now_utc_str  # noqa: E402

#: 预注册卡锚（卡 §7：产出文件必须记录本卡 commit hash；跑数晚于卡 commit）
PREREG_CARD = "docs/_working/matrix_campaign/mining/cyc_conditional_prereg_v1.md"
PREREG_CARD_COMMIT = "dfcc8ec9548c6e827cacc7ee32e7c5f0a8d7d542"
RULING_REF = "裁定#489①"

#: 窗口冻结（卡 §7；与 ch_data prereg v1 同窗）
WINDOW_EXAM = ("2025-10-09", "2026-09-30")
WINDOW_REF = ("2024-10-08", "2025-09-30")
WINDOW_LOAD = ("2024-08-01", "2026-09-30")

#: 判据常数（卡 §3~§5 冻结，禁改）
BASELINE_VOID_LINE = 0.01  # 基线有效性护栏 |mu_all|>=0.01
MIN_SECTION_WIDTH = 100  # 当日截面宽度下限（层内三元组 / 全截面宇宙）
MIN_STRATUM_DAYS = 30  # 层有效日数下限
HAC_MAXLAGS = 10  # statsmodels HAC maxlags（卡 §5.1 恰按此调用）
ALPHA = 0.05  # p_adj 显著性线

#: 基线定义（卡 §3：B1=20 日动量主基线，B2=5 日反转备用；判定顺序机械唯一）
BASELINE_DEFS: dict[str, str] = {"B1": "mom20", "B2": "rev5"}

#: 指标→列→分层器注册（卡 §2 切点=实现常数，零样本估计）
INDICATOR_COLUMNS: dict[str, list[str]] = {
    "IND-CYC-001": ["ht_dcperiod"],
    "IND-CYC-002": ["ht_dcphase"],
    "IND-CYC-004": ["ht_sine", "ht_leadsine"],
    "IND-CYC-005": ["ht_trendmode"],
}

STRATA_ORDER: dict[str, list[str]] = {
    "IND-CYC-001": ["D1", "D2", "D3"],
    "IND-CYC-002": ["P1", "P2", "P3", "P4"],
    "IND-CYC-004": ["W0", "W1"],
    "IND-CYC-005": ["M0", "M1"],
}

STAGING = RUN_ROOT / ".runtime" / "sessions" / "st-mx07-W3" / "staging"
CACHE_PATH = STAGING / "cond_exam_cache_v1.pkl"
FREEZE_PATH = STAGING / "cond_exam_freeze_v1.json"
OUTPUT_PATH = RUN_ROOT / "docs" / "_working" / "fexam" / "indicator_conditional_exam_scores_v1.yaml"


# ────────────────────────── 相位分层器（卡 §2 切点=实现常数）──────────────────────────


def strata_dcperiod(dcperiod: pd.DataFrame) -> pd.DataFrame:
    """IND-CYC-001：D1≤20<D2≤35<D3（周期长度三层）。"""
    out = pd.DataFrame(index=dcperiod.index, columns=dcperiod.columns, dtype="object")
    out[dcperiod <= 20] = "D1"
    out[(dcperiod > 20) & (dcperiod <= 35)] = "D2"
    out[dcperiod > 35] = "D3"
    return out


def strata_dcphase(dcphase: pd.DataFrame) -> pd.DataFrame:
    """IND-CYC-002：bucket=floor(phase/90)∈{0,1,2,3}→P1..P4（floor 语义，边界归下一层）。"""
    bucket = np.floor(dcphase / 90.0)
    label = bucket.map(lambda b: {0.0: "P1", 1.0: "P2", 2.0: "P3", 3.0: "P4"}.get(b))
    return label.astype("object")


def strata_sine(sine: pd.DataFrame, leadsine: pd.DataFrame) -> pd.DataFrame:
    """IND-CYC-004：W1=ht_sine>ht_leadsine（下行半程），W0=≤（上行半程）；任一缺失=标签缺失。"""
    out = pd.DataFrame(np.nan, index=sine.index, columns=sine.columns, dtype="object")
    both = sine.notna() & leadsine.notna()
    out[both & (sine > leadsine)] = "W1"
    out[both & (sine <= leadsine)] = "W0"
    return out


def strata_trendmode(trendmode: pd.DataFrame) -> pd.DataFrame:
    """IND-CYC-005：M1=trendmode==1（趋势态），M0==0（循环态）；其他值=标签缺失。"""
    out = pd.DataFrame(np.nan, index=trendmode.index, columns=trendmode.columns, dtype="object")
    out[trendmode == 1] = "M1"
    out[trendmode == 0] = "M0"
    return out


STRATA_FUNCS = {
    "IND-CYC-001": lambda ind: strata_dcperiod(ind["ht_dcperiod"]),
    "IND-CYC-002": lambda ind: strata_dcphase(ind["ht_dcphase"]),
    "IND-CYC-004": lambda ind: strata_sine(ind["ht_sine"], ind["ht_leadsine"]),
    "IND-CYC-005": lambda ind: strata_trendmode(ind["ht_trendmode"]),
}


# ────────────────────────── IC 统计量（卡 §4/§5 冻结口径）──────────────────────────


def daily_cross_ic(b: pd.DataFrame, r5: pd.DataFrame) -> pd.Series:
    """全截面日度 spearman IC；当日宇宙宽度（B,r5 双有效计数）<100→NaN。"""
    dates: list[pd.Timestamp] = []
    vals: list[float] = []
    for t in b.index:
        bb = b.loc[t]
        rr = r5.loc[t]
        ok = bb.notna() & rr.notna()
        if int(ok.sum()) < MIN_SECTION_WIDTH:
            dates.append(t)
            vals.append(np.nan)
            continue
        rho = bb[ok].corr(rr[ok], method="spearman")
        dates.append(t)
        vals.append(float(rho) if pd.notna(rho) else np.nan)
    return pd.Series(vals, index=pd.DatetimeIndex(dates), dtype="float64")


def stratum_daily_ic(
    b: pd.DataFrame,
    r5: pd.DataFrame,
    label: pd.DataFrame,
    stratum: str,
) -> pd.Series:
    """层内日度 spearman IC；当日该层截面宽度（{L,B,r5} 三元组非缺失计数）<100→NaN。"""
    dates: list[pd.Timestamp] = []
    vals: list[float] = []
    for t in b.index:
        bb = b.loc[t]
        rr = r5.loc[t]
        ll = label.loc[t]
        ok = bb.notna() & rr.notna() & (ll == stratum)
        if int(ok.sum()) < MIN_SECTION_WIDTH:
            dates.append(t)
            vals.append(np.nan)
            continue
        rho = bb[ok].corr(rr[ok], method="spearman")
        dates.append(t)
        vals.append(float(rho) if pd.notna(rho) else np.nan)
    return pd.Series(vals, index=pd.DatetimeIndex(dates), dtype="float64")


def hac_t_test(d: pd.Series) -> dict[str, Any]:
    """卡 §5.1 恰按所写调用：OLS 常数回归 HAC(maxlags=10)，t/p 双侧。

    退化护栏（卡未定，机械不留自由度）：len<2 或 se=0 → t=nan,p=1.0,degenerate=true
    （p_adj=1.0=零证据，不影响判活方向的保守性）。
    """
    x = d.dropna()
    n = int(x.size)
    if n < 2:
        return {"n_days": n, "mean_d": float("nan"), "t_hac": float("nan"), "p_raw": 1.0, "degenerate": True}
    import statsmodels.api as sm

    res = sm.OLS(endog=x.to_numpy(dtype="float64"), exog=np.ones((n, 1))).fit(
        cov_type="HAC", cov_kwds={"maxlags": HAC_MAXLAGS}
    )
    se = float(np.sqrt(res.cov_params()[0, 0]))
    if not np.isfinite(se) or se == 0.0:
        return {
            "n_days": n,
            "mean_d": float(x.mean()),
            "t_hac": float("nan"),
            "p_raw": 1.0,
            "degenerate": True,
        }
    return {
        "n_days": n,
        "mean_d": float(x.mean()),
        "t_hac": float(res.tvalues[0]),
        "p_raw": float(res.pvalues[0]),
        "degenerate": False,
    }


# ────────────────────────── 单窗口管线（卡 §9.2 唯一合法步序）──────────────────────────


def select_baseline(
    mom20: pd.DataFrame, rev5: pd.DataFrame, r5: pd.DataFrame, window: tuple[str, str]
) -> dict[str, Any]:
    """卡 §3 步序 2：先 B1 后 B2，|mu_all|>=0.01 即选中；双废=VOID。"""
    detail: dict[str, Any] = {}
    for name, panel in (("B1", mom20), ("B2", rev5)):
        ic = daily_cross_ic(panel, r5).loc[window[0] : window[1]].dropna()
        mu_all = float(ic.mean()) if len(ic) else float("nan")
        detail[name] = {"mu_all": mu_all, "n_days": int(ic.size), "alive": bool(abs(mu_all) >= BASELINE_VOID_LINE)}
        if detail[name]["alive"]:
            return {"baseline_used": name, "baseline_ic_all": mu_all, "baseline_detail": detail, "void": False}
    return {"baseline_used": None, "baseline_ic_all": float("nan"), "baseline_detail": detail, "void": True}


def _resolve_strata_order(ind: str, label: pd.DataFrame, strata_list: list[str] | None) -> list[str]:
    """层序解析：真跑四件走冻结 STRATA_ORDER（零自由度）；合成指标须显式给 strata_list。"""
    if strata_list is not None:
        return list(strata_list)
    return list(STRATA_ORDER[ind])


def blind_layer_counts(
    strata: dict[str, pd.DataFrame],
    b: pd.DataFrame,
    r5: pd.DataFrame,
    window: tuple[str, str],
    *,
    strata_order: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """卡 §9.2 步序 3（解盲前）：层有效性计数只看缺失掩码不看收益值。"""
    counts: dict[str, dict[str, int]] = {}
    k_eff: dict[str, int] = {}
    voided: dict[str, str] = {}
    for ind, label in strata.items():
        order = _resolve_strata_order(ind, label, (strata_order or {}).get(ind))
        per: dict[str, int] = {}
        for s in order:
            ok = b.notna() & r5.notna() & (label == s)
            ok = ok.loc[window[0] : window[1]]
            per_day = int((ok.sum(axis=1) >= MIN_SECTION_WIDTH).sum())
            per[s] = per_day
        valid = [s for s in order if per[s] >= MIN_STRATUM_DAYS]
        counts[ind] = per
        k_eff[ind] = len(valid)
        if len(valid) < 2:
            voided[ind] = f"有效层 {valid} 不足 2（层有效日数={per}）"
    n_fam = 0
    for ind in strata:
        n_fam += k_eff[ind] * (k_eff[ind] - 1) // 2
    return {"stratum_day_counts": counts, "k_eff": k_eff, "voided": voided, "family_size": n_fam}


def run_indicator(
    ind: str,
    label: pd.DataFrame,
    b: pd.DataFrame,
    r5: pd.DataFrame,
    window: tuple[str, str],
    n_fam: int,
    void_reason: str | None,
    *,
    strata_list: list[str] | None = None,
) -> dict[str, Any]:
    """卡 §9.2 步序 4（解盲）：逐日层内 IC→两两 HAC→p_adj→判活（§5.2）。"""
    out: dict[str, Any] = {"strata": {}, "pairs": [], "void_reason": None}
    if void_reason is not None:
        out["verdict"] = "void"
        out["void_reason"] = void_reason
        return out
    order = _resolve_strata_order(ind, label, strata_list)
    ic_all_series = daily_cross_ic(b, r5).loc[window[0] : window[1]]
    mu_all = float(ic_all_series.dropna().mean())
    strat_ic: dict[str, pd.Series] = {}
    strat_meta: dict[str, dict[str, Any]] = {}
    for s in order:
        ic_s = stratum_daily_ic(b, r5, label, s).loc[window[0] : window[1]]
        valid = ic_s.dropna()
        strat_ic[s] = ic_s
        strat_meta[s] = {
            "n_days": int(valid.size),
            "n_stockdays": int((b.notna() & r5.notna() & (label == s)).loc[window[0] : window[1]].sum().sum()),
            "mu_s": float(valid.mean()) if valid.size else float("nan"),
        }
        out["strata"][s] = strat_meta[s]
    out["mu_all"] = mu_all
    valid_layers = [s for s in order if strat_meta[s]["n_days"] >= MIN_STRATUM_DAYS]
    pairs: list[dict[str, Any]] = []
    for i, a in enumerate(valid_layers):
        for bq in valid_layers[i + 1 :]:
            d = (strat_ic[a] - strat_ic[bq]).dropna()  # 两层 IC 均有效日（交集，按日序）
            stat = hac_t_test(d)
            p_adj = min(1.0, stat["p_raw"] * n_fam)
            pairs.append(
                {
                    "a": a,
                    "b": bq,
                    "n_days": stat["n_days"],
                    "mean_d": stat["mean_d"],
                    "t_hac": stat["t_hac"],
                    "p_raw": stat["p_raw"],
                    "p_adj": p_adj,
                    "degenerate": stat["degenerate"],
                }
            )
    out["pairs"] = pairs
    sig = [p for p in pairs if p["p_adj"] < ALPHA]
    max_abs_mu_s = max((abs(strat_meta[s]["mu_s"]) for s in valid_layers), default=float("nan"))
    out["gain"] = max_abs_mu_s - abs(mu_all)
    out["best_stratum"] = max(valid_layers, key=lambda s: abs(strat_meta[s]["mu_s"])) if valid_layers else None
    alive = bool(sig) and bool(out["gain"] > 0)
    out["verdict"] = "pass" if alive else "fail"
    return out


def run_window(
    data: dict[str, pd.DataFrame], window: tuple[str, str], *, freeze_path: Path | None = None
) -> dict[str, Any]:
    """单窗全管线（考试窗=判生死；参照窗同管线 report-only）。

    冻结纪律（卡 §9.2）：freeze_path 落盘发生在 blind_layer_counts（步序 3，只看掩码）
    之后、run_indicator（步序 4 解盲）之前——物理写入先于任何层内 IC 数值存在。
    """
    r5 = data["r5"]
    mom20 = data["mom20"]
    rev5 = data["rev5"]
    base = select_baseline(mom20, rev5, r5, window)
    result: dict[str, Any] = {
        "window": list(window),
        "baseline_used": base["baseline_used"],
        "baseline_ic_all": base["baseline_ic_all"],
        "baseline_detail": base["baseline_detail"],
    }
    if base["void"]:
        result["family_verdict"] = "void"
        result["void_reason"] = "基线双废（B1/B2 |mu_all| 均低于护栏 0.01）"
        result["per_indicator"] = {}
        return result
    b = {"B1": mom20, "B2": rev5}[base["baseline_used"]]
    strata = {ind: STRATA_FUNCS[ind](data["indicators"]) for ind in STRATA_ORDER}
    blind = blind_layer_counts(strata, b, r5, window)
    result["family_size"] = blind["family_size"]
    result["k_eff"] = blind["k_eff"]
    result["stratum_day_counts"] = blind["stratum_day_counts"]
    if freeze_path is not None:
        freeze_path.parent.mkdir(parents=True, exist_ok=True)
        with open(freeze_path, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "frozen_before_unblind": True,
                    "window": list(window),
                    "baseline_used": base["baseline_used"],
                    "family_size": blind["family_size"],
                    "k_eff": blind["k_eff"],
                    "stratum_day_counts": blind["stratum_day_counts"],
                },
                fh,
                ensure_ascii=False,
                indent=2,
            )
        print(f"[freeze] family_size={blind['family_size']} -> {freeze_path}", flush=True)
    per: dict[str, dict[str, Any]] = {}
    for ind in STRATA_ORDER:
        per[ind] = run_indicator(
            ind,
            strata[ind],
            b,
            r5,
            window,
            blind["family_size"],
            blind["voided"].get(ind),
        )
    result["per_indicator"] = per
    n_void = sum(1 for v in per.values() if v["verdict"] == "void")
    n_pass = sum(1 for v in per.values() if v["verdict"] == "pass")
    if n_void >= 2:
        result["family_verdict"] = "void"
        result["void_reason"] = f"指标 VOID 数 {n_void}>=2（卡 §6 VOID 分支）"
    elif n_pass >= 1:
        result["family_verdict"] = "pass"
    else:
        result["family_verdict"] = "fail"
    return result


# ────────────────────────── 数据装载与缓存（卡 §9.1）──────────────────────────


def load_data() -> dict[str, pd.DataFrame]:
    """CH 只读装载数据加载窗（2024-08-01..2026-09-30，覆盖两窗+20 日回看）；pickle 落 staging。"""
    STAGING.mkdir(parents=True, exist_ok=True)
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "rb") as fh:
            return pd.read_pickle(fh)  # noqa: S301 — 自产自销 staging 缓存
    ind_cols = sorted({c for cols in INDICATOR_COLUMNS.values() for c in cols})
    indicators: dict[str, pd.DataFrame] = {}
    for col in ind_cols:
        panel = ch_data.load_panel(ch_data.T_TECHNICAL_INDICATOR, col, *WINDOW_LOAD)
        if panel.empty:
            raise ch_data.CHAccessError(f"technical_indicator 列 {col} 空面板（fail-closed 禁伪造）")
        indicators[col] = panel
        print(f"[load] {col}: {panel.shape}", flush=True)
    close = ch_data.load_close(*WINDOW_LOAD)
    if close.empty:
        raise ch_data.CHAccessError("kline_daily_hfq close 空面板（fail-closed 禁伪造）")
    print(f"[load] close: {close.shape}", flush=True)
    # 日期×代码对齐（机械交集，零填充）：close 为交易日历基准，指标列与 close 取公共域
    common_dates = close.index
    common_syms = close.columns
    for col, panel in indicators.items():
        common_dates = common_dates.intersection(panel.index)
        common_syms = common_syms.intersection(panel.columns)
    print(f"[align] dates={len(common_dates)} symbols={len(common_syms)}", flush=True)
    close = close.loc[common_dates, common_syms]
    indicators = {c: p.loc[common_dates, common_syms] for c, p in indicators.items()}
    r5 = close.shift(-5) / close - 1.0
    mom20 = close / close.shift(20) - 1.0
    rev5 = -(close / close.shift(5) - 1.0)
    data = {"indicators": indicators, "close": close, "r5": r5, "mom20": mom20, "rev5": rev5}
    with open(CACHE_PATH, "wb") as fh:
        pd.to_pickle(data, fh)
    print(f"[cache] {CACHE_PATH}", flush=True)
    return data


def compact_result(res: dict[str, Any]) -> dict[str, Any]:
    """产出摘要（去 detail 体积；数字全部 round 6 保读数原文可复核）。"""

    def _num(x: Any) -> Any:
        return round(float(x), 6) if isinstance(x, (int, float)) and np.isfinite(x) else x

    out: dict[str, Any] = {
        "window": res["window"],
        "baseline_used": res.get("baseline_used"),
        "baseline_ic_all": _num(res.get("baseline_ic_all")),
        "family_size": res.get("family_size"),
        "family_verdict": res["family_verdict"],
    }
    if res.get("void_reason"):
        out["void_reason"] = res["void_reason"]
    per: dict[str, Any] = {}
    for ind, v in res.get("per_indicator", {}).items():
        entry: dict[str, Any] = {
            "strata": {s: {k: _num(x) for k, x in meta.items()} for s, meta in v.get("strata", {}).items()},
            "mu_all": _num(v.get("mu_all")),
            "gain": _num(v.get("gain")),
            "best_stratum": v.get("best_stratum"),
            "pairs": [{k: _num(x) for k, x in p.items()} for p in v.get("pairs", [])],
            "verdict": v["verdict"],
        }
        if v.get("void_reason"):
            entry["void_reason"] = v["void_reason"]
        per[ind] = entry
    out["per_indicator"] = per
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="CYC 族条件变量考场（预注册卡判据冻结；一次窗口）")
    ap.add_argument("--stage", choices=["load", "exam", "ref", "all"], default="all")
    args = ap.parse_args()
    if args.stage in ("load", "all"):
        load_data()
    if args.stage == "load":
        return 0
    data = load_data()
    results: dict[str, Any] = {}
    if args.stage in ("exam", "all"):
        results["exam"] = run_window(data, WINDOW_EXAM, freeze_path=FREEZE_PATH)
    if args.stage in ("ref", "all"):
        results["ref"] = run_window(data, WINDOW_REF, freeze_path=STAGING / "cond_exam_freeze_ref_v1.json")
    if args.stage != "all":
        for tag, res in results.items():
            print(f"===== {tag} =====")
            print(json.dumps(compact_result(res), ensure_ascii=False, indent=2, default=str))
        return 0
    doc: dict[str, Any] = {
        "doc_type": "fexam_indicator_conditional_scores",
        "version": "v1",
        "generated_at_utc": now_utc_str(),
        "prereg_ref": {
            "card": PREREG_CARD,
            "card_commit": PREREG_CARD_COMMIT,
            "ruling": RULING_REF,
        },
        "baseline_used": results["exam"].get("baseline_used"),
        "baseline_ic_all": results["exam"].get("baseline_ic_all"),
        "family_size": results["exam"].get("family_size"),
        "exam_window": list(WINDOW_EXAM),
        "per_indicator": compact_result(results["exam"])["per_indicator"],
        "family_verdict": results["exam"]["family_verdict"],
        "ref_window_report": compact_result(results["ref"]),
        "device_ledger": [
            {
                "object": "indicator_conditional_exam",
                "device": "cpu",
                "statsmodels_hac_maxlags": HAC_MAXLAGS,
                "rng": "none",
            }
        ],
    }
    if results["exam"].get("void_reason"):
        doc["void_reason"] = results["exam"]["void_reason"]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, allow_unicode=True, sort_keys=False, width=100)
    print(f"[output] {OUTPUT_PATH}", flush=True)
    print(
        f"[verdict] family={doc['family_verdict']} baseline={doc['baseline_used']} family_size={doc['family_size']}",
        flush=True,
    )
    for ind, v in doc["per_indicator"].items():
        print(f"  {ind}: {v['verdict']} gain={v.get('gain')} pairs={len(v.get('pairs', []))}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
