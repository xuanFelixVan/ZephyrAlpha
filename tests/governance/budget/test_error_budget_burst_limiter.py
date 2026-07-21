# [A_test] module_id: MOD-GOV_error_budget_burst_limiter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_error_budget_burst_limiter
# [INVARIANTS] Error Budget Burst限制不可绕过;daily≤20%/hourly≤5%
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_error_budget_burst_limiter.py
# [TTL] task_bound

import time

from zephyr.governance.ops_governance.error_budget_burst_limiter import BurstLimiter


class TestBurstLimiterInstantiation:
    def test_instantiation(self):
        bl = BurstLimiter()
        assert bl is not None

    def test_initial_requests_empty(self):
        bl = BurstLimiter()
        assert bl._requests == []

    def test_max_burst_default(self):
        bl = BurstLimiter()
        assert bl._max_burst == 10

    def test_burst_window_default(self):
        bl = BurstLimiter()
        assert bl._burst_window_s == 60


class TestBurstLimiterAllow:
    def test_first_request_allowed(self):
        bl = BurstLimiter()
        assert bl.allow() is True

    def test_up_to_max_burst_allowed(self):
        bl = BurstLimiter()
        for _ in range(10):
            assert bl.allow() is True

    def test_exceeds_max_burst_rejected(self):
        bl = BurstLimiter()
        for _ in range(10):
            bl.allow()
        assert bl.allow() is False

    def test_repeated_rejection_after_burst(self):
        bl = BurstLimiter()
        for _ in range(10):
            bl.allow()
        assert bl.allow() is False
        assert bl.allow() is False

    def test_requests_tracked(self):
        bl = BurstLimiter()
        bl.allow()
        bl.allow()
        assert len(bl._requests) == 2

    def test_window_expiry_allows_again(self):
        bl = BurstLimiter()
        bl._burst_window_s = 0
        for _ in range(10):
            bl.allow()
        assert bl.allow() is True

    def test_partial_window_expiry(self):
        bl = BurstLimiter()
        bl._burst_window_s = 1
        for _ in range(10):
            bl.allow()
        assert bl.allow() is False
        time.sleep(1.1)
        assert bl.allow() is True
