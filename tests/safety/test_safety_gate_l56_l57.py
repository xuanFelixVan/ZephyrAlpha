# [A_test] module_id: SRC-TST-1515 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L56_L57
# [INVARIANTS] evolution_debt>0.5 must reject; loop_detected must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l56_l57 import SafetyGateL56L57


class TestSafetyGateL56L57Instantiation:
    def test_default_values(self):
        gate = SafetyGateL56L57()
        assert gate.evolution_debt == 0.0
        assert gate.purpose_drift == 0.0
        assert gate.loop_detected is False


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL56L57()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l56_evolution_debt_rejects(self):
        gate = SafetyGateL56L57()
        gate.evolution_debt = 0.6
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l56_purpose_drift_observe(self):
        gate = SafetyGateL56L57()
        gate.purpose_drift = 0.4
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l56_loop_detected_rejects(self):
        gate = SafetyGateL56L57()
        gate.loop_detected = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l57_always_passes(self):
        gate = SafetyGateL56L57()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l57 = [r for r in results if r.layer == "L57"]
        assert len(l57) == 1
        assert l57[0].verdict == GateVerdict.PASS
