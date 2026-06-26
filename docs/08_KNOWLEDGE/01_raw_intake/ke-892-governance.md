---
module_id: KE-814
status: active
title: 2.3 优先级裁决规则
category: governance
ttl: permanent
---

# 2.3 优先级裁决规则

2.3 优先级裁决规则

当多个任务竞争同一资源（同一 AI session、同一文件）时，按以下顺序裁决：

1. **按优先级排序**：P0 > P1 > P2 > P3 > P4
2. **同优先级按 safety_level 排序**：H > M > L
3. **同优先级同 safety_level 按创建时间排序**：先到先得（created_at 更早的优先）
4. **Owner 有最终裁定权**：任何自动裁决结果都可以被 Owner 推翻

---
