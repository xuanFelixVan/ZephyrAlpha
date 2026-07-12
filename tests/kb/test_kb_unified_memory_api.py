# [A_test] module_id: SRC-TST-1179 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_unified_memory_api
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_kb._backend_protocol import (
    InMemoryMemoryBackend,
)
from zephyr.intelligence.model_evaluation.unified_memory_api import (
    DEFAULT_EMBEDDING_MODELS,
    UNIFIED_COLLECTION,
    UnifiedMemoryAPI,
    WriteTrace,
    WriteTraceMissing,
    build_provenance,
    get_unified_memory_api,
    reset_unified_memory_api,
)


class TestWriteTrace:
    def test_create_valid(self):
        wt = WriteTrace(origin="M1:test", audit_chain=["T-001"])
        assert wt.origin == "M1:test"
        assert wt.audit_chain == ["T-001"]
        assert wt.arbitration is None

    def test_create_with_arbitration(self):
        wt = WriteTrace(origin="M3:router", audit_chain=["T-002", "RI-03"], arbitration="R84")
        assert wt.arbitration == "R84"
        assert len(wt.audit_chain) == 2

    def test_frozen_immutable(self):
        wt = WriteTrace(origin="M1:test", audit_chain=["T-001"])
        with pytest.raises(Exception):
            wt.origin = "changed"

    def test_empty_origin_rejected(self):
        with pytest.raises(Exception):
            WriteTrace(origin="", audit_chain=["T-001"])

    def test_empty_audit_chain_rejected(self):
        with pytest.raises(Exception):
            WriteTrace(origin="M1:test", audit_chain=[])

    def test_extra_field_rejected(self):
        with pytest.raises(Exception):
            WriteTrace(origin="M1:test", audit_chain=["T-001"], unknown="bad")


class TestBuildProvenance:
    def test_build_basic(self):
        prov = build_provenance(origin="M1:comp", audit_chain=["T-007"])
        assert isinstance(prov, WriteTrace)
        assert prov.origin == "M1:comp"

    def test_build_with_arbitration(self):
        prov = build_provenance(origin="M4:refl", audit_chain=["RI-02"], arbitration="R84")
        assert prov.arbitration == "R84"


class TestUnifiedMemoryAPI:
    def _make_api(self) -> UnifiedMemoryAPI:
        backend = InMemoryMemoryBackend()
        return UnifiedMemoryAPI(backend=backend, enforce_capability=False)

    def test_write_and_recall(self):
        api = self._make_api()
        prov = build_provenance(origin="test", audit_chain=["T-001"])
        chunk_id = api.write(topic="test_topic", content="hello world", provenance=prov)
        assert chunk_id
        results = api.recall(topic="test_topic", k=5)
        assert len(results) >= 1
        assert results[0].content == "hello world"

    def test_write_empty_topic_raises(self):
        api = self._make_api()
        prov = build_provenance(origin="test", audit_chain=["T-001"])
        with pytest.raises(ValueError, match="topic"):
            api.write(topic="", content="content", provenance=prov)

    def test_write_empty_content_raises(self):
        api = self._make_api()
        prov = build_provenance(origin="test", audit_chain=["T-001"])
        with pytest.raises(ValueError, match="content"):
            api.write(topic="t", content="   ", provenance=prov)

    def test_write_none_provenance_raises(self):
        api = self._make_api()
        with pytest.raises(WriteTraceMissing):
            api.write(topic="t", content="c", provenance=None)

    def test_write_non_writetrace_provenance_raises(self):
        api = self._make_api()
        with pytest.raises(WriteTraceMissing):
            api.write(topic="t", content="c", provenance="not_a_trace")

    def test_write_empty_audit_chain_raises(self):
        wt = WriteTrace.model_construct(origin="x", audit_chain=[], arbitration=None)
        api = self._make_api()
        with pytest.raises(WriteTraceMissing):
            api.write(topic="t", content="c", provenance=wt)

    def test_search_basic(self):
        api = self._make_api()
        prov = build_provenance(origin="test", audit_chain=["T-001"])
        api.write(topic="search_topic", content="python machine learning", provenance=prov)
        results = api.search(query="python", k=5)
        assert isinstance(results, list)

    def test_search_empty_query_returns_empty(self):
        api = self._make_api()
        results = api.search(query="", k=5)
        assert results == []

    def test_recall_empty_topic_returns_empty(self):
        api = self._make_api()
        results = api.recall(topic="", k=5)
        assert results == []

    def test_count(self):
        api = self._make_api()
        prov = build_provenance(origin="test", audit_chain=["T-001"])
        api.write(topic="t1", content="c1", provenance=prov)
        api.write(topic="t2", content="c2", provenance=prov)
        assert api.count() == 2

    def test_backend_property(self):
        backend = InMemoryMemoryBackend()
        api = UnifiedMemoryAPI(backend=backend, enforce_capability=False)
        assert api.backend is backend


class TestSingletonFunctions:
    def setup_method(self):
        reset_unified_memory_api()

    def teardown_method(self):
        reset_unified_memory_api()

    def test_get_unified_memory_api_returns_instance(self):
        backend = InMemoryMemoryBackend()
        api = get_unified_memory_api(backend=backend, enforce_capability=False, reset=True, prefer_vms=False)
        assert isinstance(api, UnifiedMemoryAPI)

    def test_reset_clears_singleton(self):
        backend = InMemoryMemoryBackend()
        api1 = get_unified_memory_api(backend=backend, enforce_capability=False, reset=True, prefer_vms=False)
        reset_unified_memory_api()
        api2 = get_unified_memory_api(
            backend=InMemoryMemoryBackend(), enforce_capability=False, reset=True, prefer_vms=False
        )
        assert api1 is not api2


class TestConstants:
    def test_unified_collection(self):
        assert UNIFIED_COLLECTION == "unified_memory"

    def test_default_embedding_models(self):
        assert isinstance(DEFAULT_EMBEDDING_MODELS, tuple)
        assert len(DEFAULT_EMBEDDING_MODELS) >= 1
