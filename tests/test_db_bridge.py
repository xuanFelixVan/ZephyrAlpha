# [A_test] module_id: SRC-TST-0704 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] tests.test_db_bridge

# [INVARIANTS] tests must not modify production database; all DB ops use tmp_path

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] all tests must pass with exit 0

# [TESTS] python -m pytest tests/test_db_bridge.py -q

"""Tests for zephyr.observability.feedback_loop.db_bridge — record_via_db_contract and bulk_record_via_db_contract."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from zephyr.ops.db_bridge import (
    FLE_METRICS_TABLE_DDL,
    _ensure_table,
    bulk_record_via_db_contract,
    record_via_db_contract,
)


def _make_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test_fle.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(FLE_METRICS_TABLE_DDL)
    conn.close()
    return db_path


def _count_rows(db_path: Path) -> int:
    conn = sqlite3.connect(str(db_path))
    row = conn.execute("SELECT COUNT(*) FROM fle_metrics").fetchone()
    conn.close()
    return row[0]


def _fetch_all(db_path: Path) -> list[dict[str, Any]]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM fle_metrics ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


class TestEnsureTable:
    def test_creates_table_idempotent(self, tmp_path: Path) -> None:
        db_path = tmp_path / "idem.db"
        conn = sqlite3.connect(str(db_path))
        _ensure_table(conn)
        _ensure_table(conn)
        conn.execute(
            "INSERT INTO fle_metrics (metric_type, metric_name, metric_value, recorded_at) "
            "VALUES (?, ?, ?, datetime('now'))",
            ("latency", "p99", 1.23),
        )
        conn.commit()
        assert _count_rows(db_path) == 1
        conn.close()

    def test_creates_indexes(self, tmp_path: Path) -> None:
        db_path = tmp_path / "idx.db"
        conn = sqlite3.connect(str(db_path))
        _ensure_table(conn)
        indexes = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='fle_metrics'"
        ).fetchall()
        index_names = {r[0] for r in indexes}
        assert "idx_fle_metrics_type" in index_names
        assert "idx_fle_metrics_at" in index_names
        assert "idx_fle_metrics_session" in index_names
        conn.close()


class TestRecordViaDbContract:
    def test_single_insert_returns_rowid(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        rowid = record_via_db_contract(
            "latency",
            "p99",
            1.23,
            tags=["env:prod"],
            session_id="sess-001",
            task_id="task-001",
            cost_usd=0.05,
            token_count=120,
            db_path=str(db_path),
        )
        assert rowid >= 1
        assert _count_rows(db_path) == 1

    def test_inserted_data_matches_input(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        record_via_db_contract(
            "cost",
            "total",
            9.99,
            tags=["layer:infra"],
            session_id="sess-002",
            task_id="task-002",
            cost_usd=9.99,
            token_count=500,
            db_path=str(db_path),
        )
        rows = _fetch_all(db_path)
        assert len(rows) == 1
        r = rows[0]
        assert r["metric_type"] == "cost"
        assert r["metric_name"] == "total"
        assert abs(r["metric_value"] - 9.99) < 1e-9
        assert json.loads(r["tags"]) == ["layer:infra"]
        assert r["session_id"] == "sess-002"
        assert r["task_id"] == "task-002"
        assert abs(r["cost_usd"] - 9.99) < 1e-9
        assert r["token_count"] == 500

    def test_default_optional_fields(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        rowid = record_via_db_contract("count", "events", 42.0, db_path=str(db_path))
        assert rowid >= 1
        rows = _fetch_all(db_path)
        r = rows[0]
        assert json.loads(r["tags"]) == []
        assert r["session_id"] == ""
        assert r["task_id"] == ""
        assert r["cost_usd"] == 0.0
        assert r["token_count"] == 0

    def test_tags_none_treated_as_empty_list(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        record_via_db_contract("gauge", "heap", 3.14, tags=None, db_path=str(db_path))
        rows = _fetch_all(db_path)
        assert json.loads(rows[0]["tags"]) == []

    def test_negative_metric_value(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        rowid = record_via_db_contract("delta", "change", -5.5, db_path=str(db_path))
        assert rowid >= 1
        rows = _fetch_all(db_path)
        assert abs(rows[0]["metric_value"] - (-5.5)) < 1e-9

    def test_zero_metric_value(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        rowid = record_via_db_contract("counter", "zero", 0.0, db_path=str(db_path))
        assert rowid >= 1
        rows = _fetch_all(db_path)
        assert rows[0]["metric_value"] == 0.0

    def test_invalid_db_path_raises(self, tmp_path: Path) -> None:
        with pytest.raises(sqlite3.OperationalError):
            record_via_db_contract("x", "y", 1.0, db_path=str(tmp_path / "nonexistent" / "deep" / "bad.db"))


class TestBulkRecordViaDbContract:
    def test_bulk_insert_count(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        records = [
            {"metric_type": "latency", "metric_name": "p50", "metric_value": 0.5},
            {"metric_type": "latency", "metric_name": "p99", "metric_value": 2.0},
            {"metric_type": "cost", "metric_name": "total", "metric_value": 3.5},
        ]
        count = bulk_record_via_db_contract(records, db_path=str(db_path))
        assert count == 3
        assert _count_rows(db_path) == 3

    def test_bulk_inserted_data(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        records = [
            {
                "metric_type": "tokens",
                "metric_name": "input",
                "metric_value": 100.0,
                "tags": ["model:gpt4"],
                "session_id": "sess-b1",
                "task_id": "task-b1",
                "cost_usd": 1.0,
                "token_count": 100,
            },
        ]
        bulk_record_via_db_contract(records, db_path=str(db_path))
        rows = _fetch_all(db_path)
        r = rows[0]
        assert r["metric_type"] == "tokens"
        assert r["metric_name"] == "input"
        assert abs(r["metric_value"] - 100.0) < 1e-9
        assert json.loads(r["tags"]) == ["model:gpt4"]
        assert r["session_id"] == "sess-b1"
        assert r["cost_usd"] == 1.0
        assert r["token_count"] == 100

    def test_empty_list_returns_zero(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        count = bulk_record_via_db_contract([], db_path=str(db_path))
        assert count == 0
        assert _count_rows(db_path) == 0

    def test_missing_fields_use_defaults(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        records = [{"metric_type": "partial", "metric_name": "sparse"}]
        bulk_record_via_db_contract(records, db_path=str(db_path))
        rows = _fetch_all(db_path)
        r = rows[0]
        assert r["metric_value"] == 0.0
        assert json.loads(r["tags"]) == []
        assert r["session_id"] == ""
        assert r["task_id"] == ""
        assert r["cost_usd"] == 0.0
        assert r["token_count"] == 0

    def test_invalid_db_path_raises(self, tmp_path: Path) -> None:
        records = [{"metric_type": "x", "metric_name": "y", "metric_value": 1.0}]
        with pytest.raises(sqlite3.OperationalError):
            bulk_record_via_db_contract(records, db_path=str(tmp_path / "nope" / "bad.db"))

    def test_large_bulk_insert(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        records = [{"metric_type": "bulk", "metric_name": f"item_{i}", "metric_value": float(i)} for i in range(50)]
        count = bulk_record_via_db_contract(records, db_path=str(db_path))
        assert count == 50
        assert _count_rows(db_path) == 50


class TestDbBridgeEdgeCases:
    def test_record_with_empty_strings(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        rowid = record_via_db_contract("", "", 0.0, tags=[], session_id="", task_id="", db_path=str(db_path))
        assert rowid >= 1
        rows = _fetch_all(db_path)
        assert rows[0]["metric_type"] == ""
        assert rows[0]["metric_name"] == ""

    def test_record_with_unicode_tags(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        tags = ["环境:生产", "层:基础设施"]
        record_via_db_contract("unicode", "test", 1.0, tags=tags, db_path=str(db_path))
        rows = _fetch_all(db_path)
        assert json.loads(rows[0]["tags"]) == tags

    def test_bulk_with_mixed_completeness(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        records = [
            {
                "metric_type": "full",
                "metric_name": "complete",
                "metric_value": 10.0,
                "tags": ["a"],
                "session_id": "s1",
                "task_id": "t1",
                "cost_usd": 2.0,
                "token_count": 50,
            },
            {"metric_type": "minimal", "metric_name": "partial", "metric_value": 5.0},
        ]
        count = bulk_record_via_db_contract(records, db_path=str(db_path))
        assert count == 2
        rows = _fetch_all(db_path)
        assert rows[0]["session_id"] == "s1"
        assert rows[1]["session_id"] == ""

    def test_record_very_large_metric_value(self, tmp_path: Path) -> None:
        db_path = _make_db(tmp_path)
        large_val = 1e15
        record_via_db_contract("big", "huge", large_val, db_path=str(db_path))
        rows = _fetch_all(db_path)
        assert abs(rows[0]["metric_value"] - large_val) < large_val * 1e-9
