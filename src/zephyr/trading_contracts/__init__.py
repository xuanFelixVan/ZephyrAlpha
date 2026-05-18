# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.trading_contracts
# [INVARIANTS] trading-domain types only; no business logic
# [MODIFY-GUARD] none
# [CONSUMERS] l03_signal_generation; l04_risk_management; l05_portfolio_construction; l06_trade_execution; l07_post_trade_analytics; l10_compliance; l11_ml_platform
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]

"""zephyr.trading_contracts — trading-domain data contracts.

Moved from shared/contracts/ to eliminate cross-package violations.
Infrastructure contracts (core/, backpressure/) remain in shared/contracts/.
"""

from zephyr.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading_contracts.execution.fill import Fill
from zephyr.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading_contracts.execution.model_serving_request import ModelServingRequest
from zephyr.trading_contracts.execution.position import PositionSnapshot
from zephyr.trading_contracts.execution.execution_rejection_error import ExecutionRejectionError
from zephyr.trading_contracts.market.factor_signal import FactorSignal
from zephyr.trading_contracts.market.synthesized_signal import SynthesizedSignal
from zephyr.trading_contracts.market.market_data import NormalizedMarketData
from zephyr.trading_contracts.market.instrument import (
    AssetClass,
    ETF,
    FX,
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
from zephyr.trading_contracts.market.macro_factor_signal import MacroFactorSignal
from zephyr.trading_contracts.market.factor_monitor_report import FactorMonitorReport
from zephyr.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning
from zephyr.trading_contracts.risk.risk_limits import RiskLimits
from zephyr.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.trading_contracts.risk.risk_metrics import RiskMetricsReport
from zephyr.trading_contracts.risk.compliance_rule import ComplianceRule
from zephyr.trading_contracts.risk.risk_validator_protocol import (
    RiskValidatorProtocol,
    ViolationDetail,
)
from zephyr.trading_contracts.risk.risk_limit_violation_error import RiskLimitViolationError

__all__ = [
    "Order",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "Fill",
    "CapitalAllocationResult",
    "ExecutionReport",
    "ModelServingRequest",
    "PositionSnapshot",
    "ExecutionRejectionError",
    "FactorSignal",
    "SynthesizedSignal",
    "NormalizedMarketData",
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
    "AssetClass",
    "Exchange",
    "Country",
    "CurrencyCode",
    "Jurisdiction",
    "TradingCalendarName",
    "MacroFactorSignal",
    "FactorMonitorReport",
    "SignalDegradationWarning",
    "RiskLimits",
    "RiskDashboardSnapshot",
    "RiskMetricsReport",
    "ComplianceRule",
    "RiskValidatorProtocol",
    "ViolationDetail",
    "RiskLimitViolationError",
]
