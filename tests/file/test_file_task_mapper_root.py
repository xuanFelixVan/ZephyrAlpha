# [A_test] module_id: SRC-TST-0911 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_file_task_mapper
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_file_task_mapper_root.py
# [TTL] task_bound

from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace
from zephyr.orchestrator.file_task_mapper import (
    FileTaskMapper,
    RegisterReport,
    SyncInconsistency,
    SyncReport,
    classify_file_to_namespace,
)


class TestClassifyFileToNamespace:
    def test_adr_path(self):
        result = classify_file_to_namespace("docs/adr/adr-0001-test.md")
        assert result == TaskNamespace.KBG

    def test_enterprise_architecture_path(self):
        result = classify_file_to_namespace("docs/02_enterprise_architecture/ea.md")
        assert result == TaskNamespace.KBG

    def test_construction_plan_path(self):
        result = classify_file_to_namespace("docs/construction-plan-phase1.md")
        assert result == TaskNamespace.CP

    def test_ke_path(self):
        result = classify_file_to_namespace("docs/KE-001-entry.md")
        assert result == TaskNamespace.KE

    def test_ke_lowercase_path(self):
        result = classify_file_to_namespace("docs/ke-005-entry.md")
        assert result == TaskNamespace.KE

    def test_std_path(self):
        result = classify_file_to_namespace("docs/01_policies_and_standards/std.md")
        assert result == TaskNamespace.STD

    def test_dw_path(self):
        result = classify_file_to_namespace("docs/19_development_workspace/dw.md")
        assert result == TaskNamespace.DW

    def test_src_path(self):
        result = classify_file_to_namespace("src/zephyr/module.py")
        assert result == TaskNamespace.SRC

    def test_ops_fallback(self):
        result = classify_file_to_namespace("scripts/run.py")
        assert result == TaskNamespace.OPS

    def test_backslash_normalized(self):
        result = classify_file_to_namespace("src\\zephyr\\module.py")
        assert result == TaskNamespace.SRC


class TestRegisterReport:
    def test_default_values(self):
        report = RegisterReport()
        assert report.total == 0
        assert report.inserted == 0
        assert report.skipped_existing == 0
        assert report.errors == []

    def test_custom_values(self):
        report = RegisterReport(total=5, inserted=3, skipped_existing=2, errors=["err"])
        assert report.total == 5
        assert report.inserted == 3
        assert report.skipped_existing == 2
        assert report.errors == ["err"]


class TestSyncInconsistency:
    def test_create(self):
        inc = SyncInconsistency(
            task_id="T-1",
            file_path="test.md",
            disk_exists=False,
            frontmatter_status=None,
            task_status="COMPLETED",
            issue="MISSING_ARTIFACT_ERROR",
        )
        assert inc.task_id == "T-1"
        assert inc.disk_exists is False
        assert inc.issue == "MISSING_ARTIFACT_ERROR"


class TestSyncReport:
    def test_default_values(self):
        report = SyncReport()
        assert report.checked == 0
        assert report.consistent == 0
        assert report.inconsistencies == []


class TestFileTaskMapperInstantiation:
    def test_create_with_default_db(self):
        with patch("zephyr.trading.orchestrator.file_task_mapper.init_db"):
            mapper = FileTaskMapper()
            assert mapper is not None

    def test_create_with_custom_db(self):
        with patch("zephyr.trading.orchestrator.file_task_mapper.init_db"):
            mapper = FileTaskMapper(db_path=Path("/tmp/test.db"))
            assert mapper is not None


class TestFileTaskMapperResolve:
    def test_resolve_returns_empty_for_no_mapping(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.execute.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        with (
            patch("zephyr.trading.orchestrator.file_task_mapper.get_db_connection", return_value=mock_conn),
            patch("zephyr.trading.orchestrator.file_task_mapper.init_db"),
        ):
            mapper = FileTaskMapper()
            result = mapper.resolve("nonexistent.md")
            assert result == []

    def test_resolve_returns_task_ids(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"task_id": "SRC-1"}, {"task_id": "SRC-2"}]
        mock_conn.execute.return_value = mock_cursor
        with (
            patch("zephyr.trading.orchestrator.file_task_mapper.get_db_connection", return_value=mock_conn),
            patch("zephyr.trading.orchestrator.file_task_mapper.init_db"),
        ):
            mapper = FileTaskMapper()
            result = mapper.resolve("src/zephyr/module.py")
            assert result == ["SRC-1", "SRC-2"]


class TestFileTaskMapperResolveReverse:
    def test_resolve_reverse_returns_empty(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.execute.return_value = mock_cursor
        with (
            patch("zephyr.trading.orchestrator.file_task_mapper.get_db_connection", return_value=mock_conn),
            patch("zephyr.trading.orchestrator.file_task_mapper.init_db"),
        ):
            mapper = FileTaskMapper()
            result = mapper.resolve_reverse("NONEXISTENT-1")
            assert result == []

    def test_resolve_reverse_returns_file_roles(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"file_path": "a.py", "role": "primary"},
            {"file_path": "b.py", "role": "secondary"},
        ]
        mock_conn.execute.return_value = mock_cursor
        with (
            patch("zephyr.trading.orchestrator.file_task_mapper.get_db_connection", return_value=mock_conn),
            patch("zephyr.trading.orchestrator.file_task_mapper.init_db"),
        ):
            mapper = FileTaskMapper()
            result = mapper.resolve_reverse("SRC-1")
            assert len(result) == 2
            assert result[0]["file_path"] == "a.py"
            assert result[0]["role"] == "primary"


class TestFileTaskMapperGetTasksForFile:
    def test_delegates_to_resolve(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"task_id": "SRC-1"}]
        mock_conn.execute.return_value = mock_cursor
        with (
            patch("zephyr.trading.orchestrator.file_task_mapper.get_db_connection", return_value=mock_conn),
            patch("zephyr.trading.orchestrator.file_task_mapper.init_db"),
        ):
            mapper = FileTaskMapper()
            result = mapper.get_tasks_for_file("src/zephyr/mod.py")
            assert result == ["SRC-1"]


class TestFileTaskMapperRollback:
    def test_rollback_executes_deletes(self):
        mock_conn = MagicMock()
        with (
            patch("zephyr.trading.orchestrator.file_task_mapper.get_db_connection", return_value=mock_conn),
            patch("zephyr.trading.orchestrator.file_task_mapper.init_db"),
        ):
            mapper = FileTaskMapper()
            mapper.rollback("SRC-1")
        assert mock_conn.execute.call_count >= 4
