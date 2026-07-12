# [A_test] module_id: SRC-TST-0977 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_parameterized_safety_gate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.parameterized_safety_gate
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_parameterized_safety_gate.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.parameterized_safety_gate import (
    ActionContext,
    GateVerdict,
    ParameterizedSafetyGate,
)


class TestParameterizedSafetyGateInstantiation:
    def test_default_construction(self):
        psg = ParameterizedSafetyGate()
        assert psg.rules == []
        assert psg.results == []

    def test_construction_with_rules(self):
        rules = [{"layer": "TEST", "type": "always_pass", "gate_type": "HARD"}]
        psg = ParameterizedSafetyGate(rules=rules)
        assert len(psg.rules) == 1


class TestEvaluate:
    def test_evaluate_always_pass_rule(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {"layer": "L_TEST", "type": "always_pass", "gate_type": "HARD"},
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = psg.evaluate(ctx)
        assert len(results) == 1
        assert results[0].verdict == GateVerdict.PASS

    def test_evaluate_threshold_rule_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L_SEV",
                    "type": "threshold",
                    "field": "severity",
                    "threshold": 8,
                    "op": "gt",
                    "gate_type": "HARD",
                    "reject_reason": "Severity {value} > {threshold}",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", severity=9)
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_evaluate_threshold_rule_pass(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L_SEV",
                    "type": "threshold",
                    "field": "severity",
                    "threshold": 8,
                    "op": "gt",
                    "gate_type": "HARD",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", severity=5)
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.PASS

    def test_evaluate_boolean_rule_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L_RBAC",
                    "type": "boolean",
                    "field": "rbac_authorized",
                    "expected": True,
                    "gate_type": "HARD",
                    "reject_reason": "RBAC denied",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", rbac_authorized=False)
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_evaluate_frequency_rule(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L_FREQ",
                    "type": "frequency",
                    "limit": 2,
                    "gate_type": "SOFT",
                    "reject_reason": "Rate limit exceeded",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        psg.evaluate(ctx)
        psg.evaluate(ctx)
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_hard_reject_short_circuits(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {"layer": "L1", "type": "always_pass", "gate_type": "HARD"},
                {
                    "layer": "L2",
                    "type": "threshold",
                    "field": "severity",
                    "threshold": 0,
                    "op": "gt",
                    "gate_type": "HARD",
                    "reject_reason": "blocked",
                },
                {"layer": "L3", "type": "always_pass", "gate_type": "HARD"},
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", severity=5)
        results = psg.evaluate(ctx)
        assert len(results) == 2
        assert results[1].verdict == GateVerdict.REJECT


class TestProperties:
    def test_is_blocked_false_when_no_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {"layer": "L1", "type": "always_pass", "gate_type": "HARD"},
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        psg.results = psg.evaluate(ctx)
        assert psg.is_blocked is False

    def test_is_blocked_true_when_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L1",
                    "type": "threshold",
                    "field": "severity",
                    "threshold": 0,
                    "op": "gt",
                    "gate_type": "HARD",
                    "reject_reason": "blocked",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", severity=5)
        psg.results = psg.evaluate(ctx)
        assert psg.is_blocked is True

    def test_reject_trace(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L1",
                    "type": "threshold",
                    "field": "severity",
                    "threshold": 0,
                    "op": "gt",
                    "gate_type": "HARD",
                    "reject_reason": "blocked",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", severity=5)
        psg.results = psg.evaluate(ctx)
        trace = psg.reject_trace
        assert len(trace) > 0
        assert "L1" in trace[0]


class TestBoundaries:
    def test_evaluate_empty_rules(self):
        psg = ParameterizedSafetyGate(rules=[])
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = psg.evaluate(ctx)
        assert results == []

    def test_evaluate_enum_rule(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L_ENUM",
                    "type": "enum",
                    "field": "action_type",
                    "allowed_values": ["REPAIR", "DIAGNOSE"],
                    "gate_type": "HARD",
                    "reject_reason": "Invalid action {value}",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="DEPLOY")
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT
