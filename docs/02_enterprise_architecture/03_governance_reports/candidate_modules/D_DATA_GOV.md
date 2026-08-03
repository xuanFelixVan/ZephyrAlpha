---
doc_type: audit_report
title: 候选模块清单 — D_DATA_GOV
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_DATA_GOV 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **19** 条（原有 0 + harvest 19）。
> harvest 去重四态: likely_new=3 / likely_implemented=16

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0206 | Data Catalog 数据目录 | / D-DATA-17 / Data Catalog / ✅ / / 元数据索引+搜索引擎+标签分类 / | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0468 | 数据质量 Data Quality | ║  │ 数据质量 (§10)                                                           │  ║ | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0471 | 数据血缘 Data Lineage | 列级血缘+OpenLineage标准+成熟度四阶段 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0473 | AI治理血缘 AI Governance Lineage | ║  │  Lineage) + 🆕AI驱动异常检测(Isolation Forest+自适应阈值)                │  ║ | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0509 | 数据源质量评分 Data Source Quality Scoring | 完整性/准确性/一致性/及时性/可用性五维度评分 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0526 | 血缘链全景 Lineage Chain Panorama | 数据源→L0→L1→L2→L3→L4→L5全链路血缘 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0527 | 列级血缘 Column-level Lineage | L0→L6全链路列级血缘 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0530 | OpenLineage标准适配 OpenLineage Adaptation | Run/Job/Dataset/Facet概念适配 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0531 | 数据质量五维度定义 ISO 8000 Five Dimensions | 完整性/准确性/一致性/及时性/可用性 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0548 | 盘前质量检查 Pre-market Quality Check | │  执行器: D-DATA-10 DataQualityScorer + D-DATA-23 DataObservability  │ | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0554 | 数据质量记分卡 Data Quality Scorecard | 按数据源/品类/质量维度评分+综合评分+趋势分析 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0584 | AI驱动数据质量监控 AI-driven Data Quality | / 30 / **Data Mesh架构**：Zhamak Dehghani提出的分布式数据架构范式——领域驱动数据所有权+数据即产品+自服务基础设施+联邦治理。AWS 2025年发布Data Mesh实践指南，强调跨目录元数据联邦+跨账户 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0594 | Market Regime Reference Data 市场状态分类参考数据 | / D-DATA-113 / Market Regime Reference Data / 市场状态分类参考数据(C-021 3×3×3立方体阈值+量能体制分层+日历约束修饰器) / ✅能建。与§0.1 L2-C市场状态和'量能=第3维度' | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0657 | C-022 数据质量自管理 Data Quality Self-management | 自动检测字段覆盖度AkShare备选 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1316 | Metadata Registry MDM 元数据注册中心MDM | 1500模块元数据注册+Security Master+THS指标定义+元数据版本 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1319 | Security Master Manager 证券主数据管理器 | 证券主数据/证券标识映射/证券生命周期+主数据版本管理 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2863 | Data Lineage 数据血缘 | / 数据血缘（因子→信号→策略→决策→执行→复盘+OpenLineage标准） / 风险数据流（→A4） / | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2864 | Data Quality SLA 数据质量SLA | / 数据质量SLA（ISO 8000五维度+P0/P1/P2三级+自动化检查流水线+违约处理+记分卡） / 合规数据报送（→A6🔒） / | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2977 | 数据域规则目录 Data Domain Rule Catalog | 数据质量血缘访问保留 | D_DATA_GOV | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（19 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0206 | Data Catalog 数据目录 | / D-DATA-17 / Data Catalog / ✅ / / 元数据索引+搜索引擎+标签分类 / | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0468 | 数据质量 Data Quality | ║  │ 数据质量 (§10)                                                           │  ║ | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0471 | 数据血缘 Data Lineage | 列级血缘+OpenLineage标准+成熟度四阶段 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0473 | AI治理血缘 AI Governance Lineage | ║  │  Lineage) + 🆕AI驱动异常检测(Isolation Forest+自适应阈值)                │  ║ | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0509 | 数据源质量评分 Data Source Quality Scoring | 完整性/准确性/一致性/及时性/可用性五维度评分 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0526 | 血缘链全景 Lineage Chain Panorama | 数据源→L0→L1→L2→L3→L4→L5全链路血缘 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0527 | 列级血缘 Column-level Lineage | L0→L6全链路列级血缘 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0530 | OpenLineage标准适配 OpenLineage Adaptation | Run/Job/Dataset/Facet概念适配 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0531 | 数据质量五维度定义 ISO 8000 Five Dimensions | 完整性/准确性/一致性/及时性/可用性 | D_DATA_GOV | harvest待评估（likely_new） |  |
| CAND-HARVEST-0548 | 盘前质量检查 Pre-market Quality Check | │  执行器: D-DATA-10 DataQualityScorer + D-DATA-23 DataObservability  │ | D_DATA_GOV | harvest待评估（likely_new） |  |
| CAND-HARVEST-0554 | 数据质量记分卡 Data Quality Scorecard | 按数据源/品类/质量维度评分+综合评分+趋势分析 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0584 | AI驱动数据质量监控 AI-driven Data Quality | / 30 / **Data Mesh架构**：Zhamak Dehghani提出的分布式数据架构范式——领域驱动数据所有权+数据即产品+自服务基础设施+联邦治理。AWS 2025年发布Data Mesh实践指南，强调跨目录元数据联邦+跨账户 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0594 | Market Regime Reference Data 市场状态分类参考数据 | / D-DATA-113 / Market Regime Reference Data / 市场状态分类参考数据(C-021 3×3×3立方体阈值+量能体制分层+日历约束修饰器) / ✅能建。与§0.1 L2-C市场状态和'量能=第3维度' | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0657 | C-022 数据质量自管理 Data Quality Self-management | 自动检测字段覆盖度AkShare备选 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1316 | Metadata Registry MDM 元数据注册中心MDM | 1500模块元数据注册+Security Master+THS指标定义+元数据版本 | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1319 | Security Master Manager 证券主数据管理器 | 证券主数据/证券标识映射/证券生命周期+主数据版本管理 | D_DATA_GOV | harvest待评估（likely_new） |  |
| CAND-HARVEST-2863 | Data Lineage 数据血缘 | / 数据血缘（因子→信号→策略→决策→执行→复盘+OpenLineage标准） / 风险数据流（→A4） / | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2864 | Data Quality SLA 数据质量SLA | / 数据质量SLA（ISO 8000五维度+P0/P1/P2三级+自动化检查流水线+违约处理+记分卡） / 合规数据报送（→A6🔒） / | D_DATA_GOV | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2977 | 数据域规则目录 Data Domain Rule Catalog | 数据质量血缘访问保留 | D_DATA_GOV | harvest待评估（likely_implemented） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0206 | Data Catalog 数据目录 | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0468 | 数据质量 Data Quality | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0471 | 数据血缘 Data Lineage | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0473 | AI治理血缘 AI Governance Lineage | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0509 | 数据源质量评分 Data Source Quality Scoring | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0526 | 血缘链全景 Lineage Chain Panorama | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0527 | 列级血缘 Column-level Lineage | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0530 | OpenLineage标准适配 OpenLineage Adaptation | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0531 | 数据质量五维度定义 ISO 8000 Five Dimensions | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0548 | 盘前质量检查 Pre-market Quality Check | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0554 | 数据质量记分卡 Data Quality Scorecard | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0584 | AI驱动数据质量监控 AI-driven Data Quality | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0594 | Market Regime Reference Data 市场状态分类参考数据 | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0657 | C-022 数据质量自管理 Data Quality Self-management | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1316 | Metadata Registry MDM 元数据注册中心MDM | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1319 | Security Master Manager 证券主数据管理器 | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2863 | Data Lineage 数据血缘 | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2864 | Data Quality SLA 数据质量SLA | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2977 | 数据域规则目录 Data Domain Rule Catalog | D_DATA_GOV | 候选待评（candidate） | harvest待评估（likely_implemented） |
