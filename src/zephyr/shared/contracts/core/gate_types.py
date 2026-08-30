# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.gate_types
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] backward-compat shim — canonical location is zephyr.gov_enforcement.rule_enforcement.gate_types
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# Lazy import to avoid circular dependency deadlock:
# shared.contracts -> governance.rule_enforcement -> governance.__init__ -> ... -> governance (cycle)
# At module load time, governance may not be fully initialized yet.
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: gate_types.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: gate_types.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L54；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: backward-compat shim — canonical location is zephyr.gov_enforcement.rule_enforc…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


def __getattr__(name):
    _mod = __import__("zephyr.gov_enforcement.rule_enforcement.gate_types", fromlist=[name])
    return getattr(_mod, name)
