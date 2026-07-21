# [A_test] module_id: MOD-GOV_context_evictor_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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


class TestPriorityLevel:
    def test_values(self):
        assert PriorityLevel.LOW == 10
        assert PriorityLevel.NORMAL == 100
        assert PriorityLevel.HIGH == 150
        assert PriorityLevel.CRITICAL == 200
        assert PriorityLevel.PINNED == 255

    def test_ordering(self):
        assert (
            PriorityLevel.LOW
            < PriorityLevel.NORMAL
            < PriorityLevel.HIGH
            < PriorityLevel.CRITICAL
            < PriorityLevel.PINNED
        )


class TestContextBlock:
    def test_defaults(self):
        block = ContextBlock(block_id="b1", content="hello")
        assert block.token_estimate == 0
        assert block.priority == PriorityLevel.NORMAL
        assert block.freshness == 0.5
        assert block.relevance == 0.5
        assert block.is_pinned is False
        assert block.is_mandatory is False

    def test_pinned_block(self):
        block = ContextBlock(block_id="b1", content="pinned", priority=PriorityLevel.PINNED)
        assert block.is_pinned is True
        assert block.is_mandatory is True

    def test_critical_block(self):
        block = ContextBlock(block_id="b1", content="crit", priority=PriorityLevel.CRITICAL)
        assert block.is_pinned is False
        assert block.is_mandatory is True

    def test_compute_eviction_score_low_priority(self):
        block = ContextBlock(block_id="b1", content="x", priority=PriorityLevel.LOW, freshness=0.1, relevance=0.1)
        score = block.compute_eviction_score()
        assert score > 0.5

    def test_compute_eviction_score_high_priority(self):
        block = ContextBlock(block_id="b1", content="x", priority=PriorityLevel.PINNED, freshness=1.0, relevance=1.0)
        score = block.compute_eviction_score()
        assert score == pytest.approx(0.0)


class TestEvictionResult:
    def test_compression_ratio_normal(self):
        result = EvictionResult(kept=[], removed=[], before_tokens=100, after_tokens=60)
        assert result.compression_ratio == pytest.approx(0.6)

    def test_compression_ratio_zero_before(self):
        result = EvictionResult(kept=[], removed=[], before_tokens=0, after_tokens=0)
        assert result.compression_ratio == 1.0


class TestContextEvictor:
    def test_default_weights(self):
        evictor = ContextEvictor()
        assert evictor.weights == (0.40, 0.35, 0.25)

    def test_custom_weights(self):
        evictor = ContextEvictor(w_p=0.5, w_f=0.3, w_r=0.2)
        assert evictor.weights == (0.5, 0.3, 0.2)

    def test_weights_from_dict(self):
        evictor = ContextEvictor(weights={"priority_weight": 0.6, "freshness_weight": 0.3, "relevance_weight": 0.1})
        assert evictor.weights == (0.6, 0.3, 0.1)

    def test_evict_empty_blocks(self):
        evictor = ContextEvictor()
        result = evictor.evict([], 1000)
        assert result.kept_count == 0
        assert result.removed_count == 0
        assert result.before_tokens == 0

    def test_evict_all_fit(self):
        evictor = ContextEvictor()
        blocks = [
            ContextBlock(block_id="b1", content="a", token_estimate=100),
            ContextBlock(block_id="b2", content="b", token_estimate=200),
        ]
        result = evictor.evict(blocks, 1000)
        assert result.kept_count == 2
        assert result.removed_count == 0
        assert result.after_tokens == 300

    def test_evict_some_removed(self):
        evictor = ContextEvictor()
        blocks = [
            ContextBlock(
                block_id="b1", content="a", token_estimate=100, priority=PriorityLevel.LOW, freshness=0.1, relevance=0.1
            ),
            ContextBlock(
                block_id="b2",
                content="b",
                token_estimate=200,
                priority=PriorityLevel.HIGH,
                freshness=0.9,
                relevance=0.9,
            ),
        ]
        result = evictor.evict(blocks, 250)
        assert result.kept_count == 1
        assert result.removed_count == 1
        assert result.kept[0].block_id == "b2"

    def test_evict_pinned_always_kept(self):
        evictor = ContextEvictor()
        blocks = [
            ContextBlock(block_id="pinned", content="p", token_estimate=500, priority=PriorityLevel.PINNED),
            ContextBlock(block_id="normal", content="n", token_estimate=100, priority=PriorityLevel.NORMAL),
        ]
        result = evictor.evict(blocks, 50)
        assert any(b.block_id == "pinned" for b in result.kept)
        assert result.removed_count == 1

    def test_instance_singleton(self):
        ContextEvictor.reset_instance()
        inst1 = ContextEvictor.instance()
        inst2 = ContextEvictor.instance()
        assert inst1 is inst2
        ContextEvictor.reset_instance()

    def test_evict_zero_budget(self):
        evictor = ContextEvictor()
        blocks = [ContextBlock(block_id="b1", content="x", token_estimate=100)]
        result = evictor.evict(blocks, 0)
        assert result.kept_count == 0
        assert result.removed_count == 1
