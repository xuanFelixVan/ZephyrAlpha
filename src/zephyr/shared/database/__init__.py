# [A_code] module_id: MOD-SHARED_DB | layer=L1_foundation | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.shared.database
# [DOMAIN] D_SHARED
# [TTL] permanent
"""


共享数据库工具包：提供 DatabaseService 共用的 CRUD mixin。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.shared.database
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.shared.database.__init__
#   intro: 共享数据库工具包：提供 DatabaseService 共用的 CRUD mixin。
#   desc: SH-DB-001 包入口，模块命名空间声明并声明 __all__（1项）
#   inputs: I1
#   outputs: zephyr.shared.database 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（1项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.shared.database 包公共 API
#   name_en: __all__ 1项
#   intro: 共享数据库工具包：提供 DatabaseService 共用的 CRUD mixin。——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = ["database_crud_mixin"]
