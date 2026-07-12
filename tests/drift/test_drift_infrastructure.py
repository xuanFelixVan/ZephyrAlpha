# [A_test] module_id: SRC-TST-0778 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_drift_infrastructure
# [INVARIANTS] 基础设施不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI/CD;drift_engine
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_drift_infrastructure.py
# [TTL] task_bound

import json
import uuid
from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.drift_infrastructure import (
    CheckpointWriter,
    EnvDiffReport,
    MaintenanceWindow,
    PartialDeploymentRecord,
    RecoveryManager,
    check_budget_for_gate,
    consume_budget,
    declare_maintenance_window,
    detect_partial_deployment,
    differential_detection,
    get_maintenance_window,
    get_or_create_budget,
    register_env_tags,
)


class TestMaintenanceWindow:
    def test_is_active_when_in_range(self):
        now = datetime.now(UTC)
        window = MaintenanceWindow(
            start_time=now - timedelta(minutes=10),
            end_time=now + timedelta(hours=2),
        )
        assert window.is_active() is True

    def test_is_not_active_when_expired(self):
        now = datetime.now(UTC)
        window = MaintenanceWindow(
            start_time=now - timedelta(hours=5),
            end_time=now - timedelta(hours=1),
        )
        assert window.is_active() is False

    def test_time_remaining(self):
        now = datetime.now(UTC)
        window = MaintenanceWindow(
            start_time=now,
            end_time=now + timedelta(hours=2),
        )
        remaining = window.time_remaining()
        assert remaining > timedelta(hours=1, minutes=59)
        assert remaining <= timedelta(hours=2)

    def test_time_remaining_expired(self):
        now = datetime.now(UTC)
        window = MaintenanceWindow(
            start_time=now - timedelta(hours=5),
            end_time=now - timedelta(hours=1),
        )
        assert window.time_remaining() == timedelta(0)


class TestDeclareMaintenanceWindow:
    def test_declare_sets_window(self):
        window = declare_maintenance_window(hours=2, triggered_by_auto=True)
        assert window is not None
        assert window.triggered_by_auto is True
        assert window.is_shadow_mode is True

    def test_get_maintenance_window_returns_last(self):
        window = declare_maintenance_window(hours=1)
        retrieved = get_maintenance_window()
        assert retrieved is window


class TestBudget:
    def test_get_or_create_budget(self):
        budget = get_or_create_budget("test-module-budget", "P0")
        assert budget.module_id == "test-module-budget"
        assert budget.tier == "P0"
        assert budget.monthly_budget == 5

    def test_consume_budget(self):
        exhausted = consume_budget("test-consume-module", "P0")
        assert isinstance(exhausted, bool)

    def test_check_budget_for_gate_allowed(self):
        result = check_budget_for_gate("test-gate-module", "P0")
        assert result["allowed"] is True
        assert result["reason"] == "OK"

    def test_check_budget_for_gate_break_glass(self):
        result = check_budget_for_gate("test-breakglass-module", "P0", break_glass=True)
        assert result["allowed"] is True
        assert result["reason"] == "BREAK_GLASS"


class TestCheckpointWriter:
    def test_write_and_cleanup(self, tmp_path):
        scan_id = uuid.uuid4()
        CheckpointWriter.write(
            scan_id,
            ["det-001", "det-002"],
            datetime.now(UTC).isoformat(),
            project_root=str(tmp_path),
        )
        ckpt_dir = tmp_path / "data" / "drift_checkpoints"
        assert ckpt_dir.exists()
        ckpt_file = ckpt_dir / f"{scan_id}.json"
        assert ckpt_file.exists()
        data = json.loads(ckpt_file.read_text(encoding="utf-8"))
        assert data["scan_id"] == str(scan_id)
        assert "det-001" in data["completed_detectors"]
        CheckpointWriter.cleanup(scan_id)
        assert not ckpt_file.exists()


class TestRecoveryManager:
    def test_check_orphaned_empty_dir(self):
        result = RecoveryManager.check_orphaned()
        assert isinstance(result, list)

    def test_on_startup_no_checkpoints(self):
        result = RecoveryManager.on_startup()
        assert result is None or isinstance(result, dict)


class TestDifferentialDetection:
    def test_env_diff_not_true_drift(self):
        register_env_tags("test-mod", {"env": "production"})
        diffs = [{"drift_dimension": "env_config"}]
        report = differential_detection("test-mod", diffs)
        assert isinstance(report, EnvDiffReport)
        assert report.diff_type == "ENV_DIFF"
        assert report.is_true_drift is False

    def test_real_drift(self):
        diffs = [{"drift_dimension": "structural_change"}]
        report = differential_detection("test-mod-real", diffs)
        assert report.is_true_drift is True
        assert report.diff_type == "DRIFT"

    def test_empty_diffs(self):
        report = differential_detection("test-mod-empty", [])
        assert report.is_true_drift is False
        assert report.diff_type == "ENV_DIFF"


class TestPartialDeployment:
    def test_creates_record(self):
        result = detect_partial_deployment(["mod-a", "mod-b"])
        assert result is not None
        assert isinstance(result, PartialDeploymentRecord)
        assert result.module_a == "mod-a"
        assert result.module_b == "mod-b"
        assert result.is_stalled is False

    def test_single_module_returns_none(self):
        result = detect_partial_deployment(["mod-a"])
        assert result is None

    def test_empty_list_returns_none(self):
        result = detect_partial_deployment([])
        assert result is None
