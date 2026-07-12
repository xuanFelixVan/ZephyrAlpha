# [A_test] module_id: SRC-TST-1562 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_self_modification_rate_limiter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.self_modification_rate_limiter
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_self_modification_rate_limiter.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.self_modification_rate_limiter import (
    SelfModificationRateLimiter,
)


class TestSelfModificationRateLimiterInstantiation:
    def test_default_instantiation(self):
        obj = SelfModificationRateLimiter()
        assert obj is not None
        assert obj.max_burst == 5
        assert obj.refill_rate_per_hour == 10

    def test_custom_params(self):
        obj = SelfModificationRateLimiter(max_burst=3, refill_rate_per_hour=20, blocked_count=0, total_requests=0)
        assert obj.max_burst == 3
        assert obj.refill_rate_per_hour == 20

    def test_is_dataclass(self):
        obj = SelfModificationRateLimiter()
        assert hasattr(obj, "__dataclass_fields__")

    def test_post_init_sets_tokens(self):
        obj = SelfModificationRateLimiter(max_burst=8)
        assert obj.tokens == pytest.approx(8.0)


class TestSelfModificationRateLimiterRequestModification:
    def test_first_request_allowed(self):
        sml = SelfModificationRateLimiter(max_burst=5)
        result = sml.request_modification(change_type="config", severity="low")
        assert result["allowed"] is True
        assert result["tokens_remaining"] == pytest.approx(4.0)

    def test_exhaust_tokens(self):
        sml = SelfModificationRateLimiter(max_burst=2)
        sml.request_modification(change_type="a", severity="low")
        sml.request_modification(change_type="b", severity="low")
        result = sml.request_modification(change_type="c", severity="low")
        assert result["allowed"] is False

    def test_blocked_count_increments(self):
        sml = SelfModificationRateLimiter(max_burst=1)
        sml.request_modification(change_type="a", severity="low")
        sml.request_modification(change_type="b", severity="low")
        assert sml.blocked_count == 1

    def test_total_requests_increments(self):
        sml = SelfModificationRateLimiter(max_burst=5)
        sml.request_modification(change_type="a", severity="low")
        sml.request_modification(change_type="b", severity="low")
        assert sml.total_requests == 2

    def test_result_contains_change_type(self):
        sml = SelfModificationRateLimiter()
        result = sml.request_modification(change_type="prompt", severity="medium")
        assert result["change_type"] == "prompt"


class TestSelfModificationRateLimiterGetStatus:
    def test_initial_status(self):
        sml = SelfModificationRateLimiter(max_burst=5)
        status = sml.get_status()
        assert status["max_burst"] == 5
        assert status["total_blocked"] == 0

    def test_status_after_requests(self):
        sml = SelfModificationRateLimiter(max_burst=5)
        sml.request_modification(change_type="a", severity="low")
        status = sml.get_status()
        assert status["total_modifications_allowed"] == 1

    def test_block_rate_calculation(self):
        sml = SelfModificationRateLimiter(max_burst=1)
        sml.request_modification(change_type="a", severity="low")
        sml.request_modification(change_type="b", severity="low")
        status = sml.get_status()
        assert status["block_rate"] > 0.0


class TestSelfModificationRateLimiterEmergencyOverride:
    def test_override_resets_tokens(self):
        sml = SelfModificationRateLimiter(max_burst=5)
        sml.request_modification(change_type="a", severity="low")
        sml.request_modification(change_type="b", severity="low")
        result = sml.emergency_override()
        assert result["override"] == "activated"
        assert result["tokens_reset"] == 5

    def test_override_resets_blocked_count(self):
        sml = SelfModificationRateLimiter(max_burst=1)
        sml.request_modification(change_type="a", severity="low")
        sml.request_modification(change_type="b", severity="low")
        sml.emergency_override()
        assert sml.blocked_count == 0

    def test_override_allows_new_requests(self):
        sml = SelfModificationRateLimiter(max_burst=1)
        sml.request_modification(change_type="a", severity="low")
        sml.request_modification(change_type="b", severity="low")
        sml.emergency_override()
        result = sml.request_modification(change_type="c", severity="low")
        assert result["allowed"] is True


class TestSelfModificationRateLimiterBoundaries:
    def test_zero_max_burst(self):
        sml = SelfModificationRateLimiter(max_burst=0)
        result = sml.request_modification(change_type="a", severity="low")
        assert result["allowed"] is False

    def test_critical_severity(self):
        sml = SelfModificationRateLimiter(max_burst=5)
        result = sml.request_modification(change_type="a", severity="critical")
        assert result["allowed"] is True
