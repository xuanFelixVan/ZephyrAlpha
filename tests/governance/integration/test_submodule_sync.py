# [A_test] module_id: MOD-GOV_submodule_sync | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_submodule_sync
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] SubmoduleSync layout detection;sync report generation;exit code 16 on out-of-sync
# [MODIFY-GUARD] src/zephyr/rollback/submodule_sync.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_submodule_sync.py
# [TTL] task_bound

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.submodule_sync import (
    EXIT_SUBMODULE_OUT_OF_SYNC,
    SubmoduleInfo,
    SubmoduleSync,
    SyncResult,
)


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def sync(project_root: Path) -> SubmoduleSync:
    return SubmoduleSync(project_root=project_root)


class TestSubmoduleSyncInstantiation:
    def test_with_explicit_root(self, project_root: Path) -> None:
        s = SubmoduleSync(project_root=project_root)
        assert s.project_root == project_root

    def test_with_none_uses_cwd(self) -> None:
        s = SubmoduleSync(project_root=None)
        assert s.project_root == Path.cwd()


class TestDetectLayout:
    def test_submodule_layout(self, project_root: Path, sync: SubmoduleSync) -> None:
        (project_root / ".gitmodules").write_text(
            '[submodule "lib"]\n\tpath = lib\n\turl = https://example.com/lib.git\n', encoding="utf-8"
        )
        assert sync.detect_layout() == "submodule"

    def test_monorepo_layout(self, project_root: Path, sync: SubmoduleSync) -> None:
        src_dir = project_root / "src"
        src_dir.mkdir()
        (src_dir / "pkg_a").mkdir()
        (src_dir / "pkg_b").mkdir()
        assert sync.detect_layout() == "monorepo"

    def test_single_repo_layout(self, project_root: Path, sync: SubmoduleSync) -> None:
        assert sync.detect_layout() == "single_repo"

    def test_single_subdir_in_src(self, project_root: Path, sync: SubmoduleSync) -> None:
        src_dir = project_root / "src"
        src_dir.mkdir()
        (src_dir / "only_one").mkdir()
        assert sync.detect_layout() == "single_repo"

    def test_no_src_dir(self, project_root: Path, sync: SubmoduleSync) -> None:
        assert sync.detect_layout() == "single_repo"


class TestListSubmodules:
    def test_no_gitmodules(self, sync: SubmoduleSync) -> None:
        result = sync.list_submodules()
        assert result == []

    def test_gitmodules_exists_no_git(self, project_root: Path, sync: SubmoduleSync) -> None:
        (project_root / ".gitmodules").write_text(
            '[submodule "lib"]\n\tpath = lib\n\turl = https://example.com/lib.git\n', encoding="utf-8"
        )
        with patch("subprocess.run", side_effect=Exception("no git")):
            result = sync.list_submodules()
        assert result == []

    def test_gitmodules_with_submodule_output(self, project_root: Path, sync: SubmoduleSync) -> None:
        (project_root / ".gitmodules").write_text('[submodule "lib"]\n', encoding="utf-8")
        mock_output = MagicMock()
        mock_output.stdout = " abc1234 lib\n def5678 core\n"
        with patch("subprocess.run", return_value=mock_output):
            with patch.object(sync, "_get_submodule_url", return_value="https://example.com/lib.git"):
                result = sync.list_submodules()
        assert len(result) == 2
        assert result[0].path == "lib"
        assert result[0].current_sha == "abc1234"
        assert result[1].path == "core"
        assert result[1].current_sha == "def5678"

    def test_gitmodules_empty_output(self, project_root: Path, sync: SubmoduleSync) -> None:
        (project_root / ".gitmodules").write_text("", encoding="utf-8")
        mock_output = MagicMock()
        mock_output.stdout = ""
        with patch("subprocess.run", return_value=mock_output):
            result = sync.list_submodules()
        assert result == []


class TestGetSubmoduleShas:
    def test_success(self, sync: SubmoduleSync) -> None:
        mock_output = MagicMock()
        mock_output.stdout = "lib abc1234\ncore def5678\n"
        with patch("subprocess.run", return_value=mock_output):
            result = sync.get_submodule_shas()
        assert result == {"lib": "abc1234", "core": "def5678"}

    def test_git_failure(self, sync: SubmoduleSync) -> None:
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=10)):
            result = sync.get_submodule_shas()
        assert result == {}

    def test_empty_output(self, sync: SubmoduleSync) -> None:
        mock_output = MagicMock()
        mock_output.stdout = ""
        with patch("subprocess.run", return_value=mock_output):
            result = sync.get_submodule_shas()
        assert result == {}


class TestSyncSubmodule:
    def test_nonexistent_path(self, sync: SubmoduleSync) -> None:
        result = sync.sync_submodule("nonexistent_path", "abc1234")
        assert result is False

    def test_existing_path_success(self, project_root: Path, sync: SubmoduleSync) -> None:
        sub_path = project_root / "lib"
        sub_path.mkdir()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = sync.sync_submodule("lib", "abc1234")
        assert result is True
        assert mock_run.call_count == 2

    def test_existing_path_git_failure(self, project_root: Path, sync: SubmoduleSync) -> None:
        sub_path = project_root / "lib"
        sub_path.mkdir()
        with patch("subprocess.run", side_effect=Exception("git error")):
            result = sync.sync_submodule("lib", "abc1234")
        assert result is False


