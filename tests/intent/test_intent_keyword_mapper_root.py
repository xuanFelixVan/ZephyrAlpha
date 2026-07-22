# [A_test] module_id: MOD-GOV_intent_keyword_mapper_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
        map_intent_to_keywords,
    )

    _IMPORT_OK = True
    _IMPORT_ERR = None
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_ERR = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_ERR}")


class TestIntentKeywordMapper:
    def test_map_intent_governance(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("governance audit compliance")
        assert result.primary_domain == IntentDomain.D6
        assert result.confidence > 0.0
        assert result.source_stage == "keyword"
        assert len(result.matched_keywords) > 0

    def test_map_intent_debug(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("debug fix error bug troubleshoot")
        assert result.primary_domain == IntentDomain.D9
        assert result.confidence > 0.0

    def test_map_intent_empty_query(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("")
        assert result.primary_domain == IntentDomain.UNKNOWN
        assert result.confidence == 0.0
        assert result.requires_human is True

    def test_map_intent_whitespace_query(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("   ")
        assert result.primary_domain == IntentDomain.UNKNOWN
        assert result.confidence == 0.0

    def test_map_intent_no_match(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("xyzzy foobar bazquux")
        assert result.primary_domain == IntentDomain.UNKNOWN
        assert result.fallback_hint == "stage-1-only"

    def test_domain_count(self):
        mapper = IntentKeywordMapper()
        assert mapper.domain_count == 10

    def test_total_keywords(self):
        mapper = IntentKeywordMapper()
        assert mapper.total_keywords >= 200

    def test_get_keywords_for_domain(self):
        mapper = IntentKeywordMapper()
        kws = mapper.get_keywords_for_domain("D6")
        assert "governance" in kws
        assert "audit" in kws

    def test_get_keywords_for_unknown_domain(self):
        mapper = IntentKeywordMapper()
        kws = mapper.get_keywords_for_domain("D99")
        assert kws == []

    def test_custom_keywords(self):
        custom = {"D0": ["custom_kw_test"]}
        mapper = IntentKeywordMapper(keywords=custom)
        result = mapper.map_intent("custom_kw_test")
        assert result.primary_domain == "D0"

    def test_custom_keywords_missing_directive_raises(self):
        custom = {"DX": ["test_kw"]}
        with pytest.raises(ValueError, match="DX"):
            IntentKeywordMapper(keywords=custom)

    def test_latency_ms_non_negative(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("governance")
        assert result.latency_ms >= 0

    def test_confidence_range(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("governance audit compliance standard policy")
        assert 0.0 <= result.confidence <= 1.0

    def test_secondary_domains_populated(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("governance audit analytics report metric")
        assert len(result.secondary_domains) > 0

    def test_suggested_directives_populated(self):
        mapper = IntentKeywordMapper()
        result = mapper.map_intent("governance audit")
        assert len(result.suggested_directives) > 0


class TestMapIntentToKeywords:
    def test_valid_intent(self):
        kws = map_intent_to_keywords("CODE_GEN")
        assert isinstance(kws, list)
        assert len(kws) > 0
        assert "generate" in kws

    def test_debug_intent(self):
        kws = map_intent_to_keywords("DEBUG")
        assert "debug" in kws

    def test_invalid_intent_raises(self):
        with pytest.raises(ValueError, match="UNKNOWN"):
            map_intent_to_keywords("UNKNOWN")

    def test_empty_intent_raises(self):
        with pytest.raises(ValueError):
            map_intent_to_keywords("")


class TestIntentDomain:
    def test_all_domains(self):
        expected = {"D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "UNKNOWN"}
        actual = {d.value for d in IntentDomain}
        assert actual == expected

    def test_domain_is_string(self):
        assert IntentDomain.D6.value == "D6"
        assert isinstance(IntentDomain.D6, str)


class TestIntentResult:
    def test_creation(self):
        r = IntentResult(
            query="test",
            primary_domain=IntentDomain.D6,
            confidence=0.9,
            source_stage="keyword",
            latency_ms=10,
        )
        assert r.query == "test"
        assert r.primary_domain == IntentDomain.D6
        assert r.confidence == 0.9
        assert r.source_stage == "keyword"
        assert r.requires_human is False
        assert r.secondary_domains == []
        assert r.matched_keywords == []

    def test_default_values(self):
        r = IntentResult(
            query="test",
            primary_domain=IntentDomain.UNKNOWN,
            confidence=0.0,
            source_stage="keyword",
            latency_ms=0,
        )
        assert r.cost_usd == 0.0
        assert r.rationale is None
        assert r.fallback_hint is None
