---
module_id: KE-1425
title: 12.2 Compress P0
category: module_blueprint
---

# 12.2 Compress P0

12.2 Compress P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-C1 | LLM 压缩正常 | Qwen2.5-3B 加载成功 | compress(bundle, 8000, 'llm_summary') | total_tokens ≤ 8000，source_traces 不丢 |
| P0-C2 | LLM 失败降级规则 | mock llama.cpp 抛异常 | compress | 自动用 rule_based，degrade_reasons 记录 DEGRADE-002 |
| P0-C3 | 规则仍超 budget 降级截断 | 设置极小 budget=500 | compress | 自动 truncate，degrade_reasons 有 DEGRADE-002b |
| P0-C4 | 压缩比报告正确 | 输入 24k | compress(..., 8000) | compression_ratio ≈ 8000/24000 |
