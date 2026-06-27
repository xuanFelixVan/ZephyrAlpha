# [A_test] module_id: SRC-TST-1781 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §test
# [MODULE] zephyr.knowledge.vector_memory
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_vector_memory.py
# [TTL] task_bound

import pytest

vms_errors = pytest.importorskip("zephyr.knowledge.vector_memory.vms_errors", reason="vms_errors not available")
VMSError = vms_errors.VMSError
DesignPrincipleError = vms_errors.DesignPrincipleError
ProvenanceMissingError = vms_errors.ProvenanceMissingError
DimensionError = vms_errors.DimensionError
ChunkStrategyError = vms_errors.ChunkStrategyError
TTLError = vms_errors.TTLError
HotColdSeparationError = vms_errors.HotColdSeparationError

vms_schemas = pytest.importorskip("zephyr.knowledge.vector_memory.vms_schemas", reason="vms_schemas not available")
Provenance = vms_schemas.Provenance
ScoredHit = vms_schemas.ScoredHit
RetrievalTrace = vms_schemas.RetrievalTrace
HealthReport = vms_schemas.HealthReport
Chunk = vms_schemas.Chunk
WriteTrace = vms_schemas.WriteTrace
CollectionMetadata = vms_schemas.CollectionMetadata

fake_vms_mod = pytest.importorskip(
    "zephyr.knowledge.vector_memory.in_memory_fake_vms", reason="in_memory_fake_vms not available"
)
InMemoryFakeVMS = fake_vms_mod.InMemoryFakeVMS


class TestVMSErrors:
    def test_vms_error_is_exception(self):
        assert issubclass(VMSError, Exception)

    def test_vms_error_can_be_raised(self):
        with pytest.raises(VMSError, match="test error"):
            raise VMSError("test error")

    def test_design_principle_error_inherits_vms_error(self):
        assert issubclass(DesignPrincipleError, VMSError)

    def test_provenance_missing_error_inherits_vms_error(self):
        assert issubclass(ProvenanceMissingError, VMSError)

    def test_dimension_error_inherits_design_principle(self):
        assert issubclass(DimensionError, DesignPrincipleError)

    def test_chunk_strategy_error_inherits_design_principle(self):
        assert issubclass(ChunkStrategyError, DesignPrincipleError)

    def test_ttl_error_inherits_design_principle(self):
        assert issubclass(TTLError, DesignPrincipleError)

    def test_hot_cold_separation_error_inherits_design_principle(self):
        assert issubclass(HotColdSeparationError, DesignPrincipleError)

    def test_catch_vms_error_catches_subclasses(self):
        with pytest.raises(VMSError):
            raise DimensionError("bad dimension")

    def test_catch_design_principle_catches_subclasses(self):
        with pytest.raises(DesignPrincipleError):
            raise TTLError("expired")

    def test_all_in___all__(self):
        expected = {
            "VMSError",
            "DesignPrincipleError",
            "ProvenanceMissingError",
            "DimensionError",
            "ChunkStrategyError",
            "TTLError",
            "HotColdSeparationError",
        }
        assert set(vms_errors.__all__) == expected


class TestProvenance:
    def test_defaults(self):
        p = Provenance()
        assert p.origin == ""
        assert p.audit_chain == []
        assert p.arbitration == ""

    def test_custom_values(self):
        p = Provenance(origin="test_origin", audit_chain=["a", "b"], arbitration="auto")
        assert p.origin == "test_origin"
        assert len(p.audit_chain) == 2
        assert p.arbitration == "auto"


class TestScoredHit:
    def test_defaults(self):
        hit = ScoredHit()
        assert hit.content == ""
        assert hit.score == 0.0
        assert hit.score_breakdown == {}
        assert hit.metadata == {}
        assert hit.provenance is None
        assert hit.partial is False

    def test_custom_values(self):
        prov = Provenance(origin="test")
        hit = ScoredHit(content="hello", score=0.95, why_top="best match", provenance=prov)
        assert hit.content == "hello"
        assert hit.score == 0.95
        assert hit.why_top == "best match"
        assert hit.provenance.origin == "test"


class TestRetrievalTrace:
    def test_defaults(self):
        rt = RetrievalTrace()
        assert rt.query == ""
        assert rt.hits == []
        assert rt.source_collection == ""

    def test_with_hits(self):
        hit = ScoredHit(content="result", score=0.9)
        rt = RetrievalTrace(query="test query", hits=[hit], source_collection="decisions")
        assert len(rt.hits) == 1
        assert rt.hits[0].content == "result"


