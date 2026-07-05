---
module_id: VIEW-02-INFORMATION-ARCH
title: Target Architecture — Information Architecture / 目标架构：信息架构
doc_type: architecture_view
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-17
superseded_by: null
supersedes: null
related_rationale: R26, R27, R28, R29, R30, R44
related_open_questions: []
tags:
- information-architecture
- togaf
- ia
- docs-structure
- document-lifecycle
- drawer-taxonomy
summary: TOGAF Information Architecture 视图。v2.0.0：全面重写对齐实际6目录结构——§2抽屉体系从虚构的20目录重写为实际的6顶级目录（_archive/_working/01_policies_and_standards/02_enterprise_architecture/03_modules/08_knowledge），§3分类依据/§4关系图/§9成熟度表全部重写，§6记忆系统路径修正，§10修订记录删除（git log是真源）。回答：docs/有哪些信息资产抽屉、分类依据、抽屉间关系、文档生命周期、元数据标准。
date: '2026-07-04'
ttl: permanent
---

## 1. Purpose of this view / 本视图的用途

The Information Architecture answers:

信息架构视图回答：

- What information assets exist in `docs/`? (Drawer taxonomy / 抽屉分类体系)
- How are they classified and why? (Classification rationale / 分类依据)
- How do they relate to each other? (Drawer relationships / 抽屉关系)
- How do documents flow through their lifecycle? (Document lifecycle / 文档生命周期)
- What metadata standard governs all documents? (Metadata standard / 元数据标准)

This view is **driven by** the Business Architecture (what capabilities determine what to document) and **drives** the Application Architecture (data distribution determines application boundaries).

本视图由业务架构**驱动**（能力决定记录什么），并**驱动**应用架构（数据分布决定应用边界）。

> **v2.0.0 变更**：原 §2 描述的 20 个顶级目录（00_governance / 03_domain_architecture / 06_security_and_identity / 07_sre_and_platform_ops / 09~14 业务域 / 16~18 合规风险审计 / 19_development_workspace / 99_archive）已全部不存在——docs/ 经多次重构后简化为 6 个顶级目录。原 §2/§3/§4/§9 基于虚构目录体系，是污染源，已全部重写对齐实际结构。原 §10 修订记录已删除（git log 是真源）。

---

## 2. `docs/` complete drawer taxonomy / `docs/` 完整抽屉体系

> 真源：[`directory_registry.yaml`](../../01_policies_and_standards/_registry/catalogs/directory_registry.yaml)（项目目录登记表 SSoT）。本节为人类可读视图，结构变更必须先改 SSoT。
>
> Classification rationale by layer: see §3. Maturity status per drawer: see §9.

当前 `docs/` 只有 **6 个顶级目录**（从原 20 个大幅精简）：

### 2.1 `01_policies_and_standards/` — 政策与标准

定义合格产物标准。包含：

- `rules/` — 60 条 TRAE 规则（`trae_001`~`trae_060`，YAML 真源）
- `policies/` — 政策文档（如 `parallel_session_coordination_policy.md`）
- `templates/` — 文档模板（blueprint / playbook / runbook / policy / register / standard 等）
- `_registry/` — 注册表与真源登记
  - `catalogs/` — 25 个注册表（`registry_master_index.yaml` 是总索引）
  - `contracts/` — 契约（`architecture_contract.yaml` / `directory_contract.yaml` / `model_capability_contract.yaml`）
  - `schemas/` — Schema（`frontmatter_schema.json` / `session_log_schema.yaml`）
  - `vocabularies/` — 33 个受控词表（`doc_type_vocabulary.yaml` / `status_vocabulary.yaml` 等）

### 2.2 `02_enterprise_architecture/` — 企业架构

全系统总体架构真源。包含 8 个子目录：

