---
module_id: ARCHIVE-INDEX-001
version: "1.0.0"
status: Active
layer: L11
owner: ZephyrAlpha-Owner
created_date: "2026-04-16"
responsibility: "ARCHIVE"
---

# docs/06_ARCHIVE/ — 归档区索引

本目录是蓝图安全流水线（Pipeline B）和文件消除流水线（Pipeline A）的 **P2 级内容归档目标路径**。

## 用途

| 来源流水线 | 归档条件 | 归档命名规范 |
|-----------|---------|------------|
| Pipeline B（蓝图安全） | P2 蓝图：有一定价值但 Phase 2 不直接使用 | `bp-archived-YYYYMMDD-{原文件名}` |
| Pipeline A（文件消除） | 有价值但已被知识条目替代的文档 | `doc-archived-YYYYMMDD-{原文件名}` |

## 归档内容导航

| 文件 | 来源 | 归档日期 | 原始路径 |
|------|------|---------|---------|
| *(尚无归档内容，流水线启动后在此追加)* | | | |

## 重要说明

- 本目录中的文件已提取价值到 `docs/08_KNOWLEDGE/`，**不再是活跃文档**
- 如需恢复某文件，应先查阅对应知识条目，再决定是否从归档取回
- 归档文件保留 git 历史，可通过 `git log -- {文件路径}` 查询变更记录
