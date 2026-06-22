---
module_id: VIEW-00-OVERVIEW
title: Target Architecture — Overview / 目标架构总览
doc_type: architecture_view
status: Active
version: 1.4.1
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
- 6-core-services
- 14-layer-frozen
summary: 架构文档组的总览视图。覆盖整体架构哲学、TOGAF 四层与 C4 模型的关系说明、关键 KB 决策记录 汇总，以及三棵树（docs/src/scripts）的架构对应关系。是所有视图的导读入口。v1.4.1：§0 英文部分从中英完全重复精简为关键信息摘要。
date: '2026-05-02'
ttl: permanent
---

# Target Architecture — Overview
# 目标架构总览

---

## 0. Executive Summary / 高管摘要

> 本节融合了 `architecture-brief.md`（已删除），为各层级读者提供一页纸快速定位。

**系统定位**：ZephyrAlpha 是个人量化投资系统的 AI-native 重构，14 层物理架构（L00 数据源 → L13 实验管线），Python 全栈，Vibe Coding 驱动（Cursor + Trae 双 AI IDE）。

**核心架构决策**：
- **14 层骨架**（TOGAF + C4 混合）→ 每层独立蓝图，层间松耦合
- **运行时三平面**（引擎平面 / Vibe Coding 平面 / 治理平面）→ 正交划分开发态和运行态关注点
- **治理三层**（制度标准层 / 企业架构层 / 蓝图施工层）→ Phase 退出准入双门协议门禁
- **安全红线**：4 条不可撤销（详见 [architecture_principles.md](architecture_principles.md) §1）
- **技术栈**：Python >=3.11（以 `pyproject.toml` requires-python 为真源）+ Pydantic v2 + SQLite WAL + ChromaDB + FastAPI 原型 + MCP 协议
- **当前阶段**：experimental 启动，14 层已冻结，模块边界待定，6 大 Vibe Coding 2.0 核心服务施工中

**System Identity**: ZephyrAlpha is an AI-native personal quantitative investment system. 14-layer physical architecture (L00→L13), Python full-stack, Vibe Coding driven. Current: experimental kickoff — layers frozen, 6 core services under construction. Tech: Python >=3.11 (see `pyproject.toml` requires-python) + Pydantic v2 + SQLite WAL + ChromaDB + FastAPI + MCP. Safety red lines: see [architecture_principles.md](architecture_principles.md) §1.

---

## 1. Architecture approach / 架构方法论

### 1.1 Three-standard composite / 三标准合成方案

ZephyrAlpha 2.0 adopts a composite of three internationally recognized standards:

ZephyrAlpha 2.0 采用三个国际标准的合成方案：

| Standard / 标准 | Role in this project / 在本项目中的作用 |
|----------------|---------------------------------------|
| **ISO/IEC/IEEE 42010:2011** | Methodology: AD = multiple Views, each View addresses Stakeholder Concerns under a Viewpoint / 方法论：AD 由多个 View 组成，每个 View 针对特定 Stakeholder 的 Concern |
| **TOGAF 9.2 / 10** | Four-layer view taxonomy: Business / Information / Application / Technology / 四层视图分类：Business / Information / Application / Technology |
| **C4 Model** (Simon Brown) | Application-level visualization: System Context (L1) and Container (L2) / 应用层可视化：系统上下文（L1）和容器（L2） |

### 1.2 ISO 42010 four elements / ISO 42010 四要素映射

| Element / 要素 | Definition / 定义 | In ZephyrAlpha 2.0 / 在本项目中的体现 |
|---------------|------------------|--------------------------------------|
| **Stakeholder** | Anyone with concerns about the architecture / 对架构有关注点的人 | 业务负责人（用户）、开发者、AI 协作者、SRE、审计者 |
| **Concern** | A matter of interest to a stakeholder / 利益相关者关心的问题 | "系统做什么"、"数据在哪"、"技术栈"、"部署拓扑" |
| **Viewpoint** | Rules for constructing a view / 定义"如何看某类 view"的规范 | TOGAF 四视图规范 + C4 规范 |
| **View** | A representation conforming to a viewpoint / 符合 viewpoint 的架构描述 | `01-04` 每份文档 |

