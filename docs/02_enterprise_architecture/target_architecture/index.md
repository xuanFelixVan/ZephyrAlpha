---
classification: confidential
date: '2026-05-06'
doc_type: index
generated: '2026-05-06'
layer: cross_layer
merged_from: README.md + index.md
module_id: ARCH-006
status: Active
title: Target Architecture — Navigation Guide / 目标架构导航
version: 2.2.0
depends_on:
  - {target: EA-INDEX, at: "§子目录", why: "父级 EA 索引——target-architecture 为其子目录，引用父级子目录一览"}
---

# Target Architecture — Navigation Guide
# 目标架构 — 导航指南

---

## 责任声明（Single Responsibility）

本目录只存放：**目标架构视图（TOGAF）— overview 到 dimension-audit-matrix + architecture-model/ + diagrams/**。

## 文件清单

| 文件 | 说明 |
|------|------|
| overview.md | 文档 |
| business_architecture.md | 架构视图 |
| information_architecture.md | 架构视图 |
| application_architecture.md | 架构视图 |
| technology_architecture.md | 架构视图 |
| runtime_planes.md | 文档 |
| capability_heatmap.md | 文档 |
| data_architecture.md | 架构视图 |
| security_architecture.md | 架构视图 |
| integration_architecture.md | 架构视图 |
| operations_architecture.md | 架构视图 |
| governance_architecture.md | 架构视图 |
| frontend_architecture.md | 架构视图 |
| dimension_audit_matrix.md | 文档 |
| session_carryover_schema.md | Schema 定义 |
| revision_history.md | 完整修订历史归档 |

## 1. What is this document set / 本文档组是什么

This is the **canonical Architecture Description Set** for ZephyrAlpha 2.0.

It describes the target architecture using the **ISO 42010 + TOGAF four-layer + C4 composite approach**:

- **ISO 42010** — defines the methodology: an Architecture Description (AD) consists of multiple Views, each addressing specific Stakeholder Concerns under a defined Viewpoint.
- **TOGAF** — defines the four view layers: Business / Information / Application / Technology.
- **C4 Model** — defines application-level visualization: System Context (L1) and Container (L2).

> **Relation to `AGENTS.md` §6.9**: Markdown views here are the narrative *Architecture Description Set*; machine-consumable facts live under `architecture-model/` YAML with the dual-tree split declared in repo-root **`architecture-model/SCOPE.yaml`**. On conflict, YAML + SCOPE win; record rationale in `architecture-rationale-log.md`.

---

本文档组是 ZephyrAlpha 2.0 的**架构描述集（Architecture Description Set）** canonical 真源。

采用 **ISO 42010 + TOGAF 四视图 + C4 合成方案**：

- **ISO 42010** — 定方法论：Architecture Description 由多个 View 组成，每个 View 针对特定 Stakeholder 的 Concern。
- **TOGAF** — 定四层视图：Business / Information / Application / Technology。
- **C4 Model** — 定应用视图的可视化：系统上下文（L1）和容器（L2）。

> **与 `AGENTS.md` §6.9 的关系**：本目录下 **TOGAF/C4 视图 Markdown** 充当 *Architecture Description Set* 的阅读真源；**可机读事实**（分层登记、跨层契约、不变量、technology-landscape 全量等）以 `architecture-model/` 下 YAML + 仓库根 **`architecture-model/SCOPE.yaml`** 双树分工为准。二者冲突时——以 YAML + SCOPE 为机器裁决依据，并回写 rationale-log。

---

---

## 1ter. Orthogonal Views / 正交视图体系

TOGAF 10 视图（00-10）按架构抽象层切分。正交视图按运行时特征和成熟度两个维度重新切分，横切所有层。设计铁律（OV-P1~P5）和扩展预留口见 [runtime_planes.md](runtime_planes.md) §0 + [capability_heatmap.md](capability_heatmap.md) §0。

| 视图编号 | 文件名 | 切片维度 | 对标业界 | 状态 |
|---------|-------|---------|---------|------|
| **04bis** | `runtime_planes.md` | 运行时特征（Hot < 10ms / Warm 10ms-1s / Cold > 1s）| Citadel / Jane Street / Two Sigma / Jump Trading | active |
| **04ter** | `capability_heatmap.md` | 能力成熟度（L0-L5）| ArchiMate 3.2 / Gartner / Goldman Sachs EA | active |

---

## 2. Document inventory / 文档清单

| File / 文件 | Layer / 层 | Answers / 回答的核心问题 | Primary audience / 主要读者 | Status / 状态 |
|------------|-----------|------------------------|--------------------------|--------------|
| `index.md`（本文） | — | 本文档组是什么？怎么读？ | 所有人 | active |
| `overview.md` | Cross-layer | 整体架构哲学？四层如何关联？关键 KB 决策记录 汇总？ | 架构师、新加入者 | active |
| `business_architecture.md` | BA | 为谁服务？核心业务能力？端到端流程？NFR？ | 业务负责人 | active |
| `information_architecture.md` | IA | `docs/` 有哪些抽屉？怎么分？文档生命周期？ | 文档维护者、AI 协作者 | active |
| `application_architecture.md` | AA | 系统有哪些应用/模块？`src/` 与 `scripts/` 如何分层？ | 开发者、架构师 | active |
| `technology_architecture.md` | TA | 用什么技术栈？运行时拓扑？部署方式？ | SRE、实施者 | active |
| `runtime_planes.md` 🔷 **正交视图 1** | Orthogonal | **运行平面**（Hot < 10ms / Warm 10ms-1s / Cold > 1s）怎么把 14 层业务代码 + 前端 + 治理层重新切分？Sim-to-Real Gap 怎么消？低延迟交易激活路径？ | 架构师、SRE、量化工程师、前端开发者、治理工程师 | active · v1.0.0 · 2026-04-19 |
| `capability_heatmap.md` 🔷 **正交视图 2** | Orthogonal | 14 层业务能力 × 10 能力域（7 业务 + 3 横切）的**成熟度热力图**（L0-L5）？Gap-to-Target 差距？每季度 review 机制？对标顶级机构差在哪？ | 架构师、产品设计、决策层、外部评审、合规 | active · v1.0.0 · 2026-04-19 |
| `data_architecture.md` | DA | 系统有哪些**业务数据对象**？PIT / Survivorship / 血缘 / MDM / 数据质量 / 保留归档怎么治理？ | 量化研究员、数据工程师、AI 架构师、风控合规 | active · v1.0.0 · 2026-04-19 |
| `security_architecture.md` | SEC | 安全域划分？IAM？密钥管理？数据保护？审计日志？威胁模型？ | 安全工程师、合规、架构师 | **active** · v1.0.0 · 2026-04-24 |
| `integration_architecture.md` | INTEG | 集成风格？内外部集成拓扑？接口契约治理？ACL 策略？事件总线规划？ | 开发者、架构师、SRE | active · v1.0.0 · 2026-04-19 |
| `operations_architecture.md` | OPS | 运维域全景（部署/监控/备份/灾备/变更/事件/容量/成本）？Runbook 目录？ | SRE、运维工程师、架构师 | **draft** · v0.2.0 · 2026-04-19 |
| `governance_architecture.md` | GOV | 治理体系三层边界（Policy/Factory/Runtime）？39 治理系统分层归属？AI 自治三层预留口子？激活路径？ | 架构师、合规、治理工程师、AI 协作者 | active · v1.0.0 · 2026-04-19 |
| `frontend_architecture.md` | FE | 前端层（frontend/）的分层 / Module Federation / State / Design System / 构建部署 / Activation Triggers ？ | 前端开发者、架构师、产品设计 | active · v1.0.0 · 2026-04-19 |
| `architecture-model/cross-cutting/capability_heatmap.yaml` | BA | 业务能力与成熟度条目（机器可读 SSoT） | 业务负责人、架构师 | active |
| `architecture-model/index.yaml` + `architecture-model/layers/*.yaml` | AA | 应用/模块与分层属性（联邦制索引 + 各层清单） | 开发者、架构师 | active |
| `architecture-model/technology/technology_landscape.yaml` | TA | 技术雷达与选型清单（Adopt/Trial/Hold） | SRE、实施者 | active |
| `integration_architecture.md` §3.2 | AA/TA | 集成点枚举（EI 系列等；v1.1.0 起由本视图承载） | 开发者、SRE | active |
| `architecture-model/` 🆕 | **YAML SSoT** | 联邦制 YAML 模型（24 分区：14 层 + shared + frontend + scripts + cross-cutting + contracts + events + ddd-model + technology + core-services + shared-infra），所有视图的模块属性数据源 | AI 协作者、架构师、CI 门禁 | active · v2.0.0 · 2026-04-21 |
| `architecture-model/scripts/check_architecture_gates.py` 🆕 | CI | GATE-01~08 + GATE-SC + EXTRA-01~03 自动检查脚本（已迁移至 `scripts/governance/d5_architecture/`） | CI、架构师 | active · v2.1.0 · 2026-05-02 |
| `architecture-model/cross-cutting/invariants.yaml` 🆕 | GOV | 不变核心（immutable core）机器可读 SSoT | 架构师、合规 | active · v1.0.0 · 2026-04-21 |
| `dimension_audit_matrix.md` | Cross-layer | 12 维架构质量评分矩阵 + 一人开发场景风险考量 | 架构师、审计 | active · v1.0.0 |
| `session_carryover_schema.md` | Cross-layer | AI 会话跨 Context Window 接续的 Schema/协议定义 | AI 协作者、架构师 | active · v1.0.0 |
| `diagrams/` | All | Mermaid 图源文件（跨域图，被多份文档引用） | 所有人 | active |

---

## 3. Reading order / 推荐阅读顺序

**First time / 第一次读（5 分钟）**：`index.md`（本文）→ `overview.md` → `information_architecture.md §3.1`（文档抽屉清单）

**Architect / 架构师（完整视图顺序）**：`00` → `01` → `02` → `05` → `03` → `07` → `04` → `06` → `08` → `09` → `10`

> 顺序逻辑：先业务（00→01）→ 信息组织（02）→ 数据对象（05）→ 应用分层（03，后端 14 层）→ 集成接口（07）→ 技术基础设施（04）→ 安全（06，active v1.0.0）→ 运维（08，draft in-progress）→ 治理（09，三层边界 Policy/Factory/Runtime）→ 前端独立平台架构（10，与 03 物理隔离）

**Developer / 开发者**：`application_architecture.md` → `integration_architecture.md`（接口契约）→ `technology_architecture.md` → `data_architecture.md`（实现数据对象时参考）

**SRE / 运维**：`technology_architecture.md` → `operations_architecture.md`（运维域全景）→ `application_architecture.md §4` → `data_architecture.md §3/§9`（存储与归档策略）

**Quant researcher / 量化研究员**：`data_architecture.md §4/§5/§6` → `application_architecture.md`（PIT / Survivorship / 血缘是回测可信的前置条件）

**Data engineer / 数据工程师**：`data_architecture.md`（全篇）→ `integration_architecture.md §3/§4`（数据流拓扑与契约）→ `application_architecture.md §4.1 L00`

**Security / 安全合规**：`security_architecture.md`（安全架构全景 active v1.0.0）→ `governance_architecture.md`（治理三层边界 + 合规架构联动）→ `integration_architecture.md §5`（ACL 策略）→ `application_architecture.md §4.1`（ACL 落盘位置）

**Governance / 治理工程师**：`governance_architecture.md`（三层边界定义 + 39 系统分层 + 激活时间表）→ `application_architecture.md §5`（scripts 治理代码拓扑）→ `security_architecture.md`（治理与安全交集）→ KB:decisions namespace（KBG-0010 治理架构三层边界，原物理文件已迁入）→ 源讨论稿 `archive/reorg-2026-04-24/realized-as-adr/working-designs/governance-three-layer-boundary-design.md`（ARC-20260424-004，决策溯源）

**AI collaborator / AI 协作者（推荐首选路径 v1.8.0）**：`architecture-model/index.yaml`（全局索引，1 分钟定位任何模块）→ 按需读取 `architecture-model/layers/lXX.yaml`（模块属性 SSoT）→ `overview.md`（设计哲学）→ 按需读取视图正文（设计理由与叙事）

**Frontend developer / 前端开发者**：`frontend_architecture.md`（全篇）→ `integration_architecture.md §3/§4`（API 契约规范）→ `data_architecture.md §2`（了解所需业务数据对象）→ `application_architecture.md §4.1 L08`（api_gateway 子模块）→ `security_architecture.md`（前端安全策略，active v1.0.0）

---

## 4. View dependencies / 视图依赖关系

> **📊 视图依赖关系总览**：见 [`diagrams/readme_view_dependency_graph.mmd`](diagrams/readme_view_dependency_graph.mmd)

**正交视图说明**：`04bis` 和 `04ter` 使用**黄色高亮节点**表示它们是 **TOGAF 10 视图之外的正交视图**——虚线 `-.正交标注叠加.->` 表示它们**不改变 TOGAF 视图的业务决策**，只是在这些视图上提供额外的切片标注（运行平面 / 能力成熟度）。详见 §1ter 正交视图体系。

**反向约束**：TA 成本限制 → AA 范围 → IA 范围 → BA 野心。

**IA vs DA 正交性**：IA 治"docs/ 文档抽屉"，DA 治"业务数据对象"，两者**平级且零内容重叠**。详见 `data_architecture.md §10.2`（图书馆书架 vs 账本资金往来的类比）。

**INTEG（07）的双重下游**：集成架构同时为安全架构提供"所有外部接入点清单"，为运维架构提供"需要监控的集成点列表"——这也是为什么 07 建议在 06/08 之前阅读。

---

## 4bis. View Status — 视图状态概览

本文档组的 **视图状态分布**：

| 状态 | 视图 | 数量 |
|------|------|:---:|
| **active** | overview–frontend + runtime-planes, capability-heatmap（正交视图）| 11（含 2 正交）|
| **draft** | `operations_architecture.md`（v0.2.0，in-progress）| 1 |
| **reserved** | `11-*.md`（预留编号，架构设计时有意跳过）| 1 |

**security_architecture.md** 已于 2026-04-24 从 skeleton 升格为 active v1.0.0。

### VIEW-11 跳号说明

视图编号 11 在架构设计时**有意跳过（reserved）**——10 个 TOGAF 视图（00-10）已构成完整的架构描述集，11 号预留为未来可能的新增视图入口（如"AI 原生架构视图"或"跨系统互操作视图"）。编号不被回收，新视图从 11 起分配。

> 对标 KB 决策记录 编号空间的 append-only 原则：编号跳过需显式登记，不得成为黑箱。

### `operations_architecture.md` 为何仍为 draft？

| 视图 | draft 的合理性 | 当前阶段情况 |
|------|-----------------|------------|
| `operations_architecture.md` | 运维架构（Runbook、DR 演练、容量规划）需要"有运维对象"才有意义 | 无生产环境、无守护进程、无 CI/CD → 写详细 Runbook 无法演练，形同虚设 |

### 何时激活（升级为 `active`）？

`operations_architecture.md` 在其 **§8/§10 Activation Triggers** 中列出了明确的激活触发条件（8 条）：

- **operations** 的核心触发：真实资金接入 / 部署至非 localhost / 7×24 小时运行需求 / 引入第二个协作成员

> **任何激活条件触发时，应立即将 `operations_architecture.md` 的 `status: draft` 改为 `status: active` 并补齐实质内容**，这是架构一致性红线。

---

## 4ter. 决策追溯档案 — `governance_architecture.md` 从 deferred-closure 到 active 的历史路径

> 详见 [architecture-rationale-log.md](../architecture-rationale-log.md) R65 + R66 条目。简要：2026-04-19 同日两次变更——上午 R65 定 `deferred-closure`，下午 R66 用户改选"立即拍板"，落地 v1.0.0 active。完整拍板路径见 KBG-0010 §1 + handoff-log.md。T1-T6 触发条件现为 09 视图内部子系统升级触发器（非视图本身激活触发器）。

---

## 5. View vs YAML SSoT — key distinction / 视图与 YAML SSoT 的区别

| Type / 类型 | Style / 风格 | Purpose / 用途 |
|------------|-------------|---------------|
| **View** (00–10) | Narrative: explains **why** / 叙事性：解释"为什么" | For humans, conveys architectural intent / 给人读，传递架构意图 |
| **YAML SSoT** (architecture-model/) | Structured: lists **what** / 结构化：列出"有哪些" | For machines, AI, and CI gates / 给机器读、给 AI、给 CI 门禁 |

No catalog without a view = a list without a soul.
No view without a catalog = empty talk.

没有 view 的 catalog 是"没灵魂的清单"，没有 catalog 的 view 是"空话"。

---

## 6. Diagrams / 图的组织

完整的图文件清单见 [diagrams/index.md](diagrams/index.md)。所有图以 `.mmd`（Mermaid）源文件存放在 `diagrams/`，被视图文档引用。单点维护原则：改一次图，所有引用自动更新。

---

## 7. Provenance / 来源说明

This document set was split and promoted from `DW-IA-DESIGN-001` (`target-information_architecture.md` v2.0.0, 690 lines), which was identified as a **Monolithic Architecture Document Anti-pattern** on 2026-04-17. The split was designed in `DW-ARCH-DESIGN-001` (`architecture-docset-meta-design.md`).

本文档组由 `DW-IA-DESIGN-001`（`target-information_architecture.md` v2.0.0，690 行）拆分升格而来。原稿于 2026-04-17 被判定为"单文件 Monolithic Anti-pattern"，拆分方案定义在 `DW-ARCH-DESIGN-001`（`architecture-docset-meta-design.md`）。

---

## 8. Revision history / 修订记录

> 完整历史见 [revision_history.md](revision_history.md)。本处仅保留最近 3 次修订。

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-05-06 | **v2.2.0（AUDIT-04 / 治理收口）**：双树与 SCOPE/SSoT 地图对齐；Python ≥3.11 基线贯通；`09_audit/findings` 与契约 `ownership_model`；`validate_ssot` + 登记表 + `batch_create_index_md` 修正；INV-005 源码/EA 分层消歧。详情见 [revision_history.md](revision_history.md)。 |
| 2026-05-02 | **v2.1.0（审计修复批次）**：修复 4 项 SSoT 对齐问题：(a) `architecture-model/infra/` 创建 core_services.yaml + shared_infra.yaml 骨架文件，消除 `_index.yaml` 引用不存在文件的问题；(b) `architecture_principles.md` v1.1.0 §0 新增安全红线 4 条（R1-R4），`overview.md` 同步改为引用链接，消除安全红线双源；(c) `ssot-authority-map.md` v2.3.0 移除 `layer_01` 历史误标、拆分矛盾追踪为活跃/已解决；(d) 修订历史归档至 `revision_history.md`，index.md 仅保留最近 3 条。 |
| 2026-05-01 | **v2.0.0（架构审查 P0 修复批次）**：(a) **删除 `dependency-graph-framework.md`**，其唯一独有价值——依赖置信度分级（L1/L2/L3）已提取迁入 `architecture-model/layers/schema.yaml` v2.1。(b) **by-domain 双轨结构调整**：§1bis 整节切除 + §2 文档清单 5 行 by-domain 删除。(c) **同步 06/08 视图状态**：`security_architecture.md` skeleton → active v1.0.0；`operations_architecture.md` skeleton → draft v0.2.0。 |

## 排除规则（不应放入本目录的内容）

- ❌ 治理规范 → `01_policies_and_standards/`
- ❌ KB 决策记录 → KB:decisions namespace（原 `02_enterprise_architecture/adr/` 物理目录已删除）

## 父级目录

- 父级：[02_enterprise_architecture](../index.md)
