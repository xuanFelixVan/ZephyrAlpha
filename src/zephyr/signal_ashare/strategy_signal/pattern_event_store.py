# [BLUEPRINT] MOD-SIG-145 | docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_signal.pattern_event_store
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] schemas.categories.market_pattern_event(DDL/INSERT_COLUMNS 真源); zephyr.data.ch_writer(client,延迟加载)
# [CONSUMERS] scripts/data/pattern_event_backfill.py(W2); pattern_win_rate 统计物化(W3); pattern_event_incremental(W4); unified_pattern_engine 扫描结果落库口
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 列序以 schemas INSERT_COLUMNS 为唯一真源(禁硬编码表结构); confirmed_at 必须是形态最后一根 bar 收盘完成时刻(PIT 铁律); 本模块只写事件表，不触发任何信号/下单路径; 注入式 client(测试不触库)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缺必需字段->ValueError; direction/pattern_class 非法->ValueError(引擎封闭集); confidence 出界->裁剪[0,1]; client 不可得->RuntimeError
# [TESTS] tests/signal_ashare/test_pattern_event_store.py
# [A_module] module_id=MOD-SIG-145 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图形事件存储（c1_market.market_pattern_event 读写，MOD-SIG-145 W1）。

图形证据闭环第一环：MOD-SIG-091 统一图形引擎的 PatternEvent 落库口。

    PatternEvent(引擎扫描) → build_event_rows(行契约校验) → PatternEventStore
    → c1_market.market_pattern_event(ReplacingMergeTree 幂等)
    → W3 胜率统计物化 → win_rate_provider 喂 MOD-SIG-115

设计对齐（signal_history_writer 同构裁定）：
  - 输入为行 dict 列表（引擎 PatternEvent.to_dict() 产物 + symbol/confirmed_at
    等落库列）；列序以 schemas/categories/market_pattern_event.py 的
    INSERT_COLUMNS 为唯一真源。
  - event_id 确定性派生（blake2b-64）：同一形态事件（模式/周期/代码/锚日/确认
    时刻/形态名相同）跨 scan_run 重扫产生同 ID → ReplacingMergeTree 去重，
    回填断点续扫与增量重跑不膨胀。
  - 枚举保真：pattern_class/direction 存引擎封闭集原文
    （反转|持续|趋势|支撑阻力|缠论|波浪；向上|向下|中性），不做翻译变换。
  - key_points 接受 list[dict]/tuple[KeyPoint]，统一转 JSON 字符串。
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from datetime import date as _date
from datetime import datetime as _datetime
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_FULL_TABLE = "c1_market.market_pattern_event"

# 引擎封闭集原文（PatternClass/PatternDirection .value，与 MOD-SIG-091 对齐）
_VALID_DIRECTIONS = ("向上", "向下", "中性")
_VALID_PATTERN_CLASSES = ("反转", "持续", "趋势", "支撑阻力", "缠论", "波浪")

_REQUIRED_FIELDS = (
    "pattern_id",
    "pattern_class",
    "direction",
    "timeframe",
    "symbol",
    "anchor_trade_date",
    "confirmed_at",
)


def _insert_columns() -> str:
    """列序真源导入（schemas 包居仓根，非 src/——调用方 sys.path 不含仓根时自适应）。"""
    try:
        from schemas.categories.market_pattern_event import INSERT_COLUMNS

        return INSERT_COLUMNS
    except ImportError:
        repo_root = Path(__file__).resolve().parents[4]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from schemas.categories.market_pattern_event import INSERT_COLUMNS

        return INSERT_COLUMNS


def _get_ch_client():
    """延迟取 clickhouse-driver Client（与 signal_history_writer 同款）。"""
    from zephyr.data.ch_writer import get_client

    return get_client()


def make_event_id(
    *,
    pattern_id: str,
    timeframe: str,
    symbol: str,
    anchor_trade_date: str,
    confirmed_at: str,
    name: str = "",
) -> int:
    """确定性事件 ID（blake2b-64 无符号整数）。

    同一形态事件重放（同模式/周期/代码/锚日/确认时刻/形态名）必产同 ID——
    幂等键语义归 ReplacingMergeTree ORDER BY，本函数只保证确定性。
    入参先经 _coerce_date/_coerce_confirmed_at 归一（'T' 分隔 ISO 串与
    datetime 对象等价），保证跨调用方口径一致。
    """
    anchor = _coerce_date(anchor_trade_date).isoformat()
    confirmed = _coerce_confirmed_at(confirmed_at).isoformat()
    payload = "|".join(
        (
            str(pattern_id),
            str(timeframe),
            str(symbol),
            anchor,
            confirmed,
            str(name),
        )
    )
    return int.from_bytes(hashlib.blake2b(payload.encode("utf-8"), digest_size=8).digest(), "big")


def _coerce_date(value: Any) -> _date:
    """Date 列入参归一：date 直通；datetime 取 .date()；ISO 字符串解析。"""
    if isinstance(value, _datetime):
        return value.date()
    if isinstance(value, _date):
        return value
    return _date.fromisoformat(str(value)[:10])  # 非法格式 ValueError 上抛


def _coerce_confirmed_at(value: Any) -> _datetime:
    """DateTime64(3,'UTC') 列入参归一：datetime 直通；ISO 字符串解析。"""
    if isinstance(value, _datetime):
        return value
    return _datetime.fromisoformat(str(value))


