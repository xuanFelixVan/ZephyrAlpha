# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.token_budget
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md;src/zephyr/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-RES_token_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PoolLevel(str, Enum):
    HOT = "hot"
    DOMAIN = "domain"
    COLD = "cold"


POOL_CAPS: Final[dict[PoolLevel, int]] = {
    PoolLevel.HOT: 800,
    PoolLevel.DOMAIN: 2000,
    PoolLevel.COLD: 8000,
}

POOL_LABELS: Final[dict[PoolLevel, str]] = {
    PoolLevel.HOT: "Hot Memory — 实时门禁状态 + 核心规则 (~800 tokens)",
    PoolLevel.DOMAIN: "Domain Triggers — 当前任务域依赖文档 (~2000 tokens)",
    PoolLevel.COLD: "Cold Memory — 全量背景被动检索 (~8000 tokens)",
}


class PoolState(BaseModel):
    level: PoolLevel
    cap: int
    consumed: int = 0
    allocations: int = 0
    overflow_count: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.cap - self.consumed)

    @property
    def utilization_ratio(self) -> float:
        if self.cap == 0:
            return 0.0
        return self.consumed / self.cap

    @property
    def is_exhausted(self) -> bool:
        return self.consumed >= self.cap

    def consume(self, amount: int) -> bool:
        if amount <= 0:
            return True
        if self.consumed + amount > self.cap:
            self.overflow_count += 1
            logger.warning(
                "Pool %s 溢出: consumed=%d + amount=%d > cap=%d",
                self.level.value,
                self.consumed,
                amount,
                self.cap,
            )
            return False
        self.consumed += amount
        self.allocations += 1
        return True

    def release(self, amount: int) -> None:
        self.consumed = max(0, self.consumed - amount)


class TokenManager:
    """三级 Token Budget 管理器。

    依据 SYS-MASTER-001 §0.3:
    - Hot Memory:  ~800 tokens  (每个 session 必读)
    - Domain Triggers: ~2000 tokens  (path_pattern 匹配触发)
    - Cold Memory:  ~8000 tokens  (主动查询)
    """

    def __init__(self) -> None:
        self._pools: dict[PoolLevel, PoolState] = {}
        self._total_allocated: int = 0
        self._degrated: bool = False
        self._created_at: datetime = datetime.now(UTC)

        for level in PoolLevel:
            cap = POOL_CAPS.get(level, 0)
            self._pools[level] = PoolState(level=level, cap=cap)

    @property
    def degraded(self) -> bool:
        return self._degrated

    @property
    def total_allocated(self) -> int:
        return self._total_allocated

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def pool(self, level: PoolLevel) -> PoolState:
        return self._pools[level]

    def hot_remaining(self) -> int:
        return self._pools[PoolLevel.HOT].remaining

    def domain_remaining(self) -> int:
        return self._pools[PoolLevel.DOMAIN].remaining

    def cold_remaining(self) -> int:
        return self._pools[PoolLevel.COLD].remaining

    def allocate(self, amount: int, level: PoolLevel) -> bool:
        """在指定池中分配 token，成功返回 True，溢出返回 False。"""
        pool = self._pools[level]
        if not pool.consume(amount):
            self._check_degraded()
            return False
        self._total_allocated += amount
        self._check_degraded()
        return True

    def allocate_hot(self, amount: int) -> bool:
        """在 Hot Memory 池分配。"""
        return self.allocate(amount, PoolLevel.HOT)

    def allocate_domain(self, amount: int) -> bool:
        """在 Domain Triggers 池分配。"""
        return self.allocate(amount, PoolLevel.DOMAIN)

    def allocate_cold(self, amount: int) -> bool:
        """在 Cold Memory 池分配。"""
        return self.allocate(amount, PoolLevel.COLD)

    def release_from(self, amount: int, level: PoolLevel) -> None:
        """释放指定池中的 token。"""
        self._pools[level].release(amount)
        self._total_allocated = max(0, self._total_allocated - amount)
        self._check_degraded()

    def _check_degraded(self) -> None:
        cold = self._pools[PoolLevel.COLD]
        ratio = cold.utilization_ratio
        if ratio >= 0.90:
            if not self._degrated:
                logger.warning(
                    "TokenBudget DEGRADED: utilization=%.1f%% consumed=%d/%d",
                    ratio * 100,
                    cold.consumed,
                    cold.cap,
                )
            self._degrated = True
        else:
            self._degrated = False

    def summary(self) -> dict[str, object]:
        """返回三级池状态摘要。"""
        return {
            "hot": {
                "cap": self._pools[PoolLevel.HOT].cap,
                "consumed": self._pools[PoolLevel.HOT].consumed,
                "remaining": self._pools[PoolLevel.HOT].remaining,
            },
            "domain": {
                "cap": self._pools[PoolLevel.DOMAIN].cap,
                "consumed": self._pools[PoolLevel.DOMAIN].consumed,
                "remaining": self._pools[PoolLevel.DOMAIN].remaining,
            },
            "cold": {
                "cap": self._pools[PoolLevel.COLD].cap,
                "consumed": self._pools[PoolLevel.COLD].consumed,
                "remaining": self._pools[PoolLevel.COLD].remaining,
                "utilization_ratio": self._pools[PoolLevel.COLD].utilization_ratio,
            },
            "total_allocated": self._total_allocated,
            "degraded": self._degrated,
        }

    def reset(self) -> None:
        """重置所有池（仅供测试）。"""
        for level in PoolLevel:
            cap = POOL_CAPS.get(level, 0)
            self._pools[level] = PoolState(level=level, cap=cap)
        self._total_allocated = 0
        self._degrated = False
        self._created_at = datetime.now(UTC)
