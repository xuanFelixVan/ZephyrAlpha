# [A_test] module_id: SRC-TST-0981 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L36_L37
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L36_L37
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L36_L37.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l36_l37 import SafetyGateL36L37


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL36L37Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL36L37()
        assert gate.context_rot == 0.0
        assert gate.dilution == 0.0
        assert gate.worsening == 0.0
        assert gate.trust_decay == 0.0


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL36L37()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l36_context_rot_and_dilution_observes(self):
        gate = SafetyGateL36L37()
        gate.context_rot = 0.4
        gate.dilution = 0.35
        results = gate.evaluate(_ctx())
        l36 = [r for r in results if r.layer == "L36"]
        assert l36[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l37_trust_decay_high_rejects(self):
        gate = SafetyGateL36L37()
        gate.trust_decay = 0.1
        results = gate.evaluate(_ctx())
        l37 = [r for r in results if r.layer == "L37"]
        assert l37[0].verdict == GateVerdict.REJECT

    def test_l37_worsening_high_observes(self):
        gate = SafetyGateL36L37()
        gate.worsening = 0.5
        results = gate.evaluate(_ctx())
        l37 = [r for r in results if r.layer == "L37"]
        assert l37[0].verdict == GateVerdict.OBSERVE_ONLY


class TestBoundaries:
    def test_l36_rot_without_dilution_passes(self):
        gate = SafetyGateL36L37()
        gate.context_rot = 0.5
        gate.dilution = 0.1
        results = gate.evaluate(_ctx())
        l36 = [r for r in results if r.layer == "L36"]
        assert l36[0].verdict == GateVerdict.PASS
