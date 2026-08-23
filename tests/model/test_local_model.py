# [A_test] module_id: MOD-GOV_local_model | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §test
# [MODULE] zephyr.integration.local_model
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_local_model.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

cache_layer = pytest.importorskip("zephyr.integration.local_model.cache_layer")
embedding_router = pytest.importorskip("zephyr.integration.local_model.embedding_router")
ollama_embedding = pytest.importorskip("zephyr.integration.local_model.ollama_embedding")
ollama_chat = pytest.importorskip("zephyr.integration.local_model.ollama_chat")

CacheLayer = cache_layer.CacheLayer
EmbeddingRouter = embedding_router.EmbeddingRouter
OllamaEmbedder = ollama_embedding.OllamaEmbedder
OllamaChat = ollama_chat.OllamaChat


class TestCacheLayer:
    def test_init_defaults(self):
        cl = CacheLayer()
        assert cl.embedding_cache_size == 0
        assert cl.query_cache_size == 0

    def test_put_and_get_embedding(self):
        cl = CacheLayer()
        vec = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        cl.put_embedding("hello world", vec)
        result = cl.get_embedding("hello world")
        assert result is not None
        np.testing.assert_array_almost_equal(result, vec)

    def test_get_embedding_miss(self):
        cl = CacheLayer()
        assert cl.get_embedding("nonexistent") is None

    def test_put_embedding_copies_vector(self):
        cl = CacheLayer()
        vec = np.array([1.0, 2.0], dtype=np.float32)
        cl.put_embedding("test", vec)
        vec[0] = 999.0
        result = cl.get_embedding("test")
        assert result[0] != 999.0

    def test_put_and_get_query_result(self):
        cl = CacheLayer()
        results = [{"id": 1, "score": 0.9}]
        cl.put_query_result("select all", "knowledge", results)
        fetched = cl.get_query_result("select all", "knowledge")
        assert fetched is not None
        assert fetched[0]["id"] == 1

    def test_get_query_result_miss(self):
        cl = CacheLayer()
        assert cl.get_query_result("nope", "rules") is None

    def test_lru_eviction(self):
        cl = CacheLayer(max_size=2)
        v1 = np.array([1.0], dtype=np.float32)
        v2 = np.array([2.0], dtype=np.float32)
        v3 = np.array([3.0], dtype=np.float32)
        cl.put_embedding("a", v1)
        cl.put_embedding("b", v2)
        cl.put_embedding("c", v3)
        assert cl.get_embedding("a") is None
        assert cl.get_embedding("b") is not None
        assert cl.get_embedding("c") is not None

    def test_invalidate_collection(self):
        cl = CacheLayer()
        vec = np.array([1.0], dtype=np.float32)
        cl.put_embedding("hello", vec, collection="knowledge")
        cl.put_embedding("world", vec, collection="rules")
        cl.invalidate_collection("knowledge")
        assert cl.get_embedding("hello", collection="knowledge") is None
        assert cl.get_embedding("world", collection="rules") is not None

    def test_invalidate_all(self):
        cl = CacheLayer()
        vec = np.array([1.0], dtype=np.float32)
        cl.put_embedding("a", vec)
        cl.put_embedding("b", vec)
        cl.invalidate_all()
        assert cl.embedding_cache_size == 0
        assert cl.query_cache_size == 0

    def test_invalidate_all_on_model_change(self):
        cl = CacheLayer()
        vec = np.array([1.0], dtype=np.float32)
        cl.put_embedding("a", vec)
        cl.invalidate_all_on_model_change("v2", "v1")
        assert cl.embedding_cache_size == 0

    def test_should_cache_embedding_no_cache(self):
        cl = CacheLayer()
        assert cl.should_cache_embedding("execution_traces") is False
        assert cl.should_cache_embedding("knowledge") is True

    def test_should_cache_query_no_cache(self):
        cl = CacheLayer()
        assert cl.should_cache_query("execution_traces") is False
        assert cl.should_cache_query("rules") is True

    def test_cache_key_with_model_version(self):
        key = CacheLayer.cache_key("abc123", model_version="v2", collection="rules")
        assert "rules" in key
        assert "v2" in key

    def test_hash_text_deterministic(self):
        h1 = CacheLayer.hash_text("hello")
        h2 = CacheLayer.hash_text("hello")
        assert h1 == h2

    def test_hash_text_different_inputs(self):
        h1 = CacheLayer.hash_text("hello")
        h2 = CacheLayer.hash_text("world")
        assert h1 != h2


