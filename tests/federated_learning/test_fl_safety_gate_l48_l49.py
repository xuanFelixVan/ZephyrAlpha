# [A_test] module_id: SRC-TST-0987 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L48_L49
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L48_L49
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L48_L49.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l48_l49 import SafetyGateL48L49


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL48L49Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL48L49()
        assert gate.dependency_integrity_ok is True
        assert gate.transitive_trust_score == 1.0
        assert gate.cognitive_budget_remaining_pct == 100.0
        assert gate.alert_flood_detected is False


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL48L49()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l48_dependency_integrity_broken_rejects(self):
        gate = SafetyGateL48L49()
        gate.dependency_integrity_ok = False
        results = gate.evaluate(_ctx())
        l48 = [r for r in results if r.layer == "L48"]
        assert l48[0].verdict == GateVerdict.REJECT

    def test_l48_transitive_trust_low_rejects(self):
        gate = SafetyGateL48L49()
        gate.transitive_trust_score = 0.3
        results = gate.evaluate(_ctx())
        l48 = [r for r in results if r.layer == "L48"]
        assert l48[0].verdict == GateVerdict.REJECT

    def test_l49_alert_flood_rejects(self):
        gate = SafetyGateL48L49()
        gate.alert_flood_detected = True
        results = gate.evaluate(_ctx())
        l49 = [r for r in results if r.layer == "L49"]
        assert l49[0].verdict == GateVerdict.REJECT

    def test_l49_cognitive_budget_low_observes(self):
        gate = SafetyGateL48L49()
        gate.cognitive_budget_remaining_pct = 5.0
        results = gate.evaluate(_ctx())
        l49 = [r for r in results if r.layer == "L49"]
        assert l49[0].verdict == GateVerdict.OBSERVE_ONLY


class TestBoundaries:
    def test_l48_transitive_trust_at_threshold_passes(self):
        gate = SafetyGateL48L49()
        gate.transitive_trust_score = 0.5
        results = gate.evaluate(_ctx())
        l48 = [r for r in results if r.layer == "L48"]
        assert l48[0].verdict == GateVerdict.PASS
