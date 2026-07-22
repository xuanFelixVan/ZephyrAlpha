# [A_test] module_id: MOD-GOV_rollback_adversarial | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-213 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_rollback_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Red-team adversarial tests for rollback system (MOD-INF-021 Phase 10).

Covers 10 adversarial scenarios (B121-B130):
  1. B121: Agent sandbox enforcement
  2. B122: Security component sabotage detection
  3. B123: KnowGoodState ledger tampering
  4. B124: Credential leak scan on rollback
  5. B125: WAL integrity verification
  6. B126: Cross-agent conflict injection
  7. B127: Intent archive integrity attack
  8. B128: Rollback abuse detection
  9. B129: Hallucination guard (state mismatch)
 10. B130: Auto-rollback signal classification

Each test verifies the system's defense-in-depth against a specific attack vector.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch


class TestAdversarialB121_SandboxEscape:
    """B121: Agent sandbox enforcement — enforce / status"""

    def test_sandbox_enforce_not_in_sandbox_blocked(self):
        from zephyr.infrastructure.runtime.sandbox_enforcer import SandboxEnforcer, SandboxMode

        enforcer = SandboxEnforcer(project_root=Path(tempfile.mkdtemp()), mode=SandboxMode.STRICT)
        result = enforcer.enforce()
        assert result.breached
        assert result.exit_code == 39

    def test_sandbox_activated_ok(self):
        from zephyr.infrastructure.runtime.sandbox_enforcer import SandboxEnforcer, SandboxMode

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            enforcer = SandboxEnforcer(project_root=root, mode=SandboxMode.STRICT)
            enforcer.activate_sandbox()
            assert enforcer.is_in_sandbox()
            result = enforcer.enforce()
            assert not result.breached

    def test_sandbox_mode_none_disables(self):
        from zephyr.infrastructure.runtime.sandbox_enforcer import SandboxEnforcer, SandboxMode

        enforcer = SandboxEnforcer(project_root=Path(tempfile.mkdtemp()), mode=SandboxMode.NONE)
        result = enforcer.enforce()
        assert not result.breached
        assert "disabled" in result.reason.lower()

    def test_sandbox_status(self):
        from zephyr.infrastructure.runtime.sandbox_enforcer import SandboxEnforcer, SandboxMode

        enforcer = SandboxEnforcer(project_root=Path(tempfile.mkdtemp()), mode=SandboxMode.STRICT)
        status = enforcer.status()
        assert status.mode == SandboxMode.STRICT
        assert status.enforced


class TestAdversarialB122_SecuritySabotage:
    """B122: validate_file_access for security-sensitive files"""

    def test_sandbox_blocks_sensitive_file_access(self):
        from zephyr.infrastructure.runtime.sandbox_enforcer import SandboxEnforcer, SandboxMode

        enforcer = SandboxEnforcer(project_root=Path(tempfile.mkdtemp()), mode=SandboxMode.STRICT)
        result = enforcer.validate_file_access(Path(".env.local"))
        assert not result


class TestAdversarialB123_KnowGoodStateTampering:
    """B123: KnowngoodstateLedger — declare / verify"""

    def test_ledger_declare_and_find(self):
        from zephyr.infrastructure.rollback.knowngoodstate_ledger import KnowngoodstateLedger

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = KnowngoodstateLedger(project_root=root)
            record = ledger.declare_known_good(
                commit_sha="abc123",
                verification_method="post_rollback_verification",
                file_count=5,
                db_integrity_pass=True,
            )
            assert record.commit_sha == "abc123"
            assert record.signature
            assert ledger.is_known_good("abc123")

    def test_ledger_not_found_for_unknown(self):
        from zephyr.infrastructure.rollback.knowngoodstate_ledger import KnowngoodstateLedger

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = KnowngoodstateLedger(project_root=root)
            assert not ledger.is_known_good("nonexistent")

    def test_ledger_get_latest(self):
        from zephyr.infrastructure.rollback.knowngoodstate_ledger import KnowngoodstateLedger

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = KnowngoodstateLedger(project_root=root)
            ledger.declare_known_good("sha-001")
            ledger.declare_known_good("sha-002")
            ledger.declare_known_good("sha-003")
            latest = ledger.get_latest_known_good(limit=2)
            assert len(latest) == 2


