# [A_test] module_id: SRC-TST-0986 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L46_L47
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L46_L47
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L46_L47.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l46_l47 import SafetyGateL46L47


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL46L47Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL46L47()
        assert gate.vicious_spiral_pct == 0.0
        assert gate.model_diversity == 1.0
        assert gate.backpressure_ratio == 0.0
        assert gate.diagnostic_consistency == 1.0
        assert gate.knowledge_freshness == 1.0
        assert gate.version_correct is True


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL46L47()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l46_vicious_spiral_rejects(self):
        gate = SafetyGateL46L47()
        gate.vicious_spiral_pct = 35.0
        results = gate.evaluate(_ctx())
        l46 = [r for r in results if r.layer == "L46"]
        assert l46[0].verdict == GateVerdict.REJECT

    def test_l46_model_diversity_low_observes(self):
        gate = SafetyGateL46L47()
        gate.model_diversity = 0.2
        results = gate.evaluate(_ctx())
        l46 = [r for r in results if r.layer == "L46"]
        assert l46[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l46_backpressure_critical_observes(self):
        gate = SafetyGateL46L47()
        gate.backpressure_ratio = 0.95
        results = gate.evaluate(_ctx())
        l46 = [r for r in results if r.layer == "L46"]
        assert l46[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l47_diagnostic_consistency_rejects(self):
        gate = SafetyGateL46L47()
        gate.diagnostic_consistency = 0.5
        results = gate.evaluate(_ctx())
        l47 = [r for r in results if r.layer == "L47"]
        assert l47[0].verdict == GateVerdict.REJECT

    def test_l47_knowledge_freshness_rejects(self):
        gate = SafetyGateL46L47()
        gate.knowledge_freshness = 0.4
        results = gate.evaluate(_ctx())
        l47 = [r for r in results if r.layer == "L47"]
        assert l47[0].verdict == GateVerdict.REJECT

    def test_l47_version_mismatch_rejects(self):
        gate = SafetyGateL46L47()
        gate.version_correct = False
        results = gate.evaluate(_ctx())
        l47 = [r for r in results if r.layer == "L47"]
        assert l47[0].verdict == GateVerdict.REJECT


class TestBoundaries:
    def test_l46_vicious_spiral_at_threshold_passes(self):
        gate = SafetyGateL46L47()
        gate.vicious_spiral_pct = 30.0
        results = gate.evaluate(_ctx())
        l46 = [r for r in results if r.layer == "L46"]
        assert l46[0].verdict == GateVerdict.PASS
