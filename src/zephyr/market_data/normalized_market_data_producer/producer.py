# [BLUEPRINT] MOD-MKT_DATA | docs/03_modules/MOD-MKT_DATA/ | §normalized_market_data_producer
# [MODULE] zephyr.market_data.normalized_market_data_producer.producer
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.data.symbol_normalizer; zephyr.shared.contracts.market_data
# [CONSUMERS] zephyr.factor.core.ctr001_consumer.converter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——ch_reader注入FINAL保证去重；仅用trade_date做截面对齐禁止用ingested_ts；CP-03门禁：产出NormalizedMarketData实例供D_FACTOR消费；CTR-001 symbol标准化(600519.SH格式)；adj_factor=0视为None(无效值)
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH查询失败->返回空列表(同ch_reader返回空串); 空标的列表->返回空列表; 行解析失败->跳过该行不抛异常
# [TESTS] tests/market_data/test_normalized_market_data_producer.py
# [A_module] module_id=MOD-MKT_DATA | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据供给。

从 ClickHouse c1_market.kline_daily 加载日K行情，转为 CTR-001 NormalizedMarketData
（frozen dataclass, Decimal 字段），供 D_FACTOR 的 ctr001_consumer 消费。

职责边界：
- ch_reader 数据访问（自动注入 FINAL，PIT 去重）
- TSV→NormalizedMarketData 转换（Decimal 字段集中转换）
- symbol 标准化（kline_daily 纯数字 → CTR-001 契约要求的 600519.SH 格式）
- adj_factor=0 视为 None（无效值，裁定#ARCH-ADJFACTOR-NULL-001）
- 质量标记映射（quality_flag→quality_score；volume=0→is_suspended）
- 幂等键生成（normalized_symbol:trade_date）
- 不做任何因子计算——纯数据供给

symbol 双向转换（裁定#ARCH-SYMBOL-NORMALIZE-001, 2026-07-25）：
  入参（契约格式 600519.SH）→ 去后缀查 DB（纯数字 600519）
  DB 返回（纯数字 600519）     → 加后缀产出（契约格式 600519.SH）
  前缀推断：6/9→.SH，0/3→.SZ，8/4→.BJ（A 股标准编码规则）

字段映射（kline_daily → NormalizedMarketData）：
  trade_date   → timestamp（datetime）
  symbol       → symbol（标准化为 600519.SH 格式）
  open/high/low/close/volume/amount → Decimal
  adj_factor   → Decimal（0 视为 None）
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

# A股 symbol 交易所推导已收敛到唯一真源 zephyr.data.symbol_normalizer
# （TRAE-082 分层前缀消歧：3位→2位→1位；裁定 #ARCH-SYMBOL-NORMALIZE-001 /
# #ARCH-DATA-SYMBOL-001/002）。2026-08-17 AI-04 审计治本：删除本文件内嵌的
# 简化版 1 位前缀映射（920xxx 北交所误判 .SH、2xx 深B/5xx 沪基金不补后缀），
# 消除双真源漂移。
from zephyr.data.symbol_normalizer import normalizer as _symbol_normalizer


def _normalize_symbol(symbol: str) -> str:
    """将纯数字 symbol 标准化为 CTR-001 契约要求的 600519.SH 格式。

    kline_daily 存储纯数字 symbol（如 600519），契约要求带交易所后缀（600519.SH）。
    交易所推导委托 symbol_normalizer（TRAE-082 分层前缀消歧真源）。
    已带后缀（含"."）的 symbol 原样返回（幂等）。
    无法推导交易所的 symbol 原样返回（不擅自添加后缀）。
    """
    if not symbol:
        return symbol
    s = str(symbol).strip()
    if "." in s:  # 已带后缀，幂等返回
        return s
    bare, exchange = _symbol_normalizer.normalize_symbol(s)
    if exchange:
        return _symbol_normalizer.to_canonical(bare, exchange)
    return s  # 未知前缀，原样返回


