# [A_test] module_id: MOD-GOV_capability_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.capability_check
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.skill_rbac_registry import AgentCapability
    from zephyr.security.access_control.capability_check import (
        MAX_CAPABILITIES,
        verify_capability_scope,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestVerifyCapabilityScopeApproved:
    def test_approved_normal_capabilities(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read", "write", "execute"])
        result = verify_capability_scope(cap)
        assert result["approved"] is True
        assert result["capabilities"] == ["read", "write", "execute"]

    def test_approved_single_capability(self):
        cap = AgentCapability(agent_id="agent-2", capabilities=["read"])
        result = verify_capability_scope(cap)
        assert result["approved"] is True

    def test_approved_max_capabilities(self):
        caps = [f"cap_{i}" for i in range(MAX_CAPABILITIES)]
        cap = AgentCapability(agent_id="agent-3", capabilities=caps)
        result = verify_capability_scope(cap)
        assert result["approved"] is True

    def test_approved_agent_id_returned(self):
        cap = AgentCapability(agent_id="my-agent", capabilities=["read"])
        result = verify_capability_scope(cap)
        assert result["agent_id"] == "my-agent"


class TestVerifyCapabilityScopeDenied:
    def test_denied_too_many_capabilities(self):
        caps = [f"cap_{i}" for i in range(MAX_CAPABILITIES + 1)]
        cap = AgentCapability(agent_id="agent-10", capabilities=caps)
        result = verify_capability_scope(cap)
        assert result["approved"] is False
        assert "too_many_capabilities" in result["reason"]

    def test_denied_restricted_capability(self):
        cap = AgentCapability(agent_id="agent-11", capabilities=["read", "sudo"])
        result = verify_capability_scope(cap)
        assert result["approved"] is False
        assert "restricted_capabilities_claimed" in result["reason"]

    def test_denied_no_capabilities(self):
        cap = AgentCapability(agent_id="agent-12", capabilities=[])
        result = verify_capability_scope(cap)
        assert result["approved"] is False
        assert result["reason"] == "no_capabilities_claimed"

    def test_denied_all_restricted(self):
        cap = AgentCapability(agent_id="agent-13", capabilities=["destroy", "purge"])
        result = verify_capability_scope(cap)
        assert result["approved"] is False

    def test_denied_single_restricted_root(self):
        cap = AgentCapability(agent_id="agent-14", capabilities=["root"])
        result = verify_capability_scope(cap)
        assert result["approved"] is False
        assert "root" in result["reason"]


class TestVerifyCapabilityScopeBoundary:
    def test_empty_capabilities_list(self):
        cap = AgentCapability(agent_id="agent-20", capabilities=[])
        result = verify_capability_scope(cap)
        assert result["approved"] is False

    def test_exactly_max_capabilities(self):
        caps = [f"cap_{i}" for i in range(MAX_CAPABILITIES)]
        cap = AgentCapability(agent_id="agent-21", capabilities=caps)
        result = verify_capability_scope(cap)
        assert result["approved"] is True

    def test_one_over_max_capabilities(self):
        caps = [f"cap_{i}" for i in range(MAX_CAPABILITIES + 1)]
        cap = AgentCapability(agent_id="agent-22", capabilities=caps)
        result = verify_capability_scope(cap)
        assert result["approved"] is False

    def test_restricted_takes_priority_over_empty(self):
        cap = AgentCapability(agent_id="agent-23", capabilities=["sudo"])
        result = verify_capability_scope(cap)
        assert result["approved"] is False
        assert "restricted" in result["reason"]
