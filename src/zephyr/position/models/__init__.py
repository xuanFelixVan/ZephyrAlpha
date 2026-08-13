# [TTL] permanent
# position/models

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包初始化导入 空包
#   fields: 无任何子模块导入，仅包标记注释
#   code: models/__init__.py L1
# 层: 算法
# - id: A1
#   name_zh: ① 包命名空间占位
#   name_en: __init__ placeholder
#   intro: 仅声明空的__all__列表，作为models包占位
#   desc: __all__: list[str]=[]，无任何导入与逻辑
#   inputs: I1
#   outputs: 空导出列表
# 层: 输出
# - id: O1
#   name_zh: 空包导出
#   name_en: zephyr.position.models.__all__
#   intro: 空列表，当前不对外导出任何符号
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