**Formula**: Architecture Description = multiple Views + consistency checks between them.
**公式**：Architecture Description = 多个 View + 它们之间的一致性检查。

### 1.3 Current phase positioning / 当前阶段定位（2026-04-24）

ZephyrAlpha 2.0 架构在当前阶段处于**"物理架构冻结 + 模块边界待定"**的过渡定位：

| 维度 | 状态 | 说明 |
|------|------|------|
| **14 层物理架构（L00-L13）** | ✅ **已冻结** | 11 源审计共识，不再讨论删减或增加层 |
| **6 大核心服务（VMS/CE/Orc/FLE/LSG/KB）** | ✅ **已定稿** | 2026-04-24 产出（`application_architecture.md §4A`）；接口规范 6 份齐备（见 `docs/03_modules/_b_track_interfaces/`）|
| **17 项技术选型** | ✅ **已定稿** | 见 `technology_landscape.yaml`（SSoT）|
| **4 路线图** | ✅ **已定稿** | 见 `phase-transition-protocol.md` |
| **模块内部边界（具体文件/函数级）** | ⏳ **讨论中** | experimental 落地时细化，不在本阶段冻结 |
| **任务卡路径（迁移重组）** | 🔧 **重组中** | 重组方案已定稿：`docs/03_modules/_restructuring/blueprint.md`（GOV-FSTR-001）——7 Phase 施工 |

**架构消费者须知**：

- 引用本架构时，14 层分层 + 6 大核心服务 + 17 项选型可以作为**强约束**写入蓝图
- 模块内部组件边界（C4-L3 以下）保持**灵活**，experimental 落地时可调整
- "Vibe Coding 2.0 基础设施"和"14 层量化业务"是**正交**关系：前者是 L12 跨层支撑；后者是 L00-L11 + L13 业务层

---

## 2. TOGAF four layers / TOGAF 四层结构

```
┌────────────────────────────────────────────────────────────┐
│  01. Business Architecture (BA) / 业务架构                  │
│      Who we serve, what we do, core processes, NFR         │
│      为谁服务、做什么业务、核心流程、非功能需求               │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  02. Information Architecture (IA) / 信息架构               │
│      What information assets exist, how organized          │
│      有哪些信息资产、如何组织、文档生命周期                   │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  03. Application Architecture (AA) / 应用架构               │
│      What modules/services exist, how they interact        │
│      有哪些应用/模块/服务、如何交互                          │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  04. Technology Architecture (TA) / 技术架构                │
│      What technology stack underpins everything            │
│      用什么技术栈支撑上述一切                                │
└────────────────────────────────────────────────────────────┘
```

**Driving relationships / 驱动关系**：

- BA drives IA: business capabilities determine what data/documents/knowledge to accumulate.
- IA drives AA: data distribution determines application boundaries.
- AA drives TA: application characteristics (batch/realtime/AI) determine technology choices.
- Reverse constraint: TA cost limits constrain AA → IA → BA ambition.

- BA 驱动 IA：业务能力决定要沉淀什么数据/文档/知识。
- IA 驱动 AA：数据分布决定应用边界。
- AA 驱动 TA：应用特性（批量/实时/AI）决定技术选型。
- 反向约束：TA 的成本上限反向约束 AA → IA → BA 的野心。

> **📊 TOGAF 架构层次图**：见 [`diagrams/togaf_layer_stack.mmd`](diagrams/togaf_layer_stack.mmd) — TOGAF 四层（Business→Information→Application→Technology）映射

---

## 3. C4 Model complement / C4 模型补充

TOGAF resolves "vertical layering". C4 Model (Simon Brown) resolves "how to visualize the inside of Application Architecture":

TOGAF 解决"垂直分层"，C4 Model（Simon Brown）解决"应用架构内部如何可视化"：