class TestHealthReport:
    def test_defaults(self):
        hr = HealthReport()
        assert hr.collection_name == ""
        assert hr.status == "unknown"
        assert hr.issue_count == 0
        assert hr.recommendations == []

    def test_custom(self):
        hr = HealthReport(collection_name="decisions", status="healthy", issue_count=0)
        assert hr.collection_name == "decisions"
        assert hr.status == "healthy"


class TestChunk:
    def test_defaults(self):
        c = Chunk()
        assert c.text == ""
        assert c.start_pos == 0
        assert c.end_pos == 0
        assert c.overlap_with_prev is False
        assert c.overlap_with_next is False

    def test_custom(self):
        c = Chunk(text="some code", start_pos=10, end_pos=50, overlap_with_prev=True)
        assert c.text == "some code"
        assert c.start_pos == 10
        assert c.overlap_with_prev is True


class TestWriteTrace:
    def test_defaults(self):
        wt = WriteTrace()
        assert wt.origin == ""
        assert wt.audit_chain == []
        assert wt.content_hash == ""

    def test_custom(self):
        wt = WriteTrace(origin="agent", content_hash="abc123", timestamp="2026-01-01T00:00:00Z")
        assert wt.origin == "agent"
        assert wt.content_hash == "abc123"


class TestCollectionMetadata:
    def test_defaults(self):
        cm = CollectionMetadata()
        assert cm.name == ""
        assert cm.dimension == 0
        assert cm.embedding_model == ""
        assert cm.chunk_strategy == ""
        assert cm.ttl_days == 0

    def test_custom(self):
        cm = CollectionMetadata(name="decisions", dimension=1024, embedding_model="BAAI/bge-m3")
        assert cm.name == "decisions"
        assert cm.dimension == 1024


class TestInMemoryFakeVMS:
    def test_init(self):
        vms = InMemoryFakeVMS()
        assert vms.started is True

    def test_start(self):
        vms = InMemoryFakeVMS()
        vms.shutdown()
        assert vms.started is False
        vms.start()
        assert vms.started is True

    def test_shutdown(self):
        vms = InMemoryFakeVMS()
        vms.write("decisions", "test content")
        vms.shutdown()
        assert vms.started is False

    def test_write_returns_id(self):
        vms = InMemoryFakeVMS()
        doc_id = vms.write("decisions", "test content")
        assert isinstance(doc_id, str)
        assert "decisions" in doc_id

    def test_write_invalid_collection_raises(self):
        vms = InMemoryFakeVMS()
        with pytest.raises(KeyError):
            vms.write("nonexistent_collection", "test")

    def test_write_with_metadata(self):
        vms = InMemoryFakeVMS()
        doc_id = vms.write("decisions", "test content", metadata={"key": "value"})
        assert isinstance(doc_id, str)

    def test_search_finds_match(self):
        vms = InMemoryFakeVMS()
        vms.write("decisions", "alpha signal detected")
        results = vms.search("decisions", "alpha")
        assert len(results) >= 1
        assert "alpha" in results[0]["content"].lower()

    def test_search_no_match(self):
        vms = InMemoryFakeVMS()
        vms.write("decisions", "alpha signal")
        results = vms.search("decisions", "xyz_not_found")
        assert len(results) == 0

    def test_search_respects_k(self):
        vms = InMemoryFakeVMS()
        vms.write("decisions", "alpha one")
        vms.write("decisions", "alpha two")
        vms.write("decisions", "alpha three")
        results = vms.search("decisions", "alpha", k=2)
        assert len(results) <= 2

    def test_search_empty_collection(self):
        vms = InMemoryFakeVMS()
        results = vms.search("decisions", "anything")
        assert len(results) == 0

    def test_recall_returns_recent(self):
        vms = InMemoryFakeVMS()
        vms.write("decisions", "first item")
        vms.write("decisions", "second item")
        results = vms.recall("decisions", k=1)
        assert len(results) == 1

    def test_health_check(self):
        vms = InMemoryFakeVMS()
        health = vms.health_check()
        assert health["status"] == "healthy"
        assert health["mode"] == "fake"
        assert "stored" in health

    def test_collection_names_class_var(self):
        assert len(InMemoryFakeVMS.COLLECTION_NAMES) > 0
        assert "decisions" in InMemoryFakeVMS.COLLECTION_NAMES
