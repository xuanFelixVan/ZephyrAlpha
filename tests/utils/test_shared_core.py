# [A_test] module_id: SRC-TST-1957 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-574 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_shared_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: shared_core"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.integration.shared.schema.base_config import BASE_CONFIG, Classification, EvolutionPolicy
from zephyr.integration.shared.schema.schemas import (
    AuditFinding,
    AuditReport,
    AuditSeverity,
    ExecutionModel,
    FailureType,
    HandoffPackage,
    KeCategory,
    KnowledgeEntry,
    NextAction,
    Task,
    TaskNamespace,
    TaskStatus,
)
from zephyr.integration.shared.schema.severity_types import SafetyLevel
from zephyr.shared.io.paths import (
    DB_DIR,
    GATES_DIR,
    REPO_ROOT,
    find_repo_root,
)


class TestTaskModel:
    def test_task_creation_minimal(self):
        now = datetime.now(UTC)
        task = Task(
            task_id="SRC-001",
            title="Test task",
            status=TaskStatus.PENDING,
            namespace=TaskNamespace.SRC,
            seq=1,
            phase=0,
            safety_level=SafetyLevel.L,
            created_at=now,
            updated_at=now,
            description="A test task for unit testing with enough length to pass validation.",
        )
        assert task.task_id == "SRC-001"
        assert task.title == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.namespace == TaskNamespace.SRC

    def test_task_status_enum_values(self):
        assert TaskStatus.PENDING.value == "PENDING"
        assert TaskStatus.IN_PROGRESS.value == "IN_PROGRESS"
        assert TaskStatus.COMPLETED.value == "COMPLETED"
        assert TaskStatus.FAILED.value == "FAILED"
        assert TaskStatus.BLOCKED.value == "BLOCKED"
        assert TaskStatus.READY.value == "READY"

    def test_task_namespace_enum_values(self):
        assert TaskNamespace.KBG.value == "KBG"
        assert TaskNamespace.CP.value == "CP"
        assert TaskNamespace.KE.value == "KE"
        assert TaskNamespace.STD.value == "STD"
        assert TaskNamespace.DW.value == "DW"
        assert TaskNamespace.SRC.value == "SRC"
        assert TaskNamespace.OPS.value == "OPS"
        assert TaskNamespace.DM.value == "DM"

    def test_execution_model_enum(self):
        assert ExecutionModel.deepseek.value == "deepseek"
        assert ExecutionModel.glm.value == "glm"
        assert ExecutionModel.claude.value == "claude"
        assert ExecutionModel.kimi.value == "kimi"
        assert ExecutionModel.qwen.value == "qwen"

    def test_normalize_execution_model(self):
        from zephyr.gov_enforcement.rule_enforcement.task_types import normalize_execution_model

        assert normalize_execution_model("deepseek") == ExecutionModel.deepseek
        assert normalize_execution_model("glm") == ExecutionModel.glm
        assert normalize_execution_model("claude") == ExecutionModel.claude
        assert normalize_execution_model("kimi") == ExecutionModel.kimi
        assert normalize_execution_model("qwen") == ExecutionModel.qwen


class TestAuditFinding:
    def test_creation(self):
        finding = AuditFinding(
            finding_id="F-001",
            severity=AuditSeverity.P0,
            description="Critical issue found",
        )
        assert finding.finding_id == "F-001"
        assert finding.severity == AuditSeverity.P0
        assert finding.description == "Critical issue found"

    def test_optional_fields_default_none(self):
        finding = AuditFinding(
            finding_id="F-002",
            severity=AuditSeverity.P2,
            description="Minor issue",
        )
        assert finding.file_path is None
        assert finding.suggestion is None


class TestAuditReport:
    def test_creation_with_findings(self):
        findings = [
            AuditFinding(finding_id="F-001", severity=AuditSeverity.P0, description="P0 issue"),
            AuditFinding(finding_id="F-002", severity=AuditSeverity.P1, description="P1 issue"),
        ]
        report = AuditReport(
            report_id="R-001",
            scanner="test-scanner",
            scan_target="/test/path",
            findings=findings,
            created_at=datetime.now(UTC),
        )
        assert report.p0_count == 1
        assert report.p1_count == 1
        assert report.passed is False

    def test_no_p0_means_passed(self):
        findings = [
            AuditFinding(finding_id="F-001", severity=AuditSeverity.P1, description="P1 issue"),
        ]
        report = AuditReport(
            report_id="R-002",
            scanner="test-scanner",
            scan_target="/test/path",
            findings=findings,
            created_at=datetime.now(UTC),
        )
        assert report.passed is True

    def test_empty_findings_is_passed(self):
        report = AuditReport(
            report_id="R-003",
            scanner="test-scanner",
            scan_target="/test/path",
            created_at=datetime.now(UTC),
        )
        assert report.passed is True
        assert report.p0_count == 0


