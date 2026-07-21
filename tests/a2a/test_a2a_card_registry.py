# [A_test] module_id: MOD-GOV_a2a_card_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_a2a_card_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_a2a_card_registry.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.a2a_card_registry import card_registry
from zephyr.infrastructure.a2a_protocol.layer1_discovery.a2a_registry import A2ARegistry
from zephyr.infrastructure.a2a_protocol.layer1_discovery.agent_card import AgentCapability, AgentCard


class TestCardRegistry:
    def test_is_a2a_registry_instance(self):
        assert isinstance(card_registry, A2ARegistry)

    def test_register_and_get(self):
        card = AgentCard(
            agent_id="agent-test-001",
            name="Test Agent",
            description="A test agent",
        )
        card_registry.register(card)
        found = card_registry.get("agent-test-001")
        assert found is not None
        assert found.agent_id == "agent-test-001"
        card_registry.unregister("agent-test-001")

    def test_discover_by_capability(self):
        card = AgentCard(
            agent_id="agent-test-002",
            name="Reader",
            description="Read agent",
            capabilities=[AgentCapability.READ],
        )
        card_registry.register(card)
        results = card_registry.discover("read")
        assert any(c.agent_id == "agent-test-002" for c in results)
        card_registry.unregister("agent-test-002")

    def test_discover_all(self):
        results = card_registry.discover()
        assert isinstance(results, list)

    def test_unregister(self):
        card = AgentCard(
            agent_id="agent-test-003",
            name="Temp",
            description="Temporary",
        )
        card_registry.register(card)
        assert card_registry.unregister("agent-test-003") is True
        assert card_registry.get("agent-test-003") is None

    def test_unregister_nonexistent(self):
        assert card_registry.unregister("nonexistent") is False
