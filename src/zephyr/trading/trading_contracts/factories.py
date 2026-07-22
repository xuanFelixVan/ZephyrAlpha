# [BLUEPRINT] MOD-TRADING-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.factories
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.execution.order; zephyr.shared.contracts.factor_signal; zephyr.shared.contracts.synthesized_signal; zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot; zephyr.trading.trading_contracts.risk.risk_limits; zephyr.trading.trading_contracts.risk.risk_metrics; zephyr.shared.contracts.core.factories
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 工厂方法仅创建trading_contracts内定义的类型实例
# [MODIFY-GUARD] 新增工厂方法须同步更新__all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError: 参数越界
# [TESTS] tests/test_trading_contracts_factories.py
# [A_module] module_id=MOD-UNK-factories | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""trading-contracts/factories.py — 交易域数据契约工厂方法

从 shared/contracts/core/factories.py 迁移至此——工厂方法创建交易域对象，
属于交易域而非基础设施层。消除 shared -> trading-contracts 的架构违规。

Phase D-3: 提供跨层数据转换的工厂方法，统一处理 float->Decimal 边界转换。

5.150 参数对象化（Long Parameter List 治本）：3 个 risk 工厂改收单一参数对象
（RiskLimitsParams / RiskDashboardSnapshotParams / RiskMetricsReportParams）。
旧调用过渡路径：
    - 关键字参数原样透传（make_risk_limits(max_single_position=0.2) 仍可用）；
    - 位置参数经参数对象构造函数（字段顺序与旧签名 1:1，如 RiskLimitsParams(None, "", 0.2)）。

SSoT: cross_layer_contracts.yaml v3.0
Status: HAND-MAINTAINED — codegen disabled (Phase D)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, TypeVar

from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderType
from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal
from zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.trading.trading_contracts.risk.risk_limits import RiskLimits
from zephyr.trading.trading_contracts.risk.risk_metrics import RiskMetricsReport

_P = TypeVar("_P")


def _to_decimal(value: float | int | str | Decimal | None) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(str(value)) if value is not None else Decimal("0")


