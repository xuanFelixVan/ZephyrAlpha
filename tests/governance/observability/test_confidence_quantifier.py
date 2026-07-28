# [A_test] module_id: MOD-GOV_confidence_quantifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_confidence_quantifier
# [INVARIANTS] 连续5次低置信→exit37
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.confidence_quantifier import (
    ConfidenceQuantifier,
    ConfidenceResult,
)


class TestConfidenceQuantifierInstantiation:
    def test_creates_instance(self):
        cq = ConfidenceQuantifier()
        assert isinstance(cq, ConfidenceQuantifier)

    def test_initial_state(self):
        cq = ConfidenceQuantifier()
        assert cq.average_confidence == 1.0
        assert cq.consecutive_low == 0
        assert cq.history == []

    def test_class_constants(self):
        assert ConfidenceQuantifier.EXIT_CODE_LOW_CONFIDENCE == 37
        assert ConfidenceQuantifier.LOW_THRESHOLD == 0.30
        assert ConfidenceQuantifier.MAX_CONSECUTIVE_LOW == 5
        assert ConfidenceQuantifier.MAX_TOTAL_LOW == 10


class TestRecord:
    def test_single_high_confidence(self):
        cq = ConfidenceQuantifier()
        result = cq.record("op-1", 0.9)
        assert isinstance(result, ConfidenceResult)
        assert result.average_confidence == 0.9
        assert result.action == "normal"
        assert result.exit_code == 0
        assert result.consecutive_low == 0

    def test_single_low_confidence(self):
        cq = ConfidenceQuantifier()
        result = cq.record("op-1", 0.1)
        assert result.consecutive_low == 1
        assert result.action == "normal"
        assert result.exit_code == 0

    def test_consecutive_low_triggers_reduce_tier(self):
        cq = ConfidenceQuantifier()
        for i in range(5):
            result = cq.record(f"op-{i}", 0.1)
        assert result.consecutive_low == 5
        assert result.action == "REDUCE_TIER"
        assert result.exit_code == 37

    def test_high_confidence_resets_consecutive(self):
        cq = ConfidenceQuantifier()
        for i in range(4):
            cq.record(f"op-{i}", 0.1)
        result = cq.record("op-4", 0.9)
        assert result.consecutive_low == 0
        assert result.action == "normal"

    def test_total_low_triggers_suspend(self):
        cq = ConfidenceQuantifier()
        for i in range(10):
            result = cq.record(f"op-{i}", 0.1)
        assert result.action == "SUSPEND_AGENT"
        assert result.exit_code == 37

    def test_mixed_confidence_no_false_trigger(self):
        cq = ConfidenceQuantifier()
        for i in range(8):
            cq.record(f"op-{i}", 0.1)
        result = cq.record("op-8", 0.9)
        cq.record("op-9", 0.9)
        assert result.consecutive_low == 0
        assert result.action == "normal"

    def test_record_appends_to_history(self):
        cq = ConfidenceQuantifier()
        cq.record("op-1", 0.5)
        cq.record("op-2", 0.7)
        assert len(cq.history) == 2
        assert cq.history[0].operation_id == "op-1"
        assert cq.history[1].operation_id == "op-2"

    def test_empty_operation_id(self):
        cq = ConfidenceQuantifier()
        result = cq.record("", 0.5)
        assert result.average_confidence == 0.5

    def test_boundary_confidence_at_threshold(self):
        cq = ConfidenceQuantifier()
        result = cq.record("op-1", 0.30)
        assert result.consecutive_low == 0
        assert result.action == "normal"

    def test_just_below_threshold(self):
        cq = ConfidenceQuantifier()
        result = cq.record("op-1", 0.29)
        assert result.consecutive_low == 1


class TestDetermineTier:
    def test_tier_1_full_auto(self):
        assert ConfidenceQuantifier.determine_tier(0.80) == "TIER_1_FULL_AUTO"
        assert ConfidenceQuantifier.determine_tier(1.0) == "TIER_1_FULL_AUTO"

    def test_tier_2_auto_with_audit(self):
        assert ConfidenceQuantifier.determine_tier(0.50) == "TIER_2_AUTO_WITH_AUDIT"
        assert ConfidenceQuantifier.determine_tier(0.79) == "TIER_2_AUTO_WITH_AUDIT"

    def test_tier_3_human_review(self):
        assert ConfidenceQuantifier.determine_tier(0.30) == "TIER_3_HUMAN_REVIEW"
        assert ConfidenceQuantifier.determine_tier(0.49) == "TIER_3_HUMAN_REVIEW"

    def test_tier_4_human_only(self):
        assert ConfidenceQuantifier.determine_tier(0.29) == "TIER_4_HUMAN_ONLY"
        assert ConfidenceQuantifier.determine_tier(0.0) == "TIER_4_HUMAN_ONLY"


class TestAverageConfidence:
    def test_empty_history_returns_one(self):
        cq = ConfidenceQuantifier()
        assert cq.average_confidence == 1.0

    def test_single_record(self):
        cq = ConfidenceQuantifier()
        cq.record("op-1", 0.6)
        assert cq.average_confidence == 0.6

    def test_multiple_records(self):
        cq = ConfidenceQuantifier()
        cq.record("op-1", 0.4)
        cq.record("op-2", 0.8)
        assert abs(cq.average_confidence - 0.6) < 1e-9


class TestCurrentTier:
    def test_empty_history_tier_1(self):
        cq = ConfidenceQuantifier()
        assert cq.current_tier == "TIER_1_FULL_AUTO"

    def test_after_records(self):
        cq = ConfidenceQuantifier()
        cq.record("op-1", 0.6)
        cq.record("op-2", 0.6)
        assert cq.current_tier == "TIER_2_AUTO_WITH_AUDIT"
