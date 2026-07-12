# [A_test] module_id: SRC-TST-1725 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_task_types
# [INVARIANTS] Tests MUST cover TaskStatus enum values; Task instantiation; model_validator; normalize_execution_model; boundary validation errors
# [MODIFY-GUARD] src/zephyr/governance/rule_enforcement/task_types.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError on test failure
# [TESTS] self
# [TTL] task_bound
from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from zephyr.gov_enforcement.rule_enforcement.task_types import (
    ExecutionModel,
    Task,
    TaskNamespace,
    TaskStatus,
    normalize_execution_model,
)
from zephyr.integration.shared.schema.base_config import Classification, EvolutionPolicy
from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel

_NOW = datetime(2026, 5, 22, 12, 0, 0)


def _make_task(**overrides):
    defaults = dict(
        task_id="KBG-1",
        namespace=TaskNamespace.KBG,
        seq=1,
        title="Test task",
        safety_level=SafetyLevel.L,
        phase=0,
        created_at=_NOW,
        updated_at=_NOW,
        description="根因：测试需要。治根：补齐 description 字段。施工步骤：(1) 添加 description 默认值。验收标准：Task 实例化成功。",
    )
    defaults.update(overrides)
    return Task(**defaults)


class TestTaskStatus:
    def test_all_enum_values(self):
        expected = {
            "PENDING",
            "IN_PROGRESS",
            "COMPLETED",
            "VERIFIED",
            "FAILED",
            "BLOCKED",
            "WAITING",
            "READY",
            "RETRY",
            "CANCELLED",
        }
        actual = {m.value for m in TaskStatus}
        assert actual == expected

    def test_enum_is_str(self):
        assert isinstance(TaskStatus.PENDING, str)
        assert TaskStatus.PENDING == "PENDING"

    def test_enum_membership(self):
        assert TaskStatus("COMPLETED") is TaskStatus.COMPLETED
        with pytest.raises(ValueError):
            TaskStatus("NONEXISTENT")


class TestTaskInstantiation:
    def test_minimal_valid_task(self):
        task = _make_task()
        assert task.task_id == "KBG-1"
        assert task.namespace == TaskNamespace.KBG
        assert task.seq == 1
        assert task.title == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.P2
        assert task.phase == 0
        assert task.execution_model == ExecutionModel.deepseek
        assert task.safety_level == SafetyLevel.L
        assert task.classification == Classification.INTERNAL
        assert task.evolution_policy == EvolutionPolicy.EXTENDABLE
        assert task.is_deleted == 0
        assert task.idempotent is False
        assert task.estimate_hours == 0.0
        assert task.actual_hours is None
        assert task.files_in_scope == []
        assert task.deliverables == []
        assert task.acceptance == []
        assert task.depends_on == []
        assert task.tags == []
        assert task.session_id is None
        assert task.waiting_for is None
        assert task.ready_at is None
        assert task.completed_at is None
        assert task.deleted_at is None
        assert task.model_rationale is None
        assert task.fallback_model is None
        assert task.schema_version == ""
        assert task.source_blueprint == ""
        assert task.source_section == ""
        assert task.directive == ""

    def test_all_namespaces_task_ids(self):
        for ns in TaskNamespace:
            task = _make_task(task_id=f"{ns.value}-42", namespace=ns, seq=42)
            assert task.namespace == ns
            assert task.task_id == f"{ns.value}-42"

    def test_full_field_task(self):
        later = _NOW + timedelta(hours=2)
        task = _make_task(
            task_id="SRC-99",
            namespace=TaskNamespace.SRC,
            seq=99,
            title="Full task",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.P0,
            phase=5,
            execution_model=ExecutionModel.claude,
            model_rationale="Complex reasoning",
            fallback_model="deepseek",
            safety_level=SafetyLevel.H,
            directive="313+325",
            idempotent=True,
            classification=Classification.CONFIDENTIAL,
            evolution_policy=EvolutionPolicy.FROZEN,
            estimate_hours=8.0,
            actual_hours=6.5,
            files_in_scope=["src/a.py", "src/b.py"],
            deliverables=["output.md"],
            acceptance=["All tests pass"],
            depends_on=["KBG-1"],
            tags=["infra", "gate"],
            session_id="session-20260522-008",
            waiting_for=None,
            ready_at=_NOW + timedelta(minutes=30),
            completed_at=later,
            updated_at=later,
            is_deleted=0,
            schema_version="2.0",
            source_blueprint="MOD-GATE_ENGINE",
            source_section="§3",
        )
        assert task.task_id == "SRC-99"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == Priority.P0
        assert task.execution_model == ExecutionModel.claude
        assert task.safety_level == SafetyLevel.H
        assert task.classification == Classification.CONFIDENTIAL
        assert task.evolution_policy == EvolutionPolicy.FROZEN
        assert task.estimate_hours == 8.0
        assert task.actual_hours == 6.5
        assert len(task.files_in_scope) == 2
        assert task.idempotent is True
        assert task.directive == "313+325"

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc_info:
            _make_task(unknown_field="value")
        assert "extra" in str(exc_info.value).lower() or "forbid" in str(exc_info.value).lower()


