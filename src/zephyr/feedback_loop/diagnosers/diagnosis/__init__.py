# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.diagnosis
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS] zephyr.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新diagnosers/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包diagnosis: 诊断引擎族（DW-242分类，原_diagnosis.py聚合迁移而来）

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
#   intro: 再导出 auto_diagnosis, causal_inference_engine, counterfactual, diagnosis_engine,…
#   desc: __init__ import L0；__all__ 14 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（14 符号）
#   name_en: __all__
#   intro: auto_diagnosis, causal_inference_engine, counterfactual, diagnosis_engine, diag…
#   downstream: zephyr.feedback_loop.diagnosers.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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

__all__ = [
    "auto_diagnosis",
    "causal_inference_engine",
    "counterfactual",
    "diagnosis_engine",
    "diagnosis_kpi",
    "impact_predictor",
    "incident_knowledge_injector",
    "interactive_diagnosis",
    "knowledge_bus_factor_monitor",
    "knowledge_market",
    "mtti_tracker",
    "nonstationary_effectiveness",
    "statistical_hygiene_auditor",
    "vertical_self_assessment",
]
