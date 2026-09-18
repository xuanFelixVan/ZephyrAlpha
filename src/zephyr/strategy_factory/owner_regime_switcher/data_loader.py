# [BLUEPRINT] MOD-SOWNER-002 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_regime_switcher.data_loader
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas; typing; zephyr.data.table_registry; zephyr.infrastructure.database_service
# [CONSUMERS] zephyr.strategy_factory.owner_regime_switcher.exam; scripts/strategy_factory/run_s_owner_002_exam.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] DatabaseService 唯一数据入口（禁裸 duckdb/裸 clickhouse_driver）；只读查询；cache 仅 .runtime/tmp（测试隔离铁律：禁写 data/ 业务目录）；ETF 日线由 60min 聚合（kline_etf_daily 历史段缺失，冻结文档已披露）；regime 快照 run_id 钉死；本域查询禁 FINAL（regime/kline 表 FINAL 触发 CH Code 181，2026-09-17 实测）——以 drop_duplicates 同键保末行护栏等价替代
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/空集)
# [TESTS] tests/strategy_factory/test_s_owner_002_redblue.py
# [A_module] module_id=MOD-SOWNER-002 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据装载：篮子 ETF 日线（60min 聚合，执行面）+ regime 快照（调度面）+ 000300 指数日线（检测器质量描述表）。

口径（与 S-OWNER-001 data_loader 同源）:
  * ETF 日线 = kline_etf_60min 逐日聚合（open=首根 open，close=末根 close，
    high/low=极值，amount=sum）；kline_etf_daily 历史段缺失（2026-07 起），冻结 §0 披露。
  * regime: c1_backtest.regime_snapshot_history，run_id 钉死 PINNED_RUN_ID。
  * 本地 parquet cache 于 .runtime/tmp/sowner002_cache（CH 错峰自备 cache，多车道共库不共缓存）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

from zephyr.data.table_registry import get_registry
from zephyr.infrastructure.database_service import DatabaseService

CACHE_DIR = Path(".runtime/tmp/sowner002_cache")

# 表名真源=TableRegistry（TABLE-NAME-REGISTRY 门禁禁硬编码字面量，无 noqa 逃生）。
# 两品类已在 business_data_categories.yaml 在册，故导入期解析安全（禁在顶层调用未注册品类）。
_TBL_ETF_60MIN: Final[str] = get_registry().table("market_etf_kline_60min")
_TBL_INDEX_DAILY: Final[str] = get_registry().table("market_index_kline")

# 与 S-OWNER-001 regime_gate 同一钉用 run（同一次 P0 印教材产出，勿改）
PINNED_RUN_ID = "VAL-P0-20260916-230726"
WARMUP_START = "2018-06-01"  # MA20/动量 20 日 rolling 预热（冻结 §1）
IDX_SYMBOL_CANONICAL = "000300.SH"

__all__: Final = ["PINNED_RUN_ID", "WARMUP_START", "load_basket_daily", "load_regime_snapshots", "load_index_daily"]


def _query_df(sql: str, cache_name: str | None = None) -> pd.DataFrame:
    """只读查询 + 可选 parquet cache（cache 在 .runtime/tmp，进程外可复核）。"""
    cache_path = CACHE_DIR / cache_name if cache_name else None
    if cache_path is not None and cache_path.exists():
        return pd.read_parquet(cache_path)
    df = DatabaseService().get_clickhouse_conn().query_dataframe(sql)
    if cache_path is not None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache_path, index=False)
    return df


def load_basket_daily(symbols: list[str], warmup_start: str = WARMUP_START) -> dict[str, pd.DataFrame]:
    """篮子各标的聚合日线（open/high/low/close/amount，升序 index=trade_date）。

    :raises RuntimeError: 任一标的空数据（冻结 §0 数据契约）。
    """
    out: dict[str, pd.DataFrame] = {}
    sym_list = "','".join(symbols)
    df = _query_df(
        f"SELECT symbol, trade_date, trade_time, toFloat64(open) AS open, toFloat64(high) AS high, "  # noqa: bare-sql  只读行情快照查询，PIT 装载器局部 f-string 按日期参数化，集中化收益低于可读性损失（s-owner002 存量原样收编）
        f"toFloat64(low) AS low, toFloat64(close) AS close, toFloat64(amount) AS amount "
        f"FROM {_TBL_ETF_60MIN} "
        f"WHERE symbol IN ('{sym_list}') AND trade_date >= '{warmup_start}' "
        f"ORDER BY symbol, trade_date, trade_time",
        "basket_60min.parquet",
    )
    if df.empty:
        raise RuntimeError("篮子 60min 数据为空")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    # 幂等护栏（等价 FINAL 语义，规避该表 FINAL 的 CH 181 崩溃）：同键保最后一行
    df = df.drop_duplicates(subset=["symbol", "trade_date", "trade_time"], keep="last")
    for sym, g in df.groupby("symbol"):
        daily = g.groupby("trade_date").agg(
            open=("open", "first"),
            high=("high", "max"),
            low=("low", "min"),
            close=("close", "last"),
            amount=("amount", "sum"),
        )
        out[str(sym)] = daily.sort_index()
    missing = [s for s in symbols if s not in out]
    if missing:
        raise RuntimeError(f"篮子标的缺数据: {missing}")
    return out


def load_regime_snapshots(run_id: str = PINNED_RUN_ID) -> pd.DataFrame:
    """regime 快照（trade_date/dominant/confidence + 7 维概率列；升序）。

    注: 该表 FINAL 触发 CH Code 181（服务端查询崩溃，2026-09-17 实测）；
    run_id 内 (trade_date) 无重复（3621 行/2 run=各 1812 整），弃 FINAL+
    drop_duplicates 幂等护栏语义等价。
    """
    df = _query_df(
        f"SELECT trade_date, dominant, toFloat64(confidence) AS confidence, "  # noqa: bare-sql  只读行情快照查询，PIT 装载器局部 f-string 按日期参数化，集中化收益低于可读性损失（s-owner002 存量原样收编）
        f"p_r1, p_r2, p_r3, p_r4, p_r10, p_r11, p_r12 "
        f"FROM c1_backtest.regime_snapshot_history "
        f"WHERE run_id = '{run_id}' ORDER BY trade_date",
        f"regime_snap_{run_id}.parquet",
    )
    if df.empty:
        raise RuntimeError(f"regime 快照为空 run_id={run_id}")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.drop_duplicates(subset=["trade_date"], keep="last")
    return df.sort_values("trade_date").reset_index(drop=True)


def load_index_daily(warmup_start: str = WARMUP_START) -> pd.DataFrame:
    """000300 指数日线（close；检测器质量描述表前向收益用）。"""
    df = _query_df(
        f"SELECT trade_date, toFloat64(close) AS close FROM {_TBL_INDEX_DAILY} "  # noqa: bare-sql  只读行情快照查询，PIT 装载器局部 f-string 按日期参数化，集中化收益低于可读性损失（s-owner002 存量原样收编）
        f"WHERE symbol_canonical = '{IDX_SYMBOL_CANONICAL}' AND trade_date >= '{warmup_start}' "
        f"ORDER BY trade_date",
        "idx_daily_000300.parquet",
    )
    if df.empty:
        raise RuntimeError("000300 指数日线为空")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.drop_duplicates(subset=["trade_date"], keep="last")  # 幂等护栏（弃 FINAL 规避 181）
    return df.set_index("trade_date").sort_index()
