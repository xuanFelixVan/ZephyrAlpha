# [BLUEPRINT] MOD-DATA_GOV | (pending)
# [MODULE] zephyr.data_governance.core
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DATA_GOV_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# data_gov/core

# NOTE(P1W17): scaffold 注册器对本子包写入非法行首 eager import
# （from zephyr.data_governance/core.lineage_parser import LineageParser，斜杠非点号）
# + __all__.append("LineageParser")——已归一移除，恢复本包"空导出、子模块显式导入"
# 约定（与 zephyr.data_governance 包级一致）。

# NOTE(P1W18): scaffold 注册器对本子包再次写入非法行首 eager import
# （static_lineage_analyzer / runtime_lineage_collector / column_lineage_analyzer /
# record_lineage_tracker 四次，斜杠非点号）+ __all__.append——均已归一移除，维持
# "空导出、子模块显式导入"约定（同 P1W17 处置，见 #ARCH-242 族）。

"""


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
#   desc: 源码 L1-L60；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
