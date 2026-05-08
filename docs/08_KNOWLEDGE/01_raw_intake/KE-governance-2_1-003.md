---
module_id: KE-governance-2_1-003
title: 2.1 维度总览
category: governance_rule
---

# 2.1 维度总览

2.1 维度总览

| # | 维度 | 英文 | frontmatter 字段 | 受控词表大小 | 用途 |
|---|------|------|-----------------|:----------:|------|
| 1 | 领域 | Domain | `domain` | 9 | 按业务/技术领域分组规则 |
| 2 | 层级 | Layer | `layer` | 3 | 按规范性语言强度分层 |
| 3 | 作用范围 | Scope | `scope` | 4 | 按影响范围分级 |
| 4 | 稳定性 | Stability | `stability` | 3 | 按变更频率分级 |
| 5 | 执行者 | Executor | `ai_autonomy` | 3 | 按谁有权执行/修改分级 |

> **注意**：维度 2（Layer）和维度 5（Executor）已有对应的 frontmatter 字段（`layer` 和 `ai_autonomy`）。
> 本标准不新增这两个字段，而是明确其受控词表和分类规则。
> 维度 3（Scope）和维度 4（Stability）引入两个新字段：`scope`、`stability`。

---
