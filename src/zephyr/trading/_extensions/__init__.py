# [TTL] permanent
# trading/_extensions

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求 import 触发
#   fields: 模块全限定名 zephyr.trading._extensions
#   code: src/zephyr/trading/_extensions/__init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 空包命名空间初始化
#   name_en: __all__ = []
#   intro: 仅声明空导出列表，占位保留 _extensions 私有子包结构
#   desc: 模块级赋值 __all__: list[str] = []，无导入无计算
#   inputs: I1
#   outputs: 空包命名空间
# 层: 输出
# - id: O1
#   name_zh: 空包命名空间
#   name_en: empty package namespace
#   intro: 不导出任何符号，仅作为 trading._extensions 私有子包挂载点
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
