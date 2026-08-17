# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [A_module] module_id=MOD-INF-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.integration.budget_enforcer
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.integration.budget_enforcer.__init__
#   intro: MOD-INF-001 包入口
#   desc: MOD-INF-001 包入口，模块命名空间声明并声明 __all__（1项）
#   inputs: I1
#   outputs: zephyr.integration.budget_enforcer 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（1项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.integration.budget_enforcer 包公共 API
#   name_en: __all__ 1项
#   intro: MOD-INF-001 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = ["degradation_spiral_detector"]
