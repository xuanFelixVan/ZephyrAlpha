---
module_id: GOV-002
title: "登记表集中存储目录索引"
doc_type: index
status: Active
version: "2.3.0"
date: "2026-06-26"
summary: "_registry/catalogs/ 导航入口。v2.3.0：P2-1 向内收——删除 document_metadata_index_registry.yaml（与 rule_catalog_registry.yaml 同源同数据的真重复），所有引用重定向至 rule_catalog_registry.yaml（PS-REG-018）。计数 28→27→26。"
tags: [index, catalogs, registry, navigation]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
ttl: permanent
---

# Catalogs — 登记表集中存储目录

## 责任声明（Single Responsibility）

本目录存放 ZephyrAlpha 项目所有**登记表/注册表/清单类型的 YAML 文件**。

> **v2.0.0 更新（2026-05-02）**：原 v1.x 规则限制"仅放脚本自动生成的文件"不再适用。
> 原因是：登记表本质上属于同一类型（doc_type=register），按文件性质集中放置
> 优于按"谁创建了它"分类（对标 Linux FHS——同性质文件放同一目录）。
> 详见 PS-REG-005 registry-master-index.yaml §1。

## 文件清单（本目录 **26** 个文件：**25** 份登记/契约类工件 + **本 index.md**）

| 文件 | 类型 | 说明 | 维护方式 |
|------|:---:|------|:---:|
| `registry_master_index.yaml` | 总索引 | 登记表总索引——`total_registries` / `registries[]` 以本文件为准（**勿写死**）；由 `generate_registry_master_index.py` 自动生成 | auto |
| `_index.yaml` | 别名表 | TRAE 规则高级别名表（PS-REG-001，RULE-ZERO..RULE-TWENTY） | manual |
| `architecture_issue_registry.yaml` | 登记表 | 架构问题登记（#ARCH-XXX） | manual |
| `capability_canonical_file_registry.yaml` | 登记表 | 能力-规范文件映射（capability_id → canonical_file） | semi_auto |
| `derived_identifier_registry.yaml` | 登记表 | 派生标识符规则（blueprint_id/node_path 从 domain_id 派生） | manual |
| `domain_naming_rules.yaml` | 登记表 | 域命名规则（NR-001..005，apply_depgraph --insert-domain 强制） | manual |
| `task_card_meta_registry.yaml` | 注册表 | 三套任务卡系统元层管理 | manual |
| `infrastructure_registry.yaml` | 登记表 | 运行时基础设施组件（以 `total_registered` 为准） | manual |
| `cross_module_dependency_registry.yaml` | 登记表 | 跨模块依赖——含正反向双图 | semi_auto |
| `ai_risk_register.yaml` | 登记表 | AI操作特有风险——含热力矩阵 | manual |
| `knowledge_article_registry.yaml` | 登记表 | KMS知识条目索引 | semi_auto |
| `ai_session_registry.yaml` | 登记表 | AI Session摘要记录 | semi_auto |
| `frontmatter_field_registry.yaml` | 登记表 | frontmatter 字段的类型/必填性/枚举值 | manual |
| `directory_registry.yaml` | 登记表 | 目录——职责声明/轨道归属/index.md 存在性 | manual |
| `gate_registry.yaml` | 登记表 | 门禁（以 `total_gates` 为准）——pre-commit / 架构 / 元数据 等 | auto |
| `declarative_contract_tracker_registry.yaml` | 登记表 | 声明式契约跟踪（config 与蓝图承诺 vs 实现） | manual |
| `frontier_llm_benchmark_ranking.yaml` | 登记表 | 前沿 LLM 基准排名——模型能力/价格/延迟对比 | manual |
| `registry_consistency_contract.yaml` | 契约 | 登记表的登记表——跨登记表共享字段一致性契约 | manual |
| `ai_autonomy_authority_registry.yaml` | 登记表 | AI 自治权限登记表——全模块权限终表 | manual |
| `rule_catalog_registry.yaml` | 登记表 | 规则目录——全部规则的分类索引与交叉引用 | auto |
| `functional_domain_registry.yaml` | 登记表 | 功能域登记表——按功能域组织的模块注册 | manual |
| `business_streams_registry.yaml` | 登记表 | 业务流定义 | manual |
| `depgraph_scan_exclusions.yaml` | 登记表 | depgraph 扫描排除规则（数据真源，规则定义见 trae_058） | manual |
| `hard_boundaries_registry.yaml` | 登记表 | 硬边界定义 | manual |

## 外部登记表（不在本目录，由 catalog 索引引用）

| 文件 | 位置 | registry_id |
|------|------|:--:|
| 模块ID注册表 | `architecture_model/module_id_registry.yaml` | REG-MOD-ALPHA_SIGNAL_DOMAIN |
| 蓝图深度评估登记表 | `03_modules/blueprint_registry.yaml` | REG-MOD-003 |
| Embedding模型注册表 | `config/embedding_model_registry.yaml` | REG-AI-002 |

> **已迁入**（2026-05-03）：model_capability_contract.yaml（→ `_registry/contracts/`）

## 排除规则（不应放入本目录的内容）

- ❌ policy/standard 类文件 → `governance/`
- ❌ template 类文件 → `templates/`
- ✅ YAML 格式的登记表允许存放在此（如 ai_autonomy_authority_registry.yaml），优先使用 YAML 格式
- ❌ 架构模型 YAML → `architecture_model/`
- ❌ 运行时配置 YAML → `config/` 或 `src/zephyr/` 对应子包

## 父级目录

- 父级：[_registry](../index.md)
- 总索引：[registry_master_index.yaml](registry_master_index.yaml)
