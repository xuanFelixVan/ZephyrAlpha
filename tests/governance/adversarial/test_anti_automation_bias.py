# [A_test] module_id: SRC-TST-0319 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_anti_automation_bias
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_anti_automation_bias.py -q
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.anti_automation_bias import (
    AntiAutomationBias,
    AntiSycophancyFilter,
    FatigueLevel,
    OversightAction,
    ReviewDecision,
)


class TestAntiAutomationBiasInit:
    def test_default_forced_review_ratio(self):
        ab = AntiAutomationBias()
        assert ab.forced_review_ratio == 0.05

    def test_custom_forced_review_ratio(self):
        ab = AntiAutomationBias(forced_review_ratio=0.10)
        assert ab.forced_review_ratio == 0.10

    def test_initial_fatigue_level_is_normal(self):
        ab = AntiAutomationBias()
        assert ab.fatigue_level == FatigueLevel.NORMAL


class TestForcedReviewRatioSetter:
    def test_clamps_below_minimum(self):
        ab = AntiAutomationBias()
        ab.forced_review_ratio = 0.001
        assert ab.forced_review_ratio == 0.01

    def test_clamps_above_maximum(self):
        ab = AntiAutomationBias()
        ab.forced_review_ratio = 0.50
        assert ab.forced_review_ratio == 0.20

    def test_valid_value_accepted(self):
        ab = AntiAutomationBias()
        ab.forced_review_ratio = 0.15
        assert ab.forced_review_ratio == 0.15


class TestEvaluate:
    def test_non_autonomous_returns_pass(self):
        ab = AntiAutomationBias()
        result = ab.evaluate("op-1", is_autonomous=False)
        assert result.action == OversightAction.PASS

    def test_autonomous_increments_count(self):
        ab = AntiAutomationBias(forced_review_ratio=0.0)
        ab.evaluate("op-1", is_autonomous=True)
        ab.evaluate("op-2", is_autonomous=True)
        monitoring = ab.get_review_monitoring()
        assert monitoring["total_autonomous_ops"] == 2

    def test_fatigued_level_blocks(self):
        ab = AntiAutomationBias()
        ab.fatigue_level = FatigueLevel.FATIGUED
        result = ab.evaluate("op-1", is_autonomous=True)
        assert result.action == OversightAction.BLOCK_AND_NOTIFY

    def test_elevated_level_forces_review(self):
        ab = AntiAutomationBias()
        ab.fatigue_level = FatigueLevel.ELEVATED
        result = ab.evaluate("op-1", is_autonomous=True)
        assert result.action == OversightAction.FORCE_REVIEW
        assert result.forced_review is True

    def test_mechanical_confirmation_forces_review(self):
        ab = AntiAutomationBias(forced_review_ratio=0.0)
        ab.consecutive_confirms = 10
        result = ab.evaluate("op-1", is_autonomous=True)
        assert result.action == OversightAction.FORCE_REVIEW
        assert "Mechanical confirmation" in result.reason


