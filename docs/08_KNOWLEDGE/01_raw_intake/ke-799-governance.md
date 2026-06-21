---
module_id: KE-722
status: active
title: 11. 变更同步规则
category: governance
---

# 11. 变更同步规则

11. 变更同步规则

本策略 `stability: evolving`——生命周期阶段和转换条件会随 Phase 边界变化。以下矩阵定义变更类型与消费者同步要求：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 新增/删除生命周期阶段 | 全部 Tier 1 消费者 | 更新所有文件中的 `status` 枚举列表 + MLC-001 转换表 | 同 commit |
| 修改 MLC-001 转换条件 | GOV-MOD-001（Tier 1） | 确保准入规则与前置条件一致 | 同 commit |
| 修改 §3 受控枚举表 | GOV-MOD-005（Tier 1） | 更新 INJ-004 `valid_values` 列表 | 同 commit |
| 修改 MLC-003 退役步骤 | GOV-MOD-004（Tier 1） | 更新 IFC-007 消费者迁移步骤引用 | 同 commit 或 24h 内 |
| 修改 P0 特殊约束 | 全部 Tier 1 | 评估 P0 模块是否需重新审批 | 同 commit |
| frontmatter 仅变更 | 无 | 不需同步 | — |

**消费者通知机制**：上述表中"通知"动作的执行方式见 GOV-MOD-002 §10 消费者通知机制——Session Log 条目 + ADR + module-id-registry.json 三层通知体系。
