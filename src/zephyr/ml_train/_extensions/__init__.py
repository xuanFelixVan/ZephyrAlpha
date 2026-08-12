# [TTL] permanent
# ml_train/_extensions

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无（空包标记，不读数据表/外部API）
#   code: ml_train/_extensions/__init__.py L1
# 层: 算法
# - id: A1
#   name_zh: ① 命名空间包声明
#   name_en: __all__
#   intro: 仅声明 ml_train._extensions 包命名空间，导出列表为空
#   desc: 模块体只有包注释与 __all__: list[str] = []，无函数/类/数据计算
#   inputs: I1
#   outputs: 空导出列表
# 层: 输出
# - id: O1
#   name_zh: 空导出列表 __all__
#   name_en: __all__
#   intro: 对外不导出任何符号，仅作包命名空间占位
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
