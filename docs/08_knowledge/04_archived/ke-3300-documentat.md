---
module_id: KE-3188
title: 12.3 成本优化策略
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 12.3 成本优化策略

12.3 成本优化策略

| 策略 | 预期节省 |
|-----|---------|
| LLM 分级路由（非关键用便宜模型） | 30-50% LLM 成本 |
| Cursor 抵扣最大化（"人在键盘前"=Cursor） | 80% Runtime API |
| 因子计算缓存 | 30% L02 CPU |
| 回测并行延迟到夜间 | 15% 白日 CPU 峰值 |
| LLM Prompt Token 压缩 | 20-40% input token |
