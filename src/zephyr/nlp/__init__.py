# [BLUEPRINT] MOD-NLP-INFERENCE-001 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §
# [MODULE] zephyr.nlp
# [DOMAIN] D_DATA
# [TTL] permanent
"""


zephyr.nlp — NLP 情感分析管道（P1-E3）。

单一推理源原则：推理轨复用 Ollama local_model 层，训练轨产物转 GGUF 回灌。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.nlp
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.nlp.__init__
#   intro: zephyr.nlp — NLP 情感分析管道（P1-E3）。
#   desc: MOD-NLP-INFERENCE-001 包入口，模块命名空间声明并声明 __all__（动态聚合）
#   inputs: I1
#   outputs: zephyr.nlp 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（动态聚合）
# 层: 输出
# - id: O1
#   name_zh: zephyr.nlp 包公共 API
#   name_en: __all__ 动态聚合
#   intro: zephyr.nlp — NLP 情感分析管道（P1-E3）。——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""
