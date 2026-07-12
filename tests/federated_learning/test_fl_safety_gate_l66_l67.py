# [A_test] module_id: SRC-TST-0996 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L66_L67
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L66_L67
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L66_L67.py
# [TTL] task_bound

from unittest.mock import patch

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l66_l67 import SafetyGateL66L67


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL66L67Instantiation:
    def test_default_construction(self):
        with patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core"):
            gate = SafetyGateL66L67()
            assert gate.audit_log == []


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        with patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core"):
            gate = SafetyGateL66L67()
            results = gate.evaluate(_ctx())
            assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l66_compliance_fail_rejects(self):
        with patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core"):
            gate = SafetyGateL66L67()
            ctx = _ctx(compliance_ok=False)
            results = gate.evaluate(ctx)
            l66 = [r for r in results if r.layer == "L66"]
            assert l66[0].verdict == GateVerdict.REJECT

    def test_l67_rejects_when_upstream_rejects(self):
        with patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core"):
            gate = SafetyGateL66L67()
            ctx = _ctx(compliance_ok=False)
            results = gate.evaluate(ctx)
            l67 = [r for r in results if r.layer == "L67"]
            assert l67[0].verdict == GateVerdict.REJECT


class TestAuditLog:
    def test_evaluate_creates_audit_entries(self):
        with patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core"):
            gate = SafetyGateL66L67()
            gate.evaluate(_ctx())
            assert len(gate.audit_log) == 2

    def test_full_audit_trace(self):
        with patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core"):
            gate = SafetyGateL66L67()
            gate.evaluate(_ctx())
            trace = gate.full_audit_trace()
            assert "L66" in trace
            assert "L67" in trace


class TestBoundaries:
    def test_l66_pass_l67_pass(self):
        with patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core"):
            gate = SafetyGateL66L67()
            results = gate.evaluate(_ctx())
            assert results[0].verdict == GateVerdict.PASS
            assert results[1].verdict == GateVerdict.PASS
