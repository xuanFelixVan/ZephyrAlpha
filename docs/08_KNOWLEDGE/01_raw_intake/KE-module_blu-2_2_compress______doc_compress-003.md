---
module_id: KE-module_blu-2_2_compress______doc_compress-003
title: 2.2 Compress（压缩）— doc_compressor.py + context_budget_tracker.py
category: module_blueprint
---

# 2.2 Compress（压缩）— doc_compressor.py + context_budget_tracker.py

2.2 Compress（压缩）— doc_compressor.py + context_budget_tracker.py

```
压缩策略（三级回退）：
  Level 1: Qwen2.5-3B 本地摘要模型 → 语义压缩
  Level 2: 规则基摘要 → 关键段落提取
  Level 3: 截断 → 超出预算直接截断
```

Token 预算分配：
| 类型 | Token 预算 | 优先级 |
|------|:---:|:---:|
| KE 条目 | 0-3000 | 最高 |
| 规则/策略 | 0-2000 | 高 |
| 蓝图 | 0-2000 | 中 |
| 运行时日志 | 0-1000 | 低 |
| **总计** | **8000** | — |
