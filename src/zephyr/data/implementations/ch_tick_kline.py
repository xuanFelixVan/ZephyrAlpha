# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.ch_tick_kline
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.table_registry
# [CONSUMERS] zephyr.data.implementations.qmt_bridge_provider; zephyr.data.kline_resampler
# [STARTUP] imported
# [MATURITY] stable
# [INVARIANTS] CH 内聚合零搬运（SQL_ 前缀 NO-BARE-SQL 豁免）；OHLCV 口径铁律 open=argMin(price)/close=argMax(price)/high=max/low=min/volume=Δsum/amount=Δsum；Δ 增量口径按 symbol 有序窗内后差（负值=新快照重置，sumIf 过滤）；目标表幂等=ALTER DELETE(BETWEEN trade_date)+INSERT（同 kline_resampler 模式）；symbol 存纯码；pct_change/amplitude 对齐 miniqmt 口径填 0（miniQMT 不提供）
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源表空窗→返回 0 不报错；DELETE/INSERT 失败抛 RuntimeError 由调用方降级；非法 period → ValueError
# [TESTS] tests/zephyr/data/test_ch_tick_kline.py
# [TTL] permanent
"""tick→分钟K线 CH 内自拼（台账 §8.6 任务二/裁定③方案 b，2026-09-09）。

数据流：c1_market.tick_data（miniqmt 囤货 + qmt_bridge 双源同表）
  → SQL 聚合（1min/5min 基础周期）→ c1_market.kline_1min / kline_5min
15/30/60min 由既有 kline_resampler 从 1m/5m 合成（复用，不重写）。

OHLCV 口径铁律（台账 §8.5.1 方案 b）：
- bar 窗口 = toStartOfMinute/trade_time 按 5min 对齐（toStartOfFiveMinute）
- open = argMin(price, timestamp)（窗口内最早快照价）
- close = argMax(price, timestamp)（窗口内最晚快照价）
- high/low = max/min(price)
- volume/amount = Δ 累加：快照 volume/amount 是当日累计值，同 symbol 按
  timestamp 排序后后差（正值累加；0/负值=快照重置或横盘，sumIf 只取正差）
- 集合竞价/午休半根 bar 按窗口自然裁剪（无 tick 的窗口不产行）
- pct_change/amplitude：miniQMT 口径 1min 表填 0（下游已容忍）

幂等写入（kline_resampler 同模式，盘后批量）：
- ALTER TABLE ... DELETE WHERE trade_date BETWEEN ...（mutations_sync=2）
- INSERT INTO ... SELECT 聚合
"""

from __future__ import annotations

import logging

from zephyr.data.ch_writer import get_client
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# 目标表（注册表真源派生，#ARCH-CH-024）
_TBL_KLINE_1MIN = get_registry().table("market_kline_1min")
_TBL_KLINE_5MIN = get_registry().table("market_kline_5min")

# 源表（tick_data）
_SRC_TABLE = get_registry().table("market_tick")

# 支持的基础周期
_PERIODS = {
    "1min": ("1m", _TBL_KLINE_1MIN),
    "5min": ("5m", _TBL_KLINE_5MIN),
}

# NO-BARE-SQL gate 豁免 SQL_ 前缀（同 kline_resampler）
# 1min 表无 data_source 列（DEFAULT local_intraday）：无法按来源区分行——
# DELETE 会连官方历史一起删（#QMT-DAY-0908-OVERWRITE 事故根因）。故 1min 合成
# 默认拒绝覆盖已含数据的窗口，显式 allow_official_overwrite=True 才放行。
SQL_DELETE_KLINE = (
    "ALTER TABLE {table} DELETE "
    "WHERE trade_date BETWEEN '{start}' AND '{end}' "
    "SETTINGS mutations_sync = 2"
)

# 5min 表有 data_source 列：幂等 DELETE 只删本模块写过的 synth_tick 行，
# 官方历史行永不触碰（#QMT-DAY-0908-OVERWRITE 事故教训）
SQL_DELETE_KLINE_5MIN = (
    "ALTER TABLE {table} DELETE "
    "WHERE trade_time BETWEEN '{start} 00:00:00' AND '{end} 23:59:59' "
    "AND data_source = 'synth_tick' "
    "SETTINGS mutations_sync = 2"
)

