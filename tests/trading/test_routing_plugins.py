# [A_test] module_id: MOD-GOV_routing_plugins | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_routing_plugins
# [INVARIANTS] Filter→Score→Bind three-phase invariant; RoutingContext.candidates only shrinks in filter phase
# [MODIFY-GUARD] plugin list changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] NoEligibleNodeError when all candidates filtered out
# [TESTS] pytest tests/test_routing_plugins.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.infrastructure.pipeline.ct_pipe_routing import CtPipeRoutingHints
from zephyr.infrastructure.pipeline.models import M_MODULES
from zephyr.infrastructure.pipeline.routing_plugins import (
    DEFAULT_PLUGINS,
    ComplexityFilter,
    CostScorer,
    NoEligibleNodeError,
    PipelineAffinityScorer,
    PipelineRouter,
    PriorityScorer,
    RoutingContext,
    RoutingPlugin,
    TaskTypeFilter,
)


class TestRoutingContext:
    def test_initialization_with_hints(self):
        hints = CtPipeRoutingHints(task_type="MODEL_BUILD", priority_value="P2")
        ctx = RoutingContext(hints)
        assert ctx.hints is hints
        assert ctx.candidates == list(M_MODULES)
        assert len(ctx.scores) == len(M_MODULES)
        assert all(s == 0.0 for s in ctx.scores.values())
        assert ctx.rejections == {}

    def test_candidates_mutable(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        ctx = RoutingContext(hints)
        ctx.candidates.remove("M1")
        assert "M1" not in ctx.candidates

    def test_scores_mutable(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        ctx = RoutingContext(hints)
        ctx.scores["M1"] = 10.0
        assert ctx.scores["M1"] == 10.0


class TestTaskTypeFilter:
    def test_model_build_keeps_m1_m2(self):
        hints = CtPipeRoutingHints(task_type="MODEL_BUILD", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        assert "M1" in ctx.candidates
        assert "M2" in ctx.candidates
        assert "M3" not in ctx.candidates

    def test_audit_keeps_audit_nodes(self):
        hints = CtPipeRoutingHints(task_type="AUDIT", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        expected = {"M3", "M4", "M6", "M7", "M8", "M9", "M10"}
        assert set(ctx.candidates) == expected

    def test_ops_keeps_m2(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        assert "M2" in ctx.candidates

    def test_unknown_type_removes_all(self):
        hints = CtPipeRoutingHints(task_type="NONEXISTENT", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        assert len(ctx.candidates) == 0

    def test_auto_fix_keeps_m11(self):
        hints = CtPipeRoutingHints(task_type="AUTO_FIX", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        assert ctx.candidates == ["M11"]

    def test_rejections_populated(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        assert len(ctx.rejections) > 0


class TestComplexityFilter:
    def test_high_complexity_keeps_only_m1(self):
        hints = CtPipeRoutingHints(
            task_type="MODEL_BUILD",
            priority_value="P2",
            estimated_complexity="HIGH",
        )
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        ComplexityFilter().apply(ctx)
        assert "M1" in ctx.candidates

    def test_low_complexity_keeps_all(self):
        hints = CtPipeRoutingHints(
            task_type="MODEL_BUILD",
            priority_value="P2",
            estimated_complexity="LOW",
        )
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        before_count = len(ctx.candidates)
        ComplexityFilter().apply(ctx)
        assert len(ctx.candidates) == before_count

    def test_no_complexity_keeps_all(self):
        hints = CtPipeRoutingHints(
            task_type="MODEL_BUILD",
            priority_value="P2",
        )
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        before_count = len(ctx.candidates)
        ComplexityFilter().apply(ctx)
        assert len(ctx.candidates) == before_count

    def test_h_variant_high_complexity(self):
        hints = CtPipeRoutingHints(
            task_type="MODEL_BUILD",
            priority_value="P2",
            estimated_complexity="H",
        )
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        ComplexityFilter().apply(ctx)
        assert "M1" in ctx.candidates


class TestPriorityScorer:
    def test_audit_p0_gives_m3_high_score(self):
        hints = CtPipeRoutingHints(task_type="AUDIT", priority_value="P0")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        PriorityScorer().apply(ctx)
        assert ctx.scores["M3"] > 0

    def test_model_build_gives_m2_score(self):
        hints = CtPipeRoutingHints(task_type="MODEL_BUILD", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        PriorityScorer().apply(ctx)
        assert ctx.scores["M2"] > 0


class TestPipelineAffinityScorer:
    def test_model_build_prefers_a_pipeline(self):
        hints = CtPipeRoutingHints(task_type="MODEL_BUILD", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        PipelineAffinityScorer().apply(ctx)
        a_nodes = [n for n in ctx.candidates if n in ("M1", "M2", "M3", "M4", "M5")]
        if a_nodes:
            assert any(ctx.scores[n] > 0 for n in a_nodes)

    def test_audit_prefers_b_pipeline(self):
        hints = CtPipeRoutingHints(task_type="AUDIT", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        PipelineAffinityScorer().apply(ctx)
        b_nodes = [n for n in ctx.candidates if n in ("M6", "M7", "M8", "M9", "M10", "M11")]
        if b_nodes:
            assert any(ctx.scores[n] > 0 for n in b_nodes)


class TestCostScorer:
    def test_cost_scorer_adds_scores(self):
        hints = CtPipeRoutingHints(task_type="MODEL_BUILD", priority_value="P2")
        ctx = RoutingContext(hints)
        TaskTypeFilter().apply(ctx)
        CostScorer().apply(ctx)
        for node in ctx.candidates:
            assert ctx.scores[node] >= 0.0


class TestPipelineRouter:
    def test_model_build_high_routes_to_m1(self):
        hints = CtPipeRoutingHints(
            task_type="MODEL_BUILD",
            priority_value="P2",
            estimated_complexity="HIGH",
        )
        router = PipelineRouter()
        decision = router.route(hints)
        assert decision.node_id == "M1"

    def test_ops_routes_to_m2(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        router = PipelineRouter()
        decision = router.route(hints)
        assert decision.node_id == "M2"

    def test_audit_p0_routes_to_m3(self):
        hints = CtPipeRoutingHints(task_type="AUDIT", priority_value="P0")
        router = PipelineRouter()
        decision = router.route(hints)
        assert decision.node_id == "M3"

    def test_unsupported_type_raises_no_eligible_node(self):
        hints = CtPipeRoutingHints(task_type="NONEXISTENT", priority_value="P2")
        router = PipelineRouter()
        with pytest.raises(NoEligibleNodeError):
            router.route(hints)

    def test_custom_plugins(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        router = PipelineRouter(plugins=[TaskTypeFilter()])
        decision = router.route(hints)
        assert decision.node_id == "M2"

    def test_decision_has_rationale(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        router = PipelineRouter()
        decision = router.route(hints)
        assert decision.rationale


class TestDefaultPlugins:
    def test_has_six_plugins(self):
        assert len(DEFAULT_PLUGINS) == 6

    def test_contains_task_type_filter(self):
        assert any(isinstance(p, TaskTypeFilter) for p in DEFAULT_PLUGINS)

    def test_contains_complexity_filter(self):
        assert any(isinstance(p, ComplexityFilter) for p in DEFAULT_PLUGINS)

    def test_contains_priority_scorer(self):
        assert any(isinstance(p, PriorityScorer) for p in DEFAULT_PLUGINS)

    def test_contains_pipeline_affinity_scorer(self):
        assert any(isinstance(p, PipelineAffinityScorer) for p in DEFAULT_PLUGINS)

    def test_contains_cost_scorer(self):
        assert any(isinstance(p, CostScorer) for p in DEFAULT_PLUGINS)


class TestRoutingPluginAbstract:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            RoutingPlugin()
