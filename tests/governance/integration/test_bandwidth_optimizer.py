# [A_test] module_id: MOD-GOV_bandwidth_optimizer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_bandwidth_optimizer
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] BandwidthScore composite in [0,1]; recommend returns valid OptimizationRecommendation
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.bandwidth_optimizer import (
    BandwidthDimension,
    BandwidthScore,
    OptimizationRecommendation,
    recommend,
)


class TestBandwidthScore:
    def test_default_composite_is_zero(self):
        score = BandwidthScore()
        assert score.composite == 0.0

    def test_composite_with_values(self):
        score = BandwidthScore(
            interrupt_overhead=1.0,
            context_switching=1.0,
            decision_fatigue=1.0,
            communication_latency=1.0,
            attention_span=1.0,
            cognitive_load=1.0,
        )
        assert score.composite > 0.0
        assert score.composite <= 1.0

    def test_normalize_clamps_to_one(self):
        score = BandwidthScore(
            interrupt_overhead=100.0,
            context_switching=200.0,
            decision_fatigue=50.0,
            communication_latency=300.0,
            attention_span=10.0,
            cognitive_load=999.0,
        )
        score.normalize()
        assert score.interrupt_overhead <= 1.0
        assert score.context_switching <= 1.0
        assert score.cognitive_load <= 1.0

    def test_normalize_small_values(self):
        score = BandwidthScore(interrupt_overhead=2.0)
        score.normalize()
        assert 0.0 <= score.interrupt_overhead <= 1.0

    def test_composite_rounded_to_three_decimals(self):
        score = BandwidthScore(interrupt_overhead=3.7, context_switching=2.1)
        composite = score.composite
        str_repr = str(composite)
        if "." in str_repr:
            decimals = str_repr.split(".")[1]
            assert len(decimals) <= 3


class TestRecommend:
    def test_high_score_returns_small_granularity(self):
        score = BandwidthScore(
            interrupt_overhead=8.0,
            context_switching=8.0,
            decision_fatigue=8.0,
            communication_latency=8.0,
            attention_span=8.0,
            cognitive_load=8.0,
        )
        rec = recommend(score)
        assert isinstance(rec, OptimizationRecommendation)
        assert rec.task_granularity == "small"
        assert rec.max_tasks_per_session == 10

    def test_medium_score_returns_medium_granularity(self):
        score = BandwidthScore(
            interrupt_overhead=5.0,
            context_switching=5.0,
            decision_fatigue=5.0,
            communication_latency=5.0,
            attention_span=5.0,
            cognitive_load=5.0,
        )
        rec = recommend(score)
        assert rec.task_granularity == "medium"

    def test_low_score_returns_large_granularity(self):
        score = BandwidthScore(
            interrupt_overhead=1.0,
            context_switching=1.0,
            decision_fatigue=1.0,
            communication_latency=1.0,
            attention_span=1.0,
            cognitive_load=1.0,
        )
        rec = recommend(score)
        assert rec.task_granularity == "large"
        assert rec.max_tasks_per_session == 65

    def test_recommend_normalizes_input(self):
        score = BandwidthScore(interrupt_overhead=100.0)
        rec = recommend(score)
        assert isinstance(rec, OptimizationRecommendation)


class TestBandwidthDimension:
    def test_enum_values(self):
        assert BandwidthDimension.INTERRUPT_OVERHEAD.value == "interrupt_overhead"
        assert BandwidthDimension.COGNITIVE_LOAD.value == "cognitive_load"

    def test_all_dimensions_exist(self):
        expected = {
            "interrupt_overhead",
            "context_switching",
            "decision_fatigue",
            "communication_latency",
            "attention_span",
            "cognitive_load",
        }
        actual = {d.value for d in BandwidthDimension}
        assert actual == expected


class TestBoundaryCases:
    def test_zero_score(self):
        score = BandwidthScore()
        rec = recommend(score)
        assert rec.task_granularity == "large"

    def test_negative_values(self):
        score = BandwidthScore(interrupt_overhead=-1.0)
        composite = score.composite
        assert isinstance(composite, float)

    def test_empty_optimization_recommendation_defaults(self):
        rec = OptimizationRecommendation()
        assert rec.task_granularity == "medium"
        assert rec.focus_shift_interval_seconds == 1800
        assert rec.max_tasks_per_session == 30
        assert rec.suggested_break_seconds == 300
