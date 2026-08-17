---
doc_type: index
title: "_registry/contracts/ 目录索引"
status: Active
ttl: permanent
version: "1.0.2"
module_id: GOV-004
generated: '2026-08-17'
---

# Contracts — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**CI 消费的 YAML 验证契约**。

## 文件清单

| 文件 | 说明 |
|------|------|
| architecture_contract.yaml | 架构合规自动验证契约（VR-001~VR-011） |
| model_capability_contract.yaml | AI 模型能力矩阵契约（9 个模型） |
| contract_mapping_table.yaml | 契约映射表——契约 ID 与文件路径双向索引 |
| data_retention_contract.yaml | 数据保留与回测分层契约（数据保留策略+分层体系唯一真源） |
| directory_contract.yaml | 目录契约（目录维度约束唯一真源——目录责任/归属规则） |

## 排除规则（不应放入本目录的内容）

- ❌ .md 文件 → `docs/02_enterprise_architecture/`（知识条目走 KB 知识库/KE 管线，docs/08_knowledge/ 已退役）

## 父级目录

- 父级：[_registry](../../_registry/index.md)
