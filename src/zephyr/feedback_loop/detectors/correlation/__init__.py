# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation
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
# [GOV-DOC-018] 子包correlation: 跨信号/系统关联与因果族（DW-244分类，原_correlation.py聚合迁移而来）

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
#   intro: 再导出 action_efficacy_decay_detector, action_interaction_detector, action_side_ef…
#   desc: __init__ import L0；__all__ 16 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（16 符号）
#   name_en: __all__
#   intro: action_efficacy_decay_detector, action_interaction_detector, action_side_effect…
#   downstream: zephyr.feedback_loop.detectors.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

_SUBMODULES = [
    "cross_signal_validator",
    "cross_system_correlator",
    "multi_signal_correlator",
    "trace_causal_bridge",
    "decision_provenance",
    "dependency_freshness_monitor",
    "action_efficacy_decay_detector",
    "action_interaction_detector",
    "action_side_effect_cumulative_detector",
    "agent_trajectory_anomaly_detector",
    "ensemble_detector",
    "fle_performance_regression_detector",
    "external_health",
    "external_validation_checkpoint",
    "rumor_noise_filter",
    "traffic_replay_validator",
]

__all__ = [
    "action_efficacy_decay_detector",
    "action_interaction_detector",
    "action_side_effect_cumulative_detector",
    "agent_trajectory_anomaly_detector",
    "cross_signal_validator",
    "cross_system_correlator",
    "decision_provenance",
    "dependency_freshness_monitor",
    "ensemble_detector",
    "external_health",
    "external_validation_checkpoint",
    "fle_performance_regression_detector",
    "multi_signal_correlator",
    "rumor_noise_filter",
    "trace_causal_bridge",
    "traffic_replay_validator",
]
