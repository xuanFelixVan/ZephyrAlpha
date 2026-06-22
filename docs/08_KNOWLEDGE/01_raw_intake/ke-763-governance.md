---
module_id: KE-686
status: active
title: 1.1 目的
category: governance
---

# 1.1 目的

1.1 目的

**`docs/01_policies_and_standards/_registry/catalogs/*.yaml` 的自动收录清单**以 [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml) 的 **`total_registries`** 为唯一真源（**勿手写常数**；以 `generate_registry_master_index.py` 最近一次输出为准）。下表描述 **MRS-001 登记目标分类**（15 类工件域；含域外路径如 `03_modules/*.yaml`），**不得**与 `total_registries` 混为一谈。

| 分类 | 登记表数 | 示例 |
|------|:---:|------|
| governance_rule | 2 | document-metadata-index-registry.yaml |
| document | 1 | document-metadata-index-registry.yaml（原 master-document-inventory-registry.md 已废弃） |
| module | 4 | module-registry.yaml, blueprint-registry.yaml, module_id_registry.yaml, task-card-meta-registry.md |
| ai_asset | 4 | ai_autonomy_authority_registry.yaml, embedding_model_registry.yaml |
| risk | 1 | ai-risk-registry.md |
| infrastructure | 1 | infrastructure-registry.md |
| dependency | 1 | cross-module-dependency-registry.yaml |
| operational | 1 | script-health-registry.md |
| knowledge | 1 | knowledge-article-registry.md |
| vocabulary | 3 | doc_type / rule_form / status 受控词表 |
| contract | 1 | architecture-contract.yaml |
| field_definition | 1 | frontmatter-field-registry.md |
| physical_structure | 1 | directory-registry.md |
| quality_gate | 1 | gate-registry.md |
| architecture_decision | 1 | adr-status-registry.yaml（冻结壳；ADR 物理树已废弃，决策见 KB/rationale） |

修改任何一个登记表的共享字段而不同步其他相关登记表，会导致数据不一致——这正是 4 轮审计抓住 25 个问题的共同根因（最初发生在模块登记表，但根本原因适用于所有分类）。

本标准定义：**创建/修改任何项目工件（artifact）后，必须同步更新哪些登记表、更新顺序、校验方式**。
