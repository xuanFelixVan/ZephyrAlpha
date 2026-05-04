---
module_id: CAT-IDX-001
title: "登记表集中存储目录索引"
doc_type: index
status: active
version: "2.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
summary: "_registry/catalogs/ 目录的导航入口。存放 ZephyrAlpha 项目所有登记表/注册表/清单类型的 YAML 文件。"
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

## 文件清单（20 entries）

| 文件 | 类型 | 说明 | 维护方式 |
|------|:---:|------|:---:|
| `registry-master-index.yaml` | 总索引 | 登记表总索引——一站式查找所有38张登记表 | manual |
| `document-metadata-index.yaml` | 注册表 | 127个文件元数据索引（auto-generated）——取代旧的 master-document-inventory.yaml | auto |
| `master-document-inventory.yaml` | 清单 | ⛔ deprecated——被 document-metadata-index.yaml 取代（手动 25/131 vs 自动 127/131） | — |
| `task-card-meta-registry.yaml` | 注册表 | 三套任务卡系统元层管理 | manual |
| `infrastructure-registry.yaml` | 登记表 | 8个运行时基础设施组件 | manual |
| `cross-module-dependency-registry.yaml` | 登记表 | 5条跨模块依赖——含正反向双图 | semi_auto |
| `script-health-registry.yaml` | 登记表 | 39个治理脚本维度/超时/健康评分 | semi_auto |
| `ai-risk-register.yaml` | 登记表 | 8个AI操作特有风险——含热力矩阵 | manual |
| `knowledge-article-registry.yaml` | 登记表 | KMS知识条目索引（Phase 3 落地） | semi_auto |
| `ai-session-registry.yaml` | 登记表 | AI Session摘要记录（Phase 2 落地） | semi_auto |
| `frontmatter-field-registry.yaml` | 登记表 | 40个 frontmatter 字段的类型/必填性/枚举值 | manual |
| `directory-registry.yaml` | 登记表 | 82个目录——职责声明/轨道归属/index.md 存在性 | manual |
| `gate-registry.yaml` | 登记表 | 34个门禁分 5 类——pre-commit/KMS管道/架构评审/准入/VC | manual |
| `adr-status-registry.yaml` | 登记表 | 41个 ADR——accepted/superseded/skipped/reserved 状态 | manual |
| `declarative-contract-tracker.yaml` | 登记表 | 5条声明式契约——YAML 承诺 vs Python 实现的差距跟踪 | manual |
| `frontier-llm-benchmark-ranking.md` | 登记表 | 前沿 LLM 基准排名——模型能力/价格/延迟对比 | manual |
| `rule-registry.md` | 登记表 | 规则登记表——全部规则的集中发现入口（v1.4.0，从 meta/ 迁入） | manual |
| `registry-of-registries.yaml` | 契约 | 登记表的登记表——跨登记表共享字段一致性契约（v1.1.0，从 meta/ 迁入） | manual |
| `ai-autonomy-authority-registry.md` | 登记表 | AI 自治权限登记表——全模块权限终表（v1.3.0，从 governance/ai/ 迁入） | manual |
| `rule-catalog.yaml` | 登记表 | 规则目录——全部规则的分类索引与交叉引用 | manual |

## 外部登记表（不在本目录，由 catalog 索引引用）

| 文件 | 位置 | registry_id |
|------|------|:--:|
| 模块ID注册表 | `02_enterprise_architecture/.../module-id-registry.yaml` | REG-MOD-001 |
| 模块生命周期登记表 | `03_modules/module-registry.yaml` | REG-MOD-002 |
| 蓝图深度评估登记表 | `03_modules/blueprint-registry.yaml` | REG-MOD-003 |
| Embedding模型注册表 | `src/zephyr/config/embedding_model_registry.yaml` | REG-AI-002 |

> **已迁入**（2026-05-03）：rule-registry.md、registry-of-registries.yaml、ai-autonomy-authority-registry.md、model-capability-contract.yaml（→ `_registry/contracts/`）

## 排除规则（不应放入本目录的内容）

- ❌ policy/standard 类文件 → `governance/`
- ❌ template 类文件 → `templates/`
- ✅ .md 格式的登记表允许存放在此（如 rule-registry.md、ai-autonomy-authority-registry.md），但优先使用 YAML 格式
- ❌ 架构模型 YAML → `02_enterprise_architecture/target-architecture/architecture-model/`
- ❌ 运行时配置 YAML → `config/` 或 `src/zephyr/` 对应子包

## 父级目录

- 父级：[_registry](../../_registry/index.md)
- 总索引：[registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml)
