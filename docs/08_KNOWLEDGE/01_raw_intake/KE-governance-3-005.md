---
module_id: KE-governance-3-005
title: 3. 变更分级
category: governance_rule
---

# 3. 变更分级

3. 变更分级

| 级别 | 定义 | 推导公式 | 审批要求 |
|:---:|------|---------|---------|
| **P0** | 修改 `stability: frozen` 的文件 | `stability=frozen` | Owner 必须手动执行，AI 禁止操作 |
| **P1** | 修改 `stability: stable` + `scope: global` 的文件中的强制条款 | `stability=stable AND scope=global` | Owner 明确批准后 AI 可执行 |
| **P2** | 修改 `stable`（scope≠global）或 `evolving` 的非强制条款 | `stable+非global` 或 `evolving` | AI 可执行，Session Log 记录 |
| **P3** | 新增规则文档（含完整 frontmatter） | 新文件 | AI 可执行，Session Log 记录 |

> **大白话**：P0 = 冻结文件（改它得 Owner 亲自动手）。P1 = 全局稳定文件中强制规则（Owner 点头后 AI 才能改）。P2 = 其他非全局规则（AI 自己改但要留日志）。P3 = 新建文件（AI 自由但要留日志）。

---
