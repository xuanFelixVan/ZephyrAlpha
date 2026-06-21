---
module_id: KE-3484
title: 11. 修改条件
category: governance
---

# 11. 修改条件

11. 修改条件

本策略 `ai_autonomy: human_gated`——铁律本身不可被 AI 修改，但解释和补充说明有分级权限：

| 级别 | 变更范围 | 审批方 | 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调整 | AI 自批 | Session Log 记录 |
| L1 | 增加铁律的"为什么举例" | AI 可建议，Owner 确认 | Session Log 提案 → Owner 24h 内确认 |
| L2 | 新增铁律 / 修改已有铁律内容 | Owner 审批 | 必须创建 KB 决策记录 |
| L3 | 删除铁律 / 严重度重新分级 | Owner 审批 | 必须创建 KB 决策记录 + 所有 Tier 1 消费者同步 |
| — | 受保护路径列表（IRN-010 附录） | Owner 唯一 | 此列表变更影响所有文件写保护，仅 Owner 可操作 |
