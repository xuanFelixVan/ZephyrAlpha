# [A_test] module_id: SRC-TST-0983 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L40_L41
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L40_L41
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L40_L41.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l40_l41 import SafetyGateL40L41


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL40L41Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL40L41()
        assert gate.immutable_core_violation is False
        assert gate.operational_window_prohibited is False
        assert gate.container_mutable is False
        assert gate.image_drift_detected is False


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL40L41()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l40_immutable_core_violation_rejects(self):
        gate = SafetyGateL40L41()
        gate.immutable_core_violation = True
        results = gate.evaluate(_ctx())
        l40 = [r for r in results if r.layer == "L40"]
        assert l40[0].verdict == GateVerdict.REJECT

    def test_l40_operational_window_prohibited_rejects(self):
        gate = SafetyGateL40L41()
        gate.operational_window_prohibited = True
        results = gate.evaluate(_ctx())
        l40 = [r for r in results if r.layer == "L40"]
        assert l40[0].verdict == GateVerdict.REJECT

    def test_l41_image_drift_rejects(self):
        gate = SafetyGateL40L41()
        gate.image_drift_detected = True
        results = gate.evaluate(_ctx())
        l41 = [r for r in results if r.layer == "L41"]
        assert l41[0].verdict == GateVerdict.REJECT

    def test_l41_container_mutable_observes(self):
        gate = SafetyGateL40L41()
        gate.container_mutable = True
        results = gate.evaluate(_ctx())
        l41 = [r for r in results if r.layer == "L41"]
        assert l41[0].verdict == GateVerdict.OBSERVE_ONLY


class TestBoundaries:
    def test_l40_both_violations_rejects_on_first(self):
        gate = SafetyGateL40L41()
        gate.immutable_core_violation = True
        gate.operational_window_prohibited = True
        results = gate.evaluate(_ctx())
        l40 = [r for r in results if r.layer == "L40"]
        assert l40[0].verdict == GateVerdict.REJECT
