# [A_test] module_id: SRC-TST-0754 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_disk_guard
# [INVARIANTS] DISK_THRESHOLD_PCT=5.0; check returns (bool, str); should_enter_readonly inverses check[0]
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] total_gb=0 returns (False, msg); no division by zero
# [TESTS] test_disk_guard.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.fault_tolerance.disk_guard import DISK_THRESHOLD_PCT, DiskGuard


class TestDiskThresholdConstant:
    def test_threshold_value(self):
        assert DISK_THRESHOLD_PCT == 5.0


class TestDiskGuard:
    @pytest.fixture()
    def guard(self):
        return DiskGuard()

    def test_check_sufficient_space(self, guard):
        ok, msg = guard.check(50.0, 100.0)
        assert ok is True
        assert msg == "OK"

    def test_check_low_space(self, guard):
        ok, msg = guard.check(3.0, 100.0)
        assert ok is False
        assert "3.0%" in msg
        assert f"{DISK_THRESHOLD_PCT}%" in msg

    def test_check_exact_threshold(self, guard):
        ok, msg = guard.check(5.0, 100.0)
        assert ok is True
        assert msg == "OK"

    def test_check_just_below_threshold(self, guard):
        ok, msg = guard.check(4.99, 100.0)
        assert ok is False

    def test_check_zero_total(self, guard):
        ok, msg = guard.check(0.0, 0.0)
        assert ok is False

    def test_check_full_disk(self, guard):
        ok, msg = guard.check(0.0, 100.0)
        assert ok is False

    def test_check_tiny_free(self, guard):
        ok, msg = guard.check(0.01, 100.0)
        assert ok is False

    def test_should_enter_readonly_true(self, guard):
        assert guard.should_enter_readonly(3.0, 100.0) is True

    def test_should_enter_readonly_false(self, guard):
        assert guard.should_enter_readonly(50.0, 100.0) is False

    def test_should_enter_readonly_zero_total(self, guard):
        assert guard.should_enter_readonly(0.0, 0.0) is True

    def test_check_inverses_readonly(self, guard):
        ok, _ = guard.check(3.0, 100.0)
        assert guard.should_enter_readonly(3.0, 100.0) is not ok

    def test_check_large_disk(self, guard):
        ok, msg = guard.check(500.0, 1000.0)
        assert ok is True

    def test_check_message_format_low_space(self, guard):
        _, msg = guard.check(2.5, 100.0)
        assert "磁盘剩余" in msg
