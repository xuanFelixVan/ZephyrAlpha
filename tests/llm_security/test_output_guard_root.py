# [A_test] module_id: SRC-TST-1349 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.output_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")


from zephyr.security.access_control.guards.output_guard import (
    CREDENTIAL_PATTERNS,
    MAX_OUTPUT_SIZE,
    PII_PATTERNS,
    OutputDecision,
    OutputGuard,
    OutputResult,
)


class TestOutputDecision:
    def test_enum_values(self):
        assert OutputDecision.CLEAN.value == "CLEAN"
        assert OutputDecision.SANITIZED.value == "SANITIZED"
        assert OutputDecision.TRUNCATED.value == "TRUNCATED"
        assert OutputDecision.BLOCKED.value == "BLOCKED"

    def test_enum_members(self):
        members = list(OutputDecision)
        assert len(members) == 4


class TestPIIPatterns:
    def test_not_empty(self):
        assert len(PII_PATTERNS) > 0

    def test_each_pattern_is_tuple(self):
        for pattern, label, desc in PII_PATTERNS:
            assert isinstance(pattern, str)
            assert isinstance(label, str)
            assert isinstance(desc, str)
            assert pattern
            assert label


class TestCredentialPatterns:
    def test_not_empty(self):
        assert len(CREDENTIAL_PATTERNS) > 0

    def test_each_pattern_is_tuple(self):
        for pattern, desc in CREDENTIAL_PATTERNS:
            assert isinstance(pattern, str)
            assert isinstance(desc, str)
            assert pattern


class TestMaxOutputSize:
    def test_value(self):
        assert MAX_OUTPUT_SIZE == 1024 * 1024


class TestOutputResult:
    def test_defaults(self):
        result = OutputResult()
        assert result.decision == OutputDecision.CLEAN
        assert result.sanitized_content == ""
        assert result.findings == []
        assert result.truncated_original_size == 0

    def test_custom_values(self):
        result = OutputResult(
            decision=OutputDecision.SANITIZED,
            sanitized_content="masked",
            findings=["PII detected"],
            truncated_original_size=0,
        )
        assert result.decision == OutputDecision.SANITIZED
        assert result.sanitized_content == "masked"
        assert len(result.findings) == 1


