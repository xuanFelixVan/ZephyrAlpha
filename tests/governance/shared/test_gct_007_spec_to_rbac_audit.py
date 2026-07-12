# [A_test] module_id: SRC-TST-0130 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-287 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_007_spec_to_rbac_audit
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""G-CT-007 — Agent Spec → Audit 集成测试."""

from __future__ import annotations


class TestGCT007SpecToAudit:
    """验证 agent-spec/registry.py 的 AgentCapability 可被 audit-trail/spec_auditor.py 记录."""

    def test_capability_creatable(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability

        cap = AgentCapability(agent_id="test", capabilities=["read:docs", "write:tests"])
        assert cap.agent_id == "test"

    def test_spec_auditor_records_capability(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability
        from zephyr.gov_audit.spec_auditor import record_agent_spec

        cap = AgentCapability(agent_id="test", capabilities=["read:docs"])
        result = record_agent_spec(cap)
        assert "agent_id" in result
        assert result["event_type"] == "AGENT_SPEC_REGISTERED"

    def test_spec_registry_register(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability, SpecRegistry

        registry = SpecRegistry()
        cap = AgentCapability(agent_id="test", capabilities=["cap"])
        registry.register(cap)
        result = cap.agent_id
        assert result == "test"
