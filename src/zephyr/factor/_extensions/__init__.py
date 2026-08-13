# [TTL] permanent
# factor/_extensions

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 空扩展包占位（无外部输入）
#   fields: 仅模块文档串 "# factor/_extensions" 一行注释
#   code: src/zephyr/factor/_extensions/__init__.py L1
# 层: 算法
# - id: A1
#   name_zh: ① 空导出列表声明
#   name_en: __all__
#   intro: 声明 __all__ 为空列表，把包标记为将来因子扩展的挂接点
#   desc: __all__: list[str] = []（L3），无 import、无函数、无注册逻辑
#   inputs: I1
#   outputs: 空 __all__ 列表
# 层: 输出
# - id: O1
#   name_zh: zephyr.factor._extensions 空命名空间
#   name_en: empty package namespace
#   intro: 对外不导出任何符号，仅占住扩展点包路径
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
