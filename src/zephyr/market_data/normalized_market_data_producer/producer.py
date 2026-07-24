# [BLUEPRINT] MOD-MKT_DATA | docs/03_modules/MOD-MKT_DATA/ | §normalized_market_data_producer
# [MODULE] zephyr.market_data.normalized_market_data_producer.producer
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.shared.contracts.market_data
# [CONSUMERS] zephyr.factor.core.ctr001_consumer.converter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——ch_reader注入FINAL保证去重；仅用trade_date做截面对齐禁止用ingested_ts；CP-03门禁：产出NormalizedMarketData实例供D_FACTOR消费
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH查询失败->返回空列表(同ch_reader返回空串); 空标的列表->返回空列表; 行解析失败->跳过该行不抛异常
# [TESTS] tests/market_data/test_normalized_market_data_producer.py
# [TTL] permanent
"""NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据供给。

从 ClickHouse c1_market.kline_daily 加载日K行情，转为 CTR-001 NormalizedMarketData
（frozen dataclass, Decimal 字段），供 D_FACTOR 的 ctr001_consumer 消费。

职责边界：
- ch_reader 数据访问（自动注入 FINAL，PIT 去重）
- TSV→NormalizedMarketData 转换（Decimal 字段集中转换）
- 质量标记映射（quality_flag→quality_score；volume=0→is_suspended）
- 幂等键生成（symbol:trade_date）
- 不做任何因子计算——纯数据供给

字段映射（kline_daily → NormalizedMarketData）：
  trade_date   → timestamp（datetime）
  symbol       → symbol
  open/high/low/close/volume/amount/adj_factor → Decimal
  quality_flag → quality_score（1→1.0 通过；0→0.5 异常）
  volume=0     → is_suspended=True（停牌日无成交）
  data_source  → data_source
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Sequence

import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.shared.contracts.market_data import NormalizedMarketData

log = logging.getLogger(__name__)

# 表名真源：business_data_categories.yaml via table_registry（裁定 #ARCH-CH-024）
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
# ch_reader.query() 自动注入 FINAL（ReplacingMergeTree 去重），故 final 占位留空
_SQL_LOAD_KLINE = (
    "SELECT trade_date, symbol, open, high, low, close, volume, amount, "
    "adj_factor, data_source, quality_flag "
    "FROM {tbl}{final} "
    "WHERE symbol IN ({symbols}) "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY symbol, trade_date"
)

# TSV 列顺序（ClickHouse SELECT 返回无表头，按 SELECT 顺序映射）
_KLINE_COLUMNS = [
    "trade_date", "symbol", "open", "high", "low",
    "close", "volume", "amount", "adj_factor", "data_source", "quality_flag",
]

# quality_flag 语义（裁定 #ARCH-CH-021 P0-4）：
#   1 = 已校验通过 → quality_score=1.0
#   0 = 检出异常   → quality_score=0.5（保真标记，下游可据 quality_score<0.7 过滤）
_QFLAG_TO_SCORE = {1: 1.0, 0: 0.5}
_DEFAULT_QUALITY_SCORE = 1.0


def _escape_symbol(symbol: str) -> str:
    """转义标的代码中的单引号，防 SQL 注入。"""
    return str(symbol).replace("'", "\\'")


def _format_symbols(symbols: Sequence[str]) -> str:
    """格式化标的列表为 SQL IN 子句内容（'a','b','c'）。"""
    escaped = [_escape_symbol(s) for s in symbols if s]
    return ",".join(f"'{s}'" for s in escaped)


def _to_decimal(value: str | None) -> Decimal | None:
    """安全转 Decimal；None/空串/nan/None/非数值返回 None。"""
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() in ("none", "nan", "null"):
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def _to_int(value: str | None, default: int = 1) -> int:
    """安全转 int；None/非数值返回 default。"""
    if value is None or value == "":
        return default
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return default


def _tsv_to_dataframe(tsv: str) -> pd.DataFrame:
    """解析 ch_reader 返回的 TSV 为 DataFrame（TSV 无表头，按列顺序映射）。

    全列按 str 读取，避免 pandas dtype 推断把 '000001' 当整数 1（前导零丢失），
    或把空 data_source 当 NaN→'nan' 字符串。数值转换在 _row_to_record 中按需做。
    """
    if not tsv or not tsv.strip():
        return pd.DataFrame()
    df = pd.read_csv(StringIO(tsv), sep="\t", header=None, names=_KLINE_COLUMNS, dtype=str)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def _row_to_record(row: pd.Series) -> NormalizedMarketData | None:
    """单行 kline_daily 数据 → NormalizedMarketData（Decimal 字段转换）。

    解析失败返回 None（调用方跳过）。
    """
    try:
        close = _to_decimal(row["close"])
        if close is None:
            return None
        open_p = _to_decimal(row["open"]) or close
        high = _to_decimal(row["high"]) or close
        low = _to_decimal(row["low"]) or close
        volume = _to_decimal(row["volume"]) or Decimal("0")
        amount = _to_decimal(row["amount"])
        adj_factor = _to_decimal(row["adj_factor"])
        symbol = str(row["symbol"])
        ts = row["trade_date"]
        if isinstance(ts, pd.Timestamp):
            ts = ts.to_pydatetime().replace(tzinfo=timezone.utc)
        elif isinstance(ts, datetime):
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = pd.Timestamp(ts).to_pydatetime().replace(tzinfo=timezone.utc)
        qflag = _to_int(row.get("quality_flag"), default=1)
        quality_score = _QFLAG_TO_SCORE.get(qflag, _DEFAULT_QUALITY_SCORE)
        # 停牌判定：volume=0 视为停牌日（无成交）
        is_suspended = volume == Decimal("0")
        raw_src = row.get("data_source")
        src_str = str(raw_src).strip() if raw_src is not None else ""
        if src_str == "" or src_str.lower() in ("nan", "none", "null"):
            src_str = "unknown"
        data_source = src_str
        return NormalizedMarketData(
            symbol=symbol,
            timestamp=ts,
            open=open_p,
            high=high,
            low=low,
            close=close,
            volume=volume,
            amount=amount,
            adj_factor=adj_factor,
            data_source=data_source,
            idempotency_key=f"{symbol}:{ts:%Y%m%d}",
            quality_score=quality_score,
            is_suspended=is_suspended,
        )
    except (KeyError, ValueError, TypeError) as exc:
        log.warning("行解析失败 symbol=%s: %s", row.get("symbol"), exc)
        return None


def load_kline(
    symbols: Sequence[str], start: str, end: str
) -> list[NormalizedMarketData]:
    """从 ClickHouse 加载日K行情，转为 NormalizedMarketData 列表。

    Args:
        symbols: 标的代码列表（如 ['600519.SH', '000001.SZ']）
        start: 起始日期 'YYYY-MM-DD'
        end: 结束日期 'YYYY-MM-DD'

    Returns:
        NormalizedMarketData 列表。空标的或查询失败返回空列表。
    """
    if not symbols:
        return []
    sql = _SQL_LOAD_KLINE.format(
        tbl=_TBL_KLINE_DAILY, final="",
        symbols=_format_symbols(symbols), start=start, end=end,
    )
    df = _tsv_to_dataframe(ch_reader.query(sql))
    if df.empty:
        return []
    records: list[NormalizedMarketData] = []
    for _, row in df.iterrows():
        rec = _row_to_record(row)
        if rec is not None:
            records.append(rec)
    log.info("load_kline: symbols=%d, date=%s~%s, loaded=%d",
             len(symbols), start, end, len(records))
    return records


def produce(
    symbols: Sequence[str], start: str, end: str
) -> list[NormalizedMarketData]:
    """生产 NormalizedMarketData（load_kline 的语义别名，对齐 CP-03 门禁命名）。

    CP-03 门禁要求 D_MKT_DATA 产出 NormalizedMarketData 供 D_FACTOR 消费。
    本函数是 load_kline 的业务语义入口，供上游 pipeline 调用。

    Args:
        symbols: 标的代码列表
        start: 起始日期 'YYYY-MM-DD'
        end: 结束日期 'YYYY-MM-DD'

    Returns:
        NormalizedMarketData 列表
    """
    return load_kline(symbols, start, end)
