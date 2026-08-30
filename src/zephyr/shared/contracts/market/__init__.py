# [A_module] module_id=MOD-SHR-market | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md |
# [TTL] permanent
# ARCH-DATA-SSOT-001: 5 个数据契约真源归一到 shared/contracts/ 根目录
# （cross_layer_contracts.yaml CTR-001/002/003/004/005 声明）。
# 本目录仅保留 instrument shim——instrument 真源仍在 trading 域。
"""
Backward-compat shim — only instrument remains.

Data contracts (market_data/factor_signal/factor_monitor_report/macro_factor_signal/synthesized_signal)
canonical location is now zephyr.shared.contracts.* (codegen SSoT, cross_layer_contracts.yaml declared).

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: importlib
#   code: __init__.py import L40
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 instrument（共 1 符号）
#   desc: __init__ import L40；__all__ 1 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: instrument
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import importlib

__all__ = [
    "instrument",
]

from . import instrument

_INSTRUMENT_SYMBOLS = {
    "AssetClass": "zephyr.trading.trading_contracts.market.instrument",
    "ETF": "zephyr.trading.trading_contracts.market.instrument",
    "FX": "zephyr.trading.trading_contracts.market.instrument",
    "Bond": "zephyr.trading.trading_contracts.market.instrument",
    "Country": "zephyr.trading.trading_contracts.market.instrument",
    "Crypto": "zephyr.trading.trading_contracts.market.instrument",
    "CryptoContractType": "zephyr.trading.trading_contracts.market.instrument",
    "CurrencyCode": "zephyr.trading.trading_contracts.market.instrument",
    "Exchange": "zephyr.trading.trading_contracts.market.instrument",
    "Future": "zephyr.trading.trading_contracts.market.instrument",
    "Instrument": "zephyr.trading.trading_contracts.market.instrument",
    "Jurisdiction": "zephyr.trading.trading_contracts.market.instrument",
    "Option": "zephyr.trading.trading_contracts.market.instrument",
    "OptionType": "zephyr.trading.trading_contracts.market.instrument",
    "Stock": "zephyr.trading.trading_contracts.market.instrument",
    "TradingCalendarName": "zephyr.trading.trading_contracts.market.instrument",
}


def __getattr__(name):
    if name in _INSTRUMENT_SYMBOLS:
        mod = importlib.import_module(_INSTRUMENT_SYMBOLS[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
