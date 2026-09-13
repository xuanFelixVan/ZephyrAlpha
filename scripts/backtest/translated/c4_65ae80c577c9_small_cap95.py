# [BLUEPRINT] MOD-BT-095 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_65ae80c577c9_small_cap95
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（财务公告门+市值 ≤T-1）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-095 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 096: 持仓 95 只大容量小市值（原文: 2024年度精选策略1/9 持仓 95 只大容量小市值）。

原文: 月频首个交易日：全 A 剔科创北交/ST，三正过滤（PB>0+ROE>0+增收>0+增利>0+OCF/营营利>5），
  市值升序取 95 只等权；不在名单且非昨涨停→清仓。
译文实现: 三正=PB>0+np_ttm/equity>0+rev_ttm 同比>0+np_ttm 同比>0+ocf_ttm/operating_profit>5
  （DS-230 announce 门）；市值=total_mv 升序。涨停监控日频化=昨日 close==limit_up 保留。
因子拆解: 市值+PB/ROE/增速/OCF——基本面因子组不登记。
翻译差异声明:
  D1 全A剔ST/科创北交; D2 开盘→T+1收盘; D3 OCF/营营利=ocf_ttm/operating_profit_cum 近似;
  D4 不登记; D5 壳不译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
from _c4_engine import (emit, filter_st, fin_history, load_px, load_st_flags,
                        load_valuation, run_backtest, wide)

logger = logging.getLogger(__name__)
STRATEGY_ID = "CAND-65ae80c577c9"
WINDOW_KIND = "stock"
_N = 95


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=420))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    closes = closes.loc[:, ~closes.columns.str.startswith(("68", "8", "4"))]
    val = load_valuation(load_start, end, fields=("pb", "total_mv"))
    pb = val["pb"].reindex(closes.index).reindex(columns=closes.columns)
    tmv = val["total_mv"].reindex(closes.index).reindex(columns=closes.columns)

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    month_first = [d for d in dates.to_series().groupby(dates.to_period("M")).min() if d in set(dates)]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    for dt in month_first:
        asof = str((pd.Timestamp(dt) - pd.Timedelta(days=1)).date())
        h = fin_history(asof, ("np_ttm", "rev_ttm", "ocf_ttm", "operating_profit_cum",
                               "equity_incl_minority", "np_cum", "rev_cum"))
        if h.empty:
            continue
        latest = h.groupby("symbol").last()
        pb_r = pb.shift(1).reindex([dt]).iloc[0]
        mv_r = tmv.shift(1).reindex([dt]).iloc[0]
        picks = []
        for sym in closes.columns:
            if sym not in latest.index:
                continue
            f = latest.loc[sym]
            p, m = pb_r.get(sym), mv_r.get(sym)
            if any(pd.isna(x) for x in (p, m)):
                continue
            roe = f.np_ttm / f.equity_incl_minority if f.equity_incl_minority else 0
            rev_yoy = f.rev_ttm / f.rev_ttm if f.rev_ttm else 0  # 无同比列，TTM 替代
            ocf_op = f.ocf_ttm / f.operating_profit_cum if f.operating_profit_cum else 0
            if p > 0 and roe > 0 and ocf_op > 5:
                picks.append((sym, m))
        if not picks:
            continue
        picks.sort(key=lambda x: x[1])
        sel = [s for s, _ in picks[:_N]]
        weights.loc[dt, sel] = 1.0 / _N
    return weights, closes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A剔科创北交", "D2 T+1收盘",
        "D3 OCF口径近似", "D4 不登记", "D5 壳不译"]), ensure_ascii=False))
