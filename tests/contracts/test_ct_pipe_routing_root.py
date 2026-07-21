# [A_test] module_id: MOD-GOV_ct_pipe_routing_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_ct_pipe_routing
# [INVARIANTS] CtPipeRoutingHints.task_type min_length=1; resolve_ct_pipe_orc001 decision tree invariants; modules_slice_from_node only accepts M1-M11
# [MODIFY-GUARD] decision tree changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PipelineRoutingInputsError on unsupported/missing inputs; ValueError on unknown node_id
# [TESTS] pytest tests/test_ct_pipe_routing.py
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from zephyr.infrastructure.pipeline.ct_pipe_routing import (
    CtPipeRoutingHints,
    PipelineRoutingInputsError,
    ct_pipe_hints_from_task_card,
    enforce_affinity,
    modules_slice_from_node,
    resolve_ct_pipe_orc001,
)
from zephyr.infrastructure.pipeline.models import PipelineRouteDecision


@dataclass
class MockPriority:
    value: str = "P2"


@dataclass
class MockTaskCard:
    tags: list[str] = None
    pipeline_task_type: str = ""
    priority: Any = None
    target_layer: str = ""
    estimated_complexity: str = ""
    estimated_tokens: int = 8000

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.priority is None:
            self.priority = MockPriority()


class TestCtPipeRoutingHints:
    def test_valid_hints(self):
        hints = CtPipeRoutingHints(
            task_type="MODEL_BUILD",
            priority_value="P1",
            target_layer="D_INFRA_OPS",
            estimated_complexity="HIGH",
        )
        assert hints.task_type == "MODEL_BUILD"
        assert hints.priority_value == "P1"
        assert hints.target_layer == "D_INFRA_OPS"
        assert hints.estimated_complexity == "HIGH"

    def test_default_priority(self):
        hints = CtPipeRoutingHints(task_type="OPS")
        assert hints.priority_value == "P2"

    def test_optional_fields_none(self):
        hints = CtPipeRoutingHints(task_type="AUDIT")
        assert hints.target_layer is None
        assert hints.estimated_complexity is None

    def test_empty_task_type_rejected(self):
        with pytest.raises(Exception):
            CtPipeRoutingHints(task_type="")

    def test_invalid_priority_rejected(self):
        with pytest.raises(Exception):
            CtPipeRoutingHints(task_type="OPS", priority_value="X9")


class TestCtPipeHintsFromTaskCard:
    def test_extracts_pipeline_task_type(self):
        task = MockTaskCard(pipeline_task_type="MODEL_BUILD", priority=MockPriority("P1"))
        hints = ct_pipe_hints_from_task_card(task)
        assert hints is not None
        assert hints.task_type == "MODEL_BUILD"
        assert hints.priority_value == "P1"

    def test_extracts_from_tags(self):
        task = MockTaskCard(
            tags=["ct_pipe.task_type=AUDIT"],
            pipeline_task_type="",
            priority=MockPriority("P0"),
        )
        hints = ct_pipe_hints_from_task_card(task)
        assert hints is not None
        assert hints.task_type == "AUDIT"

    def test_returns_none_when_no_type(self):
        task = MockTaskCard(pipeline_task_type="", tags=[], priority=MockPriority("P2"))
        assert ct_pipe_hints_from_task_card(task) is None

    def test_target_layer_from_field(self):
        task = MockTaskCard(
            pipeline_task_type="DOC_WRITE",
            target_layer="D_MKT_DATA",
            priority=MockPriority("P2"),
        )
        hints = ct_pipe_hints_from_task_card(task)
        assert hints.target_layer == "D_MKT_DATA"

    def test_target_layer_from_tag(self):
        task = MockTaskCard(
            pipeline_task_type="DOC_WRITE",
            tags=["ct_pipe.layer=D_FACTOR"],
            priority=MockPriority("P2"),
        )
        hints = ct_pipe_hints_from_task_card(task)
        assert hints.target_layer == "D_FACTOR"

    def test_complexity_from_field(self):
        task = MockTaskCard(
            pipeline_task_type="MODEL_BUILD",
            estimated_complexity="HIGH",
            priority=MockPriority("P2"),
        )
        hints = ct_pipe_hints_from_task_card(task)
        assert hints.estimated_complexity == "HIGH"

    def test_complexity_inferred_from_tokens(self):
        task = MockTaskCard(
            pipeline_task_type="MODEL_BUILD",
            estimated_tokens=8000,
            estimated_complexity="",
            priority=MockPriority("P2"),
        )
        hints = ct_pipe_hints_from_task_card(task)
        assert hints.estimated_complexity == "HIGH"

    def test_complexity_not_inferred_below_threshold(self):
        task = MockTaskCard(
            pipeline_task_type="MODEL_BUILD",
            estimated_tokens=5000,
            estimated_complexity="",
            priority=MockPriority("P2"),
        )
        hints = ct_pipe_hints_from_task_card(task)
        assert hints.estimated_complexity is None

    def test_task_type_uppercase_normalized(self):
        task = MockTaskCard(
            pipeline_task_type="model-build",
            priority=MockPriority("P2"),
        )
        hints = ct_pipe_hints_from_task_card(task)
        assert hints.task_type == "MODEL_BUILD"


