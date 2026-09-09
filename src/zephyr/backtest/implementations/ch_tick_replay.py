# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_backtest/backtest_engine_blueprint.md
# [MODULE] zephyr.backtest.implementations.ch_tick_replay
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.table_registry; pandas
# [CONSUMERS] zephyr.backtest.core.tick_replay.TickReplayEngine; zephyr.backtest.implementations.event_driven_engine
# [STARTUP] imported
# [MATURITY] stable
# [INVARIANTS] duck-typed 与 MiniQmtQuoteProvider.fetch_historical(symbol/start/end/interval='tick') 同构（返回 DataFrame 同列名）；SQL 按 symbol+时间窗直取（idx_ts/idx_symbol 跳数索引裁剪）；1 档降级如实登记（bid/ask 2-5 档填 0，撮合预校验只用 bid1/ask1——matching_logic 既有口径）；时间窗过滤语义与 TickReplayEngine._apply_time_window 一致
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空窗返回空 DataFrame（TickReplayEngine 既有语义：warning+跳过）；CH 异常抛 CHBackfillReadError 由调用方转 TickReplayError
# [TESTS] tests/zephyr/backtest/test_ch_tick_replay.py
# [TTL] permanent
"""回测 tick 回放 CH adapter（台账 §8.6 任务三/裁定①，2026-09-09）。

背景：event_driven_engine.run_tick 经 MiniQmtQuoteProvider.fetch_historical
（xtquant 本地缓存）读回测 tick——9/18 miniQMT 退役后断供。本 adapter 读
c1_market.tick_data（miniqmt 囤货 + qmt_bridge 双源同表），SQL 直取、
无 SDK 依赖，保持 provider 注入接口不变（duck-typed 替换）。

已知降级（台账 §8.3.1 裁定①如实登记）：
- tick_data 表为 1 档（tick_to_row 取 [0] 设计）：价格/成交量回放全覆盖；
  盘口深度回放 bid/ask 2-5 档填 0——matching_logic 撮合预校验只用
  bid1/ask1（既有口径，1 档够用）。五档深度回放待 tick_depth_5
  （台账 §8.6 任务一）积累后升级（后续可 JOIN 同键五档表回填 2-5 档）。

DataFrame 列契约（与 TickReplayEngine._row_to_tick_snapshot 对齐）：
    timestamp (datetime), last_price, open, high, low, prev_close,
    amount, volume, ask_price_1..5, bid_price_1..5, ask_vol_1..5,
    bid_vol_1..5, stock_status, transaction_num
"""

from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

from zephyr.data.ch_writer import get_client
from zephyr.data.table_registry import get_registry

_logger = logging.getLogger(__name__)

_TBL_TICK_DATA = get_registry().table("market_tick")


class CHBackfillReadError(Exception):
    """CH tick 回放读取错误（调用方 TickReplayEngine 转 TickReplayError）。"""


# tick_data → 回放 DataFrame 的列映射（1 档；2-5 档填 0 如实降级）
_SQL_COLUMNS = (
    "timestamp, price, volume, amount, bid_price, ask_price, bid_volume, ask_volume"
)


def fetch_historical(
    symbol: str,
    start: datetime,
    end: datetime,
    interval: str = "tick",
) -> pd.DataFrame:
    """MiniQmtQuoteProvider.fetch_historical 的 CH duck-typed 等价实现。

    Args:
        symbol: QMT 格式代码（600000.SH）；CH symbol 列存纯码，内部转换
        start/end: 时间窗（含端点；end 为当日则取当日全天）
        interval: 仅支持 "tick"（对齐既有调用语义）

    Returns:
        DataFrame（列契约见模块 docstring）；无数据返回空 DataFrame。

    Raises:
        ValueError: interval 非 tick。
        CHBackfillReadError: CH 查询失败。
    """
    if interval != "tick":
        raise ValueError(f"仅支持 interval='tick'，收到: {interval}")

    bare = symbol.split(".")[0]
    # end 含当天全天（调用方传 datetime，取日期部分做 BETWEEN）
    start_d = start.strftime("%Y-%m-%d")
    end_d = end.strftime("%Y-%m-%d")
    start_ts = start.strftime("%Y-%m-%d %H:%M:%S")
    end_ts = end.strftime("%Y-%m-%d %H:%M:%S")

    sql = f"""
    SELECT {_SQL_COLUMNS}
    FROM {_TBL_TICK_DATA}
    WHERE symbol = '{bare}'
      AND trade_date BETWEEN '{start_d}' AND '{end_d}'
      AND timestamp BETWEEN toDateTime64('{start_ts}', 3, 'Asia/Shanghai')
                        AND toDateTime64('{end_ts}', 3, 'Asia/Shanghai')
      AND price > 0
    ORDER BY timestamp
    """
    try:
        client = get_client()
        rows = client.execute(sql)
    except Exception as e:  # noqa: BLE001 — 统一转 CHBackfillReadError
        raise CHBackfillReadError(f"CH tick 读取失败 symbol={symbol}: {e}") from e

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(
        rows,
        columns=[
            "timestamp", "last_price", "volume", "amount",
            "bid_price_1", "ask_price_1", "bid_vol_1", "ask_vol_1",
        ],
    )
    # 1 档 → 5 档（2-5 档填 0，如实降级；撮合预校验只用 bid1/ask1）
    for i in range(2, 6):
        df[f"bid_price_{i}"] = 0
        df[f"ask_price_{i}"] = 0
        df[f"bid_vol_{i}"] = 0
        df[f"ask_vol_{i}"] = 0
    df["bid_vol_1"] = df["bid_vol_1"].fillna(0)
    df["ask_vol_1"] = df["ask_vol_1"].fillna(0)
    df["open"] = df["last_price"]
    df["high"] = df["last_price"]
    df["low"] = df["last_price"]
    df["prev_close"] = df["last_price"]
    df["stock_status"] = 0
    df["transaction_num"] = 0
    # 列序对齐 _row_to_tick_snapshot 期望（dict 读取，顺序无硬约束，统一排好）
    ordered = [
        "timestamp", "last_price", "open", "high", "low", "prev_close",
        "amount", "volume",
        "ask_price_1", "ask_price_2", "ask_price_3", "ask_price_4", "ask_price_5",
        "bid_price_1", "bid_price_2", "bid_price_3", "bid_price_4", "bid_price_5",
        "ask_vol_1", "ask_vol_2", "ask_vol_3", "ask_vol_4", "ask_vol_5",
        "bid_vol_1", "bid_vol_2", "bid_vol_3", "bid_vol_4", "bid_vol_5",
        "stock_status", "transaction_num",
    ]
    return df[ordered]
