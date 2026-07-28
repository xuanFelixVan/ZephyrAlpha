# [A_test] module_id: MOD-GOV_rollback_simulator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_simulator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.rollback_simulator import RollbackSimulator, SimulationResult


@pytest.fixture
def simulator(tmp_path: Path) -> RollbackSimulator:
    return RollbackSimulator(project_root=tmp_path)


class TestRollbackSimulatorInstantiation:
    def test_creates_with_defaults(self):
        sim = RollbackSimulator()
        assert sim.project_root is not None

    def test_creates_with_custom_root(self, tmp_path: Path):
        sim = RollbackSimulator(project_root=tmp_path)
        assert sim.project_root == tmp_path

    def test_worktree_prefix_constant(self):
        assert RollbackSimulator.WORKTREE_PREFIX == ".zephyr/sim_worktree_"


class TestSimulateRollback:
    def test_successful_simulation(self, simulator: RollbackSimulator):
        with patch.object(simulator, "_run_git") as mock_git:
            mock_git.side_effect = [
                "",
                "",
            ]
            with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="",
                    stderr="",
                )
                result = simulator.simulate_rollback("abc1234")
                assert isinstance(result, SimulationResult)
                assert result.safe_to_rollback is True
                assert result.commit_sha == "abc1234"
                assert result.duration_ms >= 0
                assert result.conflict_files == []

    def test_conflict_simulation(self, simulator: RollbackSimulator):
        with patch.object(simulator, "_run_git") as mock_git:
            mock_git.side_effect = [
                "",
                "file1.py\nfile2.py",
                "",
            ]
            with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,
                    stdout="",
                    stderr="CONFLICT (content): Merge conflict in file1.py",
                )
                result = simulator.simulate_rollback("abc1234")
                assert result.safe_to_rollback is False
                assert len(result.conflict_files) >= 0

    def test_simulation_error(self, simulator: RollbackSimulator):
        with patch.object(simulator, "_run_git") as mock_git:
            mock_git.side_effect = Exception("git not available")
            result = simulator.simulate_rollback("abc1234")
            assert result.safe_to_rollback is False
            assert len(result.details) > 0
            assert any("error" in d.lower() for d in result.details)

    def test_simulation_result_fields(self, simulator: RollbackSimulator):
        with patch.object(simulator, "_run_git") as mock_git:
            mock_git.side_effect = ["", ""]
            with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                result = simulator.simulate_rollback("deadbeef")
                assert result.commit_sha == "deadbeef"
                assert isinstance(result.worktree_path, str)
                assert isinstance(result.files_changed, int)
                assert isinstance(result.db_impact, int)
                assert result.db_impact == 0
                assert isinstance(result.details, list)

    def test_simulation_cleans_up_worktree(self, simulator: RollbackSimulator):
        with patch.object(simulator, "_run_git") as mock_git:
            mock_git.side_effect = ["", "", ""]
            with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                simulator.simulate_rollback("abc1234")
                cleanup_calls = [c for c in mock_git.call_args_list if "worktree" in str(c) and "remove" in str(c)]
                assert len(cleanup_calls) >= 1


class TestRunGit:
    def test_run_git_success(self, simulator: RollbackSimulator):
        with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="output", returncode=0)
            result = simulator._run_git(["status"])
            assert result == "output"

    def test_run_git_exception(self, simulator: RollbackSimulator):
        with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=15)
            result = simulator._run_git(["status"])
            assert result == ""

    def test_run_git_with_cwd(self, simulator: RollbackSimulator, tmp_path: Path):
        with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="ok", returncode=0)
            simulator._run_git(["status"], cwd=tmp_path / "subdir")
            call_kwargs = mock_run.call_args
            assert "subdir" in str(call_kwargs)


class TestBoundaryCases:
    def test_empty_commit_sha(self, simulator: RollbackSimulator):
        with patch.object(simulator, "_run_git") as mock_git:
            mock_git.side_effect = ["", ""]
            with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                result = simulator.simulate_rollback("")
                assert isinstance(result, SimulationResult)
                assert result.commit_sha == ""

    def test_very_long_commit_sha(self, simulator: RollbackSimulator):
        long_sha = "a" * 40
        with patch.object(simulator, "_run_git") as mock_git:
            mock_git.side_effect = ["", ""]
            with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                result = simulator.simulate_rollback(long_sha)
                assert result.commit_sha == long_sha

    def test_multiple_simulations(self, simulator: RollbackSimulator):
        with patch.object(simulator, "_run_git") as mock_git:
            mock_git.side_effect = ["", "", "", ""]
            with patch("zephyr.infrastructure.rollback.rollback_simulator.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                r1 = simulator.simulate_rollback("sha1")
                r2 = simulator.simulate_rollback("sha2")
                assert r1.commit_sha == "sha1"
                assert r2.commit_sha == "sha2"
