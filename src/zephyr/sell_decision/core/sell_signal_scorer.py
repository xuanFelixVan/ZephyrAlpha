# [BLUEPRINT] MOD-SELL-002 | docs/03_modules/MOD-SELL-002/
# [MODULE] zephyr.sell_decision.core.sell_signal_scorer
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.sell_decision.core.sell_signal_collector ; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SELL-007(融合引擎) ; MOD-SELL-008(仲裁器) ; MOD-SELL-009(紧迫度评分)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 评分=置信度×强度×贝叶斯准确率调整×共振加成,值域[0,1]封顶; 小样本准确率向0.5先验收缩(α=8); 共振=同标的同方向≥2不同timeframe; strength异常>1截断不放大(Fail-Closed); 输出按score降序+symbol字典序确定性排序; 与具体选股策略零耦合(三维解耦); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-SELL-002/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidScoreInputError(ZA-SELL-0020)
# [TESTS] tests/sell_decision/test_sell_signal_scorer.py
# [A_module] module_id=MOD-SELL-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Sell Signal Scorer — 卖出信号评分器 (MOD-SELL-002)

SELL-01 收集的原始信号 → 综合评分（0~1），供融合/仲裁/紧迫度消费：

    score = confidence × strength × accuracy_adjusted × resonance_multiplier

  - confidence：信号原始置信度（SELL-01 已校验 ∈[0,1]）；
  - strength：信号强度，异常 >1 截断至 1.0（Fail-Closed 不放大）；
  - accuracy_adjusted：信号类型的历史命中率，贝叶斯收缩
    (hits + α·0.5)/(total + α)，α=8——小样本向 0.5 中性先验收缩，
    防止"2/2 命中=100%"的过拟合读数（宪章 §4.2 B-009 精神）；
    无统计时取 0.5 中性；
  - resonance_multiplier：跨周期共振加成（同标的同方向 ≥2 个不同
    timeframe 信号 → ×(1+bonus)，默认 bonus=0.15，乘后封顶 1.0）。

三维解耦：只消费标准化 SellSignal（信号类型枚举），不认识任何具体
选股策略（what）——评分逻辑对全部策略通用。

纪律：纯函数、无 IO；准确率统计由调用方注入（禁自造数据管道）。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from zephyr.sell_decision.core.sell_signal_collector import (
    SellSignal,
    SellSignalType,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "AccuracyStat",
    "InvalidScoreInputError",
    "ScoredSellSignal",
    "score_signals",
]

# 贝叶斯收缩强度（先验等效样本数）
_ACCURACY_PRIOR: Final = 8.0
# 默认跨周期共振加成
_DEFAULT_RESONANCE_BONUS: Final = 0.15


class InvalidScoreInputError(ZephyrBaseError):
    """卖出信号评分输入非法（准确率统计矛盾/共振加成越界）。"""

    error_code = "ZA-SELL-0020"


@dataclass(frozen=True)
class AccuracyStat:
    """信号类型历史准确率统计。

    Attributes:
        hits: 命中次数（信号触发后按预期方向兑现）
        total: 总触发次数
    """

    hits: int
    total: int

    def adjusted_rate(self, prior: float = _ACCURACY_PRIOR) -> float:
        """贝叶斯收缩后命中率（小样本向 0.5 先验收缩）。"""
        return (self.hits + prior * 0.5) / (self.total + prior)


@dataclass(frozen=True)
class ScoredSellSignal:
    """评分后的卖出信号（frozen 不可变）。

    Attributes:
        signal: 原始信号（SELL-01 SellSignal）
        score: 综合评分 ∈[0,1]
        confidence_component: 置信度分量
        strength_component: 强度分量（截断后）
        accuracy_component: 准确率调整分量
        resonance_multiplier: 共振加成倍数（无共振=1.0）
        resonance: 是否命中跨周期共振
    """

    signal: SellSignal
    score: float
    confidence_component: float
    strength_component: float
    accuracy_component: float
    resonance_multiplier: float
    resonance: bool = field(default=False)


def _validate_accuracy_stats(stats: Mapping[SellSignalType, AccuracyStat]) -> None:
    for stype, st in stats.items():
        if st.hits < 0 or st.total < 0:
            raise InvalidScoreInputError(
                f"信号类型 {stype.value} 准确率统计含负值（hits={st.hits}, total={st.total}）"
            )
        if st.hits > st.total:
            raise InvalidScoreInputError(
                f"信号类型 {stype.value} 命中数 {st.hits} 超总次数 {st.total}（统计矛盾）"
            )


def score_signals(
    signals: Sequence[SellSignal],
    *,
    accuracy_stats: Mapping[SellSignalType, AccuracyStat] | None = None,
    resonance_bonus: float = _DEFAULT_RESONANCE_BONUS,
) -> list[ScoredSellSignal]:
    """卖出信号综合评分（纯函数）。

    Args:
        signals: SELL-01 标准化信号列表
        accuracy_stats: {SellSignalType: AccuracyStat}，缺省=中性 0.5
        resonance_bonus: 跨周期共振加成 ∈[0,1]（默认 0.15）

    Returns:
        list[ScoredSellSignal]，按 score 降序、同分按 symbol 字典序

    Raises:
        InvalidScoreInputError: 统计矛盾/加成越界
    """
    if not math.isfinite(resonance_bonus) or not (0.0 <= resonance_bonus <= 1.0):
        raise InvalidScoreInputError(f"resonance_bonus 非法（须 ∈[0,1]），got {resonance_bonus}")
    stats = accuracy_stats or {}
    _validate_accuracy_stats(stats)
    if not signals:
        return []

    # 共振检测：同 (symbol, direction) 组内 ≥2 个不同 timeframe
    tf_by_group: dict[tuple[str, str], set[str]] = {}
    for sig in signals:
        key = (sig.symbol, sig.direction.value)
        tf_by_group.setdefault(key, set()).add(sig.timeframe.value)
    resonant_groups = {k for k, tfs in tf_by_group.items() if len(tfs) >= 2}

    scored: list[ScoredSellSignal] = []
    for sig in signals:
        confidence = sig.confidence
        strength = min(max(sig.strength, 0.0), 1.0)
        stat = stats.get(sig.signal_type)
        accuracy = stat.adjusted_rate() if stat is not None else 0.5

        resonant = (sig.symbol, sig.direction.value) in resonant_groups
        multiplier = 1.0 + resonance_bonus if resonant else 1.0

        score = confidence * strength * accuracy * multiplier
        score = min(max(score, 0.0), 1.0)

        scored.append(
            ScoredSellSignal(
                signal=sig,
                score=score,
                confidence_component=confidence,
                strength_component=strength,
                accuracy_component=accuracy,
                resonance_multiplier=multiplier,
                resonance=resonant,
            )
        )

    scored.sort(key=lambda s: (-s.score, s.signal.symbol, s.signal.signal_type.value))
    return scored
