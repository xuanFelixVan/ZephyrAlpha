# [A_test] module_id: MOD-GOV_models_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §4.2
# [MODULE] tests.test_models
# [INVARIANTS] FixAction.fingerprint MUST be deterministic; FixStatus transitions MUST be legal
# [MODIFY-GUARD] blueprint.md §4.2; models.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertion errors on invariant violation
# [TESTS] tests/test_models_root.py
# [TTL] task_bound

from __future__ import annotations

import hashlib

import pytest

from zephyr.infrastructure.auto_fix_engine.models import (
    BaseFixer,
    BlastRadius,
    BudgetDecision,
    BudgetInfo,
    ComplianceEvidence,
    FixAction,
    FixConfidence,
    FixDeadLetter,
    FixHealthReport,
    FixHistory,
    FixLevel,
    FixReport,
    FixStatus,
    SafetyDecision,
    ShadowResult,
    ValidationResult,
)


class TestFixLevel:
    def test_enum_values(self):
        assert FixLevel.L1_RULE.value == "l1_rule"
        assert FixLevel.L2_LLM.value == "l2_llm"
        assert FixLevel.L3_AGENT.value == "l3_agent"

    def test_enum_from_string(self):
        assert FixLevel("l1_rule") == FixLevel.L1_RULE
        assert FixLevel("l2_llm") == FixLevel.L2_LLM
        assert FixLevel("l3_agent") == FixLevel.L3_AGENT

    def test_enum_invalid_raises(self):
        with pytest.raises(ValueError):
            FixLevel("invalid_level")


class TestFixConfidence:
    def test_enum_values(self):
        assert FixConfidence.HIGH.value == "high"
        assert FixConfidence.MEDIUM.value == "medium"
        assert FixConfidence.LOW.value == "low"

    def test_enum_from_string(self):
        assert FixConfidence("high") == FixConfidence.HIGH


class TestFixStatus:
    def test_all_status_values(self):
        expected = {
            "pending": FixStatus.PENDING,
            "in_progress": FixStatus.IN_PROGRESS,
            "completed": FixStatus.COMPLETED,
            "failed": FixStatus.FAILED,
            "dead_letter": FixStatus.DEAD_LETTER,
            "approval_pending": FixStatus.APPROVAL_PENDING,
            "cancelled": FixStatus.CANCELLED,
        }
        for val, enum_member in expected.items():
            assert enum_member.value == val

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError):
            FixStatus("nonexistent")


class TestBlastRadius:
    def test_default_values(self):
        br = BlastRadius()
        assert br.files == 0
        assert br.modules == 0
        assert br.lines_estimate == 0
        assert br.risk == "low"

    def test_custom_values(self):
        br = BlastRadius(files=5, modules=2, lines_estimate=100, risk="high")
        assert br.files == 5
        assert br.modules == 2
        assert br.lines_estimate == 100
        assert br.risk == "high"


class TestValidationResult:
    def test_valid_result(self):
        vr = ValidationResult(valid=True, check_name="syntax", evidence="no errors")
        assert vr.valid is True
        assert vr.check_name == "syntax"
        assert vr.evidence == "no errors"
        assert vr.error == ""

    def test_invalid_result(self):
        vr = ValidationResult(valid=False, check_name="file_exists", error="not found")
        assert vr.valid is False
        assert vr.error == "not found"

    def test_default_fields(self):
        vr = ValidationResult(valid=True, check_name="test")
        assert vr.evidence == ""
        assert vr.error == ""


class TestBudgetInfo:
    def test_default_values(self):
        bi = BudgetInfo()
        assert bi.daily_remaining == 50
        assert bi.monthly_remaining == 500
        assert bi.llm_tokens_remaining == 500000

    def test_custom_values(self):
        bi = BudgetInfo(daily_remaining=10, monthly_remaining=100, llm_tokens_remaining=5000)
        assert bi.daily_remaining == 10
        assert bi.monthly_remaining == 100
        assert bi.llm_tokens_remaining == 5000


class TestSafetyDecision:
    def test_approved(self):
        sd = SafetyDecision(approved=True, confidence=FixConfidence.HIGH, reason="ok")
        assert sd.approved is True
        assert sd.confidence == FixConfidence.HIGH

    def test_denied(self):
        sd = SafetyDecision(approved=False, confidence=FixConfidence.LOW, reason="dangerous")
        assert sd.approved is False
        assert sd.reason == "dangerous"

    def test_default_confidence(self):
        sd = SafetyDecision(approved=True)
        assert sd.confidence == FixConfidence.HIGH


