# [A_test] module_id: SRC-TST-1520 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L66_L67
# [INVARIANTS] compliance fail must reject L66; upstream reject must reject L67
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from unittest.mock import patch

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l66_l67 import SafetyGateL66L67


class TestSafetyGateL66L67Instantiation:
    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_default_values(self, mock_write):
        gate = SafetyGateL66L67()
        assert gate.audit_log == []


class TestEvaluate:
    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_pass_when_compliant(self, mock_write):
        gate = SafetyGateL66L67()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", compliance_ok=True)
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_l66_compliance_fail_rejects(self, mock_write):
        gate = SafetyGateL66L67()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", compliance_ok=False)
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_l67_rejects_when_upstream_rejects(self, mock_write):
        gate = SafetyGateL66L67()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", compliance_ok=False)
        results = gate.evaluate(ctx)
        assert results[1].verdict == GateVerdict.REJECT

    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_l67_passes_when_upstream_passes(self, mock_write):
        gate = SafetyGateL66L67()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", compliance_ok=True)
        results = gate.evaluate(ctx)
        assert results[1].verdict == GateVerdict.PASS

    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_audit_log_populated(self, mock_write):
        gate = SafetyGateL66L67()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", compliance_ok=True)
        gate.evaluate(ctx)
        assert len(gate.audit_log) == 2

    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_write_to_core_called(self, mock_write):
        gate = SafetyGateL66L67()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", compliance_ok=True)
        gate.evaluate(ctx)
        assert mock_write.call_count == 2


class TestFullAuditTrace:
    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_trace_format(self, mock_write):
        gate = SafetyGateL66L67()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", compliance_ok=True)
        gate.evaluate(ctx)
        trace = gate.full_audit_trace()
        assert "L66" in trace
        assert "L67" in trace
        assert "PASS" in trace

    @patch("zephyr.trading.feedback_loop.gates.safety_gate_L66_L67.write_to_core")
    def test_trace_empty_before_evaluate(self, mock_write):
        gate = SafetyGateL66L67()
        trace = gate.full_audit_trace()
        assert trace == ""
