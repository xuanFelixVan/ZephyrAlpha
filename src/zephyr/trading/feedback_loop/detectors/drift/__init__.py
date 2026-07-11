# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.drift
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.detectors.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新detectors/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK_drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包drift: 概念/配置/分布漂移族（DW-244分类，原_drift.py聚合迁移而来）

_SUBMODULES = [
    "concept_drift",
    "config_drift",
    "ensemble_drift",
    "gradual_poisoning_detector",
    "diminishing_returns_detector",
    "context_window_contamination_detector",
    "trend_cycle_separator",
]

__all__ = ['concept_drift', 'config_drift', 'context_window_contamination_detector', 'diminishing_returns_detector', 'ensemble_drift', 'gradual_poisoning_detector', 'trend_cycle_separator']

