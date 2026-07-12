# [A_test] module_id: SRC-TST-1117 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-397 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_incremental_review
# [INVARIANTS] REVIEW_DIMENSIONS has 6 entries; ReviewChunk defaults time_budget to 30
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_incremental_review.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.execution.incremental_review import (
    REVIEW_DIMENSIONS,
    ReviewChunk,
)


class TestReviewChunk:
    def test_creation_defaults(self):
        chunk = ReviewChunk(level="L1", chunk_id="C1")
        assert chunk.time_budget_minutes == 30

    def test_creation_custom(self):
        chunk = ReviewChunk(level="L2", chunk_id="C2", time_budget_minutes=60)
        assert chunk.time_budget_minutes == 60

    def test_fields_assigned(self):
        chunk = ReviewChunk(level="L3", chunk_id="C3")
        assert chunk.level == "L3"
        assert chunk.chunk_id == "C3"


class TestReviewDimensions:
    def test_dimension_count(self):
        assert len(REVIEW_DIMENSIONS) == 6

    def test_expected_keys(self):
        expected = {"consistency", "accuracy", "completeness", "traceability", "token_efficiency", "no_regression"}
        assert set(REVIEW_DIMENSIONS.keys()) == expected

    def test_all_values_non_empty(self):
        for key, value in REVIEW_DIMENSIONS.items():
            assert value != ""


class TestBoundary:
    def test_review_chunk_empty_level(self):
        chunk = ReviewChunk(level="", chunk_id="C0")
        assert chunk.level == ""

    def test_review_chunk_zero_budget(self):
        chunk = ReviewChunk(level="L1", chunk_id="C1", time_budget_minutes=0)
        assert chunk.time_budget_minutes == 0
