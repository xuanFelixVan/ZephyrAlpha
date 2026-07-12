# [A_test] module_id: SRC-TST-1803 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_wireheading_prevention
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.security.wireheading_prevention
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_wireheading_prevention.py
# [TTL] task_bound


from zephyr.feedback_loop.security.wireheading_prevention import (
    WireheadingPrevention,
    WireheadState,
)


class TestWireheadingPreventionInstantiation:
    def test_default_instantiation(self):
        wp = WireheadingPrevention()
        assert wp.immutable_metrics == {}
        assert wp.modification_attempts == []
        assert wp.state == WireheadState.CLEAN
        assert wp.safe_mode_until == 0.0


class TestRegisterMetric:
    def test_register_returns_signature(self):
        wp = WireheadingPrevention()
        sig = wp.register_metric("error_rate", "errors / total_requests")
        assert isinstance(sig, str)
        assert len(sig) == 32

    def test_register_stores_hash(self):
        wp = WireheadingPrevention()
        wp.register_metric("error_rate", "errors / total_requests")
        assert "error_rate" in wp.immutable_metrics


class TestVerifyMetric:
    def test_verify_matching_definition(self):
        wp = WireheadingPrevention()
        wp.register_metric("error_rate", "errors / total_requests")
        assert wp.verify_metric("error_rate", "errors / total_requests") is True

    def test_verify_tampered_definition(self):
        wp = WireheadingPrevention()
        wp.register_metric("error_rate", "errors / total_requests")
        result = wp.verify_metric("error_rate", "errors / (total_requests - skipped)")
        assert result is False
        assert wp.state == WireheadState.ATTEMPT_DETECTED

    def test_verify_unknown_metric_passes(self):
        wp = WireheadingPrevention()
        assert wp.verify_metric("new_metric", "any definition") is True

    def test_three_attempts_trigger_safe_mode(self):
        wp = WireheadingPrevention()
        wp.register_metric("m1", "def1")
        wp.verify_metric("m1", "tampered1")
        wp.verify_metric("m1", "tampered2")
        wp.verify_metric("m1", "tampered3")
        assert wp.state == WireheadState.ATTEMPT_DETECTED
        assert wp.safe_mode_until > 0

    def test_safe_mode_blocks_all_verifications(self):
        wp = WireheadingPrevention()
        wp.register_metric("m1", "def1")
        wp.state = WireheadState.SAFE_MODE
        assert wp.verify_metric("m1", "def1") is False


class TestOwnerOverrideReset:
    def test_reset_clears_state(self):
        wp = WireheadingPrevention()
        wp.state = WireheadState.SAFE_MODE
        wp.modification_attempts.append({"test": True})
        wp.owner_override_reset()
        assert wp.state == WireheadState.CLEAN
        assert wp.modification_attempts == []

    def test_reset_allows_verification_again(self):
        wp = WireheadingPrevention()
        wp.register_metric("m1", "def1")
        wp.verify_metric("m1", "tampered")
        wp.owner_override_reset()
        assert wp.verify_metric("m1", "def1") is True
