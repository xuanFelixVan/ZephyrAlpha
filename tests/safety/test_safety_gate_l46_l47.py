# [A_test] module_id: SRC-TST-1510 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L46_L47
# [INVARIANTS] vicious_spiral>30% must reject; diagnostic_consistency<0.7 must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l46_l47 import SafetyGateL46L47


class TestSafetyGateL46L47Instantiation:
    def test_default_values(self):
        gate = SafetyGateL46L47()
        assert gate.vicious_spiral_pct == 0.0
        assert gate.model_diversity == 1.0
        assert gate.backpressure_ratio == 0.0
        assert gate.diagnostic_consistency == 1.0
        assert gate.knowledge_freshness == 1.0
        assert gate.version_correct is True


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL46L47()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l46_vicious_spiral_rejects(self):
        gate = SafetyGateL46L47()
        gate.vicious_spiral_pct = 35.0
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l46_model_diversity_low_observe(self):
        gate = SafetyGateL46L47()
        gate.model_diversity = 0.2
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l46_backpressure_critical_observe(self):
        gate = SafetyGateL46L47()
        gate.backpressure_ratio = 0.95
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l47_diagnostic_consistency_rejects(self):
        gate = SafetyGateL46L47()
        gate.diagnostic_consistency = 0.5
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l47 = [r for r in results if r.layer == "L47"]
        assert len(l47) == 1
        assert l47[0].verdict == GateVerdict.REJECT

    def test_l47_knowledge_freshness_rejects(self):
        gate = SafetyGateL46L47()
        gate.knowledge_freshness = 0.3
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l47 = [r for r in results if r.layer == "L47"]
        assert len(l47) == 1
        assert l47[0].verdict == GateVerdict.REJECT

    def test_l47_version_mismatch_rejects(self):
        gate = SafetyGateL46L47()
        gate.version_correct = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l47 = [r for r in results if r.layer == "L47"]
        assert len(l47) == 1
        assert l47[0].verdict == GateVerdict.REJECT
