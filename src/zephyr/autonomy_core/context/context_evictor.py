# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_evictor
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
# [A_module] module_id=MOD-ORC_context_evictor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""context_evictor.py — 三维逐出器 (DD9, TASK-014 beta a)
===========================================================
优先级(priority) × 新鲜度(freshness) × 相关性(relevance) 三维加权排序，
当 token budget 超限时决定驱逐哪些上下文条目。

公式: score = w_p × (1 - priority_norm) + w_f × (1 - freshness) + w_r × (1 - relevance)
分数越高意味着越倾向于被逐出。
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class PriorityLevel(IntEnum):
    LOW = 10
    NORMAL = 100
    HIGH = 150
    CRITICAL = 200
    PINNED = 255


@dataclass
class ContextBlock:
    block_id: str
    content: str
    token_estimate: int = 0
    priority: PriorityLevel = PriorityLevel.NORMAL
    freshness: float = 0.5
    relevance: float = 0.5
    provenance: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_pinned(self) -> bool:
        return self.priority is PriorityLevel.PINNED

    @property
    def is_mandatory(self) -> bool:
        return self.priority in (PriorityLevel.PINNED, PriorityLevel.CRITICAL)

    def compute_eviction_score(self) -> float:
        _norm = self.priority.value / PriorityLevel.PINNED.value
        return 0.40 * (1.0 - _norm) + 0.35 * (1.0 - self.freshness) + 0.25 * (1.0 - self.relevance)


@dataclass
class EvictionResult:
    kept: list[ContextBlock]
    removed: list[ContextBlock]
    kept_count: int = 0
    removed_count: int = 0
    before_tokens: int = 0
    after_tokens: int = 0

    @property
    def compression_ratio(self) -> float:
        if self.before_tokens == 0:
            return 1.0
        return self.after_tokens / self.before_tokens


class ContextEvictor:
    """三维逐出器 (DD9)。

    公式: score = w_p × (1 - priority_norm) + w_f × (1 - freshness) + w_r × (1 - relevance)
    分数越高 → 越先被逐出。低分块优先保留。
    """

    _instance: ContextEvictor | None = None
    # 5.81.3 修复：Singleton 无 DCL, 并发首次调用会创建多个实例导致状态分叉
    _instance_lock: threading.Lock = threading.Lock()

    @classmethod
    def reset_instance(cls) -> None:
        with cls._instance_lock:
            cls._instance = None

    @classmethod
    def instance(cls, **kwargs: Any) -> ContextEvictor:
        # 5.81.3 修复：double-checked locking 防止并发创建多实例
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance

    def __init__(
        self,
        w_p: float = 0.40,
        w_f: float = 0.35,
        w_r: float = 0.25,
        weights: dict[str, float] | None = None,
    ) -> None:
        if weights is not None:
            self._wp = weights.get("priority_weight", 0.40)
            self._wf = weights.get("freshness_weight", 0.35)
            self._wr = weights.get("relevance_weight", 0.25)
        else:
            self._wp = w_p
            self._wf = w_f
            self._wr = w_r

    @property
    def weights(self) -> tuple[float, float, float]:
        return (self._wp, self._wf, self._wr)

    def evict(
        self,
        blocks: list[ContextBlock],
        token_budget: int,
    ) -> EvictionResult:
        pinned = [b for b in blocks if b.is_pinned]
        evictable = [b for b in blocks if not b.is_pinned]

        before_tokens = sum(b.token_estimate for b in blocks)

        for b in evictable:
            _norm = b.priority.value / PriorityLevel.PINNED.value
            b._score = self._wp * (1.0 - _norm) + self._wf * (1.0 - b.freshness) + self._wr * (1.0 - b.relevance)

        evictable.sort(key=lambda b: b._score)

        kept: list[ContextBlock] = list(pinned)
        removed: list[ContextBlock] = []
        remaining = token_budget - sum(b.token_estimate for b in pinned)

        for b in evictable:
            if remaining >= b.token_estimate:
                kept.append(b)
                remaining -= b.token_estimate
            else:
                removed.append(b)

        after_tokens = sum(b.token_estimate for b in kept)

        return EvictionResult(
            kept=kept,
            removed=removed,
            kept_count=len(kept),
            removed_count=len(removed),
            before_tokens=before_tokens,
            after_tokens=after_tokens,
        )
