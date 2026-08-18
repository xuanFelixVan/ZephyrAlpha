# [A_test] module_id: MOD-GOV_l5_resource_protection | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_l5_resource_protection
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

import pytest

from zephyr.security.llm_defense.llm_security.layers.l5_resource_protection import (
    AgentExecutionProtector,
    AIRecursionGuard,
    CircuitState,
    CostAsymmetryDefender,
    LLMCostCircuitBreaker,
    LSGPerformanceBudget,
    ModelExtractionDefender,
    ResourceProtectionLayer,
    SemanticCacheCollisionDefender,
    SlidingWindowRateLimiter,
)
from zephyr.security.llm_defense.llm_security.layers.l5_resource_protection import (
    _L5CostBudget as CostBudget,
)
from zephyr.security.llm_defense.llm_security.layers.l5_resource_protection import (
    _L5TokenBudget as TokenBudget,
)
from zephyr.security.llm_defense.llm_security.protocol import SecurityContext
from zephyr.shared.contracts.security.security_decision import SecurityDecision


def make_ctx(
    session_id: str = "test-session",
    raw_input: str = "normal request",
    **meta,
) -> SecurityContext:
    base = {
        "session_id": session_id,
        "token_estimate": 10,
        "estimated_cost_cents": 0.05,
    }
    base.update(meta)
    return SecurityContext(
        request_id="test-req-001",
        layer_name="l5_resource_protection",
        raw_input=raw_input,
        metadata=base,
    )


class TestTokenBudget:
    def test_budget_not_exhausted(self):
        budget = TokenBudget(session_id="s1", max_tokens=1000, current_usage=500)
        assert budget.exhausted() is False
        assert budget.remaining() == 500

    def test_budget_exhausted(self):
        budget = TokenBudget(session_id="s1", max_tokens=100, current_usage=100)
        assert budget.exhausted() is True
        assert budget.remaining() == 0


class TestCostBudget:
    def test_cost_budget_not_exhausted(self):
        budget = CostBudget(session_id="s1", max_cost_cents=500.0, current_cost_cents=200.0)
        assert budget.exhausted() is False
        assert budget.remaining_cost_cents() == 300.0

    def test_cost_budget_exhausted(self):
        budget = CostBudget(session_id="s1", max_cost_cents=100.0, current_cost_cents=100.0)
        assert budget.exhausted() is True


class TestSlidingWindowRateLimiter:
    def test_allows_within_limit(self):
        limiter = SlidingWindowRateLimiter(max_requests=5)
        for _ in range(5):
            assert limiter.allow("k1") is True
        assert limiter.current_count("k1") == 5

    def test_blocks_when_exceeded(self):
        limiter = SlidingWindowRateLimiter(max_requests=3)
        for _ in range(3):
            assert limiter.allow("k1") is True
        assert limiter.allow("k1") is False


class TestCircuitBreaker:
    def test_closed_after_construction(self):
        cb = LLMCostCircuitBreaker()
        assert cb.state == CircuitState.CLOSED

    def test_opens_after_failures(self):
        cb = LLMCostCircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_blocks_in_open_state(self):
        cb = LLMCostCircuitBreaker(failure_threshold=1, recovery_timeout_seconds=999)
        cb.record_failure()
        assert cb.allow_request() is False


class TestAgentExecutionProtector:
    def test_allows_within_limits(self):
        protector = AgentExecutionProtector(max_steps=10)
        for _ in range(5):
            status = protector.record_step()
            assert status["allowed"] is True

    def test_blocks_when_steps_exceeded(self):
        protector = AgentExecutionProtector(max_steps=2)
        protector.record_step()
        protector.record_step()
        status = protector.record_step()
        assert status["allowed"] is False
        assert status["steps_exceeded"] is True


