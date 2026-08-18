# [A_test] module_id: MOD-GOV_l3_output_security | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_l3_output_security
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import pytest

from zephyr.security.llm_defense.llm_security.layers.l3_output import (
    AgentPublicInteractionGuard,
    AIGeneratedCodeTrustBoundary,
    OutputSecurityLayer,
)
from zephyr.security.llm_defense.llm_security.protocol import SecurityContext
from zephyr.shared.contracts.security.security_decision import SecurityDecision


class TestOutputSecurityLayer:
    @pytest.fixture
    def layer(self):
        return OutputSecurityLayer()

    def test_validate_schema_valid(self, layer):
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            name: str
            count: int

        result = layer.validate_schema({"name": "test", "count": 5}, TestSchema)
        assert result.valid is True

    def test_validate_schema_invalid(self, layer):
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            name: str

        result = layer.validate_schema({"name": 123}, TestSchema)
        assert result.valid is False
        assert len(result.errors) > 0

    def test_sandbox_execution_safe_code(self, layer):
        result = layer.sandbox_execution("print('hello')")
        assert result.safe is True
        assert "hello" in result.output

    def test_sandbox_execution_blocked(self, layer):
        result = layer.sandbox_execution("import os; os.system('ls')")
        assert result.safe is False
        assert "Blocked keyword" in result.blocked_reason

    def test_redact_sensitive_data_api_key(self, layer):
        content = "Here is my key: sk-abcdefghijklmnopqrstuvwxyz123456789012345678"
        result = layer.redact_sensitive_data(content)
        assert result.redactions > 0
        assert "sk-abc" not in result.clean_text or "[BLOCKED]" in result.clean_text

    def test_redact_sensitive_data_email(self, layer):
        content = "Contact me at john.doe@example.com for details"
        result = layer.redact_sensitive_data(content)
        assert result.redactions > 0
        assert "***" in result.clean_text or "[REDACTED]" in result.clean_text

    def test_redact_no_secrets(self, layer):
        content = "The weather is sunny today."
        result = layer.redact_sensitive_data(content)
        assert result.redactions == 0
        assert result.clean_text == content

    def test_detect_hallucination_clean(self, layer):
        result = layer.detect_hallucination("Paris is the capital of France.")
        assert result.is_hallucination is False
        assert result.confidence < 0.5

    def test_detect_hallucination_certainty(self, layer):
        result = layer.detect_hallucination("I am certain that the answer is 42 and there is no way it could be wrong.")
        assert result.confidence > 0.0

    def test_check_content_safety_clean(self, layer):
        result = layer.check_content_safety("How to bake a chocolate cake")
        assert result.safe is True
        assert len(result.violations) == 0

    def test_check_content_safety_toxic(self, layer):
        result = layer.check_content_safety("How to make a bomb at home")
        assert result.safe is False
        assert len(result.violations) > 0

    @pytest.mark.asyncio
    async def test_evaluate_clean(self, layer):
        ctx = SecurityContext(request_id="r1", layer_name="l3", raw_input="The capital of France is Paris.")
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.ALLOW

    @pytest.mark.asyncio
    async def test_evaluate_with_secrets(self, layer):
        ctx = SecurityContext(
            request_id="r2",
            layer_name="l3",
            raw_input="API key: sk-abcdefghijklmnopqrstuvwxyz123456789012345678",
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.DENY

    def test_layer_identity(self, layer):
        assert layer.layer_name() == "l3_output"
        assert layer.layer_index() == 3


class TestAIGeneratedCodeTrustBoundary:
    @pytest.fixture
    def auditor(self):
        return AIGeneratedCodeTrustBoundary()

    def test_audit_safe_code(self, auditor):
        code = "def hello():\n    print('hello')\n"
        result = auditor.audit(code)
        assert result["safe"] is True
        assert result["issue_count"] == 0

    def test_audit_dangerous_import(self, auditor):
        code = "import os\nos.system('ls')\n"
        result = auditor.audit(code)
        assert result["safe"] is False
        assert any(i["type"] == "dangerous_import" for i in result["issues"])

    def test_audit_dynamic_execution(self, auditor):
        code = "eval(user_input)\n"
        result = auditor.audit(code)
        assert any(i["type"] == "dynamic_execution" for i in result["issues"])

    def test_audit_file_access(self, auditor):
        code = "with open('/etc/passwd') as f:\n    print(f.read())\n"
        result = auditor.audit(code)
        assert any(i["type"] == "file_system_access" for i in result["issues"])

    def test_audit_credential_handling(self, auditor):
        code = "password = 'secret123'\n"
        result = auditor.audit(code)
        assert any(i["type"] == "credential_handling" for i in result["issues"])

    def test_audit_network_access(self, auditor):
        code = "import socket\ns = socket.socket()\n"
        result = auditor.audit(code)
        assert any(i["type"] == "network_access" for i in result["issues"])


class TestAgentPublicInteractionGuard:
    @pytest.fixture
    def guard(self):
        return AgentPublicInteractionGuard()

    def test_sanitize_for_github(self, guard):
        content = "API key: sk-abc123def456 and email: user@example.com"
        result = guard.sanitize_for_github(content)
        assert "[REDACTED]" in result
        assert "ZephyrAlpha LSG" in result

    def test_sanitize_for_api(self, guard):
        content = "Secret: mypassword123"
        result = guard.sanitize_for_api(content)
        assert "[REDACTED]" in result
