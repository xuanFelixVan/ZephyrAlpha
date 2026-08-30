# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.shared._cross_layer
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

AI-15 审计治本（2026-08-17）：
- 移除 AlphaSignalPipeline / alpha_signal_pipeline 悬空导出——真源已迁至
  zephyr.signal_fundamental.pipeline（本包内该文件早已不存在，惰性映射必炸）。
- 修复 _SUBMODULES 惰性导入路径：原指向不存在的
  zephyr.cross_asset.cross_market_data_adapter.{name}，改回本包真实子模块路径。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final
#   code: __init__.py import L49
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 MLExperimentPipeline, ml_experiment_pipeline（共 2 符号）
#   desc: __init__ import L49；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: MLExperimentPipeline, ml_experiment_pipeline
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

__all__ = [
    "MLExperimentPipeline",
    "ml_experiment_pipeline",
]

_LAZY_IMPORTS = {
    "MLExperimentPipeline": ("zephyr.shared._cross_layer.ml_experiment_pipeline", "MLExperimentPipeline"),
}

_SUBMODULES: Final = ["ml_experiment_pipeline"]


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

        mod = importlib.import_module(f"zephyr.shared._cross_layer.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
