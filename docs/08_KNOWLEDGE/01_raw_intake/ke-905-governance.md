---
module_id: KE-827
status: active
title: 2.6 超时豁免治理
category: governance
ttl: permanent
---

# 2.6 超时豁免治理

2.6 超时豁免治理

以下情况可以豁免超时规则（不触发自动降级或升级）：

- Owner 明确标注"长期阻塞"的任务（在 tags 中添加 `exempt:timeout`）
- 依赖外部第三方（如监管审批）的任务——在 `blocked_reason` 中注明"外部依赖"

---
