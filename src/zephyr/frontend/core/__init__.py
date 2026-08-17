# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [TTL] permanent
# frontend/core

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: frontend/core 子包命名空间
#   fields: 无运行时数据字段（纯包占位，无函数无类）
#   code: src/zephyr/frontend/core/__init__.py L1
# 层: 算法
# - id: A1
#   name_zh: ① 空导出初始化
#   name_en: __all__
#   intro: 声明空 __all__ 列表作为子包占位，不对外导出任何符号
#   desc: 模块级赋值 __all__: list[str] = []，全文仅 3 行
#   inputs: I1
#   outputs: 空导出列表
# 层: 输出
# - id: O1
#   name_zh: 空导出符号表
#   name_en: __all__
#   intro: frontend/core 当前不导出任何符号，仅占住包路径
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
