# [A_test] module_id: SRC-TST-0626 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_conversation_tax_detector
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] assess returns TaxAssessment; drift in [0,1]
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.context_governance.conversation_tax_detector import (
    ConversationTaxDetector,
    TaxAssessment,
)


class TestConversationTaxDetector:
    def test_instantiation_defaults(self):
        det = ConversationTaxDetector()
        assert det.last_assessment() is None

    def test_instantiation_custom(self):
        det = ConversationTaxDetector(drift_window=5, decay_threshold=0.8)
        assert det.last_assessment() is None

    def test_record_reply_and_assess(self):
        det = ConversationTaxDetector()
        det.record_reply(output_length=100, cost=0.01)
        assessment = det.assess()
        assert isinstance(assessment, TaxAssessment)
        assert assessment.content_drift == 0.0
        assert assessment.efficiency_decay == 0.0

    def test_assess_with_topic_vectors(self):
        det = ConversationTaxDetector(drift_window=10)
        for i in range(6):
            det.record_reply(output_length=100, cost=0.01, topic_vector=(1.0, 0.0, 0.0))
        for i in range(6):
            det.record_reply(output_length=100, cost=0.01, topic_vector=(0.0, 1.0, 0.0))
        assessment = det.assess()
        assert assessment.content_drift > 0.0

    def test_efficiency_decay(self):
        det = ConversationTaxDetector()
        for _ in range(5):
            det.record_reply(output_length=200, cost=0.01)
        for _ in range(5):
            det.record_reply(output_length=10, cost=0.01)
        assessment = det.assess()
        assert assessment.efficiency_decay > 0.0

    def test_should_summarize_on_drift(self):
        det = ConversationTaxDetector(drift_window=10, decay_threshold=0.3)
        det.record_reply(output_length=100, cost=0.01, topic_vector=(1.0, 0.0))
        det.record_reply(output_length=100, cost=0.01, topic_vector=(0.0, 1.0))
        det.record_reply(output_length=100, cost=0.01, topic_vector=(1.0, 1.0))
        det.record_reply(output_length=100, cost=0.01, topic_vector=(0.5, 0.5))
        assessment = det.assess()
        if assessment.content_drift > 0.5:
            assert assessment.should_summarize is True

    def test_cost_per_meaningful_reply(self):
        det = ConversationTaxDetector()
        det.record_reply(output_length=100, cost=0.5)
        assessment = det.assess()
        assert assessment.cost_per_meaningful_reply > 0.0

    def test_last_assessment_stored(self):
        det = ConversationTaxDetector()
        det.record_reply(output_length=100, cost=0.01)
        det.assess()
        assert det.last_assessment() is not None
        assert isinstance(det.last_assessment(), TaxAssessment)

    def test_reset(self):
        det = ConversationTaxDetector()
        det.record_reply(output_length=100, cost=0.01)
        det.assess()
        det.reset()
        assert det.last_assessment() is None

    def test_meaningful_action_threshold(self):
        det = ConversationTaxDetector()
        det.record_reply(output_length=5, cost=0.01)
        det.record_reply(output_length=5, cost=0.01)
        assessment = det.assess()
        assert assessment.cost_per_meaningful_reply == 0.02

    def test_recommendation_ok(self):
        det = ConversationTaxDetector()
        det.record_reply(output_length=100, cost=0.01)
        assessment = det.assess()
        assert "OK" in assessment.recommendation


class TestBoundaryCases:
    def test_assess_without_replies(self):
        det = ConversationTaxDetector()
        assessment = det.assess()
        assert assessment.content_drift == 0.0
        assert assessment.efficiency_decay == 0.0
        assert assessment.dead_conversation_prob == 0.0

    def test_record_reply_zero_length(self):
        det = ConversationTaxDetector()
        det.record_reply(output_length=0, cost=0.0)
        assessment = det.assess()
        assert isinstance(assessment, TaxAssessment)

    def test_single_reply_no_decay(self):
        det = ConversationTaxDetector()
        det.record_reply(output_length=100, cost=0.01)
        assessment = det.assess()
        assert assessment.efficiency_decay == 0.0
