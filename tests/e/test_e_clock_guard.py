# [A_test] module_id: MOD-GOV_e_clock_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_clock_guard
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.governance.ops_governance.clock_guard import ClockGuard


class TestClockGuardInit:
    def test_attributes_exist(self):
        cg = ClockGuard()
        assert hasattr(cg, "_monotonic_start")
        assert hasattr(cg, "_wall_start")
        assert isinstance(cg.monotonic_start, float)
        assert isinstance(cg.wall_start, float)


class TestDetectDrift:
    def test_returns_nonnegative_float(self):
        cg = ClockGuard()
        drift = cg.detect_drift()
        assert isinstance(drift, float)
        assert drift >= 0.0

    def test_fresh_instance_drift_is_small(self):
        cg = ClockGuard()
        drift = cg.detect_drift()
        assert drift < 1.0

    def test_drift_grows_with_sleep(self):
        cg = ClockGuard()
        d1 = cg.detect_drift()
        time.sleep(0.5)
        d2 = cg.detect_drift()
        assert d2 > d1


class TestIsSuspicious:
    def test_fresh_instance_not_suspicious(self):
        cg = ClockGuard()
        assert cg.is_suspicious() is False


class TestValidateTimestamp:
    def test_current_time_valid(self):
        cg = ClockGuard()
        assert cg.validate_timestamp(time.time()) is True

    def test_old_timestamp_invalid(self):
        cg = ClockGuard()
        old = time.time() - 120.0
        assert cg.validate_timestamp(old) is False

    def test_custom_tolerance(self):
        cg = ClockGuard()
        ts = time.time() - 3.0
        assert cg.validate_timestamp(ts, tolerance_s=5.0) is True
        assert cg.validate_timestamp(ts, tolerance_s=2.0) is False

    def test_future_timestamp_invalid(self):
        cg = ClockGuard()
        future = time.time() + 120.0
        assert cg.validate_timestamp(future) is False
