# [TTL] permanent
# ex_core/_extensions

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求 import zephyr.ex_core._extensions
#   fields: 无参数（Python 解释器包初始化）
#   code: src/zephyr/ex_core/_extensions/__init__.py L1
# 层: 算法
# - id: A1
#   name_zh: ① 空包初始化
#   name_en: __init__ (empty package)
#   intro: 仅声明空 __all__，不导入任何子模块、不注册任何扩展
#   desc: __all__: list[str] = []；无函数无类无逻辑，纯命名空间占位（私有扩展包预留）
#   inputs: I1
#   outputs: 空导出列表
# 层: 输出
# - id: O1
#   name_zh: 空包命名空间（__all__=[]）
#   name_en: empty package namespace
#   intro: 对外不导出任何符号，_extensions 子包当前无实现
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
