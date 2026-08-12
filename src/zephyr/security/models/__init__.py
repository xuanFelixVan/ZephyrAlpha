# [TTL] permanent
# security/models

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求 import语句
#   fields: 对 zephyr.security.models 包的 import 请求
#   code: zephyr/security/models/__init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 空包占位声明
#   name_en: zephyr.security.models.__init__
#   intro: 安全数据模型包的占位根模块只声明空导出清单不含任何逻辑
#   desc: 仅一行 __all__: list[str] = []; 无re-export无函数无类, 作为未来安全模型的命名空间占位
#   inputs: I1
#   outputs: 空包命名空间
# 层: 输出
# - id: O1
#   name_zh: models空命名空间
#   name_en: zephyr.security.models
#   intro: 不导出任何符号的空包入口, 待后续安全模型模块入驻
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
