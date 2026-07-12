# [A_test] module_id: SRC-TST-1668 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_spec_auditor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_spec_auditor.py -q
# [TTL] task_bound

from __future__ import annotations

import re
from unittest.mock import MagicMock

from zephyr.governance.audit_trail.spec_auditor import record_agent_spec
from zephyr.feedback_loop.protocols import AgentCapability


class TestRecordAgentSpecBasic:
    def test_returns_agent_spec_registered_event_type(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read", "write"], version="1.2.0")
        result = record_agent_spec(cap)
        assert result["event_type"] == "AGENT_SPEC_REGISTERED"

    def test_returns_agent_id(self):
        cap = AgentCapability(agent_id="agent-42", capabilities=["read"], version="2.0.0")
        result = record_agent_spec(cap)
        assert result["agent_id"] == "agent-42"

    def test_returns_claimed_capabilities(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read", "write", "execute"])
        result = record_agent_spec(cap)
        assert result["claimed_capabilities"] == ["read", "write", "execute"]

    def test_returns_version(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read"], version="3.5.1")
        result = record_agent_spec(cap)
        assert result["version"] == "3.5.1"

    def test_returns_timestamp(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read"])
        result = record_agent_spec(cap)
        assert "timestamp" in result
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        assert re.match(iso_pattern, result["timestamp"]) is not None

    def test_returns_model_provider_default(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read"])
        result = record_agent_spec(cap)
        assert result["model_provider"] == "unknown"


class TestRecordAgentSpecWithMock:
    def test_mock_with_model_provider(self):
        mock_cap = MagicMock()
        mock_cap.agent_id = "agent-mock"
        mock_cap.capabilities = ["execute"]
        mock_cap.model_provider = "openai"
        mock_cap.version = "4.0.0"
        result = record_agent_spec(mock_cap)
        assert result["model_provider"] == "openai"
        assert result["version"] == "4.0.0"
        assert result["agent_id"] == "agent-mock"

    def test_mock_with_claimed_capabilities_fallback(self):
        mock_cap = MagicMock(spec=[])
        mock_cap.agent_id = "agent-fallback"
        del mock_cap.capabilities
        mock_cap.claimed_capabilities = ["admin", "sudo"]
        result = record_agent_spec(mock_cap)
        assert "admin" in result["claimed_capabilities"]
        assert "sudo" in result["claimed_capabilities"]

    def test_mock_without_version_defaults(self):
        mock_cap = MagicMock(spec=[])
        mock_cap.agent_id = "agent-nov"
        del mock_cap.capabilities
        mock_cap.claimed_capabilities = []
        del mock_cap.version
        result = record_agent_spec(mock_cap)
        assert result["version"] == "0.0.0"

    def test_mock_without_model_provider_defaults(self):
        mock_cap = MagicMock(spec=[])
        mock_cap.agent_id = "agent-nomp"
        del mock_cap.capabilities
        mock_cap.claimed_capabilities = []
        del mock_cap.model_provider
        result = record_agent_spec(mock_cap)
        assert result["model_provider"] == "unknown"


class TestRecordAgentSpecBoundary:
    def test_empty_capabilities_list(self):
        cap = AgentCapability(agent_id="agent-empty", capabilities=[])
        result = record_agent_spec(cap)
        assert result["claimed_capabilities"] == []
        assert result["event_type"] == "AGENT_SPEC_REGISTERED"

    def test_single_capability(self):
        cap = AgentCapability(agent_id="agent-single", capabilities=["read"])
        result = record_agent_spec(cap)
        assert result["claimed_capabilities"] == ["read"]

    def test_many_capabilities(self):
        caps = [f"cap_{i}" for i in range(20)]
        cap = AgentCapability(agent_id="agent-many", capabilities=caps)
        result = record_agent_spec(cap)
        assert len(result["claimed_capabilities"]) == 20
        assert result["claimed_capabilities"][0] == "cap_0"
        assert result["claimed_capabilities"][19] == "cap_19"

    def test_special_characters_in_agent_id(self):
        cap = AgentCapability(agent_id="agent-日本語-🎉", capabilities=["read"])
        result = record_agent_spec(cap)
        assert result["agent_id"] == "agent-日本語-🎉"

    def test_result_has_exactly_six_keys(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read"])
        result = record_agent_spec(cap)
        expected_keys = {"event_type", "agent_id", "claimed_capabilities", "model_provider", "version", "timestamp"}
        assert set(result.keys()) == expected_keys

    def test_timestamp_is_utc_iso_format(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read"])
        result = record_agent_spec(cap)
        ts = result["timestamp"]
        assert ts.endswith("+00:00") or "T" in ts

    def test_pydantic_capability_with_default_version(self):
        cap = AgentCapability(agent_id="agent-defaults")
        result = record_agent_spec(cap)
        assert result["version"] == "1.0.0"
        assert result["claimed_capabilities"] == []
