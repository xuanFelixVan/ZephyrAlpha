# [A_test] module_id: SRC-TST-1795 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_vigil_runtime
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_vigil_runtime.py -q
# [TTL] task_bound

import time

from zephyr.gov_drift.vigil_runtime import VigilRuntime


class TestVigilRuntimeInstantiation:
    def test_default_token_budget(self):
        obj = VigilRuntime()
        assert obj._token_budget == 2000

    def test_default_tokens_used_zero(self):
        obj = VigilRuntime()
        assert obj._tokens_used == 0

    def test_default_override_window_closed(self):
        obj = VigilRuntime()
        assert obj._override_window_open is False

    def test_default_override_expiry_zero(self):
        obj = VigilRuntime()
        assert obj._override_expiry == 0.0

    def test_override_active_initially_false(self):
        obj = VigilRuntime()
        assert obj.override_active is False


class TestConsume:
    def test_within_budget_returns_true(self):
        obj = VigilRuntime()
        assert obj.consume(100) is True

    def test_exact_budget_returns_true(self):
        obj = VigilRuntime()
        assert obj.consume(2000) is True

    def test_exceed_budget_returns_false(self):
        obj = VigilRuntime()
        assert obj.consume(2001) is False

    def test_cumulative_within_budget(self):
        obj = VigilRuntime()
        obj.consume(1000)
        assert obj.consume(1000) is True

    def test_cumulative_exceed_budget(self):
        obj = VigilRuntime()
        obj.consume(1000)
        assert obj.consume(1001) is False

    def test_failed_consume_does_not_increment(self):
        obj = VigilRuntime()
        obj.consume(2001)
        assert obj._tokens_used == 0

    def test_remaining_tokens_after_consume(self):
        obj = VigilRuntime()
        obj.consume(500)
        assert obj.remaining_tokens() == 1500


class TestRemainingTokens:
    def test_full_budget_initially(self):
        obj = VigilRuntime()
        assert obj.remaining_tokens() == 2000

    def test_partial_consume(self):
        obj = VigilRuntime()
        obj.consume(300)
        assert obj.remaining_tokens() == 1700

    def test_full_consume(self):
        obj = VigilRuntime()
        obj.consume(2000)
        assert obj.remaining_tokens() == 0


class TestOverrideWindow:
    def test_open_override_sets_active(self):
        obj = VigilRuntime()
        obj.open_override_window(600)
        assert obj.override_active is True

    def test_override_expires(self):
        obj = VigilRuntime()
        obj.open_override_window(0.01)
        time.sleep(0.02)
        assert obj.override_active is False

    def test_default_duration(self):
        obj = VigilRuntime()
        obj.open_override_window()
        assert obj._override_expiry > time.time()

    def test_override_window_open_flag(self):
        obj = VigilRuntime()
        obj.open_override_window(600)
        assert obj._override_window_open is True


class TestConsumeBoundary:
    def test_zero_tokens_consume(self):
        obj = VigilRuntime()
        assert obj.consume(0) is True
        assert obj.remaining_tokens() == 2000

    def test_one_over_budget(self):
        obj = VigilRuntime()
        obj.consume(2000)
        assert obj.consume(1) is False

    def test_negative_tokens_consume(self):
        obj = VigilRuntime()
        result = obj.consume(-1)
        assert obj._tokens_used == -1
        assert result is True
