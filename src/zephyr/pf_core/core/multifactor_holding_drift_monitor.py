# [BLUEPRINT] MOD-PF-002 | docs/03_modules/_domain_portfolio_core/portfolio_optimizer/blueprint.md
# [MODULE] zephyr.pf_core.core.multifactor_holding_drift_monitor
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] 无（纯函数）; critical输出喂 multifactor_rebalance_trigger 强制换仓
# [CONSUMERS] multifactor_pit_backtest; PortfolioOptimizer 每日盘后调用
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] critical>0→should_trigger_rebalance=True(覆盖时间/漂移/信号三触发器); C2/C6约束持续满足
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空暴露字典->零偏差无警报
# [TESTS] tests/pf_core/test_multifactor_holding_drift_monitor.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: current/target 因子暴露 + current/target 行业暴露 + weight_drift(权重漂移)
# I2: HoldingDriftParams(factor alert 0.05/critical 0.10(C6边界); industry alert 0.03/critical 0.05(C2边界); weight alert 0.10→喂RebalanceTrigger 15%阈值)
# F1: monitor每日盘后(①因子暴露偏差→FACTOR_CRITICAL/FACTOR_ALERT ②行业偏差→INDUSTRY_CRITICAL/INDUSTRY_ALERT ③权重漂移>10%→WEIGHT_DRIFT/FEED_REBALANCE_TRIGGER)
# O1: HoldingDriftReport(alerts/critical_count/should_trigger_rebalance/weight_drift)
# [/ALGO_FLOW]
"""25号memo §3.7#8 持仓偏差监控（HoldingDriftMonitor，MVP 即做）。

§3.5 约束链在优化器求解时生效，但持仓后价格变化使实际因子/行业暴露偏离目标。
§3.7#6 的漂移触发（15%）只监控权重漂移，本模块补"换仓后到下次换仓期间偏差
谁来管"的断裂点——每日盘后监控因子暴露偏差（C6 边界 ±10%）与行业偏离
（C2 边界 ±5%），critical 时触发 RebalanceTrigger 强制换仓（覆盖三触发器）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__all__ = [
    "HoldingDriftParams",
    "DriftAlertType",
    "DriftAlert",
    "HoldingDriftReport",
    "monitor",
]


@dataclass(frozen=True)
class HoldingDriftParams:
    """持仓偏差监控阈值（25号memo §3.7#8 参数表）。"""

    factor_drift_alert: float = 0.05      # 因子暴露偏差>5%→预警
    factor_drift_critical: float = 0.10   # 偏差>10%→触发换仓（C6 约束边界）
    industry_drift_alert: float = 0.03    # 行业偏离>3%→预警
    industry_drift_critical: float = 0.05  # 偏差>5%→触发换仓（C2 约束边界）
    weight_drift_alert: float = 0.10      # 权重漂移>10%→预警（喂 RebalanceTrigger 15%）


class DriftAlertType(str, Enum):
    FACTOR_CRITICAL = "FACTOR_CRITICAL"      # →TRIGGER_REBALANCE
    FACTOR_ALERT = "FACTOR_ALERT"            # →MONITOR
    INDUSTRY_CRITICAL = "INDUSTRY_CRITICAL"  # →TRIGGER_REBALANCE
    INDUSTRY_ALERT = "INDUSTRY_ALERT"        # →MONITOR
    WEIGHT_DRIFT = "WEIGHT_DRIFT"            # →FEED_REBALANCE_TRIGGER


@dataclass(frozen=True)
class DriftAlert:
    """单条偏差警报。"""

    alert_type: DriftAlertType
    name: str          # 因子名/行业名/组合级 "portfolio"
    deviation: float   # |current - target|


@dataclass(frozen=True)
class HoldingDriftReport:
    """持仓偏差监控报告。"""

    alerts: tuple[DriftAlert, ...] = ()
    critical_count: int = 0
    should_trigger_rebalance: bool = False
    weight_drift: float = 0.0


def _check_exposures(
    current: dict[str, float],
    target: dict[str, float],
    alert_th: float,
    critical_th: float,
    alert_type: DriftAlertType,
    critical_type: DriftAlertType,
) -> list[DriftAlert]:
    """逐项暴露偏差检查（current/target 并集键）。"""
    alerts: list[DriftAlert] = []
    for key in set(current) | set(target):
        dev = abs(float(current.get(key, 0.0)) - float(target.get(key, 0.0)))
        if dev > critical_th:
            alerts.append(DriftAlert(critical_type, key, dev))
        elif dev > alert_th:
            alerts.append(DriftAlert(alert_type, key, dev))
    return alerts


def monitor(
    current_factor_exposure: dict[str, float] | None = None,
    target_factor_exposure: dict[str, float] | None = None,
    current_industry_exposure: dict[str, float] | None = None,
    target_industry_exposure: dict[str, float] | None = None,
    weight_drift: float = 0.0,
    params: HoldingDriftParams | None = None,
) -> HoldingDriftReport:
    """持仓偏差监控（每日盘后）。

    Returns:
        HoldingDriftReport。critical>0 → should_trigger_rebalance=True，
        触发 RebalanceTrigger 强制换仓（覆盖时间/漂移/信号三触发器）。
    """
    p = params or HoldingDriftParams()
    alerts: list[DriftAlert] = []
    alerts += _check_exposures(
        current_factor_exposure or {}, target_factor_exposure or {},
        p.factor_drift_alert, p.factor_drift_critical,
        DriftAlertType.FACTOR_ALERT, DriftAlertType.FACTOR_CRITICAL,
    )
    alerts += _check_exposures(
        current_industry_exposure or {}, target_industry_exposure or {},
        p.industry_drift_alert, p.industry_drift_critical,
        DriftAlertType.INDUSTRY_ALERT, DriftAlertType.INDUSTRY_CRITICAL,
    )
    if weight_drift > p.weight_drift_alert:
        alerts.append(DriftAlert(DriftAlertType.WEIGHT_DRIFT, "portfolio", float(weight_drift)))
    critical = sum(1 for a in alerts if a.alert_type in
                   (DriftAlertType.FACTOR_CRITICAL, DriftAlertType.INDUSTRY_CRITICAL))
    return HoldingDriftReport(
        alerts=tuple(alerts),
        critical_count=critical,
        should_trigger_rebalance=critical > 0,
        weight_drift=float(weight_drift),
    )