class TestTaskValidator:
    def test_updated_at_before_created_at_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            _make_task(
                created_at=_NOW,
                updated_at=_NOW - timedelta(seconds=1),
            )
        assert "updated_at must not be before created_at" in str(exc_info.value)

    def test_updated_at_equal_to_created_at_ok(self):
        task = _make_task(created_at=_NOW, updated_at=_NOW)
        assert task.updated_at == task.created_at

    def test_updated_at_after_created_at_ok(self):
        later = _NOW + timedelta(hours=1)
        task = _make_task(created_at=_NOW, updated_at=later)
        assert task.updated_at > task.created_at


class TestTaskBoundaryValidation:
    def test_invalid_task_id_format_no_namespace(self):
        with pytest.raises(ValidationError):
            _make_task(task_id="INVALID-1")

    def test_invalid_task_id_format_no_dash(self):
        with pytest.raises(ValidationError):
            _make_task(task_id="ADR1")

    def test_invalid_task_id_format_letters_after_dash(self):
        with pytest.raises(ValidationError):
            _make_task(task_id="ADR-abc")

    def test_invalid_task_id_empty(self):
        with pytest.raises(ValidationError):
            _make_task(task_id="")

    def test_invalid_task_id_none(self):
        with pytest.raises(ValidationError):
            _make_task(task_id=None)

    def test_seq_zero_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(seq=0)

    def test_seq_negative_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(seq=-1)

    def test_seq_one_ok(self):
        task = _make_task(seq=1)
        assert task.seq == 1

    def test_title_empty_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(title="")

    def test_title_too_long_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(title="x" * 201)

    def test_title_max_length_ok(self):
        task = _make_task(title="x" * 200)
        assert len(task.title) == 200

    def test_title_none_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(title=None)

    def test_phase_below_zero_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(phase=-1)

    def test_phase_above_nine_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(phase=10)

    def test_phase_boundaries_ok(self):
        task_lo = _make_task(phase=0)
        task_hi = _make_task(phase=9)
        assert task_lo.phase == 0
        assert task_hi.phase == 9

    def test_estimate_hours_negative_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(estimate_hours=-0.1)

    def test_actual_hours_negative_rejected(self):
        with pytest.raises(ValidationError):
            _make_task(actual_hours=-1.0)

    def test_is_deleted_out_of_range(self):
        with pytest.raises(ValidationError):
            _make_task(is_deleted=2)

    def test_is_deleted_boundary_values(self):
        task0 = _make_task(is_deleted=0)
        task1 = _make_task(is_deleted=1)
        assert task0.is_deleted == 0
        assert task1.is_deleted == 1

    def test_missing_required_field_created_at(self):
        with pytest.raises(ValidationError):
            Task(
                task_id="KBG-1",
                namespace=TaskNamespace.KBG,
                seq=1,
                title="test",
                safety_level=SafetyLevel.L,
                phase=0,
                updated_at=_NOW,
            )

    def test_missing_required_field_safety_level(self):
        with pytest.raises(ValidationError):
            Task(
                task_id="KBG-1",
                namespace=TaskNamespace.KBG,
                seq=1,
                title="test",
                phase=0,
                created_at=_NOW,
                updated_at=_NOW,
            )


class TestNormalizeExecutionModel:
    def test_exact_enum_value(self):
        assert normalize_execution_model(ExecutionModel.claude) == ExecutionModel.claude

    def test_exact_string_match(self):
        assert normalize_execution_model("deepseek") == ExecutionModel.deepseek

    def test_claude_prefix(self):
        assert normalize_execution_model("claude-3-opus") == ExecutionModel.claude

    def test_glm_prefix(self):
        assert normalize_execution_model("glm-4") == ExecutionModel.glm

    def test_deepseek_aliases(self):
        assert normalize_execution_model("ds") == ExecutionModel.deepseek
        assert normalize_execution_model("deep_seek") == ExecutionModel.deepseek

    def test_kimi_prefix(self):
        assert normalize_execution_model("kimi-v2") == ExecutionModel.kimi

    def test_qwen_prefix(self):
        assert normalize_execution_model("qwen-max") == ExecutionModel.qwen

    def test_system_maps_to_qwen(self):
        assert normalize_execution_model("system") == ExecutionModel.qwen

    def test_unknown_defaults_to_deepseek(self):
        assert normalize_execution_model("unknown-model") == ExecutionModel.deepseek

    def test_whitespace_stripped(self):
        assert normalize_execution_model("  claude  ") == ExecutionModel.claude

    def test_case_insensitive(self):
        assert normalize_execution_model("CLAUDE") == ExecutionModel.claude
        assert normalize_execution_model("DeepSeek") == ExecutionModel.deepseek
