# [BLUEPRINT] MOD-BT-163 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_valuation_pe_pb_double
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.translated._valuation_engine
# [CONSUMERS] C4 快筛批测
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-163 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""双低估值（PE+PB 复合排名）月频前 20 等权（估值因子族·双因子代表）。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _c4_engine import load_hs300, load_px, load_st_flags, wide
from _valuation_engine import load_valuation_cross_section

STRATEGY_ID = "VAL-PEPB-DOUBLE-020"
WINDOW_KIND = "stock"

def build(s, e):
    from _c4_engine import filter_st, load_st_flags
    load_start = str(pd.Timestamp(s) - pd.Timedelta(days=30))[:10]
    px = load_px(load_start, e, fields=("close",))
    uni = load_hs300()
    px = px[px["symbol"].isin(uni)]
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, e))
    pe_raw = load_valuation_cross_section(load_start, e, "pe")
    pb_raw = load_valuation_cross_section(load_start, e, "pb")
    pe_w = pe_raw.pivot(index="trade_date", columns="symbol", values="val").reindex(closes.index).ffill().reindex(columns=closes.columns)
    pb_w = pb_raw.pivot(index="trade_date", columns="symbol", values="pb" if "pb" in pb_raw.columns else "val").reindex(closes.index).ffill().reindex(columns=closes.columns)
    # 复合排名：PE 排名 + PB 排名取平均（越小越好）
    pe_rank = pe_w.shift(1).rank(axis=1, pct=True)
    pb_rank = pb_w.shift(1).rank(axis=1, pct=True)
    composite = (pe_rank + pb_rank) / 2
    dates = closes.index[(closes.index >= pd.Timestamp(s)) & (closes.index <= pd.Timestamp(e))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    rebal = set(dates.to_series().groupby(dates.to_period("M")).min())
    for dt in dates:
        if dt not in rebal: continue
        row = composite.loc[dt].dropna()
        if row.empty: continue
        picks = list(row.sort_values().index)[:20]
        if picks: weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 HS300", "D2 T+1收盘", "D3 PE+PB复合排名", "D4 公开因子", "D5 引擎"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
