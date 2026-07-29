# [A_test] module_id: MOD-GOV_compliance_auditor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §test
# [MODULE] tests.test_compliance_auditor
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_compliance_auditor.py
# [TTL] task_bound

import os

import pytest

compliance_mod = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.compliance_auditor", reason="compliance_auditor not available"
)
ComplianceAuditor = compliance_mod.ComplianceAuditor

models = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.models", reason="models not available")
FixAction = models.FixAction
FixStatus = models.FixStatus
FixLevel = models.FixLevel
FixConfidence = models.FixConfidence
ComplianceEvidence = models.ComplianceEvidence


@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test_compliance.db")


@pytest.fixture
def auditor(temp_db):
    return ComplianceAuditor(db_path=temp_db, retention_days=90)


@pytest.fixture
def sample_action():
    return FixAction(
        action_type="test_fix",
        level=FixLevel.L1_RULE,
        target="test_file.py",
        before="old content",
        after="new content",
        confidence=FixConfidence.HIGH,
    )


class TestComplianceAuditorInstantiation:
    def test_creates_db_on_init(self, temp_db):
        auditor = ComplianceAuditor(db_path=temp_db)
        assert os.path.exists(temp_db)

    def test_default_retention_days(self, temp_db):
        auditor = ComplianceAuditor(db_path=temp_db)
        assert auditor.retention_days == 90

    def test_custom_retention_days(self, temp_db):
        auditor = ComplianceAuditor(db_path=temp_db, retention_days=30)
        assert auditor.retention_days == 30


class TestComplianceAuditorAuditFix:
    def test_audit_fix_returns_evidence(self, auditor, sample_action):
        evidence = auditor.audit_fix(sample_action)
        assert isinstance(evidence, ComplianceEvidence)
        assert evidence.action_type == "test_fix"
        assert evidence.target == "test_file.py"
        assert evidence.actor == "auto-fix-engine"

    def test_audit_fix_computes_hashes(self, auditor, sample_action):
        evidence = auditor.audit_fix(sample_action)
        assert len(evidence.before_hash) == 32
        assert len(evidence.after_hash) == 32

    def test_audit_fix_with_empty_before(self, auditor):
        action = FixAction(
            action_type="test_fix",
            level=FixLevel.L1_RULE,
            target="test_file.py",
            confidence=FixConfidence.HIGH,
        )
        evidence = auditor.audit_fix(action)
        assert evidence.before_hash == ""

    def test_audit_fix_with_rbac_decision(self, auditor, sample_action):
        evidence = auditor.audit_fix(sample_action, rbac_decision="approved", validation_result="passed")
        assert evidence.rbac_decision == "approved"
        assert evidence.validation_result == "passed"

    def test_audit_fix_tamper_proof_hash(self, auditor, sample_action):
        evidence = auditor.audit_fix(sample_action)
        assert len(evidence.tamper_proof_hash) == 32


class TestComplianceAuditorVerifyEvidence:
    def test_verify_valid_evidence(self, auditor, sample_action):
        evidence = auditor.audit_fix(sample_action)
        assert auditor.verify_evidence(evidence) is True

    def test_verify_tampered_evidence(self, auditor, sample_action):
        evidence = auditor.audit_fix(sample_action)
        tampered = ComplianceEvidence(
            fix_id=evidence.fix_id,
            action_type=evidence.action_type,
            target=evidence.target,
            before_hash=evidence.before_hash,
            after_hash=evidence.after_hash,
            timestamp=evidence.timestamp,
            tamper_proof_hash="tampered_hash_00000000000000000",
        )
        assert auditor.verify_evidence(tampered) is False

    def test_verify_evidence_with_empty_hash(self):
        evidence = ComplianceEvidence(
            fix_id="test",
            action_type="test",
            target="test.py",
        )
        assert evidence.tamper_proof_hash != ""


class TestComplianceAuditorGetEvidence:
    def test_get_evidence_existing(self, auditor, sample_action):
        evidence = auditor.audit_fix(sample_action)
        retrieved = auditor.get_evidence(evidence.fix_id)
        assert retrieved is not None
        assert retrieved.fix_id == evidence.fix_id

    def test_get_evidence_nonexistent(self, auditor):
        result = auditor.get_evidence("nonexistent_id")
        assert result is None


class TestComplianceAuditorCleanupExpired:
    def test_cleanup_returns_int(self, auditor):
        result = auditor.cleanup_expired()
        assert isinstance(result, int)

    def test_cleanup_with_no_expired(self, auditor, sample_action):
        auditor.audit_fix(sample_action)
        result = auditor.cleanup_expired()
        assert result == 0
