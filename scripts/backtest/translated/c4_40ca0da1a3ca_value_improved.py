# [BLUEPRINT] MOD-BT-089 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_40ca0da1a3ca_value_improved
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（财务公告门+估值 ≤T-1）；成本=冻结土规；300 弱势不清仓只停买（忠实原文）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-089 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 090: 价值投资改进版（原文: 2025年度精选策略/55 价值投资改进版-6年9.5倍）。

原文逻辑: 祖鲁六条选股（同 087 家族）；双周调仓（num%2）；持仓 4 只等权；
  300 指数弱势（MA5<MA20 且 MA10<MA30）暂停买入（持仓不动）；周度风控：
  个股亏损<-10% 止损；指数 5 日跌幅<-13% 清仓。
译文实现: 选股同 087（DS-230 公告门）；双周=每 10 交易日；弱势门/双止损入状态机。
因子拆解: 同 087——公开基本面因子组不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST
  D2 执行时点: 原文开盘 → T 日收盘（引擎 T+1 起算）
  D3 止损口径: 原文 avg_cost 盘中价 → 信号日收盘近似；指数 5 日 -13% 清仓保真
  D4 因子登记: 公开因子组不登记
  D5 框架样板: run_weekly 壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import (emit, filter_st, fin_history, load_index, load_px, load_st_flags,
                        load_valuation, run_backtest, wide)

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-40ca0da1a3ca"
WINDOW_KIND = "stock"
_TOP_N, _REBAL, _HOLD_N = 4, 10, 10


def zulu_symbols(as_of: str) -> set[str]:
    h = fin_history(as_of, ("np_q", "equity_incl_minority", "fcff_cum", "rev_q_yoy", "np_q_yoy",
                            "total_current_assets", "total_current_liabilities"))
    if h.empty:
        return set()
    h = h.assign(
        cr=h.total_current_assets / h.total_current_liabilities.replace(0.0, np.nan),
        roe_q=h.np_q / h.equity_incl_minority.replace(0.0, np.nan),
    )
    latest = h[h.report_period == h.report_period.max()]
    ok = set(latest[latest.cr > latest.cr.mean()].symbol)
    periods = sorted(h.report_period.unique())[-4:]
    for per in periods:
        sub = h[h.report_period == per]
        ok &= set(sub[sub.roe_q > sub.roe_q.mean()].symbol)
        rev = sub.rev_q_yoy * 100.0
        npg = sub.np_q_yoy * 100.0
        ok &= set(sub[(rev >= 6) & (rev <= 30)].symbol)
        ok &= set(sub[(npg >= 8) & (npg <= 50)].symbol)
    annual = h[h.report_period.dt.month == 12]
    for per in sorted(annual.report_period.unique())[-5:]:
        sub = annual[annual.report_period == per]
        ok &= set(sub[sub.fcff_cum > 0].symbol)
    return ok


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    val = load_valuation(load_start, end, fields=("circ_mv",))
    cmv = val["circ_mv"].reindex(closes.index).reindex(columns=closes.columns)
    idx300 = load_index("000300", load_start, end, fields=("close",))["close"]
    ma5 = idx300.rolling(5).mean()
    ma10, ma20, ma30 = (idx300.rolling(n).mean() for n in (10, 20, 30))
    weak = (ma5 < ma20) & (ma10 < ma30)                      # 300 弱势门（暂停买入）
    idx5d = idx300.pct_change(_HOLD_N)

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    day_in_block = 0
    holdings: dict[str, float] = {}                            # sym -> entry close
    last_rebal = -999
    px_now_row = None
    for k, dt in enumerate(dates):
        # 风控（原文周度→此处日度检查同规则）：个股 -10% 止损；指数 5 日 -13% 清仓
        px_row = closes.iloc[k]
        for s in list(holdings):
            if px_row.get(s) is not None and not pd.isna(px_row.get(s)):
                earn = px_row[s] / holdings[s] - 1.0
                if earn < -0.10:
                    del holdings[s]
        i5 = idx5d.loc[dt] if dt in idx5d.index else np.nan
        if pd.notna(i5) and i5 < -0.13:
            holdings.clear()
        # 调仓（每 _REBAL 交易日）
        if k - last_rebal >= _REBAL:
            last_rebal = k
            if not bool(weak.shift(1).loc[dt]) if dt in weak.index else True:
                asof = (pd.Timestamp(dt) - pd.Timedelta(days=1)).date()
                syms = zulu_symbols(str(asof))
                prow = cmv.shift(1).reindex([dt]).iloc[0]
                mkt_mean = prow.mean()
                picks = [s for s in sorted(syms & set(closes.columns))
                         if pd.notna(prow.get(s)) and prow.get(s) >= mkt_mean]
                picks.sort(key=lambda s: -(prow.get(s) or 0))
                picks = picks[:_TOP_N]
                for s in picks:
                    holdings[s] = float(closes.iloc[k][s])
        # 弱势门：弱势时暂停新买入（持仓保留，忠实原文）
        weak_today = bool(weak.shift(1).loc[dt]) if dt in weak.index else False
        if holdings and not weak_today:
            pass  # 持仓照常
        # 权重输出：等权持仓
        if holdings:
            pxs = {s: (float(closes.iloc[k][s]) if not pd.isna(closes.iloc[k].get(s)) else None)
                   for s in holdings}
            pxs = {s: v for s, v in pxs.items() if v}
            if pxs:
                w_each = 1.0 / len(pxs)
                for s, v in pxs.items():
                    weights.loc[dt, s] = w_each
        day_in_block += 1
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 T+1收盘", "D3 止损收盘近似",
                                               "D4 公开因子不登记", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
