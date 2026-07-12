# [A_test] module_id: SRC-TST-1452 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_resource_guard
# [INVARIANTS] hard_limits_immutable;degradation_monotonic;pool_size_non_negative
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_resource_guard.py
# [TTL] task_bound

from unittest.mock import MagicMock, patch

from zephyr.gov_drift.resource_guard import (
    LIMITS,
    DegradationLevel,
    ResourceLimits,
    ResourceSnapshot,
    ResourceStatus,
    apply_degradation,
    is_guard_running,
    set_critical_handler,
    snapshot,
    stop_guard_loop,
    validate_scalability,
)


class TestDegradationLevel:
    def test_all_levels_exist(self):
        expected = {"NORMAL", "LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"}
        actual = {m.name for m in DegradationLevel}
        assert actual == expected

    def test_str_enum(self):
        assert DegradationLevel.NORMAL.value == "NORMAL"
        assert DegradationLevel.LEVEL_4.value == "LEVEL_4"


class TestResourceStatus:
    def test_all_statuses_exist(self):
        expected = {"OK", "WARNING", "CRITICAL", "OOM"}
        actual = {m.name for m in ResourceStatus}
        assert actual == expected


class TestResourceLimits:
    def test_defaults(self):
        lim = ResourceLimits()
        assert lim.max_memory_mb == 512
        assert lim.max_disk_mb == 2048
        assert lim.max_file_handles == 200

    def test_custom_values(self):
        lim = ResourceLimits(max_memory_mb=1024, max_disk_mb=4096, max_file_handles=500)
        assert lim.max_memory_mb == 1024
        assert lim.max_disk_mb == 4096
        assert lim.max_file_handles == 500

    def test_thresholds_ordered(self):
        lim = ResourceLimits()
        assert lim.l1_threshold < lim.l2_threshold < lim.l3_threshold < lim.l4_threshold


class TestResourceSnapshot:
    def test_defaults(self):
        snap = ResourceSnapshot()
        assert snap.memory_used_mb == 0.0
        assert snap.disk_used_mb == 0.0
        assert snap.file_handles_open == 0
        assert snap.degradation_level == DegradationLevel.NORMAL
        assert snap.status == ResourceStatus.OK

    def test_custom_values(self):
        snap = ResourceSnapshot(
            memory_used_mb=400.0,
            disk_used_mb=1000.0,
            file_handles_open=50,
            degradation_level=DegradationLevel.LEVEL_2,
            status=ResourceStatus.CRITICAL,
        )
        assert snap.memory_used_mb == 400.0
        assert snap.degradation_level == DegradationLevel.LEVEL_2


class TestSnapshot:
    def test_returns_snapshot(self):
        snap = snapshot()
        assert isinstance(snap, ResourceSnapshot)

    def test_normal_status_when_low_memory(self):
        with patch("zephyr.governance.drift_detection.resource_guard._get_memory_usage_mb", return_value=10.0):
            snap = snapshot()
            assert snap.status == ResourceStatus.OK
            assert snap.degradation_level == DegradationLevel.NORMAL

    def test_warning_at_l1(self):
        mem = LIMITS.max_memory_mb * LIMITS.l1_threshold
        with patch("zephyr.governance.drift_detection.resource_guard._get_memory_usage_mb", return_value=mem):
            snap = snapshot()
            assert snap.status == ResourceStatus.WARNING
            assert snap.degradation_level == DegradationLevel.LEVEL_1

    def test_critical_at_l2(self):
        mem = LIMITS.max_memory_mb * LIMITS.l2_threshold
        with patch("zephyr.governance.drift_detection.resource_guard._get_memory_usage_mb", return_value=mem):
            snap = snapshot()
            assert snap.status == ResourceStatus.CRITICAL
            assert snap.degradation_level == DegradationLevel.LEVEL_2

    def test_critical_at_l3(self):
        mem = LIMITS.max_memory_mb * LIMITS.l3_threshold
        with patch("zephyr.governance.drift_detection.resource_guard._get_memory_usage_mb", return_value=mem):
            snap = snapshot()
            assert snap.status == ResourceStatus.CRITICAL
            assert snap.degradation_level == DegradationLevel.LEVEL_3

    def test_oom_at_l4(self):
        mem = LIMITS.max_memory_mb * LIMITS.l4_threshold
        with patch("zephyr.governance.drift_detection.resource_guard._get_memory_usage_mb", return_value=mem):
            snap = snapshot()
            assert snap.status == ResourceStatus.OOM
            assert snap.degradation_level == DegradationLevel.LEVEL_4


class TestApplyDegradation:
    def test_normal_no_change(self):
        snap = ResourceSnapshot(degradation_level=DegradationLevel.NORMAL)
        new_pool, level = apply_degradation(snap, 8)
        assert new_pool == 8
        assert level == DegradationLevel.NORMAL

    def test_level1_halves_pool(self):
        snap = ResourceSnapshot(degradation_level=DegradationLevel.LEVEL_1)
        new_pool, level = apply_degradation(snap, 8)
        assert new_pool == 4
        assert level == DegradationLevel.LEVEL_1

    def test_level2_quarters_pool(self):
        snap = ResourceSnapshot(degradation_level=DegradationLevel.LEVEL_2)
        new_pool, level = apply_degradation(snap, 8)
        assert new_pool == 2

    def test_level3_eighths_pool(self):
        snap = ResourceSnapshot(degradation_level=DegradationLevel.LEVEL_3)
        new_pool, level = apply_degradation(snap, 8)
        assert new_pool == 1

    def test_level4_zero_pool(self):
        snap = ResourceSnapshot(degradation_level=DegradationLevel.LEVEL_4)
        new_pool, level = apply_degradation(snap, 8)
        assert new_pool == 0

    def test_pool_minimum_is_one(self):
        snap = ResourceSnapshot(degradation_level=DegradationLevel.LEVEL_1)
        new_pool, _ = apply_degradation(snap, 1)
        assert new_pool == 1

    def test_level4_calls_critical_handler(self):
        handler = MagicMock()
        set_critical_handler(handler)
        snap = ResourceSnapshot(degradation_level=DegradationLevel.LEVEL_4)
        apply_degradation(snap, 4)
        handler.assert_called_once()
        set_critical_handler(None)


class TestValidateScalability:
    def test_returns_milestones(self):
        results = validate_scalability()
        assert "10" in results
        assert "100" in results
        assert "500" in results
        assert "1500" in results

    def test_within_limit_flag(self):
        results = validate_scalability()
        for key, info in results.items():
            assert "within_limit" in info
            assert "max_est_mem_mb" in info
            assert "recommended_pool" in info


class TestGuardLoopControl:
    def test_stop_guard_loop(self):
        stop_guard_loop()
        assert is_guard_running() is False
