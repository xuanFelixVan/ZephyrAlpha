# [BLUEPRINT] MOD-NLP-INFERENCE-001 | P1-E3_NLP管道架构裁定与施工方案.md | §
# [MODULE] zephyr.nlp
# [DOMAIN] D_DATA
# [TTL] permanent
"""zephyr.nlp — NLP 情感分析管道（P1-E3）。

单一推理源原则：推理轨复用 Ollama local_model 层，训练轨产物转 GGUF 回灌。
"""
