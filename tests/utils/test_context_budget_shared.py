# [A_test] module_id: SRC-TST-1943 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-560 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_context_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/context_budget.py
===============================================
覆盖矩阵：
  BudgetEntry：
    - 构造 & 自动 token 估计 × 2
    - priority 默认值 × 1
  ContextBudget 初始化：
    - 默认 total_budget × 1
    - 自定义 total_budget × 1
  ContextBudget.allocate / release：
    - allocate 返回 alloc_id × 1
    - release 返还 token 数 × 1
    - release 不存在的 id 返回 0 × 1
  ContextBudget.add_entry / remove_entry：
    - add_entry 加入 entry × 1
    - remove_entry 移除并返回 × 1
    - remove_entry 不存在返回 None × 1
  ContextBudget 属性：
    - allocated_total × 1
    - entries_total × 1
    - consumed = allocated + entries × 1
    - remaining × 2（正常 / 谷底 0）
    - over_budget × 2
    - usage_ratio × 2
  ContextBudget.truncate：
    - 未超出预算返回空 × 1
    - OLDEST_FIRST × 1
    - NEWEST_FIRST × 1
    - SUMMARY_FIRST × 1
    - RELEVANCE_FIRST × 1
  ContextBudget.get_by_key / reset：
    - get_by_key 找到/未找到 × 2
    - reset 清除 × 1
  QuotaTracker：
    - consume 成功/失败 × 2
    - remaining / exhausted × 2
    - reset × 1
  TruncationStrategy：
    - 枚举值完整性 × 1

