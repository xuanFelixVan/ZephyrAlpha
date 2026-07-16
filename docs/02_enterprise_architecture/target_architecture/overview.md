---
module_id: VIEW-00-OVERVIEW
title: Target Architecture — Overview / 目标架构总览
doc_type: architecture_view
status: Active
version: 2.1.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-17
superseded_by: null
supersedes: null
related_rationale: R26, R27, R28, R29, R30
related_open_questions: []
tags:
- overview
- togaf
- c4
- iso-42010
- architecture-philosophy
- adr-summary
- vibe-coding-2.0
- 5-core-services
- domain-driven
- depgraph-derived
summary: 架构文档组的总览视图。v2.1.0：瘦身后保留方法论导航与关键决策记录，派生机制/惯例/修订记录/5大服务定位移交 SSoT 真源。v2.0.0：基于§2.1裁定，14层降级为域属性，功能域成为唯一物理分类体系。结构化数据由depgraph全景图派生。
date: '2026-07-04'
ttl: permanent
---

# Target Architecture — Overview
# 目标架构总览

---

## 0. Executive Summary / 高管摘要

**系统定位**：ZephyrAlpha 是个人量化投资系统的 AI-native 重构，采用功能域唯一物理分类体系（基于depgraph全景图派生），Python 全栈，Vibe Coding 驱动（Cursor + Trae 双 AI IDE）。

**核心架构决策**（v2.0.0 基于§2.1裁定）：
- **功能域唯一分类**：功能域是唯一物理分类体系，逻辑层作为域的`layer_id`属性而非并行分类（双分类=AI幻觉温床）。
- **全景图派生**：所有结构化数据（域清单/模块清单/依赖关系/容量统计）由`depgraph (PostgreSQL)`派生，禁止在MD中硬编码。
- **运行时三平面**（引擎平面 / Vibe Coding 平面 / 治理平面）→ 正交划分开发态和运行态关注点
- **治理三层**（制度标准层 / 企业架构层 / 蓝图施工层）→ Phase 退出准入双门协议门禁
- **安全红线**：4 条不可撤销（详见 [architecture_principles.md](../04_architecture_principles_decisions/architecture_principles.md) §1）
- **技术栈**：Python + Pydantic + SQLite/PostgreSQL + ChromaDB + MCP 协议（具体版本以 technology_landscape.yaml 为准）
- **当前阶段**：experimental 启动，功能域已定义，模块边界待定

> **注（v2.1.0）**：原"6 大 Vibe Coding 2.0 核心服务施工中"状态描述已移除——6大服务接口规范真源在 [`docs/03_modules/_cross_layer/_b_track_interfaces/`](../../03_modules/_cross_layer/_b_track_interfaces/)，状态以接口规范文档为准。

**System Identity**: ZephyrAlpha is an AI-native personal quantitative investment system. 53-domain unique physical classification (derived from depgraph panorama). Python full-stack, Vibe Coding driven. The legacy 14-layer (L00-L13) has been demoted to a domain attribute (`layer_id`) per §2.1 ruling — single classification eliminates AI hallucination from dual-taxonomy ambiguity.

---

## 1. Architecture approach / 架构方法论

### 1.1 Three-standard composite / 三标准合成方案

ZephyrAlpha 2.0 adopts a composite of three internationally recognized standards:

| Standard / 标准 | Role in this project / 在本项目中的作用 |
|----------------|---------------------------------------|
| **ISO/IEC/IEEE 42010:2011** | Methodology: AD = multiple Views, each View addresses Stakeholder Concerns under a Viewpoint |
| **TOGAF 9.2 / 10** | Four-layer view taxonomy: Business / Information / Application / Technology |
| **C4 Model** (Simon Brown) | Application-level visualization: System Context (L1) and Container (L2) |

### 1.2 唯一物理分类体系裁定（§2.1）

**裁定**：功能域是唯一物理分类体系。逻辑层作为域的`layer_id`属性，不作为并行分类。

| 裁定项 | 结论 | 理由 |
|--------|------|------|
| 逻辑层 vs 功能域 | **功能域唯一** | 两个并行分类=AI每次判断用哪个=幻觉温床 |
| 逻辑层信息保留方式 | 作为域的`layer_id`属性 | 属性不是分类，不产生二元性 |
| 逻辑层YAML文件 | 废弃，信息合并入depgraph域定义 | 避免SSoT分裂 |

**当前域层级分布**：由 depgraph `domains` 表派生，详见 [`generated/domains/index.md`](../generated/domains/index.md)。禁止在本文硬编码域数量/节点数/边数。

> **注（v2.1.0）**：派生工具链与派生产出目录的真源在 [`docs/02_enterprise_architecture/generated/`](../generated/) 目录及 AGENTS.md，不再于此硬编码。

### 1.3 Current phase positioning / 当前阶段定位

| 维度 | 状态 | 说明 |
|------|------|------|
| **功能域物理分类** | ✅ **已定义** | depgraph `domains` 表为SSoT |
| **5 大核心服务（VMS/CE/Orc/FLE/LSG）** | — | 接口规范真源：[`_b_track_interfaces/`](../../03_modules/_cross_layer/_b_track_interfaces/) |
| **17 项技术选型** | ✅ **已定稿** | 见 [`technology_landscape.yaml`](../../../architecture_model/technology/technology_landscape.yaml)（SSoT）|
| **模块内部边界** | ⏳ **讨论中** | experimental 落地时细化 |
| **设计态→运营态迁移** | 🔧 **进行中** | design_maturity 分布详见 generated/ 派生视图 |

