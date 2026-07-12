# [A_test] module_id: SRC-TST-0989 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L52_L53
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L52_L53
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L52_L53.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l52_l53 import SafetyGateL52L53


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL52L53Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL52L53()
        assert gate.boot_measurement_ok is True
        assert gate.spdx_compliant is True


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL52L53()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l52_boot_measurement_fails(self):
        gate = SafetyGateL52L53()
        gate.boot_measurement_ok = False
        results = gate.evaluate(_ctx())
        l52 = [r for r in results if r.layer == "L52"]
        assert l52[0].verdict == GateVerdict.REJECT

    def test_l53_spdx_non_compliant(self):
        gate = SafetyGateL52L53()
        gate.spdx_compliant = False
        results = gate.evaluate(_ctx())
        l53 = [r for r in results if r.layer == "L53"]
        assert l53[0].verdict == GateVerdict.REJECT


class TestBoundaries:
    def test_both_fail_both_reject(self):
        gate = SafetyGateL52L53()
        gate.boot_measurement_ok = False
        gate.spdx_compliant = False
        results = gate.evaluate(_ctx())
        assert results[0].verdict == GateVerdict.REJECT
        assert results[1].verdict == GateVerdict.REJECT
