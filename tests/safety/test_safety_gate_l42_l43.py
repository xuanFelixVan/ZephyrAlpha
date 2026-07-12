# [A_test] module_id: SRC-TST-1508 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L42_L43
# [INVARIANTS] CF harm>0.2 must reject; data_expired must reject; no checkpoints must block upgrade
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l42_l43 import SafetyGateL42L43


class TestSafetyGateL42L43Instantiation:
    def test_default_values(self):
        gate = SafetyGateL42L43()
        assert gate.counterfactual_harm_rate == 0.0
        assert gate.decision_entropy == 0.0
        assert gate.net_value == 0.0
        assert gate.data_expired is False
        assert gate.checkpoints_count == 0


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL42L43()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l42_cf_harm_rejects(self):
        gate = SafetyGateL42L43()
        gate.counterfactual_harm_rate = 0.3
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l42_entropy_observe(self):
        gate = SafetyGateL42L43()
        gate.decision_entropy = 0.9
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l43_net_negative_observe(self):
        gate = SafetyGateL42L43()
        gate.net_value = -1.0
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l43 = [r for r in results if r.layer == "L43"]
        assert len(l43) == 1
        assert l43[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l43_data_expired_rejects(self):
        gate = SafetyGateL42L43()
        gate.data_expired = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l43 = [r for r in results if r.layer == "L43"]
        assert len(l43) == 1
        assert l43[0].verdict == GateVerdict.REJECT

    def test_l43_no_checkpoints_blocks_upgrade(self):
        gate = SafetyGateL42L43()
        gate.checkpoints_count = 0
        ctx = ActionContext(action_id="a1", action_type="SELF_UPGRADE")
        results = gate.evaluate(ctx)
        l43 = [r for r in results if r.layer == "L43"]
        assert len(l43) == 1
        assert l43[0].verdict == GateVerdict.REJECT
