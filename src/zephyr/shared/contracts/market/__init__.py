# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
"""Backward-compat shim — canonical location is zephyr.trading_contracts.market."""

from zephyr.trading_contracts.market.factor_signal import FactorSignal  # noqa: F401
from zephyr.trading_contracts.market.synthesized_signal import SynthesizedSignal  # noqa: F401
from zephyr.trading_contracts.market.market_data import NormalizedMarketData  # noqa: F401
from zephyr.trading_contracts.market.instrument import (  # noqa: F401
    AssetClass, ETF, FX, Bond, Country, Crypto, CryptoContractType,
    CurrencyCode, Exchange, Future, Instrument, Jurisdiction, Option,
    OptionType, Stock, TradingCalendarName,
)
from . import factor_monitor_report
from . import factor_signal
from . import instrument
from . import macro_factor_signal
from . import market_data
from . import synthesized_signal
from zephyr.trading_contracts.market.macro_factor_signal import MacroFactorSignal  # noqa: F401
from zephyr.trading_contracts.market.factor_monitor_report import FactorMonitorReport  # noqa: F401
