# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.trading_contracts.market
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable

"""trading_contracts.market — market data and signal domain contracts."""

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

__all__ = [
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
]
