# [A_test] module_id: MOD-GOV_e_error_budget_burst_limiter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_error_budget_burst_limiter
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

from zephyr.governance.ops_governance.error_budget_burst_limiter import BurstLimiter


class TestBurstLimiterInit:
    def test_default_state(self):
        limiter = BurstLimiter()
        assert limiter.burst_window_s == 60
        assert limiter.max_burst == 10
        assert limiter.requests == []


class TestBurstLimiterAllow:
    def test_first_request_allowed(self):
        limiter = BurstLimiter()
        assert limiter.allow() is True

    def test_requests_up_to_max_burst(self):
        limiter = BurstLimiter()
        for _ in range(10):
            assert limiter.allow() is True

    def test_exceeds_max_burst(self):
        limiter = BurstLimiter()
        for _ in range(10):
            limiter.allow()
        assert limiter.allow() is False

    def test_requests_stored(self):
        limiter = BurstLimiter()
        limiter.allow()
        assert len(limiter.requests) == 1

    def test_requests_capped_at_max_burst(self):
        limiter = BurstLimiter()
        for _ in range(15):
            limiter.allow()
        assert len(limiter.requests) == 10