class TestResolveCtPipeOrc001:
    def test_ops_routes_to_m2(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M2"

    def test_model_build_high_routes_to_m1(self):
        hints = CtPipeRoutingHints(
            task_type="MODEL_BUILD",
            priority_value="P2",
            estimated_complexity="HIGH",
        )
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M1"

    def test_model_build_low_routes_to_m2(self):
        hints = CtPipeRoutingHints(
            task_type="MODEL_BUILD",
            priority_value="P2",
            estimated_complexity="LOW",
        )
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M2"

    def test_model_build_default_low_routes_to_m2(self):
        hints = CtPipeRoutingHints(task_type="MODEL_BUILD", priority_value="P2")
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M2"

    def test_audit_p0_routes_to_m3(self):
        hints = CtPipeRoutingHints(task_type="AUDIT", priority_value="P0")
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M3"

    def test_audit_p2_routes_to_m4(self):
        hints = CtPipeRoutingHints(task_type="AUDIT", priority_value="P2")
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M4"

    def test_doc_write_data_routes_to_m5(self):
        hints = CtPipeRoutingHints(
            task_type="DOC_WRITE",
            priority_value="P2",
            target_layer="D_MKT_DATA",
        )
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M5"

    def test_doc_write_factor_routes_to_m6(self):
        hints = CtPipeRoutingHints(
            task_type="DOC_WRITE",
            priority_value="P2",
            target_layer="D_FACTOR",
        )
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M6"

    def test_auto_fix_routes_to_m11(self):
        hints = CtPipeRoutingHints(task_type="AUTO_FIX", priority_value="P2")
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M11"

    def test_autofix_variant_routes_to_m11(self):
        hints = CtPipeRoutingHints(task_type="AUTOFIX", priority_value="P2")
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M11"

    def test_unsupported_type_raises_error(self):
        hints = CtPipeRoutingHints(task_type="UNKNOWN_TYPE", priority_value="P2")
        with pytest.raises(PipelineRoutingInputsError):
            resolve_ct_pipe_orc001(hints)

    def test_doc_write_without_target_layer_raises_error(self):
        hints = CtPipeRoutingHints(task_type="DOC_WRITE", priority_value="P2")
        with pytest.raises(PipelineRoutingInputsError):
            resolve_ct_pipe_orc001(hints)

    def test_decision_has_execution_model(self):
        hints = CtPipeRoutingHints(task_type="OPS", priority_value="P2")
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.execution_model
        assert decision.sandbox_profile
        assert decision.gate_profile

    def test_refactor_without_target_layer_raises_error(self):
        hints = CtPipeRoutingHints(task_type="REFACTOR", priority_value="P2")
        with pytest.raises(PipelineRoutingInputsError):
            resolve_ct_pipe_orc001(hints)

    def test_refactor_with_foundation_layer_routes_to_m5(self):
        hints = CtPipeRoutingHints(
            task_type="REFACTOR",
            priority_value="P2",
            target_layer="D_GOV_ENFORCEMENT",
        )
        decision = resolve_ct_pipe_orc001(hints)
        assert decision.node_id == "M5"


class TestModulesSliceFromNode:
    def test_m1_returns_order_a_from_m1(self):
        group, modules = modules_slice_from_node("M1")
        assert group == "A"
        assert modules == ["M1", "M2", "M3", "M4", "M5"]

    def test_m3_returns_order_a_from_m3(self):
        group, modules = modules_slice_from_node("M3")
        assert group == "A"
        assert modules == ["M3", "M4", "M5"]

    def test_m5_returns_order_a_from_m5(self):
        group, modules = modules_slice_from_node("M5")
        assert group == "A"
        assert modules == ["M5"]

    def test_m6_returns_order_b_from_m6(self):
        group, modules = modules_slice_from_node("M6")
        assert group == "B"
        assert modules == ["M6", "M7", "M8", "M9", "M10", "M11"]

    def test_m9_returns_order_b_from_m9(self):
        group, modules = modules_slice_from_node("M9")
        assert group == "B"
        assert modules == ["M9", "M10", "M11"]

    def test_m11_returns_order_b_from_m11(self):
        group, modules = modules_slice_from_node("M11")
        assert group == "B"
        assert modules == ["M11"]

    def test_unknown_node_raises_value_error(self):
        with pytest.raises(ValueError, match="unknown pipeline node_id"):
            modules_slice_from_node("M99")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            modules_slice_from_node("")


class TestEnforceAffinity:
    def test_m3_m7_same_model_aborts(self):
        decision = PipelineRouteDecision(
            node_id="M3",
            execution_model="deepseek",
            sandbox_profile="audit",
            gate_profile="post_exec_only",
            rationale="test",
        )
        active = {"M3": "deepseek", "M7": "deepseek"}
        warnings = enforce_affinity(decision, active)
        abort_msgs = [w for w in warnings if w.startswith("ABORT")]
        assert len(abort_msgs) >= 1

    def test_m3_m7_different_model_no_abort_for_model(self):
        decision = PipelineRouteDecision(
            node_id="M3",
            execution_model="deepseek",
            sandbox_profile="audit",
            gate_profile="post_exec_only",
            rationale="test",
        )
        active = {"M3": "deepseek", "M7": "glm"}
        warnings = enforce_affinity(decision, active)
        model_aborts = [w for w in warnings if "ABORT" in w and "M3" in w and "M7" in w]
        assert len(model_aborts) == 0

    def test_sandbox_constraint_aborts(self):
        decision = PipelineRouteDecision(
            node_id="M1",
            execution_model="deepseek",
            sandbox_profile="restricted",
            gate_profile="full_g0_g7",
            rationale="test",
        )
        warnings = enforce_affinity(decision, {})
        abort_msgs = [w for w in warnings if w.startswith("ABORT")]
        assert len(abort_msgs) >= 1

    def test_no_active_nodes_returns_warnings(self):
        decision = PipelineRouteDecision(
            node_id="M2",
            execution_model="deepseek",
            sandbox_profile="standard",
            gate_profile="pre_commit_only",
            rationale="test",
        )
        warnings = enforce_affinity(decision, None)
        assert isinstance(warnings, list)

    def test_pipeline_constraint_warns_non_m5_m6(self):
        decision = PipelineRouteDecision(
            node_id="M3",
            execution_model="deepseek",
            sandbox_profile="audit",
            gate_profile="post_exec_only",
            rationale="test",
        )
        warnings = enforce_affinity(decision, {})
        pipeline_warns = [w for w in warnings if "pipeline" in w.lower() or "A区→B区" in w]
        assert len(pipeline_warns) >= 1
