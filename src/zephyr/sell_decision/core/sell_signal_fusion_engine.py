# [BLUEPRINT] MOD-SELL-007 | docs/03_modules/_domain_sell_decision/sell_signal_fusion_engine/blueprint.md
# [MODULE] zephyr.sell_decision.core.sell_signal_fusion_engine
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.sell_decision.core.sell_signal_collector
# [CONSUMERS] MOD-SELL-008(仲裁器) ; MOD-SELL-009(紧迫度) ; D-POSITION(E-SELL-01) ; D-SIGNAL
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 综合意愿∈[0,1]; 融合置信度∈[0,1]; 多信号加权平均; 多时间框架共振×1.5; 一致性三档; 单标的异常隔离
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidFusionInputError
# [TESTS] tests/sell_decision/test_sell_signal_fusion_engine.py
# [A_module] module_id=MOD-SELL-007 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Sell Signal Fusion Engine — 卖出信号融合引擎 (MOD-SELL-007)

多卖出信号加权融合为综合卖出意愿(0~1)+融合置信度, 支持多时间框架共振增强。

融合算法 (D-SELL-DECISION §1.4 SELL-07):
    - 默认加权平均: willingness = Σ(confidence × weight × resonance) / Σ(weight × resonance)
    - 多时间框架共振: 同标的同方向多时间框架信号 → 权重 ×1.5 (v6.0)
    - 一致性检查: 同方向占比 >80%=HIGH / 50-80%=MEDIUM / <50%=LOW → 影响置信度

输出: FusedSellDecision(综合卖出意愿 + 融合置信度 + 触发信号 + 一致性), 喂给 SELL-08/09。

设计说明:
    - 消费 SELL-01 的 SellSignal(含 signal_type/timeframe/direction)
    - 默认 WeightedAverageFusion, FusionStrategy 协议可注入(贝叶斯/D-S 预留)
    - 属A类基础设施(加权融合+共振+一致性, 逻辑明确)

依据: D:\\临时工作区\\依赖图\\31-D-SELL-DECISION-卖出决策域.md §1.4 SELL-07, §4 E-SELL-01
SSoT: depgraph MOD-SELL-007
Version: 0.1.0
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Final, Protocol, runtime_checkable

