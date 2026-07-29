---
classification: confidential
date: '2026-07-30'
doc_type: index
generated: '2026-06-26'
layer: cross_layer
merged_from: README.md + index.md
module_id: ARCH-006
status: Active
title: Target Architecture — Navigation Guide / 目标架构导航
version: 3.4.0
depends_on:
  - {target: EA-INDEX, at: "§子目录", why: "父级 EA 索引——target_architecture 为其子目录"}
tags:
- index
- navigation
- domain-driven
- depgraph-derived
summary: v3.4.0：删除 dataflow_views.md/topology_views.md/c4_l1_l2_views.md（均被生成视图或SSoT覆盖，手绘图已过时漂移）；§3/§5 同步清理引用。v3.3.0：删除 dimension_audit_matrix.md；§2 域表改为指针指向 generated domain_index。v3.0.0：基于§2.1裁定，导航改为53域索引+全景图派生视图说明。
ttl: permanent
---

# Target Architecture — Navigation Guide （被恢复）
# 目标架构 — 导航

---

## 责任声明（Single Responsibility）

本目录只存放：**目标架构视图（TOGAF）— overview / 索引 / 视觉视图（C4组件·流程·治理）+ revision_history**。结构化数据真源在 `architecture_model/` YAML 与 `generated/` 派生视图。

---

## 1. What is this document set / 本文档组是什么

This is the **canonical Architecture Description Set** for ZephyrAlpha 2.0.

采用 **ISO 42010 + TOGAF 四视图 + C4 合成方案**：

- **ISO 42010** — 定方法论：Architecture Description 由多个 View 组成
- **TOGAF** — 定四层视图：Business / Information / Application / Technology
- **C4 Model** — 定应用视图的可视化：域组件分解（L3）；L1系统上下文/L2容器由生成视图（integration_topology.md）覆盖

> **v3.0.0变更**：物理代码组织以53域为准（§2.1裁定），14层降级为域属性。结构化数据由depgraph派生。

---

## 2. 域索引（数据源：depgraph）

> 完整域清单（含节点数/描述/层级分布）由 `generate_domain_index.py` 从 depgraph 自动生成，见 [`../02_domain_architecture_docs/domain_index.md`](../02_domain_architecture_docs/domain_index.md)。
> 能力成熟度分布见 [`../01_global_architecture_diagram/global_capability_heatmap.md`](../01_global_architecture_diagram/global_capability_heatmap.md)（70 域×10 能力域，depgraph 自动生成）。
> 本导航不再内联域表，避免与 depgraph 真源漂移。

---

## 3. 文件清单

| 文件 | 说明 |
|------|------|
| overview.md | 架构总览（v2.1.0：53域+全景图派生，方法论叙事）|
| application_flows.md | 5 张端到端时序图（订单/成交/风控/再平衡/异常）|
| c4_component_views.md | 3 张 C4-L3 域组件图（D_MKT_DATA/D_EX_CORE/D_ML_TRAIN）|
| governance_views.md | 治理 d2b 闭环 + 三层边界图 |
| revision_history.md | 完整修订历史归档（index.md §10 完整版）|
| business_principles.md → ../04_architecture_principles_decisions/ + value_stream_map.yaml | BA 业务架构原则（原 business_architecture.md 已迁移） |
| information_principles.md → ../04_architecture_principles_decisions/ | IA 信息架构原则（原 information_architecture.md 已迁移） |
| technology_principles.md → ../04_architecture_principles_decisions/ + dr_bcp_matrix.yaml | TA 技术架构原则（原 technology_architecture.md 已迁移） |
| data_principles.md → ../04_architecture_principles_decisions/ + data_entity_catalog.yaml | DA 数据架构原则（原 data_architecture.md 已迁移） |
| security_principles.md → ../04_architecture_principles_decisions/ + threat_model.yaml | SEC 安全架构原则（原 security_architecture.md 已迁移） |
| governance_principles.md → ../04_architecture_principles_decisions/ + governance_systems_registry.yaml | GOV 治理架构原则（原 governance_architecture.md 已迁移） |
| frontend_principles.md → ../04_architecture_principles_decisions/ + frontend_model.yaml | FE 前端架构原则（原 frontend_architecture.md 已迁移） |

