# [A_test] module_id: SRC-TST-1120 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_indexer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_indexer.py -q
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.gov_audit.indexer import AuditIndexer, IndexResult


def _make_event(
    entry_id: str = "E001",
    event_type: str = "file_write",
    timestamp: str = "2026-01-01T00:00:00Z",
    lamport: int = 1,
    agent_id: str = "agent-1",
    session_id: str = "sess-1",
    target_path: str = "/tmp/test.py",
    operation: str = "write",
    status: str = "ok",
    provenance: str = "direct_agent",
    entry_hash: str = "aabbccdd",
    prev_entry_hash: str = "",
    merkle_batch_id: str = "batch-1",
) -> dict:
    return {
        "entry_id": entry_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "lamport": lamport,
        "agent_id": agent_id,
        "session_id": session_id,
        "target_path": target_path,
        "operation": operation,
        "status": status,
        "provenance": provenance,
        "entry_hash": entry_hash,
        "prev_entry_hash": prev_entry_hash,
        "merkle_batch_id": merkle_batch_id,
    }


def _write_events(path: Path, events: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in events),
        encoding="utf-8",
    )


class TestIndexResult:
    def test_default_values(self):
        result = IndexResult()
        assert result.status == ""
        assert result.events_scanned == 0
        assert result.events_indexed == 0
        assert result.new_entries == 0
        assert result.errors == []

    def test_custom_values(self):
        result = IndexResult(
            status="ok",
            events_scanned=10,
            events_indexed=8,
            new_entries=3,
            errors=["err1"],
        )
        assert result.status == "ok"
        assert result.events_scanned == 10
        assert result.events_indexed == 8
        assert result.new_entries == 3
        assert result.errors == ["err1"]

    def test_is_pydantic_model(self):
        result = IndexResult(status="no_data")
        dumped = result.model_dump()
        assert isinstance(dumped, dict)
        assert dumped["status"] == "no_data"


class TestAuditIndexerInit:
    def test_custom_paths(self, tmp_path):
        db_path = tmp_path / "custom.db"
        events_path = tmp_path / "custom.jsonl"
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        assert indexer._db_path == db_path
        assert indexer._events_path == events_path

    def test_string_paths_accepted(self, tmp_path):
        db_path = str(tmp_path / "str.db")
        events_path = str(tmp_path / "str.jsonl")
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        assert isinstance(indexer._db_path, Path)
        assert isinstance(indexer._events_path, Path)