| Level / 级别 | Focus / 关注点 | Usage in this project / 本项目用法 |
|-------------|--------------|----------------------------------|
| **L1 — System Context** | System's position in the external world / 系统在外部世界中的位置 | ✅ Required / 必画 → `diagrams/c4_l1_system_context.mmd` |
| **L2 — Container** | Independent deployable units inside the system / 内部可独立部署单元 | ✅ Required / 必画 → `diagrams/c4_l2_containers.mmd` |
| **L3 — Component** | Components inside a container / 容器内部组件分解 | 🟡 As needed / 按需，在蓝图中画 |
| **L4 — Code** | Class/function level / 具体类/函数级别 | ❌ Not drawn / 不画（代码本身即文档）|

**TOGAF + C4 = the most mainstream combination in industry for complete enterprise architecture expression.**
**TOGAF + C4 = 工业界最主流的完整企业架构表达组合。**

---

## 4. Three trees / 三棵树的架构对应关系

The ZephyrAlpha 2.0 repository has three main trees, each corresponding to a primary architecture view:

ZephyrAlpha 2.0 仓库有三棵主树，每棵对应一个主要架构视图：

| Tree / 树 | Primary view / 核心视图归属 | Key diagrams / 主要图 | Owner document / 归属文档 |
|----------|--------------------------|---------------------|--------------------------|
| `docs/` | Information Architecture | `docs/` 抽屉拓扑图 + 文档生命周期图 + 跨抽屉引用图 | `information_architecture.md` |
| `src/` | Application Architecture | C4-L1 系统上下文 + C4-L2 容器图 + 14 层代码分层图 + 跨层数据流图(CTR-001~006) | `application_architecture.md` |
| `scripts/` | Application Architecture (sub-view) | 治理代码拓扑图 + pre-commit/CI 钩子流程图 | `application_architecture.md §4` |

---

## 5. Key KB 决策记录 summary / 关键 KB 决策记录 汇总

| KB 决策记录 | Decision / 决策 | Impact / 影响 |
|-----|----------------|--------------|
| KBG-0001 | `docs/` is the single canonical source of truth / 唯一真源 | 所有文档归属 |
| KBG-0002 | Single frontmatter schema + phased required fields / 单一 schema + 分阶段必填 | 所有文档 frontmatter |
| KBG-0003 | Dual/multi AI collaboration workflow (Kimi diverge + Opus converge) / 双 AI 协作工作流 | 文档生产方式 |
| KBG-0015 | Context Engine：NetworkX + JSON + 本地 LLM 压缩 (Qwen2.5-3B) | 6 大核心服务之一 |
| KBG-0016 | Vector Memory：ChromaDB 0.6 + BGE-M3 ONNX + 递归分块 | 6 大核心服务之一 |
| KBG-0017 | Agent Orchestrator：SQLite + asyncio.Queue 起步，NATS 升级 | 6 大核心服务之一 |
| KBG-0018 | Agent Sandbox：Windows ACL + 只读挂载；Docker Desktop（升级）| Orchestrator 配套 |
| KBG-0019 | Feedback Loop Engine：SQLite 时间序列 + EMA 异常检测 | 6 大核心服务之一 |
| KBG-0020 | LLM Security Gateway：OWASP LLM Top 10 + fail-closed + 四层防御 | 6 大核心服务之一 |
| KBG-0021 | SSoT Validator：scaffold 唯一任务，阻塞下游 | scaffold 门禁 |

Full KB 决策记录 index: KB:decisions namespace（33 ADRs, SQLite knowledge 表）

---

## 5A. Vibe Coding 2.0 Infrastructure / Vibe Coding 2.0 基础设施架构

> 新增于 v1.2.0（2026-04-24）。TOGAF 四层（§2）是**企业架构的垂直分层**；本节补充的 6 大核心服务是**AI 基础设施的横向支撑**。两者正交共存。

### 5A.1 6 大核心服务一句话定位

