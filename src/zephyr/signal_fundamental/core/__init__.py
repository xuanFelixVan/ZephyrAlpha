# [TTL] permanent
# signal/core

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求 import 触发
#   fields: 模块全限定名 zephyr.signal_fundamental.core
#   code: src/zephyr/signal_fundamental/core/__init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 空包命名空间初始化
#   name_en: __all__ = []
#   intro: 仅声明空导出列表，占位保留 core 子包结构
#   desc: 模块级赋值 __all__: list[str] = []（L3），无导入无计算
#   inputs: I1
#   outputs: 空包命名空间
# 层: 输出
# - id: O1
#   name_zh: 空包命名空间
#   name_en: empty package namespace
#   intro: 不导出任何符号，仅作为 signal_fundamental.core 子包挂载点
#   downstream: 无下游/内部使用（全库源码无 import 引用）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
