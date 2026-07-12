# [A_test] module_id: SRC-TST-1506 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L38_L39
# [INVARIANTS] HARD_BLOCK must reject; degradation>5% must block SELF_UPGRADE
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l38_l39 import SafetyGateL38L39


class TestSafetyGateL38L39Instantiation:
    def test_default_values(self):
        gate = SafetyGateL38L39()
        assert gate.hard_block_triggered is False
        assert gate.soft_block_triggered is False
        assert gate.monthly_degradation_pct == 0.0
        assert gate.cyclical_deps == 0


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL38L39()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l38_hard_block_rejects(self):
        gate = SafetyGateL38L39()
        gate.hard_block_triggered = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l38_soft_block_observe(self):
        gate = SafetyGateL38L39()
        gate.soft_block_triggered = True
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l39_degradation_blocks_self_upgrade(self):
        gate = SafetyGateL38L39()
        gate.monthly_degradation_pct = 6.0
        ctx = ActionContext(action_id="a1", action_type="SELF_UPGRADE")
        results = gate.evaluate(ctx)
        l39 = [r for r in results if r.layer == "L39"]
        assert len(l39) == 1
        assert l39[0].verdict == GateVerdict.REJECT

    def test_l39_degradation_allows_repair(self):
        gate = SafetyGateL38L39()
        gate.monthly_degradation_pct = 6.0
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l39 = [r for r in results if r.layer == "L39"]
        assert len(l39) == 1
        assert l39[0].verdict == GateVerdict.PASS

    def test_l39_cyclical_deps_rejects(self):
        gate = SafetyGateL38L39()
        gate.cyclical_deps = 6
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l39 = [r for r in results if r.layer == "L39"]
        assert len(l39) == 1
        assert l39[0].verdict == GateVerdict.REJECT
