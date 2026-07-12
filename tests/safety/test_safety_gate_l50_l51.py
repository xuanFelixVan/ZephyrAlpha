# [A_test] module_id: SRC-TST-1512 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L50_L51
# [INVARIANTS] coherence<0.6 must reject; runtime integrity must reject; L55 depends on L52-L54
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l50_l51 import SafetyGateL50L55


class TestSafetyGateL50L55Instantiation:
    def test_default_values(self):
        gate = SafetyGateL50L55()
        assert gate.coherence_score == 1.0
        assert gate.runtime_integrity is True
        assert gate.boot_attestation_ok is True
        assert gate.e2e_validation is True


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL50L55()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l50_low_coherence_rejects(self):
        gate = SafetyGateL50L55()
        gate.coherence_score = 0.5
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].layer == "L50"
        assert results[0].verdict == GateVerdict.REJECT

    def test_l52_runtime_integrity_rejects(self):
        gate = SafetyGateL50L55()
        gate.runtime_integrity = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l52 = [r for r in results if r.layer == "L52"]
        assert len(l52) == 1
        assert l52[0].verdict == GateVerdict.REJECT

    def test_l53_boot_attestation_rejects(self):
        gate = SafetyGateL50L55()
        gate.boot_attestation_ok = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l53 = [r for r in results if r.layer == "L53"]
        assert len(l53) == 1
        assert l53[0].verdict == GateVerdict.REJECT

    def test_l54_e2e_rejects(self):
        gate = SafetyGateL50L55()
        gate.e2e_validation = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l54 = [r for r in results if r.layer == "L54"]
        assert len(l54) == 1
        assert l54[0].verdict == GateVerdict.REJECT

    def test_l55_rejects_when_upstream_rejects(self):
        gate = SafetyGateL50L55()
        gate.runtime_integrity = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l55 = [r for r in results if r.layer == "L55"]
        assert len(l55) == 1
        assert l55[0].verdict == GateVerdict.REJECT

    def test_returns_six_results(self):
        gate = SafetyGateL50L55()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert len(results) == 6
