# [A_test] module_id: MOD-GOV_night_shift_queue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_night_shift_queue
# [INVARIANTS] NightShiftQueue持久化路径使用tmp_path;测试间不共享状态
# [MODIFY-GUARD] src/zephyr/runtime/night_shift_queue.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] NightShiftQueue.append返回str;pending返回list;resolve返回bool;stats返回dict
# [TESTS] tests/test_night_shift_queue.py
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.trading.night_shift_queue import NightShiftEntry, NightShiftQueue


class TestNightShiftEntry:
    def test_default_values(self):
        entry = NightShiftEntry()
        assert entry.id == ""
        assert entry.task_id == ""
        assert entry.auto_decision == "C"
        assert entry.requires_human is True
        assert entry.human_decision is None
        assert entry.options == []

    def test_custom_values(self):
        entry = NightShiftEntry(
            id="NSL-0001",
            task_id="T-001",
            module="test_mod",
            context="test context",
            auto_decision="A",
            requires_human=False,
            human_decision="approve",
        )
        assert entry.id == "NSL-0001"
        assert entry.task_id == "T-001"
        assert entry.module == "test_mod"
        assert entry.auto_decision == "A"
        assert entry.requires_human is False
        assert entry.human_decision == "approve"

    def test_serialization_roundtrip(self):
        entry = NightShiftEntry(id="NSL-0042", task_id="T-042", module="m1")
        data = json.loads(entry.model_dump_json())
        restored = NightShiftEntry(**data)
        assert restored.id == entry.id
        assert restored.task_id == entry.task_id
        assert restored.module == entry.module


class TestNightShiftQueue:
    def test_append_assigns_id(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        entry = NightShiftEntry(task_id="T-1", module="mod_a")
        eid = q.append(entry)
        assert eid.startswith("NSL-")
        assert entry.id == eid

    def test_append_preserves_existing_id(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        entry = NightShiftEntry(id="CUSTOM-1", task_id="T-1")
        eid = q.append(entry)
        assert eid == "CUSTOM-1"

    def test_pending_returns_unresolved(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        q.append(NightShiftEntry(task_id="T-1"))
        q.append(NightShiftEntry(task_id="T-2"))
        pending = q.pending()
        assert len(pending) == 2
        for p in pending:
            assert p.human_decision is None

    def test_pending_empty_when_no_file(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nonexistent.jsonl")
        assert q.pending() == []

    def test_resolve_marks_entry(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        eid = q.append(NightShiftEntry(task_id="T-1"))
        found = q.resolve(eid, "approve", "looks good")
        assert found is True
        pending = q.pending()
        assert len(pending) == 0

    def test_resolve_returns_false_for_missing(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        q.append(NightShiftEntry(task_id="T-1"))
        found = q.resolve("NONEXISTENT-ID", "approve")
        assert found is False

    def test_resolve_returns_false_when_no_file(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nonexistent.jsonl")
        assert q.resolve("any-id", "approve") is False

    def test_stats_empty(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        stats = q.stats()
        assert stats == {"total": 0, "pending": 0, "resolved": 0}

    def test_stats_after_append_and_resolve(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        e1 = q.append(NightShiftEntry(task_id="T-1"))
        q.append(NightShiftEntry(task_id="T-2"))
        stats = q.stats()
        assert stats["total"] == 2
        assert stats["pending"] == 2
        assert stats["resolved"] == 0
        q.resolve(e1, "reject")
        stats = q.stats()
        assert stats["pending"] == 1
        assert stats["resolved"] == 1

    def test_has_unresolved(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        assert q.has_unresolved() is False
        eid = q.append(NightShiftEntry(task_id="T-1"))
        assert q.has_unresolved() is True
        q.resolve(eid, "approve")
        assert q.has_unresolved() is False

    def test_counter_increments_across_appends(self, tmp_path: Path):
        q = NightShiftQueue(tmp_path / "nsq.jsonl")
        e1 = q.append(NightShiftEntry(task_id="T-1"))
        e2 = q.append(NightShiftEntry(task_id="T-2"))
        e3 = q.append(NightShiftEntry(task_id="T-3"))
        assert e1 == "NSL-0001"
        assert e2 == "NSL-0002"
        assert e3 == "NSL-0003"

    def test_counter_resumes_from_existing_file(self, tmp_path: Path):
        path = tmp_path / "nsq.jsonl"
        q1 = NightShiftQueue(path)
        q1.append(NightShiftEntry(task_id="T-1"))
        q1.append(NightShiftEntry(task_id="T-2"))
        q2 = NightShiftQueue(path)
        eid = q2.append(NightShiftEntry(task_id="T-3"))
        assert eid == "NSL-0003"

    def test_corrupted_line_skipped(self, tmp_path: Path):
        path = tmp_path / "nsq.jsonl"
        path.write_text("not-json\n", encoding="utf-8")
        q = NightShiftQueue(path)
        q.append(NightShiftEntry(task_id="T-1"))
        pending = q.pending()
        assert len(pending) == 1
        stats = q.stats()
        assert stats["total"] == 1
