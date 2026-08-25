# [BLUEPRINT] MOD-RK-37 | docs/03_modules/_domain_risk/performance_attribution_degradation/blueprint.md
# [MODULE] zephyr.risk.core.performance_attribution_degradation
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.pf_core.core.performance_attribution_engine(MOD-PF-007); zephyr.shared.foundation.errors
# [CONSUMERS] 模块48 动态信号权重联动(weight_multiplier 写回编排); D_REPORTING(退化台账); D_GOV_ENFORCEMENT(降权审计)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] IC 60日均线 reference=首窗均值/current=末窗均值; ic_decay_pct>50%→degraded(委托MOD-PF-007唯一真源); 拥挤分>warn(0.6)→HALVE(×0.5); degraded优先→ZERO(×0.0写回信号权重); action取ZERO>HALVE>KEEP; reasons全量留痕; 归因计算不重造(Brinson委托MOD-PF-007); 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDegradationInputError
# [TESTS] tests/risk/core/test_performance_attribution_degradation.py
# [A_module] module_id=MOD-RK-37 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Performance Attribution & Degradation Guard — 统一绩效归因与策略退化检测 (MOD-RK-37, CAND-RSK-040)

模块42 落码：绩效监控不只看盈亏。归因与 IC 衰减计算分散三处（MOD-L07-001/
MOD-PF-007/MOD-L02-004）已各自可用，本模块补齐缺失的**策略退化判定与自动降权
闭环**：

  1. IC 60 日均线退化判定：reference=序列首 60 日均值，current=末 60 日均值；
     衰减 >50% → degraded（判定规则委托 MOD-PF-007 detect_degradation，唯一真源，
     reference≤0 语义同其约定 → 退化）；
  2. 拥挤度联动：crowding_score（MOD-RK-13 口径 0~1）> 0.6 → 追加 ×0.5 降权；
  3. 自动降权指令：degraded → weight_multiplier=0.0（ZERO，权重归零写回信号权重）；
     拥挤超阈 → 0.5（HALVE）；否则 1.0（KEEP）。指令为纯数据，写回执行归
     调用方（模块48 动态信号权重联动编排）；
  4. 统一归因入口：brinson_attribute 薄委托 MOD-PF-007（Brinson 配置/选择/交互
     守恒口径不重造；因子/风险归因同属其 attribute_full 能力面）。

纪律：纯计算、无 IO；IC 序列为 PIT 已实现口径（INV-004 铁律，由调用方保证）；
weight_multiplier 只产出指令不直接改任何信号权重（三维解耦）。
依据: blueprint.md（MOD-RK-37）§3 核心规则；Brinson & Fachler (1985)；Man Group
AlphaGPT 退化检测实践（IC 衰减口径）
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略 IC 序列
#   fields: strategy_id + ic_series(日IC, PIT已实现, ≥window个, 全有限)
#   code: assess_strategy() 参数
# - id: I2
#   name: 拥挤度分数(可选)
#   fields: crowding_score∈[0,1](MOD-RK-13口径)
#   code: assess_strategy() 参数
# - id: I3
#   name: 配置 DegradationGuardConfig
#   fields: ic_window=60/ic_decay_threshold=0.5/crowding_warn=0.6/crowding_multiplier=0.5
#   code: DegradationGuardConfig
# 层: 算法
# - id: A1
#   name_zh: ① IC 60日均线
#   name_en: compute_ic_ma60
#   intro: reference=首window均值, current=末window均值
# - id: A2
#   name_zh: ② 退化判定委托
#   name_en: _delegate_degradation
#   intro: MOD-PF-007 detect_degradation(baseline=reference, recent=current)>50%→degraded
# - id: A3
#   name_zh: ③ 拥挤联动+降权裁决
#   name_en: _verdict
#   intro: degraded→ZERO×0.0; crowding>warn→HALVE×0.5; else KEEP×1.0; reasons全量
# - id: A4
#   name_zh: ④ 统一归因入口
#   name_en: brinson_attribute
#   intro: 薄委托MOD-PF-007 Brinson三因子(守恒口径不重算)
# 层: 输出
# - id: O1
#   name: StrategyDegradationVerdict
#   fields: ic_ma60_reference/current/ic_decay_pct/degraded/crowding_penalty/weight_multiplier/action/reasons
# 边:
# I1 --> A1
# I3 --> A1
# A1 --> A2
# I2 --> A3
# A2 --> A3
# I3 --> A3
# A3 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Final

