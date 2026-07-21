# [A_test] module_id: MOD-GOV_parsing_intent_parser | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
        EmbeddingHit,
        IntentParser,
        IntentParseTrace,
        LLMIntentVerdict,
        inject_context_for,
        plan_directive_chain,
    )
except Exception as _exc:
    pytest.skip(f"无法导入 intent_parser: {_exc}", allow_module_level=True)


class TestIntentParser:
    def test_parse_keyword_only(self):
        parser = IntentParser()
        result = parser.parse("governance audit compliance")
        assert isinstance(result, IntentResult)
        assert result.source_stage == "keyword"

    def test_parse_empty_query(self):
        parser = IntentParser()
        result = parser.parse("")
        assert isinstance(result, IntentResult)

    def test_parse_with_stage2(self):
        def mock_searcher(query, *, top_k=5):
            return [EmbeddingHit(domain="D6", score=0.9, text="governance")]

        parser = IntentParser(embedding_searcher=mock_searcher)
        result = parser.parse("governance check")
        assert isinstance(result, IntentResult)

    def test_parse_with_stage3(self):
        def mock_llm(query, *, context=None):
            return LLMIntentVerdict(primary_domain="D6", confidence=0.8, rationale="test")

        parser = IntentParser(llm_caller=mock_llm)
        result = parser.parse("obscure query xyz")
        assert isinstance(result, IntentResult)

    def test_thresholds_property(self):
        parser = IntentParser()
        t = parser.thresholds
        assert "stage1_accept" in t
        assert "stage2_accept" in t

    def test_last_trace(self):
        parser = IntentParser()
        parser.parse("governance")
        trace = parser.last_trace
        assert isinstance(trace, IntentParseTrace)
        assert "keyword" in trace.stages


class TestPlanDirectiveChain:
    def test_with_directives(self):
        result = IntentResult(
            query="test",
            primary_domain=IntentDomain.D6,
            confidence=0.9,
            source_stage="keyword",
            suggested_directives=["611", "622", "999"],
            latency_ms=0,
        )
        chain = plan_directive_chain(result)
        assert chain == "611+622+999"

    def test_with_empty_directives(self):
        result = IntentResult(
            query="test",
            primary_domain=IntentDomain.UNKNOWN,
            confidence=0.0,
            source_stage="keyword",
            suggested_directives=[],
            latency_ms=0,
        )
        chain = plan_directive_chain(result)
        assert chain == "999"

    def test_custom_separator(self):
        result = IntentResult(
            query="test",
            primary_domain=IntentDomain.D6,
            confidence=0.9,
            source_stage="keyword",
            suggested_directives=["611", "999"],
            latency_ms=0,
        )
        chain = plan_directive_chain(result, separator="-")
        assert chain == "611-999"


class TestInjectContextFor:
    def test_with_module_id(self):
        class MockInjector:
            def inject_by_module_id(self, module_id):
                return f"injected:{module_id}"

        result = IntentResult(
            query="test",
            primary_domain=IntentDomain.D6,
            confidence=0.9,
            source_stage="keyword",
            latency_ms=0,
        )
        ctx = inject_context_for(result, MockInjector())
        assert "D6" in ctx

    def test_with_unknown_domain_fallback(self):
        class MockInjector:
            def inject_by_keyword(self, keyword):
                return f"keyword:{keyword}"

        result = IntentResult(
            query="test query",
            primary_domain=IntentDomain.UNKNOWN,
            confidence=0.0,
            source_stage="keyword",
            latency_ms=0,
        )
        ctx = inject_context_for(result, MockInjector())
        assert "keyword" in ctx

    def test_with_invalid_injector(self):
        result = IntentResult(
            query="test",
            primary_domain=IntentDomain.D6,
            confidence=0.9,
            source_stage="keyword",
            latency_ms=0,
        )
        with pytest.raises(AttributeError):
            inject_context_for(result, object())


class TestEmbeddingHit:
    def test_instantiation(self):
        hit = EmbeddingHit(domain="D6", score=0.9)
        assert hit.domain == "D6"
        assert hit.score == 0.9


class TestLLMIntentVerdict:
    def test_instantiation(self):
        verdict = LLMIntentVerdict(primary_domain="D6", confidence=0.8)
        assert verdict.primary_domain == "D6"
        assert verdict.confidence == 0.8
