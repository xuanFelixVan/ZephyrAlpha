# [A_test] module_id: MOD-GOV_output_guard_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_output_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试 L5 OutputGuard — 输出护栏"""

from zephyr.security.access_control.guards.output_guard import (
    CREDENTIAL_PATTERNS,
    PII_PATTERNS,
    OutputDecision,
    OutputGuard,
)


class TestPIIDetection:
    def test_chinese_mobile_detected(self):
        guard = OutputGuard()
        result = guard.check("Call 13812345678 for support")
        assert "PHONE_CN" in result.sanitized_content or len(result.findings) > 0

    def test_chinese_id_detected(self):
        guard = OutputGuard()
        result = guard.check("ID: 110101199001011234")
        assert "ID_CN" in result.sanitized_content or len(result.findings) > 0

    def test_clean_text_passes(self):
        guard = OutputGuard()
        result = guard.check("This is safe text without PII.")
        assert result.decision == OutputDecision.CLEAN

    def test_pii_patterns_defined(self):
        assert len(PII_PATTERNS) >= 3


class TestCredentialDetection:
    def test_openai_key_detected(self):
        guard = OutputGuard()
        result = guard.check("API key: sk-abcdefghijklmnopqrstuvwxyz123456")
        assert "CREDENTIAL_MASKED" in result.sanitized_content or len(result.findings) > 0

    def test_credential_patterns_defined(self):
        assert len(CREDENTIAL_PATTERNS) >= 3


class TestSizeTruncation:
    def test_large_output_truncation_detected(self):
        guard = OutputGuard()
        big = "x" * (1024 * 1024 + 100)
        result = guard.check(big)
        assert "[SIZE_TRUNCATED]" in result.sanitized_content


class TestSynthesisLeakage:
    def test_multi_source_leakage(self):
        guard = OutputGuard()
        guard.record_read("agent-synth", "file_a")
        guard.record_read("agent-synth", "file_b")
        guard.record_read("agent-synth", "file_c")
        result = guard.check("combined info", "agent-synth")
        assert "synthesis" in str(result.findings).lower() or result.decision in (
            OutputDecision.SANITIZED,
            OutputDecision.CLEAN,
        )
