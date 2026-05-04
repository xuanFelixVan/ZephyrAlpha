---
module_id: DOM-IDX-001
title: "层域规则目录索引"
doc_type: index
status: active
version: "1.0.1"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-04"
ttl: permanent
summary: "domains/ 目录的导航入口。列出 4 个架构层的层域规则（L00/L02/L04/L07），每层含 governance/ + operational/ 子目录。"
tags: [index, domains, navigation]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
---

# Domains — 目录索引

> **module_id**: DOM-IDX-001 | **version**: 1.0.0 | **status**: active

## 责任声明（Single Responsibility）

本目录只存放：**层域特定规则（L00/L02/L04/L07）— 每个层域下有 governance/ + operational/**。

## 文件清单

| 层域 | 用途 | governance/ | operational/ | 合计 |
|------|------|:---:|:---:|:---:|
| [L00_data_source/](L00_data_source/index.md) | 数据源层 | 2 | 2 | 5 |
| [L02_alpha_factor/](L02_alpha_factor/index.md) | Alpha 因子层 | 2 | 2 | 5 |
| [L04_risk_management/](L04_risk_management/index.md) | 风险管理层 | 2 | 2 | 5 |
| [L07_post_trade_analytics/](L07_post_trade_analytics/index.md) | 盘后分析层 | 2 | 2 | 5 |

> **合计**：4 个架构层，21 个文件（含索引入口 5 个）。

## 排除规则（不应放入本目录的内容）

- ❌ 全局规则（影响所有层） → `01_policies_and_standards/governance/ 或 operational/`

## 父级目录

- 父级：[01_policies_and_standards](../index.md)