---

## 4. 派生视图（generated/ 目录）

> 所有派生视图由`scripts/governance/d5_architecture/generators/`下的生成器从depgraph派生。

| 派生视图 | 生成器 | 实际路径 | 说明 |
|---------|--------|--------|------|
| 域总览索引 | generate_domain_index.py | `../02_domain_architecture_docs/domain_index.md` | 全域总览索引 |
| 跨域依赖矩阵 | generate_cross_domain_matrix.py | `../01_global_architecture_diagram/cross_domain_matrix.md` | 跨域依赖矩阵 |
| 能力热力图 | generate_capability_heatmap.py | `../01_global_architecture_diagram/global_capability_heatmap.md` | 70域×10能力域成熟度 |
| 集成拓扑图 | generate_integration_topology.py | `../01_global_architecture_diagram/integration_topology.md` | 外部系统+内部层+契约 |
| 数据流图 | generate_dataflow_diagram.py | `../05_dataflow_architecture/dataflow_index.md` | 跨域核心数据流 |
| 单域架构文档 | generate_domain_doc.py | `generated/domains/*.md` | 单域架构文档 |

---

## 5. Document inventory / 文档清单

| File / 文件 | Layer / 层 | Answers / 回答的核心问题 | Primary audience / 主要读者 | Status / 状态 |
|------------|-----------|------------------------|--------------------------|--------------|
| `index.md`（本文） | — | 本文档组是什么？怎么读？ | 所有人 | active |
| `overview.md` | Cross-layer | 整体架构哲学？53域如何组织？ | 架构师、新加入者 | active |
| `application_flows.md` | Cross-layer | 端到端时序如何编排？ | 架构师、开发者 | active |
| `c4_component_views.md` | Cross-layer | 核心域组件分解？ | 开发者 | active |
| `governance_views.md` | Cross-layer | 治理闭环+三层边界？ | 架构师、合规 | active |
| [`business_principles.md`](../04_architecture_principles_decisions/business_principles.md) + [`value_stream_map.yaml`](../../../architecture_model/cross_cutting/value_stream_map.yaml) | BA | 为谁服务？核心业务能力？ | 业务负责人 | active |
| [`information_principles.md`](../04_architecture_principles_decisions/information_principles.md) | IA | `docs/` 有哪些抽屉？ | 文档维护者、AI 协作者 | active |
| [`technology_principles.md`](../04_architecture_principles_decisions/technology_principles.md) + [`dr_bcp_matrix.yaml`](../../../architecture_model/technology/dr_bcp_matrix.yaml) | TA | 用什么技术栈？ | SRE、实施者 | active |
| [`data_principles.md`](../04_architecture_principles_decisions/data_principles.md) + [`data_entity_catalog.yaml`](../../../architecture_model/data/data_entity_catalog.yaml) | DA | 业务数据对象？ | 量化研究员、数据工程师 | active |
| [`security_principles.md`](../04_architecture_principles_decisions/security_principles.md) + [`threat_model.yaml`](../../../architecture_model/security/threat_model.yaml) | SEC | 安全域划分？IAM？ | 安全工程师、合规 | active |
| [`governance_principles.md`](../04_architecture_principles_decisions/governance_principles.md) + [`governance_systems_registry.yaml`](../../../architecture_model/governance_systems_registry.yaml) | GOV | 治理体系三层边界？ | 架构师、合规 | active |
| [`frontend_principles.md`](../04_architecture_principles_decisions/frontend_principles.md) + [`frontend_model.yaml`](../../../architecture_model/frontend/frontend_model.yaml) | FE | 前端层分层？ | 前端开发者、架构师 | active |

---

