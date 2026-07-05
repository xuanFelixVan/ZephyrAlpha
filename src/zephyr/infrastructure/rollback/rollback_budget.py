# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_budget
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_rollback_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackBudget — 回滚预算管理器。

依据: 蓝图 MOD-INF-021 §6.2 B55 + D-021-10

回滚操作消耗预算 token:
    日配额 / 并发限制 / 总预算上限。
    预算耗尽 → 切换 forward-fix 模式。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class BudgetStatus:
    daily_used: int
    daily_limit: int
    total_used: int
    total_limit: int
    current_concurrent: int
    max_concurrent: int
    available: bool
    daily_tokens_used: int = 0
    max_daily_tokens: int = 100000
    total_tokens_used: int = 0


@dataclass
class BudgetConsumeResult:
    allowed: bool
    reason: str
    remaining_daily: int
    remaining_total: int


class RollbackBudget:
    DAILY_LIMIT: int = 10
    TOTAL_LIMIT: int = 100
    MAX_CONCURRENT: int = 3
    MAX_DAILY_TOKENS: int = 100000
    BUDGET_LOG: str = ".zephyr/rollback_budget_log.jsonl"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._budget_path = self._project_root / self.BUDGET_LOG
        self._concurrent_count = 0

    def status(self) -> BudgetStatus:
        today = datetime.now(UTC).date()
        daily_used = 0
        total_used = 0
        daily_tokens = 0
        total_tokens = 0

        if self._budget_path.exists():
            with open(self._budget_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        ts = datetime.fromisoformat(entry["timestamp_utc"])
                        total_used += 1
                        tokens = entry.get("token_cost", 0)
                        total_tokens += tokens
                        if ts.date() == today:
                            daily_used += 1
                            daily_tokens += tokens
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

        available = (
            daily_used < self.DAILY_LIMIT
            and total_used < self.TOTAL_LIMIT
            and self._concurrent_count < self.MAX_CONCURRENT
            and daily_tokens < self.MAX_DAILY_TOKENS
        )

        return BudgetStatus(
            daily_used=daily_used,
            daily_limit=self.DAILY_LIMIT,
            total_used=total_used,
            total_limit=self.TOTAL_LIMIT,
            current_concurrent=self._concurrent_count,
            max_concurrent=self.MAX_CONCURRENT,
            available=available,
            daily_tokens_used=daily_tokens,
            max_daily_tokens=self.MAX_DAILY_TOKENS,
            total_tokens_used=total_tokens,
        )

    def consume(self, reason: str = "", token_cost: int = 0) -> BudgetConsumeResult:
        s = self.status()

        if s.daily_used >= s.daily_limit:
            return BudgetConsumeResult(
                allowed=False,
                reason=f"Daily limit reached ({s.daily_limit})",
                remaining_daily=0,
                remaining_total=s.total_limit - s.total_used,
            )

        if s.total_used >= s.total_limit:
            return BudgetConsumeResult(
                allowed=False,
                reason=f"Total limit reached ({s.total_limit})",
                remaining_daily=s.daily_limit - s.daily_used,
                remaining_total=0,
            )

        if s.current_concurrent >= s.max_concurrent:
            return BudgetConsumeResult(
                allowed=False,
                reason=f"Concurrent limit reached ({s.max_concurrent})",
                remaining_daily=s.daily_limit - s.daily_used,
                remaining_total=s.total_limit - s.total_used,
            )

        if s.daily_tokens_used + token_cost > s.max_daily_tokens:
            return BudgetConsumeResult(
                allowed=False,
                reason=f"Daily token limit reached ({s.max_daily_tokens})",
                remaining_daily=s.daily_limit - s.daily_used,
                remaining_total=s.total_limit - s.total_used,
            )

        entry = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "reason": reason,
            "token_cost": token_cost,
        }
        self._budget_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._budget_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        self._concurrent_count += 1

        return BudgetConsumeResult(
            allowed=True,
            reason=reason,
            remaining_daily=s.daily_limit - s.daily_used - 1,
            remaining_total=s.total_limit - s.total_used - 1,
        )

    def release(self) -> None:
        if self._concurrent_count > 0:
            self._concurrent_count -= 1

    @property
    def concurrent_count(self) -> int:
        return self._concurrent_count
