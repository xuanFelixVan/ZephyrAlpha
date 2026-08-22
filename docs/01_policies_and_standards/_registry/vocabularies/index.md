---
doc_type: index
title: "_registry/vocabularies/ 目录索引"
status: Active
ttl: permanent
version: "2.1.0"
module_id: GOV-007
generated: '2026-08-17'
---

# Vocabularies — 目录索引

## 责任声明（Single Responsibility）

本目录存放：**AI 消费的 YAML 受控词表**。包括 `*_vocabulary.yaml` 模式的受控词表（39 个）以及 `terminology_mapping.yaml` 术语映射文件。

## 文件清单（40 个 YAML）

| 文件 | 说明 |
|------|------|
| ai_autonomy_level_planned_vocabulary.yaml | ai_autonomy_level_planned 受控词表（4 值） |
| ai_autonomy_vocabulary.yaml | ai_autonomy 受控词表（3 值） |
| ai_capability_slot_vocabulary.yaml | ai_capability_slot 受控词表（4 值） |
| blueprint_refs_status_vocabulary.yaml | blueprint_refs.status 受控词表（3 值） |
| category_vocabulary.yaml | category 受控词表（10 值） |
| classification_vocabulary.yaml | classification 受控词表（3 值） |
| compliance_tags_vocabulary.yaml | compliance_tags 受控词表（6 值） |
| contract_status_vocabulary.yaml | contract_status 受控词表（3 值） |
| created_by_vocabulary.yaml | created_by 受控词表（3 值） |
| decision_edge_type_vocabulary.yaml | decision_edge_type 受控词表（4 值：triggering/informing/constraining/approving） |
| decision_layer_vocabulary.yaml | decision_layer 受控词表（10 值：L0/L1/L2A~L2D/L3~L6） |
| dep_type_vocabulary.yaml | dep_type 受控词表（12 值：import_depends/references/test_depends 等） |
| depgraph_tags_vocabulary.yaml | depgraph nodes.tags 横切标签受控词表（1 值：ai_layer，#ARCH-169） |
| derived_from_relationship_vocabulary.yaml | derived_from.relationship 受控词表（3 值） |
| doc_type_vocabulary.yaml | doc_type 受控词表（10 值） |
| domain_vocabulary.yaml | domain 受控词表（10 值） |
| evolution_policy_vocabulary.yaml | evolution_policy 受控词表（3 值） |
| file_category_vocabulary.yaml | file_category 受控词表（10 值） |
| governance_family_vocabulary.yaml | governance_family 受控词表（4 值） |
| granularity_vocabulary.yaml | granularity 受控词表（4 值：file/directory/module/aggregated） |
| header_format_vocabulary.yaml | header_format 受控词表（7 值） |
| language_vocabulary.yaml | language 受控词表（3 值） |
| layer_vocabulary.yaml | layer 受控词表（4 值） |
| maturity_vocabulary.yaml | maturity 受控词表（4 值） |
| module_lifecycle_status_vocabulary.yaml | module_lifecycle_status 受控词表（8 值） |
| node_type_vocabulary.yaml | node_type 受控词表（23 值：module/script/test/blueprint 等） |
| provenance_audit_chain_verdict_vocabulary.yaml | provenance.audit_chain.verdict 受控词表（3 值） |
| review_status_vocabulary.yaml | review_status 受控词表（4 值） |
| rule_form_vocabulary.yaml | rule_form 受控词表（4 值） |
| safety_level_vocabulary.yaml | safety_level 受控词表（3 值） |
| scope_vocabulary.yaml | scope 受控词表（4 值） |
| section_type_vocabulary.yaml | section_type 受控词表（17 值） |
| semantic_vocabulary.yaml | semantic_type 受控词表（4 值） |
| stability_vocabulary.yaml | stability 受控词表（4 值） |
| startup_vocabulary.yaml | startup 受控词表（4 值） |
| status_vocabulary.yaml | status 受控词表（3 值） |
| target_layer_vocabulary.yaml | target_layer 受控词表（44 值：D_* 功能域全集） |
| terminology_mapping.yaml | 术语映射表 |
| ttl_vocabulary.yaml | ttl 受控词表（2 值） |
| verifiability_vocabulary.yaml | verifiability 受控词表（3 值） |

## 排除规则（不应放入本目录的内容）

- ❌ .md 文件 → `docs/02_enterprise_architecture/`（知识条目走 KB 知识库/KE 管线，docs/08_knowledge/ 已退役）

## 父级目录

- 父级：[_registry](../../_registry/index.md)