class TestOutputGuard:
    def test_init(self):
        guard = OutputGuard()
        assert guard._read_sources == {}

    def test_check_clean_content(self):
        guard = OutputGuard()
        result = guard.check("Hello, this is a normal message.")
        assert result.decision == OutputDecision.CLEAN
        assert result.sanitized_content == "Hello, this is a normal message."
        assert result.findings == []

    def test_check_empty_content(self):
        guard = OutputGuard()
        result = guard.check("")
        assert result.decision == OutputDecision.CLEAN
        assert result.sanitized_content == ""

    def test_check_phone_number_sanitized(self):
        guard = OutputGuard()
        result = guard.check("Contact: 13812345678")
        assert result.decision == OutputDecision.SANITIZED
        assert "13812345678" not in result.sanitized_content
        assert "[PHONE_CN]" in result.sanitized_content
        assert any("PHONE_CN" in f for f in result.findings)

    def test_check_email_sanitized(self):
        guard = OutputGuard()
        result = guard.check("Email: user@example.com")
        assert result.decision == OutputDecision.SANITIZED
        assert "user@example.com" not in result.sanitized_content
        assert "[EMAIL]" in result.sanitized_content
        assert any("EMAIL" in f for f in result.findings)

    def test_check_chinese_id_sanitized(self):
        guard = OutputGuard()
        result = guard.check("ID: 110101199001011234")
        assert result.decision == OutputDecision.SANITIZED
        assert "110101199001011234" not in result.sanitized_content
        assert any("ID_CN" in f for f in result.findings)

    def test_check_openai_key_sanitized(self):
        guard = OutputGuard()
        key = "sk-" + "A" * 32
        result = guard.check(f"Key: {key}")
        assert result.decision == OutputDecision.SANITIZED
        assert key not in result.sanitized_content
        assert "[CREDENTIAL_MASKED]" in result.sanitized_content
        assert any("OpenAI" in f for f in result.findings)

    def test_check_aws_key_sanitized(self):
        guard = OutputGuard()
        key = "AKIA" + "A" * 16
        result = guard.check(f"Key: {key}")
        assert result.decision == OutputDecision.SANITIZED
        assert key not in result.sanitized_content

    def test_check_github_token_sanitized(self):
        guard = OutputGuard()
        token = "ghp_" + "A" * 36
        result = guard.check(f"Token: {token}")
        assert result.decision == OutputDecision.SANITIZED
        assert token not in result.sanitized_content

    def test_check_truncation(self):
        guard = OutputGuard()
        large_content = "A" * (MAX_OUTPUT_SIZE + 1000)
        result = guard.check(large_content)
        assert result.decision in (OutputDecision.TRUNCATED,)
        assert result.truncated_original_size > MAX_OUTPUT_SIZE
        assert "[SIZE_TRUNCATED]" in result.sanitized_content

    def test_check_multiple_pii_types(self):
        guard = OutputGuard()
        content = "Phone: 13812345678, Email: user@example.com"
        result = guard.check(content)
        assert result.decision == OutputDecision.SANITIZED
        assert len(result.findings) >= 2

    def test_record_read(self):
        guard = OutputGuard()
        guard.record_read("agent-1", "source-a")
        guard.record_read("agent-1", "source-b")
        assert len(guard._read_sources["agent-1"]) == 2

    def test_record_read_truncation_at_100(self):
        guard = OutputGuard()
        for i in range(105):
            guard.record_read("agent-1", f"source-{i}")
        assert len(guard._read_sources["agent-1"]) == 100

    def test_reset_agent(self):
        guard = OutputGuard()
        guard.record_read("agent-1", "source-a")
        guard.reset_agent("agent-1")
        assert "agent-1" not in guard._read_sources

    def test_reset_agent_nonexistent(self):
        guard = OutputGuard()
        guard.reset_agent("nonexistent-agent")

    def test_synthesis_leakage_detection(self):
        guard = OutputGuard()
        guard.record_read("agent-1", "source-a")
        guard.record_read("agent-1", "source-b")
        guard.record_read("agent-1", "source-c")
        result = guard.check("Some output", agent_id="agent-1")
        assert any("Synthesis" in f for f in result.findings)

    def test_no_synthesis_leakage_below_threshold(self):
        guard = OutputGuard()
        guard.record_read("agent-1", "source-a")
        guard.record_read("agent-1", "source-b")
        result = guard.check("Some output", agent_id="agent-1")
        assert not any("Synthesis" in f for f in result.findings)

    def test_check_with_agent_id_no_reads(self):
        guard = OutputGuard()
        result = guard.check("Normal output", agent_id="agent-1")
        assert result.decision == OutputDecision.CLEAN

    def test_check_pii_and_credential_combined(self):
        guard = OutputGuard()
        key = "sk-" + "B" * 32
        content = f"Phone: 13987654321, Key: {key}"
        result = guard.check(content)
        assert result.decision == OutputDecision.SANITIZED
        assert len(result.findings) >= 2

    def test_check_unicode_content(self):
        guard = OutputGuard()
        result = guard.check("这是中文内容，没有敏感信息")
        assert result.decision == OutputDecision.CLEAN

    def test_check_none_like_content(self):
        guard = OutputGuard()
        result = guard.check("None")
        assert result.decision == OutputDecision.CLEAN

    def test_check_jwt_token(self):
        guard = OutputGuard()
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = guard.check(f"Token: {jwt}")
        assert result.decision == OutputDecision.SANITIZED
        assert "[CREDENTIAL_MASKED]" in result.sanitized_content

    def test_check_google_api_key(self):
        guard = OutputGuard()
        key = "AIza" + "A" * 35
        result = guard.check(f"Key: {key}")
        assert result.decision == OutputDecision.SANITIZED

    def test_truncation_with_pii(self):
        guard = OutputGuard()
        phone = "13812345678"
        large_content = phone + " " + "B" * MAX_OUTPUT_SIZE
        result = guard.check(large_content)
        assert result.decision == OutputDecision.SANITIZED
        assert any("PHONE_CN" in f for f in result.findings)
        assert any("truncated" in f.lower() for f in result.findings)