Safety: HIGH（上下文预算管防控是 token 过载防线）
"""

from zephyr.autonomy_core.context.context_budget import (
    BudgetEntry,
    ContextBudget,
    QuotaTracker,
    TruncationStrategy,
)


class TestBudgetEntry:
    def test_construction_with_content(self):
        entry = BudgetEntry(key="sys_prompt", content="You are a helpful assistant.")
        assert entry.key == "sys_prompt"
        assert entry.content == "You are a helpful assistant."
        assert entry.tokens > 0
        assert entry.priority == 0

    def test_construction_with_explicit_tokens(self):
        entry = BudgetEntry(key="data", content="...", tokens=42)
        assert entry.tokens == 42

    def test_priority(self):
        entry = BudgetEntry(key="high", content="urgent", priority=10)
        assert entry.priority == 10


class TestContextBudgetInit:
    def test_default_budget_size(self):
        b = ContextBudget()
        assert b.total_budget > 0
        assert b.allocation == {}
        assert b.entries == []

    def test_custom_budget(self):
        b = ContextBudget(total_budget=8000)
        assert b.total_budget == 8000


class TestAllocateRelease:
    def test_allocate_returns_id(self):
        b = ContextBudget(total_budget=16000)
        alloc_id = b.allocate(4000, "system")
        assert alloc_id.startswith("ctx-")
        assert b.allocation[alloc_id] == 4000

    def test_release_returns_tokens(self):
        b = ContextBudget(total_budget=16000)
        alloc_id = b.allocate(3000)
        released = b.release(alloc_id)
        assert released == 3000
        assert alloc_id not in b.allocation

    def test_release_nonexistent_returns_zero(self):
        b = ContextBudget(total_budget=16000)
        assert b.release("ctx-9999") == 0

    def test_multiple_allocations(self):
        b = ContextBudget(total_budget=16000)
        id1 = b.allocate(5000)
        id2 = b.allocate(3000)
        assert b.allocated_total == 8000


class TestAddRemoveEntry:
    def test_add_entry(self):
        b = ContextBudget(total_budget=16000)
        entry = b.add_entry("file_a", "some content", priority=3)
        assert entry.key == "file_a"
        assert len(b.entries) == 1

    def test_remove_entry(self):
        b = ContextBudget(total_budget=16000)
        b.add_entry("file_a", "content")
        removed = b.remove_entry("file_a")
        assert removed is not None
        assert removed.key == "file_a"
        assert len(b.entries) == 0

    def test_remove_nonexistent(self):
        b = ContextBudget(total_budget=16000)
        assert b.remove_entry("nonexistent") is None


class TestBudgetProperties:
    def test_allocated_total(self):
        b = ContextBudget(total_budget=16000)
        b.allocate(5000)
        b.allocate(3000)
        assert b.allocated_total == 8000

    def test_entries_total(self):
        b = ContextBudget(total_budget=16000)
        from zephyr.autonomy_core.context.context_budget import BudgetEntry

        b.entries = [
            BudgetEntry(key="a", content="hello world", tokens=5),
            BudgetEntry(key="b", content="hi", tokens=2),
        ]
        assert b.entries_total == 7

    def test_consumed(self):
        b = ContextBudget(total_budget=16000)
        b.allocate(100)
        from zephyr.autonomy_core.context.context_budget import BudgetEntry

        b.entries = [BudgetEntry(key="x", content="test", tokens=50)]
        assert b.consumed == 150

    def test_remaining(self):
        b = ContextBudget(total_budget=1000)
        b.allocate(200)
        assert b.remaining == 800

    def test_remaining_floors_at_zero(self):
        b = ContextBudget(total_budget=100)
        b.allocate(200)
        assert b.remaining == 0

    def test_over_budget_false(self):
        b = ContextBudget(total_budget=1000)
        b.allocate(500)
        assert not b.over_budget

    def test_over_budget_true(self):
        b = ContextBudget(total_budget=100)
        b.allocate(150)
        assert b.over_budget

    def test_usage_ratio(self):
        b = ContextBudget(total_budget=1000)
        b.allocate(300)
        assert b.usage_ratio == 0.3

    def test_usage_ratio_capped_at_one(self):
        b = ContextBudget(total_budget=100)
        b.allocate(200)
        assert b.usage_ratio == 1.0


class TestTruncate:
    def _make_budget_with_entries(self) -> ContextBudget:
        b = ContextBudget(total_budget=30)
        b.add_entry("entry1", "hello world " * 50, priority=0)
        b.add_entry("entry2", "the quick brown fox " * 50, priority=1)
        b.add_entry("entry3", "lorem ipsum dolor sit " * 50, priority=2)
        return b

    def test_no_truncation_when_within_budget(self):
        b = ContextBudget(total_budget=10000)
        b.add_entry("x", "hello")
        discarded = b.truncate(TruncationStrategy.OLDEST_FIRST)
        assert discarded == []

    def test_oldest_first(self):
        b = self._make_budget_with_entries()
        discarded = b.truncate(TruncationStrategy.OLDEST_FIRST)
        assert len(discarded) > 0
        assert b.consumed <= b.total_budget

    def test_newest_first(self):
        b = self._make_budget_with_entries()
        discarded = b.truncate(TruncationStrategy.NEWEST_FIRST)
        assert len(discarded) > 0
        assert b.consumed <= b.total_budget

    def test_summary_first(self):
        b = self._make_budget_with_entries()
        discarded = b.truncate(TruncationStrategy.SUMMARY_FIRST)
        assert len(discarded) > 0
        assert b.consumed <= b.total_budget

    def test_relevance_first(self):
        b = self._make_budget_with_entries()
        discarded = b.truncate(TruncationStrategy.RELEVANCE_FIRST)
        assert len(discarded) > 0
        assert b.consumed <= b.total_budget


class TestGetByKeyReset:
    def test_get_by_key_found(self):
        b = ContextBudget(total_budget=16000)
        b.add_entry("config", "server.port=8080")
        entry = b.get_by_key("config")
        assert entry is not None
        assert entry.key == "config"

    def test_get_by_key_not_found(self):
        b = ContextBudget(total_budget=16000)
        assert b.get_by_key("missing") is None

    def test_reset(self):
        b = ContextBudget(total_budget=16000)
        b.allocate(5000)
        b.add_entry("x", "data")
        b.reset()
        assert b.allocated_total == 0
        assert b.entries_total == 0
        assert len(b.entries) == 0
        assert len(b.allocation) == 0


class TestQuotaTracker:
    def test_consume_success(self):
        q = QuotaTracker(total_quota=1000)
        assert q.consume(300) is True
        assert q.consumed == 300

    def test_consume_exceeded(self):
        q = QuotaTracker(total_quota=500)
        assert q.consume(600) is False
        assert q.consumed == 0

    def test_consume_cumulative_fail(self):
        q = QuotaTracker(total_quota=500)
        q.consume(400)
        assert q.consume(200) is False
        assert q.consumed == 400

    def test_remaining(self):
        q = QuotaTracker(total_quota=1000)
        q.consume(600)
        assert q.remaining == 400

    def test_exhausted(self):
        q = QuotaTracker(total_quota=100)
        assert not q.exhausted
        q.consume(100)
        assert q.exhausted

    def test_exhausted_zero_quota_not_exhausted(self):
        q = QuotaTracker(total_quota=0)
        assert not q.exhausted

    def test_reset(self):
        q = QuotaTracker(total_quota=1000)
        q.consume(500)
        q.reset()
        assert q.consumed == 0


class TestTruncationStrategyEnum:
    def test_all_strategies(self):
        strategies = {s.value for s in TruncationStrategy}
        assert "oldest_first" in strategies
        assert "newest_first" in strategies
        assert "summary_first" in strategies
        assert "relevance_first" in strategies
        assert len(strategies) == 4
