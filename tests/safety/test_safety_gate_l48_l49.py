# [A_test] module_id: SRC-TST-1511 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L48_L49
# [INVARIANTS] dependency integrity broken must reject; alert flood must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l48_l49 import SafetyGateL48L49


class TestSafetyGateL48L49Instantiation:
    def test_default_values(self):
        gate = SafetyGateL48L49()
        assert gate.dependency_integrity_ok is True
        assert gate.transitive_trust_score == 1.0
        assert gate.cognitive_budget_remaining_pct == 100.0
        assert gate.alert_flood_detected is False


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL48L49()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l48_dependency_integrity_rejects(self):
        gate = SafetyGateL48L49()
        gate.dependency_integrity_ok = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l48_transitive_trust_rejects(self):
        gate = SafetyGateL48L49()
        gate.transitive_trust_score = 0.3
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l49_alert_flood_rejects(self):
        gate = SafetyGateL48L49()
        gate.alert_flood_detected = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l49 = [r for r in results if r.layer == "L49"]
        assert len(l49) == 1
        assert l49[0].verdict == GateVerdict.REJECT

    def test_l49_cognitive_budget_observe(self):
        gate = SafetyGateL48L49()
        gate.cognitive_budget_remaining_pct = 5.0
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l49 = [r for r in results if r.layer == "L49"]
        assert len(l49) == 1
        assert l49[0].verdict == GateVerdict.OBSERVE_ONLY
