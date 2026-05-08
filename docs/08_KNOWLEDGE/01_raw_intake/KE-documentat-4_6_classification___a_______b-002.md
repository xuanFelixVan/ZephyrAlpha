---
module_id: KE-documentat-4_6_classification___a_______b-002
title: 4.6 classification：域 A（文档）与域 B（任务）分层
category: documentation
---

# 4.6 classification：域 A（文档）与域 B（任务）分层

4.6 classification：域 A（文档）与域 B（任务）分层

> **2026-05-05 裁定（闭合 §4 与 §7 冲突）**：不再执行「删除 `INTERNAL` / 强制枚举二分」的迁移。文档与任务对敏感度粒度需求不同——**分层真源**，禁止混读。

| 上下文 | 合法值 | 真源 |
|--------|--------|------|
| **域 A** 文档 frontmatter | **`public` / `confidential`（推荐）**；历史文件可暂留 `internal` | 本表 + frontmatter 校验 |
| **域 B** `Task.classification` | **`public` / `internal` / `confidential`（三值）** | **`src/zephyr/shared/schemas.py`** `Classification` + `_registry/vocabularies/classification-vocabulary.yaml`；字段表见 **§7.1** |

**域 A 推荐二分**：降低 Vibe Coding 下 AI 决策成本。  
**域 B 使用三值**：区分「项目内默认可见」（`internal`）与「明确机密」（`confidential`）；与代码枚举及 SQLite 对齐。  
**与 `ai_autonomy_level` 正交**（不变）：`classification` 管外传边界，`ai_autonomy_level` 管「谁能改」。

**以下为 2026-04-29 讨论的「仅文档域二分」论据摘要**（仍适用于**仅填 frontmatter 的文档**，不推翻域 B 三值）：

- 纯公开/不公开判断在部分商业合规语境中更简单。  
- 军方 `secret` 分级本项目不使用。

**已废止的叙述**：曾计划删除枚举 `INTERNAL`、批量把 `internal` 文件改为 `confidential`——**已撤销**；以本表分层为准。

---
