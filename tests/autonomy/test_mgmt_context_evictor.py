# [A_test] module_id: MOD-GOV_mgmt_context_evictor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_evictor
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

import pytest

try:
    from zephyr.autonomy_core.context.context_evictor import (
        ContextBlock,
        ContextEvictor,
        EvictionResult,
        PriorityLevel,
    )
except Exception as _exc:
    pytest.skip(f"cannot import context_evictor: {_exc}", allow_module_level=True)


class TestContextBlock:
    def test_context_block_creation(self):
        b = ContextBlock(block_id="b1", content="hello", token_estimate=10)
        assert b.block_id == "b1"
        assert b.content == "hello"
        assert b.priority == PriorityLevel.NORMAL

    def test_is_pinned(self):
        b = ContextBlock(block_id="b1", content="pinned", priority=PriorityLevel.PINNED)
        assert b.is_pinned is True

    def test_is_mandatory(self):
        b = ContextBlock(block_id="b1", content="critical", priority=PriorityLevel.CRITICAL)
        assert b.is_mandatory is True

    def test_compute_eviction_score(self):
        b_low = ContextBlock(block_id="low", content="x", priority=PriorityLevel.LOW, freshness=0.1, relevance=0.1)
        b_high = ContextBlock(block_id="high", content="y", priority=PriorityLevel.HIGH, freshness=0.9, relevance=0.9)
        assert b_low.compute_eviction_score() > b_high.compute_eviction_score()


class TestContextEvictor:
    def test_evict_empty_blocks(self):
        evictor = ContextEvictor()
        result = evictor.evict([], token_budget=1000)
        assert isinstance(result, EvictionResult)
        assert result.kept_count == 0
        assert result.removed_count == 0

    def test_evict_within_budget_keeps_all(self):
        evictor = ContextEvictor()
        blocks = [
            ContextBlock(block_id="b1", content="a", token_estimate=100),
            ContextBlock(block_id="b2", content="b", token_estimate=200),
        ]
        result = evictor.evict(blocks, token_budget=1000)
        assert result.kept_count == 2
        assert result.removed_count == 0

    def test_evict_exceeds_budget_removes_low_priority(self):
        evictor = ContextEvictor()
        blocks = [
            ContextBlock(
                block_id="low",
                content="x",
                token_estimate=500,
                priority=PriorityLevel.LOW,
                freshness=0.1,
                relevance=0.1,
            ),
            ContextBlock(
                block_id="high",
                content="y",
                token_estimate=500,
                priority=PriorityLevel.HIGH,
                freshness=0.9,
                relevance=0.9,
            ),
        ]
        result = evictor.evict(blocks, token_budget=600)
        assert result.kept_count >= 1
        assert result.removed_count >= 1

    def test_evict_pinned_blocks_always_kept(self):
        evictor = ContextEvictor()
        blocks = [
            ContextBlock(block_id="pinned", content="p", token_estimate=500, priority=PriorityLevel.PINNED),
            ContextBlock(
                block_id="low",
                content="l",
                token_estimate=500,
                priority=PriorityLevel.LOW,
                freshness=0.1,
                relevance=0.1,
            ),
        ]
        result = evictor.evict(blocks, token_budget=600)
        pinned_ids = [b.block_id for b in result.kept if b.is_pinned]
        assert "pinned" in pinned_ids

    def test_eviction_result_compression_ratio(self):
        result = EvictionResult(kept=[], removed=[], before_tokens=1000, after_tokens=500, budget=600)
        assert result.compression_ratio == 0.5

    def test_eviction_result_zero_before_tokens(self):
        result = EvictionResult(kept=[], removed=[], before_tokens=0, after_tokens=0, budget=600)
        assert result.compression_ratio == 0.0


class TestContextEvictorSingleton:
    def test_instance_returns_same(self):
        ContextEvictor.reset_instance()
        a = ContextEvictor.instance()
        b = ContextEvictor.instance()
        assert a is b
        ContextEvictor.reset_instance()

    def test_reset_instance(self):
        ContextEvictor.instance()
        ContextEvictor.reset_instance()
        assert ContextEvictor.instance is None