class TestBudgetDecision:
    def test_allowed(self):
        bd = BudgetDecision(allowed=True, reason="ok", remaining_daily=40, remaining_monthly=400)
        assert bd.allowed is True
        assert bd.remaining_daily == 40

    def test_denied(self):
        bd = BudgetDecision(allowed=False, reason="exhausted")
        assert bd.allowed is False
        assert bd.remaining_daily == 0
        assert bd.remaining_monthly == 0


class TestFixAction:
    def test_default_creation(self):
        action = FixAction(action_type="zombie_cleanup", target="some/file.py")
        assert action.action_type == "zombie_cleanup"
        assert action.target == "some/file.py"
        assert action.level == FixLevel.L1_RULE
        assert action.status == FixStatus.PENDING
        assert action.confidence == FixConfidence.HIGH
        assert action.attempts == 1
        assert action.retry_count == 0
        assert action.verified is False
        assert action.escalated is False
        assert action.sandbox_verified is False
        assert action.token_cost == 0
        assert len(action.action_id) == 12

    def test_fingerprint_deterministic(self):
        a1 = FixAction(action_type="drift_fix", target="x.py", before="old")
        a2 = FixAction(action_type="drift_fix", target="x.py", before="old")
        assert a1.fingerprint == a2.fingerprint

    def test_fingerprint_auto_computed(self):
        action = FixAction(action_type="test", target="f.py", before="abc")
        expected = hashlib.sha256(b"test:f.py:abc").hexdigest()[:16]
        assert action.fingerprint == expected

    def test_fingerprint_not_overwritten_if_provided(self):
        action = FixAction(action_type="test", target="f.py", fingerprint="custom_fp")
        assert action.fingerprint == "custom_fp"

    def test_fingerprint_differs_for_different_targets(self):
        a1 = FixAction(action_type="fix", target="a.py", before="x")
        a2 = FixAction(action_type="fix", target="b.py", before="x")
        assert a1.fingerprint != a2.fingerprint

    def test_custom_level_and_status(self):
        action = FixAction(
            action_type="llm_fix",
            target="t.py",
            level=FixLevel.L2_LLM,
            status=FixStatus.IN_PROGRESS,
            confidence=FixConfidence.MEDIUM,
        )
        assert action.level == FixLevel.L2_LLM
        assert action.status == FixStatus.IN_PROGRESS
        assert action.confidence == FixConfidence.MEDIUM

    def test_metadata_default_empty(self):
        action = FixAction(action_type="test", target="f.py")
        assert action.metadata == {}

    def test_context_sources_default_empty(self):
        action = FixAction(action_type="test", target="f.py")
        assert action.context_sources == []

    def test_blast_radius_optional(self):
        action = FixAction(action_type="test", target="f.py")
        assert action.blast_radius is None

    def test_with_blast_radius(self):
        br = BlastRadius(files=3, risk="medium")
        action = FixAction(action_type="test", target="f.py", blast_radius=br)
        assert action.blast_radius.files == 3
        assert action.blast_radius.risk == "medium"

    def test_validation_optional(self):
        action = FixAction(action_type="test", target="f.py")
        assert action.validation is None

    def test_with_validation(self):
        vr = ValidationResult(valid=True, check_name="syntax")
        action = FixAction(action_type="test", target="f.py", validation=vr)
        assert action.validation.valid is True


class TestFixHistory:
    def test_default_creation(self):
        fh = FixHistory(action_type="zombie_cleanup", target="f.py")
        assert fh.action_type == "zombie_cleanup"
        assert fh.target == "f.py"
        assert fh.success is False
        assert fh.revert_possible is True
        assert len(fh.fix_id) == 12

    def test_custom_values(self):
        fh = FixHistory(
            action_type="drift_fix",
            target="x.py",
            before_hash="h1",
            after_hash="h2",
            success=True,
            verifier="pytest",
        )
        assert fh.success is True
        assert fh.verifier == "pytest"
        assert fh.before_hash == "h1"


class TestFixDeadLetter:
    def test_creation(self):
        action = FixAction(action_type="test", target="f.py")
        dl = FixDeadLetter(original_fix=action, failure_reason="timeout")
        assert dl.original_fix.action_type == "test"
        assert dl.failure_reason == "timeout"
        assert dl.retry_count == 0
        assert dl.escalated is False
        assert len(dl.dead_letter_id) == 12

    def test_escalated_flag(self):
        action = FixAction(action_type="test", target="f.py")
        dl = FixDeadLetter(original_fix=action, failure_reason="critical", escalated=True)
        assert dl.escalated is True


