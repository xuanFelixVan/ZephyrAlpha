# [A_test] module_id: MOD-GOV_vector_memory | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-708 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.vector_memory.test_vector_memory
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
vector-memory 模块单元测试 — MOD-INF-011
===========================================
覆盖: CollectionManager / EmbeddingRouter / HybridRetriever
      BridgeLayer / CacheLayer / DesignPrinciplesEnforcer
      InMemoryMemoryBackend / ChunkStrategyRouter / RetrievalFeedback
"""

import numpy as np
import pytest


class TestCollectionManager:
    def test_list_collections_returns_8(self):
        from zephyr.integration.vector_memory.collection_manager import CollectionManager

        cm = CollectionManager()
        assert len(cm.VMS_COLLECTION_NAMES) == 8
        assert "decisions" in cm.VMS_COLLECTION_NAMES
        assert "execution_traces" in cm.VMS_COLLECTION_NAMES

    def test_collection_names_tuple(self):
        from zephyr.integration.vector_memory.collection_schemas import COLLECTION_NAMES

        assert isinstance(COLLECTION_NAMES, tuple)
        assert len(COLLECTION_NAMES) == 8

    def test_schemas_have_required_fields(self):
        from zephyr.integration.vector_memory.collection_schemas import COLLECTION_SCHEMAS

        for name, schema in COLLECTION_SCHEMAS.items():
            assert "dimension" in schema, f"{name} missing dimension"
            assert "chunk_strategy" in schema, f"{name} missing chunk_strategy"
            assert "ttl_days" in schema, f"{name} missing ttl_days"
            assert "ai_autonomy_level" in schema, f"{name} missing ai_autonomy_level"
            assert "embedding_model" in schema, f"{name} missing embedding_model"
            assert "hnsw:space" in schema, f"{name} missing hnsw:space"
            assert schema["dimension"] in (512, 1024), f"{name} invalid dim: {schema['dimension']}"


class TestDesignPrinciplesEnforcer:
    def test_validate_dimension_whitelist(self):
        from zephyr.integration.vector_memory.design_principles import DesignPrinciplesEnforcer
        from zephyr.integration.vector_memory.vms_errors import DimensionError

        DesignPrinciplesEnforcer.validate_dimension(512)
        DesignPrinciplesEnforcer.validate_dimension(1024)
        with pytest.raises(DimensionError):
            DesignPrinciplesEnforcer.validate_dimension(768)

    def test_validate_provenance_missing(self):
        from zephyr.integration.vector_memory.design_principles import DesignPrinciplesEnforcer
        from zephyr.integration.vector_memory.vms_errors import ProvenanceMissingError

        with pytest.raises(ProvenanceMissingError):
            DesignPrinciplesEnforcer.validate_provenance(None)

        with pytest.raises(ProvenanceMissingError):
            DesignPrinciplesEnforcer.validate_provenance({"other": "field"})

    def test_validate_provenance_ok(self):
        from zephyr.integration.vector_memory.design_principles import DesignPrinciplesEnforcer

        DesignPrinciplesEnforcer.validate_provenance(
            {"origin": "test", "audit_chain": ["test"], "arbitration": "owner"}
        )
        DesignPrinciplesEnforcer.validate_provenance(
            {"provenance": {"origin": "test", "audit_chain": ["test"], "arbitration": "owner"}}
        )


class TestEmbeddingRouter:
    def test_router_collections(self):
        from zephyr.integration.local_model.embedding_router import BGE_M3_COLLECTIONS, BGE_SMALL_COLLECTIONS

        assert "decisions" in BGE_M3_COLLECTIONS
        assert "rules" in BGE_M3_COLLECTIONS
        assert "blueprints" in BGE_SMALL_COLLECTIONS
        assert "session_snapshots" in BGE_SMALL_COLLECTIONS
        assert len(BGE_M3_COLLECTIONS) == 5
        assert len(BGE_SMALL_COLLECTIONS) == 3

    def test_l2_normalize(self):
        from zephyr.integration.local_model.embedding_router import l2_normalize

        v = np.array([3.0, 4.0], dtype=np.float32)
        normed = l2_normalize(v)
        np.testing.assert_almost_equal(np.linalg.norm(normed), 1.0)

    def test_l2_normalize_zero_vector(self):
        from zephyr.integration.local_model.embedding_router import l2_normalize

        v = np.zeros(10, dtype=np.float32)
        normed = l2_normalize(v)
        np.testing.assert_array_equal(normed, v)

    def test_health_check_structure(self):
        from zephyr.integration.local_model.embedding_router import EmbeddingRouter

        router = EmbeddingRouter()
        status = router.health_check()
        assert "bge_m3_available" in status
        assert "bge_small_available" in status
        assert "fallback_mode" in status


class TestHybridRetriever:
    def test_bm25_tokenize(self):
        from zephyr.integration.vector_memory.bm25_index import BM25Index

        tokens = BM25Index.tokenize("Hello World 你好世界 test_123")
        assert "hello" in tokens
        assert "你好世界" in tokens
        assert "test_123" in tokens

    def test_bm25_index_and_search(self):
        from zephyr.integration.vector_memory.bm25_index import BM25Index

        bm25 = BM25Index()
        docs = [
            {"id": "1", "content": "Python is a programming language"},
            {"id": "2", "content": "Java is also a programming language"},
            {"id": "3", "content": "Machine learning with Python"},
        ]
        bm25.index(docs)
        results = bm25.search("Python programming", k=2)
        assert len(results) > 0
        assert results[0][0] in ("1", "3")

    def test_rrf_constant(self):
        from zephyr.integration.vector_memory.hybrid_retriever import RRF_K

        assert RRF_K == 60


class TestBridgeLayer:
    def test_migration_map(self):
        from zephyr.integration.vector_memory.bridge_layer import MIGRATION_MAP

        assert "ke_entries" in MIGRATION_MAP
        assert MIGRATION_MAP["ke_entries"]["target"] == "knowledge"
        assert "vibe_rules" in MIGRATION_MAP
        assert MIGRATION_MAP["vibe_rules"]["target"] == "rules"

    def test_topic_to_collection(self):
        from zephyr.integration.vector_memory.bridge_layer import TOPIC_TO_COLLECTION

        assert TOPIC_TO_COLLECTION.get("knowledge") == "knowledge"
        assert TOPIC_TO_COLLECTION.get("rule") == "rules"
        assert TOPIC_TO_COLLECTION.get("blueprint") == "blueprints"


class TestCacheLayer:
    def test_put_and_get_embedding(self):
        from zephyr.integration.vector_memory.cache_layer import CacheLayer

        cache = CacheLayer(max_size=10)
        vec = np.array([0.1, 0.2], dtype=np.float32)
        cache.put_embedding("hello", vec)
        cached = cache.get_embedding("hello")
        assert cached is not None
        np.testing.assert_array_almost_equal(cached, vec)

    def test_cache_miss(self):
        from zephyr.integration.vector_memory.cache_layer import CacheLayer

        cache = CacheLayer()
        assert cache.get_embedding("nonexistent") is None

    def test_invalidate_collection_only_affects_target(self):
        from zephyr.integration.vector_memory.cache_layer import CacheLayer

        cache = CacheLayer(max_size=100)
        vec = np.array([0.1, 0.2], dtype=np.float32)
        cache.put_embedding("hello", vec, collection="decisions")
        cache.put_embedding("world", vec, collection="rules")
        cache.put_query_result("q1", "decisions", [{"id": "1"}])
        cache.put_query_result("q2", "rules", [{"id": "2"}])

        cache.invalidate_collection("decisions")

        assert cache.get_embedding("hello", collection="decisions") is None
        assert cache.get_embedding("world", collection="rules") is not None
        assert cache.get_query_result("q1", "decisions") is None
        assert cache.get_query_result("q2", "rules") is not None


class TestChunkStrategyRouter:
    def test_valid_strategies(self):
        from zephyr.integration.vector_memory.chunk_strategy_router import ChunkStrategyRouter

        assert len(ChunkStrategyRouter.VALID_STRATEGIES) == 8

    def test_route_rule_level(self):
        from zephyr.integration.vector_memory.chunk_strategy_router import ChunkStrategyRouter

        router = ChunkStrategyRouter()
        chunks = router.route("This is a rule", "rule_level")
        assert len(chunks) == 1
        assert chunks[0].strategy == "rule_level"


class TestInMemoryBackend:
    def test_degraded_mode(self):
        from zephyr.integration.vector_memory.in_memory_memory_backend import InMemoryMemoryBackend

        backend = InMemoryMemoryBackend()
        assert backend.degraded is True

    def test_write_and_recall(self):
        from zephyr.integration.vector_memory.in_memory_memory_backend import InMemoryMemoryBackend

        backend = InMemoryMemoryBackend()
        doc_id = backend.write("test content", {"origin": "test"})
        assert doc_id.startswith("im::")

        results = backend.recall(k=5)
        assert len(results) == 1
        assert results[0]["degraded"] is True


class TestRetrievalFeedback:
    def test_log_feedback(self):
        from zephyr.integration.vector_memory.retrieval_feedback import RetrievalFeedback

        fb = RetrievalFeedback()
        trace = type("Trace", (), {"collection": "decisions", "query": "test", "hits": [1, 2, 3]})()
        entry = fb.log_feedback(trace, user_rating=4.0)
        assert entry.collection == "decisions"
        assert entry.hit_count == 3

    def test_hit_rates(self):
        from zephyr.integration.vector_memory.retrieval_feedback import RetrievalFeedback

        fb = RetrievalFeedback()
        trace = type("Trace", (), {"collection": "knowledge", "query": "q", "hits": [1]})()
        fb.log_feedback(trace)
        rates = fb.track_hit_rates()
        assert "knowledge" in rates
        assert rates["knowledge"]["hit_rate"] == 1.0
