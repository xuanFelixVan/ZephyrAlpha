# [TTL] permanent
# D_INFRA_RUNTIME/models sub-package

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.infrastructure.models
# 层: 算法
# - id: A1
#   name_zh: ① 子包命名空间声明
#   name_en: __init__
#   intro: 声明 D_INFRA_RUNTIME/models 子包并初始化空导出列表
#   desc: 仅写注释头 + __all__: list[str] = []，不 import 任何子模块，目录下也无其他文件
#   inputs: I1
#   outputs: 空命名空间包对象
#   invariant: __all__ 恒为空列表
# 层: 输出
# - id: O1
#   name_zh: 空导出列表 __all__
#   name_en: __all__
#   intro: 当前导出 0 个符号，为基础设施模型层预留的占位包
#   invariant: len(__all__) == 0
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
