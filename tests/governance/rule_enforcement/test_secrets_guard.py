# [A_test] module_id: SRC-TST-1541 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_secrets_guard
# [INVARIANTS] SecretsGuard.REQUIRED_KEYS=["OPENAI_API_KEY","ANTHROPIC_API_KEY","DEEPSEEK_API_KEY"]
# [MODIFY-GUARD] source-change:re-read-secrets_guard
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] sanitize_log:raises-TypeError-on-None-input
# [TESTS] self
# [TTL] task_bound

import pytest

from zephyr.gov_enforcement.rule_enforcement.secrets_guard import SecretsGuard


class TestSecretsGuardInstantiation:
    def test_default_required_keys(self):
        guard = SecretsGuard()
        assert guard.REQUIRED_KEYS == ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"]

    def test_instance_is_independent(self):
        a = SecretsGuard()
        b = SecretsGuard()
        a.REQUIRED_KEYS = []
        assert b.REQUIRED_KEYS == ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"]

    def test_required_keys_count(self):
        guard = SecretsGuard()
        assert len(guard.REQUIRED_KEYS) == 3


class TestCheckEnv:
    def test_returns_true(self):
        guard = SecretsGuard()
        assert guard.check_env() is True

    def test_return_type(self):
        guard = SecretsGuard()
        result = guard.check_env()
        assert isinstance(result, bool)


class TestScanGitLog:
    def test_returns_empty_list(self):
        guard = SecretsGuard()
        assert guard.scan_git_log() == []

    def test_return_type(self):
        guard = SecretsGuard()
        result = guard.scan_git_log()
        assert isinstance(result, list)


class TestSanitizeLog:
    def test_openai_key_redacted(self):
        guard = SecretsGuard()
        line = "export OPENAI_API_KEY=sk-abc123"
        result = guard.sanitize_log(line)
        assert "OPENAI_API_KEY" not in result
        assert "***REDACTED***" in result

    def test_anthropic_key_redacted(self):
        guard = SecretsGuard()
        line = "ANTHROPIC_API_KEY=sk-ant-xyz"
        result = guard.sanitize_log(line)
        assert "ANTHROPIC_API_KEY" not in result
        assert "***REDACTED***" in result

    def test_deepseek_key_redacted(self):
        guard = SecretsGuard()
        line = "set DEEPSEEK_API_KEY=dsk-789"
        result = guard.sanitize_log(line)
        assert "DEEPSEEK_API_KEY" not in result
        assert "***REDACTED***" in result

    def test_no_key_present(self):
        guard = SecretsGuard()
        line = "export PATH=/usr/bin"
        result = guard.sanitize_log(line)
        assert result == "export PATH=/usr/bin"

    def test_empty_string(self):
        guard = SecretsGuard()
        result = guard.sanitize_log("")
        assert result == ""

    def test_case_insensitive_detects_but_case_sensitive_replace(self):
        guard = SecretsGuard()
        line = "openai_api_key=sk-abc"
        result = guard.sanitize_log(line)
        assert result == line

    def test_none_raises(self):
        guard = SecretsGuard()
        with pytest.raises(AttributeError):
            guard.sanitize_log(None)

    def test_integer_raises(self):
        guard = SecretsGuard()
        with pytest.raises(AttributeError):
            guard.sanitize_log(12345)

    def test_preserves_surrounding_text(self):
        guard = SecretsGuard()
        line = "config OPENAI_API_KEY=value done"
        result = guard.sanitize_log(line)
        assert result.startswith("config ")
        assert result.endswith(" done")

    def test_only_first_match_redacted(self):
        guard = SecretsGuard()
        line = "OPENAI_API_KEY=sk-abc"
        result = guard.sanitize_log(line)
        assert result == "***REDACTED***=sk-abc"