def _coerce_key_points(value: Any) -> str:
    """key_points 归一为 JSON 字符串（list/dict/tuple→json；str 直通；None→''）。"""
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(list(value) if isinstance(value, tuple) else value, ensure_ascii=False)


def build_event_rows(events: list[dict[str, Any]], *, data_source: str) -> list[tuple]:
    """行 dict 列表 → 对齐 INSERT_COLUMNS 的行 tuple 列表。

    Args:
        events: 每行必需 pattern_id/pattern_class/direction/timeframe/symbol/
                anchor_trade_date/confirmed_at，可选 name/key_points/regime_tag/
                scan_run_id/event_id（缺省自动派生）
        data_source: 生产方标识（unified_pattern_engine/pattern_backfill/...）

    Raises:
        ValueError: 缺必需字段 / direction 或 pattern_class 不在引擎封闭集
    """
    if not data_source:
        raise ValueError("data_source 必填（生产方标识，审计血缘用）")
    rows: list[tuple] = []
    for i, e in enumerate(events):
        missing = [f for f in _REQUIRED_FIELDS if e.get(f) in (None, "")]
        if missing:
            raise ValueError(f"事件行 {i} 缺必需字段: {missing}")
        direction = str(e["direction"])
        if direction not in _VALID_DIRECTIONS:
            raise ValueError(f"事件行 {i} direction 非法: {direction}（合法: {_VALID_DIRECTIONS}）")
        pattern_class = str(e["pattern_class"])
        if pattern_class not in _VALID_PATTERN_CLASSES:
            raise ValueError(
                f"事件行 {i} pattern_class 非法: {pattern_class}（合法: {_VALID_PATTERN_CLASSES}）"
            )
        confidence = max(0.0, min(1.0, float(e.get("confidence") or 0.0)))
        anchor = _coerce_date(e["anchor_trade_date"])
        confirmed = _coerce_confirmed_at(e["confirmed_at"])
        event_id = int(e.get("event_id") or 0) or make_event_id(
            pattern_id=str(e["pattern_id"]),
            timeframe=str(e["timeframe"]),
            symbol=str(e["symbol"]),
            anchor_trade_date=str(anchor),
            confirmed_at=str(confirmed),
            name=str(e.get("name") or ""),
        )
        rows.append(
            (
                event_id,
                str(e["pattern_id"]),
                pattern_class,
                direction,
                confidence,
                str(e["timeframe"]),
                str(e["symbol"]).split(".")[0],
                anchor,
                confirmed,
                str(e.get("name") or ""),
                _coerce_key_points(e.get("key_points")),
                str(e.get("regime_tag") or ""),
                str(e.get("scan_run_id") or ""),
                data_source,
            )
        )
    return rows


class PatternEventStore:
    """c1_market.market_pattern_event 读写（注入式 client，测试不触库）。"""

    def __init__(self, client=None, table: str = _FULL_TABLE):
        self._client = client
        self._table = table

    def _ensure_client(self):
        if self._client is None:
            self._client = _get_ch_client()
        if self._client is None:
            raise RuntimeError("clickhouse-driver 不可用（client 未注入且 get_client 返回 None）")
        return self._client

    def insert_events(
        self,
        events: list[dict[str, Any]],
        *,
        data_source: str,
        chunk_size: int = 50_000,
    ) -> int:
        """事件写入（分块 INSERT，幂等靠 ReplacingMergeTree + 确定性 event_id）。

        Returns: 写入行数（空输入短路 0，不触库）。
        """
        if not events:
            return 0
        rows = build_event_rows(events, data_source=data_source)
        client = self._ensure_client()
        sql = f"INSERT INTO {self._table} {_insert_columns()} VALUES"
        for i in range(0, len(rows), chunk_size):
            client.execute(sql, rows[i : i + chunk_size])
        log.info("图形事件写入 %s: %d 行（data_source=%s）", self._table, len(rows), data_source)
        return len(rows)

    def query_events(
        self,
        *,
        pattern_id: str | None = None,
        symbol: str | None = None,
        timeframe: str | None = None,
        pattern_class: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100_000,
    ) -> list[dict[str, Any]]:
        """事件查询（等值过滤 + anchor_trade_date 闭区间，confirmed_at 升序）。

        Returns: dict 行列表（clickhouse-driver dict 模式）。
        """
        client = self._ensure_client()
        where: list[str] = []
        params: dict[str, Any] = {"limit": int(limit)}
        if pattern_id:
            where.append("pattern_id = %(pattern_id)s")
            params["pattern_id"] = pattern_id
        if symbol:
            where.append("symbol = %(symbol)s")
            params["symbol"] = str(symbol).split(".")[0]
        if timeframe:
            where.append("timeframe = %(timeframe)s")
            params["timeframe"] = timeframe
        if pattern_class:
            where.append("pattern_class = %(pattern_class)s")
            params["pattern_class"] = pattern_class
        if start_date:
            where.append("anchor_trade_date >= %(start_date)s")
            params["start_date"] = _coerce_date(start_date)
        if end_date:
            where.append("anchor_trade_date <= %(end_date)s")
            params["end_date"] = _coerce_date(end_date)
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        sql = (
            f"SELECT * FROM {self._table}{where_sql} "
            f"ORDER BY confirmed_at ASC LIMIT %(limit)s"
        )
        return client.execute(sql, params, with_column_types=False)


__all__ = [
    "PatternEventStore",
    "build_event_rows",
    "make_event_id",
]
