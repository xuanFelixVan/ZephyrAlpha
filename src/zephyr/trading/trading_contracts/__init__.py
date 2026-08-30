# [A_module] module_id=MOD-UNK-trading_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

"""
zephyr.trading.trading_contracts — trading-domain data contracts.

Moved from shared/contracts/ to eliminate cross-package violations.
Infrastructure contracts (core/, backpressure/) remain in shared/contracts/.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: FactorMonitorReport, FactorSignal, MacroFactorSignal, NormalizedMarke…
#   code: __init__.py import L47
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 ETF, FX, AssetClass, Bond, CapitalAllocationResult, Country, Crypto, Crypto…
#   desc: __init__ import L47；__all__ 43 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（43 符号）
#   name_en: __all__
#   intro: ETF, FX, AssetClass, Bond, CapitalAllocationResult, Country, Crypto, CryptoCont…
#   downstream: signal; risk; pf_core; ex_core; reporting; compliance; ml_train
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.contracts.factor_monitor_report import FactorMonitorReport
from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.shared.contracts.macro_factor_signal import MacroFactorSignal
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.contracts.performance_attribution_report import PerformanceAttributionReport
from zephyr.shared.contracts.portfolio.money import Money, get_currency_precision
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal
from zephyr.trading.trading_contracts import factories
from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.trading.trading_contracts.execution.execution_rejection_error import ExecutionRejectionError
from zephyr.trading.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.model_serving_request import ModelServingRequest
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading.trading_contracts.execution.position import PositionSnapshot
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
from zephyr.trading.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning
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
