# [A_test] module_id: SRC-TST-0982 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L38_L39
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L38_L39
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L38_L39.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l38_l39 import SafetyGateL38L39


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL38L39Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL38L39()
        assert gate.hard_block_triggered is False
        assert gate.soft_block_triggered is False
        assert gate.monthly_degradation_pct == 0.0
        assert gate.cyclical_deps == 0


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL38L39()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l38_hard_block_rejects(self):
        gate = SafetyGateL38L39()
        gate.hard_block_triggered = True
        results = gate.evaluate(_ctx())
        l38 = [r for r in results if r.layer == "L38"]
        assert l38[0].verdict == GateVerdict.REJECT

    def test_l38_soft_block_observes(self):
        gate = SafetyGateL38L39()
        gate.soft_block_triggered = True
        results = gate.evaluate(_ctx())
        l38 = [r for r in results if r.layer == "L38"]
        assert l38[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l39_degradation_self_upgrade_rejects(self):
        gate = SafetyGateL38L39()
        gate.monthly_degradation_pct = 6.0
        ctx = _ctx(action_type="SELF_UPGRADE")
        results = gate.evaluate(ctx)
        l39 = [r for r in results if r.layer == "L39"]
        assert l39[0].verdict == GateVerdict.REJECT

    def test_l39_cyclical_deps_rejects(self):
        gate = SafetyGateL38L39()
        gate.cyclical_deps = 6
        results = gate.evaluate(_ctx())
        l39 = [r for r in results if r.layer == "L39"]
        assert l39[0].verdict == GateVerdict.REJECT


class TestBoundaries:
    def test_l39_degradation_non_self_upgrade_passes(self):
        gate = SafetyGateL38L39()
        gate.monthly_degradation_pct = 6.0
        ctx = _ctx(action_type="REPAIR")
        results = gate.evaluate(ctx)
        l39 = [r for r in results if r.layer == "L39"]
        assert l39[0].verdict == GateVerdict.PASS
