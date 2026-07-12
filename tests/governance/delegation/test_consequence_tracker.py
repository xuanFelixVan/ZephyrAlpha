# [A_test] module_id: SRC-TST-0580 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_consequence_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.trackers.consequence_tracker import (
    Consequence,
    ConsequenceTracker,
)


class TestConsequenceTracker:
    def test_instantiation(self):
        tracker = ConsequenceTracker()
        assert tracker is not None

    def test_record(self):
        tracker = ConsequenceTracker()
        result = tracker.record("fix-001", "file_a.py", ["file_b.py", "file_c.py"])
        assert isinstance(result, Consequence)

    def test_rollback_last(self):
        tracker = ConsequenceTracker()
        tracker.record("fix-001", "file_a.py", ["file_b.py"])
        result = tracker.rollback_last()
        assert result is not None

    def test_rollback_last_empty(self):
        tracker = ConsequenceTracker()
        result = tracker.rollback_last()
        assert isinstance(result, dict)

    def test_summary(self):
        tracker = ConsequenceTracker()
        tracker.record("fix-001", "file_a.py", ["file_b.py"])
        result = tracker.summary()
        assert isinstance(result, dict)
