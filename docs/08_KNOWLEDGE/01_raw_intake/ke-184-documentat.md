---
module_id: KE-166
status: active
title: 2.1 全局字段总表
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 全局字段总表

2.1 全局字段总表

> **Canonical SSoT**：`_registry/catalogs/frontmatter-field-registry.md`（PS-REG-012）
>
> 以下仅列出字段名和必填阶段速查。完整的字段定义（类型、枚举值、描述、对标机构）请查阅 **PS-REG-012**，本文件不再重复。

| 字段 | 必填阶段 | 字段 | 必填阶段 |
|------|---------|------|---------|
| `module_id` | Draft+ | `title` | Draft+ |
| `doc_type` | Draft+ | `status` | Draft+ |
| `version` | Draft+ | `date` | Draft+ |
| `owner` | Draft+ | `layer` | Active+ |
| `classification` | Active+ | `language` | Active+ |
| `created_by` | Active+ | `ttl` | Active+ |
| `summary` | Active+ | `tags` | Active+ |
| `valid_from` | Active+ | `rule_form` | Active+ |
| `depends_on` | Active+ | `supersedes` | Active+ |
| `superseded_by` | Deprecated | `derived_from` | optional |
| `related_adr` | optional | `safety_level` | optional |
| `evolution_policy` | optional | `ai_autonomy` | optional |
| `provenance` | optional | `author_agent` | optional |
| `governance_family` | optional | `ai_capability_slot` | optional |
| `ai_autonomy_level_planned` | optional | `ai_employee_count_planned` | optional |
| `blueprint_refs` | optional | `compliance_tags` | optional |
| `human_override` | optional | `last_reviewed_by` | optional |
| `review_status` | optional | `category` | optional |
| `domain` | optional | `verifiability` | optional |
| `scope` | optional | `stability` | optional |
| `custom_*` | optional | | |
