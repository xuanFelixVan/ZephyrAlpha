# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.1
# [MODULE] zephyr.clone_guard.engines
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.engines.echo_guard_adapter
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有引擎适配器实现统一接口 CloneEngineAdapter（detect/index/health_check）；引擎升级/替换不影响编排层（Adapter 模式）
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 适配器方法永不抛异常——detect 失败返回空列表 + degraded 标记
# [TESTS] tests/clone_guard/test_echo_guard_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CloneGuard 引擎适配器子包。

Phase A: 仅 EchoGuardAdapter
Phase B: + AstGrepAdapter + RedupAdapter
Phase C: + McritAdapter + VendetectAdapter + RelateAdapter

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: __init__.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L58；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: zephyr.clone_guard.orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = [
    "ast_grep_adapter",
    "echo_guard_adapter",
    "mcrit_adapter",
    "redup_adapter",
    "relate_adapter",
    "vendetect_adapter",
]
