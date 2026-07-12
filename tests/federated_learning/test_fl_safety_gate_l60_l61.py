# [A_test] module_id: SRC-TST-0993 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L60_L61
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L60_L61
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L60_L61.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l60_l61 import SafetyGateL60L61


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL60L61Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL60L61()
        assert gate.exchange_halted is False
        assert gate.corporate_event_active is False
        assert gate.burnout_risk == 0.0


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL60L61()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l60_exchange_halted_rejects(self):
        gate = SafetyGateL60L61()
        gate.exchange_halted = True
        results = gate.evaluate(_ctx())
        l60 = [r for r in results if r.layer == "L60"]
        assert l60[0].verdict == GateVerdict.REJECT

    def test_l60_corporate_event_observes(self):
        gate = SafetyGateL60L61()
        gate.corporate_event_active = True
        results = gate.evaluate(_ctx())
        l60 = [r for r in results if r.layer == "L60"]
        assert l60[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l61_owner_burnout_rejects(self):
        gate = SafetyGateL60L61()
        ctx = _ctx(owner_fatigue=0.9)
        results = gate.evaluate(ctx)
        l61 = [r for r in results if r.layer == "L61"]
        assert l61[0].verdict == GateVerdict.REJECT


class TestBoundaries:
    def test_l61_owner_fatigue_at_threshold_passes(self):
        gate = SafetyGateL60L61()
        ctx = _ctx(owner_fatigue=0.8)
        results = gate.evaluate(ctx)
        l61 = [r for r in results if r.layer == "L61"]
        assert l61[0].verdict == GateVerdict.PASS