- `00_overview_entry/` — 全局入口索引（`index.md` + `navigation_index.md`）
- `01_global_architecture_diagram/` — 全局架构图（`cross_domain_matrix.md` / `global_capability_heatmap.md` / `integration_topology.md` / `full_project_tree_*.md`）
- `02_domain_architecture_docs/` — 53 域架构文档（`01_d_infra_a2a.md`~`49_d_trading.md` + `domain_index.md`）
- `03_governance_reports/` — 治理报告（`capacity_report.md` / `constraint_violations.md` / `design_vs_production.md`）
- `04_architecture_principles_decisions/` — 架构原则与决策（`architecture_principles.md` SSoT / `dimension_audit_matrix.md` / `dependency_path_panorama.md`）
- `generated/` — 自动派生视图（`domains/index.md` + 53 个 `*_dependency.mmd`，由 `scripts/governance/d5_architecture/generators/` 生成）
- `sample/` — 样板文件
- `target_architecture/` — TOGAF 四层视图（本文档组，见 [index.md](./index.md)）

### 2.3 `03_modules/` — 53 域模块蓝图

53 域平级结构（不再按 L00-L13 分层），每域一个 `_domain_*/` 目录：

- `_cross_layer/` — 跨层模块（`_b_track_interfaces/` / `agent_orchestrator/` / `context_engine/` / `database/` / `gate_engine/` / `shared_core/` 等 20+ 子模块）
- `_domain_autonomy_core/` / `_domain_autonomy_perm/` / `_domain_backtest/` / `_domain_compliance/` / `_domain_data/` / `_domain_execution_core/` / `_domain_factor/` / `_domain_frontend/` / `_domain_governance/` / `_domain_infrastructure_operations/` / `_domain_infrastructure_runtime/` / `_domain_integration/` / `_domain_knowledge/` / `_domain_machine_learning_train/` / `_domain_portfolio_core/` / `_domain_reporting/` / `_domain_research/` / `_domain_risk/` / `_domain_signal/` / `_domain_simulation/`
- `_master_blueprint/` — 主蓝图
- `_system_master/` — 系统主蓝图
- `specifications/` — 规格说明

> **53 域真源**：[`generated/domains/index.md`](../generated/domains/index.md)（由 depgraph `domains` 表派生）。域清单、节点数以派生视图为准。

### 2.4 `08_knowledge/` — 知识库

长期知识资产。包含：

- `01_raw_intake/` — 采集原始条目
- `02_triaged/` — 已分拣条目
- `data/` — 知识库数据

### 2.5 `_working/` — 过程区（task_bound）

过程产物，TTL=task_bound（任务完成即清理）。包含：

- `decomposition/` — 任务分解
- `module_migration/` — 模块迁移
- `p2_review_reports/` — P2 评审报告
- `research_notes/` — 研究笔记
- `ttl_content_audit/` — TTL 内容审计
- `03_governance_reports/` — 治理报告（过程态）

> **注**：`_working/` 是原 `19_development_workspace/`（2026-06-26 退役）的替代，过程区统一迁移至此。

### 2.6 `_archive/` — 归档区

非活跃但需保留的资产。包含：

- `03_modules/` — 已归档的模块文档

---

## 3. Drawer classification rationale / 抽屉分类依据

6 个顶级目录按**四种性质**分类：

| 类别 | 目录 | 性质 |
|------|------|------|
| **治理与标准层** | `01_policies_and_standards/` | 定义合格产物标准、规则、注册表、词表（跨业务域，管所有东西） |
| **架构层（中枢）** | `02_enterprise_architecture/` | 企业架构设计、53 域架构文档、治理报告、架构原则、派生视图、TOGAF 视图 |
| **模块蓝图层** | `03_modules/` | 53 域模块蓝图（`_domain_*/` 平级 + `_cross_layer/` 跨层模块） |
| **知识层** | `08_knowledge/` | 长期知识资产、AI 驱动采集流水线、可复用认知 |
| **过程区** | `_working/` | 讨论中、未定稿、任务卡、session log（TTL=task_bound） |
| **历史区** | `_archive/` | 归档、退役资产 |

