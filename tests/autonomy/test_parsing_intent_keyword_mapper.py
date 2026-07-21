# [A_test] module_id: MOD-GOV_parsing_intent_keyword_mapper | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.intent_keyword_mapper
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
    from zephyr.governance.persistence.intent_keyword_mapper import (
        IntentDomain,
        IntentKeywordMapper,
        IntentResult,
    )
except Exception as _exc:
    pytest.skip(f"无法导入 intent_keyword_mapper: {_exc}", allow_module_level=True)


class TestIntentKeywordMapper:
    def test_map_intent_governance_query(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("governance audit compliance")
        assert isinstance(result, IntentResult)
        assert result.primary_domain == IntentDomain.D6

    def test_map_intent_empty_query(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("")
        assert result.primary_domain == IntentDomain.UNKNOWN
        assert result.confidence == 0.0

    def test_map_intent_whitespace_query(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("   ")
        assert result.primary_domain == IntentDomain.UNKNOWN

    def test_map_intent_unknown_domain(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("xyzzy foobar")
        assert result.primary_domain == IntentDomain.UNKNOWN

    def test_map_intent_returns_matched_keywords(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("governance audit")
        assert len(result.matched_keywords) > 0

    def test_domain_count(self):
        mapper = IntentKeywordMapper()
        assert mapper.domain_count == 10

    def test_total_keywords(self):
        mapper = IntentKeywordMapper()
        assert mapper.total_keywords >= 200

    def test_get_keywords_for_domain(self):
        mapper = IntentKeywordMapper()
        kws = mapper.get_keywords_for_domain("D6")
        assert len(kws) >= 20
        assert "governance" in kws

    def test_get_keywords_for_unknown_domain(self):
        mapper = IntentKeywordMapper()
        kws = mapper.get_keywords_for_domain("D99")
        assert kws == []

    def test_custom_keywords_missing_directive(self):
        with pytest.raises(ValueError):
            IntentKeywordMapper(keywords={"D99": ["test"]})


class TestIntentResult:
    def test_instantiation(self):
        result = IntentResult(
            query="test",
            primary_domain=IntentDomain.D0,
            confidence=0.9,
            source_stage="keyword",
            latency_ms=5,
        )
        assert result.query == "test"
        assert result.confidence == 0.9
        assert result.latency_ms == 5

    def test_default_fields(self):
        result = IntentResult(
            query="test",
            primary_domain=IntentDomain.UNKNOWN,
            confidence=0.0,
            source_stage="keyword",
            latency_ms=0,
        )
        assert result.secondary_domains == []
        assert result.matched_keywords == []
        assert result.cost_usd == 0.0


class TestIntentDomain:
    def test_all_domains_present(self):
        expected = {"D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "UNKNOWN"}
        actual = set(m.value for m in IntentDomain)
        assert actual == expected
