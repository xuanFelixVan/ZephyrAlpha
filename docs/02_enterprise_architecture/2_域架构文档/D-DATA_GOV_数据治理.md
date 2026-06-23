---
doc_type: domain_architecture_doc
title: D-DATA_GOV 数据治理(质量+血缘+参考)架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-DATA_GOV 数据治理(质量+血缘+参考)架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-DATA_GOV |
| 域名称 | 数据治理(质量+血缘+参考) |
| 架构层 | L1_foundation |
| 模块总数 | 38 |
| 设计态模块 | 38 |
| 原型态模块 | 0 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 数据治理域。负责数据质量管理、数据血缘追踪与参考数据管理，包括数据质量门禁、血缘图谱、主数据管理、数据字典。拆分自原D-DATA域。 |

## 模块清单

共 38 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-DATA-GOV/AI治理血缘 AI Governance Lineage |  | design_only | design | 0 | 0 |
| D-DATA-GOV/AI驱动数据质量监控 AI-driven Data Quality |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Apache Polaris目录 Apache Polaris Catalog |  | design_only | design | 0 | 0 |
| D-DATA-GOV/BlackRock AI数据质量三阶段 BlackRock AI Data Quality |  | design_only | design | 0 | 0 |
| D-DATA-GOV/C-022 数据质量自管理 Data Quality Self-management |  | design_only | design | 0 | 0 |
| D-DATA-GOV/CTR-TRACE-001血缘ID贯穿全链路 Lineage ID End-to-end |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Data Catalog 数据目录 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Data Lineage 数据血缘 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Data Quality Gate 数据质量门禁 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Data Quality SLA 数据质量SLA |  | design_only | design | 0 | 0 |
| D-DATA-GOV/DataQualityDegraded 数据质量降级 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/DataQualityDegraded 数据质量降级事件 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/DataQualityError 数据质量错误 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/MVP用SQLite存储血缘 SQLite for Lineage MVP |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Market Regime Reference Data 市场状态分类参考数据 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Metadata Registry MDM 元数据注册中心MDM |  | design_only | design | 0 | 0 |
| D-DATA-GOV/OpenLineage标准适配 OpenLineage Adaptation |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Quality Gate Four-Level 质量门禁四级贯穿 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Quality Gate 质量门禁 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Reference Data 参考数据 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/Security Master Manager 证券主数据管理器 |  | design_only | design | 0 | 0 |
| D-DATA-GOV/分阶段实现MVP→V2→V3→V4 Phased Lineage |  | design_only | design | 0 | 0 |
| D-DATA-GOV/列级血缘 Column-level Lineage |  | design_only | design | 0 | 0 |
| D-DATA-GOV/列级血缘而非表级 Column-level over Table-level |  | design_only | design | 0 | 0 |
| D-DATA-GOV/列级血缘自动化 Column-level Lineage Automation |  | design_only | design | 0 | 0 |
| D-DATA-GOV/数据域规则目录 Data Domain Rule Catalog |  | design_only | design | 0 | 0 |
| D-DATA-GOV/数据源质量评分 Data Source Quality Scoring |  | design_only | design | 0 | 0 |
| D-DATA-GOV/数据血缘 Data Lineage |  | design_only | design | 0 | 0 |
| D-DATA-GOV/数据质量 Data Quality |  | design_only | design | 0 | 0 |
| D-DATA-GOV/数据质量五维度定义 ISO 8000 Five Dimensions |  | design_only | design | 0 | 0 |
| D-DATA-GOV/数据质量记分卡 Data Quality Scorecard |  | design_only | design | 0 | 0 |
| D-DATA-GOV/盘前质量检查 Pre-market Quality Check |  | design_only | design | 0 | 0 |
| D-DATA-GOV/血缘成熟度模型 Lineage Maturity Model |  | design_only | design | 0 | 0 |
| D-DATA-GOV/血缘追踪链 Lineage Tracking Chain |  | design_only | design | 0 | 0 |
| D-DATA-GOV/血缘链全景 Lineage Chain Panorama |  | design_only | design | 0 | 0 |
| D-DATA-GOV/质量检查按交易时段分三阶段 Three-stage Quality Check |  | design_only | design | 0 | 0 |
| D-DATA-GOV/质量检查自建而非Great Expectations Self-built Quality Check |  | design_only | design | 0 | 0 |
| D-DATA-GOV/质量检查自建而非Great Expectations Self-built over GE |  | design_only | design | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-INTELLIGENCE | 7 | data,contract,event |
| D-RISK | 6 | data,contract,event |
| D-OPS | 6 | data,config_depends,contract |
| D-SIGNAL | 5 | contract,data |
| D-SECURITY | 5 | contract,data,config_depends |
| D-GOVERNANCE | 5 | config_depends,data,contract |
| D-AUTONOMY_CORE | 5 | config_depends,contract,data |
| D-INTEGRATION | 4 | event,data,contract |
| D-FACTOR | 4 | config_depends,contract,event |
| D-SHARED | 3 | event,contract,data |
| D-PF_CORE | 3 | contract,data,event |
| D-MKT_DATA | 3 | event,contract,config_depends |
| D-KNOWLEDGE | 3 | data,contract |
| D-INFRA_RUNTIME | 2 | event |
| D-INFRA_OPS | 2 | config_depends,event |
| D-DATA_ENG | 2 | contract,config_depends |
| D-TRADING | 1 | config_depends |
| D-SELL_DECISION | 1 | event |
| D-REPORTING | 1 | event |
| D-POSITION | 1 | event |
| D-ML_TRAIN | 1 | contract |
| D-ML_SERVE | 1 | contract |
| D-FRONTEND | 1 | data |
| D-EX_SOR | 1 | contract |
| D-AUTONOMY_PERM | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 13 | contract,config_depends,event,data |

## 域内依赖图

详见 [d_data_gov_dependency.mmd](d_data_gov_dependency.mmd)
