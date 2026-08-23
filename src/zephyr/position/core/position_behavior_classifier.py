# [BLUEPRINT] MOD-POS-019 | docs/03_modules/MOD-POS-019/
# [MODULE] zephyr.position.core.position_behavior_classifier
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D-SELL-DECISION(行为纠偏参考) ; D_RISK(行为风险预警)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 规则分类五类互斥(优先级LOSS_HOLDING>WINNER_CUTTING>TREND_RIDING>STALE>NEUTRAL); 阈值常量化可覆写; 分类只标记不执行(三维解耦,不卖仓); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-POS-019/
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPositionFeatureError(ZA-POS-0025)
# [TESTS] tests/position/test_position_behavior_classifier.py
# [A_module] module_id=MOD-POS-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Position Behavior Classifier — 持仓行为分类器 (MOD-POS-019)

对持仓做行为金融学维度的规则分类，供卖出域行为纠偏与风控预警参考：

  - LOSS_HOLDING（套牢持有/处置效应）：深亏且长期持有——
    "亏的不卖"是典型处置效应，标记供复盘与卖出域评估；
  - WINNER_CUTTING（过早止盈倾向）：盈利但持有期很短——
    "赢的急卖"倾向，标记供复盘（本模块不阻止止盈，只标注）；
  - TREND_RIDING（趋势持有）：盈利、长持、回撤受控——健康状态；
  - STALE（呆滞）：盈亏平淡且长期占用资金——机会成本提示；
  - NEUTRAL：其他。

规则互斥，按 LOSS_HOLDING > WINNER_CUTTING > TREND_RIDING > STALE >
NEUTRAL 优先级裁定。分类只标记不执行（与卖出/选股零耦合）。

纪律：纯函数、无 IO；特征由调用方注入。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "BehaviorClass",
    "ClassificationReport",
    "InvalidPositionFeatureError",
    "PositionFeatures",
    "classify_positions",
]

# 默认阈值（经验基线，参数可覆写）
_LOSS_THRESHOLD: Final = -0.15  # 深亏线（pnl_pct ≤ 此值为套牢候选）
_LOSS_MIN_DAYS: Final = 30  # 套牢最短持有天数
_WINNER_THRESHOLD: Final = 0.08  # 盈利线（pnl_pct ≥ 此值）
_QUICK_DAYS: Final = 5  # 过早止盈最短持有天数（≤ 此值为"急卖"）
_TREND_MIN_DAYS: Final = 20  # 趋势持有最短天数
_TREND_MAX_DRAWDOWN: Final = 0.10  # 趋势持有允许的最大高点回撤
_FLAT_BAND: Final = 0.03  # 平淡带宽 |pnl| < 此值
_STALE_DAYS: Final = 60  # 呆滞最短持有天数


class BehaviorClass(str, Enum):
    """持仓行为分类。"""

    LOSS_HOLDING = "LOSS_HOLDING"  # 套牢持有（处置效应）
    WINNER_CUTTING = "WINNER_CUTTING"  # 过早止盈倾向
    TREND_RIDING = "TREND_RIDING"  # 趋势持有（健康）
    STALE = "STALE"  # 呆滞
    NEUTRAL = "NEUTRAL"  # 中性


class InvalidPositionFeatureError(ZephyrBaseError):
    """持仓行为特征非法（非有限盈亏/负持有天数/回撤越界）。"""

    error_code = "ZA-POS-0025"


@dataclass(frozen=True)
class PositionFeatures:
    """单持仓行为特征。

    Attributes:
        pnl_pct: 浮动盈亏比例（如 0.12 = +12%）
        days_held: 已持有天数（≥0）
        drawdown_from_peak: 自持仓内最高点的回撤 ∈[0,1]（默认 0）
    """

    pnl_pct: float
    days_held: int
    drawdown_from_peak: float = 0.0


@dataclass(frozen=True)
class ClassificationReport:
    """行为分类报告（frozen 不可变）。

    Attributes:
        labels: {symbol: BehaviorClass}
        counts: {BehaviorClass: 数量}（全类初始化为 0）
        warnings: 行为风险预警（处置效应等）
    """

    labels: dict[str, BehaviorClass]
    counts: dict[BehaviorClass, int]
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _validate_features(sym: str, f: PositionFeatures) -> None:
    if not math.isfinite(f.pnl_pct):
        raise InvalidPositionFeatureError(f"标的 {sym} 盈亏非有限值，got {f.pnl_pct}")
    if f.days_held < 0:
        raise InvalidPositionFeatureError(f"标的 {sym} 持有天数为负，got {f.days_held}")
    if not math.isfinite(f.drawdown_from_peak) or not (0.0 <= f.drawdown_from_peak <= 1.0):
        raise InvalidPositionFeatureError(
            f"标的 {sym} 高点回撤越界（须 ∈[0,1]），got {f.drawdown_from_peak}"
        )


def _classify_one(f: PositionFeatures) -> BehaviorClass:
    """单持仓规则分类（优先级：套牢 > 急卖 > 趋势 > 呆滞 > 中性）。"""
    if f.pnl_pct <= _LOSS_THRESHOLD and f.days_held >= _LOSS_MIN_DAYS:
        return BehaviorClass.LOSS_HOLDING
    if f.pnl_pct >= _WINNER_THRESHOLD and f.days_held <= _QUICK_DAYS:
        return BehaviorClass.WINNER_CUTTING
    if (
        f.pnl_pct >= _WINNER_THRESHOLD
        and f.days_held >= _TREND_MIN_DAYS
        and f.drawdown_from_peak <= _TREND_MAX_DRAWDOWN
    ):
        return BehaviorClass.TREND_RIDING
    if abs(f.pnl_pct) < _FLAT_BAND and f.days_held >= _STALE_DAYS:
        return BehaviorClass.STALE
    return BehaviorClass.NEUTRAL


def classify_positions(
    features: Mapping[str, PositionFeatures],
) -> ClassificationReport:
    """持仓行为分类（纯函数）。

    Args:
        features: {symbol: PositionFeatures}

    Returns:
        ClassificationReport

    Raises:
        InvalidPositionFeatureError: 特征非法
    """
    labels: dict[str, BehaviorClass] = {}
    counts: dict[BehaviorClass, int] = {c: 0 for c in BehaviorClass}
    warnings: list[str] = []

    for sym in sorted(features):
        f = features[sym]
        _validate_features(sym, f)
        cls = _classify_one(f)
        labels[sym] = cls
        counts[cls] += 1
        if cls is BehaviorClass.LOSS_HOLDING:
            warnings.append(
                f"标的 {sym} 疑似处置效应（亏 {f.pnl_pct:.1%} 持有 {f.days_held} 天），建议复盘卖出纪律"
            )
        elif cls is BehaviorClass.STALE:
            warnings.append(
                f"标的 {sym} 呆滞（{f.days_held} 天盈亏 {f.pnl_pct:.1%}），占用资金有机会成本"
            )

    return ClassificationReport(labels=labels, counts=counts, warnings=tuple(warnings))
