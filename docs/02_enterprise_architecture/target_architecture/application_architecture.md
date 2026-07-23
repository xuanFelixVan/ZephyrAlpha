---
module_id: VIEW-03-APPLICATION-ARCH
title: Target Architecture — Application Architecture / 目标架构：应用架构 （被恢复）
doc_type: architecture_view
status: Active
version: 3.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-21
superseded_by: null
supersedes: null
related_rationale: R29, R30, R33, R49, R53, R54, R55, R56, R69
related_open_questions:
- OQ-021
- OQ-022
- OQ-043
- OQ-045
- OQ-063
- OQ-067
- OQ-071
- OQ-072
- OQ-083
related_kb:
- KBG-0009
- KBG-0011
tags:
- application-architecture
- togaf
- aa
- c4
- domain-driven
- depgraph-derived
- modules
- acl
- vendor-registry
- fault-tolerance
- idempotency
- quant-redline
- runtime-planes
- orthogonal-view
- vibe-coding-2.0
- 6-core-services
summary: TOGAF Application Architecture 视图（v3.0.0 重组织版）。基于§2.1裁定，模块清单改为53域派生，数据源depgraph。原14层模块清单废弃。
date: '2026-06-26'
ttl: permanent
---

## 1. Purpose of this view / 本视图的用途

The Application Architecture answers:

- What applications / modules / services exist? (C4 views)
- How do they interact? (Interfaces and protocols)
- How is `src/zephyr/` structured? (53域物理分类，数据源depgraph)
- How is `scripts/` organized? (Governance code topology)
- Where do future platform modules belong? (Module placement)

> **v3.0.0 重组织说明**：基于§2.1裁定，模块清单改为53域派生。原14层模块清单废弃，14层降级为域的`layer_id`属性。模块属性详情见`generated/domains/*.md`（由`generate_domain_doc.py`派生）。

---

## 2. C4-L1: System Context / C4-L1 系统上下文图

### 2.1 Actor list / 参与者清单

| Actor / 参与者 | Type / 类型 | Role / 职责 |
|--------------|------------|------------|
| **Independent Operator** 独立操作者 | Human (internal) | 系统拥有者；负责策略配置、风险决策、日常监控 |
| **AI Collaborators** AI 协作者 | System (internal) | Kimi (Trae) + Opus/Sonnet (Cursor)；发散+收口工作流 |

### 2.2 External system list / 外部系统清单

| External System / 外部系统 | Direction / 方向 | Protocol / 协议 | Purpose / 用途 |
|--------------------------|----------------|----------------|---------------|
| **Broker API** 券商 API | Bidirectional | REST / FIX | 发送交易委托；接收成交回报与持仓 |
| **Market Data Provider** 行情数据源 | Inbound | REST / WebSocket | 提供历史与实时行情数据 |
| **LLM Providers** LLM 服务商 | Outbound | REST | AI 推理调用 |
| **Feishu** 飞书 | Outbound | REST (Webhook) | 通知与报告分发 |

### 2.3 System context diagram / 系统上下文图

> **📊 C4-L1 系统上下文图**：见 [`diagrams/c4_l1_system_context.mmd`](diagrams/c4_l1_system_context.mmd)

---

## 3. C4-L2: Container / C4-L2 容器图

> **📊 C4-L2 容器图**：见 [`diagrams/c4_l2_containers.mmd`](diagrams/c4_l2_containers.mmd)

---

## 4. 域架构（53域，数据源：depgraph）

> 本节为v3.0.0重写。模块清单由`generated/domains/*.md`派生，禁止在本文硬编码。
> 完整域索引见`generated/domain_index.md`。

### 4.1 域统计概览

| 指标 | 值 | 数据源 |
|------|:---:|--------|
| 域总数 | 53 | depgraph `domains` 表 |
| 节点总数 | 6501 | depgraph `nodes` 表 |
| 依赖边总数 | 7191 | depgraph `edges` 表 |
| production 节点 | 1404 | depgraph `nodes.design_maturity` |
| design 节点 | 89 | depgraph `nodes.design_maturity` |
| ~~prototype 节点~~ | ~~5008~~ | ARCH-MM-002 已删除 |

### 4.2 域层级分布

