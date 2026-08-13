# [TTL] permanent
# backtest/services

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块 隐式命名空间
#   fields: 无显式导入（__all__ 为空列表，scheduler/decay_monitor 等子模块按需直引）
#   code: backtest/services/__init__.py L1-3
# 层: 算法
# - id: A1
#   name_zh: ① 包命名空间声明
#   name_en: zephyr.backtest.services __init__
#   intro: 仅声明 backtest.services 包命名空间，空 __all__ 不re-export子模块，无计算逻辑
#   desc: 包注释 + __all__: list[str] = []（L1-3）
#   inputs: I1
#   outputs: 包级命名空间
# 层: 输出
# - id: O1
#   name_zh: zephyr.backtest.services 包入口
#   name_en: zephyr.backtest.services namespace
#   intro: 回测服务包级入口，子模块经完整路径导入
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
