---
module_id: ARCH-SMP-001
title: "架构文档库总览样板"
doc_type: architecture_view
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 架构文档库总览样板

> 这是你查看 ZephyrAlpha 架构的入口。从这里出发，你能找到所有架构相关的文档和图。
>
> **核心原则**：这个文档库是给人看的，不是给机器看的。机器看全景图数据库（depgraph.db），人看这里。所以一切都是以人怎么方便、怎么看得直白为准。

---

## 文档库结构

| 文件夹 | 是什么 | 谁维护 | 什么时候变 |
|--------|--------|--------|-----------|
| `00_overview_entry/` | 你现在看的这个文件，整个文档库的导航地图 | 自动生成 | 全景图更新时 |
| `01_global_architecture_diagram/` | 全局视图（路径树、跨域矩阵、集成拓扑图） | 自动生成 | 全景图更新时 |
| `02_domain_architecture_docs/` | 每个功能域的详细文档和依赖图 | 自动生成 | 全景图更新时 |
| `03_governance_reports/` | 容量报告、约束违规报告、设计态vs运营态报告 | 自动生成 | 全景图更新时 |
| `04_architecture_principles_decisions/` | 架构原则、安全红线、技术选型决策 | 人工维护 | 架构决策变更时 |
| `05_manual_architecture_views/` | 业务架构、信息架构等叙事性视图 | 人工维护 | 业务变化时 |
| `06_manual_architecture_diagrams/` | TOGAF四层图、C4图等手工维护的图 | 人工维护 | 架构变化时 |
| `_archive/` | 历史文档归档 | 不维护 | 不变 |

---

## 怎么看（按场景导航）

### 想快速了解系统

1. 看本文件了解文档库结构
2. 看 `01_global_architecture_diagram/full_project_tree_zh.md` 了解项目物理结构（文件怎么组织的）
3. 看 `01_global_architecture_diagram/integration_topology.md` 了解43个域之间怎么互相依赖
4. 看 `01_global_architecture_diagram/cross_domain_matrix.md` 了解域间依赖的详细数据

### 想了解某个功能域

1. 去 `02_domain_architecture_docs/` 找到对应域的文档（如 `53_d_trading.md`）
2. 看域文档了解这个域有哪些模块、每个模块干什么
3. 看域文档内嵌的 Mermaid 依赖图了解这个域内部怎么依赖、跟其他域怎么依赖
4. 看 `02_domain_architecture_docs/domain_index.md` 了解所有域的清单

### 想做架构决策

1. 看 `04_architecture_principles_decisions/架构原则.md` 了解安全红线和核心原则
2. 看 `04_architecture_principles_decisions/技术选型.md` 了解已选定的技术栈
3. 看 `04_architecture_principles_decisions/决策记录.md` 了解历史架构决策

### 想看系统健康度

1. 看 `03_governance_reports/capacity_report.md` 了解各域模块数（有没有超标）
2. 看 `03_governance_reports/constraint_violations.md` 了解有哪些违规
3. 看 `03_governance_reports/design_vs_production.md` 了解设计态到运营态的迁移进度

### 想看业务架构

1. 看 `05_manual_architecture_views/业务架构.md` 了解业务能力和流程
2. 看 `05_manual_architecture_views/信息架构.md` 了解文档和数据组织
3. 看 `06_manual_architecture_diagrams/TOGAF四层架构图.mmd` 了解四层架构全貌

---

## 数据从哪来

**自动生成的文档**（1/2/3 文件夹）：
- 数据源：`data/databases/depgraph.db`（全景图数据库）
- 全景图是唯一真源
- 架构图是全景图的派生物
- 禁止手工修改自动生成的文档
- 生成器位于：`scripts/governance/d5_architecture/generators/`

**人工维护的文档**（4/5/6 文件夹）：
- 架构原则、决策记录、业务视图等叙事性内容
- 由架构师/Owner维护
- 变更需通过架构评审

---

## 功能域速览

> 完整列表见 `02_domain_architecture_docs/domain_index.md`

| 层级 | 域数量 | 代表域 |
|------|:---:|--------|
| 基础设施层 | 2 | D_INFRA_OPS（基础设施运维）、D_INFRA_RUNTIME（运行时集成） |
| 基础层 | 6 | D-ALT_DATA（另类数据）、D-DATA_ENG（数据工程） 等 |
| 平台层 | 7 | D-AUTONOMY_CORE（自治核心）、D-FRONTEND（前端） 等 |
| 业务域层 | 28 | D-TRADING（交易运营）、D-BACKTEST（回测）、D-RISK（风险） 等 |
| 未分层 | 9 | 待分类的域 |

---

## 说明

- **这是样板文件**：实际文件由 `generate_navigation_index.py` 自动生成
- **维护方式**：自动生成
- **格式要求**：中文为主，大白话+表格+导航路径
