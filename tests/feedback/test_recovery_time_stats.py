# [A_test] module_id: SRC-TST-1435 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_recovery_time_stats
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.recovery_time_stats
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_recovery_time_stats.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.recovery_time_stats import RecoveryTimeStats


class TestRecoveryTimeStatsInstantiation:
    def test_default_instantiation(self):
        rts = RecoveryTimeStats()
        assert rts.alpha == 0.2
        assert rts.mttr_warning_multiplier == 2.0
        assert rts.global_ewma_mttr == 0.0
        assert rts.per_component == {}

    def test_custom_alpha(self):
        rts = RecoveryTimeStats(alpha=0.5)
        assert rts.alpha == 0.5


class TestRecordIncident:
    def test_record_first_incident(self):
        rts = RecoveryTimeStats()
        result = rts.record_incident("db", started_at=0.0, resolved_at=10.0)
        assert result["component"] == "db"
        assert result["recovery_time"] == 10.0
        assert result["ewma"] == 10.0
        assert result["degraded"] is False

    def test_record_multiple_incidents_same_component(self):
        rts = RecoveryTimeStats(alpha=0.5)
        rts.record_incident("db", started_at=0.0, resolved_at=10.0)
        result = rts.record_incident("db", started_at=100.0, resolved_at=120.0)
        assert result["recovery_time"] == 20.0
        assert result["ewma"] == pytest.approx(15.0)

    def test_record_multiple_components(self):
        rts = RecoveryTimeStats()
        rts.record_incident("db", started_at=0.0, resolved_at=5.0)
        rts.record_incident("cache", started_at=0.0, resolved_at=2.0)
        assert "db" in rts.per_component
        assert "cache" in rts.per_component

    def test_zero_recovery_time(self):
        rts = RecoveryTimeStats()
        result = rts.record_incident("svc", started_at=10.0, resolved_at=10.0)
        assert result["recovery_time"] == 0.0

    def test_negative_duration_clamped_to_zero(self):
        rts = RecoveryTimeStats()
        result = rts.record_incident("svc", started_at=20.0, resolved_at=10.0)
        assert result["recovery_time"] == 0.0

    def test_degraded_flag_after_many_incidents(self):
        rts = RecoveryTimeStats(alpha=0.3, mttr_warning_multiplier=2.0)
        for i in range(6):
            rts.record_incident("db", started_at=float(i), resolved_at=float(i) + 1.0)
        result = rts.record_incident("db", started_at=100.0, resolved_at=200.0)
        assert result["degraded"] is True


class TestGetGlobalMttr:
    def test_initial_global_mttr_is_zero(self):
        rts = RecoveryTimeStats()
        assert rts.get_global_mttr() == 0.0

    def test_global_mttr_updates_after_incident(self):
        rts = RecoveryTimeStats(alpha=0.5)
        rts.record_incident("db", started_at=0.0, resolved_at=10.0)
        assert rts.get_global_mttr() == pytest.approx(5.0)

    def test_global_mttr_ewma_converges(self):
        rts = RecoveryTimeStats(alpha=0.5)
        for _ in range(20):
            rts.record_incident("db", started_at=0.0, resolved_at=5.0)
        assert rts.get_global_mttr() == pytest.approx(5.0, abs=0.1)


class TestRecoveryTimeStatsBoundaries:
    def test_none_component_accepted_by_dict(self):
        rts = RecoveryTimeStats()
        rts.record_incident(None, started_at=0.0, resolved_at=1.0)
        assert None in rts.per_component

    def test_none_timestamps_raise(self):
        rts = RecoveryTimeStats()
        with pytest.raises(TypeError):
            rts.record_incident("db", started_at=None, resolved_at=1.0)
