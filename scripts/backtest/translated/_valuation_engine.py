# [BLUEPRINT] MOD-BT-096 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated._valuation_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; pandas
# [CONSUMERS] 估值类策略翻译件（PE/PB/股息率排序选股族）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（估值截面 ffill 至当前日）；成本=冻结土规；只支持 stock_indicator 已有列
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-096 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""估值类策略参数化引擎——PE/PB/股息率排序选股的共享底层。

估值因子族策略同构：按估值指标排序取前/后 N 只等权持有，月频/周频/日频调仓。
本模块把"读估值截面→过滤→排序→选股"串成参数化管道，策略文件只传参。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def load_valuation_cross_section(start: str, end: str, metric: str) -> pd.DataFrame:
    """读 stock_indicator 估值截面长表（trade_date, symbol, value），去重 ffill。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _c4_engine import run_query

    raw = pd.DataFrame(run_query(
        f"SELECT trade_date, symbol, toFloat64({metric}) AS val"
        f" FROM c1_market.stock_indicator"
        f" WHERE data_source = 'tushare_daily_basic' AND trade_date >= '{start}' AND trade_date <= '{end}'"
        f" AND {metric} IS NOT NULL AND {metric} > 0"
    ), columns=["trade_date", "symbol", "val"])
    raw["trade_date"] = pd.to_datetime(raw["trade_date"])
    raw = raw.drop_duplicates(subset=["trade_date", "symbol"], keep="last")
    return raw


def build_valuation_strategy(
    start: str, end: str,
    metric: str,              # 'pe' / 'pb' / 'dividend_yield'（dv_ttm→dividend_yield，CH 列名映射）
    ascending: bool,          # True=最低值前 N（低估值），False=最高值前 N（高股息等）
    top_n: int,               # 持仓数
    universe: str,            # 'hs300' / 'zz500' / 'all'
    rebalance: str = "monthly",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """构建估值排序策略的权重矩阵+收盘价宽表。"""
    from _c4_engine import filter_st, load_hs300, load_index_constituents, load_px, load_st_flags, wide

    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=30))[:10]
    px = load_px(load_start, end, fields=("close",))
    if universe == "hs300":
        uni = load_hs300()
    elif universe == "zz500":
        uni = load_index_constituents("000905.SH")
    else:
        uni = set(px["symbol"].unique())
    px = px[px["symbol"].isin(uni)]
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))

    raw = load_valuation_cross_section(load_start, end, metric)
    val_w = raw.pivot(index="trade_date", columns="symbol", values="val").reindex(closes.index).ffill()
    val_w = val_w.reindex(columns=closes.columns)

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    val_shift = val_w.shift(1).reindex(dates)

    # 调仓日集合
    if rebalance == "monthly":
        rebal_dates = set(dates.to_series().groupby(dates.to_period("M")).min())
    elif rebalance == "weekly":
        rebal_dates = set(dates.to_series().groupby(dates.to_period("W")).min())
    else:
        rebal_dates = set(dates)

    for dt in dates:
        if dt not in rebal_dates:
            continue
        row = val_shift.loc[dt].dropna()
        if row.empty:
            continue
        ranked = row.sort_values(ascending=ascending)
        picks = list(ranked.index)[:top_n]
        if picks:
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes
