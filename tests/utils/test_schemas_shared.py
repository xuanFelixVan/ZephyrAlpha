# [A_test] module_id: SRC-TST-1955 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-572 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_schemas
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/schemas.py（T-1）
==========================================
覆盖矩阵（5 模型 × 3 有效输入 + 3 无效输入 ≥ 30 用例 + validator 反例）

Task           : 有效 × 3 / 无效 × 3 / validator × 3
AuditReport    : 有效 × 3 / 无效 × 3 / validator × 2
KnowledgeEntry : 有效 × 3 / 无效 × 3 / validator × 2
FailurePattern : 有效 × 3 / 无效 × 3 / validator × 1
HandoffPackage : 有效 × 3 / 无效 × 3 / validator × 3

额外：strict mode (extra="forbid")、枚举值校验、BASE_CONFIG 验证
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from zephyr.gov_enforcement.rule_enforcement.task_types import Task, TaskNamespace, TaskStatus
from zephyr.integration.shared.schema.base_config import BASE_CONFIG, Classification, EvolutionPolicy
from zephyr.integration.shared.schema.schemas import (
    AuditFinding,
    AuditReport,
    BlockedItem,
    FailurePattern,
    FailureType,
    HandoffPackage,
    KnowledgeEntry,
    NextAction,
)
from zephyr.integration.shared.schema.severity_types import AuditSeverity, SafetyLevel

_UTC = UTC
_NOW = datetime(2026, 4, 24, 0, 0, 0, tzinfo=_UTC)
_LATER = datetime(2026, 4, 24, 12, 0, 0, tzinfo=_UTC)

# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def _task(**kwargs: Any) -> Task:
    defaults: dict[str, Any] = dict(
        task_id="SRC-1",
        namespace=TaskNamespace.SRC,
        seq=1,
        phase=1,
        title="Sample Task",
        execution_model="claude",
        safety_level=SafetyLevel.M,
        directive="313",
        created_at=_NOW,
        updated_at=_NOW,
        description="A sample task for testing purposes with enough length to pass validation.",
    )
    defaults.update(kwargs)
    return Task(**defaults)


def _ke(**kwargs: Any) -> KnowledgeEntry:
    defaults: dict[str, Any] = dict(
        ke_id="KE-001",
        title="Test Knowledge",
        source_file="docs/test.md",
        created_at=_NOW,
        updated_at=_NOW,
    )
    defaults.update(kwargs)
    return KnowledgeEntry(**defaults)


# ---------------------------------------------------------------------------
# Task 模型
# ---------------------------------------------------------------------------


class TestTask:
    """5 × 3 有效 + 3 无效 + validator 反例。"""

    # 有效输入
    def test_valid_minimal(self) -> None:
        t = _task()
        assert t.task_id == "SRC-1"
        assert t.status == TaskStatus.PENDING

    def test_valid_full_fields(self) -> None:
        t = _task(
            task_id="SRC-2",
            phase=2,
            status=TaskStatus.IN_PROGRESS,
            fallback_model="gpt-4",
            safety_level=SafetyLevel.H,
            idempotent=True,
            classification=Classification.CONFIDENTIAL,
            evolution_policy=EvolutionPolicy.FROZEN,
            estimate_hours=3.5,
            deliverables=["file.py"],
            acceptance=["tests pass"],
            depends_on=["SRC-3", "SRC-2"],
            session_id="sess-xyz",
            updated_at=_LATER,
        )
        assert t.phase == 2
        assert t.fallback_model == "gpt-4"
        assert len(t.depends_on) == 2

    def test_valid_status_all_values(self) -> None:
        for s in TaskStatus:
            t = _task(task_id="SRC-4", status=s, updated_at=_LATER if s != TaskStatus.PENDING else _NOW)
            assert t.status == s

    # 无效输入
    def test_invalid_task_id_format(self) -> None:
        with pytest.raises(ValidationError, match="task_id"):
            _task(task_id="task_1_01")  # 不符合 T-N-N 格式

    def test_invalid_phase_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            _task(phase=10)  # 超过 le=9

    def test_invalid_safety_level(self) -> None:
        with pytest.raises(ValidationError):
            _task(safety_level="CRITICAL")  # 不在 L/M/H

    # validator 反例
    def test_updated_before_created_rejected(self) -> None:
        with pytest.raises(ValidationError, match="updated_at"):
            _task(created_at=_LATER, updated_at=_NOW)  # updated < created

    def test_extra_field_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            _task(unknown_field="oops")

    def test_str_strip_whitespace(self) -> None:
        t = _task(title="  Task Name  ")
        assert t.title == "Task Name"


# ---------------------------------------------------------------------------
# AuditReport 模型
# ---------------------------------------------------------------------------


class TestAuditReport:
    def _report(self, **kwargs: Any) -> AuditReport:
        defaults: dict[str, Any] = dict(
            report_id="RPT-001",
            scanner="test_scanner",
            scan_target="docs/",
            created_at=_NOW,
        )
        defaults.update(kwargs)
        return AuditReport(**defaults)

    # 有效输入
    def test_valid_no_findings(self) -> None:
        r = self._report()
        assert r.passed is True
        assert r.p0_count == 0

    def test_valid_with_p1_findings(self) -> None:
        findings = [AuditFinding(finding_id="F-001", severity=AuditSeverity.P1, description="P1 issue")]
        r = self._report(findings=findings)
        assert r.passed is True  # P0=0 时 passed=True
        assert r.p1_count == 1

    def test_valid_with_p0_finding(self) -> None:
        findings = [AuditFinding(finding_id="F-002", severity=AuditSeverity.P0, description="Critical")]
        r = self._report(findings=findings)
        assert r.passed is False  # P0 > 0 → passed=False
        assert r.p0_count == 1

    # 无效输入
    def test_invalid_empty_report_id(self) -> None:
        with pytest.raises(ValidationError):
            self._report(report_id="")

    def test_invalid_empty_scanner(self) -> None:
        with pytest.raises(ValidationError):
            self._report(scanner="")

    def test_invalid_negative_p0_count(self) -> None:
        with pytest.raises(ValidationError):
            self._report(p0_count=-1)

    # validator 反例
    def test_passed_auto_set_false_when_p0(self) -> None:
        findings = [
            AuditFinding(finding_id="F-003", severity=AuditSeverity.P0, description="Critical"),
            AuditFinding(finding_id="F-004", severity=AuditSeverity.P0, description="Critical 2"),
        ]
        r = self._report(findings=findings)
        assert r.passed is False
        assert r.p0_count == 2

    def test_counts_synced_from_findings(self) -> None:
        findings = [
            AuditFinding(finding_id="A", severity=AuditSeverity.P0, description="x"),
            AuditFinding(finding_id="B", severity=AuditSeverity.P1, description="y"),
            AuditFinding(finding_id="C", severity=AuditSeverity.P2, description="z"),
        ]
        r = self._report(findings=findings)
        assert r.p0_count == 1
        assert r.p1_count == 1
        assert r.p2_count == 1


# ---------------------------------------------------------------------------
# KnowledgeEntry 模型
# ---------------------------------------------------------------------------


class TestKnowledgeEntry:
    # 有效输入
    def test_valid_minimal(self) -> None:
        ke = _ke()
        assert ke.ke_id == "KE-001"
        assert ke.source_git_deleted is False

    def test_valid_with_tags(self) -> None:
        ke = _ke(ke_id="KE-123", tags=["python", "sqlite"])
        assert ke.tags == ["python", "sqlite"]

    def test_valid_with_fingerprint(self) -> None:
        sha = "a" * 64
        ke = _ke(fingerprint_sha256=sha)
        assert ke.fingerprint_sha256 == sha

    # 无效输入
    def test_invalid_ke_id_format(self) -> None:
        with pytest.raises(ValidationError, match="ke_id"):
            _ke(ke_id="KE01")  # 缺少连字符

    def test_invalid_ke_id_too_short(self) -> None:
        with pytest.raises(ValidationError):
            _ke(ke_id="KE-01")  # 数字位不足 3 位（regex: \d{3,}）

    def test_invalid_empty_title(self) -> None:
        with pytest.raises(ValidationError):
            _ke(title="")

    # validator 反例
    def test_invalid_sha256_length(self) -> None:
        with pytest.raises(ValidationError, match="fingerprint_sha256"):
            _ke(fingerprint_sha256="abc123")  # 不是 64 位

    def test_updated_before_created_rejected(self) -> None:
        with pytest.raises(ValidationError, match="updated_at"):
            _ke(created_at=_LATER, updated_at=_NOW)


# ---------------------------------------------------------------------------
# FailurePattern 模型
# ---------------------------------------------------------------------------


