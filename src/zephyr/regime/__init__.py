"""


# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/regime__init__.yaml
"""

from zephyr.regime.regime_cycle_analyzer import RegimeCycleAnalyzer
from zephyr.regime.volatility_regime_alerter import VolatilityRegimeAlerter
from zephyr.regime.volatility_squeeze_breakout import VolatilitySqueezeBreakout

# [BLUEPRINT] MOD-REGIME-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=PKG-regime | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



D_REGIME 域包 — 跨市场状态检测（regime 检测/市场相关性/流动性/大盘分析）。

regime 检测器 CRISIS 态依赖跨市场相关性（股/债/商品/加密），本质跨市场，非 A 股专属，
故独立成域而非归入 D_ASHARE_SIGNAL（裁定 2026-08-06，30_multi_strategy_concurrency §7.2）。

# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = [
    "index_regime_panel",
    "market_forecast_fusion",
    "overlay_signals_builder",
    "regime_cycle_analyzer",
    "regime_feature_builder",
    "risk_signal_builder",
    "volatility_squeeze_breakout",
]

__all__.append("VolatilityRegimeAlerter")
# NOTE(P1W17): scaffold 注册器行首 eager import + 类名 append 已归一为模块名条目
# （market_forecast_fusion/volatility_squeeze_breakout 按字母序入列），恢复本包
# "纯模块名导出"约定；RegimeCycleAnalyzer/VolatilityRegimeAlerter 行首 eager import
# 为前波残留，本波未动。

# ORPHAN-MODULE: 引用登记（让 depgraph 发现 import 边）
from zephyr.regime.institutional_regime_scorer import InstitutionalRegimeScorer  # noqa: F401
