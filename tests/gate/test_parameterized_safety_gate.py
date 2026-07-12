# [A_test] module_id: SRC-TST-1355 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_parameterized_safety_gate
# [INVARIANTS] HARD REJECT must short-circuit; is_blocked must reflect results
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.parameterized_safety_gate import (
    ActionContext,
    GateVerdict,
    ParameterizedSafetyGate,
)


class TestActionContextInstantiation:
    def test_default_values(self):
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        assert ctx.action_id == "a1"
        assert ctx.severity == 0
        assert ctx.autonomy_level == 0
        assert ctx.has_rollback is False
        assert ctx.compliance_ok is True


class TestParameterizedSafetyGateInstantiation:
    def test_default_no_rules(self):
        psg = ParameterizedSafetyGate()
        assert psg.rules == []

    def test_with_rules(self):
        rules = [{"layer": "L1", "gate_type": "HARD", "type": "always_pass"}]
        psg = ParameterizedSafetyGate(rules=rules)
        assert len(psg.rules) == 1


class TestEvaluate:
    def test_always_pass_rule(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {"layer": "L1", "gate_type": "HARD", "type": "always_pass"},
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = psg.evaluate(ctx)
        assert len(results) == 1
        assert results[0].verdict == GateVerdict.PASS

    def test_threshold_rule_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L5",
                    "gate_type": "HARD",
                    "type": "threshold",
                    "field": "severity",
                    "threshold": 8,
                    "op": "gt",
                    "reject_reason": "Severity {value} > {threshold}",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", severity=10)
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_threshold_rule_pass(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L5",
                    "gate_type": "HARD",
                    "type": "threshold",
                    "field": "severity",
                    "threshold": 8,
                    "op": "gt",
                    "reject_reason": "Severity too high",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", severity=5)
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.PASS

    def test_boolean_rule_mismatch_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L6",
                    "gate_type": "HARD",
                    "type": "boolean",
                    "field": "has_rollback",
                    "expected": True,
                    "reject_reason": "No rollback",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", has_rollback=False)
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_boolean_rule_match_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L20",
                    "gate_type": "HARD",
                    "type": "boolean",
                    "field": "in_circuit_breaker",
                    "expected": True,
                    "reject_on": "match",
                    "reject_reason": "In CB",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", in_circuit_breaker=True)
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_frequency_rule_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L2",
                    "gate_type": "SOFT",
                    "type": "frequency",
                    "key_field": "action_type",
                    "limit": 2,
                    "reject_reason": "Freq exceeded",
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
                {
                    "layer": "L1",
                    "gate_type": "HARD",
                    "type": "boolean",
                    "field": "has_rollback",
                    "expected": True,
                    "reject_reason": "No rollback",
                },
                {"layer": "L2", "gate_type": "HARD", "type": "always_pass"},
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", has_rollback=False)
        results = psg.evaluate(ctx)
        assert len(results) == 1

    def test_enum_rule_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L17",
                    "gate_type": "HARD",
                    "type": "enum",
                    "field": "action_type",
                    "allowed_values": ["REPAIR", "NOTIFY"],
                    "reject_reason": "Invalid type",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="DELETE")
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.REJECT

    def test_observe_rule(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L21",
                    "gate_type": "HARD",
                    "type": "observe",
                    "field": "cve_alerts",
                    "reject_reason": "CVE alert: {value}",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", cve_alerts=["CVE-2024-0001"])
        results = psg.evaluate(ctx)
        assert results[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_empty_rules(self):
        psg = ParameterizedSafetyGate(rules=[])
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        results = psg.evaluate(ctx)
        assert results == []


class TestIsBlocked:
    def test_not_blocked_when_all_pass(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {"layer": "L1", "gate_type": "HARD", "type": "always_pass"},
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        psg.results = psg.evaluate(ctx)
        assert psg.is_blocked is False

    def test_blocked_when_reject(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L1",
                    "gate_type": "HARD",
                    "type": "boolean",
                    "field": "has_rollback",
                    "expected": True,
                    "reject_reason": "No rollback",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", has_rollback=False)
        psg.results = psg.evaluate(ctx)
        assert psg.is_blocked is True


class TestRejectTrace:
    def test_empty_when_no_rejects(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {"layer": "L1", "gate_type": "HARD", "type": "always_pass"},
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        psg.results = psg.evaluate(ctx)
        assert psg.reject_trace == []

    def test_contains_reject_info(self):
        psg = ParameterizedSafetyGate(
            rules=[
                {
                    "layer": "L1",
                    "gate_type": "HARD",
                    "type": "boolean",
                    "field": "has_rollback",
                    "expected": True,
                    "reject_reason": "No rollback",
                },
            ]
        )
        ctx = ActionContext(action_id="a1", action_type="REPAIR", has_rollback=False)
        psg.results = psg.evaluate(ctx)
        assert len(psg.reject_trace) == 1
        assert "L1" in psg.reject_trace[0]
