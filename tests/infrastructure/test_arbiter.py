# [A_test] module_id: MOD-GOV_arbiter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_arbiter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_arbiter.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import (
    AgentMeta,
    AgentRole,
    ArbitrationResult,
    ArbitrationVerdict,
    Arbitrator,
    FileOwnership,
)


class TestArbitratorInstantiation:
    def test_creates_instance_without_args(self):
        arb = Arbitrator()
        assert isinstance(arb, Arbitrator)

    def test_creates_instance_with_engines(self):
        arb = Arbitrator(escalation_engine=object(), deadlock_detector=object())
        assert arb.escalation_engine is not None
        assert arb.deadlock_detector is not None

    def test_initial_audit_log_empty(self):
        arb = Arbitrator()
        assert arb.get_audit_log() == []


class TestTier1Priority:
    def test_superadmin_beats_builder(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.SUPERADMIN)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.winner == "A"
        assert result.loser == "B"
        assert result.tier == 1
        assert result.verdict == ArbitrationVerdict.AUTONOMOUS

    def test_builder_loses_to_superadmin(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER)
        b = AgentMeta(agent_id="B", role=AgentRole.SUPERADMIN)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.winner == "B"
        assert result.loser == "A"

    def test_same_role_uses_seniority(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER, tasks_completed=20)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER, tasks_completed=5)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.winner == "A"
        assert result.tier == 1


class TestTier2Ownership:
    def test_ownership_rule_applies(self):
        ownership = [FileOwnership("src/zephyr/governance/", AgentRole.GOVERNANCE)]
        arb = Arbitrator(ownership_rules=ownership)
        a = AgentMeta(agent_id="A", role=AgentRole.GOVERNANCE)
        b = AgentMeta(agent_id="B", role=AgentRole.REVIEWER)
        result = arb.arbitrate(a, b, ["src/zephyr/governance/test.py"])
        assert result.winner == "A"
        assert result.tier == 2

    def test_owned_files_boost_score(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER, owned_files=["file.py"])
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.winner == "A"
        assert result.tier == 2


class TestTier3Escalation:
    def test_equal_agents_escalate(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER, tasks_completed=5)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER, tasks_completed=5)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.tier == 3
        assert result.escalation is True
        assert result.winner is None
        assert result.loser is None

    def test_escalation_has_message(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["file.py"])
        assert "ESC-A2A" in result.escalation_message


class TestArbitrationVerdict:
    def test_tier1_verdict_autonomous(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.SUPERADMIN)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.verdict == ArbitrationVerdict.AUTONOMOUS

    def test_tier2_verdict_autonomous(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER, owned_files=["file.py"])
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.verdict == ArbitrationVerdict.AUTONOMOUS

    def test_tier3_verdict_auto_guard_without_engines(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.verdict == ArbitrationVerdict.AUTO_GUARD

    def test_tier3_verdict_blocked_with_deadlock(self):
        class MockDeadlockDetector:
            def detect_cycle(self, waiter, holder):
                return ["A", "B"]

        arb = Arbitrator(deadlock_detector=MockDeadlockDetector())
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.verdict == ArbitrationVerdict.BLOCKED

    def test_tier3_verdict_auto_guard_with_engine(self):
        class MockEngine:
            def evaluate(self, category, description, owner_id):
                return object()

        class MockDeadlockDetector:
            def detect_cycle(self, waiter, holder):
                return []

        arb = Arbitrator(escalation_engine=MockEngine(), deadlock_detector=MockDeadlockDetector())
        a = AgentMeta(agent_id="A", role=AgentRole.BUILDER)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["file.py"])
        assert result.verdict == ArbitrationVerdict.AUTO_GUARD


class TestAuditLog:
    def test_audit_log_records_arbitration(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.SUPERADMIN)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        arb.arbitrate(a, b, ["file.py"])
        log = arb.get_audit_log()
        assert len(log) == 1
        assert log[0]["agent_a"] == "A"
        assert log[0]["agent_b"] == "B"
        assert log[0]["winner"] == "A"

    def test_audit_log_records_multiple(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.SUPERADMIN)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        arb.arbitrate(a, b, ["file1.py"])
        arb.arbitrate(a, b, ["file2.py"])
        assert len(arb.get_audit_log()) == 2

    def test_clear_audit_log(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.SUPERADMIN)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        arb.arbitrate(a, b, ["file.py"])
        assert len(arb.get_audit_log()) == 1
        arb.clear_audit_log()
        assert len(arb.get_audit_log()) == 0

    def test_audit_log_includes_verdict(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.SUPERADMIN)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        arb.arbitrate(a, b, ["file.py"])
        log = arb.get_audit_log()
        assert log[0]["verdict"] == "AUTONOMOUS"

    def test_audit_log_includes_conflicted_files(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="A", role=AgentRole.SUPERADMIN)
        b = AgentMeta(agent_id="B", role=AgentRole.BUILDER)
        arb.arbitrate(a, b, ["file1.py", "file2.py"])
        log = arb.get_audit_log()
        assert log[0]["conflicted_files"] == ["file1.py", "file2.py"]


class TestAgentRole:
    def test_from_string_superadmin(self):
        assert AgentRole.from_string("superadmin") == AgentRole.SUPERADMIN

    def test_from_string_unknown_defaults_builder(self):
        assert AgentRole.from_string("unknown_role") == AgentRole.BUILDER

    def test_from_string_with_spaces(self):
        assert AgentRole.from_string("safety operator") == AgentRole.SAFETY_OPERATOR
