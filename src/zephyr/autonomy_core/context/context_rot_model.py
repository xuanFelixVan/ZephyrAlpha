# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §1.1
# [MODULE] zephyr.autonomy_core.context.context_rot_model
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS] tests/context/test_context_rot_model_unit.py; tests/autonomy/test_mgmt_context_rot_model.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] effective_attention(n)=1.0 if n<=ref_tokens else ref_tokens/(ref_tokens+k*(n-ref_tokens)); warn>low>critical
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on ref_tokens<=0, k<=0, or threshold ordering violation
# [TESTS] tests/context/test_context_rot_model_unit.py; tests/autonomy/test_mgmt_context_rot_model.py
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
context_rot_model.py — Context Rot 注意力衰减数学模型
======================================================
模拟 LLM 上下文腐烂现象：随着上下文 token 数增长超过参考阈值，
模型有效注意力按调和衰减曲线下降。作为 context_evictor 和
budget_tracker 的数学基础。

公式::

    effective_attention(n) = 1.0                                  if n <= ref_tokens
                           = ref_tokens / (ref_tokens + k*(n-ref_tokens))  otherwise

其中:
  - n: 当前上下文 token 数
  - ref_tokens: 参考阈值（在此长度内注意力为 1.0）
  - k: 衰减系数（越大衰减越快）

Singleton 支持：通过 ``ContextRotModel.instance()`` 获取共享实例，
``ContextRotModel.reset_instance()`` 重置（主要用于测试隔离）。
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import ClassVar

# 默认参数（NEW API）
REF_TOKENS_DEFAULT: int = 4000
K_DEFAULT: float = 0.5
WARN_ATTENTION_DEFAULT: float = 0.50
LOW_ATTENTION_DEFAULT: float = 0.30
CRITICAL_ATTENTION_DEFAULT: float = 0.15


@dataclass(frozen=True)
class AttentionScore:
    """上下文注意力评估结果。

    Attributes:
        current_tokens: 当前上下文 token 数。
        ref_tokens: 参考阈值。
        effective_attention: 有效注意力分数 (0.0~1.0)。
        level: 分级标签，``"normal"`` / ``"warn"`` / ``"low"`` / ``"critical"``。
    """

    current_tokens: int
    ref_tokens: int
    effective_attention: float
    level: str