| 缩写 | 服务全称 | 一句话定位 | 接口规范 |
|------|---------|-----------|---------|
| **LSG** | LLM Security Gateway | LLM 交互的"安全闸"，四层防御，fail-closed | `08_.../llm-security-gateway-interface.md` |
| **CE** | Context Engine | AI 编码的"中枢神经"，上下文 build/compress/validate/inject | `08_.../context-engine-interface.md` |
| **Orc** | Agent Orchestrator | Vibe Coding 2.0 的"任务引擎"，任务生命周期 + Agent 沙箱 | `08_.../agent-orchestrator-interface.md` |
| **VMS** | Vector Memory Service | 知识与决策的"向量记忆库"，ChromaDB 5 个 Collection | `08_.../vector-memory-service-interface.md` |
| **FLE** | Feedback Loop Engine | 系统自调节的"闭环大脑"，指标→异常→动作 | `08_.../feedback-loop-engine-interface.md` |

### 5A.2 与 14 层量化架构的关系

```
L12 跨层支撑层
  └─ src/zephyr/
       ├─ llm-security/      ← LSG
       ├─ vector-memory/     ← VMS
       ├─ context-engine/    ← CE
       ├─ orchestrator/      ← Orc
       └─ feedback-loop/     ← FLE

6 大核心服务属于 L12，为 L00-L11 + L13 业务层提供 AI 基础设施能力。
```

### 5A.3 详细架构

完整架构图 / 服务间依赖 DAG / 降级协调矩阵 / 与 14 层集成方式 / 4 落地路线 → 见 [`application_architecture.md §4A`](./application_architecture.md)。

---

## 6. Architecture document conventions / 架构文档惯例

### 6.1 Diagrams / 图的惯例

All diagrams use **Mermaid-only** (including Mermaid native C4 syntax). Rationale:

所有图采用 **Mermaid-only**（含 Mermaid 原生 C4 语法）。理由：

- Text source code, Git diff friendly / 文本源码，Git diff 友好
- Native rendering in Cursor IDE, GitHub, Obsidian, Feishu / Cursor IDE、GitHub、Obsidian、Feishu 原生渲染
- Mermaid v10+ natively supports C4 four levels / Mermaid v10+ 原生支持 C4 四层
- Single maintainer, lighter is better / 单人维护，越轻越好
- Smooth future upgrade to C4 Structurizr DSL / 未来升级到 Structurizr DSL 平滑

### 6.2 Versioning / 版本化惯例

Flat directory + `frontmatter.version`. No version subdirectories (e.g., no `v2.0/`). Evidence: AWS Well-Architected, Azure Architecture Center, Google Cloud Architecture Framework, Netflix, ThoughtWorks KB 决策记录 patterns all use this approach.

平铺目录 + `frontmatter.version`。不用版本化子目录（如不建 `v2.0/`）。实证：AWS Well-Architected / Azure Architecture Center / Google Cloud Architecture Framework / Netflix / ThoughtWorks KB 决策记录 范式均采用此做法。

### 6.3 Naming / 命名惯例

Directory: `target_architecture/` (TOGAF term). File names: `NN-kebab-case.md`. Module IDs: `VIEW-NN-<TYPE>-ARCH` (primary views) / `VIEW-<TYPE>` (README/brief/vibe) / `VIEW-BYDOMAIN-<DOMAIN>` (by-domain) / `STD-<TYPE>` (schema) / `POL-<TYPE>` (protocol). Stage G (2026-04-25) migrated from `EA-ARCH-*` legacy namespace.

目录：`target_architecture/`（TOGAF 术语）。文件名：`NN-kebab-case.md`。Module ID：`VIEW-NN-<TYPE>-ARCH`（主视图）/ `VIEW-<TYPE>`（README/brief/vibe）/ `VIEW-BYDOMAIN-<DOMAIN>`（子域视图）/ `STD-<TYPE>`（Schema 标准）/ `POL-<TYPE>`（协议）。Stage G（2026-04-25）从 `EA-ARCH-*` 旧命名空间迁移。

---

## 8. Architecture Runway Index / 架构预留通道总览

> Architecture Runway（架构跑道）记录了系统未来 36 个月以上的 P3 能力挂载点。
> 所有 Runway 条目均来自 S1 产出：P3 蓝图索引（42 条）[待创建]

### §8.1 各视图 Runway 章节快速导航

