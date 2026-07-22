# [A_test] module_id: MOD-GOV_secrets | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_secrets
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

from zephyr.security.llm_defense.llm_security.patterns.secrets import (
    PRECOMPILED_SECRET_PATTERNS,
    scan_secrets,
)


class TestScanSecrets:
    def test_openai_api_key_detected(self):
        hits = scan_secrets("sk-1234567890abcdef1234567890abcdef1234567890abcdef1234")
        assert len(hits) > 0
        assert any(h["name"] == "openai_api_key" for h in hits)

    def test_aws_access_key_detected(self):
        hits = scan_secrets("AKIAIOSFODNN7EXAMPLE")
        assert len(hits) > 0
        assert any(h["name"] == "aws_access_key" for h in hits)

    def test_github_token_detected(self):
        hits = scan_secrets("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij")
        assert len(hits) > 0

    def test_private_key_detected(self):
        hits = scan_secrets("-----BEGIN RSA PRIVATE KEY-----")
        assert len(hits) > 0

    def test_password_inline_detected(self):
        hits = scan_secrets("password=supersecret123")
        assert len(hits) > 0

    def test_bearer_token_detected(self):
        hits = scan_secrets(
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        )
        assert len(hits) > 0

    def test_jwt_token_detected(self):
        hits = scan_secrets(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        )
        jwt_hits = [h for h in hits if h["name"] == "jwt_token"]
        assert len(jwt_hits) > 0

    def test_credit_card_detected(self):
        hits = scan_secrets("4111111111111111")
        cc = [h for h in hits if h["name"] == "credit_card"]
        assert len(cc) > 0

    def test_benign_text_no_hits(self):
        hits = scan_secrets("The weather is sunny today.")
        assert len(hits) == 0

    def test_database_url_detected(self):
        hits = scan_secrets("postgres://user:password@localhost:5432/mydb")
        assert len(hits) > 0

    def test_email_detected(self):
        hits = scan_secrets("user@example.com")
        email = [h for h in hits if h["name"] == "email_address"]
        assert len(email) > 0

    def test_ssn_detected(self):
        hits = scan_secrets("123-45-6789")
        ssn = [h for h in hits if h["name"] == "ssn"]
        assert len(ssn) > 0

    def test_credential_action_is_block(self):
        hits = scan_secrets("sk-1234567890abcdef1234567890abcdef1234567890abcdef1234")
        api_key_hits = [h for h in hits if h["name"] == "openai_api_key"]
        assert len(api_key_hits) > 0
        assert api_key_hits[0]["action"] == "block"

    def test_severity_levels(self):
        hits = scan_secrets("sk-1234567890abcdef1234567890abcdef1234567890abcdef1234")
        severities = {h["severity"] for h in hits}
        assert "critical" in severities


class TestPrecompiledPatterns:
    def test_patterns_compiled(self):
        assert len(PRECOMPILED_SECRET_PATTERNS) > 0

    def test_pattern_tuple_structure(self):
        for name, pattern, action, severity in PRECOMPILED_SECRET_PATTERNS:
            assert isinstance(name, str)
            assert isinstance(action, str)
            assert isinstance(severity, str)
