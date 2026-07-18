# [A_test] module_id: SRC-TST-0284 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-344 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_agent_debate
# [INVARIANTS] DebateVerdict must be consistent with content comparison
# [MODIFY-GUARD] Changes must sync with agent_debate.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_agent_debate.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.agent_debate import (
    AgentDebate,
    DebateRound,
    DebateVerdict,
    ModelResponse,
)


class TestDebateVerdict:
    def test_enum_values(self):
        assert DebateVerdict.AGREE.value == "AGREE"
        assert DebateVerdict.A_SUPERIOR.value == "A_SUPERIOR"
        assert DebateVerdict.B_SUPERIOR.value == "B_SUPERIOR"
        assert DebateVerdict.OVERRIDE.value == "OVERRIDE"

    def test_all_verdicts_count(self):
        assert len(DebateVerdict) == 4


class TestModelResponse:
    def test_from_content_creates_response(self):
        resp = ModelResponse.from_content("gpt-4", "hello world", token_count=10, latency_ms=200)
        assert resp.model == "gpt-4"
        assert resp.token_count == 10
        assert resp.latency_ms == 200

    def test_from_content_hash_consistency(self):
        resp1 = ModelResponse.from_content("model-a", "same content")
        resp2 = ModelResponse.from_content("model-b", "same content")
        assert resp1.content_hash == resp2.content_hash

    def test_from_content_different_content_different_hash(self):
        resp1 = ModelResponse.from_content("model-a", "content A")
        resp2 = ModelResponse.from_content("model-a", "content B")
        assert resp1.content_hash != resp2.content_hash

    def test_from_content_defaults(self):
        resp = ModelResponse.from_content("model-x", "test")
        assert resp.token_count == 0
        assert resp.latency_ms == 0

    def test_from_content_empty_string(self):
        resp = ModelResponse.from_content("model", "")
        assert resp.response_hash != ""
        assert resp.content_hash != ""


class TestDebateRound:
    def test_default_values(self):
        resp_a = ModelResponse.from_content("a", "hello")
        resp_b = ModelResponse.from_content("b", "world")
        rd = DebateRound(round_id=1, model_a=resp_a, model_b=resp_b)
        assert rd.consensus is False
        assert rd.verdict == DebateVerdict.OVERRIDE
        assert rd.resolution == ""


class TestAgentDebate:
    def test_debate_same_content_agrees(self):
        debate = AgentDebate()
        verdict = debate.debate("model-a", "same answer", "model-b", "same answer")
        assert verdict == DebateVerdict.AGREE

    def test_debate_different_content_override(self):
        debate = AgentDebate()
        verdict = debate.debate("model-a", "answer A", "model-b", "answer B")
        assert verdict == DebateVerdict.OVERRIDE

    def test_debate_history_records(self):
        debate = AgentDebate()
        debate.debate("a", "x", "b", "x")
        debate.debate("a", "y", "b", "z")
        history = debate.history()
        assert len(history) == 2
        assert history[0].round_id == 1
        assert history[1].round_id == 2

    def test_agreement_rate_all_agree(self):
        debate = AgentDebate()
        debate.debate("a", "x", "b", "x")
        debate.debate("a", "y", "b", "y")
        assert debate.agreement_rate() == 1.0

    def test_agreement_rate_none_agree(self):
        debate = AgentDebate()
        debate.debate("a", "x", "b", "y")
        debate.debate("a", "1", "b", "2")
        assert debate.agreement_rate() == 0.0

    def test_agreement_rate_empty_history(self):
        debate = AgentDebate()
        assert debate.agreement_rate() == 0.0

    def test_agreement_rate_mixed(self):
        debate = AgentDebate()
        debate.debate("a", "same", "b", "same")
        debate.debate("a", "diff1", "b", "diff2")
        assert debate.agreement_rate() == 0.5

    def test_adjudicate_auto_equal(self):
        debate = AgentDebate()
        verdict, content = debate.adjudicate("same text", "same text")
        assert verdict == DebateVerdict.AGREE
        assert content == "same text"

    def test_adjudicate_auto_different(self):
        debate = AgentDebate()
        verdict, content = debate.adjudicate("text A", "text B")
        assert verdict == DebateVerdict.OVERRIDE
        assert content == "text A"

    def test_adjudicate_override_decision(self):
        debate = AgentDebate()
        verdict, content = debate.adjudicate("a", "b", override_decision="manual pick")
        assert verdict == DebateVerdict.OVERRIDE
        assert content == "manual pick"

    def test_debate_empty_content_agrees(self):
        debate = AgentDebate()
        verdict = debate.debate("a", "", "b", "")
        assert verdict == DebateVerdict.AGREE
