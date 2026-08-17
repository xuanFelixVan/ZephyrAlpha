# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 技术指标输出多列 DataFrame（区别于 FactorBase 单 Series）；纯自实现 pandas/numpy 无第三方依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] autodiscover 导入失败→跳过该指标不抛；注册表空→返回空 dict
# [TESTS] tests/zephyr/factor/technical_indicators/
# [A_module] module_id=MOD-L02-TI | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ZephyrAlpha — 技术指标计算子包（D_FACTOR 域，#ARCH-DATA-TI-001）。

~40 个技术指标（KDJ/MACD/RSI/BOLL/ATR 等），分五类：
  - trend: MA/EMA/WMA/DEMA/MACD/ADX/DMI/CCI/SAR/TRIX
  - momentum: KDJ/RSI/WR/ROC/MTM/CMF/UOS/AO/CMO/StochRSI
  - volatility: ATR/BOLL/Keltner/Donchian/STDDEV/BandWidth/%B/HistVol
  - volume: OBV/MFI/VWAP/VR/AD/PVT/WVAD
  - reversal: K线形态/RSI背离/MACD背离/BOLL突破/量价背离

设计原则：
  - 纯自实现 pandas/numpy（不引入 TA-Lib，避免 C 依赖 + Windows 编译问题）
  - TechnicalIndicatorBase.compute() → DataFrame（多列输出，区别于 FactorBase 单 Series）
  - @TechnicalIndicatorRegistry.register 装饰器自动注册
  - autodiscover_technical_indicators() 自动发现 5 类指标模块

双模式计算：
  - 盘后 preload：internal_compute_provider 批量计算入 ClickHouse c1_market.technical_indicator
  - 盘中实时：sleeve 内 alpha 择时调用 compute() 即时计算（不入表）

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md
"""

from __future__ import annotations

from typing import Final

# 子模块导出供 sleeve alpha 择时 / tests 直接 import（from zephyr.factor.technical_indicators import momentum 等）
from zephyr.factor.technical_indicators import (  # noqa: I001  包内子模块显式导出
    momentum,
    reversal,
    trend,
    volatility,
    volume,
)
from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
    autodiscover_technical_indicators,
)

__all__: Final[list[str]] = [
    "TechnicalIndicatorBase",
    "TechnicalIndicatorMeta",
    "TechnicalIndicatorRegistry",
    "autodiscover_technical_indicators",
    "momentum",
    "reversal",
    "trend",
    "volatility",
    "volume",
]
