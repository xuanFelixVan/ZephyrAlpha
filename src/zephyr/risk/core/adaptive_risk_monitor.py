# [BLUEPRINT] MOD-RK-29 | docs/03_modules/_domain_risk/adaptive_risk_monitor/blueprint.md
# [MODULE] zephyr.risk.core.adaptive_risk_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.position.core.correlation_regime_monitor(MOD-POS-012); zephyr.risk.core.alert_generator(MOD-RK-06,AlertLevel语义); zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-30(Adaptive Risk Coordinator, C-004 三层联动盘中监控); CTR-P1-008 风险仪表盘(设计契约); MOD-RK-06 AlertGenerator(告警发送接线, 编排层完成)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] illiquid_ratio∈[0,1]; liquidity_level∈{normal,yellow,red}; correlation_regime∈{LOW,NORMAL,HIGH,NA}; overall_severity=各维最严(normal<yellow<orange<red); 无相关性输入→NA不参与取严; 纯函数无IO
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRiskWatchConfigError; InvalidLiquidityWatchInputError
# [TESTS] tests/risk/test_adaptive_risk_monitor.py
# [TTL] permanent

# [ALGO_FLOW]
# I1: LiquidityWatchInput 序列(标的级 Amihud/萎缩/非流动标记, 上游 MOD-RK-08 产出)
# I2: 相关性收益矩阵 {symbol: returns}(可空)
# I3: RiskWatchConfig(非流动占比黄/红阈 + 相关性 regime 阈值)
# A1: 流动性分级(illiquid_ratio≥红阈→red告警; ≥黄阈→yellow告警)
# A2: 相关性体制评估(复用MOD-POS-012 assess_correlation_regime; HIGH→orange分散失效告警)
# A3: 综合严重度取最严 + 告警聚合
# O1: RiskWatchSnapshot(仪表盘快照+MonitoringAlert元组) → C-004/仪表盘/告警接线
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I3 --> A1
# I3 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> O1
"""

Adaptive Risk Monitor — 流动性+相关性体制监控层 (MOD-RK-29, C-004 ②监控层 MVP)

C-004 自适应风控三层体系（预判+监控+熔断）的监控层能力底座：盘中聚合流动性风险
（非流动标的占比分级，指标由 MOD-RK-08 LiquidityMonitor 产出）与相关性体制
（MOD-POS-012 三档 regime），产出风险仪表盘快照与告警数据（级别语义对齐
MOD-RK-06 AlertGenerator.AlertLevel；发送接线由编排层完成，本模块不触达通道）。

底座复用裁定（W1c 同族整合）：不重复实现 Amihud/萎缩比率/相关矩阵算法；与
C-045 拥挤度（MOD-RK-13/MOD-RK-32）正交——本模块管流动性+相关性体制监控。

SSoT: docs/03_modules/_domain_risk/adaptive_risk_monitor/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from zephyr.position.core.correlation_regime_monitor import (
    CorrelationRegime,
    assess_correlation_regime,
)
from zephyr.risk.core.alert_generator import AlertLevel
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidLiquidityWatchInputError",
    "InvalidRiskWatchConfigError",
    "LiquidityWatchInput",
    "MonitoringAlert",
    "RiskWatchConfig",
    "RiskWatchSnapshot",
    "assess_risk_watch",
]

#: 严重度排序（normal < yellow < orange < red）
_SEVERITY_ORDER: Final = {"normal": 0, "yellow": 1, "orange": 2, "red": 3}


class InvalidRiskWatchConfigError(ZephyrBaseError):
    """监控层配置非法（Fail-Closed）。"""


class InvalidLiquidityWatchInputError(ZephyrBaseError):
    """流动性监控输入非法（Fail-Closed）。"""


@dataclass(frozen=True)
class RiskWatchConfig:
    """监控层配置（C 类可调参数）。

    Attributes:
        illiquid_ratio_yellow: 非流动标的占比黄告警阈（≥）
        illiquid_ratio_red: 非流动标的占比红告警阈（≥）
        correlation_low_threshold: 相关性 LOW/NORMAL 分界（透传 MOD-POS-012）
        correlation_high_threshold: 相关性 NORMAL/HIGH 分界（透传 MOD-POS-012）
    """

    illiquid_ratio_yellow: float = 0.20
    illiquid_ratio_red: float = 0.50
    correlation_low_threshold: float = 0.3
    correlation_high_threshold: float = 0.6

    def __post_init__(self) -> None:
        for name in ("illiquid_ratio_yellow", "illiquid_ratio_red"):
            v = getattr(self, name)
            if not math.isfinite(v) or not 0.0 < v <= 1.0:
                raise InvalidRiskWatchConfigError(f"{name} 必须 ∈ (0,1] 有限值: {v}")
        if self.illiquid_ratio_yellow >= self.illiquid_ratio_red:
            raise InvalidRiskWatchConfigError(
                f"illiquid_ratio_yellow 须 < illiquid_ratio_red: "
                f"{self.illiquid_ratio_yellow} >= {self.illiquid_ratio_red}"
            )


@dataclass(frozen=True)
class LiquidityWatchInput:
    """标的级流动性指标输入（上游 MOD-RK-08 LiquidityMonitor 产出的最小契约）。"""

    symbol: str
    amihud_illiq: float  # Amihud 非流动性指标（≥0）
    volume_shrinkage_ratio: float  # 成交量萎缩比率（≥0）
    is_illiquid: bool  # 综合非流动标记

    def __post_init__(self) -> None:
        if not self.symbol:
            raise InvalidLiquidityWatchInputError("symbol 不能为空")
        if not math.isfinite(self.amihud_illiq) or self.amihud_illiq < 0.0:
            raise InvalidLiquidityWatchInputError(f"amihud_illiq 必须为非负有限值: {self.amihud_illiq}")
        if not math.isfinite(self.volume_shrinkage_ratio) or self.volume_shrinkage_ratio < 0.0:
            raise InvalidLiquidityWatchInputError(
                f"volume_shrinkage_ratio 必须为非负有限值: {self.volume_shrinkage_ratio}"
            )


@dataclass(frozen=True)
class MonitoringAlert:
    """告警数据（纯数据契约，级别语义对齐 MOD-RK-06 AlertLevel.value）。"""

    level: str  # "yellow" / "orange" / "red"
    source: str  # "liquidity_watch" / "correlation_regime"
    message: str


@dataclass(frozen=True)
class RiskWatchSnapshot:
    """监控层仪表盘快照（frozen 不可变）。"""

    n_symbols: int
    n_illiquid: int
    illiquid_ratio: float  # ∈[0,1]
    liquidity_level: str  # "normal" / "yellow" / "red"
    avg_pairwise_correlation: float | None  # 无相关性输入 → None
    correlation_regime: str  # "LOW" / "NORMAL" / "HIGH" / "NA"
    diversification_effective: bool
    overall_severity: str  # 各维最严
    alerts: tuple[MonitoringAlert, ...]


def assess_risk_watch(
    liquidity: Sequence[LiquidityWatchInput],
    *,
    correlation_returns: Mapping[str, Sequence[float]] | None = None,
    config: RiskWatchConfig | None = None,
) -> RiskWatchSnapshot:
    """监控层主入口：流动性分级 + 相关性体制 → 仪表盘快照 + 告警数据。

    Args:
        liquidity: 标的级流动性指标序列（非空）
        correlation_returns: {symbol: 收益率序列}（可空 → 相关性维 NA）
        config: 配置（None → 默认）

    Returns:
        RiskWatchSnapshot

    Raises:
        InvalidRiskWatchConfigError: 配置非法
        InvalidLiquidityWatchInputError: 流动性输入为空
    """
    cfg = config or RiskWatchConfig()
    items = list(liquidity)
    if not items:
        raise InvalidLiquidityWatchInputError("流动性输入不能为空")

    n = len(items)
    n_illiquid = sum(1 for x in items if x.is_illiquid)
    ratio = n_illiquid / n

    alerts: list[MonitoringAlert] = []
    if ratio >= cfg.illiquid_ratio_red:
        liquidity_level = AlertLevel.RED.value
        alerts.append(
            MonitoringAlert(
                level=AlertLevel.RED.value,
                source="liquidity_watch",
                message=f"非流动标的占比 {ratio:.1%}（{n_illiquid}/{n}）≥ 红阈 {cfg.illiquid_ratio_red:.0%}，流动性枯竭风险",
            )
        )
    elif ratio >= cfg.illiquid_ratio_yellow:
        liquidity_level = AlertLevel.YELLOW.value
        alerts.append(
            MonitoringAlert(
                level=AlertLevel.YELLOW.value,
                source="liquidity_watch",
                message=f"非流动标的占比 {ratio:.1%}（{n_illiquid}/{n}）≥ 黄阈 {cfg.illiquid_ratio_yellow:.0%}，流动性恶化预警",
            )
        )
    else:
        liquidity_level = "normal"

    avg_corr: float | None = None
    corr_regime = "NA"
    diversification = True
    corr_severity = "normal"
    if correlation_returns is not None:
        report = assess_correlation_regime(
            correlation_returns,
            low_threshold=cfg.correlation_low_threshold,
            high_threshold=cfg.correlation_high_threshold,
        )
        avg_corr = float(report.avg_pairwise_correlation)
        corr_regime = report.regime.value
        diversification = bool(report.diversification_effective)
        if report.regime is CorrelationRegime.HIGH:
            corr_severity = AlertLevel.ORANGE.value
            detail = report.warnings[0] if report.warnings else "高相关 regime"
            alerts.append(
                MonitoringAlert(
                    level=AlertLevel.ORANGE.value,
                    source="correlation_regime",
                    message=f"相关性体制 HIGH（avg={avg_corr:.3f}）：{detail}",
                )
            )

    severities = [liquidity_level, corr_severity]
    overall = max(severities, key=lambda s: _SEVERITY_ORDER[s])

    return RiskWatchSnapshot(
        n_symbols=n,
        n_illiquid=n_illiquid,
        illiquid_ratio=ratio,
        liquidity_level=liquidity_level,
        avg_pairwise_correlation=avg_corr,
        correlation_regime=corr_regime,
        diversification_effective=diversification,
        overall_severity=overall,
        alerts=tuple(alerts),
    )
