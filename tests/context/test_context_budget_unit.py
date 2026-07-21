# [A_test] module_id: MOD-GOV_context_budget_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-610 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_context_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for context_budget.py
"""

from zephyr.autonomy_core.context.context_budget import (
    BudgetEntry,
    ContextBudget,
    QuotaTracker,
    TruncationStrategy,
)


class TestBudgetEntry:
    def test_create_entry(self):
        entry = BudgetEntry(key="file_1", content="hello world", priority=5)
        assert entry.key == "file_1"
        assert entry.content == "hello world"
        assert entry.priority == 5
        assert entry.tokens > 0

    def test_entry_auto_calculates_tokens(self):
        entry = BudgetEntry(key="doc", content="a" * 100)
        assert entry.tokens == max(100 // 4, 1)

    def test_entry_empty_content(self):
        entry = BudgetEntry(key="empty", content="")
        assert entry.tokens == 0

    def test_entry_preserves_explicit_tokens(self):
        entry = BudgetEntry(key="x", content="test", tokens=100)
        assert entry.tokens == 100


class TestContextBudget:
    def test_initial_state(self):
        budget = ContextBudget(total_budget=8000)
        assert budget.total_budget == 8000
        assert budget.consumed == 0
        assert budget.remaining == 8000
        assert not budget.over_budget
        assert budget.usage_ratio == 0.0

    def test_allocate_returns_id(self):
        budget = ContextBudget()
        alloc_id = budget.allocate(4000)
        assert alloc_id.startswith("ctx-")
        assert budget.allocated_total == 4000
        assert budget.consumed == 4000

    def test_allocate_multiple(self):
        budget = ContextBudget(total_budget=16000)
        budget.allocate(4000, "prompt")
        budget.allocate(2000, "context")
        assert budget.allocated_total == 6000

    def test_release(self):
        budget = ContextBudget()
        alloc_id = budget.allocate(3000)
        released = budget.release(alloc_id)
        assert released == 3000
        assert budget.allocated_total == 0

    def test_release_nonexistent(self):
        budget = ContextBudget()
        assert budget.release("nonexistent") == 0

    def test_add_entry(self):
        budget = ContextBudget()
        entry = budget.add_entry("f1", "some content")
        assert entry.key == "f1"
        assert len(budget.entries) == 1
        assert budget.entries_total > 0

    def test_remove_entry(self):
        budget = ContextBudget()
        budget.add_entry("f1", "data")
        removed = budget.remove_entry("f1")
        assert removed is not None
        assert removed.key == "f1"
        assert len(budget.entries) == 0

    def test_remove_entry_nonexistent(self):
        budget = ContextBudget()
        assert budget.remove_entry("nope") is None

    def test_consumed_includes_allocated_and_entries(self):
        budget = ContextBudget()
        budget.allocate(1000)
        budget.add_entry("f1", "x" * 400)
        assert budget.consumed == 1000 + (400 // 4)

    def test_remaining(self):
        budget = ContextBudget(total_budget=5000)
        budget.allocate(2000)
        assert budget.remaining == 3000

    def test_remaining_never_negative(self):
        budget = ContextBudget(total_budget=100)
        budget.allocate(500)
        assert budget.remaining == 0

    def test_over_budget(self):
        budget = ContextBudget(total_budget=100)
        budget.allocate(200)
        assert budget.over_budget

    def test_usage_ratio(self):
        budget = ContextBudget(total_budget=1000)
        budget.allocate(500)
        assert budget.usage_ratio == 0.5

    def test_truncate_oldest_first(self):
        budget = ContextBudget(total_budget=300)
        budget.add_entry("f1", "a" * 1000)
        budget.add_entry("f2", "b" * 1000)
        budget.add_entry("f3", "c" * 1000)

        discarded = budget.truncate(TruncationStrategy.OLDEST_FIRST)
        assert len(discarded) > 0
        assert discarded[0].key == "f1"

    def test_truncate_newest_first(self):
        budget = ContextBudget(total_budget=300)
        budget.add_entry("f1", "a" * 1000, priority=1)
        budget.add_entry("f2", "b" * 1000, priority=5)
        budget.add_entry("f3", "c" * 1000, priority=1)

        discarded = budget.truncate(TruncationStrategy.NEWEST_FIRST)
        assert len(discarded) > 0

    def test_truncate_summary_first(self):
        budget = ContextBudget(total_budget=300)
        budget.add_entry("f1", "a" * 1000)
        budget.add_entry("f2", "b" * 400)
        budget.add_entry("f3", "c" * 10000)

        discarded = budget.truncate(TruncationStrategy.SUMMARY_FIRST)
        assert len(discarded) > 0

    def test_truncate_no_op_when_under_budget(self):
        budget = ContextBudget(total_budget=10000)
        budget.add_entry("f1", "test")
        discarded = budget.truncate()
        assert len(discarded) == 0

    def test_get_by_key(self):
        budget = ContextBudget()
        budget.add_entry("findme", "content")
        found = budget.get_by_key("findme")
        assert found is not None
        assert found.key == "findme"

    def test_get_by_key_nonexistent(self):
        budget = ContextBudget()
        assert budget.get_by_key("nope") is None

    def test_reset(self):
        budget = ContextBudget()
        budget.allocate(1000)
        budget.add_entry("f1", "data")
        budget.reset()
        assert budget.allocated_total == 0
        assert budget.entries_total == 0
        assert budget.consumed == 0


class TestQuotaTracker:
    def test_initial_state(self):
        tracker = QuotaTracker(total_quota=10000)
        assert tracker.total_quota == 10000
        assert tracker.consumed == 0
        assert not tracker.exhausted

    def test_consume_within_quota(self):
        tracker = QuotaTracker(total_quota=10000)
        result = tracker.consume(5000)
        assert result is True
        assert tracker.consumed == 5000

    def test_consume_exceeds_quota(self):
        tracker = QuotaTracker(total_quota=1000)
        tracker.consume(800)
        result = tracker.consume(500)
        assert result is False
        assert tracker.consumed == 800

    def test_consume_no_limit(self):
        tracker = QuotaTracker(total_quota=0)
        result = tracker.consume(1000000)
        assert result is True

    def test_remaining(self):
        tracker = QuotaTracker(total_quota=5000)
        tracker.consume(2000)
        assert tracker.remaining == 3000

    def test_exhausted(self):
        tracker = QuotaTracker(total_quota=100)
        tracker.consume(100)
        assert tracker.exhausted

    def test_not_exhausted_no_limit(self):
        tracker = QuotaTracker(total_quota=0)
        assert not tracker.exhausted

    def test_reset(self):
        tracker = QuotaTracker(total_quota=10000)
        tracker.consume(5000)
        tracker.reset()
        assert tracker.consumed == 0
