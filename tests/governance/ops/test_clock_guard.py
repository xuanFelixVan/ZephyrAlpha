# [A_test] module_id: MOD-GOV_clock_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_clock_guard
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] must test all public classes and methods of clock_guard
# [MODIFY-GUARD] clock_guard.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_clock_guard.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

import time
from unittest.mock import patch

import pytest

from zephyr.governance.ops_governance.clock_guard import ClockGuard


class TestClockGuard:
    def test_instantiation(self):
        guard = ClockGuard()
        assert guard.monotonic_start > 0
        assert guard.wall_start > 0

    def test_detect_drift_near_zero(self):
        guard = ClockGuard()
        drift = guard.detect_drift()
        assert drift < 1.0

    def test_is_suspicious_false_initially(self):
        guard = ClockGuard()
        assert guard.is_suspicious() is False

    def test_is_suspicious_true_with_drift(self):
        guard = ClockGuard()
        with patch(
            "zephyr.governance.ops_governance.clock_guard.time.monotonic", return_value=guard.monotonic_start + 100
        ):
            with patch("zephyr.governance.ops_governance.clock_guard.time.time", return_value=guard.wall_start + 110):
                assert guard.is_suspicious() is True

    def test_detect_drift_with_mock(self):
        guard = ClockGuard()
        with patch(
            "zephyr.governance.ops_governance.clock_guard.time.monotonic", return_value=guard.monotonic_start + 50
        ):
            with patch("zephyr.governance.ops_governance.clock_guard.time.time", return_value=guard.wall_start + 55):
                drift = guard.detect_drift()
                assert drift == pytest.approx(5.0)

    def test_validate_timestamp_current(self):
        guard = ClockGuard()
        assert guard.validate_timestamp(time.time()) is True

    def test_validate_timestamp_recent(self):
        guard = ClockGuard()
        assert guard.validate_timestamp(time.time() - 30) is True

    def test_validate_timestamp_old(self):
        guard = ClockGuard()
        assert guard.validate_timestamp(time.time() - 120) is False

    def test_validate_timestamp_future(self):
        guard = ClockGuard()
        assert guard.validate_timestamp(time.time() + 120) is False

    def test_validate_timestamp_custom_tolerance(self):
        guard = ClockGuard()
        assert guard.validate_timestamp(time.time() - 90, tolerance_s=120) is True
        assert guard.validate_timestamp(time.time() - 90, tolerance_s=60) is False

    def test_validate_timestamp_zero_tolerance(self):
        guard = ClockGuard()
        ts = time.time()
        result = guard.validate_timestamp(ts, tolerance_s=0)
        assert isinstance(result, bool)
