# [BLUEPRINT] MOD-INF-022 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
# governance/services

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.governance.services
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.governance.services.__init__
#   intro: governance/services
#   desc: __unmanaged__src/zephyr/governance/services/__init__.py 包入口，模块命名空间声明并声明 __all__（3项）
#   inputs: I1
#   outputs: zephyr.governance.services 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（3项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.governance.services 包公共 API
#   name_en: __all__ 3项
#   intro: governance/services——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []

from typing import Final

__all__: Final = ["adapter", "cross_session_correlator", "memory_provenance"]
