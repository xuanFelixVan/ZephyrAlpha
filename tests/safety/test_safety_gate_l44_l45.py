# [A_test] module_id: SRC-TST-1509 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L44_L45
# [INVARIANTS] SLO non-compliant must reject; execution_quality<0.5 must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l44_l45 import SafetyGateL44L45


class TestSafetyGateL44L45Instantiation:
    def test_default_values(self):
        gate = SafetyGateL44L45()
        assert gate.slo_compliant is True
        assert gate.api_contracts_intact is True
        assert gate.chain_amplification == 0.0
        assert gate.execution_quality == 1.0
        assert gate.noise_filter_ok is True
        assert gate.learning_ceiling_reached is False


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL44L45()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l44_slo_noncompliant_rejects(self):
        gate = SafetyGateL44L45()
        gate.slo_compliant = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l44_api_contracts_broken_rejects(self):
        gate = SafetyGateL44L45()
        gate.api_contracts_intact = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l44_chain_amplification_observe(self):
        gate = SafetyGateL44L45()
        gate.chain_amplification = 1.5
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l45_learning_ceiling_observe(self):
        gate = SafetyGateL44L45()
        gate.learning_ceiling_reached = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l45 = [r for r in results if r.layer == "L45"]
        assert len(l45) == 1
        assert l45[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l45_execution_quality_rejects(self):
        gate = SafetyGateL44L45()
        gate.execution_quality = 0.3
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l45 = [r for r in results if r.layer == "L45"]
        assert len(l45) == 1
        assert l45[0].verdict == GateVerdict.REJECT
