#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.eval_f2_rework_variants
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.matching_logic; _f2_eval_common
# [CONSUMERS] factor_registry FCT-FQ-002 改造候选证据（状态条件化/频率网格）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 状态条件化=调仓日按锚定风险四档判持有/转现金（状态=PIT 可见，锚定态机同源）；
#              频率网格=月频 vs 周频；成本口径同窄回测（MatchingConfig #233）；
#              全部变体与 ⑥ 基线月频同数据同门槛对比
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据缺失->RuntimeError
# [TESTS] 复用 tests/factor/test_fundamentals.py 面板语义；本脚本为统计流程 CLI
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 因子改造变体评估 CLI（A 类一次性运维，随改造批次按需手动执行）
"""eval_f2_rework_variants.py — FQ-02 改造候选评估（状态条件化/频率网格，移交项 1）。

基线（⑥ 窄回测）：月频 Top50 多头 IS 超额 Sharpe=+0.421（差 0.5 准入线），
OOS 比率 0.6<0.7。本脚本考三个改造变体（同数据同成本同门槛）：
    a) 月频基准（复现基线）
    b) 月频+状态条件化：仅 r1/r2/r4（中高/中/高风险）持有，r3 低风险态转现金
       ——依据 ⑤：r3 态条件 IC +0.0027 最弱（牛市人人涨，现金流质量分不开）
    c) 周频调仓（持有 5 交易日）
产出各变体 IS/OOS/全样本超额 Sharpe 对照 → 注册表改造证据。
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "backtest"))

from _f2_eval_common import (  # noqa: E402
    ch_reader_cal,
    is_month_end,
    load_factor_panel,
    load_rebalance_prices,
)
from zephyr.backtest.core.matching_logic import MatchingConfig  # noqa: E402
from zephyr.data import ch_reader  # noqa: E402

_FACTOR = "fq02_cash_conversion"
_TOP_N = 50
_AUM = 3_000_000
_STATE_FILTER = {"r1", "r2", "r4"}  # 剔 r3 低风险态（B5 证据）


def load_states() -> dict:
    tsv = ch_reader.query(
        "SELECT trade_date, dominant FROM c1_backtest.regime_state_anchored "
        "FINAL ORDER BY trade_date FORMAT TSV")
    return {r.split("\t")[0]: r.split("\t")[1]
            for r in (tsv or "").strip().split("\n") if r}


def sharpe(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 6 or x.std(ddof=1) == 0:
        return 0.0
    return float(x.mean() / x.std(ddof=1) * np.sqrt(12))


def main() -> int:
    parser = argparse.ArgumentParser(description="FQ-02 改造候选评估（状态条件化/频率网格）")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    cfg = MatchingConfig()
    one_side = float(cfg.commission_rate + cfg.transfer_fee_rate + cfg.slippage_bps / Decimal(10000))
    sell_extra = float(cfg.stamp_tax_rate)

    panel = load_factor_panel()
    ps = panel.sort_values("announce_date")
    ann_s = ps["announce_date"]
    cal = ch_reader_cal()
    states = load_states()

    me = [d for d in cal if "2019-01-01" <= d <= "2026-08-31" and is_month_end(d, cal)]
    hold_m = {me[j]: (me[j + 1] if j + 1 < len(me) else None) for j in range(len(me))}
    week_last: dict = {}
    for d in cal:
        week_last[d[:8]] = d  # 同周保留最后交易日
    weekly = sorted(week_last.values())
    hold_w = {}
    for j, t in enumerate(weekly):
        i = cal.index(t)
        hold_w[t] = cal[i + 5] if i + 5 < len(cal) else None  # 持有 5 交易日

    need = sorted(set(me) | set(weekly) | {h for h in hold_m.values() if h}
                  | {h for h in hold_w.values() if h})
    px_df = load_rebalance_prices(need)
    px = {k: v.set_index("symbol")["close"] for k, v in px_df.groupby("td")}

    def port(reb_dates: list[str], hold_to: dict, state_filter: set | None) -> pd.Series:
        out: dict = {}
        prev_hold: set = set()
        for t in reb_dates:
            h = hold_to.get(t)
            if not h or t not in px or h not in px:
                continue
            st = states.get(t)
            px_t, px_h = px[t], px[h]
            fwd = (px_h.reindex(px_t.index) / px_t - 1.0).dropna()
            vis = ps[ann_s <= pd.Timestamp(t)].groupby("symbol").tail(1).droplevel("report_period")
            merged = pd.concat([vis[_FACTOR].rename("f"), fwd.rename("r")], axis=1).dropna()
            if len(merged) < 100:
                continue
            if state_filter and st not in state_filter:
                prev_hold = set()
                out[t] = 0.0  # 转现金（超额口径下=空仓）
                continue
            try:
                buckets = pd.qcut(merged["f"], 5, labels=False, duplicates="drop")
            except ValueError:
                continue
            top = merged[buckets == 4]
            picks = set(top.nlargest(min(_TOP_N, len(top)), "f").index)
            gross = float(top.loc[list(picks), "r"].mean())
            n_sell, n_buy = len(prev_hold - picks), len(picks - prev_hold)
            per_trade = _AUM / max(len(picks), 1)
            cost = ((n_sell / max(len(picks), 1))
                    * (max(per_trade * float(cfg.commission_rate), 5.0) / per_trade + sell_extra + one_side)
                    + (n_buy / max(len(picks), 1))
                    * (max(per_trade * float(cfg.commission_rate), 5.0) / per_trade + one_side))
            prev_hold = picks
            out[t] = gross - cost
        return pd.Series(out).sort_index()

    bench_ret = nb_bench_monthly()
    variants = {}
    for name, reb, hold, sf in (
        ("月频基线", me, hold_m, None),
        ("月频+状态条件化(剔r3)", me, hold_m, _STATE_FILTER),
        ("周频", weekly, hold_w, None),
        ("周频+状态条件化(剔r3)", weekly, hold_w, _STATE_FILTER),
    ):
        p = port(reb, hold, sf)
        exc = (p - bench_ret.reindex(p.index)).dropna()
        is_x = exc[("2019-01-01" <= exc.index) & (exc.index <= "2023-12-31")]
        oos_x = exc[exc.index >= "2024-01-01"]
        variants[name] = {
            "IS_Sh": round(sharpe(is_x), 3), "OOS_Sh": round(sharpe(oos_x), 3),
            "全样本_Sh": round(sharpe(exc), 3), "月数": int(len(exc)),
            "IS_t_p": round(float(ttest_1samp(is_x, 0.0).pvalue), 4) if len(is_x) >= 10 else None,
        }
    result = {"factor": _FACTOR, "variants": variants,
              "note": "状态条件化=剔 r3 低风险态转现金；超额=对 000300；成本五项 MatchingConfig #233"}
    text = json.dumps(result, ensure_ascii=False, indent=1)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0


def nb_bench_monthly() -> pd.Series:
    tsv = ch_reader.query(_SQL_BENCH)
    rows = [ln.split("\t") for ln in (tsv or "").strip().split("\n") if ln]
    s = pd.Series({r[0]: float(r[1]) for r in rows}).sort_index()
    me = [d for d in s.index if is_month_end(d, list(s.index))]
    return s[me].pct_change().dropna()


_SQL_BENCH = (
    "SELECT trade_date, toFloat64(close) AS close FROM c1_market.kline_index "
    "WHERE symbol='000300' AND trade_date >= '2018-12-01' ORDER BY trade_date"
)


if __name__ == "__main__":
    sys.exit(main())
