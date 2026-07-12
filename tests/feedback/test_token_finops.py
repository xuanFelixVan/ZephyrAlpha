# [A_test] module_id: SRC-TST-1750 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_token_finops
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.token_finops
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_token_finops.py
# [TTL] task_bound


from zephyr.feedback_loop.collectors.token_finops import TokenFinOps


class TestTokenFinOpsInstantiation:
    def test_default_usage_is_empty_dict(self):
        tf = TokenFinOps()
        assert tf.usage == {}

    def test_usage_with_initial_data(self):
        initial = {"llm_gateway": 500, "diagnosis": 300}
        tf = TokenFinOps(usage=initial)
        assert tf.usage == initial


class TestTokenFinOpsTrack:
    def test_track_new_subsystem(self):
        tf = TokenFinOps()
        tf.track("llm_gateway", 100)
        assert tf.usage["llm_gateway"] == 100

    def test_track_accumulates_tokens(self):
        tf = TokenFinOps()
        tf.track("llm_gateway", 100)
        tf.track("llm_gateway", 50)
        tf.track("llm_gateway", 25)
        assert tf.usage["llm_gateway"] == 175

    def test_track_multiple_subsystems(self):
        tf = TokenFinOps()
        tf.track("llm_gateway", 100)
        tf.track("diagnosis", 200)
        tf.track("escalation", 50)
        assert tf.usage["llm_gateway"] == 100
        assert tf.usage["diagnosis"] == 200
        assert tf.usage["escalation"] == 50

    def test_track_does_not_cross_contaminate(self):
        tf = TokenFinOps()
        tf.track("sub_a", 100)
        tf.track("sub_b", 200)
        tf.track("sub_a", 50)
        assert tf.usage["sub_a"] == 150
        assert tf.usage["sub_b"] == 200


class TestTokenFinOpsBoundaries:
    def test_track_zero_tokens(self):
        tf = TokenFinOps()
        tf.track("subsystem", 0)
        assert tf.usage["subsystem"] == 0

    def test_track_large_token_count(self):
        tf = TokenFinOps()
        tf.track("subsystem", 10_000_000)
        assert tf.usage["subsystem"] == 10_000_000

    def test_track_accumulates_from_initial_usage(self):
        tf = TokenFinOps(usage={"llm_gateway": 500})
        tf.track("llm_gateway", 100)
        assert tf.usage["llm_gateway"] == 600
