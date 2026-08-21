# [BLUEPRINT] MOD-CROSS_ASSET | (pending)
# [MODULE] zephyr.cross_asset.api
# [DOMAIN] D_CROSS_ASSET
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
# [A_module] module_id=MOD-CROSS_ASSET | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# cross_asset/api

"""
[DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包标记文件（无数据输入）
#   fields: 无字段——包内仅此 __init__.py 占位/聚合，无独立业务逻辑
#   code: src/zephyr/cross_asset/api/__init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包命名空间占位/聚合导出
#   name_en: __init__（模块级 __all__）
#   intro: 声明 zephyr.cross_asset.api 包命名空间，按 __all__ 声明导出
#   desc: 包级占位/聚合再导出，无函数无副作用，子模块挂载点
#   inputs: I1
#   outputs: 包级公共命名空间
# 层: 输出
# - id: O1
#   name_zh: 包公共 API 面
#   name_en: __all__
#   intro: 包级导出以 __all__ 声明为准
#   downstream: 见头部 [CONSUMERS] 声明
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
