# [A_test] module_id: SRC-TST-0366 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_spec_auditor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.gov_audit.spec_auditor import record_agent_spec
from zephyr.feedback_loop.protocols import AgentCapability


class TestRecordAgentSpec:
    def test_basic_record(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read", "write"], version="1.2.0")
        result = record_agent_spec(cap)
        assert result["event_type"] == "AGENT_SPEC_REGISTERED"
        assert result["agent_id"] == "agent-1"
        assert "read" in result["claimed_capabilities"]
        assert "write" in result["claimed_capabilities"]
        assert result["version"] == "1.2.0"
        assert "timestamp" in result

    def test_with_model_provider(self):
        cap = AgentCapability(agent_id="agent-2", capabilities=["execute"])
        cap_dict = cap.model_dump()
        cap_dict["model_provider"] = "openai"
        mock_cap = MagicMock()
        mock_cap.agent_id = "agent-2"
        mock_cap.capabilities = ["execute"]
        mock_cap.model_provider = "openai"
        mock_cap.version = "2.0.0"
        result = record_agent_spec(mock_cap)
        assert result["model_provider"] == "openai"
        assert result["version"] == "2.0.0"

    def test_empty_capabilities(self):
        cap = AgentCapability(agent_id="agent-3", capabilities=[])
        result = record_agent_spec(cap)
        assert result["claimed_capabilities"] == []

    def test_claimed_capabilities_fallback(self):
        mock_cap = MagicMock(spec=[])
        mock_cap.agent_id = "agent-4"
        del mock_cap.capabilities
        mock_cap.claimed_capabilities = ["admin"]
        result = record_agent_spec(mock_cap)
        assert "admin" in result["claimed_capabilities"]

    def test_default_model_provider(self):
        cap = AgentCapability(agent_id="agent-5")
        result = record_agent_spec(cap)
        assert result["model_provider"] == "unknown"

    def test_default_version(self):
        mock_cap = MagicMock(spec=[])
        mock_cap.agent_id = "agent-6"
        del mock_cap.capabilities
        mock_cap.claimed_capabilities = []
        del mock_cap.version
        result = record_agent_spec(mock_cap)
        assert result["version"] == "0.0.0"
