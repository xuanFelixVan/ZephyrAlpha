# [A_test] module_id: SRC-TST-0979 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_safety_gate_L1_L27
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.safety_gate_L1_L27
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_safety_gate_L1_L27.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import (
    ActionContext,
    GateVerdict,
    SafetyGatePipeline,
)


def _default_ctx(**overrides) -> ActionContext:
    defaults = dict(
        action_id="test-action",
        action_type="REPAIR",
        severity=3,
        autonomy_level=2,
        has_rollback=True,
        has_self_modification_audit=True,
        compliance_ok=True,
    )
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestSafetyGatePipelineInstantiation:
    def test_default_construction(self):
        sgp = SafetyGatePipeline()
        assert len(sgp.gates) == 27
        assert sgp.results == []

    def test_gate_names_start_with_L1(self):
        sgp = SafetyGatePipeline()
        assert sgp.gates[0][0] == "L1_BASIC_THRESHOLD"


class TestEvaluateDefaultContext:
    def test_default_context_passes_all(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx()
        results = sgp.evaluate(ctx)
        assert len(results) == 27
        assert all(r.verdict == GateVerdict.PASS for r in results)


class TestEvaluateRejectConditions:
    def test_l4_dependency_down_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(dependency_status={"db": False})
        results = sgp.evaluate(ctx)
        l4_results = [r for r in results if r.layer == "L4"]
        assert l4_results[0].verdict == GateVerdict.REJECT

    def test_l5_budget_exceeded_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(cost_estimate=500.0, budget_remaining=100.0)
        results = sgp.evaluate(ctx)
        l5_results = [r for r in results if r.layer == "L5"]
        assert l5_results[0].verdict == GateVerdict.REJECT

    def test_l6_no_rollback_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(has_rollback=False)
        results = sgp.evaluate(ctx)
        l6_results = [r for r in results if r.layer == "L6"]
        assert l6_results[0].verdict == GateVerdict.REJECT

    def test_l10_data_quality_critical_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(data_quality_score=30.0)
        results = sgp.evaluate(ctx)
        l10_results = [r for r in results if r.layer == "L10"]
        assert l10_results[0].verdict == GateVerdict.REJECT

    def test_l12_schema_mismatch_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(schema_version=2, expected_schema_version=1)
        results = sgp.evaluate(ctx)
        l12_results = [r for r in results if r.layer == "L12"]
        assert l12_results[0].verdict == GateVerdict.REJECT

    def test_l17_autonomy_exceeded_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(autonomy_level=5)
        results = sgp.evaluate(ctx)
        l17_results = [r for r in results if r.layer == "L17"]
        assert l17_results[0].verdict == GateVerdict.REJECT

    def test_l20_self_mod_not_audited_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(has_self_modification_audit=False)
        results = sgp.evaluate(ctx)
        l20_results = [r for r in results if r.layer == "L20"]
        assert l20_results[0].verdict == GateVerdict.REJECT

    def test_l21_cve_alerts_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(cve_alerts=["CVE-2024-0001"])
        results = sgp.evaluate(ctx)
        l21_results = [r for r in results if r.layer == "L21"]
        assert l21_results[0].verdict == GateVerdict.REJECT

    def test_l22_data_quality_below_80_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(data_quality_score=70.0)
        results = sgp.evaluate(ctx)
        l22_results = [r for r in results if r.layer == "L22"]
        assert l22_results[0].verdict == GateVerdict.REJECT

    def test_l27_compliance_violation_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(compliance_ok=False)
        results = sgp.evaluate(ctx)
        l27_results = [r for r in results if r.layer == "L27"]
        assert l27_results[0].verdict == GateVerdict.REJECT

    def test_l19_owner_fatigue_rejects(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(owner_fatigue=0.8)
        results = sgp.evaluate(ctx)
        l19_results = [r for r in results if r.layer == "L19"]
        assert l19_results[0].verdict == GateVerdict.REJECT


class TestHardGateShortCircuit:
    def test_hard_reject_stops_pipeline(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(dependency_status={"svc": False})
        results = sgp.evaluate(ctx)
        assert len(results) < 27
        assert results[-1].verdict == GateVerdict.REJECT


class TestProperties:
    def test_is_blocked(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(compliance_ok=False)
        sgp.results = sgp.evaluate(ctx)
        assert sgp.is_blocked is True

    def test_reject_trace(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(compliance_ok=False)
        sgp.results = sgp.evaluate(ctx)
        trace = sgp.reject_trace
        assert len(trace) > 0


class TestBoundaries:
    def test_l3_trading_hours_observe_only(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(is_trading_hours=True, severity=3)
        results = sgp.evaluate(ctx)
        l3 = [r for r in results if r.layer == "L3"]
        assert l3[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_l2_frequency_exceeded_returns_reject(self):
        sgp = SafetyGatePipeline()
        ctx = _default_ctx(action_type="FREQ_TEST")
        for _ in range(11):
            sgp.evaluate(ctx)
        last_results = sgp.evaluate(ctx)
        l2 = [r for r in last_results if r.layer == "L2"]
        assert l2[0].verdict == GateVerdict.REJECT
