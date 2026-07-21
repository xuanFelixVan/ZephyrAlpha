# [A_test] module_id: MOD-GOV_context_evictor_context_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-462 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_context_evictor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""Tests for context_evictor.py (TASK-014 beta a — migrated to ContextBlock model)."""


from zephyr.autonomy_core.context.context_evictor import (
    ContextBlock,
    ContextEvictor,
    EvictionResult,
    PriorityLevel,
)


def _block(
    block_id: str,
    tokens: int = 50,
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


class TestContextEvictor:
    def test_evict_under_budget(self) -> None:
        evictor = ContextEvictor()
        blocks = [_block("KE-001", tokens=100, freshness=0.8, relevance=0.7)]
        result = evictor.evict(blocks, token_budget=500)
        assert isinstance(result, EvictionResult)
        assert result.removed_count == 0
        assert result.kept_count == 1

    def test_evict_over_budget(self) -> None:
        evictor = ContextEvictor()
        blocks = [_block(str(i), tokens=50) for i in range(20)]
        result = evictor.evict(blocks, token_budget=100)
        assert result.removed_count > 0

    def test_low_priority_evicted_first(self) -> None:
        evictor = ContextEvictor()
        b_high = _block("HIGH", priority=PriorityLevel.HIGH, tokens=50)
        b_low = _block("LOW", priority=PriorityLevel.LOW, tokens=50)
        result = evictor.evict([b_high, b_low], token_budget=50)
        kept_ids = {b.block_id for b in result.kept}
        assert "HIGH" in kept_ids

    def test_score_uses_custom_weights(self) -> None:
        evictor = ContextEvictor(w_p=0.50, w_f=0.30, w_r=0.20)
        b = _block("X", priority=PriorityLevel.NORMAL)
        score = b.compute_eviction_score()
        assert 0.0 < score < 1.0

    def test_weights_property(self) -> None:
        evictor = ContextEvictor()
        wp, wf, wr = evictor.weights
        assert wp == 0.40
        assert wf == 0.35
        assert wr == 0.25

    def test_custom_constructor_weights(self) -> None:
        evictor = ContextEvictor(w_p=0.6, w_f=0.2, w_r=0.2)
        wp, wf, wr = evictor.weights
        assert wp == 0.6

    def test_empty_blocks(self) -> None:
        evictor = ContextEvictor()
        result = evictor.evict([], token_budget=100)
        assert result.kept_count == 0
        assert result.removed_count == 0

    def test_all_evicted_when_zero_budget(self) -> None:
        evictor = ContextEvictor()
        blocks = [_block("KE-001", tokens=50)]
        result = evictor.evict(blocks, token_budget=0)
        assert result.removed_count == 1