---

## 2. TOGAF four layers / TOGAF 四层结构

> **📊 TOGAF 四层堆叠图**：见 [`diagrams/togaf_layer_stack.mmd`](diagrams/togaf_layer_stack.mmd)

```
┌────────────────────────────────────────────────────────────┐
│  01. Business Architecture (BA) / 业务架构                  │
│      Who we serve, what we do, core processes, NFR         │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  02. Information Architecture (IA) / 信息架构               │
│      What information assets exist, how organized          │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  03. Application Architecture (AA) / 应用架构               │
│      What modules/services exist, how they interact        │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  04. Technology Architecture (TA) / 技术架构                │
│      What technology stack underpins everything            │
└────────────────────────────────────────────────────────────┘
```

> **注**：TOGAF四层是**视图分类方法**，不是物理代码分层。物理代码组织以功能域为准（见§1.2裁定）。

---

## 3. C4 Model complement / C4 模型补充

TOGAF resolves "vertical layering". C4 Model resolves "how to visualize the inside of Application Architecture":

| Level / 级别 | Focus / 关注点 | Usage in this project / 本项目用法 |
|-------------|--------------|----------------------------------|
| **L1 — System Context** | System's position in the external world | ✅ Required → `diagrams/c4_l1_system_context.mmd` |
| **L2 — Container** | Independent deployable units inside the system | ✅ Required → `diagrams/c4_l2_containers.mmd` |
| **L3 — Component** | Components inside a container | 🟡 As needed, in blueprints |
| **L4 — Code** | Class/function level | ❌ Not drawn (code itself is documentation)|

---

## 4. Three trees / 三棵树的架构对应关系

| Tree / 树 | Primary view / 核心视图归属 | Key diagrams / 主要图 | Owner document / 归属文档 |
|----------|--------------------------|---------------------|--------------------------|
| `docs/` | Information Architecture | `docs/` 抽屉拓扑图 + 文档生命周期图 | `information_architecture.md` |
| `src/` | Application Architecture | C4-L1 系统上下文 + C4-L2 容器图 + 域依赖图 | `application_architecture.md` |
| `scripts/` | Application Architecture (sub-view) | 治理代码拓扑图 + pre-commit/CI 钩子流程图 | `application_architecture.md §4` |

> **v2.0.0变更**：原"14层代码分层图"改为"域依赖图"，由`generate_domain_dependency_diagram.py`从depgraph派生。

---

## 5. Key KB 决策记录 summary / 关键 KB 决策记录 汇总

> **真源**：KB 决策记录系统。本表为关键决策导航，非穷举，新增决策以 KB 系统为准。

| KB 决策记录 | Decision / 决策 | Impact / 影响 |
|-----|----------------|--------------|
| KBG-0001 | `docs/` is the single canonical source of truth | 所有文档归属 |
| KBG-0002 | Single frontmatter schema + phased required fields | 所有文档 frontmatter |
| KBG-0003 | Dual/multi AI collaboration workflow | 文档生产方式 |
| KBG-0015 | Context Engine：NetworkX + JSON + 本地 LLM 压缩 | 5 大核心服务之一 |
| KBG-0016 | Vector Memory：ChromaDB 0.6 + BGE-M3 ONNX + 递归分块 | 5 大核心服务之一 |
| KBG-0017 | Agent Orchestrator：SQLite + asyncio.Queue 起步 | 5 大核心服务之一 |
| KBG-0018 | Agent Sandbox：Windows ACL + 只读挂载 | Orchestrator 配套 |
| KBG-0019 | Feedback Loop Engine：SQLite 时间序列 + EMA 异常检测 | 5 大核心服务之一 |
| KBG-0020 | LLM Security Gateway：OWASP LLM Top 10 + fail-closed | 5 大核心服务之一 |
| KBG-0021 | SSoT Validator：scaffold 唯一任务，阻塞下游 | scaffold 门禁 |

> **注（v2.1.0）**：5 大核心服务的详细架构图 / 服务间依赖 DAG / 降级协调矩阵真源在 [`application_architecture.md §4A`](./application_architecture.md) 及各服务接口规范文档。

---

## 6. Architecture Runway Index / 架构预留通道总览

> Architecture Runway（架构跑道）记录了系统未来 36 个月以上的 P3 能力挂载点。

### §6.1 各视图 Runway 章节快速导航

| 视图 | Runway 章节 | 主要覆盖域 |
|------|------------|----------|
| [01-BA 业务架构](./business_architecture.md) | §8 Architecture Runway | 战略层 |
| [02-IA 信息架构](./information_architecture.md) | §11 Architecture Runway | 信息/数据层 |
| [03-AA 应用架构](./application_architecture.md) | §11 Architecture Runway | 应用组件层 |
| [04-TA 技术架构](./technology_architecture.md) | §14 Architecture Runway | 基础设施层 |

> **注（v2.1.0）**：本节 Runway 导航依赖 BA/IA/AA/TA 四大视图文件的存在。若视图文件在后续治理中被删除，本导航表需同步调整。