def _strip_symbol_suffix(symbol: str) -> str:
    """去除 symbol 的交易所后缀，返回纯数字代码（600519.SH → 600519）。

    kline_daily.symbol 存储纯数字代码，调用方传入契约格式（600519.SH）时
    需先去后缀再查 DB。幂等：纯数字 symbol 原样返回。
    委托 symbol_normalizer.split_suffix_symbol（真源）。
    """
    if not symbol:
        return symbol
    bare, _exchange = _symbol_normalizer.split_suffix_symbol(str(symbol).strip())
    return bare


def _escape_symbol(symbol: str) -> str:
    """转义标的代码中的单引号，防 SQL 注入。"""
    return str(symbol).replace("'", "\\'")


def _format_symbols(symbols: Sequence[str]) -> str:
    """格式化标的列表为 SQL IN 子句内容（'a','b','c'）。

    自动去除交易所后缀（600519.SH → 600519），匹配 kline_daily 纯数字存储。
    """
    escaped = [_escape_symbol(_strip_symbol_suffix(s)) for s in symbols if s]
    return ",".join(f"'{s}'" for s in escaped)


def _to_decimal(value: str | None) -> Decimal | None:
    """安全转 Decimal；None/空串/nan/None/\\N/非数值返回 None。

    \\N 是 ClickHouse TSV 格式中 NULL 的表示（adj_factor Nullable 列可能返回）。
    """
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() in ("none", "nan", "null") or s == "\\N":
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
        # adj_factor=0 是无效值（数学上不可能，复权因子=0 意味价格归零）。
        # 历史原因：bdpan_qfq ad-hoc writer 用 0 作 placeholder 表示"缺失"。
        # 裁定#ARCH-ADJFACTOR-NULL-001（2026-07-25）：视为 None（缺失），
        # 与 schema Nullable 改造后 NULL 语义一致。
        if adj_factor is not None and adj_factor == Decimal("0"):
            adj_factor = None
        # symbol 标准化：kline_daily 纯数字 → CTR-001 契约要求的 600519.SH 格式
        symbol = _normalize_symbol(str(row["symbol"]))
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

    symbol 格式双向转换（裁定#ARCH-SYMBOL-NORMALIZE-001）：
      入参 symbols 接受契约格式（600519.SH）或纯数字（600519），内部统一
      去后缀查 DB（kline_daily 存储纯数字），产出 NormalizedMarketData.symbol
      标准化为契约格式（600519.SH）。

    Args:
        symbols: 标的代码列表（接受 '600519.SH' 或 '600519' 格式）
        start: 起始日期 'YYYY-MM-DD'
        end: 结束日期 'YYYY-MM-DD'

    Returns:
        NormalizedMarketData 列表（symbol 为 600519.SH 格式）。
        空标的或查询失败返回空列表。
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

# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def to_int(value, default: int = 1) -> int:
    """公共接口：to_int（Stage 4 公共化）。

    2026-08-17 AI-04 审计治本：补回 default=1 默认值（与私有实现 _to_int 对齐），
    原包装丢失默认值导致单参调用 TypeError。
    """
    return _to_int(value, default)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def to_decimal(value) -> Decimal | None:
    """公共接口：to_decimal（Stage 4 公共化）。"""
    return _to_decimal(value)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def strip_symbol_suffix(symbol) -> str:
    """公共接口：strip_symbol_suffix（Stage 4 公共化）。"""
    return _strip_symbol_suffix(symbol)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def row_to_record(row) -> NormalizedMarketData | None:
    """公共接口：row_to_record（Stage 4 公共化）。"""
    return _row_to_record(row)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def normalize_symbol(symbol) -> str:
    """公共接口：normalize_symbol（Stage 4 公共化）。"""
    return _normalize_symbol(symbol)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def format_symbols(symbols) -> str:
    """公共接口：format_symbols（Stage 4 公共化）。"""
    return _format_symbols(symbols)

