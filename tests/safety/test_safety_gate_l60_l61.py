# [A_test] module_id: SRC-TST-1517 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L60_L61
# [INVARIANTS] exchange halted must reject; owner_fatigue>0.8 must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l60_l61 import SafetyGateL60L61


class TestSafetyGateL60L61Instantiation:
    def test_default_values(self):
        gate = SafetyGateL60L61()
        assert gate.exchange_halted is False
        assert gate.corporate_event_active is False
        assert gate.burnout_risk == 0.0


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL60L61()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l60_exchange_halted_rejects(self):
        gate = SafetyGateL60L61()
        gate.exchange_halted = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l60_corporate_event_observe(self):
        gate = SafetyGateL60L61()
        gate.corporate_event_active = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l61_owner_burnout_rejects(self):
        gate = SafetyGateL60L61()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", owner_fatigue=0.9)
        results = gate.evaluate(ctx)
        l61 = [r for r in results if r.layer == "L61"]
        assert len(l61) == 1
        assert l61[0].verdict == GateVerdict.REJECT

    def test_l61_normal_fatigue_passes(self):
        gate = SafetyGateL60L61()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", owner_fatigue=0.5)
        results = gate.evaluate(ctx)
        l61 = [r for r in results if r.layer == "L61"]
        assert len(l61) == 1
        assert l61[0].verdict == GateVerdict.PASS
