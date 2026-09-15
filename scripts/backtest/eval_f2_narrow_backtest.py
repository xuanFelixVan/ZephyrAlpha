#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.eval_f2_narrow_backtest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.matching_logic; zephyr.backtest.core.strategy_validation_pipeline;
#                zephyr.backtest.core.metrics; zephyr.data.ch_reader
# [CONSUMERS] factor_registry FCT-FQ-001/FCT-FQ-002 ⑥ 窄回测证据（SOP-B ⑥ 策略化前置）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 成本五项口径（费率零硬编码，全量读 MatchingConfig #233 实盘裁定真源）：
#              佣金(万0.854,最低5元不免五)+印花税(万5 卖出单边)+滑点(1bp 双边)+过户费(万0.1 双边，
#              #233 口径并入佣金族)+市场冲击=0（个人资金规模≪ADV、月频换手，冲击模型 P0-003
#              pending 后接入——如实标注）+做T额外成本=0（月频无日内回转）；
#              组合口径=因子 Top-N 等权多头月频（A股融券不可用，不做空头腿；基准=000300 超额）；
#              参数网格预注册（n_quantiles{3,5,10}×top_n{30,50}，禁越界）；
#              WFA=年度折 2019-2023（fold={"sharpe":...}）；OOS=2024-01~2026-08；
#              DSR n_trials=8（本轮评估的因子候选总数，全部留痕喂校正）；
#              裁决走 run_strategy_validation（OverfittingDetector+DecisionGate 默认阈值冻结）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据缺失->RuntimeError；裁决管线非法输入->DecisionGateError 向上抛
# [TESTS] 组合口径由 eval_f2_layers_styles（同装载器）交叉；本脚本 ⑥ 产物直接喂裁决管线
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 因子 ⑥ 窄回测 CLI（A 类一次性运维，随策略化批次按需手动执行）
"""eval_f2_narrow_backtest.py — FCT-FQ-001/002 ⑥ 窄回测（SOP-B ⑥，策略化前置）。

把 experimental 因子变成可交易口径再考一次：Top-N 等权多头月频组合，
成本五项全量（费率读 MatchingConfig #233 实盘裁定真源，零硬编码），
产出 IS/WFA 年折/OOS 三段净超额 Sharpe + 参数敏感性（预注册网格）+ DSR，
喂 run_strategy_validation（OverfittingDetector 三维 + DecisionGate 三阶段门控）。

用法::

    python scripts/backtest/eval_f2_narrow_backtest.py --out out.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from decimal import Decimal

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "backtest"))

from _f2_eval_common import (  # noqa: E402 — F2 出证公共装载器（FUNCTION-DUP 单拷贝真源）
    ch_reader_cal,
    is_month_end,
    load_factor_panel,
    load_rebalance_prices,
)

# 参数网格预注册（SOP-B 三护栏：禁越界扩参）
_GRID_N_QUANTILES = (3, 5, 10)
_GRID_TOP_N = (30, 50)
_DEFAULT_TOP_N = 50
_AUM = 3_000_000  # 组合规模假设（元）——min_commission 敏感项，条目 evidence 如实标注
_FWD = 20
_IS = ("2019-01-01", "2023-12-31")
_OOS = ("2024-01-01", "2026-09-11")
_WFA_YEARS = ("2019", "2020", "2021", "2022", "2023")
_N_TRIALS = 8  # 本轮 F2 评估的因子候选总数（多重检验校正原料）
_FACTORS = ("fq01_accrual", "fq02_cash_conversion")




def monthly_series(factor: str, top_n: int, n_quantiles: int,
                   panel_sorted: pd.DataFrame, cal: list[str],
                   px_by_date: dict) -> pd.Series:
    """因子 → Top-N 等权多头月频净收益序列（含成本五项，费率读 MatchingConfig）。"""
    from zephyr.backtest.core.matching_logic import MatchingConfig

    cfg = MatchingConfig()  # #233 实盘裁定费率真源（零硬编码）
    one_side = float(cfg.commission_rate + cfg.transfer_fee_rate
                     + cfg.slippage_bps / Decimal(10000))
    sell_extra = float(cfg.stamp_tax_rate)

    ann_s = panel_sorted["announce_date"]
    month_ends = [d for d in cal if "2019-01-01" <= d <= "2026-08-31" and is_month_end(d, cal)]
    out: dict[str, float] = {}
    prev_hold: set[str] = set()
    for j, t in enumerate(month_ends):
        f20 = month_ends[j + 1] if j + 1 < len(month_ends) else None  # 持有期=月（月末→月末）
        if f20 is None or t not in px_by_date or f20 not in px_by_date:
            continue
        px_t, px_f = px_by_date[t], px_by_date[f20]
        fwd = (px_f.reindex(px_t.index) / px_t - 1.0).dropna()
        vis = panel_sorted[ann_s <= pd.Timestamp(t)].groupby("symbol").tail(1).droplevel("report_period")
        merged = pd.concat([vis[factor].rename("f"), fwd.rename("r")], axis=1).dropna()
        if len(merged) < n_quantiles * 50:
            continue
        try:
            buckets = pd.qcut(merged["f"], n_quantiles, labels=False, duplicates="drop")
        except ValueError:
            continue
        top = merged[buckets == n_quantiles - 1]
        picks = top.nlargest(min(top_n, len(top)), "f").index
        gross = float(top.loc[picks, "r"].mean())
        # 换手成本：卖出(旧-新交集外) + 买入(新-旧交集外)，按等权 AUM 计每笔最小佣金
        cur = set(picks)
        n_sell, n_buy = len(prev_hold - cur), len(cur - prev_hold)
        per_trade = _AUM / max(len(cur), 1)
        comm_sell = max(per_trade * float(cfg.commission_rate), float(cfg.min_commission))
        comm_buy = max(per_trade * float(cfg.commission_rate), float(cfg.min_commission))
        n_kept = len(cur & prev_hold)
        turnover = (n_sell + n_buy) / max(len(cur), 1)  # 换手率（单边口径）
        cost_ratio = (
            n_sell / max(len(cur), 1) * (comm_sell / per_trade + sell_extra + one_side)
            + n_buy / max(len(cur), 1) * (comm_buy / per_trade + one_side)
        ) if per_trade > 0 else 0.0
        prev_hold = cur
        out[t] = gross - cost_ratio
    return pd.Series(out).sort_index()


def sharpe(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 6 or x.std(ddof=1) == 0:
        return 0.0
    return float(x.mean() / x.std(ddof=1) * np.sqrt(12))


def _excess(port: pd.Series, bench: pd.Series) -> pd.Series:
    """月度算术超额（组合净收益 − 000300 月收益）。"""
    aligned = pd.concat([port, bench.reindex(port.index)], axis=1).dropna()
    return aligned.iloc[:, 0] - aligned.iloc[:, 1]


from zephyr.data.table_registry import get_registry  # noqa: E402 — 表名真源（#ARCH-CH-024）

_TBL_KLINE_INDEX = get_registry().table("market_index_kline")
_SQL_BENCH = (
    "SELECT trade_date, toFloat64(close) AS close FROM " + _TBL_KLINE_INDEX + " "
    "WHERE symbol='000300' AND trade_date >= '2018-12-01' ORDER BY trade_date"
)


def ev_load_bench() -> pd.Series:
    """000300 指数月末日收盘（基准真源=c1_market.kline_index）。"""
    from zephyr.data import ch_reader

    tsv = ch_reader.query(_SQL_BENCH)
    rows = [ln.split("\t") for ln in (tsv or "").strip().split("\n") if ln]
    s = pd.Series({r[0]: float(r[1]) for r in rows}).sort_index()
    me = [d for d in s.index if _is_me(d, s.index)]
    return s[me]


def _is_me(d: str, idx: pd.Index) -> bool:
    i = idx.get_loc(d)
    nxt = idx[i + 1] if i + 1 < len(idx) else None
    return nxt is None or str(nxt)[:7] != d[:7]


def main() -> int:
    parser = argparse.ArgumentParser(description="FCT-FQ-001/002 ⑥ 窄回测（成本五项+WFA/OOS+过拟合门禁）")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    from zephyr.backtest.core.strategy_validation_pipeline import (
        StrategyValidationRequest,
        run_strategy_validation,
    )
    from zephyr.simulation.deflated_sharpe_calculator import DeflatedSharpeCalculator

    panel = load_factor_panel()
    panel_sorted = panel.sort_values("announce_date")
    cal = ch_reader_cal()
    month_ends_all = [d for d in cal if "2019-01-01" <= d <= "2026-08-31" and is_month_end(d, cal)]
    need = sorted(set(month_ends_all))
    px = load_rebalance_prices(need)
    px_by_date = {k: v.set_index("symbol")["close"] for k, v in px.groupby("td")}
    tsv_b = ev_load_bench()
    bench_ret = tsv_b.pct_change().dropna()  # 000300 指数月收益

    results: dict = {}
    for factor in _FACTORS:
        port = monthly_series(factor, _DEFAULT_TOP_N, 5, panel_sorted, cal, px_by_date)
        exc = _excess(port, bench_ret)
        is_x = exc[(_IS[0] <= exc.index) & (exc.index <= _IS[1])]
        oos_x = exc[(exc.index >= _OOS[0]) & (exc.index <= _OOS[1])]
        wfa_folds = [
            {"window": y, "sharpe": sharpe(exc[(exc.index >= f"{y}-01-01") & (exc.index <= f"{y}-12-31")])}
            for y in _WFA_YEARS
        ]
        # 参数敏感性（预注册网格，IS 口径）
        param_sensitivity: dict = {"n_quantiles": [], "top_n": []}
        for q in _GRID_N_QUANTILES:
            s = monthly_series(factor, _DEFAULT_TOP_N, q, panel_sorted, cal, px_by_date)
            param_sensitivity["n_quantiles"].append((q, sharpe(_excess(s, bench_ret)[
                (_IS[0] <= s.index) & (s.index <= _IS[1])])))
        for n in _GRID_TOP_N:
            s = monthly_series(factor, n, 5, panel_sorted, cal, px_by_date)
            param_sensitivity["top_n"].append((n, sharpe(_excess(s, bench_ret)[
                (_IS[0] <= s.index) & (s.index <= _IS[1])])))
        oos_sharpe = sharpe(oos_x)
        # DSR 走官方件 MOD-SIM-024（月频超额收益序列直入，量纲自洽；A4 退役 metrics.calculate_dsr）
        dsr = (
            DeflatedSharpeCalculator().calculate(
                [float(v) for v in oos_x.values], num_trials=_N_TRIALS, risk_free_rate=0.0
            ).dsr
            if len(oos_x) >= 3
            else None
        )
        request = StrategyValidationRequest(
            strategy_id=f"{factor}-topN{_DEFAULT_TOP_N}-monthly",
            is_sharpe=sharpe(is_x),
            params={"factor": factor, "n_quantiles": 5, "top_n": _DEFAULT_TOP_N,
                    "rebalance": "monthly", "long_only": True, "aum": _AUM},
            walk_forward_results=wfa_folds,
            oos_sharpe=oos_sharpe,
            param_sensitivity=param_sensitivity,
            params_locked=True,
            perturbed_results=None,
            period_results=[{"period": y,
                             "sharpe": sharpe(exc[(exc.index >= f"{y}-01-01") & (exc.index <= f"{y}-12-31")])}
                            for y in sorted({i[:4] for i in exc.index})],
            dsr=float(dsr) if dsr is not None else None,
        )
        verdict = run_strategy_validation(request)
        results[factor] = {
            "is_sharpe_excess": round(request.is_sharpe, 3),
            "wfa_folds": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in w.items()}
                          for w in wfa_folds],
            "oos_sharpe_excess": round(oos_sharpe, 3),
            "dsr_oos": round(float(dsr), 4) if dsr is not None else None,
            "can_deploy": verdict.can_deploy,
            "gate_passed": bool(getattr(verdict.gate, "overall_passed", False)),
            "is_overfitting": verdict.overfitting.get("is_overfitting"),
            "reasons": list(verdict.reasons)[:6],
            "param_sensitivity": {k: [(p, round(s, 3)) for p, s in v] for k, v in param_sensitivity.items()},
        }
        print(f"{factor}: IS={request.is_sharpe:.3f} OOS={oos_sharpe:.3f} "
              f"can_deploy={verdict.can_deploy} overfit={verdict.overfitting.get('is_overfitting')}", flush=True)

    text = json.dumps(results, ensure_ascii=False, indent=1)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
