"""test_usage_stats — C2 三源采集纯函数/口径护栏/DDL 断言/FakeConn 入库/PG opt-in。

测试隔离：采集输入=tmp_path 构造；入库=FakeConn 注入；PG 用例=ai_tools_test_objt
临时 schema（session 级清理），不可达=skip 而非假绿。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.ai_layer.tools import STAT_SOURCES
from zephyr.ai_layer.tools.usage_stats import (
    StatsError,
    ToolUsageStore,
    _check_schema_name,
    _ddl_statements,
    manual_row,
    rows_from_audit_jsonl,
    rows_from_failures_dir,
    rows_from_telemetry,
    verify,
)

AS_OF = datetime(2026, 9, 23, 12, 0, 0, tzinfo=UTC)   # as_of 注入（禁 datetime.now）
IN_WINDOW = "2026-09-10T08:00:00+00:00"
OUT_WINDOW = "2026-08-01T08:00:00+00:00"


class FakeConn:
    """最小连接桩：记录执行语句与参数（禁写生产路径，零 PG 依赖）。"""

    def __init__(self) -> None:
        self.executed: list[tuple[str, object]] = []

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)


class FakeCursor:
    def __init__(self, conn: FakeConn) -> None:
        self._conn = conn
        self.description = None

    def execute(self, sql: str, params: object = None) -> None:
        self._conn.executed.append((sql, params))

    def fetchall(self) -> list[object]:
        return []


# ---------------------------------------------------------------------------
# 源 1：audit_jsonl
# ---------------------------------------------------------------------------

def test_audit_jsonl_window_and_bad_line(tmp_path: Path) -> None:
    p = tmp_path / "gate_execution_stats.jsonl"
    rows = [
        {"timestamp": IN_WINDOW, "failed": ["GATE-A"]},
        {"timestamp": IN_WINDOW, "failed": ["GATE-A", "GATE-B"]},
        {"timestamp": OUT_WINDOW, "failed": ["GATE-C"]},   # 窗外不进
        {"timestamp": IN_WINDOW, "failed": "not-a-list"},  # failed 畸形=只记 run
        "not-json",                                        # 坏行跳过留痕
    ]
    p.write_text("\n".join(json.dumps(r) if isinstance(r, dict) else r for r in rows),
                 encoding="utf-8")
    out = rows_from_audit_jsonl(p, as_of=AS_OF)
    by_id = {r["tool_id"]: r for r in out}
    assert by_id["gate:GATE-A"]["usage_count"] == 3        # 窗内审计行数（含畸形 failed 行）
    assert by_id["gate:GATE-A"]["failure_count"] == 2
    assert abs(by_id["gate:GATE-A"]["failure_rate"] - 2 / 3) < 1e-9
    assert "gate:GATE-C" not in by_id                      # 窗外
    assert all(r["stat_source"] == "audit_jsonl" for r in out)


def test_audit_jsonl_missing_file_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(StatsError, match="缺文件"):
        rows_from_audit_jsonl(tmp_path / "nope.jsonl", as_of=AS_OF)


# ---------------------------------------------------------------------------
# 源 2：failures_dir（口径=alerter ERROR+ 落盘）
# ---------------------------------------------------------------------------

def test_failures_dir_level_gate_and_no_fake_rate(tmp_path: Path) -> None:
    d = tmp_path / "failures"
    d.mkdir()
    cases = {
        "a_in.json": {"task_id": "snap", "level": "ERROR", "timestamp": IN_WINDOW},
        "b_out.json": {"task_id": "snap", "level": "ERROR", "timestamp": OUT_WINDOW},
        "c_warn.json": {"task_id": "snap", "level": "WARNING", "timestamp": IN_WINDOW},
        "d_other.json": {"task_id": "other", "level": "CRITICAL", "timestamp": IN_WINDOW},
    }
    for name, rec in cases.items():
        (d / name).write_text(json.dumps(rec), encoding="utf-8")
    (d / "bad.json").write_text("{broken", encoding="utf-8")
    out = rows_from_failures_dir(d, as_of=AS_OF)
    by_id = {r["tool_id"]: r for r in out}
    assert by_id["task:snap"]["failure_count"] == 1        # 窗外+WARNING 不进
    assert by_id["task:other"]["failure_count"] == 1
    for r in out:
        assert r["usage_count"] is None and r["failure_rate"] is None  # 分母禁造（RULE-DATA-OPS）


def test_failures_dir_missing_dir_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(StatsError, match="不存在"):
        rows_from_failures_dir(tmp_path / "nope", as_of=AS_OF)


# ---------------------------------------------------------------------------
# 源 3：telemetry（注入）+ 源 4：manual_v0
# ---------------------------------------------------------------------------

def test_telemetry_injected_records() -> None:
    records = [
        {"tool_id": "mcp:task_manager", "timestamp": IN_WINDOW, "latency_s": 0.30},
        {"tool_id": "mcp:task_manager", "timestamp": IN_WINDOW, "latency_s": 0.10,
         "failed": False},
        {"tool_id": "mcp:task_manager", "timestamp": IN_WINDOW, "latency_s": 0.20,
         "failed": True},
        {"name": "builtin:WebSearch", "timestamp": IN_WINDOW},          # name 兜底
        {"tool_id": "mcp:x", "timestamp": OUT_WINDOW},                  # 窗外
        {"timestamp": IN_WINDOW},                                       # 缺 id 跳过
    ]
    out = rows_from_telemetry(records, as_of=AS_OF)
    by_id = {r["tool_id"]: r for r in out}
    tm = by_id["mcp:task_manager"]
    assert tm["usage_count"] == 3
    assert tm["latency_p50_s"] == 0.2                                   # p50
    assert tm["failure_rate"] == pytest.approx(1 / 3)
    ws = by_id["builtin:WebSearch"]
    assert ws["usage_count"] == 1 and ws["failure_rate"] is None        # 无 failed 字段=不造率


def test_manual_row_vocabulary_fallback() -> None:
    row = manual_row("script:git_commit", as_of=AS_OF)
    assert row["stat_source"] == "manual_v0"                            # 兜底词在档
    assert row["usage_count"] is None
    with pytest.raises(StatsError, match="tool_id"):
        manual_row("  ", as_of=AS_OF)


def test_stat_source_vocabulary_has_manual_v0() -> None:
    assert "manual_v0" in STAT_SOURCES


# ---------------------------------------------------------------------------
# schema 白名单 + DDL 断言 + FakeConn 入库
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("schema", ["bogus", "ai_intake", "ai_tools; DROP", ""])
def test_schema_whitelist_rejects(schema: str) -> None:
    with pytest.raises(ValueError, match="不合规"):
        _check_schema_name(schema)


@pytest.mark.parametrize("schema", ["ai_tools", "ai_tools_test_objt"])
def test_schema_whitelist_accepts(schema: str) -> None:
    assert _check_schema_name(schema) == schema


def test_ddl_tz_and_vocabulary() -> None:
    stmts = _ddl_statements("ai_tools")
    table = stmts[1]
    assert "TIMESTAMPTZ" in table                                       # RULE-SCHEMA-TZ
    for src in STAT_SOURCES:
        assert f"'{src}'" in table                                      # 词表同源渲染
    assert "IF NOT EXISTS" in stmts[0]                                  # 幂等


def test_store_upsert_via_fake_conn() -> None:
    conn = FakeConn()
    store = ToolUsageStore(schema="ai_tools_test_fake", service=object(), write_conn=conn)
    row = manual_row("script:git_commit", as_of=AS_OF)
    assert store.upsert([row]) == 1
    sql, params = conn.executed[0]
    assert "INSERT INTO ai_tools_test_fake.tool_usage_stats" in sql
    assert "ON CONFLICT" in sql                                        # 幂等 upsert
    assert params["tool_id"] == "script:git_commit"                    # type: ignore[union-attr]
    with pytest.raises(StatsError, match="词表外"):
        bad = dict(row, stat_source="made_up")
        store.upsert([bad])


def test_pg_opt_in_roundtrip(test_schema: str) -> None:
    """PG opt-in：真 DDL+真 upsert 幂等（临时 schema，session 级清理）。"""
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    ok, missing = verify(test_schema)
    assert ok and not missing
    store = ToolUsageStore(schema=test_schema)
    row = manual_row("script:test_only_tool", as_of=AS_OF)
    assert store.upsert([row]) == 1
    assert store.upsert([row]) == 1                                    # 同窗刷新不炸不重
    rows = store.list_tool("script:test_only_tool")
    assert len(rows) == 1 and rows[0]["stat_source"] == "manual_v0"
    conn = get_depgraph_pg_connection(read_only=True)
    try:
        conn.cursor().execute(f"SELECT 1 FROM {test_schema}.tool_usage_stats LIMIT 1")
    finally:
        conn.close()
