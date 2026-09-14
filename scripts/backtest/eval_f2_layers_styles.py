#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.eval_f2_layers_styles
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.factor.fundamentals; scipy
# [CONSUMERS] factor_registry FCT-FQ/FCT-GR 族 ⑤ 剪枝/分域证据（SOP-B ⑤）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] PIT as-of 同 eval_f2_fundamental_ic（announce_date<=t 可见最新版本）；
#              分层=5 分位等权组合 fwd20，方向对齐"值大=好"→多空价差=top-bottom；
#              分状态=锚定风险四档（c1_backtest.regime_state_anchored，裁定#229 产物）条件 IC；
#              分域=市值三档（total_shares×close，total_shares 缺失行剔除）；
#              衰减=年度多空价差序列（留痕供 decay 剪）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据缺失->RuntimeError
# [TESTS] 复用 tests/factor/test_fundamentals.py 面板语义；本脚本为统计流程 CLI
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 因子 ⑤ 剪枝/分域证据 CLI（A 类一次性运维，随晋级批次按需手动执行）
"""eval_f2_layers_styles.py — F2 因子分层回测+分状态+市值分域（SOP-B ⑤ 剪枝证据）。

对 FCT-FQ-001/FCT-FQ-002（experimental）产出 ⑤ 剪枝三件：
    ① 分位单调性与多空价差（5 分位等权 fwd20，top−bottom 月度序列 t 检验）
    ② 分状态稳定性（锚定风险四档条件 IC——状态机与因子验证同一 PIT 口径）
    ③ 衰减视图（年度多空价差均值序列）
对六 candidate 产出市值三档分域 IC（FQ-04 优先复检对象）。

用法::

    python scripts/backtest/eval_f2_layers_styles.py --out out.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, ttest_1samp

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

_IS = ("2019-01-01", "2023-12-31")
_OOS = ("2024-01-01", "2026-09-11")
_FWD = 20
_MAIN_FACTORS = ("fq01_accrual", "fq02_cash_conversion")
_ALL_FACTORS = (
    "fq01_accrual", "fq02_cash_conversion", "fq03_gpoa", "fq04_delta_roe_q",
    "gr01_rev_q_yoy", "gr02_np_q_qoq", "fq05_info_quality", "fq06_fscore",
)


def _load_sibling():
    spec = importlib.util.spec_from_file_location(
        "eval_f2_fundamental_ic",
        str(ROOT / "scripts" / "backtest" / "eval_f2_fundamental_ic.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_SQL_STATES = "SELECT trade_date, dominant FROM c1_backtest.regime_state_anchored FINAL ORDER BY trade_date"


def load_states() -> pd.Series:
    """锚定风险四档（裁定#229 产物）→ trade_date → dominant。"""
    from zephyr.data import ch_reader

    tsv = ch_reader.query(_SQL_STATES)
    rows = [line.split("\t") for line in (tsv or "").strip().split("\n") if line]
    return pd.Series({r[0]: r[1] for r in rows}, name="state")



def _mean(x) -> float | None:
    return float(np.nanmean(x)) if len(x) else None


def _t(x) -> float | None:
    return float(ttest_1samp(x, 0.0).pvalue) if len(x) >= 10 else None


def build_result(layers: dict, style_ic: dict, state_counts: dict) -> dict:
    """聚合月度切片 → 最终 JSON 结构（五分位/单调性/多空/分年/分状态/分域）。"""
    result: dict = {"main_factors": {}, "style_ic_by_cap": {}, "state_month_counts": state_counts}
    for f in _MAIN_FACTORS:
        L = layers[f]
        q_mean = [round(float(m / n), 4) if n else None for m, n in zip(L["q_mean"], L["q_n"])]
        ls = np.array(L["ls"], dtype=float)
        by_year = {y: {"mean": round(float(np.mean(v)), 4), "n": len(v)}
                   for y, v in sorted(L["ls_by_year"].items())}
        state_ic = {st: {"mean": round(_mean(v), 4), "n": len(v)}
                    for st, v in sorted(L["state_ic"].items())}
        mono = None
        if all(x is not None for x in q_mean) and len(q_mean) >= 3:
            mono = round(float(spearmanr(range(len(q_mean)), q_mean)[0]), 3)
        result["main_factors"][f] = {
            "quantile_mean_fwd20": q_mean,
            "monotonic_spearman": mono,
            "ls_mean": round(_mean(ls), 4) if len(ls) else None,
            "ls_t_p": _t(ls),
            "ls_months": int(len(ls)),
            "ls_by_year": by_year,
            "state_cond_ic": state_ic,
        }
    for f in _ALL_FACTORS:
        result["style_ic_by_cap"][f] = {
            b: {"mean": round(_mean(v), 4) if v else None, "n": len(v),
                "t_p": round(_t(v), 5) if v else None,
                "pass_002": bool(v and abs(_mean(v)) >= 0.02 and _t(v) is not None and _t(v) < 0.05
                                 and len(v) >= 30)}
            for b, v in style_ic[f].items()
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="F2 分层回测+分状态+市值分域（SOP-B ⑤）")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

