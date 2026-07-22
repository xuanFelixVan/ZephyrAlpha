# [A_test] module_id: MOD-GOV_cli_summary | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-358 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_cli_summary
# [INVARIANTS] CLISummary.generate返回非空str; save_summary写入JSON文件
# [MODIFY-GUARD] 仅当cli_summary公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_cli_summary.py -q
# [TTL] task_bound

import json

from zephyr.shared.utils.cli_summary import BuildSummary, CLISummary


def _make_summary(
    task_id: str = "TASK-001",
    status: str = "completed",
    files_created: int = 2,
    files_modified: int = 3,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    duration_s: float = 12.5,
    timestamp_utc: str = "2026-01-01T00:00:00+00:00",
) -> BuildSummary:
    return BuildSummary(
        task_id=task_id,
        status=status,
        files_created=files_created,
        files_modified=files_modified,
        warnings=warnings or [],
        errors=errors or [],
        duration_s=duration_s,
        timestamp_utc=timestamp_utc,
    )


class TestCLISummaryInstantiation:
    def test_default_instantiation(self):
        cs = CLISummary()
        assert cs is not None

    def test_instantiation_with_output_dir(self, tmp_path):
        cs = CLISummary(output_dir=tmp_path / "summaries")
        assert cs is not None

    def test_instantiation_with_none_dir(self):
        cs = CLISummary(output_dir=None)
        assert cs is not None


class TestCLISummaryGenerate:
    def test_generate_returns_string(self):
        cs = CLISummary()
        result = cs.generate(_make_summary())
        assert isinstance(result, str)

    def test_generate_non_empty(self):
        cs = CLISummary()
        result = cs.generate(_make_summary())
        assert len(result) > 0

    def test_generate_completed_status(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(status="completed"))
        assert "[OK]" in result

    def test_generate_failed_status(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(status="failed"))
        assert "[FAIL]" in result

    def test_generate_partial_status(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(status="partial"))
        assert "[WARN]" in result

    def test_generate_unknown_status(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(status="unknown"))
        assert "[???]" in result

    def test_generate_shows_task_id(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(task_id="MY-TASK-42"))
        assert "MY-TASK-42" in result

    def test_generate_shows_file_counts(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(files_created=5, files_modified=10))
        assert "+5" in result
        assert "~10" in result

    def test_generate_shows_duration(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(duration_s=45.3))
        assert "45.3s" in result

    def test_generate_shows_warnings_count(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(warnings=["w1", "w2"]))
        assert "Warnings: 2" in result

    def test_generate_shows_errors_count(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(errors=["e1"]))
        assert "Errors: 1" in result

    def test_generate_no_warnings_when_empty(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(warnings=[]))
        assert "Warnings" not in result

    def test_generate_no_errors_when_empty(self):
        cs = CLISummary()
        result = cs.generate(_make_summary(errors=[]))
        assert "Errors" not in result


class TestCLISummaryGenerateJournal:
    def test_generate_journal_returns_string(self):
        cs = CLISummary()
        result = cs.generate_journal([_make_summary()])
        assert isinstance(result, str)

    def test_generate_journal_non_empty(self):
        cs = CLISummary()
        result = cs.generate_journal([_make_summary()])
        assert len(result) > 0

    def test_generate_journal_multiple_summaries(self):
        cs = CLISummary()
        s1 = _make_summary(task_id="T-001", status="completed")
        s2 = _make_summary(task_id="T-002", status="failed", errors=["err1"])
        result = cs.generate_journal([s1, s2])
        assert "T-001" in result
        assert "T-002" in result

    def test_generate_journal_shows_total_tasks(self):
        cs = CLISummary()
        result = cs.generate_journal([_make_summary(), _make_summary()])
        assert "Tasks: 2" in result

    def test_generate_journal_shows_failed_count(self):
        cs = CLISummary()
        s1 = _make_summary(status="completed")
        s2 = _make_summary(status="failed", errors=["e1"])
        result = cs.generate_journal([s1, s2])
        assert "1 failed" in result

    def test_generate_journal_shows_failed_section(self):
        cs = CLISummary()
        s = _make_summary(task_id="FAIL-TASK", status="failed", errors=["error detail"])
        result = cs.generate_journal([s])
        assert "TASKS FAILED" in result
        assert "FAIL-TASK" in result

    def test_generate_journal_no_failed_section_when_all_pass(self):
        cs = CLISummary()
        result = cs.generate_journal([_make_summary(status="completed")])
        assert "TASKS FAILED" not in result

    def test_generate_journal_empty_list(self):
        cs = CLISummary()
        result = cs.generate_journal([])
        assert "Tasks: 0" in result

    def test_generate_journal_shows_total_time(self):
        cs = CLISummary()
        s1 = _make_summary(duration_s=30.0)
        s2 = _make_summary(duration_s=60.0)
        result = cs.generate_journal([s1, s2])
        assert "90.0s" in result


class TestCLISummarySaveSummary:
    def test_save_creates_file(self, tmp_path):
        cs = CLISummary(output_dir=tmp_path / "summaries")
        summary = _make_summary(task_id="SAVE-001")
        path = cs.save_summary(summary)
        assert path.exists()

    def test_save_file_content(self, tmp_path):
        cs = CLISummary(output_dir=tmp_path / "summaries")
        summary = _make_summary(task_id="SAVE-002", status="completed")
        path = cs.save_summary(summary)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["task_id"] == "SAVE-002"
        assert data["status"] == "completed"

    def test_save_file_name_contains_task_id(self, tmp_path):
        cs = CLISummary(output_dir=tmp_path / "summaries")
        summary = _make_summary(task_id="NAME-TEST")
        path = cs.save_summary(summary)
        assert "NAME-TEST" in path.name

    def test_save_creates_output_dir(self, tmp_path):
        output_dir = tmp_path / "new_dir" / "sub"
        cs = CLISummary(output_dir=output_dir)
        summary = _make_summary()
        cs.save_summary(summary)
        assert output_dir.exists()

    def test_save_preserves_all_fields(self, tmp_path):
        cs = CLISummary(output_dir=tmp_path / "summaries")
        summary = _make_summary(
            task_id="FULL-001",
            files_created=3,
            files_modified=7,
            warnings=["w1"],
            errors=["e1"],
            duration_s=99.9,
        )
        path = cs.save_summary(summary)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["files_created"] == 3
        assert data["files_modified"] == 7
        assert data["warnings"] == ["w1"]
        assert data["errors"] == ["e1"]
        assert data["duration_s"] == 99.9


class TestBuildSummary:
    def test_construction(self):
        s = BuildSummary(
            task_id="T-001",
            status="completed",
            files_created=1,
            files_modified=2,
            warnings=[],
            errors=[],
            duration_s=5.0,
            timestamp_utc="2026-01-01T00:00:00Z",
        )
        assert s.task_id == "T-001"
        assert s.status == "completed"
        assert s.files_created == 1
        assert s.files_modified == 2

    def test_empty_warnings_and_errors(self):
        s = _make_summary()
        assert s.warnings == []
        assert s.errors == []
