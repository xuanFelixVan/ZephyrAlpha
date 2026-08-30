# [A_module] module_id=MOD-INF-maintenance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.maintenance
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
Re-export wrapper: true source is zephyr.shared.maintenance.

Auto-generated stub; submodules migrated to shared/maintenance/.
Uses lazy __getattr__ to avoid import errors for non-existent local submodules.

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
#   intro: 再导出 autonomy_monitor, dogfooding, handbook, zero_config（共 4 符号）
#   desc: __init__ import L0；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: autonomy_monitor, dogfooding, handbook, zero_config
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

_SUBMODULES = {
    "autonomy_monitor": "zephyr.shared.maintenance.autonomy_monitor",
    "dogfooding": "zephyr.shared.maintenance.dogfooding",
    "handbook": "zephyr.shared.maintenance.handbook",
    "zero_config": "zephyr.shared.maintenance.zero_config",
}


def __getattr__(name):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["autonomy_monitor", "dogfooding", "handbook", "zero_config"]
