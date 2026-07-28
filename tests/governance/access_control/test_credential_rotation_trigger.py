# [A_test] module_id: SRC-TST-0636 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_credential_rotation_trigger
# [INVARIANTS] scan_and_rotate exit_code=43 on leak; exit_code=0 on no leak; notify returns action key
# [MODIFY-GUARD] blueprint.md §4
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError on invariant violation
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.credential_rotation_trigger import (
    CREDENTIAL_PATTERNS,
    CredentialRotationTrigger,
    CredentialScanResult,
)


@pytest.fixture
def trigger(tmp_path: Path) -> CredentialRotationTrigger:
    return CredentialRotationTrigger(project_root=tmp_path)


class TestCredentialScanResult:
    def test_creation(self):
        result = CredentialScanResult(
            files_scanned=1,
            credentials_detected=2,
            credentials_rotated=0,
            leaks_detected=0,
            exit_code=0,
        )
        assert result.files_scanned == 1
        assert result.credentials_detected == 2
        assert result.exit_code == 0
        assert result.details == []

    def test_creation_with_details(self):
        result = CredentialScanResult(
            files_scanned=2,
            credentials_detected=3,
            credentials_rotated=1,
            leaks_detected=1,
            exit_code=43,
            details=["leak found"],
        )
        assert result.leaks_detected == 1
        assert result.exit_code == 43
        assert result.details == ["leak found"]


class TestCredentialPatterns:
    def test_patterns_exist(self):
        assert len(CREDENTIAL_PATTERNS) > 0

    def test_pattern_structure(self):
        for name, pattern in CREDENTIAL_PATTERNS:
            assert isinstance(name, str)
            assert isinstance(pattern, str)
            assert len(name) > 0
            assert len(pattern) > 0

    def test_aws_key_pattern(self):
        import re

        aws_name, aws_pat = [p for p in CREDENTIAL_PATTERNS if p[0] == "AWS_KEY"][0]
        assert re.search(aws_pat, "AKIAIOSFODNN7EXAMPLE")

    def test_github_token_pattern(self):
        import re

        gh_name, gh_pat = [p for p in CREDENTIAL_PATTERNS if p[0] == "GITHUB_TOKEN"][0]
        assert re.search(gh_pat, "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn")


class TestCredentialRotationTriggerInstantiation:
    def test_default_project_root(self):
        crt = CredentialRotationTrigger()
        assert crt.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path):
        crt = CredentialRotationTrigger(project_root=tmp_path)
        assert crt.project_root == tmp_path

    def test_exit_code_constant(self):
        assert CredentialRotationTrigger.EXIT_CODE_CREDENTIAL_LEAK == 43


class TestScanAndRotate:
    def test_no_sensitive_files(self, trigger: CredentialRotationTrigger):
        result = trigger.scan_and_rotate()
        assert result.files_scanned == 0
        assert result.credentials_detected == 0
        assert result.leaks_detected == 0
        assert result.exit_code == 0

    def test_clean_env_file(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / ".env").write_text("APP_NAME=MyApp\nDEBUG=false\n", encoding="utf-8")
        result = trigger.scan_and_rotate()
        assert result.files_scanned == 1
        assert result.credentials_detected == 0
        assert result.exit_code == 0

    def test_env_file_with_api_key(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / ".env").write_text('API_KEY="abcdefgh12345678"\nAPP_NAME=MyApp\n', encoding="utf-8")
        result = trigger.scan_and_rotate()
        assert result.files_scanned == 1
        assert result.credentials_detected >= 1
        assert result.exit_code == 0

    def test_aws_key_leak(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / ".env").write_text("AWS_ACCESS=AKIAIOSFODNN7EXAMPLE\n", encoding="utf-8")
        result = trigger.scan_and_rotate()
        assert result.leaks_detected >= 1
        assert result.exit_code == 43

    def test_github_token_leak(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / ".env.local").write_text(
            "GITHUB_TOKEN=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn\n", encoding="utf-8"
        )
        result = trigger.scan_and_rotate()
        assert result.leaks_detected >= 1
        assert result.exit_code == 43

    def test_private_key_detected(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / "config.yaml").write_text("key: |\n  -----BEGIN RSA PRIVATE KEY-----\n  data\n", encoding="utf-8")
        result = trigger.scan_and_rotate()
        assert result.credentials_detected >= 1

    def test_multiple_sensitive_files(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / ".env").write_text("APP=ok\n", encoding="utf-8")
        (tmp_path / "config.yaml").write_text("debug: true\n", encoding="utf-8")
        result = trigger.scan_and_rotate()
        assert result.files_scanned == 2

    def test_non_sensitive_file_ignored(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / "main.py").write_text('api_key = "secret12345678"\n', encoding="utf-8")
        result = trigger.scan_and_rotate()
        assert result.files_scanned == 0

    def test_credentials_rotated_always_zero(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / ".env").write_text('API_KEY="abcdefgh12345678"\n', encoding="utf-8")
        result = trigger.scan_and_rotate()
        assert result.credentials_rotated == 0

    def test_details_populated_on_detection(self, trigger: CredentialRotationTrigger, tmp_path: Path):
        (tmp_path / ".env").write_text('API_KEY="abcdefgh12345678"\n', encoding="utf-8")
        result = trigger.scan_and_rotate()
        assert len(result.details) >= 1


class TestNotifyRotationNeeded:
    def test_returns_dict(self):
        result = CredentialRotationTrigger.notify_rotation_needed("test leak")
        assert isinstance(result, dict)

    def test_contains_action(self):
        result = CredentialRotationTrigger.notify_rotation_needed("test leak")
        assert result["action"] == "CREDENTIAL_ROTATION_REQUIRED"

    def test_contains_reason(self):
        result = CredentialRotationTrigger.notify_rotation_needed("AWS key exposed")
        assert result["reason"] == "AWS key exposed"

    def test_contains_timestamp(self):
        result = CredentialRotationTrigger.notify_rotation_needed("test")
        assert "timestamp_utc" in result
        assert len(result["timestamp_utc"]) > 0

    def test_contains_instructions(self):
        result = CredentialRotationTrigger.notify_rotation_needed("test")
        assert "instructions" in result
        assert "rotate" in result["instructions"].lower()

    def test_empty_reason(self):
        result = CredentialRotationTrigger.notify_rotation_needed("")
        assert result["reason"] == ""

    def test_is_static_method(self):
        assert isinstance(CredentialRotationTrigger.__dict__["notify_rotation_needed"], staticmethod)
