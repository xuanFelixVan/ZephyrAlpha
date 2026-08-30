# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.factories
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
shared/contracts/factories.py — 跨层数据契约工厂方法

Phase D-3: 提供跨层数据转换的工厂方法，统一处理 float->Decimal 边界转换。

SSoT: cross_layer_contracts.yaml v3.0
Status: HAND-MAINTAINED — codegen disabled (Phase D)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: as_of_date 参数
#   fields: 参数 as_of_date，类型注解 datetime | None
#   code: factories.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: idempotency_key 参数
#   fields: 参数 idempotency_key，类型注解 str
#   code: factories.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_single_position 参数
#   fields: 参数 max_single_position，类型注解 float
#   code: factories.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: min_single_position 参数
#   fields: 参数 min_single_position，类型注解 float
#   code: factories.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① make_risk_limits
#   name_en: make_risk_limits
#   intro: 创建 RiskLimits 实例——与 CTR-003（float VaR 上限）对齐。
#   desc: 创建 RiskLimits 实例——与 CTR-003（float VaR 上限）对齐。 5.150.10 治本：本函数为 backward-compat 薄委托——业务逻辑 c…；源码 L136-L167
#   inputs: as_of_date idempotency_key max_single_position min_single_position ma…
#   outputs: 返回值
# - id: A2
#   name_zh: ② make_risk_dashboard_snapshot
#   name_en: make_risk_dashboard_snapshot
#   intro: 创建 RiskDashboardSnapshot——用于 D_RISK->D_FRONTEND 监控面板推送。
#   desc: 创建 RiskDashboardSnapshot——用于 D_RISK->D_FRONTEND 监控面板推送。 5.150.11 治本：本函数为 backward-compat…；源码 L175-L204
#   inputs: portfolio_id portfolio_var_1d max_drawdown_current gross_leverage top…
#   outputs: 返回值
# - id: A3
#   name_zh: ③ make_risk_metrics_report
#   name_en: make_risk_metrics_report
#   intro: 创建 RiskMetricsReport——用于 D_RISK->D_PORTFOLIO_CORE/D_REPORTI…
#   desc: 创建 RiskMetricsReport——用于 D_RISK->D_PORTFOLIO_CORE/D_REPORTING/D_FRONTEND/D_COMPLIANCE 风险指…；源码 L212-L257
#   inputs: portfolio_id var_1d_95 var_1d_99 cvar_1d_95 cvar_1d_99 max_drawdown c…
#   outputs: 返回值
# - id: A4
#   name_zh: ④ make_factor_signal
#   name_en: make_factor_signal
#   intro: 创建 FactorSignal 实例——因子信号标准化入口。
#   desc: 创建 FactorSignal 实例——因子信号标准化入口。；源码 L265-L287
#   inputs: factor_id symbol raw_value normalized_value rank_pct confidence as_of…
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ make_synthesized_signal
#   name_en: make_synthesized_signal
#   intro: 创建 SynthesizedSignal 实例——D_SIGNAL 合成信号标准化入口。
#   desc: 创建 SynthesizedSignal 实例——D_SIGNAL 合成信号标准化入口。；源码 L295-L325
#   inputs: signal_id symbol signal_value signal_direction confidence contributin…
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ make_order
#   name_en: make_order
#   intro: 创建 Order 实例——D_PORTFOLIO_CORE 委托指令标准化入口。
#   desc: 创建 Order 实例——D_PORTFOLIO_CORE 委托指令标准化入口。；源码 L333-L356
#   inputs: order_id symbol side order_type quantity strategy_id limit_price idem…
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: make_risk_limits, make_risk_dashboard_snapshot, make_risk_metrics_report, make_…
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import importlib
from datetime import UTC, datetime
from decimal import Decimal


