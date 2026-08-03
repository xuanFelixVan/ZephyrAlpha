# [A_test] module_id: MOD-GOV_right_to_be_forgotten | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_right_to_be_forgotten
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] GDPR遗忘权;hash不可逆;exit_code_19=GDPR_BLOCKED
# [MODIFY-GUARD] blueprint.md §4;src/zephyr/rollback/__init__.py
# [CONSUMERS] CI;pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] UnicodeDecodeError;OSError
# [TESTS] self
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.rollback.right_to_be_forgotten import (
    EXIT_GDPR_BLOCKED,
    ForgottenUser,
    PurgeResult,
    RightToBeForgotten,
    SensitiveMatch,
)


class TestForgottenUser:
    def test_instantiation(self):
        u = ForgottenUser(
            user_hash="abc123",
            registered_at="2026-01-01T00:00:00",
            request_id="REQ-001",
        )
        assert u.user_hash == "abc123"
        assert u.registered_at == "2026-01-01T00:00:00"
        assert u.request_id == "REQ-001"
        assert u.reason == "GDPR Article 17"

    def test_custom_reason(self):
        u = ForgottenUser(
            user_hash="abc",
            registered_at="2026-01-01",
            request_id="REQ-002",
            reason="User request",
        )
        assert u.reason == "User request"


class TestPurgeResult:
    def test_instantiation_defaults(self):
        p = PurgeResult(purged=True, files_purged=[], files_blocked=[])
        assert p.purged is True
        assert p.files_purged == []
        assert p.files_blocked == []
        assert p.gdpr_blocked is False
        assert p.exit_code == 0

    def test_gdpr_blocked(self):
        p = PurgeResult(
            purged=False,
            files_purged=[],
            files_blocked=["file1.txt"],
            gdpr_blocked=True,
            exit_code=EXIT_GDPR_BLOCKED,
        )
        assert p.gdpr_blocked is True
        assert p.exit_code == 19


class TestSensitiveMatch:
    def test_instantiation(self):
        m = SensitiveMatch(pattern="email", matched_content="ab**cd", file_path="f.txt")
        assert m.pattern == "email"
        assert m.matched_content == "ab**cd"
        assert m.file_path == "f.txt"
        assert m.line_number == 0


class TestRightToBeForgotten:
    def test_instantiation_with_tmp_dir(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        assert rtbf.registry_dir == tmp_path / "gdpr"
        assert len(rtbf.forgotten_hashes) == 0

    def test_instantiation_default_dir(self):
        rtbf = RightToBeForgotten()
        assert rtbf.registry_dir == Path("data/rollback/gdpr")

    def test_register_forgotten_user(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        user = rtbf.register_forgotten_user("user@example.com", request_id="REQ-001")
        assert isinstance(user, ForgottenUser)
        assert user.request_id == "REQ-001"
        assert user.reason == "GDPR Article 17"
        assert rtbf.is_forgotten("user@example.com") is True

    def test_register_forgotten_user_auto_request_id(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        user = rtbf.register_forgotten_user("user@example.com")
        assert user.request_id.startswith("GDPR-REQ-")

    def test_is_forgotten_false_for_unknown(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        assert rtbf.is_forgotten("unknown@example.com") is False

    def test_is_forgotten_case_insensitive(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        rtbf.register_forgotten_user("User@Example.COM")
        assert rtbf.is_forgotten("user@example.com") is True

    def test_is_forgotten_whitespace_trimmed(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        rtbf.register_forgotten_user("  user@example.com  ")
        assert rtbf.is_forgotten("user@example.com") is True

    def test_scan_files_for_forgotten_data_empty_list(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        result = rtbf.scan_files_for_forgotten_data([], project_root=tmp_path)
        assert result == []

    def test_scan_files_for_forgotten_data_nonexistent_file(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        rtbf.register_forgotten_user("test@example.com")
        result = rtbf.scan_files_for_forgotten_data(["nonexistent.txt"], project_root=tmp_path)
        assert result == []

    def test_scan_files_detects_forgotten_email(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        rtbf.register_forgotten_user("test@example.com")
        (tmp_path / "data.txt").write_text("contact test@example.com for info", encoding="utf-8")
        matches = rtbf.scan_files_for_forgotten_data(["data.txt"], project_root=tmp_path)
        assert len(matches) >= 1
        assert matches[0].pattern == "email"
        assert matches[0].file_path == "data.txt"

    def test_purge_sensitive_data_no_matches(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        result = rtbf.purge_sensitive_data(["somefile.txt"], project_root=tmp_path)
        assert result.purged is True
        assert result.gdpr_blocked is False
        assert result.exit_code == 0

    def test_purge_sensitive_data_with_email(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        rtbf.register_forgotten_user("test@example.com")
        (tmp_path / "data.txt").write_text("email: test@example.com", encoding="utf-8")
        result = rtbf.purge_sensitive_data(["data.txt"], project_root=tmp_path)
        assert result.purged is True
        assert "data.txt" in result.files_purged
        content = (tmp_path / "data.txt").read_text(encoding="utf-8")
        assert "[REDACTED-EMAIL]" in content
        assert "test@example.com" not in content

    def test_check_restore_safety_blocked(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        user = rtbf.register_forgotten_user("test@example.com")
        result = rtbf.check_restore_safety(
            ["file1.txt"],
            snapshot_data=f"some data with {user.user_hash} inside",
        )
        assert result.gdpr_blocked is True
        assert result.exit_code == EXIT_GDPR_BLOCKED
        assert result.purged is False

    def test_check_restore_safety_safe(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        rtbf.register_forgotten_user("test@example.com")
        result = rtbf.check_restore_safety(
            ["file1.txt"],
            snapshot_data="clean data without any hashes",
        )
        assert result.gdpr_blocked is False
        assert result.exit_code == 0

    def test_registry_persistence(self, tmp_path):
        gdpr_dir = tmp_path / "gdpr"
        rtbf1 = RightToBeForgotten(registry_dir=gdpr_dir)
        rtbf1.register_forgotten_user("persist@example.com")
        rtbf2 = RightToBeForgotten(registry_dir=gdpr_dir)
        assert rtbf2.is_forgotten("persist@example.com") is True

    def test_mask_identifier_short(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        assert rtbf.mask_identifier("ab") == "****"

    def test_mask_identifier_long(self, tmp_path):
        rtbf = RightToBeForgotten(registry_dir=tmp_path / "gdpr")
        masked = rtbf.mask_identifier("abcdefgh")
        assert masked.startswith("ab")
        assert masked.endswith("gh")
        assert "*" in masked
