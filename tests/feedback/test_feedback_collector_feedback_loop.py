# [A_test] module_id: SRC-TST-1876 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-498 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.feedback_loop.test_feedback_collector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for feedback_collector.py (T-2-29, C54)
===================================================
Minimum: 10 tests
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from zephyr.feedback_loop.feedback_collector import (
    FeedbackCollector,
    FeedbackEntry,
)


class TestFeedbackEntry:
    def test_valid_entry(self) -> None:
        entry = FeedbackEntry(
            entry_id="FB-0001",
            task_id="T-2-29",
            score=4,
            comment="Good work",
            tags=["accurate"],
            created_at=datetime(2026, 4, 24, 12, 0, 0),
        )
        assert entry.score == 4
        assert entry.comment == "Good work"
        assert entry.tags == ["accurate"]

    def test_score_out_of_range_low(self) -> None:
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="FB-0001",
                task_id="T-2-29",
                score=0,
                created_at=datetime(2026, 4, 24),
            )

    def test_score_out_of_range_high(self) -> None:
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="FB-0001",
                task_id="T-2-29",
                score=6,
                created_at=datetime(2026, 4, 24),
            )

    def test_tags_deduplication(self) -> None:
        entry = FeedbackEntry(
            entry_id="FB-0001",
            task_id="T-2-29",
            score=3,
            tags=["slow", "slow", "accurate"],
            created_at=datetime(2026, 4, 24),
        )
        assert entry.tags == ["slow", "accurate"]

    def test_extra_field_forbidden(self) -> None:
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="FB-0001",
                task_id="T-2-29",
                score=3,
                created_at=datetime(2026, 4, 24),
                unknown_field="oops",
            )


class TestFeedbackCollector:
    def test_add_entry(self) -> None:
        collector = FeedbackCollector()
        entry = collector.add(task_id="T-2-29", score=5, comment="Excellent")
        assert entry.entry_id == "FB-0001"
        assert entry.score == 5
        assert collector.entry_count == 1

    def test_add_multiple_entries_auto_increment(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-2-29", score=4)
        collector.add(task_id="T-2-29", score=3)
        entries = collector.get_entries()
        assert entries[0].entry_id == "FB-0001"
        assert entries[1].entry_id == "FB-0002"

    def test_get_entries_filtered_by_task(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-2-29", score=5)
        collector.add(task_id="T-2-30", score=3)
        collector.add(task_id="T-2-29", score=4)
        filtered = collector.get_entries(task_id="T-2-29")
        assert len(filtered) == 2
        assert all(e.task_id == "T-2-29" for e in filtered)

    def test_get_entries_all(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-2-29", score=5)
        collector.add(task_id="T-2-30", score=3)
        assert len(collector.get_entries()) == 2

    def test_summarize_with_entries(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-2-29", score=5, comment="Great", tags=["fast"])
        collector.add(task_id="T-2-29", score=3, comment="OK", tags=["slow", "needs-review"])
        summary = collector.summarize("T-2-29")
        assert summary.count == 2
        assert summary.average_score == 4.0
        assert summary.latest_comment == "OK"
        assert summary.tag_frequencies == {"fast": 1, "slow": 1, "needs-review": 1}

    def test_summarize_no_entries(self) -> None:
        collector = FeedbackCollector()
        summary = collector.summarize("T-2-99")
        assert summary.count == 0
        assert summary.average_score == 0.0
        assert summary.tag_frequencies == {}

    def test_flush_to_file(self, tmp_path: Path) -> None:
        store = tmp_path / "feedback.json"
        collector = FeedbackCollector(store_path=store)
        collector.add(task_id="T-2-29", score=4, comment="Good")
        count = collector.flush()
        assert count == 1
        assert store.exists()
        data = json.loads(store.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["task_id"] == "T-2-29"

    def test_flush_no_store_path(self) -> None:
        collector = FeedbackCollector()
        assert collector.flush() == 0

    def test_load_from_file(self, tmp_path: Path) -> None:
        store = tmp_path / "feedback.json"
        collector1 = FeedbackCollector(store_path=store)
        collector1.add(task_id="T-2-29", score=5, tags=["accurate"])
        collector1.flush()

        collector2 = FeedbackCollector(store_path=store)
        loaded = collector2.load()
        assert loaded == 1
        assert collector2.entry_count == 1
        entries = collector2.get_entries()
        assert entries[0].task_id == "T-2-29"
        assert entries[0].tags == ["accurate"]

    def test_load_preserves_id_counter(self, tmp_path: Path) -> None:
        store = tmp_path / "feedback.json"
        collector1 = FeedbackCollector(store_path=store)
        collector1.add(task_id="T-2-29", score=5)
        collector1.flush()

        collector2 = FeedbackCollector(store_path=store)
        collector2.load()
        new_entry = collector2.add(task_id="T-2-30", score=3)
        assert new_entry.entry_id == "FB-0002"

    def test_load_no_file(self, tmp_path: Path) -> None:
        collector = FeedbackCollector(store_path=tmp_path / "nonexistent.json")
        assert collector.load() == 0

    def test_load_no_store_path(self) -> None:
        collector = FeedbackCollector()
        assert collector.load() == 0

    def test_clear(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-2-29", score=5)
        collector.add(task_id="T-2-30", score=3)
        removed = collector.clear()
        assert removed == 2
        assert collector.entry_count == 0

    def test_store_path_property(self, tmp_path: Path) -> None:
        store = tmp_path / "feedback.json"
        collector = FeedbackCollector(store_path=store)
        assert collector.store_path == store

    def test_store_path_property_none(self) -> None:
        collector = FeedbackCollector()
        assert collector.store_path is None
