# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t.data_loader
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas; zephyr.infrastructure.database_service; zephyr.backtest.core.data_handler(数据路径纪律同源)
# [CONSUMERS] zephyr.strategy_factory.owner_band_t.exam; scripts/strategy_factory/run_s_owner_001_exam.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] DatabaseService 唯一数据入口（禁裸 duckdb/裸 clickhouse_driver）；只读查询；cache 仅 .runtime/tmp（测试隔离铁律：禁写 data/ 业务目录）；ETF 日线由 60min 聚合（kline_etf_daily 历史段缺失，冻结文档已披露）
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/空集)
# [TESTS] tests/strategy_factory/test_s_owner_001_engine.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据装载：000300 指数日线（信号面）+ 510300 ETF 60min（执行面）+ regime 快照。

口径:
  * 指数日线: c1_market.kline_index FINAL, symbol_canonical='000300.SH'
  * ETF 60min: c1_market.kline_etf_60min FINAL, symbol='510300'（bar 按序对应
    A 股 10:30/11:30/14:00/15:00 四根，存储为 UTC 时刻）
  * ETF 日线 = 60min 聚合（open=首根 open, close=末根 close, high/low=极值,
    amount=sum）；kline_etf_daily 历史段缺失（2026-07 起），冻结文档披露
  * regime: c1_backtest.regime_snapshot_history, run_id 钉死 PINNED_RUN_ID
本地 parquet cache 于 .runtime/tmp/sowner001_cache/（CH 错峰自备 cache，多车道共库不共缓存）。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from zephyr.infrastructure.database_service import DatabaseService
from zephyr.strategy_factory.owner_band_t.regime_gate import PINNED_RUN_ID

CACHE_DIR = Path(".runtime/tmp/sowner001_cache")
IDX_WARMUP_START = "2009-06-01"  # 250 日波动率分位等 rolling 预热


def _get_client():
    return DatabaseService().get_clickhouse_conn()


def _query_df(sql: str, cache_name: str | None = None) -> pd.DataFrame:
    """只读查询 + 可选 parquet cache（cache 在 .runtime/tmp，进程外可复核）。"""
    cache_path = CACHE_DIR / cache_name if cache_name else None
    if cache_path is not None and cache_path.exists():
        return pd.read_parquet(cache_path)
    df = _get_client().query_dataframe(sql)
    if cache_path is not None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache_path, index=False)
    return df


def load_index_daily() -> pd.DataFrame:
    """000300 指数日线（trade_date/open/high/low/close，升序）。"""
    df = _query_df(
        f"SELECT trade_date, toFloat64(open) AS open, toFloat64(high) AS high, "
        f"toFloat64(low) AS low, toFloat64(close) AS close "
        f"FROM c1_market.kline_index FINAL "
        f"WHERE symbol_canonical='000300.SH' AND trade_date >= '{IDX_WARMUP_START}' "
        f"ORDER BY trade_date",
        "idx_daily_000300.parquet",
    )
    if df.empty:
        raise RuntimeError("000300 指数日线为空")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df.set_index("trade_date").sort_index()


def load_etf_hourly() -> pd.DataFrame:
    """510300 ETF 60min（trade_date, bar_seq 0..3, open/high/low/close/amount）。"""
    df = _query_df(
        "SELECT trade_date, trade_time, toFloat64(open) AS open, toFloat64(high) AS high, "
        "toFloat64(low) AS low, toFloat64(close) AS close, toFloat64(amount) AS amount "
        "FROM c1_market.kline_etf_60min FINAL "
        "WHERE symbol='510300' ORDER BY trade_date, trade_time",
        "etf_60min_510300.parquet",
    )
    if df.empty:
        raise RuntimeError("510300 ETF 60min 为空")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    # 墙钟时刻 -> bar 序号（02:30/03:30/06:00/07:00 -> 0/1/2/3；
    # 存储为 UTC 时刻，柱值墙钟分量在任意 tz 标注下不变，剥 tz 取墙钟）
    tt = pd.to_datetime(df["trade_time"])
    if tt.dt.tz is not None:
        tt = tt.dt.tz_localize(None)
    hour = tt.dt.hour * 100 + tt.dt.minute
    # 两种入库编码并存（171 行为本地墙钟）：UTC(230/330/600/700) 与 CST(1030/1130/1400/1500)
    seq_map = {230: 0, 330: 1, 600: 2, 700: 3, 1030: 0, 1130: 1, 1400: 2, 1500: 3}
    df["bar_seq"] = hour.map(seq_map)
    bad = df["bar_seq"].isna()
    if bad.any():
        raise RuntimeError(f"60min bar 时刻异常 {int(bad.sum())} 行（期望 UTC 230/330/600/700 或 CST 1030/1130/1400/1500）")
    df["bar_seq"] = df["bar_seq"].astype(int)
    return df.drop(columns=["trade_time"]).sort_values(["trade_date", "bar_seq"]).reset_index(drop=True)


def aggregate_etf_daily(hourly: pd.DataFrame) -> pd.DataFrame:
    """ETF 日线聚合（含 amount 合计=滑点分层流动性输入）。"""
    g = hourly.groupby("trade_date")
    daily = pd.DataFrame(
        {
            "open": g["open"].first(),
            "high": g["high"].max(),
            "low": g["low"].min(),
            "close": g["close"].last(),
            "amount": g["amount"].sum(),
            "n_bars": g["bar_seq"].count(),
        }
    ).sort_index()
    # 少于 4 根 bar 的残缺日（停牌/数据缺口）保留但打标，engine 跳过其做T
    return daily


def load_regime_snapshots() -> pd.DataFrame:
    """regime 快照（钉死 run_id）。"""
    df = _query_df(
        f"SELECT trade_date, dominant, toFloat64(confidence) AS confidence "
        f"FROM c1_backtest.regime_snapshot_history "
        f"WHERE run_id='{PINNED_RUN_ID}' ORDER BY trade_date",
        f"regime_{PINNED_RUN_ID}.parquet",
    )
    if df.empty:
        raise RuntimeError(f"regime 快照为空 run_id={PINNED_RUN_ID}")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def build_panel() -> dict:
    """组装 engine 面板：指数日线/ETF 日线/ETF 小时线/regime 快照，按 ETF 日历对齐。"""
    idx = load_index_daily()
    hourly = load_etf_hourly()
    etf = aggregate_etf_daily(hourly)
    regime = load_regime_snapshots()
    # 信号面右对齐到执行面日历（ETF 日历为准；指数同日必在——同一 A 股日历）
    idx_aligned = idx.reindex(etf.index)
    missing = idx_aligned["close"].isna()
    if missing.any():
        etf = etf[~missing]
        hourly = hourly[hourly["trade_date"].isin(etf.index)]
        idx_aligned = idx_aligned.loc[etf.index]
    return {
        "idx": idx_aligned,
        "etf": etf,
        "hourly": hourly.set_index(["trade_date", "bar_seq"]).sort_index(),
        "regime": regime,
    }
