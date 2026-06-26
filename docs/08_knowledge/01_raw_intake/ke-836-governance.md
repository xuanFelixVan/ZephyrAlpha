---
module_id: KE-759
status: active
title: 18. 废弃流程
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 18. 废弃流程

18. 废弃流程

若本策略被更完善的接口契约治理框架取代：

1. **搜索影响**：对全部 Tier 1 消费者搜索 `IFC-001|IFC-002|...|IFC-007`——确认所有引用都有迁移路径
2. **通知期**：30 天提前通知全部消费者（Session Log + ADR）
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡期**：至少 90 天——新旧契约规范并轨运行，数据文件逐步重写
5. **归档**：过渡期满、全部引用已迁移 → `status: archived`
