---
module_id: KE-module_blu-3_3_ke_____10-004
title: 3.3 KE 状态机（10 状态）
category: module_blueprint
---

# 3.3 KE 状态机（10 状态）

3.3 KE 状态机（10 状态）

> **来源**：`03-知识库架构.md` §4 + `kb_repo.py` 代码实现。
> **对标**：ITIL Knowledge Management — 知识从 Draft 到 Verified 的正式流转需要审批门控。

```
DRAFT → SUBMITTED → REVIEWED → ACCEPTED → INDEXED → VERIFIED
  │        │           │          │          │          │
  │        │           │          │          │          ├─→ REJECTED (终态)
  │        │           │          │          │          │
  │        │           │          │          │          ├─→ DEPRECATED
  │        │           │          │          │          │      │
  │        │           │          │          │          │      └─→ ARCHIVED (终态)
  │        │           │          │          │          │
  │        │           │          │          │          └─→ SUPERSEDED
  └────────┴───────────┴──────────┘          │                 │
      (任意非终态可直接取消)                   │            (终态，被新版取代)
                                              │
```

**10 状态定义与流转规则**：

| # | 状态 | 英文 | 含义 | 进入条件 | 可流转至 |
|:--:|------|------|------|---------|---------|
| 0 | 草稿 | DRAFT | KE 刚创建，内容待完善 | 创建时默认 | SUBMITTED, REJECTED |
| 1 | 已提交 | SUBMITTED | KE 已提交，等待审核 | G1 Ingest 通过 | REVIEWED, REJECTED |
| 2 | 已审核 | REVIEWED | KE 经人类/AI 审核，内容准确 | G2 Triage 通过 | ACCEPTED, REJECTED |
| 3 | 已接受 | ACCEPTED | KE 被接受，等待入库 | 人工/AI 确认 | INDEXED, REJECTED |
| 4 | 已索引 | INDEXED | KE 已写入 ChromaDB + SQLite 索引 | G3 Analyze 通过 | VERIFIED, REJECTED |
| 5 | 已验证 | VERIFIED | KE 经四轮审计确认无误 | G4 Activate 通过 | DEPRECATED, SUPERSEDED |
| 6 | 已拒绝 | REJECTED | KE 被拒绝入库 | 任意审核门禁失败 | —（终态） |
| 7 | 已废弃 | DEPRECATED | KE 内容过时/不再适用 | half_life 到期 or 人工标记 | ARCHIVED |
| 8 | 已归档 | ARCHIVED | KE 物理归档 | DEPRECATED 确认后 30d | —（终态） |
| 9 | 已取代 | SUPERSEDED | KE 被新版 KE 取代 | `supersedes_ke` 引用 | —（终态） |

**终态**：REJECTED（拒绝）、ARCHIVED（归档）、SUPERSEDED（被取代）

> **大白话**：一条知识从"有人提了个想法"（DRAFT）→"整理好提交审核"（SUBMITTED）→"检查过没问题"（REVIEWED）→"批准入库"（ACCEPTED）→"写入数据库可检索"（INDEXED）→"经过四轮 AI 交叉审计确认无误"（VERIFIED）。中间任何一步被发现问题就进入 REJECTED（拒绝）。知识过时了就 DEPRECATED→ARCHIVED（归档）。