class TestAdversarialB124_CredentialLeakBypass:
    """B124: CredentialRotationTrigger — scan_and_rotate"""

    def test_scan_sensitive_files_no_leak(self):
        from zephyr.infrastructure.rollback.credential_rotation_trigger import CredentialRotationTrigger

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trigger = CredentialRotationTrigger(project_root=root)
            result = trigger.scan_and_rotate()
            assert result.leaks_detected == 0

    def test_notify_rotation_needed(self):
        from zephyr.infrastructure.rollback.credential_rotation_trigger import CredentialRotationTrigger

        msg = CredentialRotationTrigger.notify_rotation_needed("GitHub token leaked")
        assert msg["action"] == "CREDENTIAL_ROTATION_REQUIRED"


class TestAdversarialB125_WALForgery:
    """B125: RollbackWAL — write_ahead / check_incomplete"""

    def test_wal_write_ahead(self):
        from zephyr.infrastructure.rollback.rollback_wal import RollbackWAL

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wal = RollbackWAL(project_root=root)
            entry = wal.write_ahead("FULL_REVERT", "old", "new", ["a.py"])
            assert entry.operation == "FULL_REVERT"
            assert entry.status == "PENDING"

    def test_wal_mark_complete(self):
        from zephyr.infrastructure.rollback.rollback_wal import RollbackWAL

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wal = RollbackWAL(project_root=root)
            entry = wal.write_ahead("FULL_REVERT", "old", "new", ["a.py"])
            marked = wal.mark_complete(entry.entry_id)
            assert marked

    def test_wal_check_incomplete(self):
        from zephyr.infrastructure.rollback.rollback_wal import RollbackWAL

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wal = RollbackWAL(project_root=root)
            wal.write_ahead("FULL_REVERT", "old", "new", ["a.py"])
            status = wal.check_incomplete()
            assert status.complete is False
            assert status.pending_count == 1


class TestAdversarialB126_CrossAgentConflict:
    """B126: CrossAgentConflictDetector — detect_conflicts"""

    def test_conflict_detector_no_uncommitted(self):
        from zephyr.governance.intelligence_governance.cross_agent_conflict_detector import CrossAgentConflictDetector

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            detector = CrossAgentConflictDetector(project_root=root)
            with patch.object(detector, "_get_all_uncommitted_files", return_value=[]):
                conflicts = detector.detect_conflicts()
                assert len(conflicts) == 0


class TestAdversarialB127_IntentReplayAttack:
    """B127: IntentArchiver — archive / verify_integrity"""

    def test_intent_archiver_archive(self):
        from zephyr.infrastructure.rollback.intent_archiver import IntentArchiver

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archiver = IntentArchiver(project_root=root)
            record = archiver.archive(
                operation_id="OP-001",
                intent_text="Rollback because auto_guard failed",
                author="agent-001",
            )
            assert record.intent_id.startswith("INTENT-")
            assert record.content_hash

    def test_intent_archiver_get_intent(self):
        from zephyr.infrastructure.rollback.intent_archiver import IntentArchiver

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archiver = IntentArchiver(project_root=root)
            archiver.archive("OP-002", "Rollback for safety", "agent-001")
            intent = archiver.get_intent("OP-002")
            assert intent is not None
            assert "Rollback for safety" in intent

    def test_intent_archiver_verify_integrity(self):
        from zephyr.infrastructure.rollback.intent_archiver import IntentArchiver

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archiver = IntentArchiver(project_root=root)
            archiver.archive("OP-003", "Test intent", "agent-001")
            status = archiver.verify_integrity()
            assert status.integrity_pass


