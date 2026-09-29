# [BLUEPRINT] MOD-ML_SERVE | (pending)
# [MODULE] zephyr.ml_serve
# [DOMAIN] D_ML_SERVE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ML_SERVE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2
[DEPRECATED] 2026-09-29 夜战 SW5（st-nightsweep-sw5-20260929）依 F130 案卷
    （docs/_working/fullconnect_campaign/j_ai_design_gates/13_f130_ml_serve_adapters.md）
    定罪：四件实体生产面零 import（AST PROD=0 / TC=0）、无工厂/注册表反射装配、
    唯一跨包文本命中在 scripts/_archive/（归档件不计在产）→ 纯装饰，退役标记。
    successor：serve 层现役 = F129 ml_train（core/model_version_registry +
    implementations/default_inference_engine，后者被
    src/zephyr/intelligence/model_evaluation/implementations/default_inference_engine.py:36
    真实消费）；本包为并行未启用第二实现族，"改错包"风险经此标记对冲。
    附登记不裁：model_drift_monitor 双同名件（src/zephyr/gov_drift/detector_core/
    model_drift_monitor.py 68 行 vs src/zephyr/ml_serve/core/model_drift_monitor.py
    269 行）留 clone_guard 尺判定，clone 定性与净删均 = OWNER-GATE 登记，
    物理净删未执行。
    恢复条件：Owner 判"J 段 serve 独立成层"则撤销本标记，按 F130 缺1 补接入点+红样。

# [ALGO_FLOW] external: docs/03_modules/_domain_ml_serve/algo_flow/ml_serve__init__.yaml
"""

__all__ = []
