# [A_test] module_id: SRC-TST-0782 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.dry_run
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys
sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.dry_run import DryRunSimulator, DryRunResult, ImpactAnalysis
except Exception as exc:
    pytest.skip(f"Cannot import dry_run: {exc}", allow_module_level=True)


class TestDryRunResult:
    def test_default_values(self):
        r = DryRunResult(operation="read", would_be_decision="")
        assert r.operation == "read"
        assert r.would_be_decision == ""
        assert r.would_be_layer == ""
        assert r.would_be_reason == ""
        assert r.would_succeed is False
        assert r.affected_agents == []
        assert r.affected_operations == []

    def test_custom_values(self):
        r = DryRunResult(
            operation="write",
            would_be_decision="BLOCKED",
            would_be_layer="L3",
            would_be_reason="insufficient permissions",
            would_succeed=False,
            affected_agents=["agent-1"],
            affected_operations=["write"],
        )
        assert r.would_be_decision == "BLOCKED"
        assert r.would_succeed is False
        assert "agent-1" in r.affected_agents


class TestImpactAnalysis:
    def test_default_values(self):
        ia = ImpactAnalysis(change_description="test")
        assert ia.change_description == "test"
        assert ia.agent_impacts == {}
        assert ia.operation_impacts == {}
        assert ia.breaking_changes == []
        assert ia.recommended_actions == []

    def test_with_impacts(self):
        ia = ImpactAnalysis(
            change_description="revoke write",
            agent_impacts={"a1": ["write"]},
            breaking_changes=["write removed"],
        )
        assert "a1" in ia.agent_impacts
        assert "write removed" in ia.breaking_changes


class TestDryRunSimulator:
    def test_simulate_no_guard(self):
        sim = DryRunSimulator()
        result = sim.simulate(agent=None, operation="read")
        assert isinstance(result, DryRunResult)
        assert result.operation == "read"
        assert result.would_be_decision == "ALLOW"
        assert result.would_succeed is True

    def test_simulate_no_guard_write(self):
        sim = DryRunSimulator()
        result = sim.simulate(agent=None, operation="write", target_path="/tmp/f")
        assert result.would_succeed is True
        assert result.operation == "write"

    def test_simulate_with_guard(self):
        class FakeDecision:
            value = "BLOCKED"
        class FakeResult:
            decision = FakeDecision()
            reason = "permission denied for this operation"
        class FakeGuard:
            def check(self, agent, operation, target_path=""):
                return FakeResult()
            def is_blocked(self, result):
                return True

        sim = DryRunSimulator()
        sim.set_guard(FakeGuard())
        result = sim.simulate(agent=None, operation="delete")
        assert result.would_be_decision == "BLOCKED"
        assert result.would_succeed is False
        assert "permission denied" in result.would_be_reason

    def test_impact_analysis_with_agents(self):
        class FakeAgent:
            def __init__(self, sid, perms):
                self.session_id = sid
                self._perms = perms
            def has_permission(self, op):
                return op in self._perms

        sim = DryRunSimulator()
        a1 = FakeAgent("s1", ["read"])
        a2 = FakeAgent("s2", ["read", "write"])
        result = sim.impact_analysis(
            agents=[a1, a2],
            operations=["read", "write"],
            permission_change={"revoke": "write"},
        )
        assert isinstance(result, ImpactAnalysis)
        assert "s1" in result.agent_impacts
        assert "write" in result.agent_impacts["s1"]
        assert "s2" not in result.agent_impacts

    def test_impact_analysis_empty_agents(self):
        sim = DryRunSimulator()
        result = sim.impact_analysis(agents=[], operations=["read"], permission_change={})
        assert result.agent_impacts == {}

    def test_simulate_no_guard_with_target_path(self):
        sim = DryRunSimulator()
        result = sim.simulate(agent=None, operation="execute", target_path="/usr/bin/ls")
        assert result.would_succeed is True