def _optional_decimal(value: float | int | str | Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return _to_decimal(value)


def _coerce_params(params: _P | None, params_cls: type[_P], kwargs: dict[str, Any], factory_name: str) -> _P:
    """工厂参数收口：params 优先；kwargs 经参数对象构造函数过渡；混用/类型错误显式拒绝。"""
    if params is None:
        return params_cls(**kwargs)
    if kwargs:
        raise TypeError(f"{factory_name}: params 与关键字参数不可混用")
    if not isinstance(params, params_cls):
        raise TypeError(f"{factory_name}: params 须为 {params_cls.__name__}，收到 {type(params).__name__}")
    return params


@dataclass(frozen=True)
class RiskLimitsParams:
    """make_risk_limits 参数对象（5.150 Long Parameter List 治本）。

    字段顺序与 5.150 前 make_risk_limits 签名 1:1，构造函数即旧签名过渡入口
    （NO-LONG-PARAM-LIST gate 禁止 from_params 类方法形态的长签名）。
    """

    as_of_date: datetime | None = None
    idempotency_key: str = ""
    max_single_position: float = 0.10
    min_single_position: float = 0.0
    max_gross_leverage: float = 1.0
    max_sector_concentration: float = 0.30
    max_portfolio_var_1d: float | Decimal | None = None
    max_drawdown_limit: float | None = None
    symbol_overrides: dict[str, float] | None = None


@dataclass(frozen=True)
class RiskDashboardSnapshotParams:
    """make_risk_dashboard_snapshot 参数对象（5.150 Long Parameter List 治本）。

    字段顺序与 5.150 前 make_risk_dashboard_snapshot 签名 1:1，构造函数即旧签名过渡入口。
    """

    portfolio_id: str
    portfolio_var_1d: Decimal | float
    max_drawdown_current: float = 0.0
    gross_leverage: float = 0.0
    top_position_concentration: float = 0.0
    sector_concentrations: dict[str, float] | None = None
    active_alerts: list[str] | None = None
    overall_risk_score: float = 0.0
    idempotency_key: str = ""


@dataclass(frozen=True)
class RiskMetricsReportParams:
    """make_risk_metrics_report 参数对象（5.150 Long Parameter List 治本）。

    字段顺序与 5.150 前 make_risk_metrics_report 签名 1:1，构造函数即旧签名过渡入口。
    """

    portfolio_id: str
    var_1d_95: Decimal
    var_1d_99: Decimal
    cvar_1d_95: Decimal
    cvar_1d_99: Decimal
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    beta: float = 1.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    volatility_1d: float = 0.0
    volatility_1m: float = 0.0
    calculation_method: str = "historical"
    confidence_level: float = 0.95
    lookback_period: int = 252
    idempotency_key: str = ""
    as_of_date: datetime | None = None


def make_risk_limits(params: RiskLimitsParams | None = None, **kwargs: Any) -> RiskLimits:
    """创建 RiskLimits——单一参数对象入口（旧签名经 **kwargs/参数对象位置构造过渡）。"""
    params = _coerce_params(params, RiskLimitsParams, kwargs, "make_risk_limits")
    mpv: float | None = None
    if params.max_portfolio_var_1d is not None:
        mpv = float(params.max_portfolio_var_1d)
    return RiskLimits(
        as_of_date=params.as_of_date or datetime.now(UTC),
        idempotency_key=params.idempotency_key or f"limits-{int(datetime.now(UTC).timestamp())}",
        max_single_position=params.max_single_position,
        min_single_position=params.min_single_position,
        max_gross_leverage=params.max_gross_leverage,
        max_sector_concentration=params.max_sector_concentration,
        max_portfolio_var_1d=mpv,
        max_drawdown_limit=params.max_drawdown_limit,
        symbol_overrides=params.symbol_overrides or {},
    )


def make_risk_dashboard_snapshot(
    params: RiskDashboardSnapshotParams | None = None,
    **kwargs: Any,
) -> RiskDashboardSnapshot:
    """创建 RiskDashboardSnapshot——单一参数对象入口（旧签名经 **kwargs/参数对象位置构造过渡）。"""
    params = _coerce_params(params, RiskDashboardSnapshotParams, kwargs, "make_risk_dashboard_snapshot")
    return RiskDashboardSnapshot(
        snapshot_time=datetime.now(UTC).isoformat(),
        portfolio_id=params.portfolio_id,
        portfolio_var_1d=float(params.portfolio_var_1d),
        max_drawdown_current=params.max_drawdown_current,
        gross_leverage=params.gross_leverage,
        top_position_concentration=params.top_position_concentration,
        sector_concentrations=params.sector_concentrations or {},
        active_alerts=params.active_alerts or [],
        overall_risk_score=params.overall_risk_score,
        idempotency_key=params.idempotency_key or f"snap-{int(datetime.now(UTC).timestamp())}",
    )


def make_risk_metrics_report(
    params: RiskMetricsReportParams | None = None,
    **kwargs: Any,
) -> RiskMetricsReport:
    """创建 RiskMetricsReport——单一参数对象入口（旧签名经 **kwargs/参数对象位置构造过渡）。"""
    params = _coerce_params(params, RiskMetricsReportParams, kwargs, "make_risk_metrics_report")
    return RiskMetricsReport(
        portfolio_id=params.portfolio_id,
        as_of_date=params.as_of_date or datetime.now(UTC),
        var_1d_95=float(params.var_1d_95),
        var_1d_99=float(params.var_1d_99),
        cvar_1d_95=float(params.cvar_1d_95),
        cvar_1d_99=float(params.cvar_1d_99),
        max_drawdown=params.max_drawdown,
        current_drawdown=params.current_drawdown,
        beta=params.beta,
        sharpe_ratio=params.sharpe_ratio,
        sortino_ratio=params.sortino_ratio,
        volatility_1d=params.volatility_1d,
        volatility_1m=params.volatility_1m,
        calculation_method=params.calculation_method,
        confidence_level=params.confidence_level,
        lookback_period=params.lookback_period,
        idempotency_key=params.idempotency_key or f"metrics-{int(datetime.now(UTC).timestamp())}",
    )


def make_factor_signal(
    factor_id: str,
    symbol: str,
    raw_value: float,
    normalized_value: float | None = None,
    rank_pct: float | None = None,
    confidence: float = 1.0,
    as_of_date: datetime | None = None,
    idempotency_key: str = "",
) -> FactorSignal:
    return FactorSignal(
        as_of_date=as_of_date or datetime.now(UTC),
        factor_id=factor_id,
        idempotency_key=idempotency_key or f"fsig-{factor_id}-{symbol}-{int(datetime.now(UTC).timestamp())}",
        raw_value=raw_value,
        symbol=symbol,
        confidence=confidence,
        normalized_value=normalized_value,
        rank_pct=rank_pct,
    )


def make_synthesized_signal(
    signal_id: str,
    symbol: str,
    signal_value: float,
    signal_direction: str,
    confidence: float,
    contributing_factors: dict[str, float],
    generation_latency_ms: int,
    regime: str | None = None,
    suggested_position_pct: float | None = None,
    is_degraded: bool = False,
    idempotency_key: str = "",
    as_of_timestamp: datetime | None = None,
) -> SynthesizedSignal:
    return SynthesizedSignal(
        signal_id=signal_id,
        symbol=symbol,
        as_of_timestamp=as_of_timestamp or datetime.now(UTC),
        signal_value=signal_value,
        signal_direction=signal_direction,
        confidence=confidence,
        contributing_factors=contributing_factors,
        generation_latency_ms=generation_latency_ms,
        regime=regime,
        suggested_position_pct=suggested_position_pct,
        is_degraded=is_degraded,
        idempotency_key=idempotency_key or f"ssig-{signal_id}-{int(datetime.now(UTC).timestamp())}",
    )


def make_order(
    order_id: str,
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    quantity: Decimal,
    strategy_id: str,
    limit_price: Decimal | None = None,
    idempotency_key: str = "",
) -> Order:
    return Order(
        idempotency_key=idempotency_key or f"ord-{order_id}",
        order_id=order_id,
        order_type=order_type,
        quantity=quantity,
        side=side,
        strategy_id=strategy_id,
        symbol=symbol,
        limit_price=limit_price,
        created_at=datetime.now(UTC),
    )


__all__ = [
    "RiskDashboardSnapshotParams",
    "RiskLimitsParams",
    "RiskMetricsReportParams",
    "_optional_decimal",
    "_to_decimal",
    "make_factor_signal",
    "make_order",
    "make_risk_dashboard_snapshot",
    "make_risk_limits",
    "make_risk_metrics_report",
    "make_synthesized_signal",
]
