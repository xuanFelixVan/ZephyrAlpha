# [A_test] module_id: MOD-GOV_warm_standby | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_warm_standby
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.warm_standby import (
    CutoverResult,
    StandbyState,
    WarmStandby,
)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def standby(tmp_project: Path) -> WarmStandby:
    return WarmStandby(project_root=tmp_project)


def _make_state(
    standby_commit: str = "abc1234",
    standby_path: str = "/tmp/standby",
    last_verified_at: str = "2026-01-01T00:00:00Z",
    is_active: bool = True,
    is_stale: bool = False,
) -> StandbyState:
    return StandbyState(
        standby_commit=standby_commit,
        standby_path=standby_path,
        last_verified_at=last_verified_at,
        is_active=is_active,
        is_stale=is_stale,
    )


class TestStandbyState:
    def test_create_state(self) -> None:
        state = _make_state()
        assert state.standby_commit == "abc1234"
        assert state.standby_path == "/tmp/standby"
        assert state.is_active is True
        assert state.is_stale is False

    def test_state_fields(self) -> None:
        state = StandbyState(
            standby_commit="def5678",
            standby_path="/other/path",
            last_verified_at="2026-05-22T00:00:00Z",
            is_active=False,
            is_stale=True,
        )
        assert state.standby_commit == "def5678"
        assert state.is_active is False
        assert state.is_stale is True


class TestCutoverResult:
    def test_create_result(self) -> None:
        result = CutoverResult(
            success=True,
            previous_commit="abc",
            target_commit="def",
            rto_ms=50,
            exit_code=0,
            details=["ok"],
        )
        assert result.success is True
        assert result.rto_ms == 50
        assert result.exit_code == 0

    def test_result_default_details(self) -> None:
        result = CutoverResult(
            success=False,
            previous_commit="",
            target_commit="xyz",
            rto_ms=0,
            exit_code=14,
        )
        assert result.details == []


class TestWarmStandbyInit:
    def test_init_with_root(self, tmp_project: Path) -> None:
        ws = WarmStandby(project_root=tmp_project)
        assert ws.project_root == tmp_project
        assert ws.standby_dir == tmp_project / ".zephyr/warm_standby"
        assert ws.state_path == tmp_project / ".zephyr/warm_standby_state.json"

    def test_init_default_root(self) -> None:
        ws = WarmStandby()
        assert ws.project_root == Path.cwd()

    def test_init_none_root(self) -> None:
        ws = WarmStandby(project_root=None)
        assert ws.project_root == Path.cwd()

    def test_exit_code_constant(self) -> None:
        assert WarmStandby.EXIT_CODE_CUTOVER == 14


