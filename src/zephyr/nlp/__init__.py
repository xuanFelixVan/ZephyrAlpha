# [BLUEPRINT] MOD-NLP-INFERENCE-001 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §
# [MODULE] zephyr.nlp
# [DOMAIN] D_DATA
# [TTL] permanent
"""zephyr.nlp — NLP 情感分析管道（P1-E3）。

单一推理源原则：推理轨复用 Ollama local_model 层，训练轨产物转 GGUF 回灌。
"""