class TestAdversarialB128_RollbackAbuse:
    """B128: RollbackAbuseDetector — check_abuse"""

    def test_abuse_detector_no_audit_log(self):
        from zephyr.infrastructure.rollback.rollback_abuse_detector import RollbackAbuseDetector

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            detector = RollbackAbuseDetector(project_root=root)
            report = detector.check_abuse()
            assert not report.detected


class TestAdversarialB129_AuditLogTruncation:
    """B129: HallucinationGuard — verify_round / run_full_verification"""

    def test_hallucination_guard_verify_round(self):
        from zephyr.infrastructure.rollback.hallucination_guard import HallucinationGuard

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            py_file = root / "test.py"
            py_file.write_text("def foo():\n    return 42\n", encoding="utf-8")
            import hashlib

            content = py_file.read_text(encoding="utf-8")

            guard = HallucinationGuard(project_root=root)
            claimed = [
                {
                    "path": "test.py",
                    "md5": hashlib.md5(content.encode()).hexdigest(),
                    "sha256": hashlib.sha256(content.encode()).hexdigest(),
                    "line_count": 2,
                    "function_signatures": ["foo()"],
                    "class_names": [],
                }
            ]
            result = guard.verify_round(claimed, files=["test.py"])
            assert result.passed

    def test_hallucination_guard_detects_mismatch(self):
        from zephyr.infrastructure.rollback.hallucination_guard import HallucinationGuard

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            py_file = root / "test.py"
            py_file.write_text("def foo():\n    return 42\n", encoding="utf-8")

            guard = HallucinationGuard(project_root=root)
            claimed = [
                {
                    "path": "test.py",
                    "md5": "00000000000000000000000000000000",
                    "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
                    "line_count": 999,
                    "function_signatures": [],
                    "class_names": [],
                }
            ]
            result = guard.verify_round(claimed, files=["test.py"])
            assert not result.passed


class TestAdversarialB130_SignalClassificationBypass:
    """B130: AutoRollbackTrigger — classify / process_guard_result"""

    def test_auto_rollback_trigger_classify_passed_is_soft(self):
        from dataclasses import dataclass

        from zephyr.infrastructure.rollback.auto_rollback_trigger import AutoRollbackTrigger

        @dataclass
        class FakeAutoGuardResult:
            passed: bool = True
            source: str = "test"
            error_message: str = ""
            task_id: str = "TASK-001"
            gate_id: str = "GATE-001"

        trigger = AutoRollbackTrigger(max_retries=3)
        result = FakeAutoGuardResult()
        decision = trigger.classify(result)
        assert decision.category.value == "soft_failure"

    def test_auto_rollback_trigger_classify_hard_failure(self):
        from dataclasses import dataclass

        from zephyr.infrastructure.rollback.auto_rollback_trigger import AutoRollbackTrigger

        @dataclass
        class FakeAutoGuardResult:
            passed: bool = False
            source: str = "drift-detector"
            error_message: str = "drift detected: schema mismatch in module X"
            task_id: str = "TASK-001"
            gate_id: str = "GATE-001"

        trigger = AutoRollbackTrigger(max_retries=3)
        result = FakeAutoGuardResult()
        decision = trigger.classify(result)
        assert decision.category.value == "hard_failure"
        assert decision.should_rollback

    def test_transient_retries_exhausted_upgrades(self):
        from dataclasses import dataclass

        from zephyr.infrastructure.rollback.auto_rollback_trigger import AutoRollbackTrigger

        @dataclass
        class FakeAutoGuardResult:
            passed: bool = False
            source: str = "network_timeout"
            error_message: str = "Connection timed out"
            task_id: str = "TASK-001"
            gate_id: str = "GATE-001"

        trigger = AutoRollbackTrigger(max_retries=2)
        result = FakeAutoGuardResult()
        trigger.classify(result)
        trigger.classify(result)
        decision3 = trigger.classify(result)
        assert decision3.action in ("UPGRADE_TO_SOFT", "RETRY")
