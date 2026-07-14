# [A_module] module_id=MOD-UNK_trading_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts
# [INVARIANTS] trading-domain types only; no business logic
# [MODIFY-GUARD] none
# [CONSUMERS] signal; risk; pf_core; ex_core; reporting; compliance; ml_train
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

"""zephyr.trading.trading_contracts — trading-domain data contracts.

Moved from shared/contracts/ to eliminate cross-package violations.
Infrastructure contracts (core/, backpressure/) remain in shared/contracts/.
"""

from zephyr.gov_enforcement.rule_enforcement.compliance_rule import ComplianceRule
from zephyr.shared.contracts.performance_attribution_report import PerformanceAttributionReport
from zephyr.trading.trading_contracts import factories
from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.trading.trading_contracts.execution.execution_rejection_error import ExecutionRejectionError
from zephyr.trading.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.model_serving_request import ModelServingRequest
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading.trading_contracts.execution.position import PositionSnapshot
from zephyr.trading.trading_contracts.market.factor_monitor_report import FactorMonitorReport
from zephyr.trading.trading_contracts.market.factor_signal import FactorSignal
from zephyr.trading.trading_contracts.market.instrument import (
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
from zephyr.trading.trading_contracts.market.macro_factor_signal import MacroFactorSignal
from zephyr.trading.trading_contracts.market.market_data import NormalizedMarketData
from zephyr.trading.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning
from zephyr.trading.trading_contracts.market.synthesized_signal import SynthesizedSignal
from zephyr.trading.trading_contracts.portfolio.contracts.money import Money, get_currency_precision
from zephyr.trading.trading_contracts.portfolio.contracts.strategy_lifecycle_event import StrategyLifecycleEvent
from zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.trading.trading_contracts.risk.risk_limit_violation_error import RiskLimitViolationError
from zephyr.trading.trading_contracts.risk.risk_limits import RiskLimits
from zephyr.trading.trading_contracts.risk.risk_metrics import RiskMetricsReport
from zephyr.trading.trading_contracts.risk.risk_validator_protocol import (
    RiskValidatorProtocol,
    ViolationDetail,
)

__all__ = [
    "ETF",
    "FX",
    "AssetClass",
    "Bond",
    "CapitalAllocationResult",
    "ComplianceRule",
    "Country",
    "Crypto",
    "CryptoContractType",
    "CurrencyCode",
    "Exchange",
    "ExecutionRejectionError",
    "ExecutionReport",
    "FactorMonitorReport",
    "FactorSignal",
    "Fill",
    "Future",
    "Instrument",
    "Jurisdiction",
    "MacroFactorSignal",
    "ModelServingRequest",
    "Money",
    "NormalizedMarketData",
    "Option",
    "OptionType",
    "Order",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "PerformanceAttributionReport",
    "PositionSnapshot",
    "RiskDashboardSnapshot",
    "RiskLimitViolationError",
    "RiskLimits",
    "RiskMetricsReport",
    "RiskValidatorProtocol",
    "SignalDegradationWarning",
    "Stock",
    "StrategyLifecycleEvent",
    "SynthesizedSignal",
    "TradingCalendarName",
    "ViolationDetail",
    "factories",
    "get_currency_precision",
]
