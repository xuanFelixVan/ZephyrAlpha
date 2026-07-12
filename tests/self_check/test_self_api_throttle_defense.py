# [A_test] module_id: SRC-TST-1548 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_self_api_throttle_defense
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.self_api_throttle_defense
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_self_api_throttle_defense.py
# [TTL] task_bound


from zephyr.feedback_loop.resilience.self_api_throttle_defense import (
    SelfAPIThrottleDefense,
    ThrottleState,
)


class TestSelfAPIThrottleDefenseInstantiation:
    def test_default_instantiation(self):
        sat = SelfAPIThrottleDefense()
        assert sat.global_rate_per_second == 10.0
        assert sat.global_burst == 50
        assert sat.per_target_rate_per_second == 2.0
        assert sat.per_target_burst == 10
        assert sat.max_queue_size == 200
        assert sat.throttle_state == ThrottleState.NORMAL
        assert sat.throttled_count == 0

    def test_custom_instantiation(self):
        sat = SelfAPIThrottleDefense(global_rate_per_second=5.0, global_burst=20)
        assert sat.global_rate_per_second == 5.0
        assert sat.global_burst == 20


class TestRequestAction:
    def test_first_request_allowed(self):
        sat = SelfAPIThrottleDefense(global_tokens=10.0)
        sat.target_tokens["svc"] = 10.0
        result = sat.request_action("act-1", "svc")
        assert result["allowed"] is True
        assert result["action_id"] == "act-1"

    def test_low_priority_queued_when_tokens_depleted(self):
        sat = SelfAPIThrottleDefense(global_tokens=0.0, max_queue_size=10)
        sat.target_tokens["svc"] = 0.0
        result = sat.request_action("act-2", "svc", priority=2)
        assert result["allowed"] is False
        assert result["queued"] is True

    def test_high_priority_throttled_when_tokens_depleted(self):
        sat = SelfAPIThrottleDefense(global_tokens=0.0, max_queue_size=10)
        sat.target_tokens["svc"] = 0.0
        result = sat.request_action("act-3", "svc", priority=5)
        assert result["allowed"] is False
        assert result["queued"] is False


class TestDrainQueue:
    def test_drain_dispatches_queued_actions(self):
        sat = SelfAPIThrottleDefense(global_tokens=100.0, max_queue_size=10)
        sat.target_tokens["svc"] = 100.0
        sat.global_tokens = 0.0
        sat.target_tokens["svc"] = 0.0
        sat.request_action("q1", "svc", priority=1)
        sat.global_tokens = 100.0
        sat.target_tokens["svc"] = 100.0
        dispatched = sat.drain_queue(max_drain=5)
        assert "q1" in dispatched

    def test_drain_empty_queue(self):
        sat = SelfAPIThrottleDefense(global_tokens=100.0)
        dispatched = sat.drain_queue()
        assert dispatched == []


class TestGetThrottleStatus:
    def test_status_normal(self):
        sat = SelfAPIThrottleDefense(global_tokens=50.0)
        status = sat.get_throttle_status()
        assert status["state"] == ThrottleState.NORMAL.value
        assert "global_tokens_available" in status

    def test_status_includes_queue_depth(self):
        sat = SelfAPIThrottleDefense(global_tokens=100.0)
        status = sat.get_throttle_status()
        assert "queue_depth" in status


class TestResetCounters:
    def test_reset_clears_throttled_count(self):
        sat = SelfAPIThrottleDefense()
        sat.throttled_count = 42
        sat.throttle_state = ThrottleState.THROTTLING
        sat.reset_counters()
        assert sat.throttled_count == 0
        assert sat.throttle_state == ThrottleState.NORMAL
