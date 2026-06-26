---
module_id: KE-748
title: 15.2 `stability` 字段
category: governance_rule
ttl: permanent
---

# 15.2 `stability` 字段

15.2 `stability` 字段

| 属性 | 值 |
|------|-----|
| 字段名 | `stability` |
| 域 | A（文档 frontmatter） |
| 必填 | 是（新增规则文档时） |
| 类型 | enum |
| 受控词表 | `frozen`, `stable`, `evolving` |
| 默认值 | `stable` |
| 说明 | 规则的变更稳定性，决定变更审批门槛 |
| 归属标准 | PS-STD-004 |
| 一致性约束 | `frozen` ↔ `immutable_core`（单向强制）；其余组合无硬性约束，遵循 PS-STD-001 §2.6 架构公民原则 |

---
