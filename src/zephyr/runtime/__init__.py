# [BLUEPRINT] MOD-RUNTIME_INTRADAY | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""


ZephyrAlpha 交易运行时入口层。

承载盘中/盘后等运行时编排器，把各域组件（D-DATA/D-FACTOR/D-INFRA）组装成
可运行的单进程。区别于 orchestrator/（AI 开发流程编排），本包聚焦交易运行时。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.runtime
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.runtime.__init__
#   intro: ZephyrAlpha 交易运行时入口层。
#   desc: MOD-RUNTIME_INTRADAY 包入口，模块命名空间声明并声明 __all__（动态聚合）
#   inputs: I1
#   outputs: zephyr.runtime 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（动态聚合）
# 层: 输出
# - id: O1
#   name_zh: zephyr.runtime 包公共 API
#   name_en: __all__ 动态聚合
#   intro: ZephyrAlpha 交易运行时入口层。——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = ["intraday_main"]
