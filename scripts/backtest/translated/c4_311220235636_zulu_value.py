# [BLUEPRINT] MOD-BT-087 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_311220235636_zulu_value
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（财务按 announce_date 公告门，估值/行情用 ≤T-1）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-087 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 087: 祖鲁法则六条选股（原文: 2020年度精选策略/07 穿越牛熊基业长青的价值精选）。

原文逻辑（月频，每月第 5 交易日）：①流通市值≥全市场均值 ②流动比率≥全市场均值
③近四季 ROE≥各期全市场均值 ④近五年年度 FCFF>0 ⑤近四季营收增速 6%~30%
⑥近四季净利增速 8%~50%；按流通市值降序排列，全列表等权买入，调出即卖。
译文实现: 财务数据全部走 DS-230 financial_derived（announce_date 公告门 PIT）；
  ROE=单季净利/净资产；FCFF 年度=Q4 期 fcff_cum。
因子拆解: 市值/流动比率/ROE/FCFF/增速——基本面因子组，公开方法论不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST；原文停牌过滤不可得
  D2 执行时点: 原文开盘 → T 日收盘（引擎 T+1 起算）
  D3 规则⑤⑥原文 eps 口径 → DS-230 净利同比近似；行业过滤无（07 无此条）
  D4 因子登记: 公开基本面因子组不登记
  D5 框架样板: get_data 财务面板 → fin_history 逐期公告门等价实现
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import (emit, filter_st, fin_history, load_px, load_st_flags, load_valuation,
                        run_backtest, wide)

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-311220235636"
WINDOW_KIND = "stock"
_METRICS = ("np_q", "equity_incl_minority", "fcff_cum", "rev_q_yoy", "np_q_yoy",
            "total_current_assets", "total_current_liabilities")


def zulu_symbols(as_of: str) -> set[str]:
    """祖鲁六条选股（公告门 PIT）。"""
    h = fin_history(as_of, _METRICS)
    if h.empty:
        return set()
    h = h.assign(
        cr=h.total_current_assets / h.total_current_liabilities.replace(0.0, np.nan),
        roe_q=h.np_q / h.equity_incl_minority.replace(0.0, np.nan),
    )
    latest = h[h.report_period == h.report_period.max()]
    ok = set(latest[latest.cr > latest.cr.mean()].symbol)                      # ② 流动比率
    periods = sorted(h.report_period.unique())[-4:]
    for per in periods:                                                        # ③ 四季 ROE / ⑤⑥ 增速带
        sub = h[h.report_period == per]
        ok &= set(sub[sub.roe_q > sub.roe_q.mean()].symbol)
        rev = sub.rev_q_yoy * 100.0
        npg = sub.np_q_yoy * 100.0
        ok &= set(sub[(rev >= 6) & (rev <= 30)].symbol)
        ok &= set(sub[(npg >= 8) & (npg <= 50)].symbol)
    annual = h[h.report_period.dt.month == 12]
    for per in sorted(annual.report_period.unique())[-5:]:                     # ④ 五年 FCFF>0
        sub = annual[annual.report_period == per]
        ok &= set(sub[sub.fcff_cum > 0].symbol)
    return ok


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    val = load_valuation(load_start, end, fields=("circ_mv",))
    cmv = val["circ_mv"].reindex(closes.index).reindex(columns=closes.columns)

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    month5 = dates.to_series().groupby(dates.to_period("M")).nth(4)
    for dt in month_first_safe(month5, dates):
        asof = (pd.Timestamp(dt) - pd.Timedelta(days=1)).date()
        syms = zulu_symbols(str(asof))
        prow = cmv.shift(1).reindex([dt]).iloc[0]
        mkt_mean = prow.mean()
        picks = [s for s in sorted(syms & set(closes.columns))
                 if pd.notna(prow.get(s)) and prow.get(s) >= mkt_mean]             # ① 市值≥均值
        if picks:
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes


def month_first_safe(month5, dates):
    return [d for d in month5 if d in set(dates)]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 T+1收盘", "D3 eps→净利同比近似",
                                               "D4 公开因子不登记", "D5 fin_history 等价实现"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
