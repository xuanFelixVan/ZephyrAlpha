# [A_test] module_id: SRC-TST-1174 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_reranker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_kb_reranker.py

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.intelligence.model_evaluation.reranker import (
    DEFAULT_RERANK_MODEL,
    DEFAULT_SCORE_THRESHOLD,
    DEFAULT_TOP_K,
    RerankedHit,
    Reranker,
    _fallback_rerank,
    rerank_batch,
)


class TestReranker:
    def test_rerank_empty_documents(self):
        rk = Reranker()
        result = rk.rerank("query", [])
        assert result == []

    def test_rerank_empty_query_falls_back(self):
        rk = Reranker()
        result = rk.rerank("", ["doc1", "doc2"])
        assert len(result) == 2
        assert all(isinstance(h, RerankedHit) for h in result)

    def test_rerank_whitespace_query_falls_back(self):
        rk = Reranker()
        result = rk.rerank("   ", ["doc1"])
        assert len(result) == 1

    def test_rerank_model_unavailable_falls_back(self):
        rk = Reranker()
        rk._load_attempted = True
        rk._model = None
        result = rk.rerank("query", ["doc1", "doc2"])
        assert len(result) == 2
        assert result[0].score == 1.0

    def test_rerank_with_mock_model(self):
        rk = Reranker()
        mock_model = MagicMock()
        mock_model.compute_score.return_value = [0.9, 0.5, 0.1]
        rk._model = mock_model
        rk._load_attempted = True
        result = rk.rerank("query", ["a", "b", "c"])
        assert len(result) == 3
        assert result[0].score >= result[1].score

    def test_rerank_top_k(self):
        rk = Reranker(top_k=2)
        mock_model = MagicMock()
        mock_model.compute_score.return_value = [0.9, 0.5, 0.1]
        rk._model = mock_model
        rk._load_attempted = True
        result = rk.rerank("query", ["a", "b", "c"])
        assert len(result) == 2

    def test_rerank_score_threshold(self):
        rk = Reranker(score_threshold=0.5)
        mock_model = MagicMock()
        mock_model.compute_score.return_value = [0.9, 0.3, 0.1]
        rk._model = mock_model
        rk._load_attempted = True
        result = rk.rerank("query", ["a", "b", "c"])
        assert len(result) == 1
        assert result[0].score >= 0.5

    def test_rerank_model_exception_falls_back(self):
        rk = Reranker()
        mock_model = MagicMock()
        mock_model.compute_score.side_effect = RuntimeError("model error")
        rk._model = mock_model
        rk._load_attempted = True
        result = rk.rerank("query", ["doc1"])
        assert len(result) == 1

    def test_rerank_with_metadatas(self):
        rk = Reranker()
        rk._load_attempted = True
        rk._model = None
        result = rk.rerank("q", ["a", "b"], metadatas=[{"k": "v1"}, {"k": "v2"}])
        assert result[0].metadata == {"k": "v1"}

    def test_available_false_when_no_model(self):
        rk = Reranker()
        rk._load_attempted = True
        rk._model = None
        assert rk.available is False

    def test_top_k_minimum_one(self):
        rk = Reranker(top_k=0)
        assert rk._top_k == 1

    def test_rerank_single_score_scalar(self):
        rk = Reranker()
        mock_model = MagicMock()
        mock_model.compute_score.return_value = 0.8
        rk._model = mock_model
        rk._load_attempted = True
        result = rk.rerank("query", ["single doc"])
        assert len(result) == 1
        assert result[0].score == 0.8


class TestFallbackRerank:
    def test_basic(self):
        result = _fallback_rerank(["a", "b"], None, 5, 0.0)
        assert len(result) == 2
        assert result[0].score == 1.0

    def test_threshold_filter(self):
        result = _fallback_rerank(["a"], None, 5, 2.0)
        assert len(result) == 0

    def test_top_k(self):
        result = _fallback_rerank(["a", "b", "c"], None, 2, 0.0)
        assert len(result) == 2


class TestRerankBatch:
    def test_basic(self):
        with patch.object(
            Reranker,
            "_ensure_model",
            lambda self: setattr(self, "_load_attempted", True) or setattr(self, "_model", None),
        ):
            result = rerank_batch("query", ["doc1", "doc2"], top_k=2)
            assert isinstance(result, list)
            assert len(result) <= 2

    def test_empty(self):
        result = rerank_batch("query", [])
        assert result == []


class TestConstants:
    def test_defaults(self):
        assert DEFAULT_RERANK_MODEL == "BAAI/bge-reranker-v2-m3"
        assert DEFAULT_TOP_K == 5
        assert DEFAULT_SCORE_THRESHOLD == 0.0


class TestRerankedHit:
    def test_creation(self):
        hit = RerankedHit(text="hello", score=0.9, index=0)
        assert hit.text == "hello"
        assert hit.score == 0.9
        assert hit.metadata == {}
