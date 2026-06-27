# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.token_budget
# [DOMAIN] D-AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS] zephyr.infrastructure.shared_services.observability_02.token_utils; zephyr.autonomy_core.*
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_token_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
token_budget.py — Token 估算工具 SSoT

根因修复：此前 _estimate_tokens() 在 3 个文件中重复定义，
且存在微差（空字符串处理不一致），说明各自演化已产生分歧。

对标：
  - OpenAI tiktoken: token 计算应统一入口
  - LangChain: token 估算使用统一工具函数
"""

DEFAULT_CONTEXT_TOKEN_BUDGET: int = 8000

from dataclasses import dataclass
from enum import Enum


class TokenBudgetTier(Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


BUDGET_CAPS: dict[TokenBudgetTier, int] = {
    TokenBudgetTier.L1: 500,
    TokenBudgetTier.L2: 1500,
    TokenBudgetTier.L3: 8000,
}

DEGRADED_THRESHOLD: int = 7200


@dataclass
class BudgetState:
    level: TokenBudgetTier = TokenBudgetTier.L1
    cap: int = 500
    consumed: int = 0
    degraded: bool = False


class TokenBudgetManager:
    def __init__(self, session_id: str = "") -> None:
        self.session_id = session_id
        self._level = TokenBudgetTier.L1
        self._cap = BUDGET_CAPS[self._level]
        self._consumed = 0

    @property
    def level(self) -> TokenBudgetTier:
        return self._level

    @property
    def cap(self) -> int:
        return self._cap

    @property
    def consumed(self) -> int:
        return self._consumed

    @property
    def remaining(self) -> int:
        return self._cap - self._consumed

    @property
    def degraded(self) -> bool:
        ratio = self._consumed / self._cap if self._cap > 0 else 0
        return ratio >= 0.9

    def set_level(self, level: TokenBudgetTier) -> None:
        self._level = level
        self._cap = BUDGET_CAPS[level]

    def consume(self, tokens: int) -> bool:
        if self._consumed + tokens > self._cap:
            return False
        self._consumed += tokens
        return True

    def can_consume(self, tokens: int) -> bool:
        return self._consumed + tokens <= self._cap

    def reset(self) -> None:
        self._consumed = 0

    def to_dict(self) -> dict:
        return {
            "level": self._level.value,
            "cap": self._cap,
            "consumed": self._consumed,
            "remaining": self.remaining,
            "degraded": self.degraded,
            "usage_ratio": self._consumed / self._cap if self._cap > 0 else 0,
        }


def estimate_tokens(text: str) -> int:
    """估算文本的 token 数量。

    使用简单的 1 token ≈ 4 字符启发式估算。
    对于中文等非拉丁语系，此估算偏低，但作为预算控制足够。

    Args:
        text: 待估算的文本字符串。空字符串返回 0。

    Returns:
        估算的 token 数量（≥ 0）。
    """
    if not text:
        return 0
    return max(len(text) // 4, 1)


__all__ = [
    "BUDGET_CAPS",
    "DEFAULT_CONTEXT_TOKEN_BUDGET",
    "DEGRADED_THRESHOLD",
    "BudgetState",
    "TokenBudgetManager",
    "TokenBudgetTier",
    "estimate_tokens",
]
