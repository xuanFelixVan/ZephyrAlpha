# [A_test] module_id: SRC-TST-1235 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_llm_provider_integrity
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.llm_provider_integrity
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_llm_provider_integrity.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.reliability.llm_provider_integrity import (
    LLMProviderIntegrity,
    ProviderResponse,
)


class TestLLMProviderIntegrityInstantiation:
    def test_default_instantiation(self):
        integ = LLMProviderIntegrity()
        assert integ.responses == {}
        assert integ.min_providers == 2
        assert integ.hash_match_required == 0.5

    def test_custom_parameters(self):
        integ = LLMProviderIntegrity(min_providers=3, hash_match_required=0.7)
        assert integ.min_providers == 3
        assert integ.hash_match_required == 0.7


class TestProviderResponse:
    def test_default_timestamp(self):
        pr = ProviderResponse(provider="openai", query_hash="abc", response_hash="def")
        assert pr.timestamp == 0.0

    def test_custom_timestamp(self):
        pr = ProviderResponse(provider="anthropic", query_hash="abc", response_hash="def", timestamp=1000.0)
        assert pr.timestamp == 1000.0


class TestRecord:
    def test_record_single_response(self):
        integ = LLMProviderIntegrity()
        pr = integ.record("what is 2+2?", "4", "openai")
        assert pr.provider == "openai"
        assert isinstance(pr.query_hash, str)
        assert isinstance(pr.response_hash, str)
        assert len(integ.responses) == 1

    def test_record_multiple_providers_same_query(self):
        integ = LLMProviderIntegrity()
        integ.record("what is 2+2?", "4", "openai")
        integ.record("what is 2+2?", "4", "anthropic")
        assert len(integ.responses) == 1
        key = list(integ.responses.keys())[0]
        assert len(integ.responses[key]) == 2

    def test_record_different_queries(self):
        integ = LLMProviderIntegrity()
        integ.record("query1", "response1", "openai")
        integ.record("query2", "response2", "openai")
        assert len(integ.responses) == 2

    def test_record_returns_provider_response(self):
        integ = LLMProviderIntegrity()
        pr = integ.record("test query", "test response", "provider_a")
        assert isinstance(pr, ProviderResponse)

    def test_record_empty_query(self):
        integ = LLMProviderIntegrity()
        pr = integ.record("", "response", "provider_a")
        assert pr.query_hash != ""

    def test_record_empty_response(self):
        integ = LLMProviderIntegrity()
        pr = integ.record("query", "", "provider_a")
        assert pr.response_hash != ""


class TestConsensusOk:
    def test_no_records_returns_false(self):
        integ = LLMProviderIntegrity()
        assert integ.consensus_ok("any query") is False

    def test_single_provider_returns_false(self):
        integ = LLMProviderIntegrity(min_providers=2)
        integ.record("query", "response", "openai")
        assert integ.consensus_ok("query") is False

    def test_matching_responses_consensus(self):
        integ = LLMProviderIntegrity(min_providers=2, hash_match_required=0.5)
        integ.record("query", "same_response", "openai")
        integ.record("query", "same_response", "anthropic")
        assert integ.consensus_ok("query") is True

    def test_mismatching_responses_no_consensus(self):
        integ = LLMProviderIntegrity(min_providers=2, hash_match_required=0.99)
        integ.record("query", "response_a", "openai")
        integ.record("query", "response_b", "anthropic")
        assert integ.consensus_ok("query") is False

    def test_partial_consensus(self):
        integ = LLMProviderIntegrity(min_providers=3, hash_match_required=0.5)
        integ.record("query", "same", "openai")
        integ.record("query", "same", "anthropic")
        integ.record("query", "different", "google")
        assert integ.consensus_ok("query") is True

    def test_unknown_query_returns_false(self):
        integ = LLMProviderIntegrity()
        integ.record("known_query", "response", "openai")
        assert integ.consensus_ok("unknown_query") is False
