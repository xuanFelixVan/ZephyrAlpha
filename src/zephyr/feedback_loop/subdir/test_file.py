# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 字符串字面量（无外部输入）
#   fields: 常量 "hello"，无函数参数、无数据表
#   code: test_file.py L1
# 层: 算法
# - id: A1
#   name_zh: ① print 打印
#   name_en: print
#   intro: 调用内置 print 把 hello 写到标准输出
#   desc: print("hello")，单行脚本无任何其他逻辑
#   inputs: I1
#   outputs: stdout 一行 hello
# 层: 输出
# - id: O1
#   name_zh: 标准输出 hello
#   name_en: stdout
#   intro: 控制台打印一行 hello，无返回值、无写库、无信号
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

print("hello")
