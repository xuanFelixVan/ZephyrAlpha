"""G-CT-007 — Agent Spec → Audit 集成测试."""
from __future__ import annotations

import pytest


class TestGCT007SpecToAudit:
    """验证 agent_spec/registry.py 的 AgentCapability 可被 audit_trail/spec_auditor.py 记录."""

    def test_capability_creatable(self):
        from zephyr.governance.agent_spec.registry import AgentCapability
        cap = AgentCapability(agent_id="test", capabilities=["read:docs", "write:tests"])
        assert cap.agent_id == "test"

    def test_spec_auditor_records_capability(self):
        from zephyr.governance.agent_spec.registry import AgentCapability
        from zephyr.governance.audit_trail.spec_auditor import record_agent_spec
        cap = AgentCapability(agent_id="test", capabilities=["read:docs"])
        result = record_agent_spec(cap)
        assert "agent_id" in result
        assert result["event_type"] == "AGENT_SPEC_REGISTERED"

    def test_spec_registry_register(self):
        from zephyr.governance.agent_spec.registry import SpecRegistry, AgentCapability
        registry = SpecRegistry()
        cap = AgentCapability(agent_id="test", capabilities=["cap"])
        registry.register(cap)
        result = cap.agent_id
        assert result == "test"
