"""shared/contracts/factories.py — 跨层数据契约工厂方法

Phase D-3: 提供跨层数据转换的工厂方法，统一处理 float→Decimal 边界转换。

SSoT: cross-layer-contracts.yaml v3.0
Status: HAND-MAINTAINED — codegen disabled (Phase D)
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.shared.contracts.order import Order, OrderSide, OrderType
from zephyr.shared.contracts.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.contracts.risk_metrics import RiskMetricsReport
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal


def _to_decimal(value: Any) -> Decimal:
    """Safe float/str/int → Decimal 转换，禁止 float 直接传入。"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(str(value)) if value is not None else Decimal("0")


def _optional_decimal(value: Any) -> Optional[Decimal]:
    """Optional Decimal 转换——None → None。"""
    if value is None:
        return None
    return _to_decimal(value)


# ═══════════════════════════════════════════════════════════════════
# RiskLimits 工厂方法
# ═══════════════════════════════════════════════════════════════════

def make_risk_limits(
    as_of_date: Optional[datetime] = None,
    idempotency_key: str = "",
    max_single_position: float = 0.10,
    min_single_position: float = 0.0,
    max_gross_leverage: float = 1.0,
    max_sector_concentration: float = 0.30,
    max_portfolio_var_1d: float | Decimal | None = None,
    max_drawdown_limit: Optional[float] = None,
    symbol_overrides: Optional[Dict[str, float]] = None,
) -> RiskLimits:
    """创建 RiskLimits 实例——与 CTR-003（float VaR 上限）对齐。"""
    mpv: Optional[float] = None
    if max_portfolio_var_1d is not None:
        mpv = float(max_portfolio_var_1d)
    return RiskLimits(
        as_of_date=as_of_date or datetime.now(timezone.utc),
        idempotency_key=idempotency_key or f"limits-{int(datetime.now(timezone.utc).timestamp())}",
        max_single_position=max_single_position,
        min_single_position=min_single_position,
        max_gross_leverage=max_gross_leverage,
        max_sector_concentration=max_sector_concentration,
        max_portfolio_var_1d=mpv,
        max_drawdown_limit=max_drawdown_limit,
        symbol_overrides=symbol_overrides or {},
    )


# ═══════════════════════════════════════════════════════════════════
# RiskDashboardSnapshot 工厂方法
# ═══════════════════════════════════════════════════════════════════

def make_risk_dashboard_snapshot(
    portfolio_id: str,
    portfolio_var_1d: Decimal | float,
    max_drawdown_current: float = 0.0,
    gross_leverage: float = 0.0,
    top_position_concentration: float = 0.0,
    sector_concentrations: Optional[Dict[str, float]] = None,
    active_alerts: Optional[List[str]] = None,
    overall_risk_score: float = 0.0,
    idempotency_key: str = "",
) -> RiskDashboardSnapshot:
    """创建 RiskDashboardSnapshot——用于 L04→L08 监控面板推送。"""
    return RiskDashboardSnapshot(
        snapshot_time=datetime.now(timezone.utc).isoformat(),
        portfolio_id=portfolio_id,
        portfolio_var_1d=float(portfolio_var_1d),
        max_drawdown_current=max_drawdown_current,
        gross_leverage=gross_leverage,
        top_position_concentration=top_position_concentration,
        sector_concentrations=sector_concentrations or {},
        active_alerts=active_alerts or [],
        overall_risk_score=overall_risk_score,
        idempotency_key=idempotency_key or f"snap-{int(datetime.now(timezone.utc).timestamp())}",
    )


# ═══════════════════════════════════════════════════════════════════
# RiskMetricsReport 工厂方法
# ═══════════════════════════════════════════════════════════════════

