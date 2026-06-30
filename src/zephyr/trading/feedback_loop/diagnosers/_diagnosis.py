# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers._diagnosis
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK__diagnosis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

_SUBMODULES = [
    "auto_diagnosis",
    "diagnosis_engine",
    "diagnosis_kpi",
    "causal_inference_engine",
    "counterfactual",
    "statistical_hygiene_auditor",
    "interactive_diagnosis",
    "mtti_tracker",
    "impact_predictor",
    "incident_knowledge_injector",
    "knowledge_bus_factor_monitor",
    "knowledge_market",
    "nonstationary_effectiveness",
    "vertical_self_assessment",
]
