---
module_id: KE-185
title: 2.1 架构与治理类
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 架构与治理类

2.1 架构与治理类

| 大白话 | 行业术语 | 解释（一句话） | 关联文档 |
|-------|---------|--------------|---------|
| 唯一真源 / 正本 | Single Source of Truth (SSOT) / Canonical Source | 一件事只有一份权威记录，其他都是副本或引用 | ADR-0001 |
| 正式文档区 / 正本区 | Canonical Domain / Canonical Area | 已拍板、长期维护、外部可信的正式文档存放区 | `docs/02_enterprise_architecture/` 等 |
| 讨论区 / 沙盒 / 草稿区 | Workspace / Sandbox / Scratch | 未定稿、可随时改、不作对外承诺的区域 | ~~`docs/19_development_workspace/`~~ 已删除（2026-05-02，迁至外部独立目录） |
| 真源迁移 / 搬家 | Migration / Canonicalization | 从旧结构搬到新结构，并统一规范 | ~~`taskbook.md`~~（已归档任务卡系统） 仓库搬迁章节 |
| 文件夹规划 / 目录布局 | Information Architecture (IA) | 系统内容如何分层、分类、命名、存放的整体设计 | `docs/02_enterprise_architecture/target_architecture/information_architecture.md` |
| 规矩 / 规范 | Standard / Policy / Rule | 对"合格产物"的明确要求 | `metadata_registry.yaml` |
| 薄治理 / 轻规矩 | Thin Governance / Lightweight Governance | 只定最小必要规则，不搞庞大流程 | ~~`taskbook.md`~~（已归档任务卡系统） 段 C |
