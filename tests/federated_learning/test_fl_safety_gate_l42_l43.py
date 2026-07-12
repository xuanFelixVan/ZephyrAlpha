# [A_test] module_id: SRC-TST-0984 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L42_L43
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L42_L43
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L42_L43.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l42_l43 import SafetyGateL42L43


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL42L43Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL42L43()
        assert gate.counterfactual_harm_rate == 0.0
        assert gate.decision_entropy == 0.0
        assert gate.net_value == 0.0
        assert gate.data_expired is False
        assert gate.checkpoints_count == 0


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL42L43()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l42_cf_harm_rate_rejects(self):
        gate = SafetyGateL42L43()
        gate.counterfactual_harm_rate = 0.3
        results = gate.evaluate(_ctx())
        l42 = [r for r in results if r.layer == "L42"]
        assert l42[0].verdict == GateVerdict.REJECT

    def test_l42_decision_entropy_observes(self):
        gate = SafetyGateL42L43()
        gate.decision_entropy = 0.9
        results = gate.evaluate(_ctx())
        l42 = [r for r in results if r.layer == "L42"]
        assert l42[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l43_net_negative_observes(self):
        gate = SafetyGateL42L43()
        gate.net_value = -1.0
        results = gate.evaluate(_ctx())
        l43 = [r for r in results if r.layer == "L43"]
        assert l43[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l43_data_expired_rejects(self):
        gate = SafetyGateL42L43()
        gate.data_expired = True
        results = gate.evaluate(_ctx())
        l43 = [r for r in results if r.layer == "L43"]
        assert l43[0].verdict == GateVerdict.REJECT

    def test_l43_no_checkpoints_self_upgrade_rejects(self):
        gate = SafetyGateL42L43()
        gate.checkpoints_count = 0
        ctx = _ctx(action_type="SELF_UPGRADE")
        results = gate.evaluate(ctx)
        l43 = [r for r in results if r.layer == "L43"]
        assert l43[0].verdict == GateVerdict.REJECT


class TestBoundaries:
    def test_l43_checkpoints_present_self_upgrade_passes(self):
        gate = SafetyGateL42L43()
        gate.checkpoints_count = 3
        ctx = _ctx(action_type="SELF_UPGRADE")
        results = gate.evaluate(ctx)
        l43 = [r for r in results if r.layer == "L43"]
        assert l43[0].verdict == GateVerdict.PASS
