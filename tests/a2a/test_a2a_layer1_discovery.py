# [A_test] module_id: MOD-GOV_a2a_layer1_discovery | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §layer1_discovery
# [MODULE] tests.test_a2a_layer1_discovery
# [INVARIANTS] A2ARegistry.register/discover/get必须一致; IdentityVerifier.sign/verify必须可逆
# [MODIFY-GUARD] 仅当layer1_discovery公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_a2a_layer1_discovery.py -q
# [TTL] task_bound

import pytest

from zephyr.infrastructure.a2a_protocol.layer1_discovery.a2a_registry import A2ARegistry
from zephyr.infrastructure.a2a_protocol.layer1_discovery.agent_card import (
    AgentCapability,
    AgentCard,
)
from zephyr.infrastructure.a2a_protocol.layer1_discovery.identity_verifier import (
    IdentityVerifier,
)


class TestAgentCapability:
    def test_values(self):
        assert AgentCapability.READ.value == "read"
        assert AgentCapability.WRITE.value == "write"
        assert AgentCapability.BASH.value == "bash"
        assert AgentCapability.SEARCH.value == "search"


class TestAgentCard:
    def test_construction(self):
        card = AgentCard(
            agent_id="agent-test-1",
            name="Test Agent",
            description="A test agent",
        )
        assert card.agent_id == "agent-test-1"
        assert card.name == "Test Agent"
        assert card.version == "0.1.0"
        assert card.capabilities == []
        assert card.max_tasks == 5

    def test_with_capabilities(self):
        card = AgentCard(
            agent_id="agent-test-2",
            name="Capable Agent",
            description="Has capabilities",
            capabilities=[AgentCapability.READ, AgentCapability.WRITE],
        )
        assert len(card.capabilities) == 2
        assert AgentCapability.READ in card.capabilities

    def test_invalid_agent_id(self):
        with pytest.raises(Exception):
            AgentCard(
                agent_id="INVALID ID!",
                name="Bad",
                description="Bad ID",
            )

    def test_custom_fields(self):
        card = AgentCard(
            agent_id="agent-test-3",
            name="Custom",
            description="Custom fields",
            skill_ids=["skill-1"],
            model_preferences=["claude"],
            max_tasks=10,
            endpoint="http://localhost:8080",
        )
        assert card.skill_ids == ["skill-1"]
        assert card.model_preferences == ["claude"]
        assert card.max_tasks == 10
        assert card.endpoint == "http://localhost:8080"


class TestA2ARegistry:
    def test_instantiation(self):
        registry = A2ARegistry()
        assert registry is not None

    def test_register_and_get(self):
        registry = A2ARegistry()
        card = AgentCard(
            agent_id="agent-reg-1",
            name="Registered",
            description="Test registration",
        )
        registry.register(card)
        retrieved = registry.get("agent-reg-1")
        assert retrieved is not None
        assert retrieved.agent_id == "agent-reg-1"

    def test_get_nonexistent(self):
        registry = A2ARegistry()
        assert registry.get("nonexistent") is None

    def test_discover_all(self):
        registry = A2ARegistry()
        registry.register(AgentCard(agent_id="agent-d1", name="A1", description="D1"))
        registry.register(AgentCard(agent_id="agent-d2", name="A2", description="D2"))
        results = registry.discover()
        assert len(results) == 2

    def test_discover_by_capability(self):
        registry = A2ARegistry()
        registry.register(
            AgentCard(
                agent_id="agent-cap-1",
                name="Reader",
                description="Can read",
                capabilities=[AgentCapability.READ],
            )
        )
        registry.register(
            AgentCard(
                agent_id="agent-cap-2",
                name="Writer",
                description="Can write",
                capabilities=[AgentCapability.WRITE],
            )
        )
        readers = registry.discover(capability="read")
        assert len(readers) == 1
        assert readers[0].agent_id == "agent-cap-1"

    def test_unregister(self):
        registry = A2ARegistry()
        registry.register(AgentCard(agent_id="agent-unreg", name="U", description="D"))
        assert registry.unregister("agent-unreg") is True
        assert registry.get("agent-unreg") is None

    def test_unregister_nonexistent(self):
        registry = A2ARegistry()
        assert registry.unregister("nonexistent") is False


class TestIdentityVerifier:
    def test_instantiation(self):
        verifier = IdentityVerifier()
        assert verifier is not None

    def test_sign_and_verify(self):
        verifier = IdentityVerifier()
        agent_id = "agent-test"
        payload = {"action": "test"}
        signature = verifier.sign(agent_id, payload)
        assert verifier.verify(agent_id, payload, signature) is True

    def test_verify_wrong_signature(self):
        verifier = IdentityVerifier()
        assert verifier.verify("agent-test", {"action": "test"}, "wrong_sig") is False

    def test_verify_wrong_payload(self):
        verifier = IdentityVerifier()
        signature = verifier.sign("agent-test", {"action": "test"})
        assert verifier.verify("agent-test", {"action": "other"}, signature) is False

    def test_verify_wrong_agent(self):
        verifier = IdentityVerifier()
        signature = verifier.sign("agent-a", {"action": "test"})
        assert verifier.verify("agent-b", {"action": "test"}, signature) is False

    def test_generate_challenge(self):
        verifier = IdentityVerifier()
        challenge = verifier.generate_challenge()
        assert isinstance(challenge, str)
        assert len(challenge) == 64

    def test_different_secrets(self):
        v1 = IdentityVerifier(shared_secret=b"secret1")
        v2 = IdentityVerifier(shared_secret=b"secret2")
        sig = v1.sign("agent", {"x": 1})
        assert v2.verify("agent", {"x": 1}, sig) is False
