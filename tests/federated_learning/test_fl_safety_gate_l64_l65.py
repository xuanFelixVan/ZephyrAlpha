# [A_test] module_id: SRC-TST-0995 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L64_L65
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L64_L65
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L64_L65.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l64_l65 import SafetyGateL64L65


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL64L65Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL64L65()
        assert gate.pre_trade_risk_ok is True
        assert gate.pnl_reconciled is True
        assert gate.kb_injection_defense_active is False


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL64L65()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l64_pre_trade_risk_fails(self):
        gate = SafetyGateL64L65()
        gate.pre_trade_risk_ok = False
        results = gate.evaluate(_ctx())
        l64 = [r for r in results if r.layer == "L64"]
        assert l64[0].verdict == GateVerdict.REJECT

    def test_l64_pnl_unreconciled_observes(self):
        gate = SafetyGateL64L65()
        gate.pnl_reconciled = False
        results = gate.evaluate(_ctx())
        l64 = [r for r in results if r.layer == "L64"]
        assert l64[0].verdict == GateVerdict.OBSERVE_ONLY


class TestBoundaries:
    def test_l65_always_passes(self):
        gate = SafetyGateL64L65()
        results = gate.evaluate(_ctx())
        l65 = [r for r in results if r.layer == "L65"]
        assert l65[0].verdict == GateVerdict.PASS
