# NOTE(P1W24 并行协调): scaffold 注册器 eager import bug 第八次复发（斜杠变种
# `zephyr.feedback_loop/detectors/drift.distribution_drift_monitor`），按可逆模式归一
# 为点号合法 import 并将模块名入列 _SUBMODULES/__all__（与 #ARCH-228/235/238/242/246/250 同族）。
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: DistributionDriftMonitor
#   code: __init__.py import L34
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 concept_drift, config_drift, context_window_contamination_detector, diminis…
#   desc: __init__ import L34；__all__ 9 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（9 符号）
#   name_en: __all__
#   intro: concept_drift, config_drift, context_window_contamination_detector, diminishing…
#   downstream: zephyr.feedback_loop.detectors.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.feedback_loop.detectors.drift.distribution_drift_monitor import DistributionDriftMonitor

# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.drift
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
# [CONSUMERS] zephyr.feedback_loop.detectors.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新detectors/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包drift: 概念/配置/分布漂移族（DW-244分类，原_drift.py聚合迁移而来）

_SUBMODULES = [
    "concept_drift",
    "config_drift",
    "distribution_drift_monitor",
    "ensemble_drift",
    "gradual_poisoning_detector",
    "diminishing_returns_detector",
    "context_window_contamination_detector",
    "trend_cycle_separator",
]

__all__ = [
    "concept_drift",
    "config_drift",
    "context_window_contamination_detector",
    "diminishing_returns_detector",
    "distribution_drift_monitor",
    "ensemble_drift",
    "gradual_poisoning_detector",
    "trend_cycle_separator",
    "DistributionDriftMonitor",
]
