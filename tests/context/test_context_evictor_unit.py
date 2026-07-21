# [A_test] module_id: MOD-GOV_context_evictor_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-611 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_context_evictor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for context_evictor.py — beta a
============================================
Minimum: 12 tests
"""


from zephyr.autonomy_core.context.context_evictor import (
    ContextBlock,
    ContextEvictor,
    PriorityLevel,
)


def _make_block(
    block_id: str,
    tokens: int = 100,
    priority: PriorityLevel = PriorityLevel.NORMAL,
    freshness: float = 0.5,
    relevance: float = 0.5,
) -> ContextBlock:
    return ContextBlock(
        block_id=block_id,
        content=f"Content of {block_id}",
        token_estimate=tokens,
        priority=priority,
        freshness=freshness,
        relevance=relevance,
    )


class TestPriorityLevel:
    def test_low_lt_normal(self) -> None:
        assert PriorityLevel.LOW < PriorityLevel.NORMAL

    def test_critical_lt_pinned(self) -> None:
        assert PriorityLevel.CRITICAL < PriorityLevel.PINNED

    def test_numeric_values(self) -> None:
        assert PriorityLevel.LOW == 10
        assert PriorityLevel.PINNED == 255


class TestContextBlock:
    def test_default_construction(self) -> None:
        block = ContextBlock(block_id="b1", content="test", provenance="MOD-CONTEXT_ENGINE:§3")
        assert block.block_id == "b1"
        assert block.priority == PriorityLevel.NORMAL
        assert block.provenance == "MOD-CONTEXT_ENGINE:§3"

    def test_is_pinned(self) -> None:
        block = ContextBlock(block_id="b1", content="test", priority=PriorityLevel.PINNED)
        assert block.is_pinned
        assert block.is_mandatory

    def test_is_mandatory_critical(self) -> None:
        block = ContextBlock(block_id="b1", content="test", priority=PriorityLevel.CRITICAL)
        assert block.is_mandatory
        assert not block.is_pinned

    def test_eviction_score_low_priority_is_high(self) -> None:
        low = ContextBlock(block_id="b1", content="test", priority=PriorityLevel.LOW)
        high = ContextBlock(block_id="b2", content="test", priority=PriorityLevel.HIGH)
        assert low.compute_eviction_score() > high.compute_eviction_score()

    def test_eviction_score_fresh_block_is_lower(self) -> None:
        stale = ContextBlock(block_id="b1", content="test", freshness=0.1)
        fresh = ContextBlock(block_id="b2", content="test", freshness=0.9)
        assert stale.compute_eviction_score() > fresh.compute_eviction_score()


class TestContextEvictor:
    def test_empty_blocks(self) -> None:
        evictor = ContextEvictor()
        result = evictor.evict([], 1000)
        assert result.kept_count == 0
        assert result.removed_count == 0

    def test_within_budget_all_kept(self) -> None:
        blocks = [_make_block(f"b{i}", tokens=100) for i in range(5)]
        evictor = ContextEvictor()
        result = evictor.evict(blocks, 1000)
        assert result.kept_count == 5
        assert result.removed_count == 0

    def test_pinned_always_kept(self) -> None:
        blocks = [
            _make_block("b1", tokens=100, priority=PriorityLevel.PINNED),
            _make_block("b2", tokens=100),
        ]
        evictor = ContextEvictor()
        result = evictor.evict(blocks, 50)
        assert any(b.block_id == "b1" for b in result.kept)

    def test_low_priority_evicted_first(self) -> None:
        blocks = [
            _make_block("b1", tokens=100, priority=PriorityLevel.LOW),
            _make_block("b2", tokens=100, priority=PriorityLevel.HIGH),
        ]
        evictor = ContextEvictor()
        result = evictor.evict(blocks, 100)
        kept_ids = {b.block_id for b in result.kept}
        assert "b2" in kept_ids

    def test_eviction_reduces_token_count(self) -> None:
        blocks = [_make_block(f"b{i}", tokens=100) for i in range(20)]
        evictor = ContextEvictor()
        result = evictor.evict(blocks, 500)
        assert result.after_tokens <= 500

    def test_stale_evicted_before_fresh(self) -> None:
        fresh = _make_block("fresh", tokens=100, freshness=0.9, relevance=0.5)
        stale = _make_block("stale", tokens=100, freshness=0.1, relevance=0.5)
        evictor = ContextEvictor()
        result = evictor.evict([fresh, stale], 100)
        kept_ids = {b.block_id for b in result.kept}
        assert "fresh" in kept_ids

    def test_irrelevant_evicted_before_relevant(self) -> None:
        relevant = _make_block("rel", tokens=100, freshness=0.5, relevance=0.9)
        irrelevant = _make_block("irr", tokens=100, freshness=0.5, relevance=0.1)
        evictor = ContextEvictor()
        result = evictor.evict([relevant, irrelevant], 100)
        kept_ids = {b.block_id for b in result.kept}
        assert "rel" in kept_ids

    def test_compression_ratio(self) -> None:
        blocks = [_make_block(f"b{i}", tokens=500) for i in range(10)]
        evictor = ContextEvictor()
        result = evictor.evict(blocks, 1000)
        assert result.compression_ratio > 0

    def test_custom_weights(self) -> None:
        blocks = [
            _make_block("b1", tokens=100, freshness=0.1, relevance=0.9),
            _make_block("b2", tokens=100, freshness=0.9, relevance=0.1),
        ]
        evictor = ContextEvictor(weights={"priority_weight": 0.1, "freshness_weight": 0.8, "relevance_weight": 0.1})
        result = evictor.evict(blocks, 100)
        kept_ids = {b.block_id for b in result.kept}
        assert "b2" in kept_ids

    def test_singleton_instance(self) -> None:
        ContextEvictor.reset_instance()
        a = ContextEvictor.instance(weights={"priority_weight": 0.7, "freshness_weight": 0.2, "relevance_weight": 0.1})
        b = ContextEvictor.instance()
        assert a is b
        ContextEvictor.reset_instance()
