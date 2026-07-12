# [A_test] module_id: SRC-TST-0992 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L58_L59
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L58_L59
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L58_L59.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l58_l59 import SafetyGateL58L59


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL58L59Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL58L59()
        assert gate.explore_exploit_ratio == 0.5
        assert gate.third_party_model_risk == 0.0
        assert gate.ontology_drift == 0.0


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL58L59()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l59_third_party_model_risk_rejects(self):
        gate = SafetyGateL58L59()
        gate.third_party_model_risk = 0.8
        results = gate.evaluate(_ctx())
        l59 = [r for r in results if r.layer == "L59"]
        assert l59[0].verdict == GateVerdict.REJECT

    def test_l59_exploit_ratio_low_observes(self):
        gate = SafetyGateL58L59()
        gate.explore_exploit_ratio = 0.03
        results = gate.evaluate(_ctx())
        l59 = [r for r in results if r.layer == "L59"]
        assert l59[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l59_ontology_drift_observes(self):
        gate = SafetyGateL58L59()
        gate.ontology_drift = 0.5
        results = gate.evaluate(_ctx())
        l59 = [r for r in results if r.layer == "L59"]
        assert l59[0].verdict == GateVerdict.OBSERVE_ONLY


class TestBoundaries:
    def test_l58_always_passes(self):
        gate = SafetyGateL58L59()
        results = gate.evaluate(_ctx())
        l58 = [r for r in results if r.layer == "L58"]
        assert l58[0].verdict == GateVerdict.PASS
