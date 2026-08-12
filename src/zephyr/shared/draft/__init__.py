# [TTL] permanent
"""


包 shared.draft 的初始化文件。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.shared.draft
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.shared.draft.__init__
#   intro: 包 shared.draft 的初始化文件。
#   desc: __unmanaged__src/zephyr/shared/draft/__init__.py 包入口，模块命名空间声明并声明 __all__（1项）
#   inputs: I1
#   outputs: zephyr.shared.draft 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（1项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.shared.draft 包公共 API
#   name_en: __all__ 1项
#   intro: 包 shared.draft 的初始化文件。——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "draft_assistant",
]
