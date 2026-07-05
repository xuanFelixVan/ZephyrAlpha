# [A_test] module_id: SRC-TST-1546 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_security_secrets

# [INVARIANTS] sanitize_secret绝不暴露原始值;EnvSecretProvider从environ读取;DotEnvSecretProvider优先级env>.env

# [MODIFY-GUARD] secrets.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] SecretsError

# [TESTS] pytest tests/test_security_secrets.py -q
# [TTL] task_bound

import asyncio

import pytest

from zephyr.shared.security.secrets import (
    SECRET_INDICATOR_PATTERNS,
    DotEnvSecretProvider,
    EnvSecretProvider,
    SecretProvider,
    SecretsError,
    sanitize_secret,
)


class TestSanitizeSecret:
    def test_redacts_value(self):
        result = sanitize_secret("API_KEY", "sk-1234567890abcdef")
        assert "sk-1234567890abcdef" not in result
        assert "***REDACTED***" in result

    def test_shows_length(self):
        result = sanitize_secret("KEY", "abc")
        assert "len=3" in result

    def test_empty_value(self):
        result = sanitize_secret("KEY", "")
        assert "len=0" in result

    def test_long_value(self):
        result = sanitize_secret("KEY", "x" * 1000)
        assert "len=1000" in result
        assert "x" * 1000 not in result


class TestSecretIndicatorPatterns:
    def test_contains_common_patterns(self):
        assert "KEY" in SECRET_INDICATOR_PATTERNS
        assert "TOKEN" in SECRET_INDICATOR_PATTERNS
        assert "SECRET" in SECRET_INDICATOR_PATTERNS
        assert "PASSWORD" in SECRET_INDICATOR_PATTERNS


class TestEnvSecretProvider:
    def test_get_existing_secret(self, monkeypatch):
        monkeypatch.setenv("TEST_SECRET_001", "my-secret-value")
        provider = EnvSecretProvider()
        result = asyncio.get_event_loop().run_until_complete(provider.get_secret("TEST_SECRET_001"))
        assert result == "my-secret-value"

    def test_get_missing_secret_raises(self):
        provider = EnvSecretProvider()
        with pytest.raises(SecretsError, match="not found"):
            asyncio.get_event_loop().run_until_complete(provider.get_secret("NONEXISTENT_SECRET_XYZ_999"))

    def test_get_secret_or_default_exists(self, monkeypatch):
        monkeypatch.setenv("TEST_SECRET_002", "val")
        provider = EnvSecretProvider()
        result = asyncio.get_event_loop().run_until_complete(
            provider.get_secret_or_default("TEST_SECRET_002", "fallback")
        )
        assert result == "val"

    def test_get_secret_or_default_missing(self):
        provider = EnvSecretProvider()
        result = asyncio.get_event_loop().run_until_complete(
            provider.get_secret_or_default("NONEXISTENT_999", "fallback")
        )
        assert result == "fallback"

    def test_implements_protocol(self):
        provider = EnvSecretProvider()
        assert isinstance(provider, SecretProvider)


class TestDotEnvSecretProvider:
    @pytest.mark.asyncio
    async def test_reads_from_env_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("MY_KEY=hello_world\n", encoding="utf-8")
        provider = DotEnvSecretProvider(env_file)
        result = await provider.get_secret("MY_KEY")
        assert result == "hello_world"

    @pytest.mark.asyncio
    async def test_env_overrides_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MY_KEY", "from_env")
        env_file = tmp_path / ".env"
        env_file.write_text("MY_KEY=from_file\n", encoding="utf-8")
        provider = DotEnvSecretProvider(env_file)
        result = await provider.get_secret("MY_KEY")
        assert result == "from_env"

    @pytest.mark.asyncio
    async def test_missing_key_raises(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("OTHER_KEY=val\n", encoding="utf-8")
        provider = DotEnvSecretProvider(env_file)
        with pytest.raises(SecretsError, match="not found"):
            await provider.get_secret("MISSING_KEY")

    @pytest.mark.asyncio
    async def test_missing_env_file(self, tmp_path):
        provider = DotEnvSecretProvider(tmp_path / "nonexistent.env")
        with pytest.raises(SecretsError):
            await provider.get_secret("ANY_KEY")

    @pytest.mark.asyncio
    async def test_quoted_values(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('QUOTED="value with spaces"\n', encoding="utf-8")
        provider = DotEnvSecretProvider(env_file)
        result = await provider.get_secret("QUOTED")
        assert result == "value with spaces"

    @pytest.mark.asyncio
    async def test_comment_lines_ignored(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("# COMMENT=val\nREAL_KEY=real\n", encoding="utf-8")
        provider = DotEnvSecretProvider(env_file)
        result = await provider.get_secret("REAL_KEY")
        assert result == "real"

    @pytest.mark.asyncio
    async def test_get_secret_or_default(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("", encoding="utf-8")
        provider = DotEnvSecretProvider(env_file)
        result = await provider.get_secret_or_default("MISSING", "default_val")
        assert result == "default_val"

    def test_implements_protocol(self, tmp_path):
        provider = DotEnvSecretProvider(tmp_path / ".env")
        assert isinstance(provider, SecretProvider)


class TestSecretsError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = SecretsError("secret not found", details={"key": "X"})
        assert isinstance(err, ZephyrBaseError)
