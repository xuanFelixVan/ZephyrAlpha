"""测试: Agent Card 模型"""

import pytest
from zephyr.l01_infrastructure.a2a_protocol.layer1_discovery.agent_card import AgentCard, AgentCapability


class TestAgentCard:
    def test_create_card(self):
        card = AgentCard(agent_id="agent-test-001", name="Test Agent", description="A test agent")
        assert card.name == "Test Agent"

    def test_card_with_capabilities(self):
        card = AgentCard(
            agent_id="agent-test-002",
            name="Coder",
            description="Code generation agent",
            capabilities=[AgentCapability.WRITE, AgentCapability.SEARCH],
            skill_ids=["SKILL-DOM-DBS-001"],
        )
        assert AgentCapability.WRITE in card.capabilities
        assert len(card.capabilities) == 2
        assert card.skill_ids == ["SKILL-DOM-DBS-001"]
