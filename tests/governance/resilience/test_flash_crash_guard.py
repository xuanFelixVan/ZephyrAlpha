# [A_test] module_id: MOD-GOV_flash_crash_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_flash_crash_guard
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_flash_crash_guard.py -q
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.financial_governance.flash_crash_guard import FlashCrashGuard


class TestFlashCrashGuardInit:
    def test_default_not_tripped(self):
        guard = FlashCrashGuard()
        assert guard.tripped is False

    def test_threshold_constants(self):
        assert FlashCrashGuard.LIQUIDITY_THRESHOLD == 50.0
        assert FlashCrashGuard.VELOCITY_THRESHOLD == 60.0


class TestEvaluate:
    def test_no_trigger_normal_conditions(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=10.0, velocity_pct_per_s=20.0, bid_ask_spread_pct=1.0) is False
        assert guard.tripped is False

    def test_trigger_on_price_drop(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=55.0, velocity_pct_per_s=10.0, bid_ask_spread_pct=1.0) is True
        assert guard.tripped is True

    def test_trigger_on_velocity(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=10.0, velocity_pct_per_s=65.0, bid_ask_spread_pct=1.0) is True
        assert guard.tripped is True

    def test_trigger_on_both(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=60.0, velocity_pct_per_s=70.0, bid_ask_spread_pct=5.0) is True

    def test_boundary_exact_liquidity_threshold(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=50.0, velocity_pct_per_s=10.0, bid_ask_spread_pct=1.0) is False

    def test_boundary_just_above_liquidity_threshold(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=50.01, velocity_pct_per_s=10.0, bid_ask_spread_pct=1.0) is True

    def test_boundary_exact_velocity_threshold(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=10.0, velocity_pct_per_s=60.0, bid_ask_spread_pct=1.0) is False

    def test_boundary_just_above_velocity_threshold(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=10.0, velocity_pct_per_s=60.01, bid_ask_spread_pct=1.0) is True

    def test_zero_values_no_trigger(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=0.0, velocity_pct_per_s=0.0, bid_ask_spread_pct=0.0) is False

    def test_negative_values_no_trigger(self):
        guard = FlashCrashGuard()
        assert guard.evaluate(price_drop_pct=-10.0, velocity_pct_per_s=-5.0, bid_ask_spread_pct=-1.0) is False


class TestReset:
    def test_reset_clears_tripped(self):
        guard = FlashCrashGuard()
        guard.evaluate(price_drop_pct=55.0, velocity_pct_per_s=10.0, bid_ask_spread_pct=1.0)
        assert guard.tripped is True
        guard.reset()
        assert guard.tripped is False

    def test_reset_allows_retrigger(self):
        guard = FlashCrashGuard()
        guard.evaluate(price_drop_pct=55.0, velocity_pct_per_s=10.0, bid_ask_spread_pct=1.0)
        guard.reset()
        assert guard.evaluate(price_drop_pct=55.0, velocity_pct_per_s=10.0, bid_ask_spread_pct=1.0) is True

    def test_reset_on_untripped_guard_noop(self):
        guard = FlashCrashGuard()
        guard.reset()
        assert guard.tripped is False
