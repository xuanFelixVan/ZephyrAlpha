# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_rot_model
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_context_rot_model | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
context_rot_model.py — n² Attention 衰减数学模型 (DD7, TASK-014 beta a)
=====================================================================
模拟上下文的注意力衰减曲线，作为 context_evictor 和 budget_tracker 的
数学基础。authored: 2026-05-06.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC

UTC = UTC

K_DEFAULT: float = 0.35
BASE_TOKENS: float = 250.0


@dataclass(frozen=True)
class ContextDecayResult:
    """上下文衰减计算结果。"""

    context_id: str
    token_count: int
    age_seconds: float
    decay_factor: float  # 0.0~1.0, 1.0=new, 0.0=gone
    effective_weight: float
    recommendation: str  # "keep" | "consider_evict" | "evict"


class ContextRotModel:
    """n² 注意力衰减数学模型 (DD7)。

    decay = (1 - age / max_age)^2 · base / (base + n · k)
    where:
      - age: 自注入以来的秒数
      - max_age: 最大存活时间 (默认 3600s = 1h)
      - n: token_count
      - base: 基准 token 数 (默认 250)
      - k: 衰减指数 (默认 0.35)

    Using::

        model = ContextRotModel(max_age_s=1800)
        result = model.compute_decay("KE-005", token_count=200, age_seconds=600)
        if result.recommendation == "evict":
            print(f"Evicting {result.context_id}")
    """

    def __init__(
        self,
        *,
        max_age_s: float = 1800.0,
        k: float = K_DEFAULT,
        base_tokens: float = BASE_TOKENS,
    ) -> None:
        self._max_age_s = max_age_s
        self._k = k
        self._base_tokens = base_tokens

    def compute_decay(
        self,
        context_id: str,
        token_count: int,
        age_seconds: float,
    ) -> ContextDecayResult:
        n_tokens = max(1, token_count)
        age = max(0.0, min(age_seconds, self._max_age_s))
        age_factor = (1.0 - age / self._max_age_s) ** 2
        n_factor = self._base_tokens / (self._base_tokens + n_tokens * self._k)
        decay = age_factor * n_factor

        effective = max(0.0, decay)

        if effective > 0.5:
            rec = "keep"
        elif effective > 0.15:
            rec = "consider_evict"
        else:
            rec = "evict"

        return ContextDecayResult(
            context_id=context_id,
            token_count=n_tokens,
            age_seconds=age,
            decay_factor=round(effective, 4),
            effective_weight=round(effective, 4),
            recommendation=rec,
        )

    def batch_compute(
        self,
        items: list[tuple[str, int, float]],
    ) -> list[ContextDecayResult]:
        return [self.compute_decay(cid, tokens, age) for cid, tokens, age in items]

    @property
    def max_age_s(self) -> float:
        return self._max_age_s

    @property
    def k(self) -> float:
        return self._k
