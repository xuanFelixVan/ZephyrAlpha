---
module_id: KE-207---doc-type-005
status: active
title: 2.5 按 doc_type 分类的必填字段清单
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.5 按 doc_type 分类的必填字段清单

2.5 按 doc_type 分类的必填字段清单

> 以下清单仅适用于 `01_policies_and_standards/` 目录下的文件。
> 其他目录的文件仍按 §2.2 分阶段闸门执行。

| 字段 | policy | standard | operational_rule | register | protocol | template | adr | blueprint | construction_plan | roadmap |
|------|:------:|:-------:|:---------------:|:-------:|:-------:|:-------:|:---:|:-------:|:-----------------:|:------:|
| `module_id` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `title` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `doc_type` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `status` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `version` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `date` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `owner` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `layer` | 🔴 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🔴 |
| `classification` | 🔴 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🔴 |
| `language` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `created_by` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `ttl` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `summary` | 🔴 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `tags` | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | ⬜ | 🟡 | 🟡 | 🟡 | 🟡 |
| `rule_form` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `scope` | 🔴 | 🔴 | 🟡 | ⬜ | 🔴 | ⬜ | 🟡 | 🔴 | 🟡 | 🟡 |
| `stability` | 🔴 | 🔴 | 🟡 | ⬜ | 🔴 | ⬜ | 🟡 | 🔴 | 🔴 | 🟡 |
| `verifiability` | 🟡 | 🟡 | 🔴 | ⬜ | 🟡 | ⬜ | ⬜ | ⬜ | 🟡 | ⬜ |
| `depends_on` | 🟡 | 🟡 | 🟡 | ⬜ | 🟡 | ⬜ | 🟡 | 🟡 | 🟡 | ⬜ |
| `valid_from` | 🟡 | 🟡 | ⬜ | ⬜ | 🟡 | ⬜ | 🟡 | 🟡 | 🟡 | 🟡 |
| `supersedes` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `superseded_by` | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| `derived_from` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `evolution_policy` | 🟡 | 🟡 | ⬜ | ⬜ | 🟡 | ⬜ | ⬜ | 🟡 | ⬜ | 🟡 |
| `ai_autonomy` | 🟡 | 🟡 | 🟡 | ⬜ | 🟡 | ⬜ | 🟡 | 🟡 | 🟡 | 🟡 |

> 🔴 = 必填 | 🟡 = 条件必填 | ⬜ = 可选

**条件必填说明**：

| 字段 | 条件 |
|------|------|
| `tags` | 当 `scope: layer` 时必填，需标注所属层 |
| `layer` | register/ADR 如为全局型则填 `cross_layer`，层域型填对应层 |
| `classification` | register/ADR 如含敏感信息则必填 `confidential` |
| `verifiability` | operational_rule 必填（操作规程必须可验证）; construction_plan 有可验证产出物时必填 |
| `depends_on` | 当文件依赖其他文件才能执行时必填 |
| `valid_from` | policy/standard/protocol/ADR/blueprint/construction_plan/roadmap 有生效日期时必填 |
| `evolution_policy` | policy/standard/protocol/blueprint/roadmap 有演进策略时必填 |
| `ai_autonomy` | 涉及 AI 操作权限时必填 |

**受控词表速查**：

| 字段 | 合法值 |
|------|--------|
| `rule_form` | `declarative` / `procedural` / `data` / `structural` |
| `scope` | `global` / `domain` / `layer` / `module` |
| `stability` | `frozen` / `stable` / `evolving` / `volatile` |
| `verifiability` | `automated` / `manual` / `inspection` |
