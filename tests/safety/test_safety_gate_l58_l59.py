# [A_test] module_id: SRC-TST-1516 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L58_L59
# [INVARIANTS] third_party_model_risk>0.7 must reject; explore/exploit<0.05 must observe
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l58_l59 import SafetyGateL58L59


class TestSafetyGateL58L59Instantiation:
    def test_default_values(self):
        gate = SafetyGateL58L59()
        assert gate.explore_exploit_ratio == 0.5
        assert gate.third_party_model_risk == 0.0
        assert gate.ontology_drift == 0.0


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL58L59()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l58_always_passes(self):
        gate = SafetyGateL58L59()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].layer == "L58"
        assert results[0].verdict == GateVerdict.PASS

    def test_l59_low_explore_exploit_observe(self):
        gate = SafetyGateL58L59()
        gate.explore_exploit_ratio = 0.03
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[1].verdict == GateVerdict.OBSERVE_ONLY

    def test_l59_third_party_risk_rejects(self):
        gate = SafetyGateL58L59()
        gate.third_party_model_risk = 0.8
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[1].verdict == GateVerdict.REJECT

    def test_l59_ontology_drift_observe(self):
        gate = SafetyGateL58L59()
        gate.ontology_drift = 0.5
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[1].verdict == GateVerdict.OBSERVE_ONLY