# tick→分钟 bar 聚合（1min/5min 通用，minutes 参数化）
# Δ 口径：同 symbol 全日按 timestamp 排序，lagInFrame 后差只累加正值
# （快照 volume/amount 为当日累计；重置/横盘产生的非正差不计入）
SQL_SYNTH_KLINE_1MIN = """
INSERT INTO {table}
    (trade_date, trade_time, symbol, open, close, high, low,
     volume, amount, pct_change, amplitude)
SELECT
    toDate(window_start) AS trade_date,
    window_start AS trade_time,
    symbol,
    argMin(price, timestamp) AS open,
    argMax(price, timestamp) AS close,
    max(price) AS high,
    min(price) AS low,
    toUInt64(sumIf(d_vol, d_vol > 0)) AS volume,
    sumIf(d_amt, d_amt > 0) AS amount,
    0 AS pct_change,
    0 AS amplitude
FROM (
    SELECT
        symbol,
        timestamp,
        price,
        volume,
        amount,
        toStartOfMinute(timestamp) AS window_start,
        {lag_volume} - volume AS d_vol,
        {lag_amount} - amount AS d_amt
    FROM {src}
    WHERE trade_date BETWEEN '{start}' AND '{end}'
      AND data_source IN ('miniqmt', 'qmt_bridge')
    ORDER BY symbol, timestamp
    SETTINGS min_bytes_for_seek = 0
)
GROUP BY symbol, window_start
"""

SQL_SYNTH_KLINE_5MIN = """
INSERT INTO {table}
    (trade_time, symbol, open, high, low, close, volume, amount, data_source)
SELECT
    window_start AS trade_time,
    symbol,
    argMin(price, timestamp) AS open,
    max(price) AS high,
    min(price) AS low,
    argMax(price, timestamp) AS close,
    toUInt64(sumIf(d_vol, d_vol > 0)) AS volume,
    sumIf(d_amt, d_amt > 0) AS amount,
    'synth_tick' AS data_source
FROM (
    SELECT
        symbol,
        timestamp,
        price,
        volume,
        amount,
        toStartOfFiveMinute(timestamp) AS window_start,
        {lag_volume} - volume AS d_vol,
        {lag_amount} - amount AS d_amt
    FROM {src}
    WHERE trade_date BETWEEN '{start}' AND '{end}'
      AND data_source IN ('miniqmt', 'qmt_bridge')
    ORDER BY symbol, timestamp
)
GROUP BY symbol, window_start
"""


def _build_synth_sql(period: str, start: str, end: str) -> str:
    """构建指定周期的聚合 INSERT SQL。"""
    if period not in _PERIODS:
        raise ValueError(f"非法周期: {period}，支持 {sorted(_PERIODS)}")
    if period == "1min":
        return SQL_SYNTH_KLINE_1MIN.format(
            table=_TBL_KLINE_1MIN,
            src=_SRC_TABLE,
            start=start,
            end=end,
            lag_volume="lagInFrame(volume, 1) OVER (PARTITION BY symbol, window_start ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)",
            lag_amount="lagInFrame(amount, 1) OVER (PARTITION BY symbol, window_start ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)",
        )
    return SQL_SYNTH_KLINE_5MIN.format(
        table=_TBL_KLINE_5MIN,
        src=_SRC_TABLE,
        start=start,
        end=end,
        lag_volume="lagInFrame(volume, 1) OVER (PARTITION BY symbol, window_start ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)",
        lag_amount="lagInFrame(amount, 1) OVER (PARTITION BY symbol, window_start ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)",
    )


def _build_delete_sql(period: str, start: str, end: str) -> str:
    """构建指定周期的幂等 DELETE SQL（kline_5min 无 trade_date 列，按 tradeTime）。"""
    if period not in _PERIODS:
        raise ValueError(f"非法周期: {period}，支持 {sorted(_PERIODS)}")
    table = _PERIODS[period][1]
    if period == "1min":
        return SQL_DELETE_KLINE.format(table=table, start=start, end=end)
    return SQL_DELETE_KLINE_5MIN.format(table=table, start=start, end=end)


