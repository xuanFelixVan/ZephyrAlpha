# [A_test] module_id: SRC-TST-1507 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L40_L41
# [INVARIANTS] Immutable core violation must reject; image drift must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l40_l41 import SafetyGateL40L41


class TestSafetyGateL40L41Instantiation:
    def test_default_values(self):
        gate = SafetyGateL40L41()
        assert gate.immutable_core_violation is False
        assert gate.operational_window_prohibited is False
        assert gate.container_mutable is False
        assert gate.image_drift_detected is False


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL40L41()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l40_immutable_core_rejects(self):
        gate = SafetyGateL40L41()
        gate.immutable_core_violation = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l40_operational_window_rejects(self):
        gate = SafetyGateL40L41()
        gate.operational_window_prohibited = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l41_image_drift_rejects(self):
        gate = SafetyGateL40L41()
        gate.image_drift_detected = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l41 = [r for r in results if r.layer == "L41"]
        assert len(l41) == 1
        assert l41[0].verdict == GateVerdict.REJECT

    def test_l41_container_mutable_observe(self):
        gate = SafetyGateL40L41()
        gate.container_mutable = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l41 = [r for r in results if r.layer == "L41"]
        assert len(l41) == 1
        assert l41[0].verdict == GateVerdict.OBSERVE_ONLY
