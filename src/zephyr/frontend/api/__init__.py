# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [TTL] permanent
# frontend/api

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 空包标记文件（无数据输入）
#   fields: 无字段——包内仅此一个 __init__.py，无子模块无导入
#   code: src/zephyr/frontend/api/__init__.py L1-3
# 层: 算法
# - id: A1
#   name_zh: ① 空包命名空间占位
#   name_en: __init__（模块级 __all__）
#   intro: 声明 frontend.api 包存在，不导出任何符号
#   desc: 全文仅包名注释 + __all__: list[str] = []（L1-3），无函数无导入，为后续前端 API 子模块预留挂载点
#   inputs: I1
#   outputs: 空导出列表
# 层: 输出
# - id: O1
#   name_zh: 空公共 API 面
#   name_en: __all__=[]
#   intro: 对外不暴露任何符号，占位待扩展
#   downstream: 无下游/内部使用（全库无模块 import zephyr.frontend.api）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
