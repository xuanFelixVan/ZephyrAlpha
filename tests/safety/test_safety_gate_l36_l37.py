# [A_test] module_id: SRC-TST-1505 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L36_L37
# [INVARIANTS] context_rot>0.35+dilution>0.3 must observe; trust_decay>1.5*baseline must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l36_l37 import SafetyGateL36L37


class TestSafetyGateL36L37Instantiation:
    def test_default_values(self):
        gate = SafetyGateL36L37()
        assert gate.context_rot == 0.0
        assert gate.dilution == 0.0
        assert gate.worsening == 0.0
        assert gate.trust_decay == 0.0
        assert gate.baseline_decay == 0.05


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL36L37()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l36_context_rot_and_dilution_observe(self):
        gate = SafetyGateL36L37()
        gate.context_rot = 0.4
        gate.dilution = 0.35
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].layer == "L36"
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l36_context_rot_only_passes(self):
        gate = SafetyGateL36L37()
        gate.context_rot = 0.4
        gate.dilution = 0.1
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.PASS

    def test_l37_worsening_observe(self):
        gate = SafetyGateL36L37()
        gate.worsening = 0.5
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l37 = [r for r in results if r.layer == "L37"]
        assert len(l37) == 1
        assert l37[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l37_trust_decay_rejects(self):
        gate = SafetyGateL36L37()
        gate.trust_decay = 0.1
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l37 = [r for r in results if r.layer == "L37"]
        assert len(l37) == 1
        assert l37[0].verdict == GateVerdict.REJECT
