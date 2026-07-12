# [A_test] module_id: SRC-TST-0991 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L56_L57
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L56_L57
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L56_L57.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l56_l57 import SafetyGateL56L57


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL56L57Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL56L57()
        assert gate.evolution_debt == 0.0
        assert gate.purpose_drift == 0.0
        assert gate.loop_detected is False


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL56L57()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l56_evolution_debt_rejects(self):
        gate = SafetyGateL56L57()
        gate.evolution_debt = 0.6
        results = gate.evaluate(_ctx())
        l56 = [r for r in results if r.layer == "L56"]
        assert l56[0].verdict == GateVerdict.REJECT

    def test_l56_purpose_drift_observes(self):
        gate = SafetyGateL56L57()
        gate.purpose_drift = 0.4
        results = gate.evaluate(_ctx())
        l56 = [r for r in results if r.layer == "L56"]
        assert l56[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l56_loop_detected_rejects(self):
        gate = SafetyGateL56L57()
        gate.loop_detected = True
        results = gate.evaluate(_ctx())
        l56 = [r for r in results if r.layer == "L56"]
        assert l56[0].verdict == GateVerdict.REJECT


class TestBoundaries:
    def test_l57_always_passes(self):
        gate = SafetyGateL56L57()
        results = gate.evaluate(_ctx())
        l57 = [r for r in results if r.layer == "L57"]
        assert l57[0].verdict == GateVerdict.PASS
