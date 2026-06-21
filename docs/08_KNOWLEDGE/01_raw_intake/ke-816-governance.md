---
module_id: KE-739
title: 14. 修改条件
category: governance
---

# 14. 修改条件

14. 修改条件

本策略 `ai_autonomy: human_gated`——AI 不可自主修改。以下为分级修改规则：

| 级别 | 变更范围 | 审批方 | 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调整 | AI 自批 | Session Log 记录即可 |
| L1 | MAD 规则条件微调（如新增通过条件） | Owner 审批 | Session Log 提案 → Owner 确认 |
| L2 | MAD 规则新增/删除、否决条件变更 | Owner 审批 | 须创建 KB 决策记录 |
| L3 | 章节结构变更（新增/合并/删除） | Owner 审批 | 须创建 KB 决策记录 + 对照 PS-STD-002 §3.2.4 确认合规 |
| — | `status` 从 draft 提升为 active | Owner 唯一 | 按 PS-STD-009 变更门控 P1 流程 |