> **为什么从 20 目录精简到 6 目录？** 原 20 目录体系（00~99 编号抽屉）基于"业务域垂直分"的假设，但实际项目演进中：
> - 安全/SRE/合规/风险/审计等能力域已并入 `02_enterprise_architecture/02_domain_architecture_docs/` 的 53 域文档（D_SECURITY / D_OPS / D_COMPLIANCE / D_RISK / D_AUDITTEST 等）
> - 数据/研究/模型/策略/执行/报告等业务域已并入 `03_modules/_domain_*/` 53 域蓝图
> - 19_development_workspace 已退役，过程区统一到 `_working/`
> - 99_archive 改为 `_archive/`（下划线前缀，与 `_working/` 同为"非编号过程区"约定）
>
> **原则**：同一职责不在两处定义。业务域文档归 `02_enterprise_architecture/02_domain_architecture_docs/`，业务域蓝图归 `03_modules/_domain_*/`，避免双真源。

---

## 4. Drawer relationship diagram / 抽屉关系图

```
         ┌────────── 治理与标准层 ──────────┐
         │ 01_policies_and_standards       │
         │ (rules / policies / registry)   │
         └───────────┬─────────────────────┘
                     │ 规则 / 标准 / 词表约束
                     ↓
         ┌────────── 架构层（中枢）─────────┐
         │ 02_enterprise_architecture      │
         │  (53域文档 / 治理报告 / TOGAF视图)│
         └───────────┬─────────────────────┘
                     │ 蓝图 / 施工指引
                     ↓
         ┌────────── 模块蓝图层 ────────────┐
         │ 03_modules                      │
         │  (_domain_* 53域 + _cross_layer)│
         └───────────┬─────────────────────┘
                     │ 沉淀 / 反馈
                     ↓
         ┌────────── 知识层 ────────────────┐
         │ 08_knowledge                    │
         └─────────────────────────────────┘
                     ↑ 过程产物               ↓ 失效归档
              _working/                  _archive/
              (task_bound)               (retired)
```

> **📊 文档拓扑图**：见 [`diagrams/docs_drawer_topology.mmd`](diagrams/docs_drawer_topology.mmd) — docs/ 抽屉分类拓扑（v2.0.0 已同步对齐 6 目录结构）

---

## 5. Document lifecycle / 文档生命周期

```
┌────────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│ _working/          │ ──→ │ _working/         │ ──→ │ 02_enterprise    │
│ research_notes/    │Stabilize│ decomposition/│Promote│ /03_modules       │
│ decomposition/     │     │                   │     │ etc.（canonical）│
└────────────────────┘     └───────────────────┘     └─────────┬────────┘
                                                               │
                                                               │ Superseded / 失效替代
                                                               ↓
                                                     ┌──────────────────┐
                                                     │ _archive/        │
                                                     │ (retired assets) │
                                                     └──────────────────┘
```

Status machine / 状态机：`draft → in_discussion → review_ready → active/accepted → superseded/deprecated`

> **注**：过程区从原 `19_development_workspace/`（已退役）统一迁移至 `_working/`（TTL=task_bound）。任务完成或文档升格后，`_working/` 下过程产物应清理。

---

## 6. Organizational memory system position / 组织记忆系统在全貌中的位置

The organizational memory system belongs to `03_modules/_cross_layer/_b_track_interfaces/memory-and-context/`.

组织记忆系统属于 `03_modules/_cross_layer/_b_track_interfaces/memory-and-context/`。

> **v2.0.0 修正**：原路径 `03_modules/_b_track_interfaces/` 错误，实际在 `_cross_layer/_b_track_interfaces/`（跨层模块下）。

当前状态：重新讨论中（OQ-001、OQ-002、OQ-010 已重新打开）。三个前提问题待定：

1. Where should memory system governance policies live? / 记忆系统的治理政策应该放在哪里？
2. Where should memory system execution code live? / 记忆系统的执行代码应该放在哪里？
3. Where should memory system indexes live? / 记忆系统的索引应该放在哪里？

---

## 7. Current workspace key navigation / 当前工作区关键入口

| File / 文件 | Purpose / 用途 |
|------------|--------------|
| `docs/_working/` | 过程区入口（task_bound）：承接工作草稿、任务卡、session log 等过程产物 |
| `docs/01_policies_and_standards/_registry/vocabularies/terminology_mapping.yaml` | 术语映射表（正式位置） |
| `docs/02_enterprise_architecture/02_domain_architecture_docs/domain_index.md` | 53 域架构文档索引 |
| `docs/02_enterprise_architecture/generated/domains/index.md` | 53 域派生视图索引（depgraph 派生） |
| `docs/03_modules/_master_blueprint/blueprint.md` | 53 域主蓝图入口 |

