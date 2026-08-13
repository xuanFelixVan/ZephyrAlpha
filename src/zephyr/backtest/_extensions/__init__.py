# [TTL] permanent
# backtest/_extensions

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块 隐式命名空间
#   fields: 无显式导入（__all__ 为空列表，不re-export任何符号）
#   code: backtest/_extensions/__init__.py L1-3
# 层: 算法
# - id: A1
#   name_zh: ① 包命名空间声明
#   name_en: zephyr.backtest._extensions __init__
#   intro: 仅声明 backtest._extensions 私有扩展包命名空间，空 __all__ 不导出符号，无计算逻辑
#   desc: 包注释 + __all__: list[str] = []（L1-3）
#   inputs: I1
#   outputs: 包级命名空间
# 层: 输出
# - id: O1
#   name_zh: zephyr.backtest._extensions 包入口
#   name_en: zephyr.backtest._extensions namespace
#   intro: 回测私有扩展包级入口，当前不对外暴露任何符号
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
