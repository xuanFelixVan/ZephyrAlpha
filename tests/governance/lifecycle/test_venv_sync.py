# [A_test] module_id: MOD-GOV_venv_sync | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_venv_sync
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

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.venv_sync import (
    DepDiff,
    VenvSync,
    VenvSyncResult,
)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def venv_sync(tmp_project: Path) -> VenvSync:
    return VenvSync(project_root=tmp_project)


class TestDepDiff:
    def test_create_dep_diff(self) -> None:
        diff = DepDiff(added=["a"], removed=["b"], changed=["c"])
        assert diff.added == ["a"]
        assert diff.removed == ["b"]
        assert diff.changed == ["c"]

    def test_empty_dep_diff(self) -> None:
        diff = DepDiff(added=[], removed=[], changed=[])
        assert diff.added == []
        assert diff.removed == []
        assert diff.changed == []


class TestVenvSyncResult:
    def test_create_result(self) -> None:
        diff = DepDiff(added=[], removed=[], changed=[])
        result = VenvSyncResult(
            success=True,
            before_freeze="a==1",
            after_freeze="a==2",
            diff=diff,
            details=["ok"],
        )
        assert result.success is True
        assert result.before_freeze == "a==1"
        assert result.after_freeze == "a==2"
        assert result.details == ["ok"]

    def test_result_default_details(self) -> None:
        diff = DepDiff(added=[], removed=[], changed=[])
        result = VenvSyncResult(
            success=False,
            before_freeze="",
            after_freeze="",
            diff=diff,
        )
        assert result.details == []


class TestVenvSyncInit:
    def test_init_with_root(self, tmp_project: Path) -> None:
        vs = VenvSync(project_root=tmp_project)
        assert vs.project_root == tmp_project
        assert vs.req_path == tmp_project / "requirements.txt"

    def test_init_default_root(self) -> None:
        vs = VenvSync()
        assert vs.project_root == Path.cwd()

    def test_init_none_root(self) -> None:
        vs = VenvSync(project_root=None)
        assert vs.project_root == Path.cwd()


class TestParseFreeze:
    def test_parse_single_package(self) -> None:
        result = VenvSync.parse_freeze("requests==2.31.0")
        assert result == {"requests": "2.31.0"}

    def test_parse_multiple_packages(self) -> None:
        freeze = "requests==2.31.0\npyyaml==6.0\nflask==3.0.0"
        result = VenvSync.parse_freeze(freeze)
        assert len(result) == 3
        assert result["pyyaml"] == "6.0"

    def test_parse_empty_string(self) -> None:
        result = VenvSync.parse_freeze("")
        assert result == {}

    def test_parse_ignores_non_versioned(self) -> None:
        freeze = "requests==2.31.0\nsome-local-package\n-e git+https://..."
        result = VenvSync.parse_freeze(freeze)
        assert len(result) == 1
        assert "requests" in result

    def test_parse_case_insensitive(self) -> None:
        result = VenvSync.parse_freeze("PyYAML==6.0")
        assert "pyyaml" in result

    def test_parse_strips_whitespace(self) -> None:
        result = VenvSync.parse_freeze("  requests == 2.31.0  ")
        assert "requests" in result


class TestComputeDiff:
    def test_no_diff(self, venv_sync: VenvSync) -> None:
        before = "requests==2.31.0"
        diff = venv_sync.compute_diff(before, before)
        assert diff.added == []
        assert diff.removed == []
        assert diff.changed == []

    def test_added_package(self, venv_sync: VenvSync) -> None:
        before = "requests==2.31.0"
        after = "requests==2.31.0\nflask==3.0.0"
        diff = venv_sync.compute_diff(before, after)
        assert "flask" in diff.added
        assert diff.removed == []
        assert diff.changed == []

    def test_removed_package(self, venv_sync: VenvSync) -> None:
        before = "requests==2.31.0\nflask==3.0.0"
        after = "requests==2.31.0"
        diff = venv_sync.compute_diff(before, after)
        assert "flask" in diff.removed
        assert diff.added == []

    def test_changed_version(self, venv_sync: VenvSync) -> None:
        before = "requests==2.30.0"
        after = "requests==2.31.0"
        diff = venv_sync.compute_diff(before, after)
        assert "requests" in diff.changed

    def test_empty_before(self, venv_sync: VenvSync) -> None:
        after = "requests==2.31.0"
        diff = venv_sync.compute_diff("", after)
        assert "requests" in diff.added

    def test_empty_after(self, venv_sync: VenvSync) -> None:
        before = "requests==2.31.0"
        diff = venv_sync.compute_diff(before, "")
        assert "requests" in diff.removed


class TestSync:
    @patch("zephyr.infrastructure.rollback.venv_sync.subprocess.run")
    def test_sync_skip_deps(self, mock_run: MagicMock, venv_sync: VenvSync) -> None:
        freeze_result = MagicMock()
        freeze_result.stdout = "requests==2.31.0"
        mock_run.return_value = freeze_result
        result = venv_sync.sync(skip_deps=True)
        assert result.success is True
        assert "skipped" in result.details[0].lower()
        assert result.diff.added == []
        assert result.diff.removed == []
        assert result.diff.changed == []

    @patch("zephyr.infrastructure.rollback.venv_sync.subprocess.run")
    def test_sync_no_requirements_file(self, mock_run: MagicMock, venv_sync: VenvSync) -> None:
        freeze_result = MagicMock()
        freeze_result.stdout = "requests==2.31.0"
        mock_run.return_value = freeze_result
        result = venv_sync.sync()
        assert result.success is True
        assert any("No requirements.txt" in d for d in result.details)

    @patch("zephyr.infrastructure.rollback.venv_sync.subprocess.run")
    def test_sync_with_requirements_success(
        self,
        mock_run: MagicMock,
        venv_sync: VenvSync,
        tmp_project: Path,
    ) -> None:
        req_path = tmp_project / "requirements.txt"
        req_path.write_text("requests==2.31.0\n", encoding="utf-8")
        freeze_result = MagicMock()
        freeze_result.stdout = "requests==2.31.0"
        install_result = MagicMock()
        install_result.returncode = 0
        mock_run.side_effect = [freeze_result, install_result, freeze_result]
        result = venv_sync.sync()
        assert result.success is True

    @patch("zephyr.infrastructure.rollback.venv_sync.subprocess.run")
    def test_sync_pip_install_fails(
        self,
        mock_run: MagicMock,
        venv_sync: VenvSync,
        tmp_project: Path,
    ) -> None:
        req_path = tmp_project / "requirements.txt"
        req_path.write_text("bad-package==99.99.99\n", encoding="utf-8")
        freeze_result = MagicMock()
        freeze_result.stdout = ""
        mock_run.side_effect = [freeze_result, Exception("pip failed"), freeze_result]
        result = venv_sync.sync()
        assert result.success is True
        assert any("error" in d.lower() for d in result.details)

    @patch("zephyr.infrastructure.rollback.venv_sync.subprocess.run")
    def test_sync_freeze_exception(self, mock_run: MagicMock, venv_sync: VenvSync) -> None:
        mock_run.side_effect = OSError("pip not found")
        result = venv_sync.sync(skip_deps=True)
        assert result.success is True
        assert result.before_freeze == ""