---

## 8. Metadata standard / 元数据标准

All documents under `docs/` must comply with frontmatter schema v2.0.0:

所有 `docs/` 下文档必须遵守 frontmatter schema v2.0.0：

- **Single frontmatter schema** — 真源：[`frontmatter_schema.json`](../../01_policies_and_standards/_registry/schemas/frontmatter_schema.json)
- **Phased required fields** — status 决定哪些字段必填
- **Controlled `doc_type` vocabulary** — 真源：[`doc_type_vocabulary.yaml`](../../01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml)（9 个合法值）
- **Unified `module_id` naming** — `<DOMAIN>-[<SUBDOMAIN>-]<TYPE>-<NNN>`
- **Append-only supersedes rule** — 已接受决策只能被 supersede，不可删改（禁用删除线）

> **TTL 治理**：`ttl` 字段受控于 [`ttl_vocabulary.yaml`](../../01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml)。`task_bound` 类型文档任务完成即清理，由 TTL-METADATA gate 在 commit 时强制校验。

---

## 9. Drawer maturity status / 目录成熟度状态

| Directory / 目录 | Status / 状态 | Notes / 说明 |
|----------------|--------------|-------------|
| `01_policies_and_standards` | **active** | 60 条 TRAE 规则 + 25 个注册表 + 33 个词表已激活 |
| `02_enterprise_architecture` | **active** | 8 个子目录全部激活（00~04 + generated + sample + target_architecture） |
| `03_modules` | **partial** | 53 域 `_domain_*/` 目录骨架已建，蓝图逐步填充中；`_cross_layer/` 已激活 |
| `08_knowledge` | **partial** | `01_raw_intake/` + `02_triaged/` 已建，KMS 流水线待激活 |
| `_working` | **active** | 过程区，task_bound（任务完成即清理） |
| `_archive` | **partial** | 已归档 `03_modules/` 等资产 |

**Status semantics / 状态语义**:

- **`active`** — 正在频繁写入与维护
- **`partial`** — 目录存在，部分子目录已激活
- **`planned`** — 在 IA 里已预留，等业务里程碑触发后激活
- **`deferred`** — 确定现阶段不需要，未来触发条件满足后再评估

---

## 10. Architecture Runway / 架构预留通道

> 以下预留通道为未来 P3 能力激活后的挂载点。本节不实现任何具体逻辑，仅记录"将来何处扩展、何条件触发"。

| ID | 能力描述 | 挂载点 | 激活触发条件 |
|---|---|---|---|
| RW-IA-01 | 多模态因子信息对象 — 将文本/图像/数字融合因子纳入知识体系，扩展 §2 抽屉定义与文档生命周期规则 | `08_knowledge/` 子目录扩展 + §5 文档生命周期新增多模态类型 | NLP 因子生产验证充分 + 图像/另类数据供应商接入完成 |
| RW-IA-02 | ESG 因子信息对象 — 在 `03_modules/_domain_factor/` 下建立 ESG 因子专属蓝图，定义数据质量与血缘标准 | `03_modules/_domain_factor/` 子目录扩展 | ESG 数据供应商接入评估完成 |
| RW-IA-03 | 知识图谱自动构建 — 在 `08_knowledge/` 建立知识图谱子层，定义实体/关系信息架构与 §6 跨抽屉引用规则扩展 | `08_knowledge/` 新增子目录 + §8 元数据标准扩展 | KMS 条目 > 500 条 + 知识图谱基础设施完成 |

---

## 11. 与其他视图的边界

- **本视图**只定义 `docs/` 信息资产抽屉体系与元数据标准
- **业务能力地图**（哪些能力需要哪些文档）见 [business_architecture.md §3](./business_architecture.md)
- **应用模块边界**（代码模块如何划分）见 [application_architecture.md](./application_architecture.md)
- **架构原则**（R1-R4 安全红线 + 准入铁律）见 [../04_architecture_principles_decisions/architecture_principles.md](../04_architecture_principles_decisions/architecture_principles.md)
