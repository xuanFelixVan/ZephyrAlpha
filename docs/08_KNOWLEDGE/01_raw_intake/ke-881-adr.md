---
module_id: KE-803------adr-003
status: active
title: 2.2.5 状态字段（ADR 工作流语义）
category: governance
---

# 2.2.5 状态字段（ADR 工作流语义）

2.2.5 状态字段（ADR 工作流语义）

| 状态 | 含义 |
|---|---|
| `proposed` | 讨论稿；Markdown 草稿仅存放于 Owner 批准的草稿区或外部工作区；文件名可加 `-draft`；**禁止**写入已移除的 `docs/02_enterprise_architecture/adr/` |
| `accepted` | 已纳入 **`KB:decisions`** namespace；条目内容为 immutable |
| `superseded` | 被新 ADR 取代；原文快照保留，`superseded_by` 指向继任条目 |
| `deprecated` | 已废弃但暂无继任映射（极少使用） |
| `skipped` | 跳号 |
| `reserved` | 保留号 |

**与全局 DocStatus 的关系**：上表描述 ADR **工作流语义**。若同一 Markdown 另纳入全局文档治理，则 YAML frontmatter 中的 **`status`（draft/active/deprecated）** 必须以 **PS-STD-001 §4.1** 为准；与本节枚举并用时不得自相矛盾，冲突按 **PS-STD-004** 裁定。

KB/decisions 条目的展示用状态标签大小写以 KB schema 为准；全局 DocStatus 仍为小写三值。
