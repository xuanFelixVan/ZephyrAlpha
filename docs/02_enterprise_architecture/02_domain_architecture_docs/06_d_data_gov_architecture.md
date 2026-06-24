---
doc_type: domain_architecture_diagram
title: D-DATA_GOV 数据治理架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 06_d_data_gov / 数据治理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示数据治理（D-DATA_GOV）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 数据治理（D-DATA_GOV）的模块分布。共 38 个模块 / 38 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (38 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   AI治理血缘 AI Governance Lineage  [design]                     │
│   AI驱动数据质量监控 AI-driven Data Quality  [design]            │
│   Apache Polaris目录 Apache Polaris Catalog  [design]            │
│   BlackRock AI数据质量三阶段 BlackRock AI Data Quality  [design] │
│   C-022 数据质量自管理 Data Quality Self-management  [design]    │
│   CTR-TRACE-001血缘ID贯穿全链路 Lineage ID End-to-end  [design]  │
│   Data Catalog 数据目录  [design]                                │
│   Data Lineage 数据血缘  [design]                                │
│   Data Quality Gate 数据质量门禁  [design]                       │
│   Data Quality SLA 数据质量SLA  [design]                         │
│   DataQualityDegraded 数据质量降级  [design]                     │
│   DataQualityDegraded 数据质量降级事件  [design]                 │
│   DataQualityError 数据质量错误  [design]                        │
│   MVP用SQLite存储血缘 SQLite for Lineage MVP  [design]           │
│   Market Regime Reference Data 市场状态分类参考数据  [design]    │
│   Metadata Registry MDM 元数据注册中心MDM  [design]              │
│   OpenLineage标准适配 OpenLineage Adaptation  [design]           │
│   Quality Gate Four-Level 质量门禁四级贯穿  [design]             │
│   ...还有 20 个模块 / 20 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 38 个模块 / 38 modules）。

### 未分类 / Unclassified (38 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-DATA-GOV/AI治理血缘 AI Governance Lineage | AI治理血缘 AI Governance Lineage | design | design_only |
| 2 | D-DATA-GOV/AI驱动数据质量监控 AI-driven Data Quality | AI驱动数据质量监控 AI-driven Data Qua... | design | design_only |
| 3 | D-DATA-GOV/Apache Polaris目录 Apache Polaris Catalog | Apache Polaris目录 Apache Polaris Cat... | design | design_only |
| 4 | D-DATA-GOV/BlackRock AI数据质量三阶段 BlackRock AI Data Q... | BlackRock AI数据质量三阶段 BlackRock ... | design | design_only |
| 5 | D-DATA-GOV/C-022 数据质量自管理 Data Quality Self-management | C-022 数据质量自管理 Data Quality Sel... | design | design_only |
| 6 | D-DATA-GOV/CTR-TRACE-001血缘ID贯穿全链路 Lineage ID End-t... | CTR-TRACE-001血缘ID贯穿全链路 Lineage... | design | design_only |
| 7 | D-DATA-GOV/Data Catalog 数据目录 | Data Catalog 数据目录 | design | design_only |
| 8 | D-DATA-GOV/Data Lineage 数据血缘 | Data Lineage 数据血缘 | design | design_only |
| 9 | D-DATA-GOV/Data Quality Gate 数据质量门禁 | Data Quality Gate 数据质量门禁 | design | design_only |
| 10 | D-DATA-GOV/Data Quality SLA 数据质量SLA | Data Quality SLA 数据质量SLA | design | design_only |
| 11 | D-DATA-GOV/DataQualityDegraded 数据质量降级 | DataQualityDegraded 数据质量降级 | design | design_only |
| 12 | D-DATA-GOV/DataQualityDegraded 数据质量降级事件 | DataQualityDegraded 数据质量降级事件 | design | design_only |
| 13 | D-DATA-GOV/DataQualityError 数据质量错误 | DataQualityError 数据质量错误 | design | design_only |
| 14 | D-DATA-GOV/MVP用SQLite存储血缘 SQLite for Lineage MVP | MVP用SQLite存储血缘 SQLite for Lineag... | design | design_only |
| 15 | D-DATA-GOV/Market Regime Reference Data 市场状态分类参考数据 | Market Regime Reference Data 市场状态... | design | design_only |
| 16 | D-DATA-GOV/Metadata Registry MDM 元数据注册中心MDM | Metadata Registry MDM 元数据注册中心MDM | design | design_only |
| 17 | D-DATA-GOV/OpenLineage标准适配 OpenLineage Adaptation | OpenLineage标准适配 OpenLineage Adapt... | design | design_only |
| 18 | D-DATA-GOV/Quality Gate Four-Level 质量门禁四级贯穿 | Quality Gate Four-Level 质量门禁四级贯穿 | design | design_only |
| 19 | D-DATA-GOV/Quality Gate 质量门禁 | Quality Gate 质量门禁 | design | design_only |
| 20 | D-DATA-GOV/Reference Data 参考数据 | Reference Data 参考数据 | design | design_only |
| 21 | D-DATA-GOV/Security Master Manager 证券主数据管理器 | Security Master Manager 证券主数据管理器 | design | design_only |
| 22 | D-DATA-GOV/分阶段实现MVP→V2→V3→V4 Phased Lineage | 分阶段实现MVP→V2→V3→V4 Phased Lineage | design | design_only |
| 23 | D-DATA-GOV/列级血缘 Column-level Lineage | 列级血缘 Column-level Lineage | design | design_only |
| 24 | D-DATA-GOV/列级血缘而非表级 Column-level over Table-level | 列级血缘而非表级 Column-level over Ta... | design | design_only |
| 25 | D-DATA-GOV/列级血缘自动化 Column-level Lineage Automation | 列级血缘自动化 Column-level Lineage A... | design | design_only |
| 26 | D-DATA-GOV/数据域规则目录 Data Domain Rule Catalog | 数据域规则目录 Data Domain Rule Catalog | design | design_only |
| 27 | D-DATA-GOV/数据源质量评分 Data Source Quality Scoring | 数据源质量评分 Data Source Quality Sc... | design | design_only |
| 28 | D-DATA-GOV/数据血缘 Data Lineage | 数据血缘 Data Lineage | design | design_only |
| 29 | D-DATA-GOV/数据质量 Data Quality | 数据质量 Data Quality | design | design_only |
| 30 | D-DATA-GOV/数据质量五维度定义 ISO 8000 Five Dimensions | 数据质量五维度定义 ISO 8000 Five Dime... | design | design_only |
| 31 | D-DATA-GOV/数据质量记分卡 Data Quality Scorecard | 数据质量记分卡 Data Quality Scorecard | design | design_only |
| 32 | D-DATA-GOV/盘前质量检查 Pre-market Quality Check | 盘前质量检查 Pre-market Quality Check | design | design_only |
| 33 | D-DATA-GOV/血缘成熟度模型 Lineage Maturity Model | 血缘成熟度模型 Lineage Maturity Model | design | design_only |
| 34 | D-DATA-GOV/血缘追踪链 Lineage Tracking Chain | 血缘追踪链 Lineage Tracking Chain | design | design_only |
| 35 | D-DATA-GOV/血缘链全景 Lineage Chain Panorama | 血缘链全景 Lineage Chain Panorama | design | design_only |
| 36 | D-DATA-GOV/质量检查按交易时段分三阶段 Three-stage Quality... | 质量检查按交易时段分三阶段 Three-stag... | design | design_only |
| 37 | D-DATA-GOV/质量检查自建而非Great Expectations Self-built ... | 质量检查自建而非Great Expectations Se... | design | design_only |
| 38 | D-DATA-GOV/质量检查自建而非Great Expectations Self-built ... | 质量检查自建而非Great Expectations Se... | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 37 条 / 37 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 37 条 / 37 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 23 条 / edges                                │
│   [runtime]: 8 条 / edges                                        │
│   [event]: 2 条 / edges                                          │
│   [contract]: 2 条 / edges                                       │
│   [config_depends]: 2 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (23 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Data Catalog 数据目录 → 数据质量 Data Quality                  │
│   Data Catalog 数据目录 → Reference Data 参考数据                │
│   数据质量 Data Quality → 数据血缘 Data Lineage                  │
│   数据质量 Data Quality → BlackRock AI数据质量三阶...            │
│   数据血缘 Data Lineage → AI治理血缘 AI Governance ...           │
│   数据血缘 Data Lineage → 列级血缘自动化 Column-lev...           │
│   AI治理血缘 AI Governance ... → 数据源质量评分 Data Sourc...    │
│   AI治理血缘 AI Governance ... → Apache Polaris目录 Apache...    │
│   数据源质量评分 Data Sourc... → 血缘链全景 Lineage Chain ...    │
│   血缘链全景 Lineage Chain ... → 列级血缘 Column-level Lin...    │
│   列级血缘 Column-level Lin... → OpenLineage标准适配 OpenL...    │
│   OpenLineage标准适配 OpenL... → 数据质量五维度定义 ISO 80...    │
│   数据质量五维度定义 ISO 80... → 盘前质量检查 Pre-market Q...    │
│   盘前质量检查 Pre-market Q... → 数据质量记分卡 Data Quali...    │
│   数据质量记分卡 Data Quali... → AI驱动数据质量监控 AI-dri...    │
│   血缘成熟度模型 Lineage Ma... → 数据域规则目录 Data Domai...    │
│   AI驱动数据质量监控 AI-dri... → Market Regime Reference D...    │
│   Market Regime Reference D... → C-022 数据质量自管理 Data...    │
│   C-022 数据质量自管理 Data... → Metadata Registry MDM 元...     │
│   Metadata Registry MDM 元... → Security Master Manager ...      │
│   Security Master Manager ... → Data Lineage 数据血缘            │
│   Data Lineage 数据血缘 → Data Quality SLA 数据质量SLA           │
│   Data Quality SLA 数据质量SLA → 数据域规则目录 Data Domai...    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     [runtime] (8 条 / edges)                     │
├──────────────────────────────────────────────────────────────────┤
│   数据血缘 Data Lineage → 分阶段实现MVP→V2→V3→V4...              │
│   质量检查自建而非Great Exp... → Data Quality SLA 数据质量SLA    │
│   列级血缘 Column-level Lin... → MVP用SQLite存储血缘 SQLit...    │
│   OpenLineage标准适配 OpenL... → 列级血缘而非表级 Column-l...    │
│   CTR-TRACE-001血缘ID贯穿全... → Data Lineage 数据血缘           │
│   质量检查按交易时段分三阶... → Metadata Registry MDM 元...      │
│   质量检查自建而非Great Exp... → Data Lineage 数据血缘           │
│   AI驱动数据质量监控 AI-dri... → Quality Gate Four-Level ...     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      [event] (2 条 / edges)                      │
├──────────────────────────────────────────────────────────────────┤
│   数据源质量评分 Data Sourc... → DataQualityDegraded 数据...     │
│   Metadata Registry MDM 元... → DataQualityDegraded 数据...      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    [contract] (2 条 / edges)                     │
├──────────────────────────────────────────────────────────────────┤
│   血缘追踪链 Lineage Tracki... → AI驱动数据质量监控 AI-dri...    │
│   C-022 数据质量自管理 Data... → DataQualityError 数据质量...    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (2 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   Quality Gate 质量门禁 → Data Quality SLA 数据质量SLA           │
│   Security Master Manager ... → Data Quality Gate 数据质...      │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `06_d_data_gov_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
