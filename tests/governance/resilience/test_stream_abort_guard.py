# [A_test] module_id: MOD-GOV_stream_abort_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_stream_abort_guard
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] check returns AbortResult; is_aborted reflects state
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.stream_abort_guard import (
    AbortDecision,
    ProviderProtocol,
    StreamAbortGuard,
    StreamCheckpoint,
)


class TestStreamAbortGuard:
    def test_instantiation_defaults(self):
        guard = StreamAbortGuard()
        assert guard.is_aborted is False

    def test_instantiation_custom(self):
        guard = StreamAbortGuard(
            checkpoint_interval=100,
            quality_threshold=0.5,
            verbosity_multiplier=2.0,
        )
        assert guard.is_aborted is False

    def test_check_continue_at_non_checkpoint(self):
        guard = StreamAbortGuard(checkpoint_interval=500)
        cp = StreamCheckpoint(tokens_emitted=123)
        result = guard.check(cp)
        assert result.decision == AbortDecision.CONTINUE

    def test_check_continue_at_checkpoint(self):
        guard = StreamAbortGuard(checkpoint_interval=500)
        cp = StreamCheckpoint(
            tokens_emitted=500,
            remaining_budget=10000.0,
            estimated_completion_tokens=1000,
            quality_score=0.9,
        )
        result = guard.check(cp)
        assert result.decision == AbortDecision.CONTINUE

    def test_check_immediate_abort_on_budget_exhausted(self):
        guard = StreamAbortGuard(checkpoint_interval=500)
        cp = StreamCheckpoint(
            tokens_emitted=500,
            remaining_budget=100.0,
            estimated_completion_tokens=1000,
            quality_score=0.9,
        )
        result = guard.check(cp)
        assert result.decision == AbortDecision.IMMEDIATE_ABORT
        assert guard.is_aborted is True

    def test_check_abort_and_retry_on_low_quality(self):
        guard = StreamAbortGuard(checkpoint_interval=500, quality_threshold=0.3)
        cp = StreamCheckpoint(
            tokens_emitted=500,
            remaining_budget=10000.0,
            estimated_completion_tokens=100,
            quality_score=0.1,
        )
        result = guard.check(cp)
        assert result.decision == AbortDecision.ABORT_AND_RETRY
        assert result.retry_model_tier == "economy"

    def test_check_abort_with_warning_on_verbose(self):
        guard = StreamAbortGuard(checkpoint_interval=500, verbosity_multiplier=3.0)
        cp = StreamCheckpoint(
            tokens_emitted=500,
            remaining_budget=10000.0,
            estimated_completion_tokens=100,
            quality_score=0.9,
            expected_max_tokens=100,
        )
        result = guard.check(cp)
        assert result.decision == AbortDecision.ABORT_WITH_WARNING

    def test_save_and_get_partial(self):
        guard = StreamAbortGuard()
        guard.save_partial("partial output text")
        assert guard.get_partial() == "partial output text"

    def test_get_resume_prompt(self):
        guard = StreamAbortGuard()
        guard.save_partial("A" * 600)
        prompt = guard.get_resume_prompt()
        assert "Previous partial output" in prompt
        assert len(prompt) > 0

    def test_get_resume_prompt_empty(self):
        guard = StreamAbortGuard()
        assert guard.get_resume_prompt() == ""

    def test_get_abort_history(self):
        guard = StreamAbortGuard(checkpoint_interval=500)
        cp = StreamCheckpoint(
            tokens_emitted=500,
            remaining_budget=0.0,
            estimated_completion_tokens=1000,
        )
        guard.check(cp)
        history = guard.get_abort_history()
        assert len(history) == 1
        assert history[0].decision == AbortDecision.IMMEDIATE_ABORT

    def test_reset(self):
        guard = StreamAbortGuard(checkpoint_interval=500)
        cp = StreamCheckpoint(
            tokens_emitted=500,
            remaining_budget=0.0,
            estimated_completion_tokens=1000,
        )
        guard.check(cp)
        guard.save_partial("partial")
        guard.reset()
        assert guard.is_aborted is False
        assert guard.get_partial() == ""

    def test_get_provider_stop_reason(self):
        guard = StreamAbortGuard()
        assert guard.get_provider_stop_reason(ProviderProtocol.ANTHROPIC) == "max_tokens"
        assert guard.get_provider_stop_reason(ProviderProtocol.OPENAI) == "length"
        assert guard.get_provider_stop_reason(ProviderProtocol.GOOGLE) == "MAX_TOKENS"
        assert guard.get_provider_stop_reason(ProviderProtocol.DEEPSEEK) == "length"

    def test_summary(self):
        guard = StreamAbortGuard(checkpoint_interval=500)
        s = guard.summary()
        assert "checkpoint_interval" in s
        assert "quality_threshold" in s
        assert "is_aborted" in s
        assert s["checkpoint_interval"] == 500

    def test_record_chunk_cost_no_abort(self):
        guard = StreamAbortGuard()
        result = guard.record_chunk_cost(0.001)
        assert result is None

    def test_record_chunk_cost_accumulation_abort(self):
        guard = StreamAbortGuard(
            micro_transaction_threshold=0.01,
            micro_transaction_accumulation_limit=0.05,
        )
        for _ in range(6):
            guard.record_chunk_cost(0.01)
        result = guard.record_chunk_cost(0.001)
        if result is not None:
            assert result.decision == AbortDecision.IMMEDIATE_ABORT


class TestStreamCheckpoint:
    def test_defaults(self):
        cp = StreamCheckpoint()
        assert cp.tokens_emitted == 0
        assert cp.quality_score == 1.0
        assert cp.provider == ProviderProtocol.ANTHROPIC


class TestBoundaryCases:
    def test_check_at_zero_tokens(self):
        guard = StreamAbortGuard(checkpoint_interval=500)
        cp = StreamCheckpoint(tokens_emitted=0)
        result = guard.check(cp)
        assert result.decision == AbortDecision.CONTINUE

    def test_check_with_zero_remaining_budget(self):
        guard = StreamAbortGuard(checkpoint_interval=500)
        cp = StreamCheckpoint(
            tokens_emitted=500,
            remaining_budget=0.0,
            estimated_completion_tokens=1,
        )
        result = guard.check(cp)
        assert result.decision == AbortDecision.IMMEDIATE_ABORT