## 6. Reading order / 推荐阅读顺序

**First time / 第一次读（5 分钟）**：`index.md`（本文）→ `overview.md` → [`../02_domain_architecture_docs/domain_index.md`](../02_domain_architecture_docs/domain_index.md)（全域总览）

**Architect / 架构师**：`overview.md` → [`../02_domain_architecture_docs/domain_index.md`](../02_domain_architecture_docs/domain_index.md) → 按域读`generated/domains/*.md`

**Developer / 开发者**：`../04_architecture_principles_decisions/application_principles.md` → `generated/domains/<相关域>.md` → `architecture_model/contracts/cross_layer_contracts.yaml`（集成点+接口契约）

**AI collaborator / AI 协作者**：[`../02_domain_architecture_docs/domain_index.md`](../02_domain_architecture_docs/domain_index.md)（全局索引）→ 按需读取`generated/domains/*.md` → `overview.md`（设计哲学）

---

## 7. View dependencies / 视图依赖关系

> **📊 视图依赖关系总览**：见 [`overview.md`](overview.md) §3 C4 模型（内嵌 mermaid）

**正交视图说明**：原 `04bis` runtime_planes 正交视图已迁移至 [`runtime_planes_principles.md`](../04_architecture_principles_decisions/runtime_planes_principles.md) + [`runtime_planes.yaml`](../../../architecture_model/cross_cutting/runtime_planes.yaml)。能力成熟度方法论见 [`capability_maturity_principles.md`](../04_architecture_principles_decisions/capability_maturity_principles.md)，热力图数据见 [`global_capability_heatmap.md`](../01_global_architecture_diagram/global_capability_heatmap.md)（depgraph 自动生成）。

**反向约束**：TA 成本限制 → AA 范围 → IA 范围 → BA 野心。

---

## 8. View vs YAML SSoT — key distinction / 视图与 YAML SSoT 的区别

| Type / 类型 | Style / 风格 | Purpose / 用途 |
|------------|-------------|---------------|
| **View** (00–10) | Narrative: explains **why** | For humans, conveys architectural intent |
| **YAML SSoT** (architecture_model/) | Structured: lists **what** | For machines, AI, and CI gates |
| **派生视图** (generated/ + 01_global/ + 05_dataflow/) | 派生: 从depgraph生成 | 结构化数据可视化，禁止手编 |

---

## 9. Provenance / 来源说明

本文档组由 `DW-IA-DESIGN-001` 拆分升格而来。v3.0.0 基于§2.1裁定重写为53域索引+全景图派生。

---

## 10. Revision history / 修订记录

> 完整历史见 [revision_history.md](revision_history.md)。本处仅保留最近 3 次修订。

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-07-30 | **v3.4.0**：删除 `dataflow_views.md`/`topology_views.md`/`c4_l1_l2_views.md`——均被生成视图（integration_topology.md/dataflow_index.md）或 SSoT（value_stream_map.yaml/cross_layer_contracts.yaml/technology_landscape.yaml）覆盖，手绘图已过时漂移（TimescaleDB→ClickHouse、53域→72域）；§3/§5/§责任声明 同步清理引用。 |
| 2026-07-30 | **v3.3.0**：删除 `dimension_audit_matrix.md`（12维评分卡无消费者，score_architecture.py 不存在）；§2 域表改为指针指向 `../02_domain_architecture_docs/domain_index.md`；§3/§5 修复 3 处 stale 引用（operations_architecture.md / dimension_audit_matrix.md / session_carryover_schema.md 均已删）。 |
| 2026-07-29 | **v3.2.0**：删除 `diagrams/` 下 22 个冗余 .mmd 图源文件（已内嵌至 MD 文档），修复全项目 .mmd 引用。 |

## 排除规则（不应放入本目录的内容）

- ❌ 治理规范 → `01_policies_and_standards/`
- ❌ KB 决策记录 → KB:decisions namespace

## 父级目录

- 父级：[02_enterprise_architecture](../index.md)