class TestFailurePattern:
    def _fp(self, **kwargs: Any) -> FailurePattern:
        defaults: dict[str, Any] = dict(
            pattern_id="F-001",
            failure_type=FailureType.VALIDATION,
            title="Test failure",
            description="Detailed description",
            created_at=_NOW,
            updated_at=_NOW,
        )
        defaults.update(kwargs)
        return FailurePattern(**defaults)

    # 有效输入
    def test_valid_minimal(self) -> None:
        fp = self._fp()
        assert fp.pattern_id == "F-001"
        assert fp.resolved is False

    def test_valid_with_steps(self) -> None:
        fp = self._fp(
            reproduction_steps=["step1", "step2"],
            mitigation="fix the bug",
            recurrence_count=3,
        )
        assert fp.recurrence_count == 3

    def test_valid_resolved(self) -> None:
        fp = self._fp(resolved=True, updated_at=_LATER)
        assert fp.resolved is True

    # 无效输入
    def test_invalid_pattern_id_format(self) -> None:
        with pytest.raises(ValidationError, match="pattern_id"):
            self._fp(pattern_id="FAIL-001")  # 不符合 F-NNN 格式

    def test_invalid_recurrence_zero(self) -> None:
        with pytest.raises(ValidationError):
            self._fp(recurrence_count=0)  # ge=1

    def test_invalid_failure_type(self) -> None:
        with pytest.raises(ValidationError):
            self._fp(failure_type="critical")  # 不在枚举

    # validator 反例
    def test_updated_before_created_rejected(self) -> None:
        with pytest.raises(ValidationError, match="updated_at"):
            self._fp(created_at=_LATER, updated_at=_NOW)


# ---------------------------------------------------------------------------
# HandoffPackage 模型
# ---------------------------------------------------------------------------


class TestHandoffPackage:
    def _pkg(self, **kwargs: Any) -> HandoffPackage:
        defaults: dict[str, Any] = dict(
            session_id="sess-001",
            completed_tasks=["SRC-5"],
            in_progress_tasks=["SRC-6"],
            blocked_items=[],
            decisions_made=[],
            next_actions=[],
            context_summary="Session completed experimental tasks.",
            open_questions=["Should we use Redis?"],
            created_at=_NOW,
        )
        defaults.update(kwargs)
        return HandoffPackage(**defaults)

    # 有效输入
    def test_valid_minimal(self) -> None:
        pkg = self._pkg()
        assert pkg.session_id == "sess-001"
        assert pkg.completed_tasks == ["SRC-5"]

    def test_valid_with_blocked_items(self) -> None:
        bi = BlockedItem(task_id="SRC-8", reason="Waiting for DB schema")
        pkg = self._pkg(blocked_items=[bi])
        assert len(pkg.blocked_items) == 1

    def test_valid_with_next_actions_sorted(self) -> None:
        actions = [
            NextAction(priority=3, action="Review docs"),
            NextAction(priority=1, action="Fix bug"),
            NextAction(priority=2, action="Write tests"),
        ]
        pkg = self._pkg(next_actions=actions)
        # validator 应按 priority 排序
        assert pkg.next_actions[0].priority == 1
        assert pkg.next_actions[1].priority == 2
        assert pkg.next_actions[2].priority == 3

    # 无效输入
    def test_invalid_empty_session_id(self) -> None:
        with pytest.raises(ValidationError):
            self._pkg(session_id="")

    def test_invalid_context_summary_too_long(self) -> None:
        with pytest.raises(ValidationError):
            self._pkg(context_summary="x" * 501)  # 超过 max_length=500

    def test_invalid_next_action_priority_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            self._pkg(next_actions=[NextAction(priority=11, action="test")])  # 超过 le=10

    # validator 反例
    def test_overlap_in_completed_and_in_progress_rejected(self) -> None:
        with pytest.raises(ValidationError, match="appear in both|overlap"):
            self._pkg(
                completed_tasks=["SRC-10", "SRC-11"],
                in_progress_tasks=["SRC-11", "SRC-12"],
            )

    def test_extra_field_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            self._pkg(unexpected_key="bad")

    def test_to_yaml_dict(self) -> None:
        pkg = self._pkg()
        d = pkg.to_yaml_dict()
        assert isinstance(d["created_at"], str)
        assert "T" in d["created_at"]  # ISO 格式


# ---------------------------------------------------------------------------
# BASE_CONFIG 验证
# ---------------------------------------------------------------------------


class TestBaseConfig:
    def test_validate_assignment_works(self) -> None:
        """validate_assignment=True：运行时字段重写也触发校验。"""
        t = _task()
        with pytest.raises(ValidationError):
            t.phase = 99  # 超出范围，应触发校验错误

    def test_str_strip_whitespace_global(self) -> None:
        """所有模型继承 str_strip_whitespace=True。"""
        ke = _ke(title="  Stripped  ")
        assert ke.title == "Stripped"

    def test_base_config_has_expected_keys(self) -> None:
        assert BASE_CONFIG.get("extra") == "forbid"
        assert BASE_CONFIG.get("str_strip_whitespace") is True
        assert BASE_CONFIG.get("validate_assignment") is True
