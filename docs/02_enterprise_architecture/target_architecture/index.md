---
classification: confidential
date: '2026-07-04'
doc_type: index
generated: '2026-06-26'
layer: cross_layer
merged_from: README.md + index.md
module_id: ARCH-006
status: Active
title: Target Architecture — Navigation Guide / 目标架构导航
version: 3.2.0
depends_on:
  - {target: EA-INDEX, at: "§子目录", why: "父级 EA 索引——target_architecture 为其子目录"}
tags:
- index
- navigation
- domain-driven
- depgraph-derived
summary: v3.2.0：修复过时声明（runtime_planes已v1.1.0+.mmd 14层清理已完成+死清单删除+断链修复）。v3.1.0：瘦身后保留导航职能，硬编码域索引移交 generated/ 真源，修订记录移交 git log。v3.0.0：基于§2.1裁定，导航改为53域索引+全景图派生视图说明。
ttl: permanent
---

# Target Architecture — Navigation Guide
# 目标架构 — 导航指南

---

## 责任声明（Single Responsibility）

本目录只存放：**目标架构视图（TOGAF）— overview 到 dimension-audit-matrix + architecture_model/ + diagrams/**。

---

## 1. What is this document set / 本文档组是什么

This is the **canonical Architecture Description Set** for ZephyrAlpha 2.0.

采用 **ISO 42010 + TOGAF 四视图 + C4 合成方案**（方法论详情见 [overview.md §1.1](./overview.md)）：

- **ISO 42010** — 定方法论：Architecture Description 由多个 View 组成
- **TOGAF** — 定四层视图：Business / Information / Application / Technology
- **C4 Model** — 定应用视图的可视化：系统上下文（L1）和容器（L2）

> **v3.0.0变更**：物理代码组织以53域为准（§2.1裁定），14层降级为域属性。结构化数据由depgraph派生。

---

## 2. 域索引（53域）

> **真源**：[`generated/domains/index.md`](../generated/domains/index.md)（由 `generate_domain_index.py` 从 depgraph `domains` 表派生）。
> **v3.1.0 变更**：原硬编码 53 域清单+节点数已移除（违反"禁止硬编码会变化的数字"原则，且数据会过时）。域清单、节点数、描述以 generated/ 派生视图为准。

---

## 3. 文件清单

> **注（v3.2.0）**：本清单已全部审核完成（2026-07-04）。A/B/C 判定逻辑：A 污染源清除、B depgraph派生、C 必须写死。已删除 architecture_endgame_locked.md + 3个迁移残留死副本。.mmd 图源内14层引用清理已完成（2026-07-04）。

| 文件 | 说明 | 状态 |
|------|------|------|
| overview.md | 架构总览（方法论导航+决策记录）| ✅ v2.1.1 已审核 |
| business_architecture.md | BA 业务架构视图 | ✅ v2.0.0 已审核（干净）|
| information_architecture.md | IA 信息架构视图 | ✅ 已审核（干净）|
| application_architecture.md | AA 应用架构视图 | ✅ v3.0.2 已审核 |
| technology_architecture.md | TA 技术架构视图 | ✅ v2.1.2 已审核 |
| runtime_planes.md | 运行时平面正交视图 | ✅ v1.1.0 已审核（§3矩阵已重写为53域）|
| capability_heatmap.md | 能力热力图正交视图 | ✅ v2.0.2 已审核 |
| data_architecture.md | DA 数据架构视图 | ✅ v1.0.2 已审核 |
| security_architecture.md | SEC 安全架构视图 | ✅ v1.0.1 已审核（断链已修） |
| integration_architecture.md | INTEG 集成架构视图 | ✅ v1.1.1 已审核 |
| operations_architecture.md | OPS 运维架构视图 | ✅ v0.2.1 已审核 |
| governance_architecture.md | GOV 治理架构视图 | ✅ v2.2.2 已审核 |
| frontend_architecture.md | FE 前端架构视图 | ✅ v1.1.1 已审核（断链已修） |
| diagrams/ | Mermaid 图源文件（28个 .mmd + index.md）| ✅ 14层引用清理已完成（2026-07-04）|

---

## 4. 派生视图（generated/目录）

> 所有派生视图由`scripts/governance/d5_architecture/generators/`下的生成器从depgraph派生。真源在 [`generated/`](../generated/) 目录。

| 派生视图 | 生成器 | 数据源 | 说明 |
|---------|--------|--------|------|
| `generated/domains/index.md` | generate_domain_index.py | domains+nodes | 53域总览索引 |
| `generated/domains/*.md` | generate_domain_doc.py | nodes+edges | 单域架构文档（53个）|
| `generated/domains/*_dependency.mmd` | generate_domain_dependency_diagram.py | nodes+edges | 单域依赖图（53个）|

> **注（v3.1.0）**：原 cross_domain_matrix / capacity_report / design_vs_production / constraint_violations 已迁至 [`01_global_architecture_diagram/`](../01_global_architecture_diagram/) 和 [`03_governance_reports/`](../03_governance_reports/)，不再在 generated/ 下。

---

## 5. Document inventory / 文档清单

| File / 文件 | Layer / 层 | Answers / 回答的核心问题 | Primary audience / 主要读者 | Status / 状态 |
|------------|-----------|------------------------|--------------------------|--------------|
| `index.md`（本文） | — | 本文档组是什么？怎么读？ | 所有人 | active |
| `overview.md` | Cross-layer | 整体架构哲学？53域如何组织？ | 架构师、新加入者 | active |
| `business_architecture.md` | BA | 为谁服务？核心业务能力？ | 业务负责人 | active |
| `information_architecture.md` | IA | `docs/` 有哪些抽屉？ | 文档维护者、AI 协作者 | active |
| `application_architecture.md` | AA | 系统有哪些应用/模块？域如何划分？ | 开发者、架构师 | active |
| `technology_architecture.md` | TA | 用什么技术栈？ | SRE、实施者 | active |
| `runtime_planes.md` 🔷 **正交视图 1** | Orthogonal | 运行平面怎么切分？ | 架构师、SRE | active |
| `capability_heatmap.md` 🔷 **正交视图 2** | Orthogonal | 53域能力成熟度热力图？ | 架构师、决策层 | active |
| `data_architecture.md` | DA | 业务数据对象？ | 量化研究员、数据工程师 | active |
| `security_architecture.md` | SEC | 安全域划分？IAM？ | 安全工程师、合规 | active |
| `integration_architecture.md` | INTEG | 集成风格？接口契约？ | 开发者、架构师、SRE | active |
| `operations_architecture.md` | OPS | 运维域全景？ | SRE、运维工程师 | draft |
| `governance_architecture.md` | GOV | 治理体系三层边界？ | 架构师、合规 | active |
| `frontend_architecture.md` | FE | 前端层分层？ | 前端开发者、架构师 | active |
| `diagrams/` | All | Mermaid 图源文件 | 所有人 | active |

---

## 6. Reading order / 推荐阅读顺序

**First time / 第一次读（5 分钟）**：`index.md`（本文）→ `overview.md` → `generated/domains/index.md`（53域总览）

**Architect / 架构师**：`overview.md` → `generated/domains/index.md` → 按域读`generated/domains/*.md`

**Developer / 开发者**：`application_architecture.md` → `generated/domains/<相关域>.md` → `integration_architecture.md`

**AI collaborator / AI 协作者**：`generated/domains/index.md`（全局索引）→ 按需读取`generated/domains/*.md` → `overview.md`（设计哲学）

---

## 7. View dependencies / 视图依赖关系

> **📊 视图依赖关系总览**：见 [`diagrams/readme_view_dependency_graph.mmd`](diagrams/readme_view_dependency_graph.mmd)

**正交视图说明**：`04bis` 和 `04ter` 是 TOGAF 10 视图之外的正交视图，提供运行平面/能力成熟度的额外切片标注。

**反向约束**：TA 成本限制 → AA 范围 → IA 范围 → BA 野心。

---

## 8. View vs YAML SSoT — key distinction / 视图与 YAML SSoT 的区别

| Type / 类型 | Style / 风格 | Purpose / 用途 |
|------------|-------------|---------------|
| **View** (00–10) | Narrative: explains **why** | For humans, conveys architectural intent |
| **YAML SSoT** (architecture_model/) | Structured: lists **what** | For machines, AI, and CI gates |
| **派生视图** (generated/) | 派生: 从depgraph生成 | 结构化数据可视化，禁止手编 |

---

## 9. Provenance / 来源说明

本文档组由 `DW-IA-DESIGN-001` 拆分升格而来。v3.0.0 基于§2.1裁定重写为53域索引+全景图派生。v3.1.0 瘦身去重。

> **注（v3.1.0）**：修订记录真源在 git log，不再单独维护 §revision_history。

## 排除规则（不应放入本目录的内容）

- ❌ 治理规范 → `01_policies_and_standards/`
- ❌ KB 决策记录 → KB:decisions namespace

## 父级目录

- 父级：[02_enterprise_architecture](../index.md)
