# [A_test] module_id: MOD-GOV_l8_multi_agent | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_l8_multi_agent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import pytest

from zephyr.security.llm_defense.llm_security.layers.l8_multi_agent import (
    AgentCommunicationItem,
    AgentIdentityResolver,
    CrossAgentPermission,
    MultiAgentSecurityLayer,
    Scope,
    TrustScoreCalculator,
    TrustTier,
)


class TestCrossAgentPermission:
    def test_not_expired_initially(self):
        perm = CrossAgentPermission(from_agent_id="a1", to_agent_id="a2", scope=Scope.READ, granted=True)
        assert perm.is_expired() is False

    def test_granted_defaults_false(self):
        perm = CrossAgentPermission(from_agent_id="a1", to_agent_id="a2")
        assert perm.granted is False


class TestTrustScoreCalculator:
    def test_calculates_score(self):
        calc = TrustScoreCalculator()
        result = calc.calculate(
            "agent-1",
            {
                "history": 0.8,
                "message_consistency": 0.7,
                "behavior_consistency": 0.6,
                "identity_strength": 0.9,
                "scope_minimization": 0.5,
            },
        )
        assert 0.0 <= result["total_score"] <= 1.0
        assert result["tier"] in [t.value for t in TrustTier]

    def test_untrusted_tier(self):
        calc = TrustScoreCalculator()
        result = calc.calculate(
            "evil-agent",
            {
                "history": 0.1,
                "message_consistency": 0.1,
                "behavior_consistency": 0.1,
                "identity_strength": 0.0,
                "scope_minimization": 0.0,
            },
        )
        assert result["tier"] == TrustTier.UNTRUSTED.value


class TestAgentIdentityResolver:
    def test_attestation_roundtrip(self):
        resolver = AgentIdentityResolver()
        resolver.register_agent("agent-1")
        attest = resolver.generate_attestation("agent-1")
        assert resolver.verify_attestation("agent-1", attest) is True

    def test_bad_attestation_fails(self):
        resolver = AgentIdentityResolver()
        resolver.register_agent("agent-1")
        assert resolver.verify_attestation("agent-1", "bad-attest") is False

    def test_message_sign_verify(self):
        resolver = AgentIdentityResolver()
        sig = resolver.sign_message("agent-1", "hello")
        assert resolver.verify_signature("agent-1", "hello", sig) is True
        assert resolver.verify_signature("agent-1", "hello", "bad-sig") is False


class TestMultiAgentSecurityLayer:
    def test_authenticate_cross_agent(self):
        layer = MultiAgentSecurityLayer()
        allowed, reason = layer.authenticate_cross_agent(
            from_agent="agent-a",
            to_agent="agent-b",
            scope="read",
            content="share data",
        )
        assert allowed is True

    def test_isolate_agent_communications(self):
        layer = MultiAgentSecurityLayer()
        item = AgentCommunicationItem(
            sender_id="agent-a",
            receiver_id="agent-b",
            content="hello",
        )
        result = layer.isolate_agent_communications(item)
        assert result.verified is True
        assert result.signature != ""
        assert len(layer.comm_history) == 1

    @pytest.mark.asyncio
    async def test_evaluate_without_agents_allowed(self):
        from zephyr.security.llm_defense.llm_security.protocol import SecurityContext, SecurityDecision

        layer = MultiAgentSecurityLayer()
        ctx = SecurityContext(
            request_id="test-l8-eval-1",
            layer_name="l8_multi_agent",
            raw_input="normal content",
            metadata={},
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.ALLOW
        assert result.layer_name == "l8_multi_agent"

    @pytest.mark.asyncio
    async def test_evaluate_with_authorized_agents(self):
        from zephyr.security.llm_defense.llm_security.protocol import SecurityContext, SecurityDecision

        layer = MultiAgentSecurityLayer()
        ctx = SecurityContext(
            request_id="test-l8-eval-2",
            layer_name="l8_multi_agent",
            raw_input="share data",
            metadata={"from_agent_id": "agent-a", "to_agent_id": "agent-b", "scope": "read"},
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.ALLOW

    @pytest.mark.asyncio
    async def test_evaluate_denies_unauthorized_cross_agent(self):
        from zephyr.security.llm_defense.llm_security.protocol import SecurityContext, SecurityDecision

        layer = MultiAgentSecurityLayer()
        layer.authenticate_cross_agent = lambda *a, **kw: (False, "unauthorized")
        ctx = SecurityContext(
            request_id="test-l8-eval-3",
            layer_name="l8_multi_agent",
            raw_input="steal data",
            metadata={"from_agent_id": "evil", "to_agent_id": "target", "scope": "admin"},
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.DENY
        assert result.score == 0.0
