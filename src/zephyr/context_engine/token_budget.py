"""
三级 Token 预算管理器（Token Budget Manager）

依据：MOD-MASTER-001 蓝图 §0.1 Token 预算
实现 L1(500)/L2(1500)/L3(8000) 三级预算控制。

功能：
1. 运行时切换预算级别
2. 追踪每次 context build 的 token 消耗
3. 超过 7200(90% L3)时自动标记 degraded=true
4. 按预算级别限制 context 大小
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import IntEnum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BudgetLevel(IntEnum):
    L1 = 1
    L2 = 2
    L3 = 3


BUDGET_CAPS: dict[BudgetLevel, int] = {
    BudgetLevel.L1: 500,
    BudgetLevel.L2: 1500,
    BudgetLevel.L3: 8000,
}

BUDGET_LABELS: dict[BudgetLevel, str] = {
    BudgetLevel.L1: "紧急 — 新 AI session 冷启动",
    BudgetLevel.L2: "标准 — 开发跨系统功能",
    BudgetLevel.L3: "完整 — 架构审查 / 新系统接入",
}

DEGRADED_RATIO: float = 0.90
DEGRADED_THRESHOLD: int = 7200

TYPE_BUDGET_ALLOCATION: dict[str, dict] = {
    "ke_entries": {
        "token_budget": 3000,
        "priority": "highest",
        "description": "知识条目——历史经验",
    },
    "vibe_rules": {
        "token_budget": 2000,
        "priority": "high",
        "description": "规则/策略——合规约束",
    },
    "blueprints": {
        "token_budget": 2000,
        "priority": "medium",
        "description": "蓝图——架构参考",
    },
    "runtime_logs": {
        "token_budget": 1000,
        "priority": "low",
        "description": "运行时日志",
    },
}

TOTAL_TOKEN_BUDGET: int = 8000


class BudgetState(BaseModel):
    level: BudgetLevel = BudgetLevel.L1
    cap: int = 500
    consumed: int = 0
    degraded: bool = False
    session_id: str = ""
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TokenBudgetManager:
    def __init__(self, session_id: str = ""):
        self._state = BudgetState(
            level=BudgetLevel.L1,
            cap=BUDGET_CAPS[BudgetLevel.L1],
            session_id=session_id,
        )
        self._history: list[int] = []

    @property
    def state(self) -> BudgetState:
        return self._state

    @property
    def consumed(self) -> int:
        return self._state.consumed

    @property
    def cap(self) -> int:
        return self._state.cap

    @property
    def remaining(self) -> int:
        return max(0, self._state.cap - self._state.consumed)

    @property
    def usage_ratio(self) -> float:
        if self._state.cap == 0:
            return 1.0
        return self._state.consumed / self._state.cap

    @property
    def degraded(self) -> bool:
        return self._state.degraded

    @property
    def level(self) -> BudgetLevel:
        return self._state.level

    def set_level(self, level: BudgetLevel) -> None:
        cap = BUDGET_CAPS[level]
        old_level = self._state.level
        self._state.level = level
        self._state.cap = cap
        self._state.last_updated = datetime.now(timezone.utc)
        self._check_degraded()
        logger.info(
            "Token budget level changed: %s(%d) → %s(%d)",
            BUDGET_LABELS.get(old_level, str(old_level)),
            BUDGET_CAPS.get(old_level, 0),
            BUDGET_LABELS.get(level, str(level)),
            cap,
        )

    def consume(self, tokens: int) -> bool:
        new_total = self._state.consumed + tokens
        if new_total > self._state.cap:
            logger.warning(
                "Token budget exceeded: %d/%d (attempted +%d)",
                self._state.consumed,
                self._state.cap,
                tokens,
            )
            self._state.consumed = self._state.cap
            self._state.degraded = True
            self._state.last_updated = datetime.now(timezone.utc)
            return False

        self._state.consumed = new_total
        self._history.append(tokens)
        self._state.last_updated = datetime.now(timezone.utc)
        self._check_degraded()
        return True

    def can_consume(self, tokens: int) -> bool:
        return (self._state.consumed + tokens) <= self._state.cap

    def reset(self) -> None:
        self._state.consumed = 0
        self._state.degraded = False
        self._state.last_updated = datetime.now(timezone.utc)
        self._history.clear()
        logger.info("Token budget reset for session %s", self._state.session_id)

    def _check_degraded(self) -> None:
        ratio = self.usage_ratio
        if ratio >= DEGRADED_RATIO:
            if not self._state.degraded:
                logger.warning(
                    "Token budget DEGRADED: %.1f%% consumed (%d/%d)",
                    ratio * 100,
                    self._state.consumed,
                    self._state.cap,
                )
            self._state.degraded = True
        else:
            self._state.degraded = False

    def to_dict(self) -> dict:
        return {
            "level": self._state.level.name,
            "level_value": self._state.level.value,
            "cap": self._state.cap,
            "consumed": self._state.consumed,
            "remaining": self.remaining,
            "usage_ratio": round(self.usage_ratio, 4),
            "degraded": self._state.degraded,
            "session_id": self._state.session_id,
        }
