# [A_module] module_id=MOD-INF-023 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_core
# [DOMAIN] D_GOV_DRIFT
# [INVARIANTS] 7-file core subset migrated from drift_detection/ to resolve directory boundary with MOD-INF-033
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""
MOD-INF-023 drift_detector core module.
Migrated from drift_detection/ to resolve directory boundary with MOD-INF-033.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final
#   code: __init__.py import L41
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Final（共 1 符号）
#   desc: __init__ import L41；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: Final
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

__all__: Final = [
    "benchmark_integrity",
    "ml_engineering",
    "model_drift_monitor",
    "performance_baseline",
    "regime_detector",
]
