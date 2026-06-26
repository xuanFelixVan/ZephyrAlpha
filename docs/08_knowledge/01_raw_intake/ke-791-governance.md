---
module_id: KE-714
title: 10. 变更同步规则
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 10. 变更同步规则

10. 变更同步规则

本策略 `stability: evolving`——铁律编号和内容会随 Phase 边界演变。以下矩阵定义变更类型与消费者同步要求：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 新增/删除铁律（IRN 编号变更） | GOV-MOD-005（Tier 1） | 更新 INJ-007/INJ-008 的 `derived_from` 字段 | 同 commit |
| 修改铁律内容措辞 | 全部消费者 | 通知 + 评估是否语义变更 | 判断：语义变更→同 commit；文字微调→24h 内 |
| P0/P1/P2 严重度分级调整 | GOV-MOD-ALPHA_SIGNAL_DOMAIN（Tier 1） | 更新 §7 否决条件中的严重度映射 | 同 commit |
| 修改 §7 与 GOV-MOD-005 分工边界 | GOV-MOD-005（Tier 1） | 协商边界 + 双文件同步 update | 同 branch，同 PR |
| frontmatter 仅变更 | 无 | 不需同步 | — |
