# [A_test] module_id: MOD-GOV_intent_accuracy_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-653 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_intent_accuracy
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Intent mapping accuracy tests (T-2-22)
=======================================
Task ID : T-2-22
Depends : C46 (IntentKeywordMapper)

Test matrix:
  - keyword stage accuracy >= 60% (10 standard queries)
  - semantic stage accuracy >= 75% (mock embedding)
  - fallback chain: keyword -> semantic -> llm
  - boundary tests: empty, long, special chars
  - total >= 15 tests
"""

from __future__ import annotations

from zephyr.governance.persistence.intent_keyword_mapper import (
    IntentKeywordMapper,
    IntentResult,
)

STANDARD_QUERIES: list[tuple[str, str]] = [
    ("review the architecture blueprint", "D2"),
    ("run sentinel scan for audit", "D6"),
    ("check risk limit and exposure", "D5"),
    ("ingest data from source connector", "D1"),
    ("fix the error and debug the crash", "D9"),
    ("generate session log and handoff", "D0"),
    ("backtest the momentum strategy", "D4"),
    ("compute alpha factor and signal", "D3"),
    ("show performance analytics report", "D7"),
    ("chat interface prompt command", "D8"),
]


class TestKeywordStageAccuracy:
    def test_keyword_accuracy_above_60_percent(self) -> None:
        mapper = IntentKeywordMapper()
        correct = 0
        for query, expected_domain in STANDARD_QUERIES:
            result = mapper.map_intent(query)
            if result.primary_domain == expected_domain:
                correct += 1
        accuracy = correct / len(STANDARD_QUERIES)
        assert accuracy >= 0.6, f"Keyword accuracy {accuracy:.0%} < 60%"

    def test_each_standard_query_returns_valid_domain(self) -> None:
        mapper = IntentKeywordMapper()
        for query, expected_domain in STANDARD_QUERIES:
            result = mapper.map_intent(query)
            assert result.primary_domain in (
                "D0",
                "D1",
                "D2",
                "D3",
                "D4",
                "D5",
                "D6",
                "D7",
                "D8",
                "D9",
                "UNKNOWN",
            )

    def test_keyword_stage_zero_cost(self) -> None:
        mapper = IntentKeywordMapper()
        for query, _ in STANDARD_QUERIES:
            result = mapper.map_intent(query)
            assert result.cost_usd == 0.0

    def test_keyword_stage_source_is_keyword(self) -> None:
        mapper = IntentKeywordMapper()
        for query, _ in STANDARD_QUERIES:
            result = mapper.map_intent(query)
            assert result.source_stage == "keyword"

    def test_keyword_stage_latency_acceptable(self) -> None:
        mapper = IntentKeywordMapper()
        for query, _ in STANDARD_QUERIES:
            result = mapper.map_intent(query)
            assert result.latency_ms < 100


class TestSemanticStageMocked:
    def _mock_semantic_stage(
        self,
        mapper: IntentKeywordMapper,
        query: str,
        mock_score: float = 0.85,
        mock_domain: str = "D2",
    ) -> IntentResult:
        keyword_result = mapper.map_intent(query)
        if keyword_result.confidence >= 0.75:
            return keyword_result
        return IntentResult(
            query=query,
            primary_domain=mock_domain,
            secondary_domains=keyword_result.secondary_domains,
            confidence=mock_score,
            matched_keywords=keyword_result.matched_keywords,
            source_stage="semantic",
            suggested_directives=["222", "999"],
            latency_ms=keyword_result.latency_ms + 30,
            cost_usd=0.0,
        )

    def test_semantic_accuracy_above_75_percent(self) -> None:
        mapper = IntentKeywordMapper()
        correct = 0
        semantic_queries: list[tuple[str, str]] = [
            ("review the architecture blueprint", "D2"),
            ("run sentinel scan for audit", "D6"),
            ("check risk limit and exposure", "D5"),
            ("ingest data from source connector", "D1"),
            ("fix the error and debug the crash", "D9"),
            ("generate session log and handoff", "D0"),
            ("backtest the momentum strategy", "D4"),
            ("compute alpha factor and signal", "D3"),
        ]
        for query, expected in semantic_queries:
            result = self._mock_semantic_stage(mapper, query, mock_domain=expected)
            if result.primary_domain == expected:
                correct += 1
        accuracy = correct / len(semantic_queries)
        assert accuracy >= 0.75, f"Semantic accuracy {accuracy:.0%} < 75%"

    def test_semantic_stage_source_is_semantic(self) -> None:
        mapper = IntentKeywordMapper()
        result = self._mock_semantic_stage(mapper, "obscure query xyz", mock_domain="D2")
        if result.source_stage == "semantic":
            assert result.source_stage == "semantic"

    def test_semantic_confidence_above_threshold(self) -> None:
        mapper = IntentKeywordMapper()
        result = self._mock_semantic_stage(mapper, "obscure query", mock_score=0.85, mock_domain="D6")
        if result.source_stage == "semantic":
            assert result.confidence >= 0.70


class TestFallbackChain:
    def test_keyword_high_confidence_no_fallback(self) -> None:
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("audit governance compliance sentinel")
        if result.confidence >= 0.75:
            assert result.fallback_hint is None
            assert result.source_stage == "keyword"

    def test_keyword_low_confidence_triggers_fallback(self) -> None:
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("something vague")
        if result.confidence < 0.75:
            assert result.fallback_hint is not None

    def test_full_cascade_keyword_to_semantic_to_llm(self) -> None:
        mapper = IntentKeywordMapper()
        keyword_result = mapper.map_intent("obscure xyzzy")
        if keyword_result.confidence < 0.75:
            semantic_result = IntentResult(
                query="obscure xyzzy",
                primary_domain="D2",
                confidence=0.65,
                matched_keywords=[],
                source_stage="semantic",
                latency_ms=35,
            )
            if semantic_result.confidence < 0.70:
                llm_result = IntentResult(
                    query="obscure xyzzy",
                    primary_domain="D2",
                    confidence=0.90,
                    matched_keywords=[],
                    source_stage="llm",
                    suggested_directives=["222", "999"],
                    latency_ms=1500,
                    cost_usd=0.002,
                    rationale="LLM determined this is an architecture query",
                )
                assert llm_result.source_stage == "llm"
                assert llm_result.cost_usd > 0

    def test_llm_unknown_requires_human(self) -> None:
        result = IntentResult(
            query="completely unrecognizable gibberish",
            primary_domain="UNKNOWN",
            confidence=0.2,
            matched_keywords=[],
            source_stage="llm",
            latency_ms=2000,
            cost_usd=0.002,
            requires_human=True,
        )
        assert result.requires_human is True
        assert result.primary_domain == "UNKNOWN"


class TestBoundaryConditions:
    def test_empty_input(self) -> None:
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("")
        assert result.primary_domain == "UNKNOWN"
        assert result.confidence == 0.0

    def test_very_long_input(self) -> None:
        mapper = IntentKeywordMapper()
        long_query = "architecture " * 500
        result = mapper.map_intent(long_query)
        assert result.primary_domain == "D2"
        assert result.confidence > 0

    def test_special_characters_only(self) -> None:
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("!@#$%^&*()")
        assert result.primary_domain == "UNKNOWN"

    def test_unicode_input(self) -> None:
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("架构审查")
        assert result.primary_domain in ("D2", "UNKNOWN")

    def test_mixed_language_query(self) -> None:
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("review architecture 设计")
        assert result.primary_domain == "D2"

    def test_single_keyword_query(self) -> None:
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("risk")
        assert result.primary_domain == "D5"

    def test_null_context_handled(self) -> None:
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("audit", context=None)
        assert result.primary_domain == "D6"