| 视图 | Runway 章节 | 条目数 | 主要覆盖域 |
|------|------------|--------|----------|
| [01-BA 业务架构](./business_architecture.md#8-architecture-runway--架构预留通道) | §8 Architecture Runway | 5 条 | 战略层（ml_train）：投委会支持、多基金经理协调、全球宏观策略、战略联盟、机构级报告 |
| [02-IA 信息架构](./information_architecture.md#11-architecture-runway--架构预留通道) | §11 Architecture Runway | 3 条 | 信息/数据层（l02/l09）：多模态因子、ESG 因子、知识图谱自动构建 |
| [03-AA 应用架构](./application_architecture.md#11-architecture-runway--架构预留通道) | §11 Architecture Runway | 22 条 | 应用组件层（l02/l03/l04/l07/l08/l09）：ML前沿研究 10 条 + 策略高阶 5 条 + 接口/研究 7 条 |
| [04-TA 技术架构](./technology_architecture.md#14-architecture-runway--架构预留通道) | §14 Architecture Runway | 7 条 | 基础设施层（l01/l06）：分布式计算、云原生、边缘计算、多云、区块链审计、SSO、合规技术栈 |
| **合计** | — | **37 条** | 全层覆盖（战略 / 信息 / 应用 / 技术）|

> **注**：P3-AI-002（强化学习通用框架）与 P3-AI-001 激活条件相同，合并到 RW-AA-L04-01 处理，故总数 37 < P3 索引的 42 条（另 5 条治理/战略类全部进入 01-BA 或 04-TA Runway）。

---

### §8.2 激活监控机制

**何时应当 Review 一次 Runway？**

| 触发类型 | 频率 | 动作 |
|---------|------|------|
| **季度例行 Review** | 每 3 个月（对齐 technology-landscape.md 刷新周期）| 对照 `p3-blueprint-index.md §6 激活监控清单` [待创建] 逐项检查触发条件 |
| **重大里程碑后** | 事件驱动 | 接入真实资金 / P0 流水线稳定运行 3 个月 / 因子库突破 100 条 / 团队规模扩展 |
| **架构重大变更后** | 事件驱动 | 新增技术选型（KB 决策记录 新增）/ 撤回某条 P1-P2 能力 / 合规要求改变 |

**如何判断是否应激活某条 Runway？**

1. **检查触发条件**：对照该条目 "激活触发条件" 列，所有条件是否已满足（AND 逻辑）
2. **更新 activation_status**：在 `p3-blueprint-index.md` [待创建] 中将该条目 `activation_status` 从 `deferred` 改为 `ready`
3. **人工拍板**：发起架构评审（Architect + AI Operator），确认资源预算（参考 04-TA §11/§12）
4. **记录决策**：激活决策写入 KB decisions namespace（替代原 adr/ 目录）
5. **Runway 条目归档**：激活后将该条目从视图 Runway 章节移除（或标注 `activated`），避免堆积

**不应激活的信号（Hold 住）**：
- 触发条件未满足，但希望"先做准备"→ **不激活**，可在 P3 条目附注研究计划
- 激活成本（人月）> 当前阶段 ROI → **推迟**，下季度重评
- 依赖基础能力（P0/P1）尚未稳定运行 → **阻塞**，先修底层

---

## 7. Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-04-17 | v1.0.0：从 DW-IA-DESIGN-001 拆分升格建立。覆盖架构方法论、三标准合成、三棵树对应关系与关键 KB 决策记录 汇总。 |
| 2026-04-19 | v1.1.0：S6 — 追加 §8 Architecture Runway Index 总览（5 视图 Runway 导航 + 激活监控机制，R63）。 |
| 2026-04-24 | v1.2.0：B-d-1 — 追加 §1.3 当前阶段定位（14 层物理架构冻结，模块边界待定）+ §5A Vibe Coding 2.0 基础设施（6 大核心服务总览）+ §5 KB 决策记录 汇总扩至 KBG-0015~0021。|
| 2026-05-02 | v1.3.0：双轨制对齐——刷新日期 + 新增 [`architecture_principles.md`](architecture_principles.md) 引用（架构原则集中 SSoT：含 Open Source First 五条子原则 + BvB 五维评分法 + 必须自研的五条硬约束）。|