def make_risk_metrics_report(
    portfolio_id: str,
    var_1d_95: Decimal,
    var_1d_99: Decimal,
    cvar_1d_95: Decimal,
    cvar_1d_99: Decimal,
    max_drawdown: float = 0.0,
    current_drawdown: float = 0.0,
    beta: float = 1.0,
    sharpe_ratio: float = 0.0,
    sortino_ratio: float = 0.0,
    volatility_1d: float = 0.0,
    volatility_1m: float = 0.0,
    calculation_method: str = "historical",
    confidence_level: float = 0.95,
    lookback_period: int = 252,
    idempotency_key: str = "",
    as_of_date: Optional[datetime] = None,
) -> RiskMetricsReport:
    """创建 RiskMetricsReport——用于 L04→L05/L07/L08/L10 风险指标推送。"""
    return RiskMetricsReport(
        portfolio_id=portfolio_id,
        as_of_date=as_of_date or datetime.now(timezone.utc),
        var_1d_95=float(var_1d_95),
        var_1d_99=float(var_1d_99),
        cvar_1d_95=float(cvar_1d_95),
        cvar_1d_99=float(cvar_1d_99),
        max_drawdown=max_drawdown,
        current_drawdown=current_drawdown,
        beta=beta,
        sharpe_ratio=sharpe_ratio,
        sortino_ratio=sortino_ratio,
        volatility_1d=volatility_1d,
        volatility_1m=volatility_1m,
        calculation_method=calculation_method,
        confidence_level=confidence_level,
        lookback_period=lookback_period,
        idempotency_key=idempotency_key or f"metrics-{int(datetime.now(timezone.utc).timestamp())}",
    )


# ═══════════════════════════════════════════════════════════════════
# FactorSignal 工厂方法
# ═══════════════════════════════════════════════════════════════════

def make_factor_signal(
    factor_id: str,
    symbol: str,
    raw_value: float,
    normalized_value: Optional[float] = None,
    rank_pct: Optional[float] = None,
    confidence: float = 1.0,
    as_of_date: Optional[datetime] = None,
    idempotency_key: str = "",
) -> FactorSignal:
    """创建 FactorSignal 实例——因子信号标准化入口。"""
    return FactorSignal(
        as_of_date=as_of_date or datetime.now(timezone.utc),
        factor_id=factor_id,
        idempotency_key=idempotency_key or f"fsig-{factor_id}-{symbol}-{int(datetime.now(timezone.utc).timestamp())}",
        raw_value=raw_value,
        symbol=symbol,
        confidence=confidence,
        normalized_value=normalized_value,
        rank_pct=rank_pct,
    )


# ═══════════════════════════════════════════════════════════════════
# SynthesizedSignal 工厂方法
# ═══════════════════════════════════════════════════════════════════

def make_synthesized_signal(
    signal_id: str,
    symbol: str,
    signal_value: float,
    signal_direction: str,
    confidence: float,
    contributing_factors: Dict[str, float],
    generation_latency_ms: int,
    regime: Optional[str] = None,
    suggested_position_pct: Optional[float] = None,
    is_degraded: bool = False,
    idempotency_key: str = "",
    as_of_timestamp: Optional[datetime] = None,
) -> SynthesizedSignal:
    """创建 SynthesizedSignal 实例——L03 合成信号标准化入口。"""
    return SynthesizedSignal(
        signal_id=signal_id,
        symbol=symbol,
        as_of_timestamp=as_of_timestamp or datetime.now(timezone.utc),
        signal_value=signal_value,
        signal_direction=signal_direction,
        confidence=confidence,
        contributing_factors=contributing_factors,
        generation_latency_ms=generation_latency_ms,
        regime=regime,
        suggested_position_pct=suggested_position_pct,
        is_degraded=is_degraded,
        idempotency_key=idempotency_key or f"ssig-{signal_id}-{int(datetime.now(timezone.utc).timestamp())}",
    )


# ═══════════════════════════════════════════════════════════════════
# Order 工厂方法
# ═══════════════════════════════════════════════════════════════════

def make_order(
    order_id: str,
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    quantity: Decimal,
    strategy_id: str,
    limit_price: Optional[Decimal] = None,
    idempotency_key: str = "",
) -> Order:
    """创建 Order 实例——L05 委托指令标准化入口。"""
    return Order(
        idempotency_key=idempotency_key or f"ord-{order_id}",
        order_id=order_id,
        order_type=order_type,
        quantity=quantity,
        side=side,
        strategy_id=strategy_id,
        symbol=symbol,
        limit_price=limit_price,
        created_at=datetime.now(timezone.utc),
    )


__all__ = [
    "_to_decimal",
    "_optional_decimal",
    "make_risk_limits",
    "make_risk_dashboard_snapshot",
    "make_risk_metrics_report",
    "make_factor_signal",
    "make_synthesized_signal",
    "make_order",
]
