# [A_test] module_id: MOD-GOV_dream_cycle | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_dream_cycle
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import json
import warnings
from datetime import datetime
from pathlib import Path

from zephyr.trading.dream_cycle import DreamCycle, DreamReport


class TestDreamReport:
    def test_default_values(self) -> None:
        report = DreamReport()
        assert report.archived_files == 0
        assert report.extracted_patterns == 0
        assert report.forgotten_items == 0
        assert report.indexed_entries == 0
        assert report.committed is False
        assert report.timestamp != ""

    def test_custom_values(self) -> None:
        report = DreamReport(archived_files=5, committed=True)
        assert report.archived_files == 5
        assert report.committed is True


class TestDreamCycleInit:
    def test_init_creates_dirs(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        cycle = DreamCycle(archive_dir=archive)
        assert cycle.archive_dir == archive
        assert cycle.episodic_dir == archive / "episodic"
        assert cycle.semantic_dir == archive / "semantic"

    def test_init_no_audit_dir(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "archive")
        assert cycle.audit_log_dir is None


class TestTriggerArchival:
    def test_trigger_archival_no_audit_dir(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "archive")
        report = cycle.trigger_archival()
        assert isinstance(report, DreamReport)
        assert report.archived_files == 0

    def test_trigger_archival_with_empty_audit_dir(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        cycle = DreamCycle(archive_dir=tmp_path / "archive", audit_log_dir=audit_dir)
        report = cycle.trigger_archival()
        assert report.archived_files == 0

    def test_trigger_archival_copies_old_logs(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        old_file = audit_dir / "ai_audit_2025-01-01.jsonl"
        old_file.write_text('{"test": true}\n', encoding="utf-8")
        cycle = DreamCycle(archive_dir=archive, audit_log_dir=audit_dir)
        report = cycle.trigger_archival()
        assert report.archived_files >= 1

    def test_trigger_archival_creates_semantic_index(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "archive")
        report = cycle.trigger_archival()
        index_file = tmp_path / "archive" / "semantic" / "index.json"
        assert index_file.exists()
        assert report.indexed_entries == 0

    def test_trigger_archival_creates_forgotten_log(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "archive")
        report = cycle.trigger_archival()
        assert (tmp_path / "archive" / "forgotten.log").exists()
        assert report.forgotten_items == 0


class TestNeedsArchival:
    def test_needs_archival_no_audit_dir(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "archive")
        assert cycle.needs_archival() is False

    def test_needs_archival_no_today_file(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        cycle = DreamCycle(archive_dir=tmp_path / "archive", audit_log_dir=audit_dir)
        assert cycle.needs_archival() is False

    def test_needs_archival_with_today_file(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        # 与被测代码同一时钟（now_utc）——datetime.now() 本地时在 UTC+8 的 00:00-08:00
        # 窗口与 UTC 日期错位致假性失败（2026-08-21 波3 回归实证）
        from zephyr.shared.utils.time_utils import now_utc

        today = now_utc().strftime("%Y-%m-%d")
        today_file = audit_dir / f"ai_audit_{today}.jsonl"
        today_file.write_text('{"entry": 1}\n', encoding="utf-8")
        cycle = DreamCycle(archive_dir=tmp_path / "archive", audit_log_dir=audit_dir)
        assert cycle.needs_archival() is True

    def test_needs_archival_already_archived(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        # 与被测代码同一时钟（now_utc）——防 UTC+8 的 00:00-08:00 窗口本地/UTC 日期错位
        from zephyr.shared.utils.time_utils import now_utc

        today = now_utc().strftime("%Y-%m-%d")
        today_file = audit_dir / f"ai_audit_{today}.jsonl"
        today_file.write_text('{"entry": 1}\n', encoding="utf-8")
        episodic_today = archive / "episodic" / today
        episodic_today.mkdir(parents=True)
        cycle = DreamCycle(archive_dir=archive, audit_log_dir=audit_dir)
        assert cycle.needs_archival() is False


class TestQueryEpisodic:
    def test_query_episodic_nonexistent_date(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "archive")
        assert cycle.query_episodic("2099-01-01") == []

    def test_query_episodic_with_data(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        date_dir = archive / "episodic" / "2025-01-01"
        date_dir.mkdir(parents=True)
        data_file = date_dir / "ai_audit_2025-01-01.jsonl"
        data_file.write_text('{"key": "value1"}\n{"key": "value2"}\n', encoding="utf-8")
        cycle = DreamCycle(archive_dir=archive)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            results = cycle.query_episodic("2025-01-01")
        assert len(results) == 2
        assert results[0]["key"] == "value1"

    def test_query_episodic_invalid_json_skipped(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        date_dir = archive / "episodic" / "2025-01-01"
        date_dir.mkdir(parents=True)
        data_file = date_dir / "ai_audit_2025-01-01.jsonl"
        data_file.write_text('{"valid": true}\nINVALID JSON\n', encoding="utf-8")
        cycle = DreamCycle(archive_dir=archive)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            results = cycle.query_episodic("2025-01-01")
        assert len(results) == 1


class TestQuerySemantic:
    def test_query_semantic_no_index(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "archive")
        assert cycle.query_semantic(["tag1"]) == []

    def test_query_semantic_with_matching_tags(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        semantic_dir = archive / "semantic"
        semantic_dir.mkdir(parents=True)
        index_file = semantic_dir / "index.json"
        entries = [
            {"tags": ["python", "test"], "content": "entry1"},
            {"tags": ["java", "prod"], "content": "entry2"},
        ]
        index_file.write_text(json.dumps(entries), encoding="utf-8")
        cycle = DreamCycle(archive_dir=archive)
        results = cycle.query_semantic(["python"])
        assert len(results) == 1
        assert results[0]["content"] == "entry1"

    def test_query_semantic_case_insensitive(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        semantic_dir = archive / "semantic"
        semantic_dir.mkdir(parents=True)
        index_file = semantic_dir / "index.json"
        entries = [{"tags": ["Python"], "content": "entry1"}]
        index_file.write_text(json.dumps(entries), encoding="utf-8")
        cycle = DreamCycle(archive_dir=archive)
        results = cycle.query_semantic(["python"])
        assert len(results) == 1

    def test_query_semantic_empty_tags(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        semantic_dir = archive / "semantic"
        semantic_dir.mkdir(parents=True)
        index_file = semantic_dir / "index.json"
        entries = [{"tags": ["python"], "content": "entry1"}]
        index_file.write_text(json.dumps(entries), encoding="utf-8")
        cycle = DreamCycle(archive_dir=archive)
        results = cycle.query_semantic([])
        assert results == []

    def test_query_semantic_invalid_json(self, tmp_path: Path) -> None:
        archive = tmp_path / "archive"
        semantic_dir = archive / "semantic"
        semantic_dir.mkdir(parents=True)
        index_file = semantic_dir / "index.json"
        index_file.write_text("NOT JSON", encoding="utf-8")
        cycle = DreamCycle(archive_dir=archive)
        assert cycle.query_semantic(["tag"]) == []
