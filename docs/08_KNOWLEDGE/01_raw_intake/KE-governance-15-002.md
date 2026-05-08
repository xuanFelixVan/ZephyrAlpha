---
module_id: KE-governance-15-002
title: 15. 废弃流程
category: governance
---

# 15. 废弃流程

15. 废弃流程

本策略定义了模块的废弃流程（MLC-003，§7），但本策略自身也可能被取代：

1. **搜索影响**：对全部 Tier 1 消费者搜索 `MLC-001|MLC-002|MLC-003`——确认所有引用都有迁移路径
2. **通知期**：30天提前通知全部消费者（Session Log + ADR）
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡期**：至少 90 天——新生命周期策略与旧策略并轨运行
5. **归档**：过渡期满 → `status: archived`
