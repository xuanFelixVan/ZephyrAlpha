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
---

# Catalogs — 登记表集中存储目录

## 责任声明（Single Responsibility）

本目录存放 ZephyrAlpha 项目所有**登记表/注册表/清单类型的 YAML 文件**。

> **v2.0.0 更新（2026-05-02）**：原 v1.x 规则限制"仅放脚本自动生成的文件"已废弃。
> 原因是：登记表本质上属于同一类型（doc_type=register），按文件性质集中放置
> 优于按"谁创建了它"分类（对标 Linux FHS——同性质文件放同一目录）。
> 详见 PS-REG-005 registry-master-index.yaml §1。

## 文件清单（本目录 **23** 个文件：**22** 份登记/契约类工件 + **本 index.md**）

| 文件 | 类型 | 说明 | 维护方式 |
|------|:---:|------|:---:|
| `registry-master-index.yaml` | 总索引 | 登记表总索引——`total_registries` / `registries[]` 以本文件为准（**勿写死**） | manual |
| `document-metadata-index-registry.yaml` | 注册表 | 与 `rule-catalog-registry.yaml` 同步的规则树元数据索引（**141** 条，以生成器为准） | auto |
| `adr-status-registry.yaml` | 登记表 | ~~KB 决策记录 状态登记表~~（**已删除**；真源迁移至 KB，见 KE-governance-adr_registry_migration-000） | ~~manual~~ |
| `task-card-meta-registry.md` | 注册表 | 三套任务卡系统元层管理 | manual |
| `infrastructure-registry.md` | 登记表 | **9** 个运行时基础设施组件（以 `total_registered` 为准） | manual |
| `cross-module-dependency-registry.yaml` | 登记表 | 5条跨模块依赖——含正反向双图 | semi_auto |
| `script-health-registry.md` | 登记表 | 39个治理脚本维度/超时/健康评分 | semi_auto |
| `ai-risk-registry.md` | 登记表 | 8个AI操作特有风险——含热力矩阵 | manual |
| `knowledge-article-registry.md` | 登记表 | KMS知识条目索引（beta 落地） | semi_auto |
| `ai-session-registry.md` | 登记表 | AI Session摘要记录（beta 落地） | semi_auto |
| `frontmatter-field-registry.md` | 登记表 | 40个 frontmatter 字段的类型/必填性/枚举值 | manual |
| `directory-registry.md` | 登记表 | **83** 个目录——职责声明/轨道归属/index.md 存在性 | manual |
| `gate-registry.md` | 登记表 | **25** 个门禁（以 `total_gates` 为准）——pre-commit / 架构 / 元数据 等 | manual |
| `declarative-contract-tracker-registry.md` | 登记表 | **11** 条声明式契约跟踪（config 与蓝图承诺 vs 实现） | manual |
| `frontier-llm-benchmark-ranking.md` | 登记表 | 前沿 LLM 基准排名——模型能力/价格/延迟对比 | manual |
| `rule-registry.md` | 登记表 | 规则登记表——全部规则的集中发现入口（v1.4.0，从 meta/ 迁入） | manual |
| `registry_of_registries.yaml` | 契约 | 登记表的登记表——跨登记表共享字段一致性契约（v1.1.0，从 meta/ 迁入） | manual |
| `ai-autonomy-authority-registry.md` | 登记表 | AI 自治权限登记表——全模块权限终表（v1.3.0，从 governance/ai/ 迁入） | manual |
| `rule-catalog-registry.yaml` | 登记表 | 规则目录——全部规则的分类索引与交叉引用 | manual |
| `functional-domain-registry.yaml` | 登记表 | 功能域登记表——按功能域组织的模块注册 | manual |
| `master-document-inventory-registry.md` | 注册表 | 主文档清单——全项目文档的集中索引 | manual |
| `project-path-tree.yaml` | 登记表 | 项目物理路径树——磁盘目录结构快照 | manual |

## 外部登记表（不在本目录，由 catalog 索引引用）

| 文件 | 位置 | registry_id |
|------|------|:--:|
| 模块ID注册表 | `02_enterprise_architecture/.../module_id_registry.yaml` | REG-MOD-001 |
| 模块生命周期登记表 | `03_modules/module-registry.yaml` | REG-MOD-002 |
| 蓝图深度评估登记表 | `03_modules/blueprint-registry.yaml` | REG-MOD-003 |
| Embedding模型注册表 | `src/zephyr/config/embedding_model_registry.yaml` | REG-AI-002 |

> **已迁入**（2026-05-03）：rule-registry.md、registry_of_registries.yaml、ai-autonomy-authority-registry.md、model-capability-contract.yaml（→ `_registry/contracts/`）

## 排除规则（不应放入本目录的内容）

- ❌ policy/standard 类文件 → `governance/`
- ❌ template 类文件 → `templates/`
- ✅ .md 格式的登记表允许存放在此（如 rule-registry.md、ai-autonomy-authority-registry.md），但优先使用 YAML 格式
- ❌ 架构模型 YAML → `02_enterprise_architecture/target-architecture/architecture-model/`
- ❌ 运行时配置 YAML → `config/` 或 `src/zephyr/` 对应子包

## 父级目录

- 父级：[_registry](../../_registry/index.md)
- 总索引：[registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml)