from zephyr.sell_decision.core.sell_signal_collector import (
    SellDirection,
    SellSignal,
    SellSignalType,
    SignalTimeFrame,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "FusionMethod",
    "ConsistencyLevel",
    "FusedSellDecision",
    "SellSignalFusedEvent",
    "FusionStrategy",
    "WeightedAverageFusion",
    "SellSignalFusionEngine",
    "InvalidFusionInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class FusionMethod(str, Enum):
    """融合算法 (SELL-07)。"""

    WEIGHTED_AVG = "WEIGHTED_AVG"             # 加权平均(默认)
    BAYESIAN = "BAYESIAN"                     # 贝叶斯融合(预留)
    DEMPSTER_SHAFER = "DEMPSTER_SHAFER"       # D-S证据理论(预留)


class ConsistencyLevel(str, Enum):
    """信号一致性等级 (SELL-07)。"""

    HIGH = "HIGH"       # 同方向 >80%
    MEDIUM = "MEDIUM"   # 50-80%
    LOW = "LOW"         # <50%


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidFusionInputError(ZephyrBaseError):
    """融合输入数据非法(如空信号列表)。"""

    error_code = "ZA-SELL-0007"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FusedSellDecision:
    """融合卖出决策 (SELL-007 产出, 喂给 SELL-08/09 / D-POSITION)。

    Attributes:
        symbol: 标的代码
        willingness: 综合卖出意愿[0,1], 0=无意愿, 1=最大意愿
        confidence: 融合置信度[0,1], 受一致性影响
        contributing_signals: 贡献信号列表
        consistency: 信号一致性(HIGH/MEDIUM/LOW)
        fusion_method: 融合算法
        dominant_signal_type: 主导信号类型(权重最高)
        resonance_enhanced: 是否经多时间框架共振增强
        reason: 人类可读融合理由
        timestamp: 融合时间
    """

    symbol: str
    willingness: float
    confidence: float
    contributing_signals: list[SellSignal] = field(default_factory=list)
    consistency: ConsistencyLevel = ConsistencyLevel.MEDIUM
    fusion_method: FusionMethod = FusionMethod.WEIGHTED_AVG
    dominant_signal_type: SellSignalType = SellSignalType.TECHNICAL
    resonance_enhanced: bool = False
    reason: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class SellSignalFusedEvent:
    """E-SELL-01 SellSignalFused 事件 (D-SELL §4)。

    卖出信号融合完成时发布, 消费者: D-POSITION, D-SIGNAL。
    """

    decision: FusedSellDecision
    timestamp: datetime
    context_snapshot: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 融合策略协议 (可注入)
# ──────────────────────────────────────────────────────────────────────────────


@runtime_checkable
class FusionStrategy(Protocol):
    """融合策略协议——默认加权平均, 贝叶斯/D-S 可选注入。

    实现方需返回 (willingness, confidence) 元组。
    """

    def fuse(self, sigs: list[SellSignal], weights: list[float]) -> tuple[float, float]:
        """融合信号→(综合意愿, 融合置信度)。

        Args:
            sigs: 信号列表
            weights: 每信号权重(已含共振增强)

        Returns:
            (willingness[0,1], confidence[0,1])
        """
        ...


# ──────────────────────────────────────────────────────────────────────────────
# 默认加权平均融合策略
# ──────────────────────────────────────────────────────────────────────────────


# signal_type 默认权重 (D-SELL §1.4, 强制类权重高)
_DEFAULT_TYPE_WEIGHTS: dict[SellSignalType, float] = {
    SellSignalType.MAIN_FORCE_DISTRIBUTION: 1.5,
    SellSignalType.BREAKOUT_FAILURE: 1.5,
    SellSignalType.FUNDAMENTAL: 1.2,
    SellSignalType.TECHNICAL: 1.0,
    SellSignalType.VOLUME_PRICE_DIVERGENCE: 1.0,
    SellSignalType.RELATIVE_STRENGTH: 0.8,
    SellSignalType.OPPORTUNITY_COST: 0.6,
    SellSignalType.TIME_STOP: 0.6,
}

# 多时间框架共振增强因子
_RESONANCE_BOOST = 1.5

# 一致性阈值
_HIGH_CONSISTENCY = 0.8
_MEDIUM_CONSISTENCY = 0.5

# 一致性→置信度因子
_CONSISTENCY_FACTOR: Final = {
    ConsistencyLevel.HIGH: 1.0,
    ConsistencyLevel.MEDIUM: 0.8,
    ConsistencyLevel.LOW: 0.5,
}


class WeightedAverageFusion:
    """加权平均融合策略(默认)。

    willingness = Σ(confidence × weight) / Σ(weight)
    confidence = willingness × consistency_factor
    """

    def __init__(self, type_weights: dict[SellSignalType, float] | None = None) -> None:
        self._type_weights = dict(type_weights) if type_weights is not None else dict(_DEFAULT_TYPE_WEIGHTS)

    def fuse(self, sigs: list[SellSignal], weights: list[float]) -> tuple[float, float]:
        if not sigs:
            return (0.0, 0.0)
        total_w = sum(weights)
        if total_w <= 0:
            return (0.0, 0.0)
        willingness = sum(s.confidence * w for s, w in zip(sigs, weights, strict=True)) / total_w
        willingness = min(max(willingness, 0.0), 1.0)
        # 置信度由 SellSignalFusionEngine 基于一致性计算, 这里返回原始意愿
        return (willingness, willingness)

    def type_weight(self, stype: SellSignalType) -> float:
        return self._type_weights.get(stype, 1.0)


# ──────────────────────────────────────────────────────────────────────────────
# 卖出信号融合引擎
# ──────────────────────────────────────────────────────────────────────────────


class SellSignalFusionEngine:
    """卖出信号融合引擎——多信号加权融合+共振增强+一致性检查。

    用法:
        engine = SellSignalFusionEngine()
        decisions = engine.fuse([
            SellSignal("000001.SZ", SellSignalType.MAIN_FORCE_DISTRIBUTION, SellDirection.CLEAR, 0.9),
            SellSignal("000001.SZ", SellSignalType.TECHNICAL, SellDirection.REDUCE, 0.6),
        ])
        for d in decisions:
            if d.willingness > 0.7:
                # 高卖出意愿

    Args:
        strategy: 融合策略(默认 WeightedAverageFusion)
        resonance_boost: 多时间框架共振增强因子(默认1.5)
        clock: 可选时间源(测试注入)
    """

    def __init__(
        self,
        strategy: FusionStrategy | None = None,
        resonance_boost: float = _RESONANCE_BOOST,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._strategy = strategy or WeightedAverageFusion()
        self._resonance_boost = resonance_boost
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._fused_callbacks: list[Callable[[SellSignalFusedEvent], None]] = []

    # ── 事件订阅 ──

    def on_fused(self, callback: Callable[[SellSignalFusedEvent], None]) -> None:
        """订阅 E-SELL-01 SellSignalFused 事件。"""
        self._fused_callbacks.append(callback)

    # ── 融合主入口 ──

    def fuse(
        self,
        sell_signals: list[SellSignal],
        now: datetime | None = None,
    ) -> list[FusedSellDecision]:
        """融合多卖出信号→综合卖出意愿。

        步骤: 按标的分组 → 每标的加权融合+共振增强+一致性检查 → 发布事件。

        Args:
            sell_signals: 卖出信号列表(来自 SELL-01)
            now: 融合时间(默认 clock())

        Returns:
            每个有信号的标的一条 FusedSellDecision(按 symbol 排序)
        """
        if not sell_signals:
            raise InvalidFusionInputError("sell_signals must not be empty")
        now = now or self._clock()

        by_symbol: dict[str, list[SellSignal]] = defaultdict(list)
        for sig in sell_signals:
            by_symbol[sig.symbol].append(sig)

        results: list[FusedSellDecision] = []
        for symbol in sorted(by_symbol.keys()):
            try:
                decision = self._fuse_one(symbol, by_symbol[symbol], now)
                results.append(decision)
                self._emit_event(decision, now)
            except Exception as exc:  # noqa: BLE001 — 单标的异常隔离
                logger.error("Fusion failed for %s: %s", symbol, exc, exc_info=True)
        return results

    # ── 单标的融合 ──

    def _fuse_one(self, symbol: str, sigs: list[SellSignal], now: datetime) -> FusedSellDecision:
        # 1. 计算每信号权重(类型权重 × 共振增强)
        weights = [self._signal_weight(s, sigs) for s in sigs]

        # 2. 融合策略计算意愿
        willingness, _raw_conf = self._strategy.fuse(sigs, weights)

        # 3. 一致性检查
        consistency = self._check_consistency(sigs)

        # 4. 置信度 = 意愿 × 一致性因子
        confidence = willingness * _CONSISTENCY_FACTOR[consistency]
        confidence = min(max(confidence, 0.0), 1.0)

        # 5. 主导信号类型(权重最高)
        dominant = sigs[max(range(len(sigs)), key=lambda i: weights[i])].signal_type

        # 6. 共振增强标记
        resonance_enhanced = any(self._has_resonance(s, sigs) for s in sigs)

        method = self._method_of_strategy()
        reason = (
            f"fused {len(sigs)} signals: willingness={willingness:.2f}, "
            f"consistency={consistency.value}, confidence={confidence:.2f}"
        )

        return FusedSellDecision(
            symbol=symbol,
            willingness=willingness,
            confidence=confidence,
            contributing_signals=list(sigs),
            consistency=consistency,
            fusion_method=method,
            dominant_signal_type=dominant,
            resonance_enhanced=resonance_enhanced,
            reason=reason,
            timestamp=now,
        )

    # ── 权重计算 ──

    def _signal_weight(self, sig: SellSignal, all_sigs: list[SellSignal]) -> float:
        """信号权重 = 类型权重 × (共振增强? resonance_boost : 1.0)。"""
        base = self._type_weight(sig.signal_type)
        if self._has_resonance(sig, all_sigs):
            return base * self._resonance_boost
        return base

    def _type_weight(self, stype: SellSignalType) -> float:
        """从策略获取类型权重(仅 WeightedAverageFusion 支持)。"""
        getter = getattr(self._strategy, "type_weight", None)
        if callable(getter):
            return getter(stype)
        return 1.0

    @staticmethod
    def _has_resonance(sig: SellSignal, all_sigs: list[SellSignal]) -> bool:
        """多时间框架共振: 同标的同方向存在其他时间框架信号。"""
        if sig.timeframe is SignalTimeFrame.UNKNOWN:
            return False
        return any(
            s is not sig
            and s.direction is sig.direction
            and s.timeframe is not sig.timeframe
            and s.timeframe is not SignalTimeFrame.UNKNOWN
            for s in all_sigs
        )

    # ── 一致性检查 ──

    @staticmethod
    def _check_consistency(sigs: list[SellSignal]) -> ConsistencyLevel:
        """同方向占比 → 一致性等级。"""
        if not sigs:
            return ConsistencyLevel.LOW
        directions = [s.direction for s in sigs]
        counts: dict[SellDirection, int] = defaultdict(int)
        for d in directions:
            counts[d] += 1
        max_ratio = max(counts.values()) / len(directions)
        if max_ratio > _HIGH_CONSISTENCY:
            return ConsistencyLevel.HIGH
        if max_ratio >= _MEDIUM_CONSISTENCY:
            return ConsistencyLevel.MEDIUM
        return ConsistencyLevel.LOW

    # ── 辅助 ──

    def _method_of_strategy(self) -> FusionMethod:
        """策略→融合方法枚举。"""
        if isinstance(self._strategy, WeightedAverageFusion):
            return FusionMethod.WEIGHTED_AVG
        return FusionMethod.WEIGHTED_AVG  # 默认(自定义策略归为加权平均类)

    # ── 事件发布 ──

    def _emit_event(self, decision: FusedSellDecision, now: datetime) -> None:
        event = SellSignalFusedEvent(
            decision=decision,
            timestamp=now,
            context_snapshot={
                "symbol": decision.symbol,
                "willingness": decision.willingness,
                "confidence": decision.confidence,
                "consistency": decision.consistency.value,
                "signal_count": len(decision.contributing_signals),
            },
        )
        for cb in self._fused_callbacks:
            try:
                cb(event)
            except Exception as exc:  # noqa: BLE001 — 回调异常不阻断
                logger.error("Fused event callback failed: %s", exc, exc_info=True)
