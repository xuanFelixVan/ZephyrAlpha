---
module_id: KE-3491
title: 12. 修改条件
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 12. 修改条件

12. 修改条件

本策略 `ai_autonomy: human_gated`——生命周期阶段定义不可由 AI 自主修改：

| 级别 | 变更范围 | 审批方 | 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调整 | AI 自批 | Session Log 记录 |
| L1 | 转换条件措辞微调（不改变语义） | AI 可建议，Owner 确认 | Session Log 提案 |
| L2 | 新增/删除生命周期阶段 | Owner 审批 | 必须创建 KB 决策记录 |
| L3 | 修改 MLC-001~003 规则本体 | Owner 审批 | 必须创建 KB 决策记录 + 全部 Tier 1 消费者同步 |
| — | `status` 枚举值新增/删除 | Owner 审批 | 必须创建 KB 决策记录——违反可能导致所有依赖模块的 `status` 字段值非法 |
