# [A_test] module_id: SRC-TST-0635 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_credential_guard
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_credential_guard.py -q
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.credential_guard import CredentialGuard


class TestCredentialGuardInstantiation:
    def test_creates_instance_without_args(self):
        guard = CredentialGuard()
        assert isinstance(guard, CredentialGuard)

    def test_multiple_instances_are_independent(self):
        g1 = CredentialGuard()
        g2 = CredentialGuard()
        assert g1 is not g2


class TestScanLine:
    def test_detects_openai_key(self):
        guard = CredentialGuard()
        line = 'export API_KEY="sk-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789"'
        result = guard.scan_line(line)
        assert len(result) >= 1
        assert any("sk-" in r for r in result)

    def test_detects_aws_key(self):
        guard = CredentialGuard()
        line = "aws_access_key_id=AKIAIOSFODNN7EXAMPLE"
        result = guard.scan_line(line)
        assert len(result) >= 1
        assert any("AKIA" in r for r in result)

    def test_detects_jwt_token(self):
        guard = CredentialGuard()
        line = 'token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc"'
        result = guard.scan_line(line)
        assert len(result) >= 1
        assert any("eyJ" in r for r in result)

    def test_detects_api_key_assignment(self):
        guard = CredentialGuard()
        line = 'api_key = "supersecretvalue123"'
        result = guard.scan_line(line)
        assert len(result) >= 1

    def test_no_match_on_clean_line(self):
        guard = CredentialGuard()
        result = guard.scan_line("print('hello world')")
        assert result == []

    def test_empty_string_returns_empty(self):
        guard = CredentialGuard()
        result = guard.scan_line("")
        assert result == []

    def test_short_value_below_threshold_not_matched(self):
        guard = CredentialGuard()
        line = 'api_key = "short"'
        result = guard.scan_line(line)
        assert result == []

    def test_multiple_patterns_in_one_line(self):
        guard = CredentialGuard()
        line = "sk-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789 and AKIAIOSFODNN7EXAMPLE"
        result = guard.scan_line(line)
        assert len(result) >= 2


class TestSanitize:
    def test_redacts_openai_key(self):
        guard = CredentialGuard()
        line = "key=sk-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789"
        result = guard.sanitize(line)
        assert "sk-" not in result
        assert "***REDACTED***" in result

    def test_redacts_aws_key(self):
        guard = CredentialGuard()
        line = "AKIAIOSFODNN7EXAMPLE"
        result = guard.sanitize(line)
        assert "AKIA" not in result
        assert "***REDACTED***" in result

    def test_clean_line_unchanged(self):
        guard = CredentialGuard()
        line = "print('hello world')"
        assert guard.sanitize(line) == line

    def test_empty_string_unchanged(self):
        guard = CredentialGuard()
        assert guard.sanitize("") == ""

    def test_multiple_redactions_in_one_line(self):
        guard = CredentialGuard()
        line = "sk-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789 AKIAIOSFODNN7EXAMPLE"
        result = guard.sanitize(line)
        assert "sk-" not in result
        assert "AKIA" not in result
        assert result.count("***REDACTED***") >= 2


class TestCheckEnvironment:
    def test_detects_key_in_env(self):
        guard = CredentialGuard()
        env = {"MY_API_KEY": "a_very_long_secret_value_here"}
        result = guard.check_environment(env)
        assert "MY_API_KEY" in result

    def test_detects_secret_in_env(self):
        guard = CredentialGuard()
        env = {"DB_SECRET": "longsecretvalue1234567890"}
        result = guard.check_environment(env)
        assert "DB_SECRET" in result

    def test_detects_token_in_env(self):
        guard = CredentialGuard()
        env = {"AUTH_TOKEN": "longtokenvalue1234567890"}
        result = guard.check_environment(env)
        assert "AUTH_TOKEN" in result

    def test_detects_password_in_env(self):
        guard = CredentialGuard()
        env = {"USER_PASSWORD": "longpasswordvalue1234567890"}
        result = guard.check_environment(env)
        assert "USER_PASSWORD" in result

    def test_short_value_not_flagged(self):
        guard = CredentialGuard()
        env = {"MY_KEY": "short"}
        result = guard.check_environment(env)
        assert "MY_KEY" not in result

    def test_safe_env_vars_not_flagged(self):
        guard = CredentialGuard()
        env = {"PATH": "/usr/bin", "HOME": "/home/user"}
        result = guard.check_environment(env)
        assert result == []

    def test_empty_dict_returns_empty(self):
        guard = CredentialGuard()
        assert guard.check_environment({}) == []

    def test_case_insensitive_key_matching(self):
        guard = CredentialGuard()
        env = {"MY_SECRET": "longvalue1234567890", "my_KEY": "longvalue1234567890"}
        result = guard.check_environment(env)
        assert len(result) == 2

    def test_boundary_value_length_exactly_eight(self):
        guard = CredentialGuard()
        env = {"MY_KEY": "12345678"}
        result = guard.check_environment(env)
        assert "MY_KEY" not in result

    def test_boundary_value_length_nine(self):
        guard = CredentialGuard()
        env = {"MY_KEY": "123456789"}
        result = guard.check_environment(env)
        assert "MY_KEY" in result
