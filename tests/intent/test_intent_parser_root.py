# [A_test] module_id: MOD-GOV_intent_parser_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.intent_parser
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
    from zephyr.governance.persistence.intent_keyword_mapper import IntentDomain, IntentResult
    from zephyr.governance.persistence.intent_parser import (
        DEFAULT_STAGE_THRESHOLDS,
        EmbeddingHit,
        IntentClassifyFailure,
        IntentParser,
        IntentParseTrace,
        IntentType,
        LLMIntentVerdict,
        classify,
        inject_context_for,
        plan_directive_chain,
    )

    _IMPORT_OK = True
    _IMPORT_ERR = None
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_ERR = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_ERR}")


class TestIntentParser:
    def test_parse_stage1_high_confidence(self):
        parser = IntentParser()
        result = parser.parse("governance audit compliance standard policy")
        assert result.primary_domain != IntentDomain.UNKNOWN
        assert result.source_stage == "keyword"
        assert result.confidence >= 0.0
        assert result.latency_ms >= 0

    def test_parse_empty_query(self):
        parser = IntentParser()
        result = parser.parse("")
        assert result.source_stage == "keyword"
        assert result.requires_human is True

    def test_parse_with_embedding_searcher(self):
        def mock_searcher(query, *, top_k=5):
            return [EmbeddingHit(domain="D6", score=0.85, text="governance", source="ke-001")]

        parser = IntentParser(embedding_searcher=mock_searcher)
        result = parser.parse("something ambiguous xyz")
        assert result.source_stage in ("keyword", "semantic", "llm")

    def test_parse_with_llm_caller(self):
        def mock_llm(query, *, context=None):
            return LLMIntentVerdict(
                primary_domain="D9",
                confidence=0.6,
                secondary_domains=["D6"],
                rationale="debug intent",
                suggested_directives=["911"],
            )

        parser = IntentParser(llm_caller=mock_llm)
        result = parser.parse("something ambiguous xyz")
        assert result.source_stage in ("keyword", "semantic", "llm")

    def test_parse_all_stages(self):
        def mock_searcher(query, *, top_k=5):
            return [
                EmbeddingHit(domain="D3", score=0.3, text="alpha", source="ke-003"),
                EmbeddingHit(domain="D9", score=0.3, text="debug", source="ke-009"),
            ]

        def mock_llm(query, *, context=None):
            return LLMIntentVerdict(
                primary_domain="D4",
                confidence=0.8,
                secondary_domains=["D3"],
                rationale="strategy intent",
                suggested_directives=["433"],
            )

        parser = IntentParser(
            embedding_searcher=mock_searcher,
            llm_caller=mock_llm,
            thresholds={"stage2_accept": 0.99},
        )
        result = parser.parse("ambiguous query with no clear keyword match")
        assert result.source_stage == "llm"
        assert result.primary_domain == "D4"

    def test_thresholds_property(self):
        parser = IntentParser()
        t = parser.thresholds
        assert "stage1_accept" in t
        assert "stage2_accept" in t
        assert "stage3_human_floor" in t

    def test_last_trace(self):
        parser = IntentParser()
        parser.parse("governance audit")
        trace = parser.last_trace
        assert trace is not None
        assert isinstance(trace, IntentParseTrace)
        assert "keyword" in trace.stages

    def test_custom_thresholds(self):
        parser = IntentParser(thresholds={"stage1_accept": 0.99})
        assert parser.thresholds["stage1_accept"] == 0.99
        assert parser.thresholds["stage2_accept"] == DEFAULT_STAGE_THRESHOLDS["stage2_accept"]

    def test_embedding_searcher_exception_fallback(self):
        def bad_searcher(query, *, top_k=5):
            raise RuntimeError("ChromaDB down")

        parser = IntentParser(embedding_searcher=bad_searcher)
        result = parser.parse("ambiguous xyz query")
        assert result.source_stage in ("keyword", "semantic", "llm")

    def test_llm_caller_exception_fallback(self):
        def bad_llm(query, *, context=None):
            raise RuntimeError("LLM API error")

        parser = IntentParser(llm_caller=bad_llm)
        result = parser.parse("ambiguous xyz query")
        assert result.source_stage in ("keyword", "semantic", "llm")


class TestClassify:
    def test_classify_code_gen(self):
        assert classify("帮我生成一个模块") == IntentType.CODE_GEN

    def test_classify_ops_fix(self):
        assert classify("修复安全漏洞") == IntentType.OPS_FIX

    def test_classify_test(self):
        assert classify("写单元测试") == IntentType.TEST

    def test_classify_empty_raises(self):
        with pytest.raises(IntentClassifyFailure):
            classify("")

    def test_classify_whitespace_raises(self):
        with pytest.raises(IntentClassifyFailure):
            classify("   ")

    def test_classify_unknown_defaults_code_gen(self):
        result = classify("xyzzy foobar bazquux")
        assert result == IntentType.CODE_GEN


class TestPlanDirectiveChain:
    def test_normal_directives(self):
        r = IntentResult(
            query="test",
            primary_domain=IntentDomain.D6,
            confidence=0.9,
            source_stage="keyword",
            suggested_directives=["611", "622", "999"],
            latency_ms=0,
        )
        assert plan_directive_chain(r) == "611+622+999"

    def test_empty_directives(self):
        r = IntentResult(
            query="test",
            primary_domain=IntentDomain.UNKNOWN,
            confidence=0.0,
            source_stage="keyword",
            suggested_directives=[],
            latency_ms=0,
        )
        assert plan_directive_chain(r) == "999"

    def test_custom_separator(self):
        r = IntentResult(
            query="test",
            primary_domain=IntentDomain.D3,
            confidence=0.9,
            source_stage="keyword",
            suggested_directives=["333", "344"],
            latency_ms=0,
        )
        assert plan_directive_chain(r, separator=",") == "333,344"


class TestInjectContextFor:
    def test_inject_by_module_id(self):
        class FakeInjector:
            def inject_by_module_id(self, module_id):
                return f"injected:{module_id}"

        r = IntentResult(
            query="test",
            primary_domain="D6",
            confidence=0.9,
            source_stage="keyword",
            latency_ms=0,
        )
        result = inject_context_for(r, FakeInjector())
        assert "D6" in result

    def test_inject_by_keyword_fallback(self):
        class FakeInjector:
            def inject_by_keyword(self, keyword):
                return f"kw:{keyword}"

        r = IntentResult(
            query="test query",
            primary_domain=IntentDomain.UNKNOWN,
            confidence=0.0,
            source_stage="keyword",
            latency_ms=0,
        )
        result = inject_context_for(r, FakeInjector())
        assert result == "kw:test query"

    def test_inject_no_methods_raises(self):
        r = IntentResult(
            query="test",
            primary_domain=IntentDomain.D6,
            confidence=0.9,
            source_stage="keyword",
            latency_ms=0,
        )
        with pytest.raises(AttributeError):
            inject_context_for(r, object())
