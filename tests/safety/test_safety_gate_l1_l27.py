# [A_test] module_id: SRC-TST-1503 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_safety_gate_L1_L27
# [INVARIANTS] HARD REJECT must short-circuit pipeline; is_blocked must reflect results
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.safety_gate_l1_l27 import (
    ActionContext,
    GateVerdict,
    SafetyGatePipeline,
)


def _nominal_ctx(**overrides):
    defaults = dict(
        action_id="a1",
        action_type="REPAIR",
        has_rollback=True,
        has_self_modification_audit=True,
        data_quality_score=100.0,
        compliance_ok=True,
    )
    defaults.update(overrides)
    return ActionContext(**defaults)


class TestActionContextInstantiation:
    def test_default_values(self):
        ctx = ActionContext(action_id="a1", action_type="REPAIR")
        assert ctx.action_id == "a1"
        assert ctx.severity == 0
        assert ctx.has_rollback is False
        assert ctx.compliance_ok is True


class TestSafetyGatePipelineInstantiation:
    def test_default_gates(self):
        pipeline = SafetyGatePipeline()
        assert len(pipeline.gates) == 27

    def test_default_frequency_counters(self):
        pipeline = SafetyGatePipeline()
        assert pipeline.frequency_counters == {}


class TestEvaluate:
    def test_all_pass_nominal_context(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx()
        results = pipeline.evaluate(ctx)
        assert all(r.verdict == GateVerdict.PASS for r in results)

    def test_l4_dependency_down_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(dependency_status={"db": False})
        results = pipeline.evaluate(ctx)
        l4_result = [r for r in results if r.layer == "L4"]
        assert len(l4_result) == 1
        assert l4_result[0].verdict == GateVerdict.REJECT

    def test_l5_budget_exceeded_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(cost_estimate=200.0, budget_remaining=100.0)
        results = pipeline.evaluate(ctx)
        l5_result = [r for r in results if r.layer == "L5"]
        assert len(l5_result) == 1
        assert l5_result[0].verdict == GateVerdict.REJECT

    def test_l6_no_rollback_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(has_rollback=False)
        results = pipeline.evaluate(ctx)
        l6_result = [r for r in results if r.layer == "L6"]
        assert len(l6_result) == 1
        assert l6_result[0].verdict == GateVerdict.REJECT

    def test_l12_schema_mismatch_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(schema_version=1, expected_schema_version=2)
        results = pipeline.evaluate(ctx)
        l12_result = [r for r in results if r.layer == "L12"]
        assert len(l12_result) == 1
        assert l12_result[0].verdict == GateVerdict.REJECT

    def test_l17_autonomy_exceeds_max_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(autonomy_level=5)
        results = pipeline.evaluate(ctx)
        l17_result = [r for r in results if r.layer == "L17"]
        assert len(l17_result) == 1
        assert l17_result[0].verdict == GateVerdict.REJECT

    def test_l19_owner_fatigue_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(owner_fatigue=0.8)
        results = pipeline.evaluate(ctx)
        l19_result = [r for r in results if r.layer == "L19"]
        assert len(l19_result) == 1
        assert l19_result[0].verdict == GateVerdict.REJECT

    def test_l20_self_mod_not_audited_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(has_self_modification_audit=False)
        results = pipeline.evaluate(ctx)
        l20_result = [r for r in results if r.layer == "L20"]
        assert len(l20_result) == 1
        assert l20_result[0].verdict == GateVerdict.REJECT

    def test_l21_cve_alerts_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(cve_alerts=["CVE-2024-0001"])
        results = pipeline.evaluate(ctx)
        l21_result = [r for r in results if r.layer == "L21"]
        assert len(l21_result) == 1
        assert l21_result[0].verdict == GateVerdict.REJECT

    def test_l22_data_quality_low_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(data_quality_score=70.0)
        results = pipeline.evaluate(ctx)
        l22_result = [r for r in results if r.layer == "L22"]
        assert len(l22_result) == 1
        assert l22_result[0].verdict == GateVerdict.REJECT

    def test_l27_compliance_violation_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(compliance_ok=False)
        results = pipeline.evaluate(ctx)
        l27_result = [r for r in results if r.layer == "L27"]
        assert len(l27_result) == 1
        assert l27_result[0].verdict == GateVerdict.REJECT

    def test_l3_trading_silence_observe(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx(is_trading_hours=True, severity=3)
        results = pipeline.evaluate(ctx)
        l3_result = [r for r in results if r.layer == "L3"]
        assert len(l3_result) == 1
        assert l3_result[0].verdict == GateVerdict.OBSERVE_ONLY

    def test_hard_reject_short_circuits(self):
        pipeline = SafetyGatePipeline()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", has_rollback=False)
        results = pipeline.evaluate(ctx)
        assert len(results) < 27

    def test_l2_frequency_limit(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx()
        for _ in range(10):
            pipeline.evaluate(ctx)
        results = pipeline.evaluate(ctx)
        l2_result = [r for r in results if r.layer == "L2"]
        assert len(l2_result) == 1
        assert l2_result[0].verdict == GateVerdict.REJECT


class TestIsBlocked:
    def test_not_blocked_on_pass(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx()
        pipeline.results = pipeline.evaluate(ctx)
        assert pipeline.is_blocked is False

    def test_blocked_on_reject(self):
        pipeline = SafetyGatePipeline()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", has_rollback=False)
        pipeline.results = pipeline.evaluate(ctx)
        assert pipeline.is_blocked is True


class TestRejectTrace:
    def test_empty_when_no_rejects(self):
        pipeline = SafetyGatePipeline()
        ctx = _nominal_ctx()
        pipeline.results = pipeline.evaluate(ctx)
        assert pipeline.reject_trace == []

    def test_contains_reject_info(self):
        pipeline = SafetyGatePipeline()
        ctx = ActionContext(action_id="a1", action_type="REPAIR", has_rollback=False)
        pipeline.results = pipeline.evaluate(ctx)
        assert len(pipeline.reject_trace) >= 1
