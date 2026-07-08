# [A_module] module_id=MOD-SHR_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
# CODEGEN-GUARD: CTR-declarations-manual
# Phase D — codegen auto-override disabled.
# All exports below are manually maintained.
# DO NOT run generate_contracts.py without removing this guard.
"""
ZephyrAlpha — shared/contracts/

Backward-compat re-export facade. Canonical trading-domain types now live in
zephyr.trading.trading_contracts. This module re-exports them so existing imports
continue to work.
"""

import importlib

from zephyr.shared.contracts.core.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)
from zephyr.shared.contracts.core.factories import (
    make_factor_signal,
    make_order,
    make_risk_dashboard_snapshot,
    make_risk_limits,
    make_risk_metrics_report,
    make_synthesized_signal,
)
from zephyr.shared.contracts.core.registry import (
    ContractMeta,
    ContractRegistry,
    VersionMismatchError,
    VersionTransition,
    get_registry,
    reset_registry,
)
from zephyr.shared.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.contracts.core.system_configuration import SystemConfiguration
from zephyr.shared.contracts.telemetry_emitter import TelemetryEmitter
from zephyr.shared.contracts.core.timestamp import (
    NaiveDatetimeError,
    Timestamp,
    ensure_utc,
    utcnow,
)
from zephyr.shared.contracts.core.trace_context import TraceContext
from zephyr.shared.contracts.errors import (
    ContractViolationError as ContractErrViolationError,
)
from zephyr.shared.contracts.errors import (
    DataQualityError,
    FactorComputationError,
)
from zephyr.shared.contracts.escalation import BudgetAlert, BudgetSeverity, BudgetType
from zephyr.shared.contracts.experiment.experiment_result import ExperimentResult
from zephyr.shared.contracts.experiment.model_serving_response import ModelServingResponse
from zephyr.shared.contracts.identity import (
    AgentIdentity,
    AgentMaturity,
    AgentRole,
    GuardDecision,
    GuardResult,
    IDESource,
    MaturityLevel,
)
from zephyr.shared.contracts.llm_gateway_protocol import (
    LLMGatewayProtocol,
    LLMResponse,
    ProviderConfig,
)
from zephyr.shared.contracts.orchestration_protocol import (
    BatchOrchestratorProtocol,
    ChaosEngineProtocol,
    ShadowCanaryProtocol,
)
from zephyr.shared.contracts.portfolio.money import (
    Money,
    MoneyCurrencyMismatchError,
    MoneyPrecisionError,
)
from zephyr.shared.contracts.portfolio.performance_attribution_report import PerformanceAttributionReport
from zephyr.shared.contracts.portfolio.strategy_lifecycle_event import StrategyLifecycleEvent
from zephyr.shared.contracts.skill_protocol import (
    SkillLoaderProtocol,
    SkillRouterProtocol,
)
from zephyr.shared.contracts.task_repository_protocol import (
    TaskRepositoryProtocol,
)

# DM-367: re-export module names for audit registration
from . import llm_gateway_protocol, orchestration_protocol, skill_protocol

# Lazy imports for trading-domain symbols (upward dependency from L0 shared -> L3 trading)
_TRADING_SYMBOLS = {
    "FactorSignal": "zephyr.execution_core.trading.trading_contracts.market.factor_signal",
    "Fill": "zephyr.execution_core.trading.trading_contracts.execution.fill",
    "ETF": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "FX": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "AssetClass": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Bond": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Country": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Crypto": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "CryptoContractType": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "CurrencyCode": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Exchange": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Future": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Instrument": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Jurisdiction": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Option": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "OptionType": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "Stock": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "TradingCalendarName": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "NormalizedMarketData": "zephyr.execution_core.trading.trading_contracts.market.market_data",
    "Order": "zephyr.execution_core.trading.trading_contracts.execution.order",
    "OrderSide": "zephyr.execution_core.trading.trading_contracts.execution.order",
    "OrderStatus": "zephyr.execution_core.trading.trading_contracts.execution.order",
    "OrderType": "zephyr.execution_core.trading.trading_contracts.execution.order",
    "PositionSnapshot": "zephyr.execution_core.trading.trading_contracts.execution.position",
    "RiskLimits": "zephyr.execution_core.trading.trading_contracts.risk.risk_limits",
    "SynthesizedSignal": "zephyr.execution_core.trading.trading_contracts.market.synthesized_signal",
    "CapitalAllocationResult": "zephyr.execution_core.trading.trading_contracts.execution.capital_allocation_result",
    "RiskDashboardSnapshot": "zephyr.execution_core.trading.trading_contracts.risk.risk_dashboard_snapshot",
    "RiskMetricsReport": "zephyr.execution_core.trading.trading_contracts.risk.risk_metrics",
    "ComplianceRule": "zephyr.execution_core.trading.trading_contracts.risk.compliance_rule",
    "ExecutionReport": "zephyr.execution_core.trading.trading_contracts.execution.execution_report",
    "ModelServingRequest": "zephyr.execution_core.trading.trading_contracts.execution.model_serving_request",
    "ExecutionRejectionError": "zephyr.execution_core.trading.trading_contracts.execution.execution_rejection_error",
    "RiskLimitViolationError": "zephyr.execution_core.trading.trading_contracts.risk.risk_limit_violation_error",
    "SignalDegradationWarning": "zephyr.execution_core.trading.trading_contracts.market.signal_degradation_warning",
}

_BACKPRESSURE_SYMBOLS = {
    "BackpressurePause",
    "BackpressureThrottle",
    "BackpressureResume",
}


def __getattr__(name):
    if name in _TRADING_SYMBOLS:
        mod = importlib.import_module(_TRADING_SYMBOLS[name])
        return getattr(mod, name)
    if name in _BACKPRESSURE_SYMBOLS:
        from zephyr.shared.contracts.backpressure import (
            BackpressurePause,
            BackpressureResume,
            BackpressureThrottle,
        )

        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
    # DM-381: LLM Gateway Protocol
    "LLMGatewayProtocol",
    "LLMResponse",
    "ProviderConfig",
    # DM-382: Skill Protocol
    "SkillLoaderProtocol",
    "SkillRouterProtocol",
    # DM-383: Task Repository Protocol
    "TaskRepositoryProtocol",
    # DM-385: Orchestration Protocol
    "ShadowCanaryProtocol",
    "ChaosEngineProtocol",
    "BatchOrchestratorProtocol",
    # DM-367: module names for audit registration
    "llm_gateway_protocol",
    "orchestration_protocol",
    "skill_protocol",
    "market_data",
    "position",
    "risk_metrics",
    "factor_monitor_report",
    "macro_factor_signal",
'approval_types', 'protocols', 'rollback_types', 'runtime_types']
