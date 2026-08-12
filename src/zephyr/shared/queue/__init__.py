# [TTL] permanent
# shared.queue package
# proxy shell removed (ARCH-DEBT 5.174 #7): import from zephyr.infrastructure.queue.task_scheduler directly
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 导入方 import 请求 Python导入机制
#   fields: 无数据字段 仅包导入语句
#   code: zephyr.shared.queue
# 层: 算法
# - id: A1
#   name_zh: ① 空包导出契约
#   name_en: __all__ empty list
#   intro: 代理壳已按 ARCH-DEBT 5.174 #7 拆除 本包不再导出任何符号
#   desc: __all__ = [] 空列表 注释引导使用方直接 import zephyr.infrastructure.queue.task_scheduler
#   inputs: I1
#   outputs: 空导出列表
#   invariant: 不导出任何符号
# 层: 输出
# - id: O1
#   name_zh: 空导出命名空间
#   name_en: empty namespace
#   intro: 导入本包拿不到任何符号 队列功能需直连 infrastructure 层实现
#   downstream: 无下游/内部使用（功能迁移至 zephyr.infrastructure.queue.task_scheduler）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
