# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [TTL] permanent
"""
Drift Detector — MOD-INF-023
=============================
Agent行为漂移检测：签名一致性 + 输出分布监控.

bridges/ 是向后兼容垫片，位于 drift_detector_core/ 下。
当前真源：zephyr.gov_drift（66 文件主包，ARCH-042 裁定 T_soft=120 合规）。
本垫片代理到 drift_detection，请直接从 drift_detection 导入。

正确导入路径:
  from zephyr.gov_drift.drift_engine import scan
  from zephyr.gov_drift.reconciler import AutoFixer
  from zephyr.gov_drift.state_machine import DriftStateMachine

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: warnings, Final
#   code: __init__.py import L45
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 warnings, Final（共 2 符号）
#   desc: __init__ import L45；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: warnings, Final
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import warnings

warnings.warn(
    "zephyr.gov_drift.detector_core.bridges 已废弃，请直接从 zephyr.gov_drift 导入。本兼容层将在 2 个版本后移除。",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from zephyr.gov_drift.ai_construction_detectors import AIConstructionDetectors
    from zephyr.gov_drift.drift_engine import scan
    from zephyr.gov_drift.drift_models import DriftEvent, DriftState
    from zephyr.gov_drift.reconciler import AutoFixer
    from zephyr.gov_drift.state_machine import DriftStateMachine
except ImportError:
    pass

from typing import Final

__all__: Final = ["drift_bridge"]

__version__ = "1.0.0"
__module_id__ = "MOD-INF-023"
