# [A_test] module_id: SRC-TST-1016 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_feedback_collector
# [INVARIANTS] FeedbackEntry.score in [1,5]; FeedbackCollector.add returns FeedbackEntry; summarize returns FeedbackSummary
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import json
from datetime import datetime
from pathlib import Path

import pytest

from zephyr.feedback_loop.feedback_collector import (
    FeedbackCollector,
    FeedbackEntry,
)


class TestFeedbackEntryInstantiation:
    def test_valid_entry(self):
        entry = FeedbackEntry(
            entry_id="FB-0001",
            task_id="T-001",
            score=4,
            comment="good",
            tags=["fast"],
            created_at=datetime.now(),
        )
        assert entry.entry_id == "FB-0001"
        assert entry.score == 4

    def test_deduplicates_tags(self):
        entry = FeedbackEntry(
            entry_id="FB-0002",
            task_id="T-001",
            score=3,
            tags=["slow", "slow", "accurate"],
            created_at=datetime.now(),
        )
        assert entry.tags == ["slow", "accurate"]

    def test_empty_tags(self):
        entry = FeedbackEntry(
            entry_id="FB-0003",
            task_id="T-001",
            score=5,
            created_at=datetime.now(),
        )
        assert entry.tags == []


class TestFeedbackEntryValidation:
    def test_score_below_range_raises(self):
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="FB-0004",
                task_id="T-001",
                score=0,
                created_at=datetime.now(),
            )

    def test_score_above_range_raises(self):
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="FB-0005",
                task_id="T-001",
                score=6,
                created_at=datetime.now(),
            )

    def test_empty_entry_id_raises(self):
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="",
                task_id="T-001",
                score=3,
                created_at=datetime.now(),
            )

    def test_empty_task_id_raises(self):
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="FB-0006",
                task_id="",
                score=3,
                created_at=datetime.now(),
            )


class TestFeedbackCollectorInstantiation:
    def test_default_init(self):
        fc = FeedbackCollector()
        assert fc.entry_count == 0
        assert fc.store_path is None

    def test_init_with_path(self):
        path = Path("/tmp/test_feedback.json")
        fc = FeedbackCollector(store_path=path)
        assert fc.store_path == path


class TestFeedbackCollectorAdd:
    def test_add_returns_entry(self):
        fc = FeedbackCollector()
        entry = fc.add(task_id="T-001", score=4)
        assert isinstance(entry, FeedbackEntry)
        assert entry.task_id == "T-001"
        assert entry.score == 4

    def test_add_increments_count(self):
        fc = FeedbackCollector()
        fc.add(task_id="T-001", score=4)
        fc.add(task_id="T-002", score=3)
        assert fc.entry_count == 2

    def test_add_with_comment_and_tags(self):
        fc = FeedbackCollector()
        entry = fc.add(task_id="T-001", score=5, comment="excellent", tags=["fast", "accurate"])
        assert entry.comment == "excellent"
        assert entry.tags == ["fast", "accurate"]

    def test_add_auto_increments_id(self):
        fc = FeedbackCollector()
        e1 = fc.add(task_id="T-001", score=4)
        e2 = fc.add(task_id="T-002", score=3)
        assert e1.entry_id == "FB-0001"
        assert e2.entry_id == "FB-0002"

    def test_add_with_custom_created_at(self):
        fc = FeedbackCollector()
        dt = datetime(2026, 1, 1, 12, 0, 0)
        entry = fc.add(task_id="T-001", score=4, created_at=dt)
        assert entry.created_at == dt


class TestFeedbackCollectorGetEntries:
    def test_get_all_entries(self):
        fc = FeedbackCollector()
        fc.add(task_id="T-001", score=4)
        fc.add(task_id="T-002", score=3)
        entries = fc.get_entries()
        assert len(entries) == 2

    def test_get_entries_by_task_id(self):
        fc = FeedbackCollector()
        fc.add(task_id="T-001", score=4)
        fc.add(task_id="T-002", score=3)
        fc.add(task_id="T-001", score=5)
        entries = fc.get_entries(task_id="T-001")
        assert len(entries) == 2

    def test_get_entries_nonexistent_task(self):
        fc = FeedbackCollector()
        fc.add(task_id="T-001", score=4)
        entries = fc.get_entries(task_id="T-999")
        assert entries == []


class TestFeedbackCollectorSummarize:
    def test_summarize_with_entries(self):
        fc = FeedbackCollector()
        fc.add(task_id="T-001", score=4, tags=["fast"])
        fc.add(task_id="T-001", score=2, tags=["slow"], comment="bad")
        summary = fc.summarize("T-001")
        assert summary.count == 2
        assert summary.average_score == 3.0
        assert summary.latest_comment == "bad"
        assert summary.tag_frequencies == {"fast": 1, "slow": 1}

    def test_summarize_no_entries(self):
        fc = FeedbackCollector()
        summary = fc.summarize("T-999")
        assert summary.count == 0
        assert summary.average_score == 0.0
        assert summary.tag_frequencies == {}


class TestFeedbackCollectorFlush:
    def test_flush_without_path_returns_zero(self):
        fc = FeedbackCollector()
        fc.add(task_id="T-001", score=4)
        assert fc.flush() == 0

    def test_flush_with_path(self, tmp_path):
        path = tmp_path / "feedback.json"
        fc = FeedbackCollector(store_path=path)
        fc.add(task_id="T-001", score=4)
        count = fc.flush()
        assert count == 1
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 1


class TestFeedbackCollectorLoad:
    def test_load_without_path_returns_zero(self):
        fc = FeedbackCollector()
        assert fc.load() == 0

    def test_load_nonexistent_file_returns_zero(self):
        fc = FeedbackCollector(store_path=Path("/nonexistent/path.json"))
        assert fc.load() == 0

    def test_flush_and_load_roundtrip(self, tmp_path):
        path = tmp_path / "feedback.json"
        fc = FeedbackCollector(store_path=path)
        fc.add(task_id="T-001", score=4, tags=["fast"])
        fc.flush()

        fc2 = FeedbackCollector(store_path=path)
        loaded = fc2.load()
        assert loaded == 1
        assert fc2.entry_count == 1


class TestFeedbackCollectorClear:
    def test_clear_returns_count(self):
        fc = FeedbackCollector()
        fc.add(task_id="T-001", score=4)
        fc.add(task_id="T-002", score=3)
        count = fc.clear()
        assert count == 2
        assert fc.entry_count == 0

    def test_clear_empty(self):
        fc = FeedbackCollector()
        count = fc.clear()
        assert count == 0
