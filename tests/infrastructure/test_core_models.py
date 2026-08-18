# [A_test] module_id: MOD-GOV_core_models | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-371 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_core_models
# [INVARIANTS] GateLevel enum values match gate engine expectations; TaskAuditFinding validation rules; TaskCard instantiation validates inherited+extended fields; DecompositionResult/GateCheckResult field constraints
# [MODIFY-GUARD] src/zephyr/core/models.py
# [CONSUMERS] pytest CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] self
# [TTL] task_bound
from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.shared.foundation.models import (
    DecompositionResult,
    GateCheckResult,
    GateLevel,
    TaskAuditFinding,
    TaskCard,
)
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.schema.schemas import TaskNamespace, TaskStatus
from zephyr.shared.schema.severity_types import Priority, SafetyLevel

_NOW = datetime(2026, 5, 23, 12, 0, 0)


def _make_card(**overrides):
    defaults = dict(
        task_id="STD-999",
        namespace=TaskNamespace.STD,
        seq=999,
        title="Test TaskCard",
        safety_level=SafetyLevel.L,
        phase=0,
        created_at=_NOW,
        updated_at=_NOW,
        source_blueprint="MOD-INF-016",
        source_section="§3.2",
        description="A task card for testing core models stability freeze",
    )
    defaults.update(overrides)
    return TaskCard(**defaults)


class TestGateLevel:
    def test_all_levels_present(self):
        expected = {"G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G10", "G11", "G12"}
        actual = {g.value for g in GateLevel}
        assert actual == expected

    def test_count_is_11(self):
        assert len(GateLevel) == 11

    def test_str_membership(self):
        assert GateLevel("G7") is GateLevel.G7
        assert GateLevel("G0") is GateLevel.G0

    def test_invalid_level_raises(self):
        with pytest.raises(ValueError):
            GateLevel("G99")


class TestTaskAuditFinding:
    def test_valid_finding(self):
        f = TaskAuditFinding(
            finding_id="F-0001",
            dimension="code_quality",
            severity="high",
            description="Test finding",
            source_task="STD-001",
        )
        assert f.finding_id == "F-0001"
        assert f.dimension == "code_quality"
        assert f.severity == "high"
        assert f.resolved is False
        assert f.resolution_note is None

    def test_resolved_with_note(self):
        f = TaskAuditFinding(
            finding_id="F-0002",
            dimension="security",
            severity="critical",
            description="Critical issue",
            source_task="STD-002",
            resolved=True,
            resolution_note="Fixed by commit abc123",
        )
        assert f.resolved is True
        assert f.resolution_note == "Fixed by commit abc123"

    def test_invalid_finding_id_pattern(self):
        with pytest.raises(ValidationError):
            TaskAuditFinding(
                finding_id="INVALID",
                dimension="test",
                severity="low",
                description="Bad ID",
                source_task="STD-001",
            )

    def test_invalid_finding_id_no_dash(self):
        with pytest.raises(ValidationError):
            TaskAuditFinding(
                finding_id="F0001",
                dimension="test",
                severity="low",
                description="Bad ID",
                source_task="STD-001",
            )

    def test_invalid_severity_value(self):
        with pytest.raises(ValidationError):
            TaskAuditFinding(
                finding_id="F-0003",
                dimension="test",
                severity="unknown",
                description="Bad severity",
                source_task="STD-001",
            )

    def test_severity_boundary_all_values(self):
        for sev in ("critical", "high", "medium", "low", "info"):
            f = TaskAuditFinding(
                finding_id="F-0004",
                dimension="test",
                severity=sev,
                description="Valid",
                source_task="STD-001",
            )
            assert f.severity == sev


class TestTaskCardInstantiation:
    def test_minimal_valid_card(self):
        card = _make_card()
        assert card.task_id == "STD-999"
        assert card.status == TaskStatus.PENDING
        assert card.priority == Priority.P2
        assert card.source_blueprint == "MOD-INF-016"

    def test_full_field_card(self):
        card = _make_card(
            task_id="KBG-500",
            namespace=TaskNamespace.KBG,
            seq=500,
            title="Full card",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.P0,
            phase=3,
            upstream_files=[str(REPO_ROOT / "src" / "a.py")],
            downstream_outputs=[{"path": "out.md", "description": "Output"}],
            allowed_touch=[str(REPO_ROOT / "src" / "b.py")],
            forbidden_touch=[str(REPO_ROOT / "src" / "secrets.py")],
            rollback_instructions="git reset --hard HEAD~1",
            estimated_tokens=16000,
            timeout_minutes=60,
            construction_status="in_progress",
            verification_status="verified",
        )
        assert card.upstream_files == [str(REPO_ROOT / "src" / "a.py")]
        assert card.estimated_tokens == 16000
        assert card.timeout_minutes == 60
        assert card.construction_status == "in_progress"
        assert card.verification_status == "verified"

    def test_source_blueprint_empty_accepted_at_model_level(self):
        card = _make_card(source_blueprint="")
        assert card.source_blueprint == ""
        assert TaskRepository.validate_template_fields(TaskRepository.__new__(TaskRepository), card) != []

    def test_description_too_short_rejected(self):
        with pytest.raises(ValidationError):
            _make_card(description="short")

    def test_description_max_length_enforced_at_repo_level(self):
        long_desc = "x" * 50001
        with pytest.raises(ValidationError):
            _make_card(description=long_desc)

    def test_description_boundary_min(self):
        card = _make_card(description="x" * 10)
        assert len(card.description) == 10

    def test_description_boundary_max(self):
        card = _make_card(description="根因：测试。治根：测试。施工步骤：(1) 测试。验收标准：测试。" + "x" * 770)
        assert len(card.description) >= 800

    def test_estimated_tokens_boundary_min(self):
        card = _make_card(estimated_tokens=500)
        assert card.estimated_tokens == 500

    def test_estimated_tokens_below_min_rejected(self):
        with pytest.raises(ValidationError):
            _make_card(estimated_tokens=499)

    def test_timeout_minutes_below_min_rejected(self):
        with pytest.raises(ValidationError):
            _make_card(timeout_minutes=4)

    def test_block_sessions_count_negative_rejected(self):
        with pytest.raises(ValidationError):
            _make_card(block_sessions_count=-1)

    def test_block_sessions_count_zero_ok(self):
        card = _make_card(block_sessions_count=0)
        assert card.block_sessions_count == 0

    def test_completed_gates_default(self):
        card = _make_card()
        assert card.completed_gates == []

    def test_blocked_gates_default(self):
        card = _make_card()
        assert card.blocked_gates == {}

    def test_dependency_fields_defaults(self):
        card = _make_card()
        assert card.dependency_type == "hard"
        assert card.dependency_rationale == ""
        assert card.depgraph_nodes == []


class TestDecompositionResult:
    def test_valid_empty_decomposition(self):
        dr = DecompositionResult(total_tasks=0, tasks=[])
        assert dr.total_tasks == 0
        assert dr.tasks == []
        assert dr.dependency_graph == {}
        assert dr.unassigned_items == []
        assert dr.warnings == []

    def test_valid_decomposition_with_tasks(self):
        card1 = _make_card(task_id="STD-001", seq=1)
        card2 = _make_card(task_id="STD-002", seq=2)
        dr = DecompositionResult(
            total_tasks=2,
            tasks=[card1, card2],
            dependency_graph={"STD-002": ["STD-001"]},
            unassigned_items=[],
            warnings=["test warning"],
        )
        assert dr.total_tasks == 2
        assert len(dr.tasks) == 2
        assert dr.dependency_graph == {"STD-002": ["STD-001"]}
        assert dr.warnings == ["test warning"]

    def test_total_tasks_negative_rejected(self):
        with pytest.raises(ValidationError):
            DecompositionResult(total_tasks=-1, tasks=[])

    def test_mismatched_total_does_not_raise(self):
        card = _make_card(task_id="STD-003", seq=3)
        dr = DecompositionResult(total_tasks=1, tasks=[card])
        assert dr.total_tasks == 1
        assert len(dr.tasks) == 1


class TestGateCheckResult:
    def test_passed_result(self):
        gcr = GateCheckResult(gate_id=GateLevel.G7, task_id="STD-001", passed=True)
        assert gcr.gate_id == GateLevel.G7
        assert gcr.task_id == "STD-001"
        assert gcr.passed is True
        assert gcr.violations == []
        assert gcr.checked_at is not None

    def test_failed_result_with_violations(self):
        gcr = GateCheckResult(
            gate_id=GateLevel.G3,
            task_id="STD-002",
            passed=False,
            violations=["Missing manifest", "Unregistered file"],
        )
        assert gcr.passed is False
        assert len(gcr.violations) == 2

    def test_checked_at_is_iso_format(self):
        gcr = GateCheckResult(gate_id=GateLevel.G1, task_id="STD-003", passed=True)
        from datetime import datetime as dt

        dt.fromisoformat(gcr.checked_at)

    def test_missing_gate_id_raises(self):
        with pytest.raises(ValidationError):
            GateCheckResult(task_id="STD-004", passed=True)