class TestFixReport:
    def test_default_values(self):
        report = FixReport()
        assert report.total_attempted == 0
        assert report.succeeded == 0
        assert report.failed == 0
        assert report.escalated == 0
        assert report.dead_lettered == 0
        assert report.actions == []
        assert report.cascade_alerts == []

    def test_with_actions(self):
        a1 = FixAction(action_type="fix1", target="a.py", status=FixStatus.COMPLETED)
        a2 = FixAction(action_type="fix2", target="b.py", status=FixStatus.FAILED)
        report = FixReport(total_attempted=2, succeeded=1, failed=1, actions=[a1, a2])
        assert len(report.actions) == 2
        assert report.succeeded == 1
        assert report.failed == 1

    def test_budget_info_default(self):
        report = FixReport()
        assert report.budget_remaining.daily_remaining == 50


class TestFixHealthReport:
    def test_default_healthy(self):
        hr = FixHealthReport()
        assert hr.healthy is True
        assert hr.budget_ok is True
        assert hr.cascade_active is False
        assert hr.dead_letter_count == 0
        assert hr.db_accessible is True
        assert hr.config_loaded is True

    def test_unhealthy_state(self):
        hr = FixHealthReport(
            healthy=False,
            budget_ok=False,
            cascade_active=True,
            dead_letter_count=5,
            approval_queue_size=3,
        )
        assert hr.healthy is False
        assert hr.cascade_active is True
        assert hr.dead_letter_count == 5
        assert hr.approval_queue_size == 3


class TestShadowResult:
    def test_default_values(self):
        sr = ShadowResult()
        assert sr.safe_to_apply is False
        assert sr.test_result is None
        assert sr.type_result is None
        assert sr.lint_result is None
        assert sr.error == ""
        assert sr.shadow_dir == ""

    def test_safe_result(self):
        sr = ShadowResult(safe_to_apply=True, shadow_dir="/tmp/shadow")
        assert sr.safe_to_apply is True
        assert sr.shadow_dir == "/tmp/shadow"


class TestComplianceEvidence:
    def test_default_creation(self):
        ce = ComplianceEvidence(fix_id="fx1", action_type="test", target="f.py")
        assert ce.fix_id == "fx1"
        assert ce.actor == "auto-fix-engine"
        assert len(ce.tamper_proof_hash) > 0

    def test_hash_auto_computed(self):
        ce = ComplianceEvidence(fix_id="fx1", action_type="test", target="f.py")
        raw = f"{ce.fix_id}:{ce.action_type}:{ce.target}:{ce.before_hash}:{ce.after_hash}:{ce.timestamp}"
        expected = hashlib.sha256(raw.encode()).hexdigest()[:32]
        assert ce.tamper_proof_hash == expected

    def test_hash_not_overwritten_if_provided(self):
        ce = ComplianceEvidence(fix_id="fx1", action_type="test", target="f.py", tamper_proof_hash="custom_hash")
        assert ce.tamper_proof_hash == "custom_hash"

    def test_hash_differs_for_different_fixes(self):
        ce1 = ComplianceEvidence(fix_id="fx1", action_type="test", target="a.py")
        ce2 = ComplianceEvidence(fix_id="fx2", action_type="test", target="b.py")
        assert ce1.tamper_proof_hash != ce2.tamper_proof_hash


class TestBaseFixer:
    def test_creation(self):
        fixer = BaseFixer(fixer_id="test_fixer", action_type="test_action")
        assert fixer.fixer_id == "test_fixer"
        assert fixer.action_type == "test_action"
        assert fixer.level == FixLevel.L1_RULE
        assert fixer.dimension == ""
        assert fixer.description == ""

    def test_custom_level(self):
        fixer = BaseFixer(fixer_id="f1", action_type="a1", level=FixLevel.L2_LLM, dimension="security")
        assert fixer.level == FixLevel.L2_LLM
        assert fixer.dimension == "security"

    def test_scan_raises_not_implemented(self):
        fixer = BaseFixer(fixer_id="f1", action_type="a1")
        with pytest.raises(NotImplementedError):
            fixer.scan()

    def test_fix_raises_not_implemented(self):
        fixer = BaseFixer(fixer_id="f1", action_type="a1")
        with pytest.raises(NotImplementedError):
            fixer.fix("target")

    def test_validate_raises_not_implemented(self):
        fixer = BaseFixer(fixer_id="f1", action_type="a1")
        with pytest.raises(NotImplementedError):
            fixer.validate("target")

    def test_rollback_raises_not_implemented(self):
        fixer = BaseFixer(fixer_id="f1", action_type="a1")
        with pytest.raises(NotImplementedError):
            fixer.rollback("target")
