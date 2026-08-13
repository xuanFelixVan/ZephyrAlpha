# [TTL] permanent
# pf_core/core

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求（import zephyr.pf_core.core）
#   fields: 无参数，纯包初始化触发
#   code: core/__init__.py L1
# 层: 算法
# - id: A1
#   name_zh: ① 空包标记初始化
#   name_en: __init__ (empty package marker)
#   intro: 仅声明空 __all__，不做任何再导出、零副作用
#   desc: L1-3：仅一行包注释 + __all__ = []；子模块 constraint_solver（MOD-PF-006）须经显式路径导入
#   inputs: I1
#   outputs: 空包命名空间
# 层: 输出
# - id: O1
#   name_zh: 空包命名空间
#   name_en: zephyr.pf_core.core namespace
#   intro: 只提供包路径占位，不暴露任何符号
#   downstream: 无下游/内部使用（unmanaged 文件，无 [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
