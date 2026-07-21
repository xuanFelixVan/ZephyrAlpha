# [A_test] module_id: MOD-GOV_context_budget_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_context_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_context_budget.py
# [TTL] task_bound

from __future__ import annotations

import threading

from zephyr.governance.context_governance.context_budget import (
    BudgetEntry,
    ContextBudget,
    QuotaTracker,
    TruncationStrategy,
)


class TestTruncationStrategy:
    def test_enum_values(self):
        assert TruncationStrategy.NEWEST_FIRST.value == "newest_first"
        assert TruncationStrategy.OLDEST_FIRST.value == "oldest_first"
        assert TruncationStrategy.SUMMARY_FIRST.value == "summary_first"
        assert TruncationStrategy.RELEVANCE_FIRST.value == "relevance_first"

    def test_enum_is_string(self):
        for member in TruncationStrategy:
            assert isinstance(member.value, str)


class TestBudgetEntry:
    def test_post_init_estimates_tokens(self):
        entry = BudgetEntry(key="k1", content="a" * 40)
        assert entry.tokens > 0

    def test_post_init_no_override_explicit_tokens(self):
        entry = BudgetEntry(key="k1", content="hello world", tokens=42)
        assert entry.tokens == 42

    def test_empty_content_zero_tokens(self):
        entry = BudgetEntry(key="k1", content="")
        assert entry.tokens == 0


class TestContextBudget:
    def test_allocate_returns_alloc_id(self):
        budget = ContextBudget(total_budget=10000)
        alloc_id = budget.allocate(1000, "test")
        assert alloc_id.startswith("ctx-")

    def test_allocate_increments_counter(self):
        budget = ContextBudget(total_budget=10000)
        id1 = budget.allocate(100)
        id2 = budget.allocate(200)
        assert id1 != id2

    def test_release_returns_tokens(self):
        budget = ContextBudget(total_budget=10000)
        alloc_id = budget.allocate(500)
        released = budget.release(alloc_id)
        assert released == 500

    def test_release_unknown_returns_zero(self):
        budget = ContextBudget(total_budget=10000)
        assert budget.release("nonexistent") == 0

    def test_add_entry(self):
        budget = ContextBudget(total_budget=10000)
        entry = budget.add_entry("k1", "some content", priority=3)
        assert entry.key == "k1"
        assert entry.priority == 3
        assert budget.entries_total > 0

    def test_remove_entry(self):
        budget = ContextBudget(total_budget=10000)
        budget.add_entry("k1", "content")
        removed = budget.remove_entry("k1")
        assert removed is not None
        assert removed.key == "k1"
        assert budget.remove_entry("k1") is None

    def test_remove_entry_nonexistent(self):
        budget = ContextBudget(total_budget=10000)
        assert budget.remove_entry("nope") is None

    def test_allocated_total(self):
        budget = ContextBudget(total_budget=10000)
        budget.allocate(300)
        budget.allocate(700)
        assert budget.allocated_total == 1000

    def test_consumed_equals_allocated_plus_entries(self):
        budget = ContextBudget(total_budget=10000)
        budget.allocate(500)
        budget.add_entry("k1", "a" * 400)
        assert budget.consumed == budget.allocated_total + budget.entries_total

    def test_remaining(self):
        budget = ContextBudget(total_budget=1000)
        budget.allocate(300)
        assert budget.remaining == 700

    def test_remaining_never_negative(self):
        budget = ContextBudget(total_budget=100)
        budget.allocate(500)
        assert budget.remaining == 0

    def test_over_budget(self):
        budget = ContextBudget(total_budget=100)
        budget.allocate(200)
        assert budget.over_budget is True

    def test_not_over_budget(self):
        budget = ContextBudget(total_budget=1000)
        budget.allocate(500)
        assert budget.over_budget is False

    def test_usage_ratio(self):
        budget = ContextBudget(total_budget=1000)
        budget.allocate(250)
        assert budget.usage_ratio == 0.25

    def test_usage_ratio_zero_budget(self):
        budget = ContextBudget(total_budget=0)
        assert budget.usage_ratio == 1.0

    def test_truncate_oldest_first(self):
        budget = ContextBudget(total_budget=50)
        budget.add_entry("k1", "a" * 200, priority=1)
        budget.add_entry("k2", "b" * 200, priority=5)
        discarded = budget.truncate(TruncationStrategy.OLDEST_FIRST)
        assert len(discarded) > 0
        assert not budget.over_budget or budget.entries_total <= 50

    def test_truncate_newest_first(self):
        budget = ContextBudget(total_budget=50)
        budget.add_entry("k1", "a" * 200, priority=1)
        budget.add_entry("k2", "b" * 200, priority=5)
        discarded = budget.truncate(TruncationStrategy.NEWEST_FIRST)
        assert len(discarded) > 0

    def test_truncate_not_over_budget_returns_empty(self):
        budget = ContextBudget(total_budget=10000)
        budget.add_entry("k1", "small")
        assert budget.truncate() == []

    def test_get_by_key(self):
        budget = ContextBudget(total_budget=10000)
        budget.add_entry("k1", "content")
        found = budget.get_by_key("k1")
        assert found is not None
        assert found.key == "k1"

    def test_get_by_key_not_found(self):
        budget = ContextBudget(total_budget=10000)
        assert budget.get_by_key("missing") is None

    def test_reset(self):
        budget = ContextBudget(total_budget=10000)
        budget.allocate(500)
        budget.add_entry("k1", "content")
        budget.reset()
        assert budget.allocated_total == 0
        assert budget.entries_total == 0

    def test_thread_safety(self):
        budget = ContextBudget(total_budget=100000)
        errors = []

        def worker():
            try:
                for _ in range(50):
                    aid = budget.allocate(10)
                    budget.add_entry(f"k-{aid}", "x" * 40)
                    budget.release(aid)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []


class TestQuotaTracker:
    def test_consume_within_quota(self):
        qt = QuotaTracker(total_quota=1000)
        assert qt.consume(500) is True
        assert qt.remaining == 500

    def test_consume_exceeds_quota(self):
        qt = QuotaTracker(total_quota=100)
        assert qt.consume(200) is False

    def test_consume_zero_quota_unlimited(self):
        qt = QuotaTracker(total_quota=0)
        assert qt.consume(9999) is True

    def test_exhausted(self):
        qt = QuotaTracker(total_quota=100)
        qt.consume(100)
        assert qt.exhausted is True

    def test_not_exhausted(self):
        qt = QuotaTracker(total_quota=100)
        qt.consume(50)
        assert qt.exhausted is False

    def test_remaining(self):
        qt = QuotaTracker(total_quota=100)
        qt.consume(30)
        assert qt.remaining == 70

    def test_remaining_never_negative(self):
        qt = QuotaTracker(total_quota=50)
        qt.consume(30)
        qt.consume(30)
        assert qt.remaining >= 0

    def test_reset(self):
        qt = QuotaTracker(total_quota=100)
        qt.consume(80)
        qt.reset()
        assert qt.consumed == 0
        assert qt.remaining == 100
