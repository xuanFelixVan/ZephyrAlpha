# [BLUEPRINT] MOD-REGIME-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=PKG-regime-core | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_REGIME 域核心包 — regime 检测器核心实现。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: RegimeDetector, RegimeProbabilities, RegimeSnapshot, ShrinkageResult,…
#   code: __init__.py import L35
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 RegimeDetector, RegimeProbabilities, ShrinkageResult, TransitionTriggered,…
#   desc: __init__ import L35；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: RegimeDetector, RegimeProbabilities, ShrinkageResult, TransitionTriggered, Regi…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.regime.core.regime_detector import (
    RegimeDetector,
    RegimeProbabilities,
    RegimeSnapshot,
    ShrinkageResult,
    TransitionTriggered,
)

__all__ = [
    "RegimeDetector",
    "RegimeProbabilities",
    "ShrinkageResult",
    "TransitionTriggered",
    "RegimeSnapshot",
]
