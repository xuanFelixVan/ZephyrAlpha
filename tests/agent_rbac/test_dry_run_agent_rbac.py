# [A_test] module_id: MOD-GOV_dry_run_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_dry_run
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试 L7 DryRun — 权限模拟与影响分析"""

from zephyr.security.access_control.dry_run import DryRunResult, DryRunSimulator, ImpactAnalysis
from zephyr.security.access_control.identity import AgentIdentity


class TestDryRun:
    def test_no_guard_defaults_allow(self):
        sim = DryRunSimulator()
        agent = AgentIdentity(session_id="dr-test")
        result = sim.simulate(agent, "write:src")
        assert result.would_succeed
        assert result.operation == "write:src"

    def test_with_guard(self):
        from zephyr.security.access_control.guards.rbac_guard import RBACGuard

        sim = DryRunSimulator()
        sim.set_guard(RBACGuard())
        agent = AgentIdentity(session_id="dr-test-2")
        result = sim.simulate(agent, "read:docs")
        assert result.would_succeed

    def test_impact_analysis_basic(self):
        sim = DryRunSimulator()
        agents = [
            AgentIdentity(session_id="a1", permissions=["read:docs"]),
            AgentIdentity(session_id="a2", permissions=["write:src"]),
        ]
        analysis = sim.impact_analysis(agents, ["read:docs", "write:src"], {"change": "test"})
        assert isinstance(analysis, ImpactAnalysis)
        assert analysis.change_description

    def test_dry_run_result_fields(self):
        result = DryRunResult(
            operation="test:op",
            would_be_decision="BLOCKED",
            would_be_layer="L0",
            would_be_reason="Immutable core block",
            would_succeed=False,
        )
        assert result.would_be_decision == "BLOCKED"
        assert not result.would_succeed
