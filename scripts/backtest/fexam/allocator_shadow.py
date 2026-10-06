# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 批4 分配器五套影子考
# [MODULE] scripts.backtest.fexam.allocator_shadow
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.implementations.vectorized_engine（引擎复用）;
#                zephyr.pf_core.core.msprt_champion_challenger（序贯统计内核复用，可降级）;
#                scripts.backtest.fexam.ch_data; scripts.backtest.fexam.strategy_exam（信号装置复用）
# [CONSUMERS] run_fexam.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 五套同一合成信号+同一窗口（与批2同窗）影子并行；简化实现如实标注
#              （非 pf_alloc 逐行复用——weight 变换向量化和，MOD 锚随行）；
#              只报当前证据量不判终胜负（MOD-PF-008 序贯统计口径）；mSPRT 不可用降级配对 t 并留痕
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单套失败→该套缺失+原因，其余继续
# [TESTS] tests/backtest/fexam/test_strategy_exam.py（权重变换性质同file覆盖）
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（五套定义禁改）
# [TTL] permanent
# create-guard-not-dup: 分配器影子比较（MOD-PF-008口径），无既有等价物
"""allocator_shadow — 批4：5 套分配器影子考（champion-challenger 证据量报告）。

五套（prereg 冻结，roster.ALLOCATORS 同源）：
1. three_layer_stack(champion)=0.5*等权+0.3*逆波+0.2*动量倾斜，SIG-131 钳制±50%均值，RK-08 地板≥0
2. equal_weight(challenger)
3. rk08_solo=逆波动率风险预算（简化）
4. pa015_solo=体制倾斜（trend_up 放大动量/trend_down 放大逆波）（简化）
5. sig131_solo=等权×±50%钳制（简化）

合成信号来源（确定性，禁挑）：批1分数册 pass 因子列（无 pass 时回退全部 ch_backed 列并如实标注降级）。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
for _p in (str(RUN_ROOT / "scripts" / "backtest" / "fexam"), str(_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ch_data  # noqa: E402
from roster import PREREG_V1  # noqa: E402
from strategy_exam import (  # noqa: E402
    WINDOW_IS,
    WINDOW_RUN,
    composite_signal,
    monthly_topn_signals,
    window_metrics,
)

from zephyr.backtest.implementations.vectorized_engine import (  # noqa: E402
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

CLAMP = 0.5  # SIG-131 钳制带宽（±50% 均值权重）


# ---------- 权重变换（纯函数，单测面） ----------


def w_equal(signal_row: pd.Series) -> pd.Series:
    return pd.Series(1.0, index=signal_row.index)


def w_inverse_vol(columns_value_panel: pd.DataFrame, date: pd.Timestamp, lookback: int = 60) -> pd.Series:
    """逆波动率：过去 lookback 日截面收益波动倒数，缺失处用等权兜底。"""
    pos = columns_value_panel.index.get_loc(date)
    lo = max(0, pos - lookback)
    hist = columns_value_panel.iloc[lo : pos + 1].pct_change()
    vol = hist.std()
    inv = 1.0 / vol.replace(0.0, np.nan)
    if inv.notna().sum() < 5:
        return w_equal(columns_value_panel.loc[date])
    return inv.fillna(inv.median())


def w_momentum_tilt(columns_value_panel: pd.DataFrame, date: pd.Timestamp, lookback: int = 20) -> pd.Series:
    """动量倾斜：过去 lookback 日收益率的截面秩 pct。"""
    pos = columns_value_panel.index.get_loc(date)
    lo = max(0, pos - lookback)
    mom = columns_value_panel.iloc[lo : pos + 1].iloc[-1] / columns_value_panel.iloc[lo : pos + 1].iloc[0] - 1.0
    return mom.rank(axis=0, pct=True)


def clamp_weights(w: pd.Series, cap_frac: float = CLAMP) -> pd.Series:
    """SIG-131 钳制：单票权重不超组合均值×(1±cap_frac×n 标准化带)——简化口径=min(w, mean×2) 后归一。"""
    if (w <= 0).all():
        return w
    cap = float(w.mean()) * (1.0 + cap_frac * 2)
    return w.clip(upper=cap)


def normalize(w: pd.Series) -> pd.Series:
    s = float(w.sum())
    return w / s if s > 0 else w * 0.0


def three_layer_weights(eq: pd.Series, iv: pd.Series, mom: pd.Series) -> pd.Series:
    """三层栈：RK-08 地板（权重≥0）+PA-015 倾斜+SIG-131 钳制（简化实现，MOD 锚见册）。"""
    w = 0.5 * eq + 0.3 * iv + 0.2 * mom
    w = w.clip(lower=0.0)  # RK-08 地板：禁负权
    w = clamp_weights(w)  # SIG-131 运动学钳制
    return normalize(w)


def pa015_weights(iv: pd.Series, mom: pd.Series, regime: str | None) -> pd.Series:
    """体制倾斜：trend_up 放大动量，trend_down/其他 放大逆波（简化 MOD-PA-015）。"""
    if regime == "trend_up":
        w = 0.3 * iv + 0.7 * mom
    else:
        w = 0.7 * iv + 0.3 * mom
    return normalize(w.clip(lower=0.0))


# ---------- 批执行 ----------


def _pick_composite_columns(roster: dict[str, Any], factor_book_path: Path | None) -> tuple[list[str], str]:
    """确定性选列：批1 pass 列优先，无 pass 回退全部 ch_backed（如实标注降级）。"""
    picked: list[str] = []
    note = "factor_book_missing_fallback_all"
    if factor_book_path and factor_book_path.exists():
        book = yaml.safe_load(factor_book_path.read_text(encoding="utf-8"))
        passers = [r for r in book.get("results", []) if r.get("verdict") == "pass" and r.get("ch_backings")]
        if passers:
            picked = sorted({r["ch_backings"][0] for r in passers})
            note = f"batch1_pass_columns(n={len(picked)})"
    if not picked:
        picked = sorted(
            {
                b
                for i in roster.get("indicator", [])
                if i.get("bucket") == "ch_backed"
                for b in (i.get("ch_backings") or [])
            }
        )
        if picked:
            note = f"indicator_ch_backed_fallback(n={len(picked)})——批1因子0可考时的prereg回退"
    return picked[:24], note  # 上限24列防爆炸（prereg 冻结口径）


def run_shadow(
    roster: dict[str, Any],
    out_path: Path,
    factor_book_path: Path | None,
    *,
    session_id: str = "st-matrix-20261006",
) -> dict[str, Any]:
    """批4主入口：五套影子跑 + 证据量报告。"""
    device = PREREG_V1["strategy_device"]
    keys, selection_note = _pick_composite_columns(roster, factor_book_path)
    if not keys:
        raise RuntimeError("无可用合成列（批1分数册与 roster 均无 ch_backed 列）——fail-closed")

    flat, close, _vol = _load_inputs(keys)
    regimes, regime_source = ch_data.regime_series(*WINDOW_RUN)

    # 合成信号→top_n 基础目标（等权底仓），再按五套做权重变换
    columns = {k: ch_data.load_panel(*k.rsplit(".", 1), *WINDOW_RUN) for k in keys}
    composite = composite_signal(columns, {})
    base = monthly_topn_signals(composite, close.index, top_n=int(device["top_n"]))
    value_panel = sum(columns.values()) / max(len(columns), 1)

    schemes = {
        "ALC-THREELAYER-001": _scheme_three_layer(base, value_panel),
        "ALC-EQUAL-001": base.copy(),
        "ALC-RK08-001": _scheme_inverse_vol(base, value_panel),
        "ALC-PA015-001": _scheme_regime_tilt(base, value_panel, regimes),
        "ALC-SIG131-001": _scheme_clamped(base),
    }

    engine = DefaultBacktestEngine(BacktestConfig())
    results: list[dict[str, Any]] = []
    navs: dict[str, pd.Series] = {}
    for alc_id, signals in schemes.items():
        try:
            result = engine.run(flat, signals, strategy_name=alc_id)
            nav = engine.last_portfolio.nav_series
            nav = nav[~nav.index.isna()]
            navs[alc_id] = nav
            is_m = window_metrics(nav, *WINDOW_IS)
            oos_m = window_metrics(nav, *ch_data.WINDOW_HOLDOUT)
            results.append(
                {
                    "allocator_id": alc_id,
                    "verdict": "measured",
                    "metrics": {"is": is_m, "oos": oos_m, "regime_sharpe": _nav_regime_sharpe(nav, regimes)},
                    "engine_run_id": result.idempotency_key,
                }
            )
        except Exception as exc:  # noqa: BLE001 — 单套失败不阻断（ERROR_CONTRACT）
            results.append(
                {
                    "allocator_id": alc_id,
                    "verdict": "error",
                    "reason": f"{type(exc).__name__}: {exc}"[:200],
                    "metrics": {},
                }
            )

    evidence = _evidence_report(navs, results)
    book = {
        "doc_type": "fexam_allocator_shadow",
        "version": "v1",
        "generated_at_utc": str(now_utc()),
        "window_definition": {
            "run": list(WINDOW_RUN),
            "is": list(WINDOW_IS),
            "oos_holdout": list(ch_data.WINDOW_HOLDOUT),
            "same_window_as": "batch2策略考同窗",
        },
        "composite_selection": {"columns": keys, "note": selection_note, "cap": "前24列（prereg冻结）"},
        "simplification_note": (
            "五套=权重变换向量化和的简化实现（非 pf_alloc 逐行复用）；"
            "MOD锚：RK-08=risk/core/risk_budget、PA-015=regime_bma_weighting、SIG-131=signal_weight_adjuster；"
            "逐行复用属 M 级施工另行登记"
        ),
        "regime_source": regime_source,
        "results": results,
        "evidence_report": evidence,
        "verdict_note": "只报当前证据量不判终胜负（MOD-PF-008 序贯统计口径）",
    }
    from zephyr.shared.io.file_utils import safe_write_text

    out_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(out_path, yaml.safe_dump(book, allow_unicode=True, sort_keys=False, width=120))
    _write_shadow_md(book, out_path.with_name("allocator_shadow_report_v1.md"))
    return book


def _write_shadow_md(book: dict[str, Any], md_path: Path) -> None:
    """影子报告 md（五套对比表+证据量）。"""
    rows = [
        "| 分配器 | IS Sharpe | OOS Sharpe | OOS MaxDD | OOS 收益 | 判定 |",
        "|--------|-----------|------------|-----------|----------|------|",
    ]
    for r in book.get("results", []):
        m = r.get("metrics") or {}
        is_m, oos_m = m.get("is", {}), m.get("oos", {})
        rows.append(
            f"| {r['allocator_id']} | {is_m.get('sharpe', float('nan')):.2f} "
            f"| {oos_m.get('sharpe', float('nan')):.2f} "
            f"| {oos_m.get('max_drawdown', float('nan')):.2%} "
            f"| {oos_m.get('total_return', float('nan')):.2%} | {r.get('verdict')} |"
        )
    ev = book.get("evidence_report", {})
    lines = [
        "# 批4 分配器影子考报告（v1，机生）",
        "",
        f"- 生成：{book.get('generated_at_utc')}｜同窗=批2｜合成列={book['composite_selection']['note']}",
        f"- 简化实现声明：{book['simplification_note']}",
        "",
        *rows,
        "",
        "## 证据量（champion vs challengers，只报证据不判终胜负）",
        "",
    ]
    for pair in ev.get("pairs", []):
        lines.append(
            f"- {ev.get('champion')} vs {pair.get('challenger')}: "
            f"n={pair.get('n_days')} 年化差={pair.get('ann_diff', float('nan')):.2%} "
            f"t={pair.get('t_stat', float('nan')):.2f}"
        )
    lines += ["", f"> {book.get('verdict_note')}"]
    from zephyr.shared.io.file_utils import safe_write_text

    md_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(md_path, "\n".join(lines) + "\n")


def _load_inputs(keys: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from strategy_exam import _load_run_data

    return _load_run_data()


def _apply_per_rebalance(base: pd.DataFrame, fn) -> pd.DataFrame:
    out = base.copy()
    for d in base.index:
        row = base.loc[d]
        active = row[row > 0]
        if active.empty:
            continue
        w = fn(d, active)
        out.loc[d, active.index] = w.reindex(active.index).fillna(0.0)
    return out


def _scheme_three_layer(base: pd.DataFrame, value_panel: pd.DataFrame) -> pd.DataFrame:
    def fn(d: pd.Timestamp, active: pd.Series) -> pd.Series:
        eq = pd.Series(1.0, index=active.index)
        iv_full = w_inverse_vol(value_panel[active.index], d)
        mom_full = w_momentum_tilt(value_panel[active.index], d)
        return (
            three_layer_weights(
                eq, iv_full.reindex(active.index).fillna(1.0), mom_full.reindex(active.index).fillna(0.5)
            )
            * active.sum()
        )

    return _apply_per_rebalance(base, fn)


def _scheme_inverse_vol(base: pd.DataFrame, value_panel: pd.DataFrame) -> pd.DataFrame:
    def fn(d: pd.Timestamp, active: pd.Series) -> pd.Series:
        iv = w_inverse_vol(value_panel[active.index], d).reindex(active.index).fillna(1.0)
        return normalize(iv) * active.sum()

    return _apply_per_rebalance(base, fn)


def _scheme_regime_tilt(base: pd.DataFrame, value_panel: pd.DataFrame, regimes: pd.Series) -> pd.DataFrame:
    def fn(d: pd.Timestamp, active: pd.Series) -> pd.Series:
        regime = None
        if not regimes.empty:
            prior = regimes[regimes.index <= d]
            regime = str(prior.iloc[-1]) if len(prior) else None
        iv = w_inverse_vol(value_panel[active.index], d).reindex(active.index).fillna(1.0)
        mom = w_momentum_tilt(value_panel[active.index], d).reindex(active.index).fillna(0.5)
        return pa015_weights(iv, mom, regime) * active.sum()

    return _apply_per_rebalance(base, fn)


def _scheme_clamped(base: pd.DataFrame) -> pd.DataFrame:
    def fn(_d: pd.Timestamp, active: pd.Series) -> pd.Series:
        return clamp_weights(normalize(active))

    return _apply_per_rebalance(base, fn)


def _nav_regime_sharpe(nav: pd.Series, regimes: pd.Series) -> dict[str, dict[str, float]]:
    from strategy_exam import regime_sharpe as _rs

    return _rs(nav, regimes)


def _evidence_report(navs: dict[str, pd.Series], results: list[dict[str, Any]]) -> dict[str, Any]:
    """序贯统计证据量：champion(三层栈) vs 每个 challenger 的配对日收益差 + mSPRT（可降级）。"""
    champion_id = "ALC-THREELAYER-001"
    if champion_id not in navs:
        return {"status": "champion_missing", "note": "三层栈跑失败，无证据量可报"}
    out: dict[str, Any] = {"champion": champion_id, "pairs": []}
    for alc_id, nav in navs.items():
        if alc_id == champion_id:
            continue
        joined = pd.concat(
            [navs[champion_id].pct_change().rename("c"), nav.pct_change().rename("d")],
            axis=1,
            join="inner",
        ).dropna()
        if len(joined) < 30:
            out["pairs"].append({"challenger": alc_id, "status": "insufficient_overlap"})
            continue
        diff = joined["c"] - joined["d"]
        se = float(float(diff.std(ddof=0)) / np.sqrt(len(diff))) if float(diff.std(ddof=0)) > 0 else float("nan")
        tstat = float(float(diff.mean()) / se) if se and se == se and se > 0 else float("nan")
        out["pairs"].append(
            {
                "challenger": alc_id,
                "n_days": int(len(joined)),
                "ann_diff": float(float(diff.mean()) * 244),
                "t_stat": tstat,
                "evidence_note": "配对t为当前证据量参考；mSPRT正式判定需逐日流入数据（MOD-PF-008），影子考不判终胜负",
            }
        )
    return out
