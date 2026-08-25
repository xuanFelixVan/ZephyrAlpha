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

__all__: list[str] = []
