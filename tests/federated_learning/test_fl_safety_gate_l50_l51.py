# [A_test] module_id: SRC-TST-0988 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L50_L51
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L50_L51
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L50_L51.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l50_l51 import SafetyGateL50L55


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL50L55Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL50L55()
        assert gate.coherence_score == 1.0
        assert gate.runtime_integrity is True
        assert gate.boot_attestation_ok is True
        assert gate.e2e_validation is True


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL50L55()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l50_coherence_low_rejects(self):
        gate = SafetyGateL50L55()
        gate.coherence_score = 0.5
        results = gate.evaluate(_ctx())
        l50 = [r for r in results if r.layer == "L50"]
        assert l50[0].verdict == GateVerdict.REJECT

    def test_l52_runtime_integrity_rejects(self):
        gate = SafetyGateL50L55()
        gate.runtime_integrity = False
        results = gate.evaluate(_ctx())
        l52 = [r for r in results if r.layer == "L52"]
        assert l52[0].verdict == GateVerdict.REJECT

    def test_l53_boot_attestation_rejects(self):
        gate = SafetyGateL50L55()
        gate.boot_attestation_ok = False
        results = gate.evaluate(_ctx())
        l53 = [r for r in results if r.layer == "L53"]
        assert l53[0].verdict == GateVerdict.REJECT

    def test_l54_e2e_validation_rejects(self):
        gate = SafetyGateL50L55()
        gate.e2e_validation = False
        results = gate.evaluate(_ctx())
        l54 = [r for r in results if r.layer == "L54"]
        assert l54[0].verdict == GateVerdict.REJECT

    def test_l55_final_rejects_when_upstream_rejects(self):
        gate = SafetyGateL50L55()
        gate.runtime_integrity = False
        results = gate.evaluate(_ctx())
        l55 = [r for r in results if r.layer == "L55"]
        assert l55[0].verdict == GateVerdict.REJECT


class TestBoundaries:
    def test_l50_coherence_at_threshold_passes(self):
        gate = SafetyGateL50L55()
        gate.coherence_score = 0.6
        results = gate.evaluate(_ctx())
        l50 = [r for r in results if r.layer == "L50"]
        assert l50[0].verdict == GateVerdict.PASS