def _to_decimal(value: float | int | str | Decimal | None) -> Decimal:
    """Safe float/str/int -> Decimal 转换，禁止 float 直接传入。"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(str(value)) if value is not None else Decimal("0")


def _optional_decimal(value: float | int | str | Decimal | None) -> Decimal | None:
    """Optional Decimal 转换——None -> None。"""
    if value is None:
        return None
    return _to_decimal(value)


# ═══════════════════════════════════════════════════════════════════
# RiskLimits 工厂方法
# ═══════════════════════════════════════════════════════════════════


def make_risk_limits(
    as_of_date: datetime | None = None,
    idempotency_key: str = "",
    max_single_position: float = 0.10,
    min_single_position: float = 0.0,
    max_gross_leverage: float = 1.0,
    max_sector_concentration: float = 0.30,
    max_portfolio_var_1d: float | Decimal | None = None,
    max_drawdown_limit: float | None = None,
    symbol_overrides: dict[str, float] | None = None,
):
    """创建 RiskLimits 实例——与 CTR-003（float VaR 上限）对齐。

    5.150.10 治本：本函数为 backward-compat 薄委托——业务逻辑 canonical 实现位于
    `zephyr.trading.trading_contracts.factories.make_risk_limits`（参数对象版本）。
    此处经 importlib 惰性加载打破 shared(L0)→trading(L2) 静态依赖，保留旧位置/
    关键字签名以兼容历史调用方（当前 0 消费，仅为 API 兼容兜底）。
    """
    _fac = importlib.import_module("zephyr.trading.trading_contracts.factories")
    _params_cls = _fac.RiskLimitsParams
    params = _params_cls(
        as_of_date=as_of_date,
        idempotency_key=idempotency_key,
        max_single_position=max_single_position,
        min_single_position=min_single_position,
        max_gross_leverage=max_gross_leverage,
        max_sector_concentration=max_sector_concentration,
        max_portfolio_var_1d=max_portfolio_var_1d,
        max_drawdown_limit=max_drawdown_limit,
        symbol_overrides=symbol_overrides,
    )
    return _fac.make_risk_limits(params)


# ═══════════════════════════════════════════════════════════════════
# RiskDashboardSnapshot 工厂方法
# ═══════════════════════════════════════════════════════════════════


def make_risk_dashboard_snapshot(
    portfolio_id: str,
    portfolio_var_1d: Decimal | float,
    max_drawdown_current: float = 0.0,
    gross_leverage: float = 0.0,
    top_position_concentration: float = 0.0,
    sector_concentrations: dict[str, float] | None = None,
    active_alerts: list[str] | None = None,
    overall_risk_score: float = 0.0,
    idempotency_key: str = "",
):
    """创建 RiskDashboardSnapshot——用于 D_RISK->D_FRONTEND 监控面板推送。

    5.150.11 治本：本函数为 backward-compat 薄委托——业务逻辑 canonical 实现位于
    `zephyr.trading.trading_contracts.factories.make_risk_dashboard_snapshot`（参数对象版本）。
    """
    _fac = importlib.import_module("zephyr.trading.trading_contracts.factories")
    _params_cls = _fac.RiskDashboardSnapshotParams
    params = _params_cls(
        portfolio_id=portfolio_id,
        portfolio_var_1d=portfolio_var_1d,
        max_drawdown_current=max_drawdown_current,
        gross_leverage=gross_leverage,
        top_position_concentration=top_position_concentration,
        sector_concentrations=sector_concentrations,
        active_alerts=active_alerts,
        overall_risk_score=overall_risk_score,
        idempotency_key=idempotency_key,
    )
    return _fac.make_risk_dashboard_snapshot(params)


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
    as_of_date: datetime | None = None,
):
    """创建 RiskMetricsReport——用于 D_RISK->D_PORTFOLIO_CORE/D_REPORTING/D_FRONTEND/D_COMPLIANCE 风险指标推送。

    5.150.5 治本：本函数为 backward-compat 薄委托——业务逻辑 canonical 实现位于
    `zephyr.trading.trading_contracts.factories.make_risk_metrics_report`（参数对象版本）。
    """
    _fac = importlib.import_module("zephyr.trading.trading_contracts.factories")
    _params_cls = _fac.RiskMetricsReportParams
    params = _params_cls(
        portfolio_id=portfolio_id,
        var_1d_95=var_1d_95,
        var_1d_99=var_1d_99,
        cvar_1d_95=cvar_1d_95,
        cvar_1d_99=cvar_1d_99,
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
        idempotency_key=idempotency_key,
        as_of_date=as_of_date,
    )
    return _fac.make_risk_metrics_report(params)


# ═══════════════════════════════════════════════════════════════════
# FactorSignal 工厂方法
# ═══════════════════════════════════════════════════════════════════


def make_factor_signal(
    factor_id: str,
    symbol: str,
    raw_value: float,
    normalized_value: float | None = None,
    rank_pct: float | None = None,
    confidence: float = 1.0,
    as_of_date: datetime | None = None,
    idempotency_key: str = "",
):
    """创建 FactorSignal 实例——因子信号标准化入口。"""
    _mod = importlib.import_module("zephyr.trading.trading_contracts.market.factor_signal")
    _FactorSignal = _mod.FactorSignal
    return _FactorSignal(
        as_of_date=as_of_date or datetime.now(UTC),
        factor_id=factor_id,
        idempotency_key=idempotency_key or f"fsig-{factor_id}-{symbol}-{int(datetime.now(UTC).timestamp())}",
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
    contributing_factors: dict[str, float],
    generation_latency_ms: int,
    regime: str | None = None,
    suggested_position_pct: float | None = None,
    is_degraded: bool = False,
    idempotency_key: str = "",
    as_of_timestamp: datetime | None = None,
):
    """创建 SynthesizedSignal 实例——D_SIGNAL 合成信号标准化入口。"""
    _mod = importlib.import_module("zephyr.trading.trading_contracts.market.synthesized_signal")
    _SynthesizedSignal = _mod.SynthesizedSignal
    return _SynthesizedSignal(
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


# ═══════════════════════════════════════════════════════════════════
# Order 工厂方法
# ═══════════════════════════════════════════════════════════════════


def make_order(
    order_id: str,
    symbol: str,
    side,  # OrderSide — lazy imported
    order_type,  # OrderType — lazy imported
    quantity: Decimal,
    strategy_id: str,
    limit_price: Decimal | None = None,
    idempotency_key: str = "",
):
    """创建 Order 实例——D_PORTFOLIO_CORE 委托指令标准化入口。"""
    _mod = importlib.import_module("zephyr.trading.trading_contracts.execution.order")
    _Order = _mod.Order
    return _Order(
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
    "_optional_decimal",
    "_to_decimal",
    "make_factor_signal",
    "make_order",
    "make_risk_dashboard_snapshot",
    "make_risk_limits",
    "make_risk_metrics_report",
    "make_synthesized_signal",
]
