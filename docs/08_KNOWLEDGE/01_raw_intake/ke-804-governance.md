---
module_id: KE-727
status: active
title: 12. 废弃流程
category: governance
---

# 12. 废弃流程

12. 废弃流程

若本策略被更全面的 AI 行为治理框架取代：

1. **搜索影响**：对全部 Tier 1/2 消费者执行搜索 `IRN-001|IRN-002|...|IRN-010`——确认所有引用都有迁移路径
2. **通知期**：30 天提前通知全部消费者（Session Log + ADR）
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡期**：至少 90 天——期间新旧铁律并轨运行，消费者逐步切换映射
5. **归档**：过渡期满、全部引用已迁移 → `status: archived`
