# [A_test] module_id: MOD-GOV_governance_capability_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
    from zephyr.security.access_control.capability_check import (
        MAX_CAPABILITIES,
        RESTRICTED_CAPABILITIES,
        verify_capability_scope,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

try:
    from zephyr.autonomy_core.skill_rbac_registry import AgentCapability

    _CAPABILITY_OK = True
    _CAPABILITY_REASON = ""
except Exception as exc:
    _CAPABILITY_OK = False
    _CAPABILITY_REASON = str(exc)

pytestmark = pytest.mark.skipif(
    not (_IMPORT_OK and _CAPABILITY_OK),
    reason=f"capability_check: {_IMPORT_REASON}; AgentCapability: {_CAPABILITY_REASON}",
)


@pytest.mark.skipif(not (_IMPORT_OK and _CAPABILITY_OK), reason="import failed")
class TestVerifyCapabilityScope:
    def test_valid_capabilities(self):
        cap = AgentCapability(agent_id="agent-1", capabilities=["read", "write"])
        result = verify_capability_scope(cap)
        assert result["approved"] is True
        assert result["agent_id"] == "agent-1"
        assert result["capabilities"] == ["read", "write"]

    def test_too_many_capabilities(self):
        caps = [f"cap_{i}" for i in range(MAX_CAPABILITIES + 1)]
        cap = AgentCapability(agent_id="agent-2", capabilities=caps)
        result = verify_capability_scope(cap)
        assert result["approved"] is False
        assert "too_many_capabilities" in result["reason"]

    def test_restricted_capabilities(self):
        cap = AgentCapability(agent_id="agent-3", capabilities=["read", "destroy"])
        result = verify_capability_scope(cap)
        assert result["approved"] is False
        assert "restricted_capabilities_claimed" in result["reason"]

    def test_no_capabilities(self):
        cap = AgentCapability(agent_id="agent-4", capabilities=[])
        result = verify_capability_scope(cap)
        assert result["approved"] is False
        assert result["reason"] == "no_capabilities_claimed"

    def test_max_capabilities_boundary(self):
        caps = [f"cap_{i}" for i in range(MAX_CAPABILITIES)]
        cap = AgentCapability(agent_id="agent-5", capabilities=caps)
        result = verify_capability_scope(cap)
        assert result["approved"] is True

    def test_all_restricted_capabilities(self):
        for restricted in RESTRICTED_CAPABILITIES:
            cap = AgentCapability(agent_id="agent-6", capabilities=["read", restricted])
            result = verify_capability_scope(cap)
            assert result["approved"] is False


@pytest.mark.skipif(not (_IMPORT_OK and _CAPABILITY_OK), reason="import failed")
class TestCapabilityCheckConstants:
    def test_max_capabilities_positive(self):
        assert MAX_CAPABILITIES > 0

    def test_restricted_capabilities_non_empty(self):
        assert len(RESTRICTED_CAPABILITIES) > 0

    def test_destroy_is_restricted(self):
        assert "destroy" in RESTRICTED_CAPABILITIES
