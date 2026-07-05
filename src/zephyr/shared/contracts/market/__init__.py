# [A_module] module_id=MOD-SHR_market | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
"""Backward-compat shim — canonical location is zephyr.trading.trading_contracts.market."""

import importlib

__all__ = [
    "factor_monitor_report",
    "factor_signal",
    "instrument",
    "macro_factor_signal",
    "market_data",
    "synthesized_signal",
]

from . import factor_monitor_report, factor_signal, instrument, macro_factor_signal, market_data, synthesized_signal

_TRADING_SYMBOLS = {
    "FactorSignal": "zephyr.execution_core.trading.trading_contracts.market.factor_signal",
    "SynthesizedSignal": "zephyr.execution_core.trading.trading_contracts.market.synthesized_signal",
    "NormalizedMarketData": "zephyr.execution_core.trading.trading_contracts.market.market_data",
    "AssetClass": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "ETF": "zephyr.execution_core.trading.trading_contracts.market.instrument",
    "FX": "zephyr.execution_core.trading.trading_contracts.market.instrument",
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
    "MacroFactorSignal": "zephyr.execution_core.trading.trading_contracts.market.macro_factor_signal",
    "FactorMonitorReport": "zephyr.execution_core.trading.trading_contracts.market.factor_monitor_report",
}


def __getattr__(name):
    if name in _TRADING_SYMBOLS:
        mod = importlib.import_module(_TRADING_SYMBOLS[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
