# [A_test] module_id: SRC-TST-0990 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L54_L55
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L54_L55
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L54_L55.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l54_l55 import SafetyGateL54L55


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL54L55Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL54L55()
        assert gate is not None


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL54L55()
        results = gate.evaluate(_ctx())
        assert len(results) == 2
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateLayers:
    def test_l54_passes(self):
        gate = SafetyGateL54L55()
        results = gate.evaluate(_ctx())
        l54 = [r for r in results if r.layer == "L54"]
        assert l54[0].verdict == GateVerdict.PASS

    def test_l55_passes(self):
        gate = SafetyGateL54L55()
        results = gate.evaluate(_ctx())
        l55 = [r for r in results if r.layer == "L55"]
        assert l55[0].verdict == GateVerdict.PASS


class TestBoundaries:
    def test_results_contain_exactly_two(self):
        gate = SafetyGateL54L55()
        results = gate.evaluate(_ctx())
        assert len(results) == 2
