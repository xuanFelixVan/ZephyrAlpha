# [BLUEPRINT] MOD-SIG-108 | docs/03_modules/_domain_signal/multi_factor_timing_overlay/blueprint.md
# [MODULE] zephyr.signal_ashare.multi_factor_timing_overlay
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none（纯函数核，不 import zephyr 内部件）
# [CONSUMERS] （候选：决策编排器+MOD-AU-010 裁决层）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 6源封闭集；权重优先级 BMA>IC>等权；负权重 clip 到 0；归一化 Σ=1；composite>+0.10 bullish/<−0.10 bearish/其余 neutral；≥3 同向共振 high_confidence；缺源降级不抛
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01482 行 + 候选注册表 CAND-TESTB-025
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知 source/重复 source/direction 非{-1,0,1}/strength 越界/非有限/空信号/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_multi_factor_timing_overlay.py
# [A_module] module_id=MOD-SIG-108 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
多因子叠加择时（MOD-SIG-108，B10-01482，模块57）。

6 源择时信号库 + IC 加权或 BMA 叠加 + ≥3 同向共振高置信标记。
与 timing_analyst_agent（MOD-AU-010）分工：本件=信号合成层，010=Agent 裁决层。

依据: AUD-DRAFT-001 深挖批 B10-01482（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-108
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: multi_factor_timing_overlay.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MultiFactorTimingOverlay
#   name_en: MultiFactorTimingOverlay
#   intro: 多源择时信号叠加共振检测器。
#   desc: 多源择时信号叠加共振检测器。；公共方法（定义序）: overlay；源码 L130-L206
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: MultiFactorTimingOverlay
#   downstream: （候选：决策编排器+MOD-AU-010 裁决层）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "MultiFactorTimingOverlay",
    "TIMING_SOURCES",
    "TimingOverlayConfig",
    "TimingOverlayResult",
    "TimingSignal",
]

# ------------------------------------------------------------------
# 封闭集
# ------------------------------------------------------------------
TIMING_SOURCES: Final[tuple[str, ...]] = (
    "sentiment_reversal",
    "regime_shift",
    "volatility_breakout",
    "calendar",
    "volume",
    "northbound",
)


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class TimingSignal:
    source: str
    direction: int  # -1, 0, 1
    strength: float  # [0, 1]

    def __post_init__(self):
        if self.source not in TIMING_SOURCES:
            raise ValueError(f"未知 source: {self.source}")
        if self.direction not in (-1, 0, 1):
            raise ValueError("direction 必须为 -1/0/1")
        if not (0.0 <= self.strength <= 1.0) or not math.isfinite(self.strength):
            raise ValueError("strength 必须在 [0,1] 且有限")


@dataclass(frozen=True)
class TimingOverlayConfig:
    direction_threshold: float = 0.10
    resonance_threshold: int = 3

    def __post_init__(self):
        if not math.isfinite(self.direction_threshold) or self.direction_threshold < 0:
            raise ValueError("direction_threshold 必须 ≥0 且有限")
        if self.resonance_threshold < 1:
            raise ValueError("resonance_threshold 必须 ≥1")


@dataclass(frozen=True)
class TimingOverlayResult:
    composite_score: float
    direction: str  # bullish / bearish / neutral
    resonance_count: int
    high_confidence: bool
    resonance_direction: str  # bullish / bearish / none
    weights_used: dict[str, float]
    notes: str = ""


# ------------------------------------------------------------------
# 实现
# ------------------------------------------------------------------
class MultiFactorTimingOverlay:
    """多源择时信号叠加共振检测器。"""

    def __init__(self, config: TimingOverlayConfig | None = None) -> None:
        self.config = config or TimingOverlayConfig()

    def overlay(
        self,
        signals: list[TimingSignal],
        *,
        ic_weights: dict[str, float] | None = None,
        bma_weights: dict[str, float] | None = None,
    ) -> TimingOverlayResult:
        if not signals:
            raise ValueError("signals 不可为空")
        seen = set()
        for s in signals:
            if s.source in seen:
                raise ValueError(f"重复 source: {s.source}")
            seen.add(s.source)

        # 权重优先级：BMA > IC > 等权
        sources = [s.source for s in signals]
        raw_weights: dict[str, float] = {}
        if bma_weights is not None:
            for src in sources:
                raw_weights[src] = max(0.0, bma_weights.get(src, 0.0))
        elif ic_weights is not None:
            for src in sources:
                raw_weights[src] = max(0.0, ic_weights.get(src, 0.0))
        else:
            n = len(sources)
            for src in sources:
                raw_weights[src] = 1.0 / n

        total = sum(raw_weights.values())
        if total <= 0:
            n = len(sources)
            for src in sources:
                raw_weights[src] = 1.0 / n
            total = 1.0
            notes = "fallback_equal_weights"
        else:
            notes = ""

        weights = {src: w / total for src, w in raw_weights.items()}

        composite = sum(weights.get(s.source, 0.0) * s.direction * s.strength for s in signals)

        if composite > self.config.direction_threshold:
            direction = "bullish"
        elif composite < -self.config.direction_threshold:
            direction = "bearish"
        else:
            direction = "neutral"

        # 共振计数（按多数向）
        bullish_count = sum(1 for s in signals if s.direction == 1 and s.strength > 0)
        bearish_count = sum(1 for s in signals if s.direction == -1 and s.strength > 0)
        resonance_count = max(bullish_count, bearish_count)
        high_confidence = resonance_count >= self.config.resonance_threshold and direction != "neutral"
        resonance_direction = "bullish" if bullish_count >= bearish_count else "bearish"
        if resonance_count == 0:
            resonance_direction = "none"

        if len(signals) < len(TIMING_SOURCES):
            notes = notes + ";missing_sources" if notes else "missing_sources"

        return TimingOverlayResult(
            composite_score=composite,
            direction=direction,
            resonance_count=resonance_count,
            high_confidence=high_confidence,
            resonance_direction=resonance_direction,
            weights_used=weights,
            notes=notes,
        )
