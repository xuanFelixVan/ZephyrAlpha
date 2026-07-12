# [A_test] module_id: SRC-TST-1504 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L28_L29
# [INVARIANTS] DR drill overdue must block REPAIR/DEPLOY; skill_trust<0.5 must block
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

import time

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l28_l29 import SafetyGateL28L29


class TestSafetyGateL28L29Instantiation:
    def test_default_values(self):
        gate = SafetyGateL28L29()
        assert gate.last_drill == 0.0
        assert gate.cve_active == []
        assert gate.skill_trust == 1.0


class TestEvaluate:
    def test_pass_when_no_issues(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time()
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l28_drill_overdue_blocks_repair(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time() - 86400 * 100
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert results[0].layer == "L28"
        assert results[0].verdict == GateVerdict.REJECT

    def test_l28_drill_overdue_blocks_deploy(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time() - 86400 * 100
        ctx = ActionContext(action_id="a1", action_type="DEPLOY")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_l28_drill_overdue_allows_notify(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time() - 86400 * 100
        ctx = ActionContext(action_id="a1", action_type="NOTIFY")
        results = gate.evaluate(ctx)
        assert results[0].verdict == GateVerdict.PASS

    def test_l29_cve_active_observe(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time()
        gate.cve_active = ["CVE-2024-0001"]
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l29 = [r for r in results if r.layer == "L29"]
        assert len(l29) == 1
        assert l29[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l29_low_skill_trust_rejects(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time()
        gate.skill_trust = 0.3
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        l29 = [r for r in results if r.layer == "L29"]
        assert len(l29) == 1
        assert l29[0].verdict == GateVerdict.REJECT

    def test_l28_reject_short_circuits_l29(self):
        gate = SafetyGateL28L29()
        gate.last_drill = 0.0
        gate.skill_trust = 0.3
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = gate.evaluate(ctx)
        assert len(results) == 1
        assert results[0].layer == "L28"
