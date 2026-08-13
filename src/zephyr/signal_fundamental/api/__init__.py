# [TTL] permanent
# signal/api

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包初始化上下文 空符号表
#   fields: 仅一行包注释（signal/api）与空 __all__ 类型标注列表，无任何导入或逻辑
#   code: __init__.py L1-L3
# 层: 算法
# - id: A1
#   name_zh: ① 空包初始化
#   name_en: __init__
#   intro: signal_fundamental.api 占位包初始化，仅声明空的公共符号表
#   desc: 文件仅含包注释与 __all__: list[str] = []，不导入任何子模块、不定义任何函数；为基本面信号 API 层预留的包占位
#   inputs: I1
#   outputs: 空公共符号表
# 层: 输出
# - id: O1
#   name_zh: 空公共命名空间
#   name_en: zephyr.signal_fundamental.api
#   intro: 基本面信号 API 占位包命名空间，当前不对外暴露任何符号
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
