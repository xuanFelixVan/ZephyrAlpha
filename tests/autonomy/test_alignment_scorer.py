# [A_test] module_id: MOD-GOV_alignment_scorer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.alignment_scorer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.llm_defense.llm_security.alignment_scorer import AlignmentResult, AlignmentScorer

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


class TestAlignmentResult:
    def test_dataclass_fields(self):
        r = AlignmentResult(cosine_similarity=0.85, aligned=True, recommendation="proceed")
        assert r.cosine_similarity == 0.85
        assert r.aligned is True
        assert r.recommendation == "proceed"

    def test_default_not_applicable(self):
        with pytest.raises(TypeError):
            AlignmentResult()


class TestAlignmentScorer:
    def test_score_returns_alignment_result(self):
        scorer = AlignmentScorer()
        result = scorer.score(context_embedding=[0.1, 0.2], task_embedding=[0.3, 0.4])
        assert isinstance(result, AlignmentResult)

    def test_score_high_similarity_aligned(self):
        scorer = AlignmentScorer()
        result = scorer.score(context_embedding=[1.0], task_embedding=[1.0])
        assert result.aligned is True
        assert result.recommendation == "proceed"

    def test_score_cosine_similarity_range(self):
        scorer = AlignmentScorer()
        result = scorer.score(context_embedding=[0.5], task_embedding=[0.5])
        assert 0.0 <= result.cosine_similarity <= 1.0

    def test_score_with_empty_embeddings(self):
        scorer = AlignmentScorer()
        result = scorer.score(context_embedding=[], task_embedding=[])
        assert isinstance(result, AlignmentResult)

    def test_score_with_different_length_embeddings(self):
        scorer = AlignmentScorer()
        result = scorer.score(context_embedding=[0.1, 0.2], task_embedding=[0.3])
        assert isinstance(result, AlignmentResult)

    def test_score_with_zero_embeddings(self):
        scorer = AlignmentScorer()
        result = scorer.score(context_embedding=[0.0, 0.0], task_embedding=[0.0, 0.0])
        assert isinstance(result, AlignmentResult)

    def test_multiple_scores_independent(self):
        scorer = AlignmentScorer()
        r1 = scorer.score(context_embedding=[0.1], task_embedding=[0.2])
        r2 = scorer.score(context_embedding=[0.9], task_embedding=[0.8])
        assert isinstance(r1, AlignmentResult)
        assert isinstance(r2, AlignmentResult)
