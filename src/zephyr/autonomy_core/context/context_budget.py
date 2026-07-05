# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §3-§8
# [MODULE] zephyr.autonomy_core.context.context_budget
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS] blueprint.md §0; zephyr.autonomy_core 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-CONTEXT_ENGINE 四阶段流水线不可绕过; Token 预算硬限制; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ContextEngineError
# [TESTS] tests/context-engine/
# [A_module] module_id=MOD-ORC_context_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""[BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md | §3-§8

TruncationStrategy — TruncationStrategy

依据: 蓝图 MOD-CONTEXT_ENGINE §3-§8

"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum, unique

from zephyr.infrastructure.capacity_assurance.token_budget import DEFAULT_CONTEXT_TOKEN_BUDGET, estimate_tokens


@unique
class TruncationStrategy(str, Enum):
    """超预算截断策略。"""

    NEWEST_FIRST = "newest_first"

    OLDEST_FIRST = "oldest_first"

    SUMMARY_FIRST = "summary_first"

    RELEVANCE_FIRST = "relevance_first"


@dataclass
class BudgetEntry:
    """单条上下文条目的预算追踪记录。"""

    key: str

    content: str

    tokens: int = 0

    priority: int = 0

    def __post_init__(self) -> None:
        if self.tokens == 0 and self.content:
            self.tokens = estimate_tokens(self.content)


@dataclass
class ContextBudget:
    """上下文预算管理器——配额分配、追踪、截断。





    Usage::





        budget = ContextBudget(total_budget=16000)


        alloc_id = budget.allocate(4000, "system_prompt")


        budget.add_entry("file_1", content_string, priority=5)


        if budget.over_budget:


            discarded = budget.truncate(TruncationStrategy.OLDEST_FIRST)


        budget.release(alloc_id)





    Attributes:


        total_budget: 总 token 预算。


        allocation: 已分配配额表 {alloc_id: allocated_tokens}。


        entries: 预算条目列表（动态增删）。


    """

    total_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET

    allocation: dict[str, int] = field(default_factory=dict)

    entries: list[BudgetEntry] = field(default_factory=list)

    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)

    _alloc_counter: int = field(default=0, init=False, repr=False)

    def allocate(self, tokens: int, requester: str = "") -> str:
        """分配配额。





        Args:


            tokens: 申请的 token 数量。


            requester: 调用方标识（用于日志）。





        Returns:


            分配 ID 字符串，用于 release()。


        """

        with self._lock:
            self._alloc_counter += 1

            alloc_id = f"ctx-{self._alloc_counter:04d}"

            self.allocation[alloc_id] = tokens

            return alloc_id

    def release(self, alloc_id: str) -> int:
        """释放已分配的配额。





        Returns:


            释放的 token 数量。alloc_id 不存在返回 0。


        """

        with self._lock:
            return self.allocation.pop(alloc_id, 0)

    def add_entry(self, key: str, content: str, priority: int = 0) -> BudgetEntry:
        """添加上下文条目到追踪列表。"""

        entry = BudgetEntry(key=key, content=content, priority=priority)

        with self._lock:
            self.entries.append(entry)

        return entry

    def remove_entry(self, key: str) -> BudgetEntry | None:
        """移除指定键的上下文条目。"""

        with self._lock:
            for i, entry in enumerate(self.entries):
                if entry.key == key:
                    return self.entries.pop(i)

        return None

    @property
    def allocated_total(self) -> int:
        """分配表中已占用的 token 总量。"""

        with self._lock:
            return sum(self.allocation.values())

    @property
    def entries_total(self) -> int:
        """追踪条目中已占用的 token 总量。"""

        with self._lock:
            return sum(e.tokens for e in self.entries)

    @property
    def consumed(self) -> int:
        """总消费 = 分配 + 条目。"""

        return self.allocated_total + self.entries_total

    @property
    def remaining(self) -> int:
        """剩余 token 预算。"""

        return max(0, self.total_budget - self.consumed)

    @property
    def over_budget(self) -> bool:
        """是否超出预算。"""

        return self.consumed > self.total_budget

    @property
    def usage_ratio(self) -> float:
        """预算使用比例（0.0-1.0）。"""

        if self.total_budget <= 0:
            return 1.0

        return min(1.0, self.consumed / self.total_budget)

    def truncate(
        self,
        strategy: TruncationStrategy = TruncationStrategy.OLDEST_FIRST,
    ) -> list[BudgetEntry]:
        """超预算截断：按策略丢弃条目直到预算内。





        Args:


            strategy: 截断策略。





        Returns:


            被丢弃的条目列表。


        """

        with self._lock:
            if not self.over_budget:
                return []

            excess = self.consumed - self.total_budget

            if strategy is TruncationStrategy.NEWEST_FIRST:
                sorted_entries = sorted(self.entries, key=lambda e: -e.priority)

            elif strategy is TruncationStrategy.OLDEST_FIRST:
                sorted_entries = list(self.entries)

            elif strategy is TruncationStrategy.SUMMARY_FIRST:
                sorted_entries = sorted(self.entries, key=lambda e: (e.priority, len(e.content)))

            elif strategy is TruncationStrategy.RELEVANCE_FIRST:
                sorted_entries = sorted(self.entries, key=lambda e: -e.priority)

            else:
                sorted_entries = list(self.entries)

            discarded: list[BudgetEntry] = []

            remaining_entries: list[BudgetEntry] = []

            freed = 0

            for entry in sorted_entries:
                if freed < excess:
                    freed += entry.tokens

                    discarded.append(entry)

                else:
                    remaining_entries.append(entry)

            self.entries = remaining_entries

            return discarded

    def get_by_key(self, key: str) -> BudgetEntry | None:
        """按 key 查找条目。"""

        with self._lock:
            for entry in self.entries:
                if entry.key == key:
                    return entry

        return None

    def reset(self) -> None:
        """重置所有分配和条目。"""

        with self._lock:
            self.allocation.clear()

            self.entries.clear()

            self._alloc_counter = 0


@dataclass
class QuotaTracker:
    """配额使用追踪器——按租户/会话维度追踪 budget 消耗。





    与 ContextBudget 配合使用：ContextBudget 管理即时预算，


    QuotaTracker 管理跨会话/长周期的配额消耗统计。


    """

    total_quota: int = 0

    consumed: int = 0

    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)

    def consume(self, tokens: int) -> bool:
        """消耗配额。返回 True 表示成功，False 表示配额不足。"""

        with self._lock:
            if self.total_quota > 0 and self.consumed + tokens > self.total_quota:
                return False

            self.consumed += tokens

            return True

    @property
    def remaining(self) -> int:
        """剩余配额。"""

        with self._lock:
            return max(0, self.total_quota - self.consumed)

    @property
    def exhausted(self) -> bool:
        """配额是否耗尽。"""

        return self.total_quota > 0 and self.consumed >= self.total_quota

    def reset(self) -> None:
        """重置配额追踪器。"""

        with self._lock:
            self.consumed = 0


__all__ = [
    "BudgetEntry",
    "ContextBudget",
    "QuotaTracker",
    "TruncationStrategy",
]
