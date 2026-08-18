# [A_test] module_id: MOD-GOV_l4_agent_security | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_l4_agent_security
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import pytest

from zephyr.security.llm_defense.llm_security.layers.l4_agent import (
    AgentImpersonationDefender,
    AgentPermission,
    AgentSecurityLayer,
    ApprovalOutcome,
    FinancialComplianceGate,
    LongHorizonAgentDefender,
    RiskLevel,
)
from zephyr.security.llm_defense.llm_security.protocol import SecurityContext
from zephyr.shared.contracts.security.security_decision import SecurityDecision


def make_ctx(
    tool_name: str = "read_file",
    raw_input: str = "safe content",
    **meta,
) -> SecurityContext:
    base = {
        "tool_name": tool_name,
        "tool_params": {},
        "intent": "",
        "objective": "",
        "agent_id": "",
        "session_id": "test-session",
    }
    base.update(meta)
    return SecurityContext(
        request_id="test-req-001",
        layer_name="l4_agent",
        raw_input=raw_input,
        metadata=base,
    )


class TestToolCallAuthorization:
    def test_authorize_known_tool_read(self):
        layer = AgentSecurityLayer()
        auth = layer.authorize_tool_call("read_file", {"session_id": "s1", "tool_params": {}})
        assert auth.granted is True
        assert auth.permission_required == AgentPermission.READ_ONLY
        assert auth.risk == RiskLevel.LOW

    def test_authorize_unknown_tool_denied(self):
        layer = AgentSecurityLayer()
        auth = layer.authorize_tool_call("evil_malware_tool")
        assert auth.granted is False
        assert auth.risk == RiskLevel.HIGH
        assert "Unknown tool" in auth.reason

    def test_authorize_write_critical_denied_with_safe_max(self):
        layer = AgentSecurityLayer(max_permission=AgentPermission.WRITE_SAFE)
        auth = layer.authorize_tool_call("delete_file")
        assert auth.granted is False
        assert auth.permission_required == AgentPermission.WRITE_CRITICAL
        assert "max=write_safe" in auth.reason


class TestValidateToolParams:
    def test_validate_params_clean(self):
        layer = AgentSecurityLayer()
        ok, err = layer.validate_tool_params("read_file", {"path": "/tmp/safe.txt"})
        assert ok is True
        assert err == ""

    def test_validate_params_code_injection(self):
        layer = AgentSecurityLayer()
        ok, err = layer.validate_tool_params("run_command", {"command": "eval(dangerous())"})
        assert ok is False
        assert "code_injection" in err

    def test_validate_params_path_traversal(self):
        layer = AgentSecurityLayer()
        ok, err = layer.validate_tool_params("read_file", {"path": "../../etc/passwd"})
        assert ok is False
        assert "path_traversal" in err

    def test_validate_params_system_command(self):
        layer = AgentSecurityLayer()
        ok, err = layer.validate_tool_params("run_command", {"command": "rm -rf /"})
        assert ok is False
        assert "system_command" in err


class TestRequestHumanApproval:
    def test_low_risk_auto_approved(self):
        layer = AgentSecurityLayer()
        req = layer.request_human_approval("read_file", {}, RiskLevel.LOW, "")
        assert req.outcome == ApprovalOutcome.APPROVED
        assert req.risk == RiskLevel.LOW

    def test_high_risk_stays_pending(self):
        layer = AgentSecurityLayer()
        req = layer.request_human_approval("delete_file", {}, RiskLevel.HIGH, "needs review")
        assert req.outcome == ApprovalOutcome.PENDING
        assert req.risk == RiskLevel.HIGH

    def test_explicit_approve_changes_outcome(self):
        layer = AgentSecurityLayer()
        req = layer.request_human_approval("delete_file", {}, RiskLevel.HIGH, "")
        result = layer.approve_request(req.request_id)
        assert result is not None
        assert result.outcome == ApprovalOutcome.APPROVED

    def test_explicit_deny_changes_outcome(self):
        layer = AgentSecurityLayer()
        req = layer.request_human_approval("delete_file", {}, RiskLevel.HIGH, "")
        result = layer.deny_request(req.request_id)
        assert result is not None
        assert result.outcome == ApprovalOutcome.DENIED


class TestFinancialComplianceGate:
    def test_fj1_insider_trading_blocked(self):
        gate = FinancialComplianceGate()
        result = gate.scan("This is insider non-public material information before earnings")
        assert result["blocked"] is True
        assert result["violations"] >= 1
        assert "insider_trading" in result["findings"]

    def test_financial_clean_passes(self):
        gate = FinancialComplianceGate()
        result = gate.scan("The weather is nice today and stocks are volatile")
        assert result["blocked"] is False
        assert result["violations"] == 0


class TestEvaluateFullPipeline:
    @pytest.mark.asyncio
    async def test_evaluate_read_tool_allowed(self):
        layer = AgentSecurityLayer()
        layer.set_approval_auto_mode(True)
        ctx = make_ctx(tool_name="read_file", raw_input="read docs/foo.md")
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.ALLOW
        assert result.layer_name == "l4_agent"

    @pytest.mark.asyncio
    async def test_evaluate_unknown_tool_denied(self):
        layer = AgentSecurityLayer()
        ctx = make_ctx(tool_name="suspicious_tool", raw_input="anything")
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.DENY
        assert "unknown" in result.reason.lower()


class TestAgentImpersonationDefender:
    def test_marker_generation_and_verification(self):
        defender = AgentImpersonationDefender(secret="test-impersonation-secret")
        marker = defender.generate_unforgeable_marker("agent-42")
        assert marker.startswith("zephyr-ag|agent-42|")
        assert defender.verify_marker(marker, "agent-42") is True

    def test_verify_fake_marker_fails(self):
        defender = AgentImpersonationDefender(secret="test-impersonation-secret")
        assert defender.verify_marker("fake-marker", "agent-42") is False

    def test_verify_wrong_agent_id_fails(self):
        defender = AgentImpersonationDefender(secret="test-impersonation-secret")
        marker = defender.generate_unforgeable_marker("agent-42")
        assert defender.verify_marker(marker, "agent-99") is False


class TestLongHorizonAgentDefender:
    def test_initial_intent_consistent(self):
        defender = LongHorizonAgentDefender()
        result = defender.check_intent_consistency("write unit tests")
        assert result["consistent"] is True
        assert result["drift"] == 0.0
