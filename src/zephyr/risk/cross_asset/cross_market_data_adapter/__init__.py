# [A_module] module_id=MOD-UNK-cross_market_data_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.risk.cross_asset.cross_market_data_adapter
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
_cross_layer: Cross-layer integration pipelines for domain blueprints.

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
#   intro: 再导出 AlphaSignalPipeline, MLExperimentPipeline, ml_experiment_pipeline（共 3 符号）
#   desc: __init__ import L0；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: AlphaSignalPipeline, MLExperimentPipeline, ml_experiment_pipeline
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "AlphaSignalPipeline",
    "MLExperimentPipeline",
    "ml_experiment_pipeline",
]

_LAZY_IMPORTS = {
    "AlphaSignalPipeline": ("zephyr.shared._cross_layer.alpha_signal_pipeline", "AlphaSignalPipeline"),
    "MLExperimentPipeline": (
        "zephyr.cross_asset.cross_market_data_adapter.ml_experiment_pipeline",
        "MLExperimentPipeline",
    ),
}

_SUBMODULES = ["ml_experiment_pipeline"]


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        import importlib

        mod_path, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr_name)
        globals()[name] = value
        return value
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.cross_asset.cross_market_data_adapter.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
