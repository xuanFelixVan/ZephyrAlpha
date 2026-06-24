# [A_test] module_id: SRC-TST-1295 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.monotonic_clock
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
import sys

sys.path.insert(0, "src")

import time

import pytest

try:
    from zephyr.security.access_control.monotonic_clock import MonotonicClock
except Exception as _exc:
    pytest.skip(f"Cannot import monotonic_clock: {_exc}", allow_module_level=True)


class TestMonotonicClock:
    def test_now_returns_positive(self):
        clock = MonotonicClock()
        t = clock.now()
        assert t >= 0

    def test_now_advances(self):
        clock = MonotonicClock()
        t1 = clock.now()
        time.sleep(0.05)
        t2 = clock.now()
        assert t2 >= t1

    def test_verify_valid_timestamp(self):
        clock = MonotonicClock()
        result = clock.verify(time.time())
        assert result["valid"] is True

    def test_verify_backward_drift(self):
        clock = MonotonicClock()
        clock.verify(time.time())
        result = clock.verify(time.time() - 100)
        assert result["valid"] is False
        assert result["reason"] == "clock_drift_backward"

    def test_verify_drift_violation_counter(self):
        clock = MonotonicClock()
        clock.verify(time.time())
        clock.verify(time.time() - 100)
        assert clock._drift_violations == 1

    def test_verify_within_tolerance(self):
        clock = MonotonicClock()
        now = time.time()
        clock.verify(now)
        result = clock.verify(now - 5, tolerance_seconds=10.0)
        assert result["valid"] is True

    def test_verify_outside_tolerance(self):
        clock = MonotonicClock()
        now = time.time()
        clock.verify(now)
        result = clock.verify(now - 20, tolerance_seconds=10.0)
        assert result["valid"] is False

    def test_initial_last_wall_time_zero(self):
        clock = MonotonicClock()
        assert clock._last_wall_time == 0.0

    def test_verify_updates_last_wall_time(self):
        clock = MonotonicClock()
        ts = time.time()
        clock.verify(ts)
        assert clock._last_wall_time == ts
