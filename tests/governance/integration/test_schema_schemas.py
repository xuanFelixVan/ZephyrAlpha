# [A_test] module_id: MOD-GOV_schema_schemas | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_schema_schemas
# [DOMAIN] D_GOVERNANCE

# [INVARIANTS] AuditReport.sync_counts自动同步;KnowledgeEntry.ke_id格式KE-NNN;HandoffPackage无重叠

# [MODIFY-GUARD] schemas.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] Pydantic ValidationError

# [TESTS] pytest tests/test_schema_schemas.py -q
# [TTL] task_bound

from datetime import UTC, datetime

import pytest

from zephyr.shared.schema.schemas import (
    AuditFinding,
    AuditReport,
    BlockedItem,
    Decision,
    FailurePattern,
    FailureType,
    HandoffPackage,
    KeCategory,
    KnowledgeEntry,
    NextAction,
)
from zephyr.shared.schema.severity_types import AuditSeverity


def _now():
    return datetime.now(UTC)


class TestKeCategory:
    def test_members(self):
        assert KeCategory.blueprint_decision.value == "blueprint_decision"
        assert KeCategory.lesson_learned.value == "lesson_learned"
        assert KeCategory.architecture.value == "architecture"


class TestFailureType:
    def test_members(self):
        assert FailureType.VALIDATION.value == "validation"
        assert FailureType.LOGIC.value == "logic"
        assert FailureType.INFRASTRUCTURE.value == "infrastructure"


class TestAuditFinding:
    def test_valid(self):
        f = AuditFinding(
            finding_id="F-001",
            severity=AuditSeverity.P1,
            description="test finding",
        )
        assert f.finding_id == "F-001"
        assert f.severity == AuditSeverity.P1

    def test_empty_finding_id_raises(self):
        with pytest.raises(Exception):
            AuditFinding(finding_id="", severity=AuditSeverity.P0, description="x")

    def test_description_too_long_raises(self):
        with pytest.raises(Exception):
            AuditFinding(finding_id="F-1", severity=AuditSeverity.P0, description="x" * 1001)


class TestAuditReport:
    def test_sync_counts(self):
        findings = [
            AuditFinding(finding_id="F-1", severity=AuditSeverity.P0, description="p0"),
            AuditFinding(finding_id="F-2", severity=AuditSeverity.P1, description="p1"),
            AuditFinding(finding_id="F-3", severity=AuditSeverity.P2, description="p2"),
        ]
        report = AuditReport(
            report_id="R-001",
            scanner="test",
            scan_target="src/",
            findings=findings,
            created_at=_now(),
        )
        assert report.p0_count == 1
        assert report.p1_count == 1
        assert report.p2_count == 1
        assert report.passed is False

    def test_passed_when_no_p0(self):
        findings = [
            AuditFinding(finding_id="F-1", severity=AuditSeverity.P2, description="p2"),
        ]
        report = AuditReport(
            report_id="R-002",
            scanner="test",
            scan_target="src/",
            findings=findings,
            created_at=_now(),
        )
        assert report.passed is True

    def test_no_findings_passes(self):
        report = AuditReport(
            report_id="R-003",
            scanner="test",
            scan_target="src/",
            created_at=_now(),
        )
        assert report.passed is True
        assert report.p0_count == 0