class TestSyncAllSubmodules:
    def test_no_submodules(self, sync: SubmoduleSync) -> None:
        with patch.object(sync, "list_submodules", return_value=[]):
            result = sync.sync_all_submodules("abc1234")
        assert isinstance(result, SyncResult)
        assert result.success is True
        assert result.submodules_processed == 0
        assert result.submodules_synced == 0
        assert result.exit_code == 0

    def test_all_synced(self, sync: SubmoduleSync) -> None:
        subs = [
            SubmoduleInfo(path="lib", url="https://example.com/lib.git", current_sha="aaa1111"),
            SubmoduleInfo(path="core", url="https://example.com/core.git", current_sha="bbb2222"),
        ]
        with patch.object(sync, "list_submodules", return_value=subs):
            with patch.object(sync, "sync_submodule", return_value=True):
                result = sync.sync_all_submodules("target_sha")
        assert result.success is True
        assert result.submodules_synced == 2
        assert result.exit_code == 0

    def test_some_out_of_sync(self, sync: SubmoduleSync) -> None:
        subs = [
            SubmoduleInfo(path="lib", url="u1", current_sha="aaa"),
            SubmoduleInfo(path="core", url="u2", current_sha="bbb"),
        ]

        def fake_sync(path: str, sha: str) -> bool:
            return path == "lib"

        with patch.object(sync, "list_submodules", return_value=subs):
            with patch.object(sync, "sync_submodule", side_effect=fake_sync):
                result = sync.sync_all_submodules("target_sha")
        assert result.success is False
        assert result.out_of_sync == ["core"]
        assert result.exit_code == EXIT_SUBMODULE_OUT_OF_SYNC


class TestRollbackSubmodulesConsistent:
    def test_all_synced(self, sync: SubmoduleSync) -> None:
        targets = {"lib": "sha1", "core": "sha2"}
        with patch.object(sync, "sync_submodule", return_value=True):
            result = sync.rollback_submodules_consistent("main_sha", targets)
        assert result.success is True
        assert result.submodules_synced == 2
        assert result.exit_code == 0

    def test_partial_failure(self, sync: SubmoduleSync) -> None:
        targets = {"lib": "sha1", "core": "sha2"}

        def fake_sync(path: str, sha: str) -> bool:
            return path == "lib"

        with patch.object(sync, "sync_submodule", side_effect=fake_sync):
            result = sync.rollback_submodules_consistent("main_sha", targets)
        assert result.success is False
        assert result.out_of_sync == ["core"]
        assert result.exit_code == EXIT_SUBMODULE_OUT_OF_SYNC

    def test_empty_targets(self, sync: SubmoduleSync) -> None:
        result = sync.rollback_submodules_consistent("main_sha", {})
        assert result.success is True
        assert result.submodules_processed == 0


class TestDetectMonorepoModules:
    def test_no_src_dir(self, project_root: Path, sync: SubmoduleSync) -> None:
        result = sync.detect_monorepo_modules()
        assert result == []

    def test_src_with_packages(self, project_root: Path, sync: SubmoduleSync) -> None:
        src_dir = project_root / "src"
        pkg_a = src_dir / "pkg_a"
        pkg_a.mkdir(parents=True)
        (pkg_a / "setup.py").write_text("# setup", encoding="utf-8")
        pkg_b = src_dir / "pkg_b"
        pkg_b.mkdir(parents=True)
        (pkg_b / "pyproject.toml").write_text("# pyproject", encoding="utf-8")
        result = sync.detect_monorepo_modules()
        assert len(result) == 2
        names = [m.package_name for m in result]
        assert "pkg_a" in names
        assert "pkg_b" in names

    def test_src_without_packages(self, project_root: Path, sync: SubmoduleSync) -> None:
        src_dir = project_root / "src"
        plain = src_dir / "plain_dir"
        plain.mkdir(parents=True)
        result = sync.detect_monorepo_modules()
        assert result == []


class TestGenerateSyncReport:
    def test_report_structure(self, sync: SubmoduleSync) -> None:
        sr = SyncResult(
            success=True,
            submodules_processed=2,
            submodules_synced=2,
            out_of_sync=[],
            errors=[],
            exit_code=0,
        )
        report = sync.generate_sync_report(sr)
        assert report["success"] is True
        assert report["submodules_processed"] == 2
        assert report["submodules_synced"] == 2
        assert report["out_of_sync"] == []
        assert report["exit_code"] == 0
        assert "report_id" in report
        assert "timestamp_utc" in report
        assert report["report_id"].startswith("SUBMODULE-SYNC-")

    def test_report_with_failures(self, sync: SubmoduleSync) -> None:
        sr = SyncResult(
            success=False,
            submodules_processed=3,
            submodules_synced=1,
            out_of_sync=["lib", "core"],
            errors=["SUBMODULE_OUT_OF_SYNC: lib"],
            exit_code=EXIT_SUBMODULE_OUT_OF_SYNC,
        )
        report = sync.generate_sync_report(sr)
        assert report["success"] is False
        assert report["exit_code"] == 16
        assert len(report["out_of_sync"]) == 2


class TestSubmoduleInfoDataclass:
    def test_defaults(self) -> None:
        info = SubmoduleInfo(path="lib", url="https://example.com/lib.git", current_sha="abc1234")
        assert info.target_sha == ""
        assert info.synced is False

    def test_custom_values(self) -> None:
        info = SubmoduleInfo(path="lib", url="u", current_sha="aaa", target_sha="bbb", synced=True)
        assert info.target_sha == "bbb"
        assert info.synced is True


class TestExitCode:
    def test_exit_code_value(self) -> None:
        assert EXIT_SUBMODULE_OUT_OF_SYNC == 16
