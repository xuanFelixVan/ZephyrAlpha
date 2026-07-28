# [A_test] module_id: SRC-TST-1540 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §6.12
# [MODULE] tests.test_secret_rotation_aware
# [INVARIANTS] exit code 15 when stale secrets found; rotatable secrets auto-rotate
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.rollback.secret_rotation_aware import (
    ROTATION_URLS,
    SECRET_PATTERNS,
    RotationResult,
    SecretRotationAware,
    StaleSecret,
)


class TestStaleSecret:
    def test_creation(self):
        s = StaleSecret(
            file_path=".env",
            secret_type="ZEPHYR_API_KEY",
            age_days=30.0,
            rotatable=True,
            rotation_url="http://localhost:8999/api/keys/rotate",
        )
        assert s.file_path == ".env"
        assert s.rotatable is True

    def test_non_rotatable(self):
        s = StaleSecret(
            file_path=".env",
            secret_type="GITHUB_TOKEN",
            age_days=10.0,
            rotatable=False,
            rotation_url="https://github.com/settings/tokens",
        )
        assert s.rotatable is False


class TestSecretRotationAwareInit:
    def test_default_project_root(self):
        scanner = SecretRotationAware()
        assert scanner.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        scanner = SecretRotationAware(project_root=tmp_path)
        assert scanner.project_root == tmp_path


class TestScan:
    def test_scan_no_env_files(self, tmp_path):
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert isinstance(result, RotationResult)
        assert result.total_secrets == 0
        assert result.stale_secrets == 0
        assert result.rotated == 0
        assert result.deferred == 0
        assert result.exit_code == 0

    def test_scan_with_rotatable_secret(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('ZEPHYR_API_KEY = "sk-test-key-123"\n', encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert result.total_secrets == 1
        assert result.stale_secrets == 1
        assert result.rotated == 1
        assert result.deferred == 0
        assert result.exit_code == 15

    def test_scan_with_non_rotatable_secret(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('GITHUB_TOKEN = "ghp_abc123"\n', encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert result.total_secrets == 1
        assert result.deferred == 1
        assert result.rotated == 0
        assert result.exit_code == 15

    def test_scan_with_multiple_secrets(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            'ZEPHYR_API_KEY = "sk-test"\nGITHUB_TOKEN = "ghp_test"\n',
            encoding="utf-8",
        )
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert result.total_secrets == 2
        assert result.rotated == 1
        assert result.deferred == 1

    def test_scan_empty_env_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("", encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert result.total_secrets == 0
        assert result.exit_code == 0

    def test_scan_env_with_no_secrets(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("SOME_VAR=hello\nOTHER=world\n", encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert result.total_secrets == 0
        assert result.exit_code == 0

    def test_scan_jwt_secret_rotatable(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('JWT_SECRET = "myjwtsecret"\n', encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert result.rotated == 1

    def test_scan_openai_non_rotatable(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('OPENAI_API_KEY = "sk-proj-abc123"\n', encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert result.deferred == 1

    def test_scan_details_content(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('ZEPHYR_API_KEY = "sk-test"\n', encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert any("Rotated" in d for d in result.details)

    def test_scan_multiple_env_files(self, tmp_path):
        (tmp_path / ".env").write_text('ZEPHYR_API_KEY = "sk-test"\n', encoding="utf-8")
        (tmp_path / ".env.local").write_text('GITHUB_TOKEN = "ghp_test"\n', encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        result = scanner.scan()
        assert result.total_secrets == 2


class TestGetDeferredSecrets:
    def test_no_deferred(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('ZEPHYR_API_KEY = "sk-test"\n', encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        deferred = scanner.get_deferred_secrets()
        assert len(deferred) == 0

    def test_has_deferred(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('GITHUB_TOKEN = "ghp_test"\n', encoding="utf-8")
        scanner = SecretRotationAware(project_root=tmp_path)
        deferred = scanner.get_deferred_secrets()
        assert len(deferred) > 0
        assert all(isinstance(s, StaleSecret) for s in deferred)

    def test_no_env_files(self, tmp_path):
        scanner = SecretRotationAware(project_root=tmp_path)
        deferred = scanner.get_deferred_secrets()
        assert deferred == []


class TestSecretPatterns:
    def test_patterns_exist(self):
        assert "ZEPHYR_API_KEY" in SECRET_PATTERNS
        assert "GITHUB_TOKEN" in SECRET_PATTERNS
        assert "OPENAI_API_KEY" in SECRET_PATTERNS
        assert "JWT_SECRET" in SECRET_PATTERNS

    def test_rotation_urls_exist(self):
        assert len(ROTATION_URLS) == len(SECRET_PATTERNS)