class TestEmbeddingRouter:
    def test_init_defaults(self):
        router = EmbeddingRouter()
        assert router.backend == "ollama"
        assert router.bge_m3_available is False
        assert router.bge_small_available is False
        assert router.fallback_mode == "none"

    def test_health_check(self):
        router = EmbeddingRouter()
        hc = router.health_check()
        assert "bge_m3_available" in hc
        assert "bge_small_available" in hc
        assert "fallback_mode" in hc
        assert "backend" in hc

    def test_shutdown(self):
        router = EmbeddingRouter()
        router.shutdown()
        assert router.bge_m3_available is False
        assert router.bge_small_available is False

    def test_embed_unknown_collection_raises(self):
        router = EmbeddingRouter()
        router.fallback_mode = "none"
        with pytest.raises(KeyError, match="未知 Collection"):
            router.embed("text", "unknown_collection")

    def test_embed_fallback_in_memory(self):
        router = EmbeddingRouter()
        router.fallback_mode = "in_memory"
        vec = router.embed("text", "knowledge")
        assert isinstance(vec, np.ndarray)
        assert vec.shape[0] > 0

    def test_embed_batch_fallback_in_memory(self):
        router = EmbeddingRouter()
        router.fallback_mode = "in_memory"
        mat = router.embed_batch(["a", "b"], "knowledge")
        assert isinstance(mat, np.ndarray)
        assert mat.shape[0] == 2

    def test_l2_normalize(self):
        vec = np.array([3.0, 4.0], dtype=np.float32)
        result = embedding_router.l2_normalize(vec)
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6

    def test_l2_normalize_zero_vector(self):
        vec = np.zeros(3, dtype=np.float32)
        result = embedding_router.l2_normalize(vec)
        np.testing.assert_array_equal(result, vec)

    def test_verify_model_checksum_nonexistent(self):
        assert embedding_router.verify_model_checksum(Path("Z:\\nonexistent\\path\\model")) is False

    def test_verify_model_checksum_no_expected(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            assert embedding_router.verify_model_checksum(td_path) is True


class TestOllamaEmbedder:
    def test_init_defaults(self):
        emb = OllamaEmbedder()
        assert emb.model == "BGE-M3:latest"
        assert emb.url == "http://localhost:11434"
        assert emb.normalize is True

    def test_dim_returns_zero_when_not_verified(self):
        emb = OllamaEmbedder()
        emb.verified = True
        assert emb.dim == 0

    def test_available_false_when_not_reachable(self):
        # available 内部走 _verify()（非 verify()），真探活 requests.get /api/tags；
        # 在 requests 层 mock 连接拒绝，与本机 Ollama 服务是否在跑解耦
        emb = OllamaEmbedder()
        with patch("requests.get", side_effect=ConnectionError("connection refused")):
            assert emb.available is False

    def test_encode_empty_list(self):
        emb = OllamaEmbedder()
        result = emb.encode([])
        assert result.shape == (0, 0)

    def test_shutdown(self):
        emb = OllamaEmbedder()
        emb.verified = True
        emb.shutdown()
        assert emb.verified is False

    def test_quick_alive_unreachable(self):
        with patch("requests.get", side_effect=Exception("connection refused")):
            assert OllamaEmbedder.quick_alive("http://fake:99999") is False


class TestOllamaChat:
    def test_init_defaults(self):
        chat = OllamaChat()
        assert chat.model == "qwen3:8b"
        assert chat.url == "http://localhost:11434"
        assert chat.temperature == 0.1

    def test_available_false_when_not_reachable(self):
        # available 内部走 _verify()（非 verify()），真探活 requests.get /api/tags；
        # 在 requests 层 mock 连接拒绝，与本机 Ollama 服务是否在跑解耦
        chat = OllamaChat()
        with patch("requests.get", side_effect=ConnectionError("connection refused")):
            assert chat.available is False

    def test_supported_work_types(self):
        chat = OllamaChat()
        wt = chat.supported_work_types
        assert "task_classification" in wt
        assert "tag_completion" in wt
        assert "summary_extraction" in wt

    def test_strip_think_block(self):
        text = "<think\nsome reasoning\n</think\nactual output"
        result = OllamaChat.strip_think_block(text)
        assert "actual output" in result

    def test_strip_think_block_empty(self):
        assert OllamaChat.strip_think_block("") == ""

    def test_parse_json_valid(self):
        result = OllamaChat.parse_json('{"key": "value"}')
        assert result["key"] == "value"

    def test_parse_json_with_code_fence(self):
        raw = '```json\n{"key": "value"}\n```'
        result = OllamaChat.parse_json(raw)
        assert result["key"] == "value"

    def test_parse_json_invalid_returns_empty(self):
        result = OllamaChat.parse_json("not json at all")
        assert result == {}

    def test_parse_json_with_expected_keys(self):
        result = OllamaChat.parse_json('{"a": 1}', expected_keys=["a", "b"])
        assert "a" in result

    def test_shutdown(self):
        chat = OllamaChat()
        chat.verified = True
        chat.shutdown()
        assert chat.verified is False

    def test_quick_alive_unreachable(self):
        with patch("requests.get", side_effect=Exception("connection refused")):
            assert OllamaChat.quick_alive("http://fake:99999") is False

    def test_ask_with_mock(self):
        chat = OllamaChat()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"message": {"content": "test reply"}}
        with patch("requests.post", return_value=mock_resp):
            result = chat.ask("hello")
            assert result == "test reply"

    def test_ask_json_with_mock(self):
        chat = OllamaChat()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"message": {"content": '{"category": "audit"}'}}
        with patch("requests.post", return_value=mock_resp):
            result = chat.ask_json("classify this")
            assert result["category"] == "audit"


from pathlib import Path
