# [A_test] module_id: SRC-TST-0980 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L28_L29
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L28_L29
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L28_L29.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateVerdict
from zephyr.feedback_loop.gates.safety_gate_l28_l29 import SafetyGateL28L29


def _ctx(**overrides) -> ActionContext:
    defaults = dict(action_id="a1", action_type="REPAIR", severity=3)
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGateL28L29Instantiation:
    def test_default_construction(self):
        gate = SafetyGateL28L29()
        assert gate.last_drill == 0.0
        assert gate.cve_active == []
        assert gate.skill_trust == 1.0


class TestEvaluateDefaultPass:
    def test_default_context_passes_with_recent_drill(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time()
        ctx = _ctx()
        results = gate.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateReject:
    def test_l28_dr_overdue_repair_rejects(self):
        gate = SafetyGateL28L29()
        gate.last_drill = 0.0
        ctx = _ctx(action_type="REPAIR")
        results = gate.evaluate(ctx)
        l28 = [r for r in results if r.layer == "L28"]
        assert l28[0].verdict == GateVerdict.REJECT

    def test_l29_skill_trust_low_rejects(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time()
        gate.skill_trust = 0.3
        ctx = _ctx()
        results = gate.evaluate(ctx)
        l29 = [r for r in results if r.layer == "L29"]
        assert l29[0].verdict == GateVerdict.REJECT

    def test_l29_cve_active_observes(self):
        gate = SafetyGateL28L29()
        gate.last_drill = time.time()
        gate.cve_active = ["CVE-2024-0001"]
        ctx = _ctx()
        results = gate.evaluate(ctx)
        l29 = [r for r in results if r.layer == "L29"]
        assert l29[0].verdict == GateVerdict.OBSERVE_ONLY


class TestBoundaries:
    def test_l28_deploy_action_also_checked(self):
        gate = SafetyGateL28L29()
        gate.last_drill = 0.0
        ctx = _ctx(action_type="DEPLOY")
        results = gate.evaluate(ctx)
        l28 = [r for r in results if r.layer == "L28"]
        assert l28[0].verdict == GateVerdict.REJECT

    def test_l28_non_repair_action_passes(self):
        gate = SafetyGateL28L29()
        gate.last_drill = 0.0
        ctx = _ctx(action_type="DIAGNOSE")
        results = gate.evaluate(ctx)
        l28 = [r for r in results if r.layer == "L28"]
        assert l28[0].verdict == GateVerdict.PASS
