# [A_test] module_id: SRC-TST-0994 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L62_L63
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L62_L63
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L62_L63.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l62_l63 import SafetyGateL62L63


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL62L63Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL62L63()
        assert gate.network_partition is False
        assert gate.immutable_infra_ok is True
        assert gate.self_api_throttled is False
        assert gate.intraday_anomaly is False


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL62L63()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l62_network_partition_rejects(self):
        gate = SafetyGateL62L63()
        gate.network_partition = True
        results = gate.evaluate(_ctx())
        l62 = [r for r in results if r.layer == "L62"]
        assert l62[0].verdict == GateVerdict.REJECT

    def test_l62_immutable_infra_violated_rejects(self):
        gate = SafetyGateL62L63()
        gate.immutable_infra_ok = False
        results = gate.evaluate(_ctx())
        l62 = [r for r in results if r.layer == "L62"]
        assert l62[0].verdict == GateVerdict.REJECT

    def test_l63_self_api_throttled_observes(self):
        gate = SafetyGateL62L63()
        gate.self_api_throttled = True
        results = gate.evaluate(_ctx())
        l63 = [r for r in results if r.layer == "L63"]
        assert l63[0].verdict == GateVerdict.OBSERVE_ONLY


class TestBoundaries:
    def test_l63_default_passes(self):
        gate = SafetyGateL62L63()
        results = gate.evaluate(_ctx())
        l63 = [r for r in results if r.layer == "L63"]
        assert l63[0].verdict == GateVerdict.PASS
