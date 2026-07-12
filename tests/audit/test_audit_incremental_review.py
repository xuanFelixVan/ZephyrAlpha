# [A_test] module_id: SRC-TST-0354 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_incremental_review
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.incremental_review import REVIEW_DIMENSIONS, ReviewChunk


class TestReviewChunk:
    def test_create_chunk(self):
        chunk = ReviewChunk(level="L1", chunk_id="CH-001")
        assert chunk.level == "L1"
        assert chunk.chunk_id == "CH-001"
        assert chunk.time_budget_minutes == 30

    def test_custom_time_budget(self):
        chunk = ReviewChunk(level="L2", chunk_id="CH-002", time_budget_minutes=60)
        assert chunk.time_budget_minutes == 60

    def test_default_values(self):
        chunk = ReviewChunk(level="L3", chunk_id="CH-003")
        assert chunk.time_budget_minutes == 30

    def test_empty_level(self):
        chunk = ReviewChunk(level="", chunk_id="CH-004")
        assert chunk.level == ""


class TestReviewDimensions:
    def test_dimensions_exist(self):
        expected_keys = {"consistency", "accuracy", "completeness", "traceability", "token_efficiency", "no_regression"}
        assert set(REVIEW_DIMENSIONS.keys()) == expected_keys

    def test_dimensions_have_descriptions(self):
        for key, desc in REVIEW_DIMENSIONS.items():
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_dimension_count(self):
        assert len(REVIEW_DIMENSIONS) == 6
