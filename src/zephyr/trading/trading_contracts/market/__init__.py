# [A_module] module_id=MOD-UNK_market | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.market
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

"""trading-contracts.market — market data and signal domain contracts."""

from zephyr.shared.contracts.factor_monitor_report import FactorMonitorReport
from zephyr.shared.contracts.factor_signal import FactorSignal
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
from zephyr.shared.contracts.macro_factor_signal import MacroFactorSignal
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.trading.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal

__all__ = [
    "ETF",
    "FX",
    "AssetClass",
    "Bond",
    "Country",
    "Crypto",
    "CryptoContractType",
    "CurrencyCode",
    "Exchange",
    "FactorMonitorReport",
    "FactorSignal",
    "Future",
    "Instrument",
    "Jurisdiction",
    "MacroFactorSignal",
    "NormalizedMarketData",
    "Option",
    "OptionType",
    "SignalDegradationWarning",
    "Stock",
    "SynthesizedSignal",
    "TradingCalendarName",
    "factor_monitor_report",
    "factor_signal",
    "instrument",
    "macro_factor_signal",
    "market_data",
    "signal_degradation_warning",
    "synthesized_signal",
]
