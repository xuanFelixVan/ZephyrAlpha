---
module_id: KE-governance-5_4_mrs-002-005
title: 5.4 MRS-002：同步原子性
category: governance
---

# 5.4 MRS-002：同步原子性

5.4 MRS-002：同步原子性

**规则**：所有关联登记表的修改 MUST 在同一批次操作中完成。

- 禁止先改 A 再改 B（分开两个操作）。必须一个 SearchReplace/Write 批次覆盖所有目标文件
- 如果某个关联文件当前不在编辑上下文内，MUST 先 Read 该文件再加入同批次修改
- 原子性对标 AGENTS.md §6.2

**大白话**：创建规则文档时，document-metadata-index.yaml + module-id-registry.yaml 两个登记表必须一起更新（原 master-document-inventory.yaml 已废弃被 document-metadata-index.yaml 取代），不能今天写一个明天补一个。现在知道为什么 4 轮审计抓住了 25 个问题了——每次都是"做完主要事情就想不起来同步了"。
