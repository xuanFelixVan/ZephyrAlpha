---
module_id: OPS-IDX-001
title: "操作手册目录索引"
doc_type: index
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
summary: "operational/ 目录的导航入口。列出 3 个操作子域的目录结构和文件清单。新 AI session 进入操作域时，应首先读取本文件以建立全局认知。"
tags: [index, operational, navigation]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
---

# Operational — 目录索引

> **module_id**: OPS-IDX-001 | **version**: 1.0.0 | **status**: active

## 责任声明（Single Responsibility）

本目录只存放：**过程式操作手册 — vibe_coding/（VC 操作）、devops/（CI/部署）、migration/（迁移）**。

## 文件清单

| 子目录 | 用途 | 文件数 |
|--------|------|:---:|
| [`vibe_coding/`](vibe_coding/index.md) | Vibe Coding 操作——上下文规则、session 状态机、门禁清单、应急手册 | 4 |
| [`devops/`](devops/index.md) | DevOps 操作——pre-commit、CI、架构变更 playbook | 2 |
| [`migration/`](migration/index.md) | 迁移操作——老树→新树审计 | 1 |

> **合计**：3 个子目录，8 个文件（含索引入口 4 个）。

## 排除规则（不应放入本目录的内容）

- ❌ 声明式治理规则 → `01_policies_and_standards/governance/`
- ❌ 层域特定规则 → `01_policies_and_standards/domains/`

## 父级目录

- 父级：[01_policies_and_standards](../index.md)
