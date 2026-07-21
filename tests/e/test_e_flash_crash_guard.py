# [A_test] module_id: MOD-GOV_e_flash_crash_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_flash_crash_guard
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

from zephyr.governance.financial_governance.flash_crash_guard import FlashCrashGuard


class TestFlashCrashGuardConstants:
    def test_liquidity_threshold(self):
        assert FlashCrashGuard.LIQUIDITY_THRESHOLD == 50.0

    def test_velocity_threshold(self):
        assert FlashCrashGuard.VELOCITY_THRESHOLD == 60.0


class TestFlashCrashGuardInit:
    def test_default_state(self):
        fcg = FlashCrashGuard()
        assert fcg._tripped is False
        assert fcg._trip_time == 0.0
        assert fcg.tripped is False


class TestFlashCrashGuardEvaluate:
    def test_price_drop_below_threshold(self):
        fcg = FlashCrashGuard()
        result = fcg.evaluate(10.0, 5.0, 0.1)
        assert result is False
        assert fcg.tripped is False

    def test_price_drop_exceeds_threshold(self):
        fcg = FlashCrashGuard()
        result = fcg.evaluate(60.0, 5.0, 0.1)
        assert result is True
        assert fcg.tripped is True

    def test_velocity_exceeds_threshold(self):
        fcg = FlashCrashGuard()
        result = fcg.evaluate(10.0, 70.0, 0.1)
        assert result is True
        assert fcg.tripped is True

    def test_both_exceed(self):
        fcg = FlashCrashGuard()
        result = fcg.evaluate(60.0, 70.0, 0.1)
        assert result is True
        assert fcg.tripped is True

    def test_trip_time_set(self):
        fcg = FlashCrashGuard()
        fcg.evaluate(60.0, 5.0, 0.1)
        assert fcg._trip_time > 0


class TestFlashCrashGuardReset:
    def test_reset_clears_trip(self):
        fcg = FlashCrashGuard()
        fcg.evaluate(60.0, 5.0, 0.1)
        assert fcg.tripped is True
        fcg.reset()
        assert fcg.tripped is False
