# [A_test] module_id: SRC-TST-1710 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_suppression_learner
# [INVARIANTS] SUPPRESSION_THRESHOLD=3;pattern_hash_deterministic;suppress_only_when_active
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_suppression_learner.py
# [TTL] task_bound

import uuid
from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.suppression_learner import (
    SuppressionLearner,
    SuppressionRule,
)


class TestSuppressionRule:
    def test_creation(self):
        now = datetime.now(UTC)
        rule = SuppressionRule(
            rule_id=uuid.uuid4(),
            detector_id="db_schema_drift",
            module_id="MOD-INF-023",
            pattern_hash="abc123",
            drift_dimension="schema",
            false_positive_count=3,
            created_at=now,
            last_false_positive_at=now,
        )
        assert rule.detector_id == "db_schema_drift"
        assert rule.is_active is True
        assert rule.suppressed_count == 0
        assert rule.last_reviewed_at is None

    def test_default_values(self):
        now = datetime.now(UTC)
        rule = SuppressionRule(
            rule_id=uuid.uuid4(),
            detector_id="d",
            module_id="m",
            pattern_hash="h",
            drift_dimension="dim",
            false_positive_count=1,
            created_at=now,
            last_false_positive_at=now,
        )
        assert rule.is_active is True
        assert rule.suppressed_count == 0


class TestComputePatternHash:
    def test_deterministic(self):
        learner = SuppressionLearner()
        h1 = learner.compute_pattern_hash("det", "dim", "sig")
        h2 = learner.compute_pattern_hash("det", "dim", "sig")
        assert h1 == h2

    def test_different_inputs_different_hash(self):
        learner = SuppressionLearner()
        h1 = learner.compute_pattern_hash("det1", "dim", "sig")
        h2 = learner.compute_pattern_hash("det2", "dim", "sig")
        assert h1 != h2

    def test_hash_is_sha256_hex(self):
        learner = SuppressionLearner()
        h = learner.compute_pattern_hash("det", "dim", "sig")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestRecordFalsePositive:
    def test_first_record_returns_none(self):
        learner = SuppressionLearner()
        result = learner.record_false_positive("det", "mod", "dim", "sig")
        assert result is None

    def test_second_record_returns_none(self):
        learner = SuppressionLearner()
        learner.record_false_positive("det", "mod", "dim", "sig")
        result = learner.record_false_positive("det", "mod", "dim", "sig")
        assert result is None

    def test_threshold_creates_active_rule(self):
        learner = SuppressionLearner()
        learner.record_false_positive("det", "mod", "dim", "sig")
        learner.record_false_positive("det", "mod", "dim", "sig")
        learner.record_false_positive("det", "mod", "dim", "sig")
        key = "det:mod:" + learner.compute_pattern_hash("det", "dim", "sig")
        rule = learner._patterns[key]
        assert rule.is_active is True
        assert rule.false_positive_count >= 3

    def test_reactivation_after_deactivation(self):
        learner = SuppressionLearner()
        learner.record_false_positive("det", "mod", "dim", "sig")
        learner.record_false_positive("det", "mod", "dim", "sig")
        learner.record_false_positive("det", "mod", "dim", "sig")
        key = "det:mod:" + learner.compute_pattern_hash("det", "dim", "sig")
        learner._patterns[key].is_active = False
        result = learner.record_false_positive("det", "mod", "dim", "sig")
        assert result is not None
        assert result.is_active is True

    def test_increments_count(self):
        learner = SuppressionLearner()
        learner.record_false_positive("det", "mod", "dim", "sig")
        learner.record_false_positive("det", "mod", "dim", "sig")
        learner.record_false_positive("det", "mod", "dim", "sig")
        learner.record_false_positive("det", "mod", "dim", "sig")
        key = "det:mod:" + learner.compute_pattern_hash("det", "dim", "sig")
        assert learner._patterns[key].false_positive_count == 4


class TestShouldSuppress:
    def test_no_rule_returns_false(self):
        learner = SuppressionLearner()
        assert learner.should_suppress("det", "mod", "dim", "sig") is False

    def test_active_rule_returns_true(self):
        learner = SuppressionLearner()
        for _ in range(3):
            learner.record_false_positive("det", "mod", "dim", "sig")
        assert learner.should_suppress("det", "mod", "dim", "sig") is True

    def test_suppress_increments_counter(self):
        learner = SuppressionLearner()
        for _ in range(3):
            learner.record_false_positive("det", "mod", "dim", "sig")
        learner.should_suppress("det", "mod", "dim", "sig")
        learner.should_suppress("det", "mod", "dim", "sig")
        key = "det:mod:" + learner.compute_pattern_hash("det", "dim", "sig")
        assert learner._patterns[key].suppressed_count == 2


class TestShadowObserve:
    def test_records_observation_for_active_rule(self):
        learner = SuppressionLearner()
        for _ in range(3):
            learner.record_false_positive("det", "mod", "dim", "sig")
        learner.shadow_observe("det", "mod", "dim", "sig")
        key = "det:mod:" + learner.compute_pattern_hash("det", "dim", "sig")
        assert key in learner._shadow_observations
        assert len(learner._shadow_observations[key]) == 1


class TestCheckPatternChange:
    def test_no_change_returns_false(self):
        learner = SuppressionLearner()
        for _ in range(3):
            learner.record_false_positive("det", "mod", "dim", "sig")
        learner.shadow_observe("det", "mod", "dim", "sig")
        assert learner.check_pattern_change("det", "mod", "dim", "sig") is False

    def test_change_deactivates_rule(self):
        learner = SuppressionLearner()
        for _ in range(3):
            learner.record_false_positive("det", "mod", "dim", "sig_A")
        key = "det:mod:" + learner.compute_pattern_hash("det", "dim", "sig_A")
        learner.shadow_observe("det", "mod", "dim", "sig_A")
        learner._shadow_observations[key].append("sig_B")
        result = learner.check_pattern_change("det", "mod", "dim", "sig_A")
        assert result is True
        assert learner._patterns[key].is_active is False


class TestGetRulesNeedingReview:
    def test_no_rules(self):
        learner = SuppressionLearner()
        assert learner.get_rules_needing_review() == []

    def test_recent_rule_not_needing_review(self):
        learner = SuppressionLearner()
        for _ in range(3):
            learner.record_false_positive("det", "mod", "dim", "sig")
        assert learner.get_rules_needing_review() == []

    def test_old_rule_needs_review(self):
        learner = SuppressionLearner()
        for _ in range(3):
            learner.record_false_positive("det", "mod", "dim", "sig")
        key = "det:mod:" + learner.compute_pattern_hash("det", "dim", "sig")
        learner._patterns[key].created_at = datetime.now(UTC) - timedelta(days=31)
        needs = learner.get_rules_needing_review()
        assert len(needs) == 1


class TestMarkReviewed:
    def test_marks_rule_as_reviewed(self):
        learner = SuppressionLearner()
        for _ in range(3):
            learner.record_false_positive("det", "mod", "dim", "sig")
        key = "det:mod:" + learner.compute_pattern_hash("det", "dim", "sig")
        rule = learner._patterns[key]
        learner.mark_reviewed(rule.rule_id)
        assert rule.last_reviewed_at is not None