class ContextRotModel:
    """Context Rot 注意力衰减数学模型。

    使用调和衰减曲线模拟 LLM 上下文腐烂现象。token 数在 ``ref_tokens``
    以内时注意力为 1.0；超过 ``ref_tokens`` 后按
    ``ref_tokens / (ref_tokens + k*(n-ref_tokens))`` 衰减。

    Using::

        model = ContextRotModel(ref_tokens=4000, k=0.5)
        if model.needs_compression(token_count=20000):
            max_tokens = model.recommended_max_tokens()
            # 压缩上下文至 max_tokens 以内

    Singleton::

        shared = ContextRotModel.instance(ref_tokens=8000)
        same = ContextRotModel.instance()  # 同一实例
        ContextRotModel.reset_instance()  # 重置（主要用于测试）
    """

    # Singleton state (class-level)
    _instance: ClassVar[ContextRotModel | None] = None
    _instance_lock: ClassVar[RLock] = RLock()

    def __init__(
        self,
        *,
        ref_tokens: int = REF_TOKENS_DEFAULT,
        k: float = K_DEFAULT,
        warn_attention: float = WARN_ATTENTION_DEFAULT,
        low_attention: float = LOW_ATTENTION_DEFAULT,
        critical_attention: float = CRITICAL_ATTENTION_DEFAULT,
    ) -> None:
        if ref_tokens <= 0:
            raise ValueError(f"ref_tokens must be positive, got {ref_tokens}")
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        # 阈值顺序约束：warn > low > critical
        if not (warn_attention > low_attention > critical_attention):
            raise ValueError(
                "threshold ordering violated: require warn_attention > "
                f"low_attention > critical_attention, got "
                f"warn={warn_attention}, low={low_attention}, "
                f"critical={critical_attention}"
            )

        self._ref_tokens = ref_tokens
        self._k = k
        self._warn_attention = warn_attention
        self._low_attention = low_attention
        self._critical_attention = critical_attention

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def ref_tokens(self) -> int:
        return self._ref_tokens

    @property
    def k(self) -> float:
        return self._k

    @property
    def thresholds(self) -> dict[str, float]:
        """注意力阈值字典（warn/low/critical）。"""
        return {
            "warn": round(self._warn_attention, 2),
            "low": round(self._low_attention, 2),
            "critical": round(self._critical_attention, 2),
        }

    # ------------------------------------------------------------------
    # Core math
    # ------------------------------------------------------------------
    def effective_attention(self, token_count: int) -> float:
        """计算给定 token 数下的有效注意力分数。

        Args:
            token_count: 当前上下文 token 数。

        Returns:
            有效注意力分数 (0.0~1.0)。``token_count <= ref_tokens`` 时为 1.0。
        """
        n = max(0, token_count)
        if n <= self._ref_tokens:
            return 1.0
        # ref_tokens / (ref_tokens + k * (n - ref_tokens))
        denom = self._ref_tokens + self._k * (n - self._ref_tokens)
        if denom <= 0:
            return 0.0
        return self._ref_tokens / denom

    def evaluate(self, token_count: int) -> AttentionScore:
        """评估给定 token 数并返回分级结果。

        Args:
            token_count: 当前上下文 token 数。

        Returns:
            ``AttentionScore`` 实例，包含 effective_attention 与 level。
        """
        score = self.effective_attention(token_count)
        if score >= self._warn_attention:
            level = "normal"
        elif score >= self._low_attention:
            level = "warn"
        elif score >= self._critical_attention:
            level = "low"
        else:
            level = "critical"
        return AttentionScore(
            current_tokens=max(0, token_count),
            ref_tokens=self._ref_tokens,
            effective_attention=score,
            level=level,
        )

    # ------------------------------------------------------------------
    # Health checks
    # ------------------------------------------------------------------
    def is_healthy(self, token_count: int) -> bool:
        """上下文是否健康（注意力 >= warn 阈值）。"""
        return self.effective_attention(token_count) >= self._warn_attention

    def needs_compression(self, token_count: int) -> bool:
        """是否需要压缩上下文（注意力 < warn 阈值）。"""
        return self.effective_attention(token_count) < self._warn_attention

    def recommended_max_tokens(self) -> int:
        """推荐的最大 token 数（注意力不低于 0.50 的上界）。

        通过反推公式求解：``ref_tokens / (ref_tokens + k*(n-ref_tokens)) >= 0.50``
        解为 ``n <= ref_tokens + ref_tokens / k``（当 0.50 < 1.0 时）。

        Returns:
            整数 token 上界，保证 ``effective_attention(ret) >= 0.50``。
        """
        # 当目标 attention = 0.5 时:
        #   ref_tokens / (ref_tokens + k*(n-ref_tokens)) = 0.5
        #   => ref_tokens + k*(n-ref_tokens) = 2*ref_tokens
        #   => k*(n-ref_tokens) = ref_tokens
        #   => n = ref_tokens + ref_tokens / k
        target = 0.50
        if target >= 1.0:
            return self._ref_tokens
        # n_max = ref_tokens * (1 + (1 - target) / (target * k))
        # 由 target = ref / (ref + k*(n-ref)) 解出:
        #   ref + k*(n-ref) = ref / target
        #   k*(n-ref) = ref/target - ref = ref*(1-target)/target
        #   n = ref + ref*(1-target)/(target*k) = ref * (1 + (1-target)/(target*k))
        n_max = self._ref_tokens * (1.0 + (1.0 - target) / (target * self._k))
        # 向下取整确保 effective_attention(n_max) >= target
        ret = int(n_max)
        # 双重校验：若因浮点误差导致越界，递减直到满足
        while ret > self._ref_tokens and self.effective_attention(ret) < target:
            ret -= 1
        return ret

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------
    @classmethod
    def instance(
        cls,
        *,
        ref_tokens: int = REF_TOKENS_DEFAULT,
        k: float = K_DEFAULT,
        warn_attention: float = WARN_ATTENTION_DEFAULT,
        low_attention: float = LOW_ATTENTION_DEFAULT,
        critical_attention: float = CRITICAL_ATTENTION_DEFAULT,
    ) -> ContextRotModel:
        """获取共享单例实例。

        首次调用时按参数创建实例；后续调用忽略参数并返回已有实例。
        测试中请使用 ``reset_instance()`` 清理状态。
        """
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls(
                    ref_tokens=ref_tokens,
                    k=k,
                    warn_attention=warn_attention,
                    low_attention=low_attention,
                    critical_attention=critical_attention,
                )
            return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例（主要用于测试隔离）。"""
        with cls._instance_lock:
            cls._instance = None
