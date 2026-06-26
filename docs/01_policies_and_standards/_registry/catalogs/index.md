---
module_id: GOV-002
title: "登记表集中存储目录索引"
doc_type: index
status: Active
version: "2.1.0"
date: "2026-05-06"
summary: "_registry/catalogs/ 导航入口。v2.1.0：**文件/条数与 `registry-master-index`、`rule-catalog`、各登记表 `total_*` 字段对账**；勿使用历史常数（如「38 张」）。"
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

> **v2.0.0 更新（2026-05-02）**：原 v1.x 规则限制"仅放脚本自动生成的文件"已废弃。
> 原因是：登记表本质上属于同一类型（doc_type=register），按文件性质集中放置
> 优于按"谁创建了它"分类（对标 Linux FHS——同性质文件放同一目录）。
> 详见 PS-REG-005 registry-master-index.yaml §1。

## 文件清单（本目录 **24** 个文件：**23** 份登记/契约类工件 + **本 index.md**）

| 文件 | 类型 | 说明 | 维护方式 |
|------|:---:|------|:---:|
| `registry_master_index.yaml` | 总索引 | 登记表总索引——`total_registries` / `registries[]` 以本文件为准（**勿写死**） | manual |
| `document_metadata_index_registry.yaml` | 注册表 | 与 `rule_catalog_registry.yaml` 同步的规则树元数据索引（以生成器为准） | auto |
| `task_card_meta_registry.yaml` | 注册表 | 三套任务卡系统元层管理 | manual |
| `infrastructure_registry.yaml` | 登记表 | 运行时基础设施组件（以 `total_registered` 为准） | manual |
| `cross_module_dependency_registry.yaml` | 登记表 | 跨模块依赖——含正反向双图 | semi_auto |
| `script_health_registry.yaml` | 登记表 | 治理脚本维度/超时/健康评分 | semi_auto |
| `ai_risk_register.yaml` | 登记表 | AI操作特有风险——含热力矩阵 | manual |
| `knowledge_article_registry.yaml` | 登记表 | KMS知识条目索引 | semi_auto |
| `ai_session_registry.yaml` | 登记表 | AI Session摘要记录 | semi_auto |
| `frontmatter_field_registry.yaml` | 登记表 | frontmatter 字段的类型/必填性/枚举值 | manual |
| `directory_registry.yaml` | 登记表 | 目录——职责声明/轨道归属/index.md 存在性 | manual |
| `gate_registry.yaml` | 登记表 | 门禁（以 `total_gates` 为准）——pre-commit / 架构 / 元数据 等 | manual |
| `declarative_contract_tracker_registry.yaml` | 登记表 | 声明式契约跟踪（config 与蓝图承诺 vs 实现） | manual |
| `frontier_llm_benchmark_ranking.yaml` | 登记表 | 前沿 LLM 基准排名——模型能力/价格/延迟对比 | manual |
| `registry_of_registries.yaml` | 契约 | 登记表的登记表——跨登记表共享字段一致性契约 | manual |
| `ai_autonomy_authority_registry.yaml` | 登记表 | AI 自治权限登记表——全模块权限终表 | manual |
| `rule_catalog_registry.yaml` | 登记表 | 规则目录——全部规则的分类索引与交叉引用 | manual |
| `functional_domain_registry.yaml` | 登记表 | 功能域登记表——按功能域组织的模块注册 | manual |
| `master_document_inventory_registry.yaml` | 注册表 | 主文档清单——全项目文档的集中索引 | manual |
| `business_streams.yaml` | 登记表 | 业务流定义 | manual |
| `depgraph_scan_exclusions.yaml` | 登记表 | depgraph 扫描排除规则 | manual |
| `hard_boundaries.yaml` | 登记表 | 硬边界定义 | manual |

## 外部登记表（不在本目录，由 catalog 索引引用）

| 文件 | 位置 | registry_id |
|------|------|:--:|
| 模块ID注册表 | `02_enterprise_architecture/target_architecture/architecture_model/module_id_registry.yaml` | REG-MOD-001 |
| 模块生命周期登记表 | `03_modules/module_registry.yaml` | REG-MOD-002 |
| 蓝图深度评估登记表 | `03_modules/blueprint_registry.yaml` | REG-MOD-003 |
| Embedding模型注册表 | `config/embedding_model_registry.yaml` | REG-AI-002 |

> **已迁入**（2026-05-03）：model_capability_contract.yaml（→ `_registry/contracts/`）

## 排除规则（不应放入本目录的内容）

- ❌ policy/standard 类文件 → `governance/`
- ❌ template 类文件 → `templates/`
- ✅ YAML 格式的登记表允许存放在此（如 ai_autonomy_authority_registry.yaml），优先使用 YAML 格式
- ❌ 架构模型 YAML → `02_enterprise_architecture/target_architecture/architecture_model/`
- ❌ 运行时配置 YAML → `config/` 或 `src/zephyr/` 对应子包

## 父级目录

- 父级：[_registry](../index.md)
- 总索引：[registry_master_index.yaml](registry_master_index.yaml)