class TestRebuild:
    def test_no_events_file_returns_no_data(self, tmp_path):
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=tmp_path / "nonexistent.jsonl",
        )
        result = indexer.rebuild()
        assert isinstance(result, IndexResult)
        assert result.status == "no_data"
        assert result.events_scanned == 0
        assert result.events_indexed == 0
        assert result.new_entries == 0

    def test_empty_events_file_returns_no_data(self, tmp_path):
        events_path = tmp_path / "empty.jsonl"
        events_path.write_text("", encoding="utf-8")
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "no_data"
        assert result.events_scanned == 0

    def test_single_event_indexed(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        _write_events(events_path, [_make_event()])
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "ok"
        assert result.events_scanned == 1
        assert result.events_indexed == 1
        assert result.new_entries == 1

    def test_multiple_events_indexed(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        events = [
            _make_event(entry_id="E001", agent_id="agent-1", event_type="file_write"),
            _make_event(entry_id="E002", agent_id="agent-2", event_type="file_read"),
            _make_event(entry_id="E003", agent_id="agent-1", event_type="file_write"),
        ]
        _write_events(events_path, events)
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "ok"
        assert result.events_scanned == 3
        assert result.events_indexed == 3
        assert result.new_entries == 3

    def test_rebuild_second_time_no_new_entries(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        _write_events(events_path, [_make_event()])
        db_path = tmp_path / "test.db"
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        first = indexer.rebuild()
        assert first.new_entries == 1
        assert first.status == "ok"
        second = indexer.rebuild()
        assert second.events_scanned == 1
        assert second.new_entries == 0

    def test_event_missing_entry_id_records_error(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        bad_event = {"event_type": "test", "timestamp": "2026-01-01"}
        events_path.write_text(json.dumps(bad_event), encoding="utf-8")
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "ok"
        assert len(result.errors) >= 1

    def test_creates_db_file_on_rebuild(self, tmp_path):
        db_path = tmp_path / "subdir" / "test.db"
        events_path = tmp_path / "events.jsonl"
        _write_events(events_path, [_make_event()])
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        indexer.rebuild()
        assert db_path.exists()

    def test_mixed_valid_and_invalid_events(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        valid = _make_event(entry_id="E001")
        invalid = {"event_type": "orphan", "timestamp": "2026-01-01"}
        events_path.write_text(
            json.dumps(valid) + "\n" + json.dumps(invalid),
            encoding="utf-8",
        )
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.events_scanned == 2
        assert result.events_indexed == 1
        assert len(result.errors) >= 1


class TestQueryStats:
    def test_no_db_returns_empty(self, tmp_path):
        indexer = AuditIndexer(
            db_path=tmp_path / "missing.db",
            events_path=tmp_path / "missing.jsonl",
        )
        stats = indexer.query_stats()
        assert stats["total"] == 0
        assert stats["by_event_type"] == {}
        assert stats["by_agent"] == {}

    def test_stats_after_rebuild_single_event(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        _write_events(events_path, [_make_event(event_type="file_write", agent_id="agent-1")])
        db_path = tmp_path / "test.db"
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        indexer.rebuild()
        stats = indexer.query_stats()
        assert stats["total"] == 1
        assert "file_write" in stats["by_event_type"]
        assert stats["by_event_type"]["file_write"] == 1
        assert "agent-1" in stats["by_agent"]

    def test_stats_after_rebuild_multiple_agents_and_types(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        events = [
            _make_event(entry_id="E001", event_type="file_write", agent_id="agent-1"),
            _make_event(entry_id="E002", event_type="file_read", agent_id="agent-2"),
            _make_event(entry_id="E003", event_type="file_write", agent_id="agent-1"),
        ]
        _write_events(events_path, events)
        db_path = tmp_path / "test.db"
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        indexer.rebuild()
        stats = indexer.query_stats()
        assert stats["total"] == 3
        assert stats["by_event_type"]["file_write"] == 2
        assert stats["by_event_type"]["file_read"] == 1
        assert stats["by_agent"]["agent-1"] == 2
        assert stats["by_agent"]["agent-2"] == 1

    def test_stats_reflects_rebuild_update(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        _write_events(events_path, [_make_event(entry_id="E001")])
        db_path = tmp_path / "test.db"
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        indexer.rebuild()
        assert indexer.query_stats()["total"] == 1
        new_events = [_make_event(entry_id="E001"), _make_event(entry_id="E002")]
        _write_events(events_path, new_events)
        indexer.rebuild()
        assert indexer.query_stats()["total"] == 2


class TestBoundaryConditions:
    def test_events_with_blank_lines(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        event_json = json.dumps(_make_event())
        events_path.write_text(
            "\n\n" + event_json + "\n\n",
            encoding="utf-8",
        )
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "ok"
        assert result.events_scanned == 1

    def test_large_batch_events(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        events = [_make_event(entry_id=f"E{i:04d}", lamport=i) for i in range(200)]
        _write_events(events_path, events)
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "ok"
        assert result.events_scanned == 200
        assert result.events_indexed == 200
        assert result.new_entries == 200
        stats = indexer.query_stats()
        assert stats["total"] == 200

    def test_special_characters_in_fields(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        event = _make_event(
            entry_id="E-SPECIAL",
            agent_id="agent-日本語",
            target_path="C:\\Users\\测试\\file.py",
        )
        _write_events(events_path, [event])
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "ok"
        stats = indexer.query_stats()
        assert "agent-日本語" in stats["by_agent"]