class TestRecordReview:
    def test_confirmed_safe_increments_consecutive(self):
        ab = AntiAutomationBias()
        ab.record_review("op-1", ReviewDecision.CONFIRMED_SAFE, response_time_s=2.0)
        assert ab.consecutive_confirms == 1

    def test_overridden_resets_consecutive(self):
        ab = AntiAutomationBias()
        ab.consecutive_confirms = 5
        ab.record_review("op-1", ReviewDecision.OVERRIDDEN, response_time_s=1.0)
        assert ab.consecutive_confirms == 0

    def test_timed_out_does_not_update_consecutive(self):
        ab = AntiAutomationBias()
        ab.consecutive_confirms = 3
        ab.record_review("op-1", ReviewDecision.TIMED_OUT, response_time_s=30.0)
        assert ab.consecutive_confirms == 3

    def test_response_times_capped_at_20(self):
        ab = AntiAutomationBias()
        for i in range(25):
            ab.record_review(f"op-{i}", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        assert len(ab.last_response_times) <= 20


class TestRecordAuditFeedback:
    def test_record_updates_was_safe_in_audit(self):
        ab = AntiAutomationBias()
        ab.record_review("op-1", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        ab.record_audit_feedback("op-1", actually_unsafe=True)
        for rec in ab.review_records:
            if rec.operation_id == "op-1":
                assert rec.was_safe_in_audit is False

    def test_record_safe_feedback(self):
        ab = AntiAutomationBias()
        ab.record_review("op-1", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        ab.record_audit_feedback("op-1", actually_unsafe=False)
        for rec in ab.review_records:
            if rec.operation_id == "op-1":
                assert rec.was_safe_in_audit is True


class TestEvaluateReviewQuality:
    def test_no_reviews_returns_none_miss_rate(self):
        ab = AntiAutomationBias()
        result = ab.evaluate_review_quality()
        assert result["miss_rate"] is None
        assert result["total_reviewed"] == 0

    def test_with_audit_feedback(self):
        ab = AntiAutomationBias()
        ab.record_review("op-1", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        ab.record_review("op-2", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        ab.record_audit_feedback("op-1", actually_unsafe=True)
        ab.record_audit_feedback("op-2", actually_unsafe=False)
        result = ab.evaluate_review_quality()
        assert result["miss_rate"] == 0.5
        assert result["total_reviewed"] == 2
        assert result["misses"] == 1


class TestProbeSycophancy:
    def test_consistent_decisions(self):
        ab = AntiAutomationBias()
        probe = ab.probe_sycophancy("content", "framing-a", "framing-b", "allow", "allow")
        assert probe.consistent is True
        assert probe.original_decision == "allow"
        assert probe.alternate_decision == "allow"

    def test_inconsistent_decisions(self):
        ab = AntiAutomationBias()
        probe = ab.probe_sycophancy("content", "framing-a", "framing-b", "allow", "block")
        assert probe.consistent is False

    def test_sycophancy_rate_calculation(self):
        ab = AntiAutomationBias()
        ab.probe_sycophancy("c1", "f1", "f2", "allow", "allow")
        ab.probe_sycophancy("c2", "f1", "f2", "allow", "block")
        assert ab.get_sycophancy_rate() == 0.5

    def test_empty_sycophancy_rate_is_zero(self):
        ab = AntiAutomationBias()
        assert ab.get_sycophancy_rate() == 0.0


class TestGetReviewMonitoring:
    def test_returns_expected_keys(self):
        ab = AntiAutomationBias()
        monitoring = ab.get_review_monitoring()
        expected_keys = [
            "confirmation_rate",
            "avg_response_time_s",
            "response_time_trend",
            "consecutive_confirms",
            "fatigue_level",
            "review_quality",
            "sycophancy_rate",
            "total_autonomous_ops",
            "total_reviews_triggered",
        ]
        for key in expected_keys:
            assert key in monitoring

    def test_summary_delegates_to_monitoring(self):
        ab = AntiAutomationBias()
        assert ab.summary() == ab.get_review_monitoring()


class TestAntiSycophancyFilterStripIdentity:
    def test_strips_identity_keys(self):
        metadata = {
            "actor_name": "Alice",
            "actor_role": "admin",
            "operation": "delete",
            "session_id": "sess-1",
        }
        result = AntiSycophancyFilter.strip_identity(metadata)
        assert "actor_name" not in result
        assert "actor_role" not in result
        assert "session_id" not in result
        assert "operation" in result

    def test_preserves_non_identity_keys(self):
        metadata = {"operation": "delete", "target": "/data"}
        result = AntiSycophancyFilter.strip_identity(metadata)
        assert result == {"operation": "delete", "target": "/data"}


class TestAntiSycophancyFilterDetectEmotionalMarkers:
    def test_detects_urgent(self):
        markers = AntiSycophancyFilter.detect_emotional_markers("This is urgent, please help")
        assert "urgent" in markers
        assert "please" in markers

    def test_no_markers_in_neutral_text(self):
        markers = AntiSycophancyFilter.detect_emotional_markers("Delete file /tmp/cache")
        assert markers == []

    def test_detects_harmless(self):
        markers = AntiSycophancyFilter.detect_emotional_markers("It's harmless, don't worry")
        assert "harmless" in markers
        assert "don't worry" in markers


class TestAntiSycophancyFilterNormalizeFraming:
    def test_replaces_emotional_markers(self):
        result = AntiSycophancyFilter.normalize_framing("This is urgent and critical")
        assert "[FILTERED]" in result
        assert "urgent" not in result.lower() or "[FILTERED]" in result

    def test_neutral_text_unchanged(self):
        text = "Delete the temporary file"
        result = AntiSycophancyFilter.normalize_framing(text)
        assert result == text


class TestAntiSycophancyFilterVerifyConsistency:
    def test_consistent_decisions(self):
        probes = AntiSycophancyFilter.verify_consistency("content", ["variant-a", "variant-b"], lambda x: "allow")
        assert len(probes) == 2
        assert all(p.consistent for p in probes)

    def test_inconsistent_decisions(self):
        call_count = 0

        def decision_fn(content: str) -> str:
            nonlocal call_count
            call_count += 1
            return "allow" if call_count == 1 else "block"

        probes = AntiSycophancyFilter.verify_consistency("content", ["variant-a"], decision_fn)
        assert len(probes) == 1
        assert probes[0].consistent is False


class TestFatigueLevelUpdate:
    def test_fatigue_triggered_by_slow_responses(self):
        ab = AntiAutomationBias()
        for i in range(10):
            ab.record_review(f"op-fast-{i}", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        for i in range(10):
            ab.record_review(f"op-slow-{i}", ReviewDecision.CONFIRMED_SAFE, response_time_s=5.0)
        assert ab.fatigue_level in (FatigueLevel.ELEVATED, FatigueLevel.FATIGUED)

    def test_normal_fatigue_with_mixed_decisions(self):
        ab = AntiAutomationBias()
        for i in range(14):
            ab.record_review(f"op-safe-{i}", ReviewDecision.CONFIRMED_SAFE, response_time_s=2.0)
        for i in range(6):
            ab.record_review(f"op-over-{i}", ReviewDecision.OVERRIDDEN, response_time_s=2.0)
        assert ab.fatigue_level == FatigueLevel.NORMAL


class TestBoundary:
    def test_zero_review_ratio(self):
        ab = AntiAutomationBias(forced_review_ratio=0.01)
        ab.forced_review_ratio = 0.0
        assert ab.forced_review_ratio == 0.01

    def test_very_high_review_ratio(self):
        ab = AntiAutomationBias()
        ab.forced_review_ratio = 1.0
        assert ab.forced_review_ratio == 0.20

    def test_many_reviews_tracked(self):
        ab = AntiAutomationBias()
        for i in range(100):
            ab.record_review(f"op-{i}", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        assert len(ab.review_records) == 100