class TestKnowledgeEntry:
    def test_valid(self):
        now = _now()
        ke = KnowledgeEntry(
            ke_id="KE-001",
            title="Test KE",
            source_file="docs/test.md",
            created_at=now,
            updated_at=now,
        )
        assert ke.ke_id == "KE-001"
        assert ke.category == KeCategory.best_practice

    def test_invalid_ke_id_format(self):
        now = _now()
        with pytest.raises(Exception, match="KE-"):
            KnowledgeEntry(
                ke_id="BAD-ID",
                title="Test",
                source_file="docs/test.md",
                created_at=now,
                updated_at=now,
            )

    def test_invalid_sha256_length(self):
        now = _now()
        with pytest.raises(Exception, match="64-char"):
            KnowledgeEntry(
                ke_id="KE-002",
                title="Test",
                source_file="docs/test.md",
                fingerprint_sha256="abc",
                created_at=now,
                updated_at=now,
            )

    def test_updated_before_created_raises(self):
        now = _now()
        from datetime import timedelta

        with pytest.raises(Exception, match="updated_at"):
            KnowledgeEntry(
                ke_id="KE-003",
                title="Test",
                source_file="docs/test.md",
                created_at=now,
                updated_at=now - timedelta(hours=1),
            )


class TestFailurePattern:
    def test_valid(self):
        now = _now()
        fp = FailurePattern(
            pattern_id="F-001",
            failure_type=FailureType.VALIDATION,
            title="Test pattern",
            description="desc",
            created_at=now,
            updated_at=now,
        )
        assert fp.recurrence_count == 1
        assert fp.resolved is False

    def test_invalid_pattern_id(self):
        now = _now()
        with pytest.raises(Exception, match="F-"):
            FailurePattern(
                pattern_id="BAD",
                failure_type=FailureType.LOGIC,
                title="t",
                description="d",
                created_at=now,
                updated_at=now,
            )


class TestBlockedItem:
    def test_valid(self):
        bi = BlockedItem(task_id="T-001", reason="waiting for approval")
        assert bi.task_id == "T-001"
        assert bi.blocked_since is None

    def test_empty_reason_raises(self):
        with pytest.raises(Exception):
            BlockedItem(task_id="T-001", reason="")


class TestDecision:
    def test_valid(self):
        d = Decision(decision_id="D-001", summary="Use X", rationale="X is better")
        assert d.kb_ref is None


class TestNextAction:
    def test_valid(self):
        a = NextAction(priority=1, action="Fix bug")
        assert a.owner is None

    def test_invalid_priority(self):
        with pytest.raises(Exception):
            NextAction(priority=0, action="bad")
        with pytest.raises(Exception):
            NextAction(priority=11, action="bad")


class TestHandoffPackage:
    def test_valid(self):
        hp = HandoffPackage(
            session_id="s-001",
            completed_tasks=["T-001"],
            in_progress_tasks=["T-002"],
            blocked_items=[],
            decisions_made=[],
            next_actions=[NextAction(priority=1, action="Continue")],
            context_summary="In progress",
            open_questions=[],
            created_at=_now(),
        )
        assert hp.session_id == "s-001"

    def test_overlap_tasks_raises(self):
        with pytest.raises(Exception, match="appear in both"):
            HandoffPackage(
                session_id="s-001",
                completed_tasks=["T-001"],
                in_progress_tasks=["T-001"],
                blocked_items=[],
                decisions_made=[],
                next_actions=[],
                context_summary="",
                open_questions=[],
                created_at=_now(),
            )

    def test_next_actions_sorted(self):
        hp = HandoffPackage(
            session_id="s-001",
            completed_tasks=[],
            in_progress_tasks=[],
            blocked_items=[],
            decisions_made=[],
            next_actions=[
                NextAction(priority=5, action="low"),
                NextAction(priority=1, action="high"),
            ],
            context_summary="",
            open_questions=[],
            created_at=_now(),
        )
        assert hp.next_actions[0].action == "high"
        assert hp.next_actions[1].action == "low"

    def test_to_yaml_dict(self):
        hp = HandoffPackage(
            session_id="s-001",
            completed_tasks=[],
            in_progress_tasks=[],
            blocked_items=[],
            decisions_made=[],
            next_actions=[],
            context_summary="",
            open_questions=[],
            created_at=_now(),
        )
        d = hp.to_yaml_dict()
        assert isinstance(d, dict)
        assert "session_id" in d
        assert isinstance(d["created_at"], str)