from zephyr.pf_core.core.performance_attribution_engine import (
    BrinsonResult,
    PerformanceAttributionEngine,
    SegmentReturn,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "DegradationAction",
    "DegradationGuardConfig",
    "InvalidDegradationInputError",
    "PerformanceAttributionDegradationGuard",
    "StrategyDegradationVerdict",
]


class InvalidDegradationInputError(ZephyrBaseError):
    """退化检测输入/配置非法（Fail-Closed）。"""


class DegradationAction(str, Enum):
    """降权动作（严格度降序）。"""

    ZERO = "ZERO"  # 权重归零（degraded，写回信号权重=0）
    HALVE = "HALVE"  # 权重减半（拥挤超阈）
    KEEP = "KEEP"  # 保持


@dataclass(frozen=True)
class DegradationGuardConfig:
    """退化检测配置（C 类可调；默认值=候选登记真源）。"""

    ic_window: int = 60  # IC 均线窗口（60 日均线）
    ic_decay_threshold: float = 0.5  # 衰减退化阈（>50%）
    crowding_warn: float = 0.6  # 拥挤度警戒（MOD-RK-13 默认阈口径）
    crowding_multiplier: float = 0.5  # 拥挤降权倍率

    def __post_init__(self) -> None:
        if self.ic_window < 10:
            raise InvalidDegradationInputError(f"ic_window 必须 ≥10: {self.ic_window}")
        if not (0.0 < self.ic_decay_threshold < 1.0):
            raise InvalidDegradationInputError(f"ic_decay_threshold 须 ∈(0,1): {self.ic_decay_threshold}")
        if not (0.0 < self.crowding_warn < 1.0):
            raise InvalidDegradationInputError(f"crowding_warn 须 ∈(0,1): {self.crowding_warn}")
        if not (0.0 < self.crowding_multiplier < 1.0):
            raise InvalidDegradationInputError(f"crowding_multiplier 须 ∈(0,1): {self.crowding_multiplier}")


@dataclass(frozen=True)
class StrategyDegradationVerdict:
    """策略退化裁决（frozen 留痕）。"""

    strategy_id: str
    ic_ma60_reference: float
    ic_ma60_current: float
    ic_decay_pct: float
    degraded: bool
    crowding_score: float | None
    crowding_penalty: bool
    weight_multiplier: float
    action: DegradationAction
    reasons: tuple[str, ...]