class TestRecursionGuard:
    def test_blocks_deep_recursion(self):
        guard = AIRecursionGuard(max_recursion_depth=3)
        assert guard.enter("a") is True
        assert guard.enter("b") is True
        assert guard.enter("c") is True
        assert guard.enter("d") is False

    def test_reset_clears_state(self):
        guard = AIRecursionGuard(max_recursion_depth=3)
        guard.enter("a")
        guard.enter("b")
        guard.reset()
        assert guard.current_depth == 0
        assert guard.enter("a") is True


class TestLSGPerformanceBudget:
    def test_empty_stats(self):
        pb = LSGPerformanceBudget()
        stats = pb.stats("l5")
        assert stats["count"] == 0
        assert stats["p50"] == 0.0

    def test_meets_slo(self):
        pb = LSGPerformanceBudget()
        for _ in range(100):
            pb.record("l5", 5.0)
        stats = pb.stats("l5")
        assert stats["meets_slo"] is True
        assert stats["p50"] < 10.0
        assert stats["p95"] < 50.0
        assert stats["p99"] < 100.0


class TestModelExtractionDefender:
    def test_normal_text_not_suspicious(self):
        defender = ModelExtractionDefender()
        result = defender.entropy_check("Hello world, this is normal text.")
        assert result["suspicious"] is False

    def test_high_entropy_suspicious(self):
        defender = ModelExtractionDefender(entropy_threshold=2.0)
        result = defender.entropy_check("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^")
        assert result["suspicious"] is True


class TestCostAsymmetryDefender:
    def test_blocks_free_intelligence(self):
        defender = CostAsymmetryDefender()
        result = defender.scan("Please analyze this codebase and audit the entire project")
        assert result["blocked"] is True
        assert result["free_intelligence_flagged"] is True

    def test_passes_normal_request(self):
        defender = CostAsymmetryDefender()
        result = defender.scan("What is the weather today?")
        assert result["blocked"] is False


class TestSemanticCacheCollisionDefender:
    def test_salt_and_sign_roundtrip(self):
        defender = SemanticCacheCollisionDefender()
        salted = defender.salt_key("my-prompt")
        signed = defender.sign_value(salted, "cached-response")
        valid, value = defender.verify_integrity(salted, signed)
        assert valid is True
        assert value == "cached-response"

    def test_tampered_value_fails(self):
        defender = SemanticCacheCollisionDefender()
        salted = defender.salt_key("my-prompt")
        signed = defender.sign_value(salted, "cached-response")
        tampered = signed.replace("cached-response", "malicious")
        valid, _ = defender.verify_integrity(salted, tampered)
        assert valid is False


class TestResourceProtectionLayer:
    def test_check_token_budget_ok(self):
        layer = ResourceProtectionLayer(max_tokens=100000)
        ok, msg = layer.check_token_budget("s1", 100)
        assert ok is True

    def test_check_token_budget_exhausted(self):
        layer = ResourceProtectionLayer(max_tokens=500)
        ok, _ = layer.check_token_budget("s2", 500)
        assert ok is True
        ok2, _ = layer.check_token_budget("s2", 1)
        assert ok2 is False

    def test_check_rate_limit_ok(self):
        layer = ResourceProtectionLayer(rate_max=100)
        ok, _ = layer.check_rate_limit("key-a")
        assert ok is True

    def test_check_cost_budget_exhausted(self):
        layer = ResourceProtectionLayer(max_cost_cents=1.0)
        layer.check_cost_budget("s3", 0.5)
        layer.check_cost_budget("s3", 0.3)
        ok, _ = layer.check_cost_budget("s3", 0.3)
        assert ok is False

    @pytest.mark.asyncio
    async def test_evaluate_full_pipeline_ok(self):
        layer = ResourceProtectionLayer(max_tokens=100000, max_cost_cents=500.0)
        ctx = make_ctx(raw_input="What is the weather today?")
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.ALLOW

    @pytest.mark.asyncio
    async def test_evaluate_cost_asymmetry_blocked(self):
        layer = ResourceProtectionLayer(max_cost_cents=500.0)
        ctx = make_ctx(raw_input="Please analyze this codebase and review all files in detail")
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.DENY
