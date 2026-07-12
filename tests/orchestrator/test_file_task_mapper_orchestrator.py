# [A_test] module_id: SRC-TST-1915 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-534 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.orchestrator.test_file_task_mapper
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for file_task_mapper.py (T-2-02)
"""

from pathlib import Path

import pytest
import yaml

from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace
from zephyr.orchestrator.file_task_mapper import (
    FileTaskMapper,
    classify_file_to_namespace,
)


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    return tmp_path / "test_metadata.db"


@pytest.fixture
def mapper(tmp_db: Path) -> FileTaskMapper:
    return FileTaskMapper(db_path=tmp_db)


class TestClassifyFileToNamespace:
    def test_adr_pattern(self) -> None:
        ns = classify_file_to_namespace("docs/02_enterprise_architecture/architecture-rationale-log.md")
        assert ns == TaskNamespace.ADR

    def test_construction_plan_pattern(self) -> None:
        ns = classify_file_to_namespace("docs/04_construction_plans/construction-plan-L01-infrastructure.md")
        assert ns == TaskNamespace.CP

    def test_ke_pattern(self) -> None:
        ns = classify_file_to_namespace("docs/08_knowledge/best-practices/ke-025-encoding-lesson.md")
        assert ns == TaskNamespace.KE

    def test_scripts_pattern(self) -> None:
        ns = classify_file_to_namespace("scripts/governance/validate_ssot.py")
        assert ns == TaskNamespace.OPS

    def test_src_pattern(self) -> None:
        ns = classify_file_to_namespace("src/zephyr/db/task_repo.py")
        assert ns == TaskNamespace.SRC

    def test_std_pattern(self) -> None:
        ns = classify_file_to_namespace("docs/01_policies_and_standards/governance/task/task-card-standard.md")
        assert ns == TaskNamespace.STD

    def test_dw_pattern(self) -> None:
        ns = classify_file_to_namespace("docs/19_development_workspace/structure-and-mapping/handoff-log.md")
        assert ns == TaskNamespace.DW

    def test_ops_fallback(self) -> None:
        ns = classify_file_to_namespace("docs/some-random-file.md")
        assert ns == TaskNamespace.OPS

    def test_windows_backslash(self) -> None:
        ns = classify_file_to_namespace("docs\\02_enterprise_architecture\\adr\\adr-0038-file-as-task-paradigm.md")
        assert ns == TaskNamespace.ADR


class TestFileTaskMapperRegister:
    def test_register_file_returns_task_id(self, mapper: FileTaskMapper) -> None:
        tid = mapper.register_file("docs/test.md", phase=2, title="Test Task")
        assert (
            tid.startswith("OPS-")
            or tid.startswith("ADR-")
            or tid.startswith("CP-")
            or tid.startswith("KE-")
            or tid.startswith("STD-")
            or tid.startswith("DW-")
            or tid.startswith("SRC-")
        )

    def test_register_file_creates_mapping(self, mapper: FileTaskMapper) -> None:
        tid = mapper.register_file("docs/test.md")
        files = mapper.get_tasks_for_file("docs/test.md")
        assert tid in files

    def test_resolve_after_register(self, mapper: FileTaskMapper) -> None:
        tid = mapper.register_file("docs/resolve-test.md")
        result = mapper.resolve("docs/resolve-test.md")
        assert tid in result

    def test_resolve_nonexistent_returns_empty(self, mapper: FileTaskMapper) -> None:
        result = mapper.resolve("docs/nonexistent.md")
        assert result == []

    def test_resolve_reverse(self, mapper: FileTaskMapper) -> None:
        tid = mapper.register_file("docs/reverse-test.md")
        files = mapper.resolve_reverse(tid)
        assert any(f["file_path"] == "docs/reverse-test.md" for f in files)

    def test_resolve_reverse_no_file_task(self, mapper: FileTaskMapper) -> None:
        files = mapper.resolve_reverse("OPS-99999")
        assert files == []


class TestFileTaskMapperTriage:
    def test_register_from_triage(self, mapper: FileTaskMapper, tmp_path: Path) -> None:
        triage_file = tmp_path / "triage-result.yaml"
        triage_data = {
            "files": [
                {"path": "docs/file1.md", "phase": 2, "name": "File 1"},
                {"path": "docs/file2.md", "phase": 2, "name": "File 2"},
            ]
        }
        triage_file.write_text(yaml.dump(triage_data), encoding="utf-8")

        report = mapper.register_from_triage(triage_file)
        assert report.total == 2
        assert report.inserted == 2
        assert report.skipped_existing == 0

    def test_register_from_triage_skips_existing(self, mapper: FileTaskMapper, tmp_path: Path) -> None:
        triage_file = tmp_path / "triage-result.yaml"
        triage_data = {
            "files": [
                {"path": "docs/dup.md", "phase": 2, "name": "Dup"},
            ]
        }
        triage_file.write_text(yaml.dump(triage_data), encoding="utf-8")

        report1 = mapper.register_from_triage(triage_file)
        report2 = mapper.register_from_triage(triage_file)
        assert report1.inserted == 1
        assert report2.inserted == 1

    def test_register_from_triage_missing_file(self, mapper: FileTaskMapper, tmp_path: Path) -> None:
        triage_file = tmp_path / "nonexistent.yaml"
        report = mapper.register_from_triage(triage_file)
        assert len(report.errors) == 1


class TestFileTaskMapperRollback:
    def test_rollback_removes_task(self, mapper: FileTaskMapper) -> None:
        tid = mapper.register_file("docs/rollback-test.md")
        mapper.rollback(tid)
        result = mapper.resolve("docs/rollback-test.md")
        assert result == []

    def test_rollback_nonexistent_does_not_raise(self, mapper: FileTaskMapper) -> None:
        mapper.rollback("OPS-99999")


class TestFileTaskMapperSync:
    def test_sync_pending_no_file_is_consistent(self, mapper: FileTaskMapper) -> None:
        tid = mapper.register_file("docs/sync-pending-no-file.md")
        report = mapper.sync_file_state(tid)
        assert report.checked == 1
        assert report.consistent == 1
        assert len(report.inconsistencies) == 0

    def test_sync_single_task(self, mapper: FileTaskMapper) -> None:
        tid = mapper.register_file("docs/sync-single.md")
        report = mapper.sync_file_state(tid)
        assert report.checked == 1

    def test_sync_all_tasks(self, mapper: FileTaskMapper) -> None:
        mapper.register_file("docs/sync-a.md")
        mapper.register_file("docs/sync-b.md")
        report = mapper.sync_file_state()
        assert report.checked >= 2
