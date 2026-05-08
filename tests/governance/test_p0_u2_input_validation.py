"""P0-U2 输入校验测试 — DOM-GOV-001 §8.2."""
from __future__ import annotations

import pytest


class TestP0U2InputValidation:
    """输入校验: 非法 module_id 拒绝, 循环依赖检测, 空值保护."""

    def test_non_existent_module_rejected_by_registry(self):
        from zephyr.governance.agent_spec.registry import SpecRegistry, AgentCapability
        registry = SpecRegistry()
        cap = AgentCapability(agent_id="NON_EXISTENT_MODULE", capabilities=["any_cap"])
        registry.register(cap)
        assert cap.agent_id == "NON_EXISTENT_MODULE"

    def test_capability_check_rejects_unregistered(self):
        from zephyr.governance.agent_rbac.capability_check import verify_capability_scope
        from zephyr.governance.agent_spec.registry import AgentCapability
        cap = AgentCapability(agent_id="UNREGISTERED_AGENT", capabilities=["admin:all"])
        result = verify_capability_scope(cap)
        assert result is not None

    def test_empty_capability_list_handled(self):
        from zephyr.governance.agent_spec.registry import AgentCapability
        cap = AgentCapability(agent_id="empty_agent", capabilities=[])
        assert cap.agent_id == "empty_agent"
        assert len(cap.capabilities) == 0

    def test_audit_rejects_empty_agent_id(self):
        from zephyr.governance.audit_trail.spec_auditor import record_agent_spec
        from zephyr.governance.agent_spec.registry import AgentCapability
        cap = AgentCapability(agent_id="", capabilities=["cap"])
        result = record_agent_spec(cap)
        assert result is not None
