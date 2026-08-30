# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.anomaly
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
# [GOV-DOC-018] 子包anomaly: 异常检测族（DW-244分类，原_anomaly.py聚合迁移而来）

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 anomaly_clustering, anomaly_detector, emergent_behavior_detector, flapping_…
#   desc: __init__ import L0；__all__ 11 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（11 符号）
#   name_en: __all__
#   intro: anomaly_clustering, anomaly_detector, emergent_behavior_detector, flapping_dete…
#   downstream: zephyr.feedback_loop.detectors.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

_SUBMODULES = [
    "anomaly_detector",
    "anomaly_clustering",
    "log_anomaly",
    "emergent_behavior_detector",
    "heisenbug_detector",
    "intermittent_failure_pattern",
    "silent_corruption_detector",
    "synthetic_anomaly_generator",
    "temporal_pattern",
    "infinite_loop_detector",
    "flapping_detector",
]

__all__ = [
    "anomaly_clustering",
    "anomaly_detector",
    "emergent_behavior_detector",
    "flapping_detector",
    "heisenbug_detector",
    "infinite_loop_detector",
    "intermittent_failure_pattern",
    "log_anomaly",
    "silent_corruption_detector",
    "synthetic_anomaly_generator",
    "temporal_pattern",
]
