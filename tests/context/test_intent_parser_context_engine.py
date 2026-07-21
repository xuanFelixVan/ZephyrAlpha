# [A_test] module_id: MOD-GOV_intent_parser_context_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-470 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_intent_parser
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for intent_parser.py (T-3-20, A26, V-09)
====================================================
覆盖：三阶段级联（keyword / semantic / llm），置信度门禁，降级链路，
与 DOSLauncher / ContextInjector 的集成辅助函数。

最少测试：15 条。
"""


from typing import Any

import pytest

from zephyr.governance.persistence.intent_keyword_mapper import IntentKeywordMapper, IntentResult
from zephyr.governance.persistence.intent_parser import (
    DEFAULT_STAGE_THRESHOLDS,
    EmbeddingHit,
    IntentParser,
    LLMIntentVerdict,
    inject_context_for,
    plan_directive_chain,
)

# ---------------------------------------------------------------------------
# 辅助 mock
# ---------------------------------------------------------------------------


class FakeEmbedding:
    def __init__(self, hits: list[EmbeddingHit]) -> None:
        self.hits = hits
        self.called_with: list[str] = []

    def __call__(self, query: str, *, top_k: int = 5) -> list[EmbeddingHit]:
        self.called_with.append(query)
        return self.hits[:top_k]


class FailingEmbedding:
    def __call__(self, query: str, *, top_k: int = 5) -> list[EmbeddingHit]:
        raise RuntimeError("chroma down")


class FakeLLM:
    def __init__(self, verdict: LLMIntentVerdict) -> None:
        self.verdict = verdict
        self.called_with: list[str] = []

    def __call__(self, query: str, *, context: dict[str, Any] | None = None) -> LLMIntentVerdict:
        self.called_with.append(query)
        return self.verdict


class FailingLLM:
    def __call__(self, query: str, *, context: dict[str, Any] | None = None) -> LLMIntentVerdict:
        raise RuntimeError("llm 5xx")


# ---------------------------------------------------------------------------
# Stage 1 直通
# ---------------------------------------------------------------------------


class TestStage1Direct:
    def test_high_confidence_keyword_short_circuits_to_stage1(self) -> None:
        """自定义 keyword 表使得 "foo" → confidence=1.0，直接命中 Stage 1。"""
        mapper = IntentKeywordMapper(keywords={"D6": ["foo"]})
        emb = FakeEmbedding([])
        llm = FakeLLM(LLMIntentVerdict(primary_domain="D0", confidence=0.9))
        parser = IntentParser(mapper, embedding_searcher=emb, llm_caller=llm)
        result = parser.parse("foo")
        assert result.source_stage == "keyword"
        assert result.primary_domain == "D6"
        assert emb.called_with == []  # Stage 2 未调用
        assert llm.called_with == []

    def test_stage1_unknown_descends_to_stage2(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D6": ["foo"]})
        emb = FakeEmbedding([EmbeddingHit(domain="D3", score=0.9, text="momentum")])
        parser = IntentParser(mapper, embedding_searcher=emb)
        result = parser.parse("bar baz xyzzy")
        assert result.source_stage == "semantic"
        assert result.primary_domain == "D3"
        assert emb.called_with == ["bar baz xyzzy"]


# ---------------------------------------------------------------------------
# Stage 2 语义
# ---------------------------------------------------------------------------


class TestStage2Semantic:
    def test_semantic_accepts_over_threshold(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nonexistent-kw"]})
        emb = FakeEmbedding(
            [
                EmbeddingHit(domain="D3", score=0.9, text="alpha factor"),
                EmbeddingHit(domain="D3", score=0.8, text="momentum"),
                EmbeddingHit(domain="D4", score=0.3, text="strategy"),
            ]
        )
        parser = IntentParser(mapper, embedding_searcher=emb)
        result = parser.parse("unknown query for factor research")
        assert result.source_stage == "semantic"
        assert result.primary_domain == "D3"
        assert result.confidence >= 0.7

    def test_semantic_below_threshold_falls_to_llm(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nonexistent"]})
        # 三个域平分，confidence 约 1/3
        emb = FakeEmbedding(
            [
                EmbeddingHit(domain="D1", score=0.5),
                EmbeddingHit(domain="D2", score=0.5),
                EmbeddingHit(domain="D3", score=0.5),
            ]
        )
        llm = FakeLLM(LLMIntentVerdict(primary_domain="D2", confidence=0.8))
        parser = IntentParser(mapper, embedding_searcher=emb, llm_caller=llm)
        result = parser.parse("truly ambiguous text")
        assert result.source_stage == "llm"
        assert result.primary_domain == "D2"

    def test_semantic_no_hits_falls_to_llm(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nonexistent"]})
        emb = FakeEmbedding([])
        llm = FakeLLM(LLMIntentVerdict(primary_domain="D5", confidence=0.5))
        parser = IntentParser(mapper, embedding_searcher=emb, llm_caller=llm)
        result = parser.parse("some unusual query")
        assert result.source_stage == "llm"

    def test_semantic_exception_falls_to_llm(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nonexistent"]})
        llm = FakeLLM(LLMIntentVerdict(primary_domain="D5", confidence=0.6))
        parser = IntentParser(mapper, embedding_searcher=FailingEmbedding(), llm_caller=llm)
        result = parser.parse("another query")
        assert result.source_stage == "llm"
        assert result.primary_domain == "D5"


# ---------------------------------------------------------------------------
# Stage 3 LLM
# ---------------------------------------------------------------------------


class TestStage3LLM:
    def test_llm_low_confidence_requires_human(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nope"]})
        llm = FakeLLM(LLMIntentVerdict(primary_domain="D4", confidence=0.1))
        parser = IntentParser(mapper, llm_caller=llm)
        result = parser.parse("something unclear")
        assert result.source_stage == "llm"
        assert result.requires_human is True

    def test_llm_unknown_domain_requires_human(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nope"]})
        llm = FakeLLM(LLMIntentVerdict(primary_domain="UNKNOWN", confidence=0.8))
        parser = IntentParser(mapper, llm_caller=llm)
        result = parser.parse("weird stuff")
        assert result.requires_human is True

    def test_llm_normal_path(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nope"]})
        llm = FakeLLM(
            LLMIntentVerdict(
                primary_domain="D7",
                confidence=0.9,
                secondary_domains=["D0"],
                suggested_directives=["777", "999"],
                cost_usd=0.003,
            )
        )
        parser = IntentParser(mapper, llm_caller=llm)
        result = parser.parse("report analytics dashboard please")
        assert result.primary_domain == "D7"
        assert result.suggested_directives == ["777", "999"]
        assert result.cost_usd == pytest.approx(0.003)
        assert result.requires_human is False

    def test_llm_failure_returns_unknown_human(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nope"]})
        parser = IntentParser(mapper, llm_caller=FailingLLM())
        result = parser.parse("obscure input")
        assert result.requires_human is True
        assert "llm_error" in (result.rationale or "")


# ---------------------------------------------------------------------------
# 级联与 trace
# ---------------------------------------------------------------------------


class TestTraceAndCascade:
    def test_trace_records_stages(self) -> None:
        mapper = IntentKeywordMapper(keywords={"D9": ["nope"]})
        emb = FakeEmbedding([])  # 无命中
        llm = FakeLLM(LLMIntentVerdict(primary_domain="D3", confidence=0.9))
        parser = IntentParser(mapper, embedding_searcher=emb, llm_caller=llm)
        parser.parse("ambiguous query")
        trace = parser.last_trace
        assert trace is not None
        assert trace.stages == ["keyword", "semantic", "llm"]
        assert trace.total_latency_ms >= 0

    def test_stage2_only_no_llm(self) -> None:
        """stage 1 fail + stage 2 命中 + 无 llm → 使用 semantic 结果。"""
        mapper = IntentKeywordMapper(keywords={"D9": ["nope"]})
        emb = FakeEmbedding([EmbeddingHit(domain="D4", score=0.95)])
        parser = IntentParser(mapper, embedding_searcher=emb)
        result = parser.parse("x")
        assert result.source_stage == "semantic"
        assert result.primary_domain == "D4"

    def test_all_unavailable_returns_unknown_human(self) -> None:
        """三个 stage 都无可用依赖 → UNKNOWN + requires_human。"""
        mapper = IntentKeywordMapper(keywords={"D9": ["nope"]})
        parser = IntentParser(mapper)
        result = parser.parse("total mystery")
        assert result.primary_domain == "UNKNOWN"
        assert result.requires_human is True
        assert result.fallback_hint is not None

    def test_custom_thresholds(self) -> None:
        mapper = IntentKeywordMapper()
        emb = FakeEmbedding([EmbeddingHit(domain="D1", score=0.4)])
        # 把 stage2 阈值调到 0.1 → 0.4 / 0.4 = 1.0，应直接采纳
        parser = IntentParser(mapper, embedding_searcher=emb, thresholds={"stage2_accept": 0.1})
        # 先让 stage 1 UNKNOWN
        result = parser.parse("nothing-matches-keyword-list xyzzy qux")
        assert result.source_stage == "semantic"


# ---------------------------------------------------------------------------
# 集成辅助函数
# ---------------------------------------------------------------------------


class TestIntegrationHelpers:
    def test_plan_directive_chain_joins(self) -> None:
        r = IntentResult(
            query="q",
            primary_domain="D2",
            confidence=0.9,
            matched_keywords=[],
            source_stage="keyword",
            suggested_directives=["222", "244", "999"],
            latency_ms=1,
        )
        assert plan_directive_chain(r) == "222+244+999"

    def test_plan_directive_chain_empty_falls_back(self) -> None:
        r = IntentResult(
            query="q",
            primary_domain="UNKNOWN",
            confidence=0.0,
            matched_keywords=[],
            source_stage="llm",
            suggested_directives=[],
            latency_ms=1,
        )
        assert plan_directive_chain(r) == "999"

    def test_inject_context_for_uses_module_id_when_known(self) -> None:
        class FakeInjector:
            def __init__(self) -> None:
                self.module_id_called: str | None = None
                self.keyword_called: str | None = None

            def inject_by_module_id(self, module_id: str) -> str:
                self.module_id_called = module_id
                return f"ctx-for-{module_id}"

            def inject_by_keyword(self, keyword: str) -> str:
                self.keyword_called = keyword
                return f"ctx-kw-{keyword}"

        r = IntentResult(
            query="q",
            primary_domain="D3",
            confidence=0.9,
            matched_keywords=[],
            source_stage="keyword",
            latency_ms=1,
        )
        inj = FakeInjector()
        out = inject_context_for(r, inj)
        assert out == "ctx-for-IntentDomain.D3"
        assert inj.module_id_called == "D3"

    def test_inject_context_for_falls_back_to_keyword(self) -> None:
        class KeywordOnly:
            def inject_by_keyword(self, keyword: str) -> str:
                return f"kw-{keyword}"

        r = IntentResult(
            query="risk check",
            primary_domain="UNKNOWN",
            confidence=0.0,
            matched_keywords=[],
            source_stage="llm",
            latency_ms=1,
        )
        out = inject_context_for(r, KeywordOnly())
        assert out == "kw-risk check"

    def test_inject_context_for_raises_without_interface(self) -> None:
        class Bad:
            pass

        r = IntentResult(
            query="q",
            primary_domain="D1",
            confidence=0.9,
            matched_keywords=[],
            source_stage="keyword",
            latency_ms=1,
        )
        with pytest.raises(AttributeError):
            inject_context_for(r, Bad())


def test_default_thresholds_exposed() -> None:
    assert "stage1_accept" in DEFAULT_STAGE_THRESHOLDS
    assert "stage2_accept" in DEFAULT_STAGE_THRESHOLDS
    assert DEFAULT_STAGE_THRESHOLDS["stage1_accept"] > DEFAULT_STAGE_THRESHOLDS["stage2_accept"]


def test_exports_present() -> None:
    from zephyr.governance.persistence import intent_parser as m

    for name in [
        "EmbeddingHit",
        "LLMIntentVerdict",
        "EmbeddingSearcher",
        "LLMIntentCaller",
        "IntentParseTrace",
        "IntentParser",
        "plan_directive_chain",
        "inject_context_for",
        "DEFAULT_STAGE_THRESHOLDS",
    ]:
        assert hasattr(m, name), f"missing export: {name}"
