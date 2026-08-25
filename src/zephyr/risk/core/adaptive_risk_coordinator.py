# [BLUEPRINT] MOD-RK-30 | docs/03_modules/_domain_risk/adaptive_risk_coordinator/blueprint.md
# [MODULE] zephyr.risk.core.adaptive_risk_coordinator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.adaptive_risk_forecast(MOD-RK-28); zephyr.risk.core.adaptive_risk_monitor(MOD-RK-29); zephyr.shared.foundation.errors
# [CONSUMERS] MOD-L06-001 RiskLayerOrchestrator(执行侧三层喂入, 设计契约); C-038 黑天鹅模式库(MOD-RK-31, 升级触发源)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 熔断级别取最严(KILL_SWITCH>HALT_NEW>REDUCE_POSITION>NONE); position_cap_scale∈[0,1]; limit_scale_final=forecast.limit_scale×regime_multiplier(不放大); 未知regime保守0.7; KILL_SWITCH仅advised不直接触发(委托stop_loss存量链路); B-001~B-006硬边界只读; 纯函数无IO
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCoordinatorConfigError
# [TESTS] tests/risk/test_adaptive_risk_coordinator.py
# [TTL] permanent

# [ALGO_FLOW]
# I1: ForwardVarForecast(①预判层契约) + regime_state(C-021 状态)
# I2: RiskWatchSnapshot(②监控层契约) + black_swan_escalated(C-038 升级标记)
# I3: CoordinatorConfig(降仓档/regime乘数表/未知保守乘数) + B-001~B-006硬边界注册表
# A1: 盘前计划(limit_scale×regime_multiplier收紧+sit_out透传)
# A2: 盘中熔断分级(monitor红→HALT_NEW/橙→REDUCE; breach→REDUCE; sit_out→HALT_NEW; 黑天鹅→KILL_SWITCH advised; 取最严)
# O1: PremarketRiskPlan / AdaptiveRiskDecision(frozen) → 执行侧编排消费
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I1 --> A2
# I2 --> A2
# I3 --> A2
# A1 --> O1
# A2 --> O1
"""

Adaptive Risk Coordinator — C-004 自适应风控三层联动装配层 (MOD-RK-30, MVP)

C-004 三层联动的薄装配编排面（W1c 同族整合裁定：底座复用+薄装配，禁止复制）：
消费 ①预判层（MOD-RK-28 ForwardVarForecast）与 ②监控层（MOD-RK-29
RiskWatchSnapshot）的数据契约，产出盘前计划（sit_out/限额缩放下发）与盘中熔断
分级（REDUCE_POSITION/HALT_NEW/KILL_SWITCH 取最严）；参数随 C-021 市场状态
自适应（regime 乘数表，未知状态保守 0.7）。

熔断层纪律：KILL_SWITCH 仅产 kill_switch_advised（BS-007 纪律：建议非直接触发），
执行委托 stop_loss / MOD-L06-001 RiskLayerOrchestrator 存量链路，本模块不 import
不复制。B-001~B-006 硬边界注册表为代码 SSoT（frozen 映射），值锚定
config/risk_params.yaml（INV-002/G10/G11/G12），单测锚定防漂移。

SSoT: docs/03_modules/_domain_risk/adaptive_risk_coordinator/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping

from zephyr.risk.core.adaptive_risk_forecast import ForwardVarForecast
from zephyr.risk.core.adaptive_risk_monitor import RiskWatchSnapshot
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "AdaptiveRiskDecision",
    "CircuitBreakerLevel",
    "CoordinatorConfig",
    "HardBoundary",
    "InvalidCoordinatorConfigError",
    "PremarketRiskPlan",
    "decide_intraday",
    "get_hard_boundaries",
    "plan_premarket",
]


class InvalidCoordinatorConfigError(ZephyrBaseError):
    """三层联动装配层配置非法（Fail-Closed）。"""


@dataclass(frozen=True)
class HardBoundary:
    """单条硬边界（B-00x，值锚定 config/risk_params.yaml 真源）。"""

    boundary_id: str  # "B-001".."B-006"
    name: str  # 中文名
    value: float  # 边界值
    source_key: str  # risk_params.yaml 键名


#: B-001~B-006 硬边界注册表（代码 SSoT；值锚定 config/risk_params.yaml，单测锚定防漂移）
_HARD_BOUNDARIES: Final = MappingProxyType(
    {
        "B-001": HardBoundary("B-001", "单一持仓NAV占比上限", 0.05, "max_single_position_nav_ratio"),
        "B-002": HardBoundary("B-002", "行业集中度NAV占比上限", 0.30, "max_sector_concentration_nav_ratio"),
        "B-003": HardBoundary("B-003", "总杠杆上限", 1.0, "max_gross_leverage"),
        "B-004": HardBoundary("B-004", "策略间相关性阈值", 0.85, "max_strategy_correlation_threshold"),
        "B-005": HardBoundary("B-005", "因子集合重叠比例上限", 0.60, "max_factor_overlap_threshold"),
        "B-006": HardBoundary("B-006", "股票池重叠比例上限", 0.70, "max_universe_overlap_threshold"),
    }
)

#: 默认 regime 风险乘数表（C-021 状态自适应；收紧方向，>1 无意义故上限 1.0）
_DEFAULT_REGIME_MULTIPLIERS: Final = MappingProxyType(
    {
        "CALM": 1.0,
        "NORMAL": 1.0,
        "TURBULENT": 0.7,
        "CRISIS": 0.4,
    }
)


def get_hard_boundaries() -> Mapping[str, HardBoundary]:
    """返回 B-001~B-006 硬边界注册表（只读映射）。"""
    return _HARD_BOUNDARIES


class CircuitBreakerLevel(str, Enum):
    """熔断分级（严重度递增）。"""

    NONE = "NONE"
    REDUCE_POSITION = "REDUCE_POSITION"  # 降仓
    HALT_NEW = "HALT_NEW"  # 禁开仓
    KILL_SWITCH = "KILL_SWITCH"  # Kill Switch 建议（委托 stop_loss 执行）


_LEVEL_ORDER: Final = {
    CircuitBreakerLevel.NONE: 0,
    CircuitBreakerLevel.REDUCE_POSITION: 1,
    CircuitBreakerLevel.HALT_NEW: 2,
    CircuitBreakerLevel.KILL_SWITCH: 3,
}


@dataclass(frozen=True)
class CoordinatorConfig:
    """装配层配置（C 类可调参数）。

    Attributes:
        reduce_cap_scale: REDUCE_POSITION 档仓位上限缩放
        regime_multipliers: C-021 状态 → 风险乘数（∈(0,1]）
        unknown_regime_multiplier: 未知状态保守乘数（Fail-Closed 方向）
    """

    reduce_cap_scale: float = 0.5
    regime_multipliers: Mapping[str, float] = field(default_factory=lambda: dict(_DEFAULT_REGIME_MULTIPLIERS))
    unknown_regime_multiplier: float = 0.7

    def __post_init__(self) -> None:
        for name, v in (("reduce_cap_scale", self.reduce_cap_scale), ("unknown_regime_multiplier", self.unknown_regime_multiplier)):
            if not math.isfinite(v) or not 0.0 < v <= 1.0:
                raise InvalidCoordinatorConfigError(f"{name} 必须 ∈ (0,1] 有限值: {v}")
        for state, m in self.regime_multipliers.items():
            if not math.isfinite(m) or not 0.0 < m <= 1.0:
                raise InvalidCoordinatorConfigError(f"regime_multipliers[{state!r}] 必须 ∈ (0,1]: {m}")


@dataclass(frozen=True)
class PremarketRiskPlan:
    """盘前风险计划（预判层 → 限额下发）。"""

    sit_out: bool
    limit_scale: float  # forecast.limit_scale × regime_multiplier（∈(0,1]）
    regime_state: str
    regime_multiplier: float
    var_pct: float
    conformal_var_pct: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class AdaptiveRiskDecision:
    """盘中三层联动裁决（取最严）。"""

    level: CircuitBreakerLevel
    position_cap_scale: float  # ∈[0,1]
    allow_new_positions: bool
    kill_switch_advised: bool
    reasons: tuple[str, ...]


def plan_premarket(
    forecast: ForwardVarForecast,
    *,
    regime_state: str = "NORMAL",
    config: CoordinatorConfig | None = None,
) -> PremarketRiskPlan:
    """盘前计划：①预判层输出 × C-021 状态乘数 → sit_out/限额缩放下发。

    Args:
        forecast: MOD-RK-28 前瞻预判结果
        regime_state: C-021 市场状态标签（未知 → 保守乘数）
        config: 配置（None → 默认）

    Returns:
        PremarketRiskPlan
    """
    cfg = config or CoordinatorConfig()
    reasons: list[str] = []
    multiplier = cfg.regime_multipliers.get(regime_state)
    if multiplier is None:
        multiplier = cfg.unknown_regime_multiplier
        reasons.append(f"未知 regime 状态 {regime_state!r}，取保守乘数 {multiplier}")
    limit_scale = min(1.0, forecast.limit_scale * multiplier)
    if forecast.sit_out:
        reasons.append(f"①预判层 sit_out（conformal_var={forecast.conformal_var_pct:.4f}）")
    if forecast.limit_breached:
        reasons.append(f"①预判层限额超限（limit_scale={forecast.limit_scale:.3f}）")
    return PremarketRiskPlan(
        sit_out=forecast.sit_out,
        limit_scale=limit_scale,
        regime_state=regime_state,
        regime_multiplier=multiplier,
        var_pct=forecast.var_pct,
        conformal_var_pct=forecast.conformal_var_pct,
        reasons=tuple(reasons),
    )


def decide_intraday(
    monitor: RiskWatchSnapshot,
    *,
    forecast: ForwardVarForecast | None = None,
    black_swan_escalated: bool = False,
    config: CoordinatorConfig | None = None,
) -> AdaptiveRiskDecision:
    """盘中熔断分级：②监控层 + ①预判层 + C-038 升级标记 → 取最严裁决。

    Args:
        monitor: MOD-RK-29 监控层快照
        forecast: MOD-RK-28 预判结果（可空）
        black_swan_escalated: C-038 黑天鹅模式库升级标记（→ KILL_SWITCH 建议）
        config: 配置（None → 默认）

    Returns:
        AdaptiveRiskDecision
    """
    cfg = config or CoordinatorConfig()
    level = CircuitBreakerLevel.NONE
    cap = 1.0
    reasons: list[str] = []

    if monitor.overall_severity == "red":
        level = CircuitBreakerLevel.HALT_NEW
        reasons.append("②监控层红档（流动性/相关性严重）→ 禁开仓")
    elif monitor.overall_severity in ("orange", "yellow") and _LEVEL_ORDER[CircuitBreakerLevel.REDUCE_POSITION] > _LEVEL_ORDER[level]:
        if monitor.overall_severity == "orange":
            level = CircuitBreakerLevel.REDUCE_POSITION
            cap = min(cap, cfg.reduce_cap_scale)
            reasons.append("②监控层橙档 → 降仓")

    if forecast is not None:
        if forecast.limit_breached and _LEVEL_ORDER[CircuitBreakerLevel.REDUCE_POSITION] > _LEVEL_ORDER[level]:
            level = CircuitBreakerLevel.REDUCE_POSITION
        if forecast.limit_breached:
            cap = min(cap, forecast.limit_scale)
            reasons.append(f"①预判层限额超限 → 仓位上限缩放 {forecast.limit_scale:.3f}")
        if forecast.sit_out and _LEVEL_ORDER[CircuitBreakerLevel.HALT_NEW] > _LEVEL_ORDER[level]:
            level = CircuitBreakerLevel.HALT_NEW
            reasons.append("①预判层 sit_out → 禁开仓")

    kill_advised = False
    if black_swan_escalated:
        level = CircuitBreakerLevel.KILL_SWITCH
        cap = 0.0
        kill_advised = True
        reasons.append("C-038 黑天鹅模式升级 → Kill Switch 建议（委托 stop_loss 执行）")

    return AdaptiveRiskDecision(
        level=level,
        position_cap_scale=cap,
        allow_new_positions=_LEVEL_ORDER[level] < _LEVEL_ORDER[CircuitBreakerLevel.HALT_NEW],
        kill_switch_advised=kill_advised,
        reasons=tuple(reasons),
    )
