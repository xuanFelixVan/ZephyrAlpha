# [BLUEPRINT] MOD-ALT_DATA | (pending)
# [MODULE] zephyr.alt_data
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ALT_DATA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.alt_data
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: __init__
#   intro: 声明 MOD-ALT_DATA 另类数据域包入口并初始化空导出列表
#   desc: 写蓝图注释头（domain=D_ALT_DATA）+ __all__ = []，不 import 子包；子目录 api/core/services/infrastructure/_extensions 均为预留空壳
#   inputs: I1
#   outputs: 空命名空间包对象
#   invariant: __all__ 恒为空列表
# 层: 输出
# - id: O1
#   name_zh: 空导出列表 __all__
#   name_en: __all__
#   intro: 当前导出 0 个符号，另类数据域各子包尚未挂载实现
#   invariant: len(__all__) == 0
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = []
