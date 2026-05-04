"""
ContextRotModel — Transformer n² 注意力衰减数学模型
====================================================
Task ID     : beta a — ContextRot 显式建模
safety_level: M (experimental)
Depends     : context_budget_tracker.py

背景
----
Anthropic 2025 上下文工程白皮书指出：Transformer 的 pairwise attention
是 n² 复杂度 — 上下文越长，每对 token 间注意力越稀薄。"LLM 像人类有
工作记忆上限 — 每新增 token 都消耗注意力预算。"

ZephyrAlpha 的 ContextBudgetTracker 只追踪 Token 数量（容量边界），
不追踪注意力稀释（质量边界）。本模块填补这个缺口。

数学模型
--------
effective_attention(N) = (N_ref / N)^k

其中：
  N     = 当前上下文 token 数
  N_ref = 参考上下文大小（模型训练/评测时的典型 context window 中位值）
  k     = 衰减指数（校准参数，默认 0.5 — n² 的平方根特征）

当 N = N_ref 时，effective_attention = 1.0（满注意力）
当 N → ∞ 时，effective_attention → 0

设计决策 DD7：幂函数 n^{-k} — 比一刀切阈值更能反映 Transformer 的
soft attention sparsity 特性。

使用示例
--------
    model = ContextRotModel(ref_tokens=4000, k=0.5)
    score = model.evaluate(current_tokens=12000)
    if score < model.low_attention_threshold:
        trigger_eager_compression()
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import ClassVar

__all__ = [
    "AttentionScore",
    "ContextRotModel",
    "DEFAULT_ROT_PARAMS",
]

DEFAULT_ROT_PARAMS: dict[str, float] = {
    "ref_tokens": 4000.0,
    "k": 0.5,
    "warn_attention": 0.50,
    "low_attention": 0.30,
    "critical_attention": 0.15,
}


@dataclass(frozen=True)
class AttentionScore:
    """单次注意力评估结果。

    Attributes
    ----------
    effective_attention : float
        有效注意力分数 (0.0 ~ 1.0)。
    current_tokens : int
        当前上下文 Token 数。
    ref_tokens : int
        参考 Token 数。
    k : float
        衰减指数。
    level : str
        注意力等级：normal / warn / low / critical。
    """

    effective_attention: float
    current_tokens: int
    ref_tokens: int
    k: float
    level: str


class ContextRotModel:
    """n² 注意力衰减模型 — 单例服务。

    Parameters
    ----------
    ref_tokens : int
        参考上下文大小（默认 4000）。
    k : float
        衰减指数（默认 0.5，n² 平方根特征）。
    warn_attention : float
        警告阈值，低于此值触发 attention_warn（默认 0.50）。
    low_attention : float
        低注意力阈值，低于此值触发 attention_low（默认 0.30）。
    critical_attention : float
        危急阈值，低于此值触发 attention_critical（默认 0.15）。
    """

    _instance: ClassVar[ContextRotModel | None] = None
    _lock: ClassVar[RLock] = RLock()

    def __init__(
        self,
        ref_tokens: int = 4000,
        k: float = 0.5,
        warn_attention: float = 0.50,
        low_attention: float = 0.30,
        critical_attention: float = 0.15,
    ) -> None:
        if ref_tokens <= 0:
            raise ValueError("ref_tokens must be positive")
        if k <= 0.0:
            raise ValueError("k must be positive (n² 衰减特征)")
        if not (critical_attention < low_attention < warn_attention <= 1.0):
            raise ValueError(
                f"Thresholds must satisfy critical({critical_attention}) < "
                f"low({low_attention}) < warn({warn_attention}) <= 1.0"
            )
        self._ref_tokens = ref_tokens
        self._k = k
        self._warn_attention = warn_attention
        self._low_attention = low_attention
        self._critical_attention = critical_attention

    # ------------------------------------------------------------------
    # 单例接口
    # ------------------------------------------------------------------

    @classmethod
    def instance(cls, **kwargs: float) -> ContextRotModel:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(**{k: int(v) if k == "ref_tokens" else v for k, v in kwargs.items()} if kwargs else {})
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        with cls._lock:
            cls._instance = None

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    @property
    def ref_tokens(self) -> int:
        return self._ref_tokens

    @property
    def k(self) -> float:
        return self._k

    @property
    def thresholds(self) -> dict[str, float]:
        return {
            "warn": self._warn_attention,
            "low": self._low_attention,
            "critical": self._critical_attention,
        }

    def effective_attention(self, current_tokens: int) -> float:
        """计算给定 Token 数下的有效注意力分数。

        公式：effective_attention(N) = (N_ref / N)^k

        Parameters
        ----------
        current_tokens : int
            当前上下文 Token 总数。

        Returns
        -------
        float
            effective_attention 分数 (0.0 ~ 1.0)。
            N ≤ N_ref 时返回 1.0（满注意力）。
        """
        if current_tokens <= 0:
            return 1.0
        if current_tokens <= self._ref_tokens:
            return 1.0
        ratio = self._ref_tokens / current_tokens
        return ratio ** self._k

    def evaluate(self, current_tokens: int) -> AttentionScore:
        """全面评估当前上下文的注意力质量。

        Returns
        -------
        AttentionScore
            注意力分数 + 等级。
        """
        score = self.effective_attention(current_tokens)
        level = self._classify(score)
        return AttentionScore(
            effective_attention=score,
            current_tokens=current_tokens,
            ref_tokens=self._ref_tokens,
            k=self._k,
            level=level,
        )

    def is_healthy(self, current_tokens: int) -> bool:
        """注意力是否在健康范围（≥ warn 阈值）。"""
        return self.effective_attention(current_tokens) >= self._warn_attention

    def needs_compression(self, current_tokens: int) -> bool:
        """是否需要紧急压缩（< low 阈值）。"""
        return self.effective_attention(current_tokens) < self._low_attention

    def recommended_max_tokens(self) -> int:
        """推荐的最大 Token 数（对应 warn 阈值）。
        
        N_max = N_ref / (warn_attention)^(1/k)
        """
        if self._warn_attention <= 0.0:
            return self._ref_tokens
        return int(self._ref_tokens / (self._warn_attention ** (1.0 / self._k)))

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _classify(self, score: float) -> str:
        if score >= self._warn_attention:
            return "normal"
        if score >= self._low_attention:
            return "warn"
        if score >= self._critical_attention:
            return "low"
        return "critical"
