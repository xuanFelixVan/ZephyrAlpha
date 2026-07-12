# [A_test] module_id: SRC-TST-1518 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L62_L63
# [INVARIANTS] network partition must reject; immutable infra violated must reject
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l62_l63 import SafetyGateL62L63


class TestSafetyGateL62L63Instantiation:
    def test_default_values(self):
        gate = SafetyGateL62L63()
        assert gate.network_partition is False
        assert gate.immutable_infra_ok is True
        assert gate.self_api_throttled is False
        assert gate.intraday_anomaly is False


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL62L63()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l62_network_partition_rejects(self):
        gate = SafetyGateL62L63()
        gate.network_partition = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l62_immutable_infra_rejects(self):
        gate = SafetyGateL62L63()
        gate.immutable_infra_ok = False
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l63_self_api_throttled_observe(self):
        gate = SafetyGateL62L63()
        gate.self_api_throttled = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[1].verdict == GateVerdict.OBSERVE_ONLY

    def test_returns_two_results(self):
        gate = SafetyGateL62L63()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert len(results) == 2
