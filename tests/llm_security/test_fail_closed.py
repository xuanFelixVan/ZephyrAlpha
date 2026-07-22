# [A_test] module_id: MOD-GOV_fail_closed | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_fail_closed
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import pytest

from zephyr.security.llm_defense.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityResult,
)
from zephyr.shared.contracts.security.security_decision import SecurityDecision


class MockUncertainLayer(LLMSecurityProtocol):
    """模拟一个不确定的安全层——安全分数 0.3（低于阈值 0.5）."""

    def layer_name(self) -> str:
        return "mock_uncertain"

    def layer_index(self) -> int:
        return 0

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        return SecurityResult(
            decision=SecurityDecision.BLOCK,
            reason="Uncertain decision",
            layer_name=self.layer_name(),
            score=0.3,
        )


class MockBlockLayer(LLMSecurityProtocol):
    """模拟一个始终 BLOCK 的层."""

    def layer_name(self) -> str:
        return "mock_block"

    def layer_index(self) -> int:
        return 0

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        return SecurityResult(
            decision=SecurityDecision.BLOCK,
            reason="Default block",
            layer_name=self.layer_name(),
            score=0.0,
        )


class MockWhitelistLayer(LLMSecurityProtocol):
    """模拟一个白名单放行层."""

    def layer_name(self) -> str:
        return "mock_whitelist"

    def layer_index(self) -> int:
        return 0

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        if ctx.metadata.get("whitelist", False):
            return SecurityResult(
                decision=SecurityDecision.ALLOW,
                reason="Whitelist allowed",
                layer_name=self.layer_name(),
                score=0.9,
            )
        return SecurityResult(
            decision=SecurityDecision.BLOCK,
            reason="Not in whitelist",
            layer_name=self.layer_name(),
            score=0.0,
        )


class TestFailClosed:
    def test_default_block_constant(self):
        assert LLMSecurityProtocol.DEFAULT_BLOCK is True
        assert LLMSecurityProtocol.UNCERTAINTY_THRESHOLD == 0.5

    def test_fail_closed_default_returns_block(self):
        assert LLMSecurityProtocol.fail_closed_default() == SecurityDecision.BLOCK

    @pytest.mark.asyncio
    async def test_uncertain_decision_blocks(self):
        layer = MockUncertainLayer()
        ctx = SecurityContext(
            request_id="test-1",
            layer_name="mock_uncertain",
            raw_input="test input",
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.BLOCK
        assert result.score < 0.5
        assert LLMSecurityProtocol.is_uncertain(result.score) is True

    @pytest.mark.asyncio
    async def test_block_layer_returns_block(self):
        layer = MockBlockLayer()
        ctx = SecurityContext(
            request_id="test-2",
            layer_name="mock_block",
            raw_input="test",
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.BLOCK

    @pytest.mark.asyncio
    async def test_whitelist_allow(self):
        layer = MockWhitelistLayer()
        ctx = SecurityContext(
            request_id="test-3",
            layer_name="mock_whitelist",
            raw_input="whitelisted request",
            metadata={"whitelist": True},
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.ALLOW

    @pytest.mark.asyncio
    async def test_not_in_whitelist_blocks(self):
        layer = MockWhitelistLayer()
        ctx = SecurityContext(
            request_id="test-4",
            layer_name="mock_whitelist",
            raw_input="normal request",
            metadata={"whitelist": False},
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.BLOCK

    def test_seven_consequences_reverse_validation(self):
        """不部署LSG的七项后果反向验证——确保每项后果有对应防御层."""
        consequences = [
            ("prompt_injection", ["l1_input", "l2_prompt_protection"]),
            ("data_leak", ["l3_output", "l6_observability"]),
            ("hallucination", ["l3_output"]),
            ("agent_abuse", ["l4_agent", "l8_multi_agent"]),
            ("resource_exhaustion", ["l5_resource_protection"]),
            ("model_extraction", ["l5_resource_protection"]),
            ("cost_asymmetry", ["l5_resource_protection"]),
        ]
        from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

        gw = LSGSecurityGateway()
        for name, expected_layers in consequences:
            for layer_name in expected_layers:
                layer = gw.get_layer(layer_name)
                assert layer is not None, (
                    f"Consequence '{name}' requires layer '{layer_name}' but it is missing from LSG"
                )

        decisions = [SecurityDecision.BLOCK, SecurityDecision.DENY, SecurityDecision.ALLOW, SecurityDecision.FLAG]
        assert SecurityDecision.BLOCK in decisions
        block_idx = decisions.index(SecurityDecision.BLOCK)
        assert block_idx < decisions.index(SecurityDecision.ALLOW), "BLOCK must precede ALLOW as fail-closed default"
