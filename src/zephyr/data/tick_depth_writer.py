# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.tick_depth_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.table_registry; zephyr.shared.market.infer_market_type
# [CONSUMERS] zephyr.data.tick_subscriber; zephyr.data.implementations.tick_depth_backfill
# [STARTUP] imported
# [MATURITY] stable
# [INVARIANTS] 五档 30 列行装配唯一真源（实时 tick dict 路径 depth_row_from_tick / xtquant DataFrame 路径共用 build 语义）；列序与 schemas/categories/intraday/market_tick_depth_5.py INSERT_COLUMNS 严格一致；只产出 tuple 不做 IO；纯码 symbol（与 tick_data 同构）；quality_flag=1 需 price 且 bid1/ask1 齐
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 转换函数纯函数无异常路径（输入异常值→None/quality_flag=0）；缺主价返回 None 行由调用方跳过
# [TESTS] tests/zephyr/data/test_tick_subscriber.py::TestTickDepthBypass; tests/zephyr/data/test_tick_depth_backfill.py
# [TTL] permanent
"""五档盘口行装配器（台账 §8.6 任务一/裁定⑤，2026-09-09）。

两条数据路径共用同一套行装配语义：
- depth_row_from_tick(stock_code, tick)：实时路径——桥 dump/xtdata 推送的
  xtdata 等价 tick dict（bidPrice/askPrice/bidVol/askVol 为 1~5 元素列表）。
- tick_depth_backfill.build_depth_row(...)：历史回填路径（xtquant DataFrame 行）。

列序（30 列，与 tick_depth_5 INSERT_COLUMNS 同序）：
    trade_date, timestamp, recorded_time, symbol, market_type, price,
    volume, amount, data_source,
    bid_price1..5, ask_price1..5, bid_volume1..5, ask_volume1..5, quality_flag
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

_TBL_TICK_DEPTH_5 = get_registry().table("market_tick_depth_5")

DEPTH_COLUMNS = [
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


def _dec(val) -> Decimal | None:
    """安全转 Decimal（None/非法→None；0 保留——盘口 0 档是合法挂单价语义由上游保证）。"""
    if val is None:
        return None
    try:
        d = Decimal(str(val))
        return None if d != d else d
    except (InvalidOperation, ValueError, TypeError):
        return None


def _uint(val):
    if val is None:
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    if f != f or f < 0:
        return None
    return int(f)


def _p(seq, i):
    return _dec(seq[i]) if isinstance(seq, (list, tuple)) and len(seq) > i else None


def _v(seq, i):
    return _uint(seq[i]) if isinstance(seq, (list, tuple)) and len(seq) > i else None


def _infer_market_type(stock_code: str) -> str:
    """QMT stock_code -> market_type（与 tick_subscriber.infer_market_type 逐行同语义）。

    锚定说明：推导真源在 zephyr.data.tick_subscriber（tick_to_row 既有口径），
    此处因依赖方向（底层装配器不依赖上层 subscriber）同语义实现；
    test_tick_subscriber.py::TestTickDepthBypass::test_market_type_anchor
    用同一批代码锚定两实现一致，防止漂移。
    """
    if stock_code.endswith(".SH"):
        code = stock_code[:-3]
        if code.startswith("000") or code.startswith("880"):
            return "index"
        if code.startswith("51"):
            return "etf"
        if code.startswith("50"):
            return "lof"
        return "stock"
    if stock_code.endswith(".SZ"):
        code = stock_code[:-3]
        if code.startswith("399"):
            return "index"
        if code.startswith("159"):
            return "etf"
        if code.startswith("16") or code.startswith("18"):
            return "lof"
        if code.startswith("12") or code.startswith("11"):
            return "cb"
        return "stock"
    if stock_code.endswith(".BJ"):
        return "stock_bj"
    return "stock"


def depth_row_from_tick(stock_code: str, tick: dict, data_source: str = "miniqmt") -> tuple | None:
    """实时 tick dict → tick_depth_5 的 30 列 tuple（缺主价返回 None 由调用方跳过）。

    tick 形态与 tick_to_row 输入完全一致（xtdata 等价 dict）：
        time(epoch ms)/lastPrice/volume/amount/bidPrice[..]/askPrice[..]/
        bidVol[..]/askVol[..]
    symbol 存纯码（去后缀，与 tick_data 同构）；recorded_time=本地接收时刻。
    """
    if not tick or not tick.get("time"):
        return None
    ts_ms = tick.get("time", 0)
    dt = datetime.fromtimestamp(ts_ms / 1000)
    trade_date = dt.date()
    timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    recorded_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    symbol = stock_code.split(".")[0]
    price = _dec(tick.get("lastPrice"))
    volume = _uint(tick.get("volume"))
    amount = _dec(tick.get("amount"))
    bid_prices = tick.get("bidPrice") or []
    ask_prices = tick.get("askPrice") or []
    bid_vols = tick.get("bidVol") or []
    ask_vols = tick.get("askVol") or []

    has_depth = _p(bid_prices, 0) is not None and _p(ask_prices, 0) is not None
    quality_flag = 1 if (price is not None and has_depth) else 0

    return (
        trade_date,
        timestamp_str,
        recorded_time_str,
        symbol,
        _infer_market_type(stock_code),
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
