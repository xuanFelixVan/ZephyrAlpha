# [A_test] module_id: SRC-TST-1514 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L54_L55
# [INVARIANTS] L54 and L55 must always pass in default state
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l54_l55 import SafetyGateL54L55


class TestSafetyGateL54L55Instantiation:
    def test_default_creation(self):
        gate = SafetyGateL54L55()
        assert gate is not None


class TestEvaluate:
    def test_default_pass(self):
        gate = SafetyGateL54L55()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_returns_two_results(self):
        gate = SafetyGateL54L55()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert len(results) == 2

    def test_l54_layer_name(self):
        gate = SafetyGateL54L55()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].layer == "L54"

    def test_l55_layer_name(self):
        gate = SafetyGateL54L55()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[1].layer == "L55"
