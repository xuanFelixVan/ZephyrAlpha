---
module_id: GOV-030
title: "文档模板目录索引"
doc_type: index
status: Active
version: "1.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
summary: "templates/ 目录的导航入口。列出全部 9 个文档模板。"
tags: [index, templates, navigation]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
---

# Templates — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**文档模板 — policy/standard/runbook/playbook/KB 决策记录/blueprint/roadmap/risk-register 模板**。

## 文件清单（本目录 **9** 个模板 + **本 index.md**）

| 文件 | 说明 |
|------|------|
| `blueprint_construction_template.md` | 蓝图+施工图模板 |
| `dependency_graph_template.md` | 依赖图数据结构模板 |
| `playbook_runbook.md` | Playbook 模板 |
| `policy_template.md` | Policy 模板（含已废弃 protocol 类型，protocol migrated_to policy） |
| `register_template.md` | Register/Registry 模板 |
| `risk_register_template.md` | 风险登记表模板 |
| `roadmap_template.md` | Roadmap 模板 |
| `runbook_template.md` | Runbook 模板 |
| `standard_template.md` | Standard 模板 |

## 排除规则（不应放入本目录的内容）

- ❌ 正式规则文件 → `01_policies_and_standards/rules/`（governance/、operational/ 目录已删除合并至 rules/）
- ❌ 模块文档 → `03_modules/`

## 父级目录

- 父级：[01_policies_and_standards](../index.md)
