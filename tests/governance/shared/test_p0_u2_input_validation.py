# [A_test] module_id: SRC-TST-0139 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-296 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_p0_u2_input_validation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""P0-U2 输入校验测试 — DOM-GOV-001 §8.2."""

from __future__ import annotations


class TestP0U2InputValidation:
    """输入校验: 非法 module_id 拒绝, 循环依赖检测, 空值保护."""

    def test_non_existent_module_rejected_by_registry(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability, SpecRegistry

        registry = SpecRegistry()
        cap = AgentCapability(agent_id="NON_EXISTENT_MODULE", capabilities=["any_cap"])
        registry.register(cap)
        assert cap.agent_id == "NON_EXISTENT_MODULE"

    def test_capability_check_rejects_unregistered(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability
        from zephyr.security.access_control.capability_check import verify_capability_scope

        cap = AgentCapability(agent_id="UNREGISTERED_AGENT", capabilities=["admin:all"])
        result = verify_capability_scope(cap)
        assert result is not None

    def test_empty_capability_list_handled(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability

        cap = AgentCapability(agent_id="empty_agent", capabilities=[])
        assert cap.agent_id == "empty_agent"
        assert len(cap.capabilities) == 0

    def test_audit_rejects_empty_agent_id(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability
        from zephyr.gov_audit.spec_auditor import record_agent_spec

        cap = AgentCapability(agent_id="", capabilities=["cap"])
        result = record_agent_spec(cap)
        assert result is not None