class TestInitialize:
    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_initialize_creates_state_file(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        worktree_result = MagicMock()
        worktree_result.returncode = 0
        mock_run.return_value = worktree_result
        result = standby.initialize("abc1234")
        assert result is True
        state_path = tmp_project / ".zephyr/warm_standby_state.json"
        assert state_path.exists()
        data = json.loads(state_path.read_text(encoding="utf-8"))
        assert data["standby_commit"] == "abc1234"
        assert data["is_active"] is True

    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_initialize_returns_true_if_dir_exists(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        standby_dir = tmp_project / ".zephyr/warm_standby"
        standby_dir.mkdir(parents=True)
        result = standby.initialize("abc1234")
        assert result is True
        mock_run.assert_not_called()

    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_initialize_failure(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
    ) -> None:
        mock_run.side_effect = OSError("git not found")
        result = standby.initialize("abc1234")
        assert result is False


class TestCutover:
    def test_cutover_no_state_file(self, standby: WarmStandby) -> None:
        result = standby.cutover("def5678")
        assert result.success is False
        assert result.exit_code == 14
        assert "No warm standby initialized" in result.details

    def test_cutover_corrupt_state_file(
        self,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        state_path = tmp_project / ".zephyr/warm_standby_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text("not json", encoding="utf-8")
        result = standby.cutover("def5678")
        assert result.success is False
        assert "Failed to read standby state" in result.details

    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_cutover_success(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        state_path = tmp_project / ".zephyr/warm_standby_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_data = {
            "standby_commit": "abc1234",
            "standby_path": str(tmp_project / ".zephyr/warm_standby"),
            "last_verified_at": "2026-01-01T00:00:00Z",
            "is_active": True,
            "is_stale": False,
        }
        state_path.write_text(json.dumps(state_data), encoding="utf-8")
        checkout_result = MagicMock()
        checkout_result.returncode = 0
        mock_run.return_value = checkout_result
        result = standby.cutover("def5678")
        assert result.success is True
        assert result.previous_commit == "abc1234"
        assert result.target_commit == "def5678"
        assert result.exit_code == 0
        assert result.rto_ms >= 0

    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_cutover_git_checkout_failure(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        state_path = tmp_project / ".zephyr/warm_standby_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_data = {
            "standby_commit": "abc1234",
            "standby_path": "/tmp/standby",
            "last_verified_at": "2026-01-01T00:00:00Z",
            "is_active": True,
            "is_stale": False,
        }
        state_path.write_text(json.dumps(state_data), encoding="utf-8")
        mock_run.side_effect = RuntimeError("checkout failed")
        result = standby.cutover("def5678")
        assert result.success is False
        assert result.exit_code == 14


class TestRotate:
    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_rotate_removes_old_and_initializes(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        standby_dir = tmp_project / ".zephyr/warm_standby"
        standby_dir.mkdir(parents=True)
        remove_result = MagicMock()
        remove_result.returncode = 0
        add_result = MagicMock()
        add_result.returncode = 0
        mock_run.side_effect = [remove_result, add_result]
        result = standby.rotate("newcommit")
        assert result is True

    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_rotate_remove_failure_still_initializes(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
    ) -> None:
        remove_error = MagicMock(side_effect=OSError("worktree remove failed"))
        add_result = MagicMock()
        add_result.returncode = 0
        mock_run.side_effect = [remove_error, add_result]
        result = standby.rotate("newcommit")
        assert result is True


class TestVerifyIntegrity:
    def test_verify_no_standby_dir(self, standby: WarmStandby) -> None:
        assert standby.verify_integrity() is False

    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_verify_success(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        standby_dir = tmp_project / ".zephyr/warm_standby"
        standby_dir.mkdir(parents=True)
        result = MagicMock()
        result.returncode = 0
        mock_run.return_value = result
        assert standby.verify_integrity() is True

    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_verify_git_failure(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        standby_dir = tmp_project / ".zephyr/warm_standby"
        standby_dir.mkdir(parents=True)
        result = MagicMock()
        result.returncode = 1
        mock_run.return_value = result
        assert standby.verify_integrity() is False

    @patch("zephyr.infrastructure.rollback.warm_standby.subprocess.run")
    def test_verify_exception(
        self,
        mock_run: MagicMock,
        standby: WarmStandby,
        tmp_project: Path,
    ) -> None:
        standby_dir = tmp_project / ".zephyr/warm_standby"
        standby_dir.mkdir(parents=True)
        mock_run.side_effect = OSError("git error")
        assert standby.verify_integrity() is False


class TestGetState:
    def test_get_state_no_file(self, standby: WarmStandby) -> None:
        assert standby.get_state() is None

    def test_get_state_valid_file(self, standby: WarmStandby, tmp_project: Path) -> None:
        state_path = tmp_project / ".zephyr/warm_standby_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_data = {
            "standby_commit": "abc1234",
            "standby_path": "/tmp/standby",
            "last_verified_at": "2026-01-01T00:00:00Z",
            "is_active": True,
            "is_stale": False,
        }
        state_path.write_text(json.dumps(state_data), encoding="utf-8")
        state = standby.get_state()
        assert state is not None
        assert state.standby_commit == "abc1234"
        assert state.is_active is True

    def test_get_state_corrupt_file(self, standby: WarmStandby, tmp_project: Path) -> None:
        state_path = tmp_project / ".zephyr/warm_standby_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text("{{{bad json}}}", encoding="utf-8")
        assert standby.get_state() is None


class TestSaveAndReadState:
    def test_roundtrip(self, standby: WarmStandby, tmp_project: Path) -> None:
        state_path = tmp_project / ".zephyr/warm_standby_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        original = _make_state()
        standby.save_state(original)
        loaded = standby.read_state()
        assert loaded is not None
        assert loaded.standby_commit == original.standby_commit
        assert loaded.standby_path == original.standby_path
        assert loaded.is_active == original.is_active
        assert loaded.is_stale == original.is_stale

    def test_read_state_missing_file(self, standby: WarmStandby) -> None:
        assert standby.read_state() is None
