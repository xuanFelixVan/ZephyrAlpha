# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
# CODEGEN-GUARD: CTR-declarations-manual
# Phase D — codegen auto-override disabled.
# All exports below are manually maintained.
# DO NOT run generate_contracts.py without removing this guard.
"""
ZephyrAlpha — shared/contracts/

Backward-compat re-export facade. Canonical trading-domain types now live in
zephyr.trading_contracts. This module re-exports them so existing imports
continue to work.
"""

from zephyr.shared.contracts.backpressure import (
    BackpressurePause,
    BackpressureResume,
    BackpressureThrottle,
)
from zephyr.shared.contracts.core.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)
from zephyr.shared.contracts.errors import (
    ContractViolationError as ContractErrViolationError,
    DataQualityError,
    ExecutionRejectionError,
    FactorComputationError,
    RiskLimitViolationError,
    SignalDegradationWarning,
)
from zephyr.trading_contracts.market.factor_signal import FactorSignal
from zephyr.trading_contracts.execution.fill import Fill
from zephyr.trading_contracts.market.instrument import (
    ETF,
    FX,
    AssetClass,
    Bond,
    Country,
    Crypto,
    CryptoContractType,
    CurrencyCode,
    Exchange,
    Future,
    Instrument,
    Jurisdiction,
    Option,
    OptionType,
    Stock,
    TradingCalendarName,
)
from zephyr.trading_contracts.market.market_data import NormalizedMarketData
from zephyr.shared.contracts.portfolio.money import (
    Money,
    MoneyCurrencyMismatchError,
    MoneyPrecisionError,
)
from zephyr.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading_contracts.execution.position import PositionSnapshot
from zephyr.shared.contracts.core.registry import (
    ContractMeta,
    ContractRegistry,
    VersionMismatchError,
    VersionTransition,
    get_registry,
    reset_registry,
)
from zephyr.trading_contracts.risk.risk_limits import RiskLimits
from zephyr.shared.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.contracts.core.timestamp import (
    NaiveDatetimeError,
    Timestamp,
    ensure_utc,
    utcnow,
)
from zephyr.shared.contracts.core.trace_context import TraceContext
from zephyr.trading_contracts.market.synthesized_signal import SynthesizedSignal
from zephyr.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.shared.contracts.portfolio.performance_attribution_report import PerformanceAttributionReport
from zephyr.shared.contracts.core.system_configuration import SystemConfiguration
from zephyr.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.trading_contracts.risk.risk_metrics import RiskMetricsReport
from zephyr.shared.contracts.experiment.experiment_result import ExperimentResult
from zephyr.trading_contracts.risk.compliance_rule import ComplianceRule
from zephyr.shared.contracts.portfolio.strategy_lifecycle_event import StrategyLifecycleEvent
from zephyr.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading_contracts.execution.model_serving_request import ModelServingRequest
from zephyr.shared.contracts.experiment.model_serving_response import ModelServingResponse
from zephyr.shared.contracts.core.telemetry_emitter import TelemetryEmitter
from zephyr.shared.contracts.core.factories import (
    make_factor_signal,
    make_order,
    make_risk_dashboard_snapshot,
    make_risk_limits,
    make_risk_metrics_report,
    make_synthesized_signal,
)
from zephyr.shared.contracts.escalation import BudgetAlert, BudgetSeverity, BudgetType
from zephyr.shared.contracts.identity import (
    AgentIdentity,
    AgentMaturity,
    AgentRole,
    GuardDecision,
    GuardResult,
    IDESource,
    MaturityLevel,
)

__all__ = [
    "NormalizedMarketData",
    "FactorSignal",
    "RiskLimits",
    "Order",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "Fill",
    "PositionSnapshot",
    "ContractViolationError",
    "EnforcementMode",
    "enforce_output",
    "enforce_input",
    "enforce",
    "AssetClass",
    "Exchange",
    "Country",
    "CurrencyCode",
    "Jurisdiction",
    "TradingCalendarName",
    "Instrument",
    "Stock",
    "ETF",
    "Future",
    "Option",
    "OptionType",
    "Bond",
    "FX",
    "Crypto",
    "CryptoContractType",
    "Money",
    "MoneyPrecisionError",
    "MoneyCurrencyMismatchError",
    "Timestamp",
    "utcnow",
    "ensure_utc",
    "NaiveDatetimeError",
    "RuntimePlane",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_LATENCY_BUDGET_MS",
    "HOT_PATH_ACTIVATED",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "TraceContext",
    "DataQualityError",
    "FactorComputationError",
    "SignalDegradationWarning",
    "RiskLimitViolationError",
    "ExecutionRejectionError",
    "ContractErrViolationError",
    "BackpressurePause",
    "BackpressureThrottle",
    "BackpressureResume",
    "ContractRegistry",
    "ContractMeta",
    "VersionTransition",
    "VersionMismatchError",
    "get_registry",
    "reset_registry",
    "SynthesizedSignal",
    "CapitalAllocationResult",
    "PerformanceAttributionReport",
    "SystemConfiguration",
    "RiskDashboardSnapshot",
    "RiskMetricsReport",
    "ExperimentResult",
    "ComplianceRule",
    "StrategyLifecycleEvent",
    "ExecutionReport",
    "ModelServingRequest",
    "ModelServingResponse",
    "TelemetryEmitter",
    "make_risk_limits",
    "make_risk_dashboard_snapshot",
    "make_risk_metrics_report",
    "make_factor_signal",
    "make_synthesized_signal",
    "make_order",
    "BudgetAlert",
    "BudgetSeverity",
    "BudgetType",
    "AgentIdentity",
    "AgentMaturity",
    "AgentRole",
    "GuardDecision",
    "GuardResult",
    "IDESource",
    "MaturityLevel",
]
