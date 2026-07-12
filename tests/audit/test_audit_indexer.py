# [A_test] module_id: SRC-TST-0355 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_indexer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json

from zephyr.gov_audit.indexer import AuditIndexer, IndexResult


class TestAuditIndexerInit:
    def test_default_paths(self):
        indexer = AuditIndexer()
        assert indexer._db_path.name == "audit_index.db"
        assert indexer._events_path.name == "events.jsonl"

    def test_custom_paths(self, tmp_path):
        db = tmp_path / "custom.db"
        ev = tmp_path / "custom.jsonl"
        indexer = AuditIndexer(db_path=db, events_path=ev)
        assert indexer._db_path == db
        assert indexer._events_path == ev


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

    def test_empty_events_file(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        events_path.write_text("", encoding="utf-8")
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "no_data"

    def test_index_events(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        events = [
            {
                "entry_id": "E001",
                "event_type": "file_write",
                "timestamp": "2026-01-01T00:00:00Z",
                "lamport": 1,
                "agent_id": "agent-1",
                "session_id": "sess-1",
                "target_path": "/tmp/test.py",
                "operation": "write",
                "status": "ok",
                "provenance": "direct_agent",
                "entry_hash": "aabbccdd",
                "prev_entry_hash": "",
                "merkle_batch_id": "batch-1",
            },
        ]
        events_path.write_text(
            "\n".join(json.dumps(e) for e in events),
            encoding="utf-8",
        )
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert result.status == "ok"
        assert result.events_scanned == 1
        assert result.events_indexed == 1
        assert result.new_entries == 1

    def test_duplicate_entries_no_new(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        event = {
            "entry_id": "E001",
            "event_type": "file_write",
            "timestamp": "2026-01-01T00:00:00Z",
            "lamport": 1,
            "agent_id": "agent-1",
            "session_id": "sess-1",
            "entry_hash": "aabb",
        }
        events_path.write_text(json.dumps(event), encoding="utf-8")
        db_path = tmp_path / "test.db"
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        indexer.rebuild()
        result = indexer.rebuild()
        assert result.new_entries == 0

    def test_missing_entry_id_reports_error(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        events_path.write_text(
            json.dumps({"event_type": "test", "timestamp": "2026-01-01"}),
            encoding="utf-8",
        )
        indexer = AuditIndexer(
            db_path=tmp_path / "test.db",
            events_path=events_path,
        )
        result = indexer.rebuild()
        assert len(result.errors) > 0


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

    def test_stats_after_rebuild(self, tmp_path):
        events_path = tmp_path / "events.jsonl"
        events_path.write_text(
            json.dumps(
                {
                    "entry_id": "E001",
                    "event_type": "file_write",
                    "timestamp": "2026-01-01T00:00:00Z",
                    "lamport": 1,
                    "agent_id": "agent-1",
                    "session_id": "sess-1",
                    "entry_hash": "aa",
                }
            ),
            encoding="utf-8",
        )
        db_path = tmp_path / "test.db"
        indexer = AuditIndexer(db_path=db_path, events_path=events_path)
        indexer.rebuild()
        stats = indexer.query_stats()
        assert stats["total"] == 1
        assert "file_write" in stats["by_event_type"]