class TestKnowledgeEntry:
    def test_creation(self):
        now = datetime.now(UTC)
        ke = KnowledgeEntry(
            ke_id="KE-001",
            title="Test KE",
            source_file="test.py",
            created_at=now,
            updated_at=now,
        )
        assert ke.ke_id == "KE-001"
        assert ke.category == KeCategory.best_practice

    def test_invalid_ke_id_format(self):
        with pytest.raises(Exception):
            KnowledgeEntry(
                ke_id="invalid",
                title="Test",
                source_file="test.py",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

    def test_updated_before_created_rejected(self):
        with pytest.raises(Exception):
            KnowledgeEntry(
                ke_id="KE-002",
                title="Test",
                source_file="test.py",
                created_at=datetime(2026, 1, 2, tzinfo=UTC),
                updated_at=datetime(2026, 1, 1, tzinfo=UTC),
            )

    def test_invalid_sha256_rejected(self):
        with pytest.raises(Exception):
            KnowledgeEntry(
                ke_id="KE-003",
                title="Test",
                source_file="test.py",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                fingerprint_sha256="tooshort",
            )


class TestHandoffPackage:
    def test_creation(self):
        now = datetime.now(UTC)
        pkg = HandoffPackage(
            session_id="session-20260518-001",
            completed_tasks=["T-001"],
            in_progress_tasks=["T-002"],
            blocked_items=[],
            decisions_made=[],
            next_actions=[NextAction(priority=1, action="Do X")],
            context_summary="Test session",
            open_questions=[],
            created_at=now,
        )
        assert pkg.session_id == "session-20260518-001"
        assert pkg.completed_tasks == ["T-001"]

    def test_overlap_tasks_rejected(self):
        now = datetime.now(UTC)
        with pytest.raises(Exception):
            HandoffPackage(
                session_id="session-20260518-002",
                completed_tasks=["T-001"],
                in_progress_tasks=["T-001"],
                blocked_items=[],
                decisions_made=[],
                next_actions=[],
                context_summary="Test",
                open_questions=[],
                created_at=now,
            )

    def test_next_actions_sorted_by_priority(self):
        now = datetime.now(UTC)
        pkg = HandoffPackage(
            session_id="session-20260518-003",
            completed_tasks=[],
            in_progress_tasks=[],
            blocked_items=[],
            decisions_made=[],
            next_actions=[
                NextAction(priority=5, action="Low priority"),
                NextAction(priority=1, action="High priority"),
                NextAction(priority=3, action="Medium priority"),
            ],
            context_summary="Test",
            open_questions=[],
            created_at=now,
        )
        priorities = [a.priority for a in pkg.next_actions]
        assert priorities == sorted(priorities)


class TestBaseConfig:
    def test_base_config_is_frozen(self):
        assert BASE_CONFIG.get("extra") == "forbid"
        assert BASE_CONFIG.get("validate_assignment") is True

    def test_classification_enum(self):
        assert Classification.PUBLIC.value == "public"
        assert Classification.INTERNAL.value == "internal"
        assert Classification.CONFIDENTIAL.value == "confidential"

    def test_evolution_policy_enum(self):
        assert EvolutionPolicy.FROZEN.value == "frozen"
        assert EvolutionPolicy.EXTENDABLE.value == "extendable"
        assert EvolutionPolicy.REWRITABLE.value == "rewritable"


class TestPathConstants:
    def test_repo_root_is_path(self):
        assert isinstance(REPO_ROOT, Path)

    def test_repo_root_exists(self):
        assert REPO_ROOT.exists()

    def test_repo_root_has_src_zephyr(self):
        assert (REPO_ROOT / "src" / "zephyr" / "__init__.py").exists()

    def test_db_dir_under_repo_root(self):
        assert DB_DIR == REPO_ROOT / "data"

    def test_gates_dir_under_repo_root(self):
        assert GATES_DIR == REPO_ROOT / "src" / "zephyr" / "gates"

    def test_find_repo_root_returns_path(self):
        root = find_repo_root()
        assert isinstance(root, Path)
        assert (root / "src" / "zephyr" / "__init__.py").exists()


class TestFailureType:
    def test_enum_values(self):
        assert FailureType.VALIDATION.value == "validation"
        assert FailureType.LOGIC.value == "logic"
        assert FailureType.INFRASTRUCTURE.value == "infrastructure"
        assert FailureType.TIMEOUT.value == "timeout"
        assert FailureType.UNKNOWN.value == "unknown"
