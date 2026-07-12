# [A_test] module_id: SRC-TST-1735 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_temporal_integrity_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.temporal_integrity_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_temporal_integrity_guard.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.diagnosers.temporal_integrity_guard import (
    TemporalIntegrityGuard,
    TimeAnomaly,
)


class TestTimeAnomaly:
    def test_backward_jump_value(self):
        assert TimeAnomaly.BACKWARD_JUMP.value == "BACKWARD_JUMP"

    def test_forward_jump_value(self):
        assert TimeAnomaly.FORWARD_JUMP.value == "FORWARD_JUMP"

    def test_dst_transition_value(self):
        assert TimeAnomaly.DST_TRANSITION.value == "DST_TRANSITION"

    def test_ntp_drift_value(self):
        assert TimeAnomaly.NTP_DRIFT.value == "NTP_DRIFT"

    def test_stale_timestamp_value(self):
        assert TimeAnomaly.STALE_TIMESTAMP.value == "STALE_TIMESTAMP"

    def test_all_anomalies_count(self):
        assert len(TimeAnomaly) == 6


class TestTemporalIntegrityGuardInstantiation:
    def test_default_params(self):
        tig = TemporalIntegrityGuard()
        assert tig.max_backward_tolerance == 1.0
        assert tig.max_forward_gap == 3600.0
        assert tig.max_ntp_drift_seconds == 5.0
        assert tig.max_timestamp_age == 300.0
        assert tig.last_wall_clock == 0.0
        assert tig.last_monotonic == 0.0
        assert tig.ntp_offset == 0.0
        assert tig.dst_aware is True
        assert tig.time_anomalies == []

    def test_custom_params(self):
        tig = TemporalIntegrityGuard(
            max_backward_tolerance=2.0,
            max_forward_gap=7200.0,
            max_ntp_drift_seconds=10.0,
            max_timestamp_age=600.0,
            dst_aware=False,
        )
        assert tig.max_backward_tolerance == 2.0
        assert tig.max_forward_gap == 7200.0
        assert tig.dst_aware is False


class TestValidateTimestamp:
    def test_first_timestamp_valid(self):
        tig = TemporalIntegrityGuard()
        result = tig.validate_timestamp(time.time())
        assert result["valid"] is True
        assert result["anomalies"] == []

    def test_forward_sequence_valid(self):
        tig = TemporalIntegrityGuard()
        now = time.time()
        tig.validate_timestamp(now)
        result = tig.validate_timestamp(now + 10)
        assert result["valid"] is True

    def test_backward_jump_detected(self):
        tig = TemporalIntegrityGuard(max_backward_tolerance=1.0)
        now = time.time()
        tig.validate_timestamp(now)
        result = tig.validate_timestamp(now - 100)
        assert result["valid"] is False
        anomaly_types = [a["type"] for a in result["anomalies"]]
        assert TimeAnomaly.BACKWARD_JUMP.value in anomaly_types

    def test_stale_timestamp_detected(self):
        tig = TemporalIntegrityGuard(max_timestamp_age=300.0)
        old_ts = time.time() - 600
        result = tig.validate_timestamp(old_ts)
        anomaly_types = [a["type"] for a in result["anomalies"]]
        assert TimeAnomaly.STALE_TIMESTAMP.value in anomaly_types

    def test_recommendation_discard_on_backward(self):
        tig = TemporalIntegrityGuard()
        now = time.time()
        tig.validate_timestamp(now)
        result = tig.validate_timestamp(now - 50)
        assert result["recommendation"] == "discard_data_point"

    def test_recommendation_accept_on_valid(self):
        tig = TemporalIntegrityGuard()
        result = tig.validate_timestamp(time.time())
        assert result["recommendation"] == "accept"

    def test_dst_like_jump_detected(self):
        tig = TemporalIntegrityGuard()
        now = time.time()
        tig.validate_timestamp(now)
        result = tig.validate_timestamp(now - 3600)
        anomaly_types = [a["type"] for a in result["anomalies"]]
        assert TimeAnomaly.DST_TRANSITION.value in anomaly_types


class TestIsDstBoundary:
    def test_returns_bool(self):
        tig = TemporalIntegrityGuard()
        result = tig.is_dst_boundary(time.time())
        assert isinstance(result, bool)

    def test_dst_aware_false_always_false(self):
        tig = TemporalIntegrityGuard(dst_aware=False)
        result = tig.is_dst_boundary(time.time())
        assert result is False


class TestGetTemporalHealth:
    def test_no_anomalies_healthy(self):
        tig = TemporalIntegrityGuard()
        health = tig.get_temporal_health()
        assert health["healthy"] is True
        assert health["anomalies_last_hour"] == 0

    def test_with_anomalies_unhealthy(self):
        tig = TemporalIntegrityGuard()
        now = time.time()
        tig.validate_timestamp(now)
        tig.validate_timestamp(now - 100)
        health = tig.get_temporal_health()
        assert health["total_anomalies"] >= 1

    def test_ntp_offset_in_result(self):
        tig = TemporalIntegrityGuard()
        health = tig.get_temporal_health()
        assert "ntp_offset_estimate" in health


class TestResetHistory:
    def test_clears_anomalies(self):
        tig = TemporalIntegrityGuard()
        now = time.time()
        tig.validate_timestamp(now)
        tig.validate_timestamp(now - 100)
        assert len(tig.time_anomalies) > 0
        tig.reset_history()
        assert tig.time_anomalies == []

    def test_resets_clocks(self):
        tig = TemporalIntegrityGuard()
        tig.validate_timestamp(time.time())
        tig.reset_history()
        assert tig.last_wall_clock == 0.0
        assert tig.last_monotonic == 0.0