def synth_tick_kline(period: str, start: str, end: str, allow_official_overwrite: bool = False) -> int:
    """tick→分钟K 合成（DELETE+INSERT，盘后批量，防官方数据误覆盖）。

    Args:
        period: "1min" 或 "5min"（15/30/60min 走 kline_resampler）
        start: "YYYY-MM-DD"
        end: "YYYY-MM-DD"
        allow_official_overwrite: 1min 窗口已含数据时是否强删重灌。
            默认 False——miniqmt 尚在产（9/18 退役），官方 1min 仍持续覆盖
            全窗口，此期间 1min 合成只允许跑官方未覆盖的日期；5min 表
            DELETE 自带 data_source='synth_tick' 过滤，不受此门影响。

    Returns:
        本次 INSERT 行数。源窗口无数据返回 0（幂等正常态）。

    Raises:
        RuntimeError: DELETE/INSERT 失败，或 1min 目标窗口已有数据且未显式放行。
    """
    if period not in _PERIODS:
        raise ValueError(f"非法周期: {period}，支持 {sorted(_PERIODS)}")
    table = _PERIODS[period][1]
    client = get_client()

    # 防误覆盖门（#QMT-DAY-0908-OVERWRITE）：1min 无来源列，无法幂等删自己的行——
    # 目标窗口已有数据（无论官方/合成）一律先拒绝，需显式 allow_official_overwrite。
    if period == "1min" and not allow_official_overwrite:
        existing = client.execute(
            f"SELECT count() FROM {table} WHERE trade_date BETWEEN '{start}' AND '{end}'"
        )[0][0]
        if existing:
            raise RuntimeError(
                f"{table} 窗口 [{start}~{end}] 已有 {existing} 行（可能含官方历史）。"
                "1min 合成不覆盖已有数据窗口；确认要重灌时显式传 "
                "allow_official_overwrite=True（先取证备份，见 trae_063 三步验证）"
            )

    del_sql = _build_delete_sql(period, start, end)
    ins_sql = _build_synth_sql(period, start, end)
    try:
        client.execute(del_sql)
    except Exception as e:  # noqa: BLE001 — 统一转 RuntimeError 语义
        raise RuntimeError(f"{table} 幂等 DELETE 失败 [{start}~{end}]: {e}") from e
    try:
        client.execute(ins_sql)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"{table} 聚合 INSERT 失败 [{start}~{end}]: {e}") from e

    # 行数核对（DELETE+INSERT 后窗口内行数）
    where = (
        f"trade_time BETWEEN '{start} 00:00:00' AND '{end} 23:59:59'"
        if period == "5min"
        else f"trade_date BETWEEN '{start}' AND '{end}'"
    )
    count_sql = f"SELECT count() FROM {table} WHERE {where}"
    n = client.execute(count_sql)[0][0]
    log.info("synth_tick_kline %s [%s~%s]: %d bars", period, start, end, n)
    return n


# ---------- 15/30/60min：从 kline_1min 二次合成（kline_resampler 同模式） ----------
# 目标表无 data_source 列（与 1min 同）：防误覆盖门同款（#QMT-DAY-0908-OVERWRITE）
_H_PERIOD_TABLES = {
    "15min": get_registry().table("market_kline_15min"),
    "30min": get_registry().table("market_kline_30min"),
    "60min": get_registry().table("market_kline_60min"),
}

# 15/30/60min 表 INSERT 列序：OCLH（open, close, high, low）——注意与 5min 的 OHLC 不同
SQL_DELETE_H = (
    "ALTER TABLE {table} DELETE "
    "WHERE trade_date BETWEEN '{start}' AND '{end}' "
    "SETTINGS mutations_sync = 2"
)

SQL_SYNTH_H = """
INSERT INTO {table}
    (trade_date, trade_time, symbol, open, close, high, low, volume, amount)
SELECT
    toDate(window_start) AS trade_date,
    window_start AS trade_time,
    symbol,
    argMin(open, trade_time) AS open,
    argMax(close, trade_time) AS close,
    max(high) AS high,
    min(low) AS low,
    sum(volume) AS volume,
    sum(amount) AS amount
FROM {src}
WHERE trade_date BETWEEN '{start}' AND '{end}'
GROUP BY symbol, toStartOfInterval(trade_time, INTERVAL {minutes} MINUTE) AS window_start
"""


def synth_kline_from_1min(period: str, start: str, end: str, allow_official_overwrite: bool = False) -> int:
    """kline_1min → 15/30/60min 幂等合成（DELETE+INSERT，防误覆盖门同 1min）。

    Args:
        period: "15min" / "30min" / "60min"
        start/end: "YYYY-MM-DD"（含端点）
        allow_official_overwrite: 窗口已有数据时显式放行（默认拒绝）。

    Returns:
        合成后窗口内行数（0=源无数据）。
    """
    if period not in _H_PERIOD_TABLES:
        raise ValueError(f"非法周期: {period}，支持 {sorted(_H_PERIOD_TABLES)}")
    table = _H_PERIOD_TABLES[period]
    minutes = int(period.replace("min", ""))
    client = get_client()

    if not allow_official_overwrite:
        existing = client.execute(
            f"SELECT count() FROM {table} WHERE trade_date BETWEEN '{start}' AND '{end}'"
        )[0][0]
        if existing:
            raise RuntimeError(
                f"{table} 窗口 [{start}~{end}] 已有 {existing} 行（可能含官方历史）。"
                "合成不覆盖已有数据窗口；确认重灌时显式传 allow_official_overwrite=True"
            )

    del_sql = SQL_DELETE_H.format(table=table, start=start, end=end)
    ins_sql = SQL_SYNTH_H.format(
        table=table,
        src=_TBL_KLINE_1MIN,
        minutes=minutes,
        start=start,
        end=end,
    )
    try:
        client.execute(del_sql)
        client.execute(ins_sql)
    except Exception as e:  # noqa: BLE001 — 统一转 RuntimeError 语义
        raise RuntimeError(f"{table} 合成失败 [{start}~{end}]: {e}") from e

    n = client.execute(
        f"SELECT count() FROM {table} WHERE trade_date BETWEEN '{start}' AND '{end}'"
    )[0][0]
    log.info("synth_kline_from_1min %s [%s~%s]: %d bars", period, start, end, n)
    return n