| layer_id | 域数量 | 域清单 |
|----------|:---:|--------|
| `L0_infrastructure` | 5 | `D_INFRA_A2A`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_INFRA_RUNTIME`, `D_INFRA_TELEMETRY` |
| `L1_foundation` | 15 | `D_ALT_DATA`, `D_AUTONOMY_CORE`, `D_BEHAVIORAL_AUDIT`, `D_DATA_ENG`, `D_DATA_GOV`, `D_DATA_SEC`, `D_FRONTEND`, `D_INTEGRATION`, `D_INTEGRATION_GATEWAY`, `D_MKT_DATA`, `D_OPS`, `D_REPORTING`, `D_SECURITY`, `D_SECURITY_LLM`, `D_SHARED` |
| `L2_domain` | 32 | `D_ASHARE_SIGNAL`, `D_AUDITTEST`, `D_AUTONOMY_PERM`, `D_BACKTEST`, `D_COMPLIANCE`, `D_CROSS_ASSET`, `D_DIGITAL_TWIN`, `D_EXEC_SIM`, `D_EX_CORE`, `D_EX_SOR`, `D_FACTOR`, `D_FUNDAMENTAL_SIGNAL`, `D_GOVERNANCE`, `D_GOV_AUDIT`, `D_GOV_DOCS`, `D_GOV_DRIFT`, `D_GOV_ENFORCEMENT`, `D_GOV_RULE`, `D_GOV_SCRIPTS`, `D_INTELLIGENCE`, `D_KNOWLEDGE`, `D_ML_SERVE`, `D_ML_TRAIN`, `D_PF_ALLOC`, `D_PF_CORE`, `D_POSITION`, `D_RISK`, `D_SELL_DECISION`, `D_SIGLEGACY`, `D_SIGQC`, `D_SIMULATION`, `D_TRADING` |
| `unassigned` | 1 | `D_GOV_REPAIR` |


### 4.3 域详细清单

> 完整域清单（含模块数/容量/描述）见 [`generated/domain_index.md`](../generated/domain_index.md)。
> 单域详细文档见 [`generated/domains/*.md`](../generated/domains/)（53个）。
> 单域依赖图见 [`generated/domains/*_dependency.mmd`](../generated/domains/)（53个）。

### 4.4 跨域依赖矩阵

> 完整跨域依赖矩阵见 [`generated/cross_domain_matrix.md`](../generated/cross_domain_matrix.md)（由`generate_cross_domain_matrix.py`从`edges`表派生）。

---

## 4A. Vibe Coding 2.0 Infrastructure / Vibe Coding 2.0 基础设施架构

### 4A.1 6 大核心服务一句话定位

| 缩写 | 服务全称 | 一句话定位 | 域归属 |
|------|---------|-----------|--------|
| **LSG** | LLM Security Gateway | LLM 交互的"安全闸"，四层防御，fail-closed | 见depgraph |
| **CE** | Context Engine | AI 编码的"中枢神经" | 见depgraph |
| **Orc** | Agent Orchestrator | Vibe Coding 2.0 的"任务引擎" | 见depgraph |
| **VMS** | Vector Memory Service | 知识与决策的"向量记忆库" | 见depgraph |
| **FLE** | Feedback Loop Engine | 系统自调节的"闭环大脑" | 见depgraph |

### 4A.2 与域架构的关系

6 大核心服务属于`layer_id=L1_platform`的跨层支撑域，为业务域提供 AI 基础设施能力。具体域归属见depgraph `domains`表。

---

## 5. Scripts governance code topology / 治理代码拓扑

> 治理代码拓扑图：见 [`diagrams/scripts_topology.mmd`](diagrams/scripts_topology.mmd)

治理脚本注册表：`scripts/script-manifest.yaml`（SSoT）

---

## 6. Module placement principles / 模块归属原则

### 6.1 域归属判定

新模块归属哪个域？查询depgraph `domains`表，按功能职责匹配`description`字段。无法匹配时，评估是否需要新增域（需Owner批准）。

### 6.2 跨域依赖规则

- 跨域依赖MUST在depgraph `edges`表登记
- 禁止循环依赖（由`arch_constraints`表约束）
- 跨域依赖强度由`coupling_strength`字段标注

### 6.3 容量管理

- 单域节点上限：150（默认）/ 200（高度耦合可放宽）
- 容量报告见 [`generated/capacity_report.md`](../generated/capacity_report.md)
- 超容域必须拆分（需Owner批准）

---

## 7. Fault tolerance & idempotency / 容错与幂等设计摘要

> 详细设计见各域蓝图。本节仅摘要。

- **幂等性**：所有写操作MUST支持幂等重试
- **容错**：失败不阻塞（DLQ + 告警）
- **回滚**：双轨Checkpoint（git commit + DB dump：SQLite JSONL / pg_dump）

---

## 8. ACL & vendor registry / ACL与供应商注册表

- ACL落盘位置：见`security_architecture.md`
- 供应商注册表：`architecture_model/technology/vendor_registry.yaml`

---

## 9. Runtime planes orthogonal view / 运行时平面正交视图

> 详见 [`runtime_planes.md`](runtime_planes.md)

运行时三平面（Hot < 10ms / Warm 10ms-1s / Cold > 1s）横切所有域，不改变域的业务决策。

---

## 10. Architecture Runway / 架构预留通道

> 详见各视图 Runway 章节。合计 37 条 P3 能力挂载点。

---

## 11. Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-06-26 | **v3.0.0（DM-200912 Phase4-A）**：基于§2.1裁定重写——模块清单改为53域派生（数据源depgraph）；原14层模块清单废弃；新增§4域架构、§4.1域统计概览、§4.2域层级分布、§4.3域详细清单、§4.4跨域依赖矩阵；§6模块归属原则改为域归属判定。 |
| 2026-05-06 | v2.2.0：双树与 SCOPE/SSoT 地图对齐。 |
| 2026-04-22 | v2.0.0：模块属性详情迁移至 architecture_model/ 联邦 YAML 模型。 |
