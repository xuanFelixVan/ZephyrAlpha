# [A_test] module_id: SRC-TST-0985 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L44_L45
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L44_L45
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L44_L45.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l44_l45 import SafetyGateL44L45


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL44L45Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL44L45()
        assert gate.slo_compliant is True
        assert gate.api_contracts_intact is True
        assert gate.chain_amplification == 0.0
        assert gate.execution_quality == 1.0
        assert gate.noise_filter_ok is True
        assert gate.learning_ceiling_reached is False


class TestEvaluateDefaultPass:
    def test_default_context_passes(self):
        gate = SafetyGateL44L45()
        results = gate.evaluate(_ctx())
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l44_slo_non_compliant_rejects(self):
        gate = SafetyGateL44L45()
        gate.slo_compliant = False
        results = gate.evaluate(_ctx())
        l44 = [r for r in results if r.layer == "L44"]
        assert l44[0].verdict == GateVerdict.REJECT

    def test_l44_api_contracts_broken_rejects(self):
        gate = SafetyGateL44L45()
        gate.api_contracts_intact = False
        results = gate.evaluate(_ctx())
        l44 = [r for r in results if r.layer == "L44"]
        assert l44[0].verdict == GateVerdict.REJECT

    def test_l44_chain_amplification_observes(self):
        gate = SafetyGateL44L45()
        gate.chain_amplification = 1.5
        results = gate.evaluate(_ctx())
        l44 = [r for r in results if r.layer == "L44"]
        assert l44[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l45_execution_quality_degraded_rejects(self):
        gate = SafetyGateL44L45()
        gate.execution_quality = 0.3
        results = gate.evaluate(_ctx())
        l45 = [r for r in results if r.layer == "L45"]
        assert l45[0].verdict == GateVerdict.REJECT

    def test_l45_learning_ceiling_observes(self):
        gate = SafetyGateL44L45()
        gate.learning_ceiling_reached = True
        results = gate.evaluate(_ctx())
        l45 = [r for r in results if r.layer == "L45"]
        assert l45[0].verdict == GateVerdict.OBSERVE_ONLY


class TestBoundaries:
    def test_l45_execution_quality_at_threshold_passes(self):
        gate = SafetyGateL44L45()
        gate.execution_quality = 0.5
        results = gate.evaluate(_ctx())
        l45 = [r for r in results if r.layer == "L45"]
        assert l45[0].verdict == GateVerdict.PASS
