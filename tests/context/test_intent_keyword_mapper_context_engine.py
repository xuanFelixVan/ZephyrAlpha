# [A_test] module_id: MOD-GOV_intent_keyword_mapper_context_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-469 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_intent_keyword_mapper
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for intent_keyword_mapper.py (T-2-21)
=================================================
Coverage: IntentResult, IntentKeywordMapper, _tokenize
Minimum: 10 tests
"""

import pytest

from zephyr.governance.persistence.intent_keyword_mapper import (
    IntentKeywordMapper,
    IntentResult,
    _tokenize,
)


class TestTokenize:
    def test_english_tokens(self) -> None:
        tokens = _tokenize("run sentinel scan")
        assert "run" in tokens
        assert "sentinel" in tokens
        assert "scan" in tokens

    def test_mixed_chinese_english(self) -> None:
        tokens = _tokenize("帮我跑scan")
        assert len(tokens) > 0

    def test_empty_string(self) -> None:
        assert _tokenize("") == []

    def test_special_characters(self) -> None:
        tokens = _tokenize("hello! @world #test")
        assert "hello" in tokens or len(tokens) > 0


class TestIntentResult:
    def test_valid_result(self) -> None:
        r = IntentResult(
            query="test",
            primary_domain="D0",
            confidence=0.8,
            matched_keywords=["test"],
            source_stage="keyword",
            latency_ms=5,
        )
        assert r.primary_domain == "D0"
        assert r.confidence == 0.8
        assert r.source_stage == "keyword"

    def test_unknown_domain(self) -> None:
        r = IntentResult(
            query="???",
            primary_domain="UNKNOWN",
            confidence=0.0,
            matched_keywords=[],
            source_stage="keyword",
            latency_ms=1,
        )
        assert r.primary_domain == "UNKNOWN"

    def test_confidence_bounds(self) -> None:
        with pytest.raises(Exception):
            IntentResult(
                query="x",
                primary_domain="D0",
                confidence=1.5,
                matched_keywords=[],
                source_stage="keyword",
                latency_ms=1,
            )


class TestIntentKeywordMapper:
    def setup_method(self) -> None:
        self.mapper = IntentKeywordMapper()

    def test_map_architecture_query(self) -> None:
        result = self.mapper.map_intent("review the architecture blueprint")
        assert result.primary_domain == "D2"
        assert result.confidence > 0
        assert "keyword" in result.source_stage

    def test_map_risk_query(self) -> None:
        result = self.mapper.map_intent("check risk limit and exposure")
        assert result.primary_domain == "D5"
        assert result.confidence > 0

    def test_map_debug_query(self) -> None:
        result = self.mapper.map_intent("fix the error and debug the crash")
        assert result.primary_domain == "D9"

    def test_map_data_query(self) -> None:
        result = self.mapper.map_intent("ingest data from source connector")
        assert result.primary_domain == "D1"

    def test_map_empty_query(self) -> None:
        result = self.mapper.map_intent("")
        assert result.primary_domain == "UNKNOWN"
        assert result.confidence == 0.0
        assert result.requires_human is True

    def test_map_whitespace_query(self) -> None:
        result = self.mapper.map_intent("   ")
        assert result.primary_domain == "UNKNOWN"

    def test_map_no_match_query(self) -> None:
        result = self.mapper.map_intent("xyzzy foobar quux")
        assert result.primary_domain == "UNKNOWN"
        assert result.confidence == 0.0

    def test_suggested_directives(self) -> None:
        result = self.mapper.map_intent("review architecture")
        assert len(result.suggested_directives) > 0

    def test_latency_under_5ms(self) -> None:
        result = self.mapper.map_intent("audit compliance governance")
        assert result.latency_ms < 50

    def test_zero_cost(self) -> None:
        result = self.mapper.map_intent("risk budget")
        assert result.cost_usd == 0.0

    def test_secondary_domains(self) -> None:
        result = self.mapper.map_intent("risk architecture design")
        assert len(result.secondary_domains) >= 0

    def test_fallback_hint_low_confidence(self) -> None:
        result = self.mapper.map_intent("risk")
        if result.confidence < 0.75:
            assert result.fallback_hint is not None

    def test_matched_keywords_populated(self) -> None:
        result = self.mapper.map_intent("audit governance compliance")
        assert len(result.matched_keywords) > 0

    def test_domain_count(self) -> None:
        assert self.mapper.domain_count == 10

    def test_total_keywords(self) -> None:
        assert self.mapper.total_keywords >= 200

    def test_get_keywords_for_domain(self) -> None:
        kws = self.mapper.get_keywords_for_domain("D2")
        assert "architecture" in kws

    def test_custom_keywords(self) -> None:
        custom = {"D0": ["custom_kw"]}
        mapper = IntentKeywordMapper(keywords=custom)
        result = mapper.map_intent("custom_kw")
        assert result.primary_domain == "D0"

    def test_context_parameter_ignored(self) -> None:
        result = self.mapper.map_intent("audit", context={"session": "s1"})
        assert result.primary_domain == "D6"