def cross_section(t: str, panel_sorted: pd.DataFrame, px_by_date: dict) -> pd.DataFrame:
    """t 日截面：announce<=t 的每标的最新版本 + 市值（total_shares×当日收盘），索引=symbol。"""
    ann_s = panel_sorted["announce_date"]
    vis = panel_sorted[ann_s <= pd.Timestamp(t)].groupby("symbol").tail(1)
    out = vis.droplevel("report_period")
    out["cap"] = out["total_shares"] * px_by_date[t].reindex(out.index)
    return out


def process_main_month(t: str, cs: pd.DataFrame, fwd: pd.Series, state: str | None,
                       year: str, layers: dict) -> None:
    """① 5 分位等权组合与多空价差 + ② 分状态条件 IC（两 experimental 主因子）。"""
    for f in _MAIN_FACTORS:
        pair = pd.concat([cs[f], fwd], axis=1).dropna()
        if len(pair) < 100:
            continue
        try:
            buckets = pd.qcut(pair.iloc[:, 0], 5, labels=False, duplicates="drop")
        except ValueError:
            continue
        q_ret = pair.groupby(buckets)[pair.columns[1]].mean()
        k = len(q_ret)
        layers[f]["q_mean"][:k] += q_ret.to_numpy()
        layers[f]["q_n"][:k] += 1
        ls = float(q_ret.iloc[k - 1] - q_ret.iloc[0])
        layers[f]["ls"].append(ls)
        layers[f]["ls_months"].append(t)
        layers[f]["ls_by_year"].setdefault(year, []).append(ls)
        if not state:
            continue
        sub = pd.concat([cs.loc[pair.index, f], fwd.reindex(pair.index)], axis=1)
        sub["st"] = state
        for st, g in sub.groupby("st"):
            if len(g) >= 50:
                layers[f]["state_ic"].setdefault(
                    st, []).append(float(spearmanr(g.iloc[:, 0], g.iloc[:, 1])[0]))


def process_styles_month(cs: pd.DataFrame, fwd: pd.Series, style_ic: dict) -> None:
    """③ 市值三档分域 IC（八因子全量，六 candidate 复检主体）。"""
    cs_valid = cs.dropna(subset=["cap"])
    if len(cs_valid) < 300:
        return
    try:
        cap_bin = pd.qcut(cs_valid["cap"], 3, labels=["cap_lo", "cap_mid", "cap_hi"])
    except ValueError:
        return
    merged = pd.concat([cs_valid[list(_ALL_FACTORS)], fwd.reindex(cs_valid.index).rename("fwd")],
                       axis=1)
    merged["cap_bin"] = cap_bin
    for f in _ALL_FACTORS:
        for b in ("cap_lo", "cap_mid", "cap_hi"):
            g = merged.loc[merged["cap_bin"] == b, [f, "fwd"]].dropna()
            if len(g) >= 80:
                style_ic[f][b].append(float(spearmanr(g[f], g["fwd"])[0]))


def main() -> int:
    parser = argparse.ArgumentParser(description="F2 分层回测+分状态+市值分域（SOP-B ⑤）")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    ev = _load_sibling()
    panel = ev.load_factor_panel()
    cal = ev.ch_reader_cal()
    states = load_states()
    print(f"面板 {len(panel)} 行 | 交易日历 {len(cal)} | 状态 {len(states)} 日", flush=True)

    month_ends = [d for d in cal if "2019-01-01" <= d <= "2026-08-31" and ev._is_month_end(d, cal)]
    fwd_map = {d: cal[(cal.index(d) + _FWD) % len(cal)] if cal.index(d) + _FWD < len(cal) else None
               for d in month_ends}
    need = sorted({d for d in month_ends if fwd_map[d]} | {f for f in fwd_map.values() if f})
    px = ev.load_rebalance_prices(need)
    px_by_date = {k: v.set_index("symbol")["close"] for k, v in px.groupby("td")}
    panel_sorted = panel.sort_values("announce_date")

    layers = {f: {"q_mean": np.zeros(5), "q_n": np.zeros(5), "ls": [], "ls_months": [],
                  "ls_by_year": {}, "state_ic": {}} for f in _MAIN_FACTORS}
    style_ic = {f: {"cap_lo": [], "cap_mid": [], "cap_hi": []} for f in _ALL_FACTORS}
    state_counts: dict[str, int] = {}

    for t in month_ends:
        f20 = fwd_map.get(t)
        if not f20 or t not in px_by_date or f20 not in px_by_date:
            continue
        px_t, px_f = px_by_date[t], px_by_date[f20]
        fwd = (px_f.reindex(px_t.index) / px_t - 1.0).dropna()
        if len(fwd) < 100:
            continue
        cs = cross_section(t, panel_sorted, px_by_date).reindex(fwd.index)
        state = states.get(t)
        if state:
            state_counts[state] = state_counts.get(state, 0) + 1
        process_main_month(t, cs, fwd, state, t[:4], layers)
        process_styles_month(cs, fwd, style_ic)

    result = build_result(layers, style_ic, state_counts)

    text = json.dumps(result, ensure_ascii=False, indent=1)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
