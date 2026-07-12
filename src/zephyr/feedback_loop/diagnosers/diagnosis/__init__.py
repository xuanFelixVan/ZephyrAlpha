# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.diagnosis
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS] zephyr.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新diagnosers/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK_diagnosis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包diagnosis: 诊断引擎族（DW-242分类，原_diagnosis.py聚合迁移而来）

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

__all__ = ['auto_diagnosis', 'causal_inference_engine', 'counterfactual', 'diagnosis_engine', 'diagnosis_kpi', 'impact_predictor', 'incident_knowledge_injector', 'interactive_diagnosis', 'knowledge_bus_factor_monitor', 'knowledge_market', 'mtti_tracker', 'nonstationary_effectiveness', 'statistical_hygiene_auditor', 'vertical_self_assessment']

