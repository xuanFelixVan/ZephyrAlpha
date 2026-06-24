# 架构文档库总览

> 这是你查看 ZephyrAlpha 架构的入口。从这里出发，你能找到所有架构相关的文档和图。
>
> **核心原则**：这个文档库是给人看的，不是给机器看的。机器看全景图数据库（depgraph.db），人看这里。所以一切都是以人怎么方便、怎么看得直白为准。
>
> **自动生成**：本文件由 `generate_navigation_index.py` 自动生成，每次全景图更新后自动刷新。最后更新：2026-06-24 02:29:50

---

## 文档库结构

| 文件夹 | 是什么 | 谁维护 | 什么时候变 |
|--------|--------|--------|-----------|
| `00_overview_entry/` | 你现在看的这个文件，整个文档库的导航地图 | 自动生成 | 全景图更新时 |
| `01_global_architecture_diagram/` | 全局视图（路径树、跨域矩阵、集成拓扑图），共 11 个文件 | 自动生成 | 全景图更新时 |
| `02_domain_architecture_docs/` | 每个功能域的详细文档和依赖图，共 141 个文件 | 自动生成 | 全景图更新时 |
| `03_governance_reports/` | 容量报告、约束违规报告、设计态vs运营态报告，共 6 个文件 | 自动生成 | 全景图更新时 |

---

## 怎么看（按场景导航）

### 想快速了解系统

1. 看本文件了解文档库结构
2. 看 `01_global_architecture_diagram/path_tree_zh.md` 了解项目物理结构（文件怎么组织的）
3. 看 `01_global_architecture_diagram/integration_topology.md` 了解43个域之间怎么互相依赖
4. 看 `01_global_architecture_diagram/cross_domain_matrix.md` 了解域间依赖的详细数据

### 想了解某个功能域

1. 去 `02_domain_architecture_docs/` 找到对应域的文档（如 `53_d_trading.md`）
2. 看域文档了解这个域有哪些模块、每个模块干什么
3. 看域文档内嵌的 Mermaid 依赖图了解这个域内部怎么依赖、跟其他域怎么依赖
4. 看 `02_domain_architecture_docs/domain_index.md` 了解所有域的清单

### 想看系统健康度

1. 看 `03_governance_reports/capacity_report.md` 了解各域模块数（有没有超标）
2. 看 `03_governance_reports/constraint_violations.md` 了解有哪些违规
3. 看 `03_governance_reports/design_vs_production.md` 了解设计态到运营态的迁移进度

---

## 数据从哪来

**所有文档都是自动生成的**：
- 数据源：`data/databases/depgraph.db`（全景图数据库）
- 全景图是唯一真源
- 架构图是全景图的派生物
- 禁止手工修改自动生成的文档
- 生成器位于：`scripts/governance/d5_architecture/generators/`

---

## 功能域速览

> 完整列表见 `02_domain_architecture_docs/domain_index.md`

| 层级 | 域数量 | 代表域 |
|------|:---:|--------|
| 基础设施层 | 2 | D-INFRA_OPS（基础设施运维）、D-INFRA_RUNTIME（runtime_integration） |
| 基础层 | 6 | D-ALT_DATA（另类数据）、D-BEHAVIORAL_AUDIT（行为审计）、D-DATA_ENG（数据工程(增值+融合+知识)） 等 |
| 平台层 | 7 | D-AUTONOMY_CORE（自治核心）、D-FRONTEND（前端）、D-INTEGRATION（pipeline_routing） 等 |
| 业务域层 | 38 | D-AUTONOMY_PERM（自治保护）、D-BACKTEST（回测）、D-COMPLIANCE（合规） 等 |

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-06-24 02:29:50 | 自动生成 |