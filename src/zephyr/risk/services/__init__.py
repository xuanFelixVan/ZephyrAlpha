# [TTL] permanent
# risk/services

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 空包标记文件（无数据输入）
#   fields: 无字段——仅一行包注释 `# risk/services`，无子模块无导入
#   code: src/zephyr/risk/services/__init__.py L1-3
# 层: 算法
# - id: A1
#   name_zh: ① 风控服务层命名空间占位
#   name_en: __init__（模块级 __all__）
#   intro: 预留 risk 服务层子包命名空间，当前尚无任何实现
#   desc: 仅注释（L1）+ __all__: list[str] = []（L3），无函数无导出，占位待风控服务层落地
#   inputs: I1
#   outputs: 空导出列表
# 层: 输出
# - id: O1
#   name_zh: 空公共API面
#   name_en: __all__=[]
#   intro: 对外不暴露任何符号，占位待扩展
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
