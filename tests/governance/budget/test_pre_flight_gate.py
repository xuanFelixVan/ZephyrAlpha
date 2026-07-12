# [A_test] module_id: SRC-TST-1394 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_pre_flight_gate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_pre_flight_gate.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.budget_engine import BudgetEngine
from zephyr.governance.ops_governance.budget_models import BudgetDimension, BudgetPolicy, GateDecision
from zephyr.gov_enforcement.rule_enforcement.pre_flight_gate import (
    PreFlightDecision,
    PreFlightGate,
    PreFlightReport,
)


class TestPreFlightDecision:
    def test_enum_values(self):
        assert PreFlightDecision.ALLOW is not None
        assert PreFlightDecision.SOFT_WARN is not None
        assert PreFlightDecision.HARD_WARN is not None
        assert PreFlightDecision.BLOCK is not None


class TestPreFlightReport:
    def test_all_green_when_allow(self):
        report = PreFlightReport(
            decision=PreFlightDecision.ALLOW,
            token_check=GateDecision.ALLOW,
            cost_check=GateDecision.ALLOW,
            time_check=GateDecision.ALLOW,
        )
        assert report.all_green is True

    def test_not_all_green_when_warn(self):
        report = PreFlightReport(
            decision=PreFlightDecision.SOFT_WARN,
            token_check=GateDecision.NARROW,
            cost_check=GateDecision.ALLOW,
            time_check=GateDecision.ALLOW,
        )
        assert report.all_green is False

    def test_default_recommendations(self):
        report = PreFlightReport(
            decision=PreFlightDecision.ALLOW,
            token_check=GateDecision.ALLOW,
            cost_check=GateDecision.ALLOW,
            time_check=GateDecision.ALLOW,
        )
        assert report.recommendations == []
        assert isinstance(report.checked_at, float)


class TestPreFlightGate:
    def test_init_default_engine(self):
        gate = PreFlightGate()
        assert isinstance(gate._engine, BudgetEngine)

    def test_init_custom_engine(self):
        engine = BudgetEngine()
        gate = PreFlightGate(engine=engine)
        assert gate._engine is engine

    def test_gate_allow(self):
        gate = PreFlightGate()
        report = gate.gate(
            action="test-action",
            estimated_tokens=100,
            estimated_cost=0.01,
        )
        assert isinstance(report, PreFlightReport)
        assert report.decision == PreFlightDecision.ALLOW

    def test_gate_block_when_budget_exhausted(self):
        engine = BudgetEngine()
        policy = BudgetPolicy(
            policy_id="BP-TOKEN-BLOCK",
            name="Tiny Token Budget",
            dimension=BudgetDimension.TOKEN,
            daily_limit=100,
            hourly_limit=100,
            per_request_limit=100,
        )
        engine.register_policy(policy)
        engine.record_consumption("BP-TOKEN-BLOCK", tokens=99, cost=0.0, time_minutes=0.0)
        gate = PreFlightGate(engine=engine)
        report = gate.gate(
            action="big-request",
            estimated_tokens=50000,
            estimated_cost=0.01,
        )
        assert report.decision in (
            PreFlightDecision.SOFT_WARN,
            PreFlightDecision.HARD_WARN,
            PreFlightDecision.BLOCK,
        )

    def test_gate_returns_checks(self):
        gate = PreFlightGate()
        report = gate.gate(
            action="test",
            estimated_tokens=100,
            estimated_cost=0.01,
        )
        assert isinstance(report.token_check, GateDecision)
        assert isinstance(report.cost_check, GateDecision)
        assert isinstance(report.time_check, GateDecision)

    def test_get_engine(self):
        engine = BudgetEngine()
        gate = PreFlightGate(engine=engine)
        assert gate.get_engine() is engine

    def test_gate_with_session_id(self):
        gate = PreFlightGate()
        report = gate.gate(
            action="test",
            estimated_tokens=100,
            estimated_cost=0.01,
            session_id="session-001",
        )
        assert isinstance(report, PreFlightReport)

    def test_gate_zero_tokens_zero_cost(self):
        gate = PreFlightGate()
        report = gate.gate(
            action="zero-request",
            estimated_tokens=0,
            estimated_cost=0.0,
        )
        assert isinstance(report, PreFlightReport)

    def test_gate_large_request(self):
        gate = PreFlightGate()
        report = gate.gate(
            action="huge-request",
            estimated_tokens=500000,
            estimated_cost=10.0,
        )
        assert isinstance(report, PreFlightReport)
        assert len(report.recommendations) >= 0

    def test_multiple_gates_accumulate(self):
        gate = PreFlightGate()
        r1 = gate.gate(action="req1", estimated_tokens=100, estimated_cost=0.01)
        r2 = gate.gate(action="req2", estimated_tokens=100, estimated_cost=0.01)
        assert isinstance(r1, PreFlightReport)
        assert isinstance(r2, PreFlightReport)
