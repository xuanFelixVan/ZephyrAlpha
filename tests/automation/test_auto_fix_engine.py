# [A_test] module_id: MOD-GOV_auto_fix_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §test
# [MODULE] zephyr.infrastructure.auto_fix_engine
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_auto_fix_engine.py
# [TTL] task_bound

import hashlib

import pytest

models = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.models", reason="auto-fix-engine.models not available"
)
FixAction = models.FixAction
FixStatus = models.FixStatus
FixLevel = models.FixLevel
FixConfidence = models.FixConfidence
ComplianceEvidence = models.ComplianceEvidence
BaseFixer = models.BaseFixer
BlastRadius = models.BlastRadius
ValidationResult = models.ValidationResult
BudgetInfo = models.BudgetInfo
FixReport = models.FixReport
FixDeadLetter = models.FixDeadLetter


class TestFixStatus:
    def test_all_enum_values(self):
        expected = {"PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "DEAD_LETTER", "APPROVAL_PENDING", "CANCELLED"}
        actual = {e.name for e in FixStatus}
        assert actual == expected

    def test_string_values(self):
        assert FixStatus.PENDING.value == "pending"
        assert FixStatus.IN_PROGRESS.value == "in_progress"
        assert FixStatus.COMPLETED.value == "completed"
        assert FixStatus.FAILED.value == "failed"
        assert FixStatus.DEAD_LETTER.value == "dead_letter"
        assert FixStatus.APPROVAL_PENDING.value == "approval_pending"
        assert FixStatus.CANCELLED.value == "cancelled"

    def test_is_str_enum(self):
        assert isinstance(FixStatus.PENDING, str)
        assert FixStatus.PENDING == "pending"


class TestFixLevel:
    def test_all_enum_values(self):
        expected = {"L1_RULE", "L2_LLM", "L3_AGENT"}
        actual = {e.name for e in FixLevel}
        assert actual == expected

    def test_string_values(self):
        assert FixLevel.L1_RULE.value == "l1_rule"
        assert FixLevel.L2_LLM.value == "l2_llm"
        assert FixLevel.L3_AGENT.value == "l3_agent"

    def test_is_str_enum(self):
        assert isinstance(FixLevel.L1_RULE, str)


class TestFixConfidence:
    def test_all_enum_values(self):
        expected = {"HIGH", "MEDIUM", "LOW"}
        actual = {e.name for e in FixConfidence}
        assert actual == expected

    def test_string_values(self):
        assert FixConfidence.HIGH.value == "high"
        assert FixConfidence.MEDIUM.value == "medium"
        assert FixConfidence.LOW.value == "low"


class TestFixAction:
    def test_creation_with_required_fields(self):
        action = FixAction(action_type="rename_var", target="foo.py:L10")
        assert action.action_type == "rename_var"
        assert action.target == "foo.py:L10"
        assert action.level == FixLevel.L1_RULE
        assert action.status == FixStatus.PENDING
        assert action.confidence == FixConfidence.HIGH
        assert action.attempts == 1
        assert action.retry_count == 0
        assert action.verified is False
        assert action.escalated is False
        assert action.sandbox_verified is False

    def test_fingerprint_auto_computed(self):
        action = FixAction(action_type="rename_var", target="foo.py:L10", before="old_val")
        raw = "rename_var:foo.py:L10:old_val"
        expected = hashlib.sha256(raw.encode()).hexdigest()[:16]
        assert action.fingerprint == expected

    def test_fingerprint_preserved_if_provided(self):
        action = FixAction(action_type="rename_var", target="foo.py:L10", fingerprint="custom_fp")
        assert action.fingerprint == "custom_fp"

    def test_fingerprint_deterministic(self):
        a1 = FixAction(action_type="rename_var", target="foo.py:L10", before="old")
        a2 = FixAction(action_type="rename_var", target="foo.py:L10", before="old")
        assert a1.fingerprint == a2.fingerprint

    def test_fingerprint_differs_for_different_targets(self):
        a1 = FixAction(action_type="rename_var", target="foo.py:L10", before="old")
        a2 = FixAction(action_type="rename_var", target="bar.py:L20", before="old")
        assert a1.fingerprint != a2.fingerprint

    def test_default_action_id_is_12_chars(self):
        action = FixAction(action_type="rename_var", target="foo.py")
        assert len(action.action_id) == 12

    def test_timestamp_is_utc(self):
        action = FixAction(action_type="rename_var", target="foo.py")
        assert action.timestamp.tzinfo is not None

    def test_metadata_default_empty(self):
        action = FixAction(action_type="rename_var", target="foo.py")
        assert action.metadata == {}

    def test_with_blast_radius(self):
        br = BlastRadius(files=3, modules=1, lines_estimate=50, risk="medium")
        action = FixAction(action_type="rename_var", target="foo.py", blast_radius=br)
        assert action.blast_radius.files == 3
        assert action.blast_radius.risk == "medium"

    def test_with_validation_result(self):
        vr = ValidationResult(valid=True, check_name="syntax", evidence="no errors")
        action = FixAction(action_type="rename_var", target="foo.py", validation=vr)
        assert action.validation.valid is True
        assert action.validation.check_name == "syntax"

    def test_empty_before_fingerprint(self):
        action = FixAction(action_type="delete_file", target="temp.py", before="")
        raw = "delete_file:temp.py:"
        expected = hashlib.sha256(raw.encode()).hexdigest()[:16]
        assert action.fingerprint == expected


class TestComplianceEvidence:
    def test_creation_with_required_fields(self):
        evidence = ComplianceEvidence(fix_id="fx123", action_type="rename_var", target="foo.py")
        assert evidence.fix_id == "fx123"
        assert evidence.action_type == "rename_var"
        assert evidence.target == "foo.py"
        assert evidence.actor == "auto-fix-engine"

    def test_tamper_proof_hash_auto_computed(self):
        evidence = ComplianceEvidence(fix_id="fx123", action_type="rename_var", target="foo.py")
        assert len(evidence.tamper_proof_hash) == 32
        assert evidence.tamper_proof_hash != ""

    def test_tamper_proof_hash_preserved_if_provided(self):
        evidence = ComplianceEvidence(
            fix_id="fx123", action_type="rename_var", target="foo.py", tamper_proof_hash="custom_hash_1234567890123456"
        )
        assert evidence.tamper_proof_hash == "custom_hash_1234567890123456"

    def test_tamper_proof_hash_deterministic(self):
        e1 = ComplianceEvidence(fix_id="fx123", action_type="rename_var", target="foo.py")
        e2 = ComplianceEvidence(fix_id="fx123", action_type="rename_var", target="foo.py")
        assert e1.tamper_proof_hash == e2.tamper_proof_hash

    def test_timestamp_auto_generated(self):
        evidence = ComplianceEvidence(fix_id="fx123", action_type="rename_var", target="foo.py")
        assert evidence.timestamp != ""

    def test_default_fields(self):
        evidence = ComplianceEvidence(fix_id="fx123", action_type="rename_var", target="foo.py")
        assert evidence.before_hash == ""
        assert evidence.after_hash == ""
        assert evidence.confidence == ""
        assert evidence.rbac_decision == ""
        assert evidence.validation_result == ""
        assert evidence.audit_trail_id == ""


class TestBaseFixer:
    def test_creation(self):
        fixer = BaseFixer(fixer_id="fixer_001", action_type="rename_var")
        assert fixer.fixer_id == "fixer_001"
        assert fixer.action_type == "rename_var"
        assert fixer.level == FixLevel.L1_RULE

    def test_scan_raises_not_implemented(self):
        fixer = BaseFixer(fixer_id="fixer_001", action_type="rename_var")
        with pytest.raises(NotImplementedError):
            fixer.scan()

    def test_fix_raises_not_implemented(self):
        fixer = BaseFixer(fixer_id="fixer_001", action_type="rename_var")
        with pytest.raises(NotImplementedError):
            fixer.fix("target")

    def test_validate_raises_not_implemented(self):
        fixer = BaseFixer(fixer_id="fixer_001", action_type="rename_var")
        with pytest.raises(NotImplementedError):
            fixer.validate("target")

    def test_rollback_raises_not_implemented(self):
        fixer = BaseFixer(fixer_id="fixer_001", action_type="rename_var")
        with pytest.raises(NotImplementedError):
            fixer.rollback("target")

    def test_with_optional_fields(self):
        fixer = BaseFixer(
            fixer_id="fixer_002",
            action_type="refactor",
            level=FixLevel.L2_LLM,
            dimension="quality",
            description="Refactor module",
        )
        assert fixer.level == FixLevel.L2_LLM
        assert fixer.dimension == "quality"
        assert fixer.description == "Refactor module"


class TestBlastRadius:
    def test_defaults(self):
        br = BlastRadius()
        assert br.files == 0
        assert br.modules == 0
        assert br.lines_estimate == 0
        assert br.risk == "low"

    def test_custom_values(self):
        br = BlastRadius(files=5, modules=2, lines_estimate=100, risk="high")
        assert br.files == 5
        assert br.risk == "high"


class TestValidationResult:
    def test_creation(self):
        vr = ValidationResult(valid=True, check_name="syntax")
        assert vr.valid is True
        assert vr.check_name == "syntax"
        assert vr.evidence == ""
        assert vr.error == ""

    def test_with_error(self):
        vr = ValidationResult(valid=False, check_name="lint", error="E501 line too long")
        assert vr.valid is False
        assert vr.error == "E501 line too long"


class TestBudgetInfo:
    def test_defaults(self):
        bi = BudgetInfo()
        assert bi.daily_remaining == 50
        assert bi.monthly_remaining == 500
        assert bi.llm_tokens_remaining == 500000


class TestFixReport:
    def test_defaults(self):
        report = FixReport()
        assert report.total_attempted == 0
        assert report.succeeded == 0
        assert report.failed == 0
        assert report.actions == []

    def test_with_actions(self):
        action = FixAction(action_type="rename_var", target="foo.py")
        report = FixReport(total_attempted=1, succeeded=1, actions=[action])
        assert len(report.actions) == 1
        assert report.actions[0].action_type == "rename_var"


class TestFixDeadLetter:
    def test_creation(self):
        action = FixAction(action_type="rename_var", target="foo.py")
        dl = FixDeadLetter(original_fix=action, failure_reason="timeout")
        assert dl.failure_reason == "timeout"
        assert dl.original_fix.action_type == "rename_var"
        assert dl.retry_count == 0
        assert dl.escalated is False
