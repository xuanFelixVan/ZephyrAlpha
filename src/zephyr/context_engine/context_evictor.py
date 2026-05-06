"""
ContextEvictor — 三维排序上下文逐出器
====================================
Task ID     : beta a — Eviction Chain
safety_level: M (experimental)
Depends     : context_budget_tracker.py, context_rot_model.py

背景
----
当 ContextBudgetTracker 触发 L2_THROTTLE / L3_HARD_STOP 时，需要从
已注入的上下文中逐出部分内容以释放 Token 预算。简单 FIFO/LRU 是语义盲的
——可能把"关键安全失败经验"逐出，把"无关 header"保留。

本模块按三维排序逐出：优先级 × 新鲜度 × 相关性

设计决策 DD9：三维排序 Eviction

三维权重（可校准）
------------------
priority_weight  : 防止关键安全/失败经验被逐出
freshness_weight : created_at 越新权重越高（Windsurf Freshness Decay）
relevance_weight : 与当前 intent 的相关性分数

逐出分数 = 1 / (排序得分) — 得分最低的先被逐出

使用示例
--------
    evictor = ContextEvictor()
    blocks = [
        ContextBlock(..., priority=PriorityLevel.CRITICAL, freshness=0.9, relevance=0.8),
        ContextBlock(..., priority=PriorityLevel.NORMAL, freshness=0.1, relevance=0.3),
    ]
    kept, removed = evictor.evict(blocks, token_budget=2000)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import IntEnum
from threading import RLock
from typing import ClassVar

from pydantic import BaseModel, Field

from zephyr.shared.schemas import BASE_CONFIG

__all__ = [
    "PriorityLevel",
    "ContextBlock",
    "EvictionResult",
    "ContextEvictor",
    "DEFAULT_EVICTION_WEIGHTS",
]

DEFAULT_EVICTION_WEIGHTS: dict[str, float] = {
    "priority_weight": 0.5,
    "freshness_weight": 0.2,
    "relevance_weight": 0.3,
}


class PriorityLevel(IntEnum):
    """上下文块的优先级 — 控制逐出时的保留顺序。

    数值越大优先级越高，越难被逐出。
    """

    LOW = 10
    NORMAL = 50
    HIGH = 80
    CRITICAL = 100
    PINNED = 255


class ContextBlock(BaseModel):
    """单个上下文块 — ContextInjector 注入的最小单位。

    Attributes
    ----------
    block_id : str
        唯一标识符。
    content : str
        上下文文本内容。
    token_estimate : int
        Token 估算（chars ÷ 4）。
    priority : PriorityLevel
        优先级 — CRITICAL / PINNED 除非超 budget 一定比例不会被逐出。
    source : str
        知识来源（KE id / blueprint id / 规则文件路径）。
    provenance : str
        溯源信息（{blueprint_id}:{§}/{ke_id}/{rule_id}）。
    freshness : float
        新鲜度分数 (0.0 ~ 1.0)，created_at 越新越高。
    relevance : float
        与当前 intent 的相关性分数 (0.0 ~ 1.0)。
    created_at : float
        UNIX 时间戳，用于 freshness 衰减。
    """

    model_config = BASE_CONFIG

    block_id: str = Field(min_length=1, description="唯一标识符")
    content: str = Field(min_length=1, description="上下文文本内容")
    token_estimate: int = Field(default=0, ge=0, description="Token 估算")
    priority: PriorityLevel = Field(default=PriorityLevel.NORMAL, description="优先级")
    source: str = Field(default="", description="知识来源")
    provenance: str = Field(default="", description="溯源信息 {blueprint_id}:{§}/{ke_id}")
    freshness: float = Field(default=1.0, ge=0.0, le=1.0, description="新鲜度分数")
    relevance: float = Field(default=0.5, ge=0.0, le=1.0, description="相关性分数")
    created_at: float = Field(default_factory=time.time, description="创建时间戳")

    @property
    def is_pinned(self) -> bool:
        return self.priority == PriorityLevel.PINNED

    @property
    def is_mandatory(self) -> bool:
        return self.priority >= PriorityLevel.CRITICAL

    def compute_eviction_score(
        self,
        weights: dict[str, float] | None = None,
    ) -> float:
        """计算逐出分数 = 三维加权。

        得分越高 → 越容易被逐出。
        即 score = priority_weight*(1 - norm_priority) + freshness_weight*(1 - freshness) + relevance_weight*(1 - relevance)
        """
        w = weights or DEFAULT_EVICTION_WEIGHTS
        pw = w.get("priority_weight", 0.5)
        fw = w.get("freshness_weight", 0.2)
        rw = w.get("relevance_weight", 0.3)

        norm_priority = self.priority / PriorityLevel.PINNED
        return pw * (1.0 - norm_priority) + fw * (1.0 - self.freshness) + rw * (1.0 - self.relevance)


@dataclass(frozen=True)
class EvictionResult:
    """逐出结果。

    Attributes
    ----------
    kept : list[ContextBlock]
        保留的上下文块列表。
    removed : list[ContextBlock]
        已逐出的上下文块列表。
    before_tokens : int
        逐出前 Token 总数。
    after_tokens : int
        逐出后 Token 总数。
    budget : int
        Token 预算上限。
    pinned_blocks : int
        保留的 PINNED 块数量。
    mandatory_blocks : int
        保留的 CRITICAL 块数量。
    """

    kept: list[ContextBlock] = field(default_factory=list)
    removed: list[ContextBlock] = field(default_factory=list)
    before_tokens: int = 0
    after_tokens: int = 0
    budget: int = 0
    pinned_blocks: int = 0
    mandatory_blocks: int = 0

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    @property
    def compression_ratio(self) -> float:
        if self.before_tokens == 0:
            return 0.0
        return 1.0 - (self.after_tokens / self.before_tokens)


class ContextEvictor:
    """三维排序上下文逐出器 — 单例服务。

    FIFO/LRU 是语义盲的 — 关键经验可能被逐出。
    按优先级 × 新鲜度 × 相关性三维排序逐出。

    Parameters
    ----------
    weights : dict[str, float] | None
        三维权重覆盖。默认 priority=0.5, freshness=0.2, relevance=0.3。
    hard_overrun_ratio : float
        硬超预算比例 — 若必须逐出 mandatory 块的最低 Token 使用比例。
        PINNED 块始终保留。
    """

    _instance: ClassVar[ContextEvictor | None] = None
    _lock: ClassVar[RLock] = RLock()

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        hard_overrun_ratio: float = 1.0,
    ) -> None:
        self._weights = {**DEFAULT_EVICTION_WEIGHTS, **(weights or {})}
        self._hard_overrun_ratio = hard_overrun_ratio
        self._normalize_weights()

    def _normalize_weights(self) -> None:
        total = sum(self._weights.values())
        if total > 0:
            for k in self._weights:
                self._weights[k] /= total

    # ------------------------------------------------------------------
    # 单例接口
    # ------------------------------------------------------------------

    @classmethod
    def instance(cls, **kwargs: object) -> ContextEvictor:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(
                    **{k: v for k, v in kwargs.items() if k in ("weights", "hard_overrun_ratio")} if kwargs else {}
                )
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        with cls._lock:
            cls._instance = None

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    @property
    def weights(self) -> dict[str, float]:
        return dict(self._weights)

    def evict(
        self,
        blocks: list[ContextBlock],
        token_budget: int,
    ) -> EvictionResult:
        """按三维排序逐出上下文块至 Token 预算内。

        Algorithm
        --------
        1. 统计 total tokens
        2. 若 ≤ budget — 全保留
        3. 按逐出分数升序排序 → 从"最该走"开始移除
        4. PINNED 块始终保留
        5. CRITICAL 块仅在 hard_overrun_ratio 触发后才允许逐出

        Parameters
        ----------
        blocks : list[ContextBlock]
            待逐出的上下文块列表。
        token_budget : int
            Token 预算上限。

        Returns
        -------
        EvictionResult
            逐出结果。
        """
        if not blocks:
            return EvictionResult(budget=token_budget)

        total_tokens = sum(b.token_estimate for b in blocks)
        if total_tokens <= token_budget:
            return EvictionResult(
                kept=list(blocks),
                before_tokens=total_tokens,
                after_tokens=total_tokens,
                budget=token_budget,
                pinned_blocks=sum(1 for b in blocks if b.is_pinned),
                mandatory_blocks=sum(1 for b in blocks if b.is_mandatory),
            )

        sorted_blocks = sorted(blocks, key=lambda b: b.compute_eviction_score(self._weights))

        kept: list[ContextBlock] = []
        removed: list[ContextBlock] = []
        current_tokens = 0

        for block in sorted_blocks:
            if block.is_pinned:
                kept.append(block)
                current_tokens += block.token_estimate
                continue

            would_exceed = current_tokens + block.token_estimate > token_budget
            if would_exceed and block.is_mandatory:
                critical_ratio = current_tokens / token_budget if token_budget > 0 else 1.0
                if critical_ratio >= self._hard_overrun_ratio:
                    removed.append(block)
                    continue

            if would_exceed:
                removed.append(block)
            else:
                kept.insert(0, block)
                current_tokens += block.token_estimate

        return EvictionResult(
            kept=kept,
            removed=removed,
            before_tokens=total_tokens,
            after_tokens=sum(b.token_estimate for b in kept),
            budget=token_budget,
            pinned_blocks=sum(1 for b in kept if b.is_pinned),
            mandatory_blocks=sum(1 for b in kept if b.is_mandatory),
        )
