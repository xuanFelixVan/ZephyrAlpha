# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.tick_depth_backfill
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.shared.observability.metrics
# [CONSUMERS] scripts.data.backfill_tick_depth5
# [STARTUP] imported
# [MATURITY] stable
# [INVARIANTS] 五档历史回填唯一计算层；行 tuple 与 schemas/categories/market_tick_depth_5.py 的 INSERT_COLUMNS 严格同序(30 列)；只写 c1_market.tick_depth_5（并行旁路表，禁止触碰 tick_data 链路——红线 2）；xtquant 缺失时 fail-fast 由调用方降级；data_source 固定取值 miniqmt(历史回填) 或 qmt_bridge(桥存量补五档)
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单标的抓取失败→该标的 error 列表+继续其余；quality_flag=0 置于解析异常行；全局异常上抛调用方
# [TESTS] tests/zephyr/data/test_tick_depth_backfill.py
# [TTL] permanent
"""五档盘口历史回填计算层（台账 §8.6 任务一/裁定⑤，2026-09-09）。

背景：CH tick_data 按表结构只落 1 档（tick_to_row 取 [0]），但 miniqmt
get_market_data_ex(period='tick') 返回的 19 列 tick 自带完整五档
（93 号备忘 §11.5a 实证）。退役日(9/18)前用 miniqmt 回填近期若干天；
9/18 后大QMT 沙箱同 API 可继续逐日累积。

边界（如实登记）：
- 更早的深史五档任何渠道都不存在（bdpan 历史无 bid/ask）。
- 本模块只写 c1_market.tick_depth_5 并行旁路表；tick_data 链路零变更。

行构造（与 tick_depth_5 INSERT_COLUMNS 同序，30 列）：
    trade_date, timestamp, recorded_time, symbol, market_type, price,
    volume, amount, data_source,
    bid_price1..5, ask_price1..5, bid_volume1..5, ask_volume1..5,
    quality_flag

 recorded_time 用回填执行时刻（非上游时间）——端到端延迟语义在回填场景
退化为"回填批次时间"，列 DEFAULT now() 不可用于显式列 INSERT，故显式传值。

xtquant DataFrame 字段（93 §11.5a 实证 19 列）：
    amount/askPrice[5]/askVol[5]/bidPrice[5]/bidVol[5]/high/lastClose/
    lastPrice/low/open/pvolume/stime/time(epoch ms)/transactionNum/volume
索引=YYYYMMDDHHMMSS 整数（同 miniqmt_provider._fetch_tick_data 语义）。
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterator

from zephyr.data.ch_writer import write_result
from zephyr.data.implementations.miniqmt_provider import MiniQmtIngestProvider
from zephyr.data.provider_base import FetchResult
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# 表名从注册表真源派生（#ARCH-CH-024：禁止硬编码表名字符串）
_TBL_TICK_DEPTH_5 = get_registry().table("market_tick_depth_5")

_DATA_SOURCE_BACKFILL = "miniqmt"
_DATA_SOURCE_BRIDGE = "qmt_bridge"

_COLUMNS = [
    "trade_date",
    "timestamp",
    "recorded_time",
    "symbol",
    "market_type",
    "price",
    "volume",
    "amount",
    "data_source",
    "bid_price1",
    "bid_price2",
    "bid_price3",
    "bid_price4",
    "bid_price5",
    "ask_price1",
    "ask_price2",
    "ask_price3",
    "ask_price4",
    "ask_price5",
    "bid_volume1",
    "bid_volume2",
    "bid_volume3",
    "bid_volume4",
    "bid_volume5",
    "ask_volume1",
    "ask_volume2",
    "ask_volume3",
    "ask_volume4",
    "ask_volume5",
    "quality_flag",
]

_NUMERIC_FIELDS = ("price", "volume", "amount")


def _to_decimal(value) -> Decimal | None:
    """安全转 Decimal；None/NaN/非法值 → None（Nullable 列）。"""
    if value is None:
        return None
    try:
        d = Decimal(str(value))
        if d != d:  # NaN
            return None
        return d
    except (InvalidOperation, ValueError, TypeError):
        return None


def _to_uint(value) -> int | None:
    """安全转非负整数；None/负数/非法值 → None（Nullable 列）。"""
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if f != f or f < 0:
        return None
    return int(f)


def build_depth_row(
    stock_code: str,
    ts_index: str,
    row,
    data_source: str,
    recorded_time_str: str,
) -> tuple:
    """xtquant tick DataFrame 单行 → tick_depth_5 的 30 列 tuple。

    Args:
        stock_code: QMT 格式代码（如 000001.SZ）
        ts_index: DataFrame 索引（YYYYMMDDHHMMSS 数字串）
        row: DataFrame 行（dict-like，含 bidPrice/askPrice/bidVol/askVol 数组）
        data_source: "miniqmt"（历史回填）或 "qmt_bridge"（桥存量补五档）
        recorded_time_str: 回填执行时刻 "YYYY-MM-DD HH:MM:SS"

    Returns:
        30 列 tuple（quality_flag=0 表示解析降级：五档缺失但主字段可用）。
    """
    symbol = MiniQmtIngestProvider._stock_to_symbol(stock_code)
    market_type = MiniQmtIngestProvider.detect_market_type(stock_code)

    s = str(ts_index)
    if len(s) >= 8:
        trade_date = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    else:
        trade_date = recorded_time_str[:10]
    if len(s) >= 14:
        timestamp = f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[12:14]}"
    else:
        timestamp = trade_date + " 00:00:00"

    price = _to_decimal(row.get("lastPrice"))
    if price is None:
        price = _to_decimal(row.get("price"))
    volume = _to_uint(row.get("volume"))
    amount = _to_decimal(row.get("amount"))

    bid_prices = row.get("bidPrice") or []
    ask_prices = row.get("askPrice") or []
    bid_vols = row.get("bidVol") or []
    ask_vols = row.get("askVol") or []

    def _p(seq, i):
        return _to_decimal(seq[i]) if isinstance(seq, (list, tuple)) and len(seq) > i else None

    def _v(seq, i):
        return _to_uint(seq[i]) if isinstance(seq, (list, tuple)) and len(seq) > i else None

    has_depth = any(x is not None for x in (_p(bid_prices, 0), _p(ask_prices, 0)))
    quality_flag = 1 if (price is not None and has_depth) else 0

    return (
        trade_date,
        timestamp,
        recorded_time_str,
        symbol,
        market_type,
        price,
        volume,
        amount,
        data_source,
        _p(bid_prices, 0),
        _p(bid_prices, 1),
        _p(bid_prices, 2),
        _p(bid_prices, 3),
        _p(bid_prices, 4),
        _p(ask_prices, 0),
        _p(ask_prices, 1),
        _p(ask_prices, 2),
        _p(ask_prices, 3),
        _p(ask_prices, 4),
        _v(bid_vols, 0),
        _v(bid_vols, 1),
        _v(bid_vols, 2),
        _v(bid_vols, 3),
        _v(bid_vols, 4),
        _v(ask_vols, 0),
        _v(ask_vols, 1),
        _v(ask_vols, 2),
        _v(ask_vols, 3),
        _v(ask_vols, 4),
        quality_flag,
    )


def fetch_symbol_day_depth(stock_code: str, day: str, data_source: str = _DATA_SOURCE_BACKFILL) -> tuple[list[tuple], str | None]:
    """抓取单标的一天的五档 tick（xtquant get_market_data_ex period='tick'）。

    Args:
        stock_code: QMT 格式代码
        day: "YYYYMMDD"
        data_source: 数据来源标识（miniqmt/qmt_bridge）

    Returns:
        (rows, error)——rows 为 30 列 tuple 列表；error 为 None 或错误说明。
        xtquant 缺失时返回 ([], "xtquant unavailable")。
    """
    try:
        from xtquant import xtdata
    except ImportError as e:
        return [], f"xtquant unavailable: {e}"

    try:
        data = xtdata.get_market_data_ex(
            [], [stock_code], period="tick",
            start_time=day, end_time=day, count=-1,
        )
    except Exception as e:  # noqa: BLE001 — 上游 SDK 异常按标的隔离
        return [], f"get_market_data_ex failed: {e}"

    df = data.get(stock_code) if data else None
    if df is None or len(df) == 0:
        return [], None  # 当日无本地缓存（正常：未下载/非交易日/超出缓存窗）

    recorded_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows: list[tuple] = []
    for ts_index, row in df.iterrows():
        try:
            rows.append(build_depth_row(stock_code, ts_index, row, data_source, recorded_time_str))
        except Exception as e:  # noqa: BLE001 — 单行异常不拖垮整批
            log.warning("build_depth_row failed %s@%s: %s", stock_code, ts_index, e)
    return rows, None


def backfill_days(
    symbols: list[str],
    days: list[str],
    data_source: str = _DATA_SOURCE_BACKFILL,
) -> Iterator[FetchResult]:
    """按 (标的 × 交易日) 抓取并写 c1_market.tick_depth_5。

    每 (symbol, day) 一个 FetchResult 直写 CH（write_result 自动列过滤/
    质量门禁/TSV 转义）。替 xtdata.download_history_data 由调用方决定
    （脚本层含 --download 开关；本模块保持纯读语义）。

    Yields:
        FetchResult（table=c1_market.tick_depth_5，rows=当日行）。
    """
    for stock_code in symbols:
        for day in days:
            t0 = datetime.now()
            rows, error = fetch_symbol_day_depth(stock_code, day, data_source)
            if error:
                yield FetchResult(
                    table=_TBL_TICK_DEPTH_5,
                    columns=_COLUMNS,
                    rows=[],
                    last_key=day,
                    elapsed_sec=0.0,
                    error=f"{stock_code} {day}: {error}",
                )
                continue
            ok = write_result(
                FetchResult(
                    table=_TBL_TICK_DEPTH_5,
                    columns=_COLUMNS,
                    rows=rows,
                    last_key=day,
                    elapsed_sec=(datetime.now() - t0).total_seconds(),
                )
            )
            if not ok:
                yield FetchResult(
                    table=_TBL_TICK_DEPTH_5,
                    columns=_COLUMNS,
                    rows=[],
                    last_key=day,
                    elapsed_sec=0.0,
                    error=f"{stock_code} {day}: CH write failed",
                )
                continue
            yield FetchResult(
                table=_TBL_TICK_DEPTH_5,
                columns=_COLUMNS,
                rows=rows,
                last_key=day,
                elapsed_sec=(datetime.now() - t0).total_seconds(),
            )
