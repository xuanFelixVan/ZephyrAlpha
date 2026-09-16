# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
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
# [TESTS] none  # 2026-09-05 AI-00：全仓无测试 import 本模块（原声明路径不存在）
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包anomaly: 异常检测族（DW-244分类，原_anomaly.py聚合迁移而来）

"""
# [ALGO_FLOW] external: docs/03_modules/_domain_feedback_loop/algo_flow/detectors/anomaly/anomaly__init__.yaml
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
