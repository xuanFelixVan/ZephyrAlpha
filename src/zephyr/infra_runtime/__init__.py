# [BLUEPRINT] MOD-INF_RUNTIME | (pending)
# [MODULE] zephyr.infra_runtime
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 守卫式导入：子模块未落地时对应类置 None 不阻断包导入
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_RUNTIME | layer=module | stability=evolving | safety=L | ai_autonomy=human_gated
# [TTL] permanent
"""
zephyr.infra_runtime — 基础设施运行时域包门面（MOD-INF_RUNTIME）。

D_INFRA_RUNTIME 域（资源调度/零拷贝通道/HA-SLA/数据库抽象层）统一入口。
守卫式导入（参照 zephyr.data_eng 模式）：目标类未落地时置 None，
落地即自愈，无需再改本文件。

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
#   desc: 源码 L1-L80；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: 运行时装配批（统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

# NOTE(P2W01): 并行会话 scaffold 期间子模块可能未落地，守卫式导入防包门面断链。
try:
    from zephyr.infra_runtime.resource_scheduler import ResourceScheduler
except ImportError:
    ResourceScheduler = None  # type: ignore[assignment]

try:
    from zephyr.infra_runtime.shared_memory_zero_copy import ZeroCopyChannelManager
except ImportError:
    ZeroCopyChannelManager = None  # type: ignore[assignment]

try:
    from zephyr.infra_runtime.ha_sla_framework import HaSlaFramework
except ImportError:
    HaSlaFramework = None  # type: ignore[assignment]

try:
    from zephyr.infra_runtime.database_layer import DatabaseLayer
except ImportError:
    DatabaseLayer = None  # type: ignore[assignment]

__all__ = []

__all__.append("ResourceScheduler")

__all__.append("ZeroCopyChannelManager")

__all__.append("HaSlaFramework")

__all__.append("DatabaseLayer")
