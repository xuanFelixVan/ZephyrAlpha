# [A_test] module_id: SRC-TST-1573 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_semantic_intent_preservation_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.semantic_intent_preservation_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_semantic_intent_preservation_guard.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.semantic_intent_preservation_guard import (
    SemanticIntentPreservationGuard,
)


class TestSemanticIntentPreservationGuardInstantiation:
    def test_default_instantiation(self):
        obj = SemanticIntentPreservationGuard()
        assert obj is not None
        assert obj.drift_threshold == pytest.approx(0.15)
        assert obj.pre_modification_embedding is None
        assert obj.modifications_log == []

    def test_custom_threshold(self):
        obj = SemanticIntentPreservationGuard(drift_threshold=0.3)
        assert obj.drift_threshold == pytest.approx(0.3)

    def test_is_dataclass(self):
        obj = SemanticIntentPreservationGuard()
        assert hasattr(obj, "__dataclass_fields__")


class TestSemanticIntentPreservationGuardSnapshotPreState:
    def test_snapshot_stores_embedding(self):
        guard = SemanticIntentPreservationGuard()
        vec = [0.1, 0.2, 0.3]
        guard.snapshot_pre_state(behavior_vector=vec, intent_hash="abc123")
        assert guard.pre_modification_embedding == [0.1, 0.2, 0.3]
        assert guard.pre_modification_hash == "abc123"

    def test_snapshot_copies_vector(self):
        guard = SemanticIntentPreservationGuard()
        vec = [1.0, 2.0]
        guard.snapshot_pre_state(behavior_vector=vec, intent_hash="h")
        vec[0] = 999.0
        assert guard.pre_modification_embedding[0] == pytest.approx(1.0)


class TestSemanticIntentPreservationGuardVerifyPostState:
    def test_verify_without_baseline(self):
        guard = SemanticIntentPreservationGuard()
        result = guard.verify_post_state(post_vector=[0.1, 0.2], post_hash="x")
        assert result["status"] == "no_baseline"
        assert result["drift_detected"] is False

    def test_verify_identical_vectors(self):
        guard = SemanticIntentPreservationGuard()
        vec = [0.5, 0.5, 0.5]
        guard.snapshot_pre_state(behavior_vector=vec, intent_hash="h1")
        result = guard.verify_post_state(post_vector=vec, post_hash="h2")
        assert result["cosine_similarity"] == pytest.approx(1.0, abs=1e-3)
        assert result["drift_detected"] is False

    def test_verify_opposite_vectors(self):
        guard = SemanticIntentPreservationGuard()
        guard.snapshot_pre_state(behavior_vector=[1.0, 0.0], intent_hash="h1")
        result = guard.verify_post_state(post_vector=[0.0, 1.0], post_hash="h2")
        assert result["cosine_similarity"] == pytest.approx(0.0, abs=1e-3)

    def test_verify_drift_detected(self):
        guard = SemanticIntentPreservationGuard(drift_threshold=0.01)
        guard.snapshot_pre_state(behavior_vector=[1.0, 0.0, 0.0], intent_hash="h1")
        result = guard.verify_post_state(post_vector=[0.0, 1.0, 0.0], post_hash="h2")
        assert result["drift_detected"] is True

    def test_verify_clears_baseline(self):
        guard = SemanticIntentPreservationGuard()
        guard.snapshot_pre_state(behavior_vector=[0.5, 0.5], intent_hash="h1")
        guard.verify_post_state(post_vector=[0.5, 0.5], post_hash="h2")
        assert guard.pre_modification_embedding is None
        assert guard.pre_modification_hash == ""


class TestSemanticIntentPreservationGuardGetDriftHistory:
    def test_empty_history(self):
        guard = SemanticIntentPreservationGuard()
        assert guard.get_drift_history() == []

    def test_history_with_drift(self):
        guard = SemanticIntentPreservationGuard(drift_threshold=0.01)
        guard.snapshot_pre_state(behavior_vector=[1.0, 0.0], intent_hash="h1")
        guard.verify_post_state(post_vector=[0.0, 1.0], post_hash="h2")
        history = guard.get_drift_history()
        assert len(history) == 1

    def test_history_without_drift(self):
        guard = SemanticIntentPreservationGuard(drift_threshold=0.5)
        guard.snapshot_pre_state(behavior_vector=[0.5, 0.5], intent_hash="h1")
        guard.verify_post_state(post_vector=[0.5, 0.5], post_hash="h2")
        history = guard.get_drift_history()
        assert len(history) == 0


class TestSemanticIntentPreservationGuardBoundaries:
    def test_zero_vectors(self):
        guard = SemanticIntentPreservationGuard()
        guard.snapshot_pre_state(behavior_vector=[0.0, 0.0], intent_hash="h1")
        result = guard.verify_post_state(post_vector=[0.0, 0.0], post_hash="h2")
        assert result["cosine_similarity"] == pytest.approx(0.0)

    def test_mismatched_vector_lengths(self):
        guard = SemanticIntentPreservationGuard()
        guard.snapshot_pre_state(behavior_vector=[0.5, 0.5], intent_hash="h1")
        result = guard.verify_post_state(post_vector=[0.5, 0.5, 0.5], post_hash="h2")
        assert result["cosine_similarity"] == pytest.approx(0.0)

    def test_empty_vectors(self):
        guard = SemanticIntentPreservationGuard()
        guard.snapshot_pre_state(behavior_vector=[], intent_hash="h1")
        result = guard.verify_post_state(post_vector=[], post_hash="h2")
        assert result["status"] == "no_baseline"

    def test_max_log_size(self):
        guard = SemanticIntentPreservationGuard(drift_threshold=0.01, max_log_size=3)
        for i in range(5):
            guard.snapshot_pre_state(behavior_vector=[1.0, 0.0], intent_hash="h1")
            guard.verify_post_state(post_vector=[0.0, 1.0], post_hash="h2")
        assert len(guard.modifications_log) <= 3
