---
module_id: ARCH-SMP-006
title: "物理路径树样板"
doc_type: architecture_view
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 物理路径树样板

> 这是给人看的项目物理结构图——文件怎么组织的、每个目录是干什么的。
> 格式参考 information_architecture.md：中英文对照+功能简述。

---

## 中文版

```
ZephyrAlpha/
├── docs/                           — 文档根目录：所有文档的真源 / Documents root: source of truth for all docs
│   ├── 00_governance/              — 治理总控：系统如何被管理 / Governance control: how the system is managed
│   ├── 01_policies_and_standards/  — 政策与标准：定义合格产物标准 / Policies and standards: defines qualified artifact standards
│   ├── 02_enterprise_architecture/ — 企业架构：全系统总体架构真源 / Enterprise architecture: full-system overall architecture canonical source
│   ├── 03_modules/                 — 模块生命周期文档：蓝图+施工图+交付记录 / Module lifecycle documents: blueprint + construction plan + delivery records
│   ├── 06_security_and_identity/   — 安全与身份：权限、身份、密钥与安全边界 / Security and identity: permissions, identity, keys and security boundaries
│   ├── 07_sre_and_platform_ops/    — SRE与平台运维：稳定性、监控、恢复 / SRE and platform ops: stability, monitoring, recovery
│   ├── 08_knowledge/               — 知识库：长期知识资产与可复用认知 / Knowledge base: long-term knowledge assets and reusable insights
│   ├── 09_data_platform/           — 数据平台：数据接入、存储、质量与血缘 / Data platform: data ingestion, storage, quality, lineage
│   ├── 10_research_and_factor_lab/ — 研究与因子实验室：研究框架、因子研究与实验 / Research and factor lab: research frameworks, factor research, experiments
│   ├── 11_model_and_ml_platform/   — 模型与机器学习平台：模型训练、部署、监控与版本 / Model and ML platform: model training, deployment, monitoring, versioning
│   ├── 12_strategy_and_portfolio/   — 策略与组合：策略逻辑、资金分配与组合管理 / Strategy and portfolio: strategy logic, capital allocation, portfolio management
│   ├── 13_execution_and_order_lifecycle/ — 执行与订单生命周期：委托、成交、路由与执行链路 / Execution and order lifecycle: orders, fills, routing
│   ├── 14_reporting_and_distribution/ — 报告与分发：简报生成、消息推送与结果分发 / Reporting and distribution: briefing generation, messaging, delivery
│   ├── 16_compliance_and_legal/    — 合规与法务：法规要求与法律边界 / Compliance and legal: regulatory requirements and legal boundaries
│   └── 17_risk_and_controls/       — 风险与控制：风险政策与控制框架 / Risk and controls: risk policies and control frameworks
├── scripts/                        — 脚本根目录：所有可执行脚本 / Scripts root: all executable scripts
│   ├── governance/                 — 治理脚本：审计、校验、生成器 / Governance scripts: audit, validate, generators
│   ├── construction/               — 施工脚本：建卡、施工、验收 / Construction scripts: task card, build, verify
│   └── ...                         — 其他脚本目录 / Other script directories
├── src/zephyr/                     — 源代码根目录：所有业务模块 / Source root: all business modules
│   ├── trading/                    — 交易模块：订单、执行、成交、持仓 / Trading modules: order, execution, fill, position
│   ├── governance/                 — 治理模块：规则、审计、质量 / Governance modules: rules, audit, quality
│   └── ...                         — 其他模块目录 / Other module directories
├── tests/                          — 测试根目录：所有测试文件 / Tests root: all test files
├── data/                           — 数据文件：数据库、配置、资产 / Data files: databases, configs, assets
│   ├── databases/                  — 数据库：depgraph.db 全景图 / Databases: depgraph.db panorama
│   └── ...
└── ...
```

---

## 说明

- **数据源**：`depgraph.db` 的 `arch_directory_tree` 表
- **生成器**：`generate_path_tree.py`
- **维护方式**：自动生成，全景图更新时刷新
- **格式要求**：代码块包裹，中英文对照+功能简述，格式参考 information_architecture.md
