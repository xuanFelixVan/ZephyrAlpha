---
module_id: DOCUMENT_REPOSITORY_LAYOUT_STANDARD_001
version: 1.0.0
status: Active
created_date: 2026-04-08
last_updated: '2026-04-08'
owner: 仓库 Owner
standard_type: 专业量化机构文档体系标准
applicable_scope: 全仓库 Markdown 与实施类文档的目录放置（含蓝图阶段与施工文档阶段）
compliance_level: 与 CONSTRUCTION_GATE、ARCHITECTURE 权威栈一致
parent_document: ./INDEX.md
responsibility:
  - 规定 docs 一级/关键二级目录的职责边界
  - 规定第 2 阶段（施工流程/计划/方案）默认落盘位置与命名建议
related_documents:
  - ../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md
  - ../../05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md
  - ./FILE_NAMING_STANDARD.md
---

# 文档仓库目录与阶段放置标准

> **核心职责**：回答「这类文档应该放在仓库哪个文件夹」，使个人开发 + AI 维护时**少漂移、少重复、可追溯**。  
> **职责边界**：本文规定 **docs/** 下及与文档强相关的实施目录习惯；**不**替代 `src/` 内代码结构规范（代码结构以实施蓝图与 `PATH_STANDARD` 中代码部分为准）。

---

## 1. 原则（对齐专业机构习惯、适配个人规模）

1. **一类内容一个家**：架构、因子、战术契约、实施、审计、归档**分树**；不确定时先查下表再新建目录。  
2. **真源唯一**：同一主题**一篇 canonical** 入口，复制件只进 `archive` 并写「参见 xxx」。  
3. **阶段可读**：第 1 阶段（蓝图）产出主要在 **`01_FRAMEWORK`** 与 **`01_BLUEPRINTS`**；第 2 阶段（施工文档）产出在 **`03_CONSTRUCTION_PLANS`**（见 §4）；第 3 阶段代码在 **`src/`**、测试在 **`tests/`**。  
4. **扩展规则**：未来新类型文档若下表无格，须在本文件 **§6 变更记录** 增一行再创建目录（或在 `TECH_DECISION_RECORDS` 登记后次日同步本文）。

---

## 2. `docs/` 一级目录职责（简表）

| 路径 | 放什么 | 典型文件名 |
|------|--------|------------|
| `docs/00_OVERVIEW/`、`00_RESOURCES/` | 总览、资源索引 | 少量 INDEX、概述 |
| `docs/01_FRAMEWORK/` | **总架构、框架级蓝图、跨层原则** | `ARCHITECTURE.md`、`*BLUEPRINT*.md` |
| `docs/02_FACTOR_LIBRARY/` | 因子库治理、数据源、手册 | `INDEX.md`、各子域 README |
| `docs/03_TRADING_TACTICS/` | **战术、策略规格、API 契约** | `API_Contract.md`、`Strategy_*.md` |
| `docs/04_EXECUTION/` | 执行与运行相关叙述（与战术区分以边界文档为准） | 视项目 |
| `docs/05_IMPLEMENTATION/` | **实施侧：蓝图落地、规格、运维、审计台账、施工文档** | 见 §3 |
| `docs/06_ARCHIVE/` | **只读历史、迁出真源后的副本** | 日期或主题子目录 |
| `docs/07_RESEARCH/`、`09_RESEARCH_INNOVATION/` | 研究笔记与创新（非实施真源） | 实验记录类 |
| `docs/08_HUMAN_AI_INTERFACE/`、`10_*`、`11_*` | 人机、工作流、治理、战略卷宗 | 与 `01_FRAMEWORK` 冲突时以框架为准 |
| `docs/09_AUDIT/` | **审计程序、标准、状态、报告** | `PROCEDURES/`、`STANDARDS/`、`STATE/`、`REPORTS/` |
| `docs/09_ARCHIVE/` | 历史 duplicate 等 | 与 `06_ARCHIVE` 关系见治理 Backlog |

---

## 3. `docs/05_IMPLEMENTATION/` 关键子目录

| 路径 | 放什么 |
|------|--------|
| `06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` | **实施侧蓝图**（与框架蓝图互补；第 1 阶段终稿主战场之一） |
| `06_CONSTRUCTION_DOCS/02_IMPLEMENTATION_GUIDES/` | 实施指南、操作说明 |
| `06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/` | 设计说明、评审清单等 |
| `05_TECHNICAL_SPECIFICATIONS/` | **技术规格**（偏接口与实现约束，非高层蓝图） |
| `04_OPERATIONS/audit_state/` | **运行态审计与整改报告**（权威工作目录，见 ADR-OC-002） |
| `07_OPERATIONS/` | 运维手册、知识库、检查表 |
| `02_DEVELOPMENT/` | 开发规范（含 [`PATH_STANDARD.md`](../../05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md)） |
| `99_ARCHIVE/` | 实施域内归档 |

---

## 4. 第 2 阶段（施工流程 / 计划 / 方案）默认放置

**目录（若不存在，第 2 阶段启动时创建并补 `INDEX.md`）**：

`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/03_CONSTRUCTION_PLANS/`

**建议文件（可合并，但必须有一篇总索引）**：

| 建议文件名 | 内容 |
|------------|------|
| `INDEX.md` | 本目录索引、版本、与 `CONSTRUCTION_GATE` §0.3 对应关系 |
| `CONSTRUCTION_WORKFLOW_YYYYMMDD.md` | 施工流程（从蓝图到编码、测试、合并） |
| `CONSTRUCTION_SCHEDULE_YYYYMMDD.md` | 施工计划（里程碑、依赖、Owner+AI 轮次） |
| `CONSTRUCTION_METHOD_STATEMENT_YYYYMMDD.md` | 施工方案（选型锁定、目录约定、密钥原则、验收顺序） |

命名遵守 [`FILE_NAMING_STANDARD.md`](./FILE_NAMING_STANDARD.md)；日期 `YYYYMMDD` 与 Owner 习惯一致即可。

**索引入口**：总实施导航仍可通过 [`docs/05_IMPLEMENTATION/SITEMAP.md`](../../05_IMPLEMENTATION/SITEMAP.md) 或本目录 `INDEX.md` 互链。

---

## 5. 蓝图阶段须与本标准对齐的完成项（供 CONSTRUCTION_GATE 引用）

在进入 **第 2 阶段**前，除蓝图终稿外，建议确认：

- [ ] 本文 **§2～§4** 已被 Owner 或代理人阅读，**无未解决的目录冲突**（若有，在 §6 或 `TECH_DECISION_RECORDS` 登记）。  
- [ ] **`03_CONSTRUCTION_PLANS/`** 若尚不存在，已在第 2 阶段开工当日创建并写 `INDEX.md`。  
- [ ] 新写文档**优先**落入上表对应目录；确需新目录时，已更新 **§6**。

---

## 6. 变更记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-08 | 初版：一级目录职责、05 实施子目录、第 2 阶段默认路径 |