class PerformanceAttributionDegradationGuard:
    """统一绩效归因与策略退化检测（MOD-PF-007 委托真源 + 降权闭环）。"""

    def __init__(
        self,
        config: DegradationGuardConfig | None = None,
        attribution_engine: PerformanceAttributionEngine | None = None,
    ) -> None:
        self._config = config or DegradationGuardConfig()
        self._engine = attribution_engine or PerformanceAttributionEngine(
            ic_decay_threshold=self._config.ic_decay_threshold
        )

    @property
    def config(self) -> DegradationGuardConfig:
        return self._config

    # ── ① IC 60 日均线 ───────────────────────────────────────────────

    def compute_ic_ma60(self, ic_series: Sequence[float]) -> tuple[float, float]:
        """IC 均线对：(reference=首 window 均值, current=末 window 均值)。"""
        window = self._config.ic_window
        series = [float(v) for v in ic_series]
        if len(series) < window:
            raise InvalidDegradationInputError(
                f"IC 序列长度 {len(series)} 不足窗口 {window}（Fail-Closed，不足不判定）"
            )
        if not all(math.isfinite(v) for v in series):
            raise InvalidDegradationInputError("IC 序列含非有限值（NaN/±Inf），拒绝判定")
        reference = sum(series[:window]) / window
        current = sum(series[-window:]) / window
        return reference, current

    # ── ②+③ 退化判定与降权裁决 ───────────────────────────────────────

    def assess_strategy(
        self,
        strategy_id: str,
        *,
        ic_series: Sequence[float],
        crowding_score: float | None = None,
    ) -> StrategyDegradationVerdict:
        """评估单策略退化与拥挤联动，产出降权指令。

        Args:
            strategy_id: 策略 ID（非空）
            ic_series: 日 IC 序列（PIT 已实现口径，≥window 个）
            crowding_score: 可选拥挤度分数（MOD-RK-13 口径，∈[0,1]）

        Returns:
            StrategyDegradationVerdict（action ZERO/HALVE/KEEP + weight_multiplier）

        Raises:
            InvalidDegradationInputError: 输入非法（Fail-Closed）
        """
        if not strategy_id or not str(strategy_id).strip():
            raise InvalidDegradationInputError("strategy_id 不得为空")
        cfg = self._config
        if crowding_score is not None:
            cs = float(crowding_score)
            if not math.isfinite(cs) or not (0.0 <= cs <= 1.0):
                raise InvalidDegradationInputError(f"crowding_score 须 ∈[0,1]: {crowding_score}")
        else:
            cs = None

        reference, current = self.compute_ic_ma60(ic_series)

        # ② 退化判定委托 MOD-PF-007（>50% 衰减 → degraded 唯一真源）
        detection = self._engine.detect_degradation(strategy_id, reference, current)
        degraded = bool(detection.degraded)

        # ③ 拥挤联动 + 裁决（degraded 优先）
        crowding_penalty = cs is not None and cs > cfg.crowding_warn
        reasons: list[str] = []
        if degraded:
            reasons.append(
                f"IC {cfg.ic_window} 日均线衰减 {detection.ic_decay_pct:.1%} > {cfg.ic_decay_threshold:.0%} 退化阈 → 权重归零"
            )
        else:
            reasons.append(
                f"IC {cfg.ic_window} 日均线衰减 {detection.ic_decay_pct:.1%} 未超退化阈（ref={reference:.4f} cur={current:.4f}）"
            )
        if cs is not None:
            if crowding_penalty:
                reasons.append(f"拥挤度 {cs:.2f} > 警戒 {cfg.crowding_warn:.2f} → 联动降权 ×{cfg.crowding_multiplier}")
            else:
                reasons.append(f"拥挤度 {cs:.2f} 未超警戒 {cfg.crowding_warn:.2f}")

        if degraded:
            action, multiplier = DegradationAction.ZERO, 0.0
        elif crowding_penalty:
            action, multiplier = DegradationAction.HALVE, cfg.crowding_multiplier
        else:
            action, multiplier = DegradationAction.KEEP, 1.0

        return StrategyDegradationVerdict(
            strategy_id=strategy_id,
            ic_ma60_reference=reference,
            ic_ma60_current=current,
            ic_decay_pct=float(detection.ic_decay_pct),
            degraded=degraded,
            crowding_score=cs,
            crowding_penalty=crowding_penalty,
            weight_multiplier=multiplier,
            action=action,
            reasons=tuple(reasons),
        )

    # ── ④ 统一归因入口（薄委托，不重算） ─────────────────────────────

    def brinson_attribute(self, segments: list[SegmentReturn], now: datetime | None = None) -> BrinsonResult:
        """Brinson 三因子归因统一入口（委托 MOD-PF-007，守恒口径不重造）。"""
        return self._engine.brinson_attribute(segments, now=now)
