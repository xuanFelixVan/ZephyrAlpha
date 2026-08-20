from zephyr.regime.regime_cycle_analyzer import RegimeCycleAnalyzer

# [BLUEPRINT] MOD-REGIME-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=PKG-regime | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



D_REGIME 域包 — 跨市场状态检测（regime 检测/市场相关性/流动性/大盘分析）。

regime 检测器 CRISIS 态依赖跨市场相关性（股/债/商品/加密），本质跨市场，非 A 股专属，
故独立成域而非归入 D_ASHARE_SIGNAL（裁定 2026-08-06，30_multi_strategy_concurrency §7.2）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.regime
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.regime.__init__
#   intro: D_REGIME 域包 — 跨市场状态检测（regime 检测/市场相关性/流动性/大盘分析）。
#   desc: MOD-REGIME-001 包入口，模块命名空间声明并声明 __all__（动态聚合）
#   inputs: I1
#   outputs: zephyr.regime 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（动态聚合）
# 层: 输出
# - id: O1
#   name_zh: zephyr.regime 包公共 API
#   name_en: __all__ 动态聚合
#   intro: D_REGIME 域包 — 跨市场状态检测（regime 检测/市场相关性/流动性/大盘分析）。——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = [
    "overlay_signals_builder",
    "regime_cycle_analyzer",
    "regime_feature_builder",
    "risk_signal_builder",
]
