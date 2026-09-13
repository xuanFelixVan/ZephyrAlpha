# [BLUEPRINT] MOD-SIG-145 | tests/signal_ashare/test_pattern_event_store.py
# [MODULE] tests.signal_ashare.test_pattern_event_store
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_event_store
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 测试隔离：注入 fake client，禁触生产 CH/生产路径（tmp_path 不需要——不落盘）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/signal_ashare/test_pattern_event_store.py
# [TTL] permanent
"""pattern_event_store 单测（W1）——行契约/确定性事件ID/读写 SQL 对齐/封闭集校验。"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from zephyr.signal_ashare.strategy_signal.pattern_event_store import (
    PatternEventStore,
    build_event_rows,
    make_event_id,
)

_BASE_EVENT = {
    "pattern_id": "双顶@day",
    "pattern_class": "反转",
    "direction": "向下",
    "confidence": 0.8,
    "timeframe": "day",
    "symbol": "600519",
    "anchor_trade_date": "2026-09-10",
    "confirmed_at": "2026-09-10T15:00:00+00:00",
    "name": "双顶",
    "key_points": [{"idx": 10, "price": 1800.0, "role": "顶1"}],
    "regime_tag": "risk_off",
    "scan_run_id": "scan-20260914-001",
}


class _FakeClient:
    """捕获 execute 调用的假 client（测试不触库）。"""

    def __init__(self):
        self.calls: list[tuple[str, object]] = []
        self.rows: list[dict] = []

    def execute(self, sql, params=None, with_column_types=True):
        self.calls.append((sql, params))
        return self.rows


def _schema_columns() -> list[str]:
    from schemas.categories.market_pattern_event import INSERT_COLUMNS

    body = INSERT_COLUMNS.strip().strip("()")
    return [c.strip() for c in body.split(",")]


# ── 确定性事件 ID ──────────────────────────────────────────────


def test_make_event_id_deterministic_and_sensitive():
    kw = dict(
        pattern_id="双顶@day",
        timeframe="day",
        symbol="600519",
        anchor_trade_date="2026-09-10",
        confirmed_at="2026-09-10T15:00:00+00:00",
        name="双顶",
    )
    a = make_event_id(**kw)
    b = make_event_id(**kw)
    assert a == b  # 重放幂等：同事件同 ID
    assert 0 <= a < 2**64
    changed = dict(kw, confirmed_at="2026-09-11T15:00:00+00:00")
    assert make_event_id(**changed) != a  # 确认时刻不同→不同 ID


# ── 行契约 ────────────────────────────────────────────────────


def test_build_event_rows_aligns_schema_columns():
    rows = build_event_rows([dict(_BASE_EVENT)], data_source="pattern_backfill")
    assert len(rows) == 1
    assert len(rows[0]) == len(_schema_columns())
    row = rows[0]
    assert row[0] == make_event_id(**{k: _BASE_EVENT[k] for k in (
        "pattern_id", "timeframe", "symbol", "anchor_trade_date", "confirmed_at", "name")})
    assert row[1] == "双顶@day"
    assert row[2] == "反转"
    assert row[3] == "向下"
    assert row[4] == 0.8
    assert row[6] == "600519"  # 纯数字口径（后缀剥离）
    assert row[7] == date(2026, 9, 10)  # Date 列=date 对象
    assert isinstance(row[8], datetime)  # DateTime64 列=datetime 对象
    assert '"顶1"' in row[10]  # key_points 已转 JSON


def test_build_event_rows_accepts_typed_dates_and_clips_confidence():
    ev = dict(
        _BASE_EVENT,
        anchor_trade_date=date(2026, 9, 10),
        confirmed_at=datetime(2026, 9, 10, 15, 0, 0),
        confidence=1.7,  # 出界裁剪
    )
    rows = build_event_rows([ev], data_source="unified_pattern_engine")
    assert rows[0][7] == date(2026, 9, 10)
    assert rows[0][4] == 1.0


def test_build_event_rows_rejects_missing_and_bad_enum():
    bad = {k: v for k, v in _BASE_EVENT.items() if k != "confirmed_at"}
    with pytest.raises(ValueError, match="缺必需字段"):
        build_event_rows([bad], data_source="x")
    with pytest.raises(ValueError, match="direction 非法"):
        build_event_rows([dict(_BASE_EVENT, direction="看涨")], data_source="x")
    with pytest.raises(ValueError, match="pattern_class 非法"):
        build_event_rows([dict(_BASE_EVENT, pattern_class="head_shoulders")], data_source="x")
    with pytest.raises(ValueError, match="data_source"):
        build_event_rows([dict(_BASE_EVENT)], data_source="")


def test_build_event_rows_same_event_same_id_across_runs():
    r1 = build_event_rows([dict(_BASE_EVENT)], data_source="pattern_backfill")
    r2 = build_event_rows([dict(_BASE_EVENT)], data_source="pattern_event_incremental")
    assert r1[0][0] == r2[0][0]  # 跨 scan_run/data_source 重扫→同 event_id→引擎去重


# ── Store 读写 SQL 对齐 ───────────────────────────────────────


def test_store_insert_uses_schema_columns_and_chunks():
    fake = _FakeClient()
    store = PatternEventStore(client=fake)
    events = [dict(_BASE_EVENT, symbol=f"{i:06d}") for i in range(7)]
    n = store.insert_events(events, data_source="pattern_backfill", chunk_size=3)
    assert n == 7
    assert [len(c[1]) for c in fake.calls] == [3, 3, 1]  # 分块
    sql = fake.calls[0][0]
    from schemas.categories.market_pattern_event import INSERT_COLUMNS

    assert sql == f"INSERT INTO c1_market.market_pattern_event {INSERT_COLUMNS} VALUES"


def test_store_insert_empty_short_circuits():
    fake = _FakeClient()
    store = PatternEventStore(client=fake)
    assert store.insert_events([], data_source="x") == 0
    assert fake.calls == []


def test_store_query_builds_filters():
    fake = _FakeClient()
    fake.rows = []
    store = PatternEventStore(client=fake)
    store.query_events(
        pattern_id="双顶@day",
        symbol="600519.SH",
        timeframe="day",
        start_date="2026-09-01",
        end_date="2026-09-10",
        limit=50,
    )
    sql, params = fake.calls[0]
    assert "pattern_id = %(pattern_id)s" in sql
    assert "symbol = %(symbol)s" in sql
    assert params["symbol"] == "600519"  # 后缀剥离
    assert params["start_date"] == date(2026, 9, 1)
    assert params["limit"] == 50
    assert "ORDER BY confirmed_at ASC" in sql


def test_store_without_client_raises_runtime_error(monkeypatch):
    import zephyr.signal_ashare.strategy_signal.pattern_event_store as mod

    monkeypatch.setattr(mod, "_get_ch_client", lambda: None)
    store = PatternEventStore(client=None)
    with pytest.raises(RuntimeError, match="clickhouse-driver"):
        store.query_events(pattern_id="x")
    with pytest.raises(RuntimeError, match="clickhouse-driver"):
        store.insert_events([dict(_BASE_EVENT)], data_source="x")
