# [A_test] module_id: SRC-TST-1519 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L64_L65
# [INVARIANTS] pre-trade risk fail must reject; PnL unreconciled must observe
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l64_l65 import SafetyGateL64L65


class TestSafetyGateL64L65Instantiation:
    def test_default_values(self):
        gate = SafetyGateL64L65()
        assert gate.pre_trade_risk_ok is True
        assert gate.pnl_reconciled is True
        assert gate.kb_injection_defense_active is False


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL64L65()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l64_pre_trade_risk_rejects(self):
        gate = SafetyGateL64L65()
        gate.pre_trade_risk_ok = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l64_pnl_unreconciled_observe(self):
        gate = SafetyGateL64L65()
        gate.pnl_reconciled = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l65_default_passes(self):
        gate = SafetyGateL64L65()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l65 = [r for r in results if r.layer == "L65"]
        assert len(l65) == 1
        assert l65[0].verdict == GateVerdict.PASS

    def test_returns_two_results(self):
        gate = SafetyGateL64L65()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert len(results) == 2
