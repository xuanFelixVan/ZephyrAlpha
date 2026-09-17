# [BLUEPRINT] MOD-BT-102 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_bd42540f86e4_pe_pb
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日用 ≤T-1 估值+收盘价）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-102 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译: PE+PB 双因子价值筛选（原文: 2020年度精选策略/94 PE和PB策略）。

原文: 沪深300 池；PB∈(3,10) 且 PE(LYR)∈(10,20)；max_hold=5；日频调仓。
译文: stock_indicator 表 pe_ttm 代理 pe_lyr（D3）；无排序（wizard input_dict 空壳）→按代码序取前 5 等权。
因子拆解: PE/PB 价值双因子——公开因子，不登记 factor_registry（未过 IC/去马甲检验）。
差异声明: D1 成分快照 / D2 T+1 收盘 / D3 pe_lyr→pe_ttm 代理 / D4 公开因子不登记 / D5 空壳不译。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, filter_st, load_px, load_hs300, load_st_flags, run_backtest, run_query, wide

STRATEGY_ID = "CAND-bd42540f86e4"
WINDOW_KIND = "stock"
_TOP_N = 5


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=30))[:10]
    px = load_px(load_start, end, fields=("close",))
    hs = load_hs300(start, end)
    px = px[px["symbol"].isin(hs)]
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    # 估值截面（stock_indicator 按日取最近不晚于 T-1 的行）
    raw = pd.DataFrame(run_query(
        f"SELECT trade_date, symbol, toFloat64(pe) AS pe, toFloat64(pb) AS pb"
        f" FROM c1_market.stock_indicator"
        f" WHERE data_source = 'tushare_daily_basic' AND trade_date >= '{load_start}' AND trade_date <= '{end}'"
    ), columns=["trade_date", "symbol", "pe", "pb"])
    raw["trade_date"] = pd.to_datetime(raw["trade_date"])
    raw = raw.drop_duplicates(subset=["trade_date", "symbol"], keep="last")
    pe_w = raw.pivot(index="trade_date", columns="symbol", values="pe").reindex(closes.index).ffill()
    pb_w = raw.pivot(index="trade_date", columns="symbol", values="pb").reindex(closes.index).ffill()
    pe_w = pe_w.reindex(columns=closes.columns)
    pb_w = pb_w.reindex(columns=closes.columns)
    cand = (pe_w > 10) & (pe_w < 20) & (pb_w > 3) & (pb_w < 10)
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    c_idx = cand.shift(1).reindex(dates).fillna(False)
    for k, dt in enumerate(dates):
        picks = [s for s in closes.columns if bool(c_idx.iloc[k, closes.columns.get_loc(s)])][:_TOP_N]
        if picks:
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 成分快照", "D2 T+1收盘", "D3 pe_lyr→pe_ttm", "D4 公开因子不登记", "D5 空壳不译"]),
        ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
