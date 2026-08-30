# [A_module] module_id=MOD-INF-session | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.session
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
Re-export wrapper: true source is zephyr.shared.session / zephyr.shared.session_continuity.

Auto-generated stub; submodules migrated to shared/.
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
#   intro: 再导出 session_boundary, session_continuity（共 2 符号）
#   desc: __init__ import L0；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: session_boundary, session_continuity
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

_SUBMODULES = {
    "session_boundary": "zephyr.shared.session.session_boundary",
    "session_continuity": "zephyr.shared.session_continuity",
}


def __getattr__(name):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["session_boundary", "session_continuity"]
