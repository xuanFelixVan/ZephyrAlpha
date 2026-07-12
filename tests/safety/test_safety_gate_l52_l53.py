# [A_test] module_id: SRC-TST-1513 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L52_L53
# [INVARIANTS] Boot measurement mismatch must reject; SPDX non-compliant must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l52_l53 import SafetyGateL52L53


class TestSafetyGateL52L53Instantiation:
    def test_default_values(self):
        gate = SafetyGateL52L53()
        assert gate.boot_measurement_ok is True
        assert gate.spdx_compliant is True


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL52L53()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l52_boot_measurement_rejects(self):
        gate = SafetyGateL52L53()
        gate.boot_measurement_ok = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l53_spdx_noncompliant_rejects(self):
        gate = SafetyGateL52L53()
        gate.spdx_compliant = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[1].verdict == GateVerdict.REJECT

    def test_returns_two_results(self):
        gate = SafetyGateL52L53()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert len(results) == 2
