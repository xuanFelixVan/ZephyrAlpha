# [BLUEPRINT] MOD-BT-086 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_8d000bf3ccc3_pb_poe_dual_ma
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas; c3_fundamental.financial_indicator
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（财报按 announce_date 公告日进信号，T 日执行用 ≤T-1 已公告数据）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-094 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 094: PB-POE+双均线（原文: 2024年度精选策略1/65，md5=8d000bf3ccc3）。

原文逻辑: 池=全 A；market_cap>800 亿 且 pb_ratio<20 且 roe>7，按 (roe-pb) 降序取前 100；
  MA10>MA60 且 close>MA60（多头双确认）入 buylist；持仓 5 只等权，30 日调仓。
译文实现: roe 取 financial_indicator（announce_date 公告日 PIT 对齐）；pb/market_cap 取
  stock_indicator（tushare_daily_basic，亿元口径换算 total_mv/10000）；均线用 HFQ 收盘。
因子拆解: PB-ROE 复合（价值+质量）——公开因子，不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表内）剔 ST（stk_limit st_flag）
  D2 执行时点: 原文 30 日开盘调仓 → 30 日周期 T 收盘
  D3 财报 PIT: roe 按 announce_date 进信号（公告前不可见，严格时点）
  D4 因子登记: 公开 PB-ROE 不登记
  D5 框架样板: 停牌过滤不可得（HFQ 无停牌列），声明
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, run_backtest, run_query, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-8d000bf3ccc3"
WINDOW_KIND = "stock"
_TOP, _POOL_CAP, _REFRESH = 5, 100, 30
_MV_MIN_YI = 800.0  # 市值下限（亿元）
_ROE_MIN, _PB_MAX = 7.0, 20.0


def _load_fund_panel(start: str, end: str) -> pd.DataFrame:
    """财报面板：announce_date 可见期内每股最新 roe（严格 PIT 长表）。"""
    rows = run_query(
        f"SELECT symbol, announce_date, roe FROM c3_fundamental.financial_indicator "
        f"WHERE announce_date >= '{start}' AND announce_date <= '{end}' "
        f"AND roe IS NOT NULL AND symbol != '' ORDER BY announce_date"
    )
    df = pd.DataFrame(rows, columns=["symbol", "announce_date", "roe"])
    df["announce_date"] = pd.to_datetime(df["announce_date"])
    return df


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=150))[:10]
    px = load_px(load_start, end, fields=("close",))
    close = filter_st(wide(px, "close").ffill(), load_st_flags(load_start, end))
    val = pd.DataFrame(
        run_query(f"SELECT trade_date, symbol, toFloat64(pb) AS pb, toFloat64(total_mv) AS total_mv "
                  f"FROM c1_market.stock_indicator WHERE data_source='tushare_daily_basic' "
                  f"AND trade_date >= '{start}' AND trade_date <= '{end}'"),
        columns=["trade_date", "symbol", "pb", "total_mv"])
    val["trade_date"] = pd.to_datetime(val["trade_date"])
    # 重拉过渡期同键双行（ReplacingMergeTree 合并前）：保市值非空行
    val = val.sort_values(["trade_date", "symbol", "total_mv"], na_position="first")             .drop_duplicates(["trade_date", "symbol"], keep="last")
    pb_w = wide(val, "pb").reindex(close.index).ffill()
    mv_w = wide(val, "total_mv").reindex(close.index).ffill().reindex(columns=close.columns) / 10000.0  # 万元→亿元
    # 财报 roe：公告日可见（严格 PIT）——按公告日 ffill 到交易日
    fund = _load_fund_panel(load_start, end)
    roe_long = fund.rename(columns={"announce_date": "trade_date"}).drop_duplicates(
        subset=["trade_date", "symbol"], keep="last")  # 同日多报取末条（年报+一季报同日公告常见）
    roe_w = wide(roe_long, "roe").reindex(close.index).ffill().reindex(columns=close.columns)
    mv10 = (mv_w.rolling(30).mean() > _MV_MIN_YI)
    base = mv10 & (pb_w < _PB_MAX) & (roe_w > _ROE_MIN)
    score = (roe_w - pb_w).where(base)
    ma10, ma60 = close.rolling(10).mean(), close.rolling(60).mean()
    dual_ma = (close > ma60) & (ma10 > ma60)
    cand = base & dual_ma

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    c_idx = cand.shift(1).reindex(dates).fillna(False)
    s_idx = score.shift(1).reindex(dates)
    rebal_counter = -1
    for k, dt in enumerate(dates):
        if rebal_counter > 0:
            rebal_counter -= 1
            continue
        row = c_idx.iloc[k] & s_idx.iloc[k].notna().fillna(False)
        if not bool(row.any()):
            continue
        picks = list(s_idx.iloc[k][row].sort_values(ascending=False).index)[:_TOP]
        weights.loc[dt, picks] = 1.0 / len(picks)
        rebal_counter = _REFRESH
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 30日收盘调仓", "D3 财报公告日PIT",
                                               "D4 PB-ROE公开因子不入库", "D5 停牌不可剔声明"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
