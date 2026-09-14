# [BLUEPRINT] MOD-BT-096 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated._valuation_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; pandas
# [CONSUMERS] 估值类策略翻译件（PE/PB/股息率/市值排序选股族）；基本面门策略翻译件（financial_indicator PIT）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（估值截面 ffill 至当前日；基本面值自 announce_date 起生效）；成本=冻结土规；估值列=stock_indicator 已有列，基本面列=c3_fundamental.financial_indicator 已有列
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-096 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""估值类策略参数化引擎——PE/PB/股息率/市值排序选股的共享底层。

估值因子族策略同构：按估值指标排序取前/后 N 只等权持有，月频/周频/日频调仓。
本模块把"读估值截面→过滤→排序→选股"串成参数化管道，策略文件只传参。
2026-09-15 扩展：基本面过滤门（c3_fundamental.financial_indicator，announce_date PIT）
+ 基本面主排序源——解锁复合门（增速/ROE/ROA/负债率）策略翻译批。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_FUND_LOAD_PRELOAD_DAYS = 400  # 基本面公告滞后最多约 4 个月，预载 400 天保窗口起点有值


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


def load_fundamental_announcements(start: str, end: str, metric: str) -> pd.DataFrame:
    """读 financial_indicator 公告长表（announce_date, symbol, value）——PIT 原始事件。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _c4_engine import run_query

    raw = pd.DataFrame(run_query(
        f"SELECT announce_date, symbol, toFloat64({metric}) AS val"
        f" FROM c3_fundamental.financial_indicator"
        f" WHERE announce_date >= '{start}' AND announce_date <= '{end}'"
        f" AND {metric} IS NOT NULL"
    ), columns=["announce_date", "symbol", "val"])
    raw["announce_date"] = pd.to_datetime(raw["announce_date"])
    raw = raw.sort_values(["symbol", "announce_date"]).drop_duplicates(
        subset=["announce_date", "symbol"], keep="last")
    return raw


def pit_daily_frame(announcements: pd.DataFrame, daily_index: pd.DatetimeIndex) -> pd.DataFrame:
    """公告事件 → 日频 PIT 宽表（值自 announce_date 起生效，ffill 至下一公告；纯函数可测）。"""
    if announcements.empty:
        return pd.DataFrame(index=daily_index)
    piv = announcements.pivot_table(index="announce_date", columns="symbol",
                                    values="val", aggfunc="last")
    union = daily_index.union(piv.index)
    filled = piv.reindex(union).sort_index().ffill()
    return filled.reindex(daily_index)


def build_valuation_strategy(
    start: str, end: str,
    metric: str,              # 'pe' / 'pb' / 'dividend_yield' / 'circ_mv' 等 stock_indicator 列
    ascending: bool,          # True=最低值前 N（低估值），False=最高值前 N（高股息/大市值等）
    top_n: int,               # 持仓数
    universe: str,            # 'hs300' / 'zz500' / 'all'
    rebalance: str = "monthly",
    sort_source: str = "valuation",            # 'valuation'=stock_indicator 列排序 | 'fundamental'=financial_indicator 列
    gates: list | None = None,                 # [("valuation"|"fundamental", col, op, value), ...] AND 语义
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """构建估值/基本面排序策略的权重矩阵+收盘价宽表。

    gates 示例：[("fundamental", "net_profit_yoy", ">", 10), ("valuation", "pb", "<", 2)]。
    PIT 口径与主排序一致：T 日调仓用 T-1 日截面（shift(1)）；门值缺失=剔除（fail-closed）。
    """
    from _c4_engine import filter_st, load_hs300, load_index_constituents, load_px, load_st_flags, wide

    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=30))[:10]
    fund_load_start = str(pd.Timestamp(start) - pd.Timedelta(days=_FUND_LOAD_PRELOAD_DAYS))[:10]
    px = load_px(load_start, end, fields=("close",))
    if universe == "hs300":
        uni = load_hs300()
    elif universe == "zz500":
        uni = load_index_constituents("000905.SH")
    else:
        uni = set(px["symbol"].unique())
    px = px[px["symbol"].isin(uni)]
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)

    def _val_daily(col: str) -> pd.DataFrame:
        raw = load_valuation_cross_section(load_start, end, col)
        return raw.pivot(index="trade_date", columns="symbol", values="val").reindex(closes.index).ffill()

    def _fund_daily(col: str) -> pd.DataFrame:
        raw = load_fundamental_announcements(fund_load_start, end, col)
        return pit_daily_frame(raw, closes.index).reindex(columns=closes.columns)

    def _daily(source: str, col: str) -> pd.DataFrame:
        return _fund_daily(col) if source == "fundamental" else _val_daily(col)

    # 主排序截面（缓存复用：排序源与门同列时只查一次）
    frames: dict[tuple[str, str], pd.DataFrame] = {}
    rank_source, rank_col = (sort_source, metric)
    needed = {(rank_source, rank_col)} | {(g[0], g[1]) for g in (gates or [])}
    for key in needed:
        frames[key] = _daily(*key)

    rank_shift = frames[(rank_source, rank_col)].shift(1).reindex(dates)
    gate_shifts = [(g, frames[(g[0], g[1])].shift(1).reindex(dates)) for g in (gates or [])]

    # 调仓日集合
    if rebalance == "monthly":
        rebal_dates = set(dates.to_series().groupby(dates.to_period("M")).min())
    elif rebalance == "weekly":
        rebal_dates = set(dates.to_series().groupby(dates.to_period("W")).min())
    else:
        rebal_dates = set(dates)

    _OPS = {">": lambda s, v: s > v, "<": lambda s, v: s < v,
            ">=": lambda s, v: s >= v, "<=": lambda s, v: s <= v}

    for dt in dates:
        if dt not in rebal_dates:
            continue
        row = rank_shift.loc[dt].dropna()
        if row.empty:
            continue
        for (source, col, op, value), gshift in gate_shifts:
            if dt not in gshift.index:
                row = row.iloc[0:0]
                break
            grow = gshift.loc[dt].reindex(row.index)
            masked = row[_OPS[op](grow, value)]
            masked = masked[grow.reindex(masked.index).notna()]
            row = masked
            if row.empty:
                break
        if row.empty:
            continue
        ranked = row.sort_values(ascending=ascending)
        picks = list(ranked.index)[:top_n]
        if picks:
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes
