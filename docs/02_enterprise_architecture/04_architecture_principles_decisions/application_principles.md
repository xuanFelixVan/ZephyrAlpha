---
module_id: VIEW-04PRINC-APPLICATION
title: Architecture Principles — Application / 架构原则：应用
doc_type: architecture_view
status: Active
version: 1.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-19
superseded_by: null
supersedes: VIEW-03-APPLICATION-ARCH
related_rationale: []
related_open_questions:
- OQ-063
- OQ-071
- OQ-083
related_kb:
- KBG-0009
- KBG-0011
tags:
- application-principles
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
- 5-core-services
summary: 应用架构永恒原则文档。timeless 方法论——模块归属判定原则（域归属/跨域依赖/容量管理）、Vibe Coding 2.0 五大核心服务定位（LSG/CE/Orc/VMS/FLE）、容错与幂等设计铁律、C4 视图分层、运行时三平面正交视图。派生数据（全域清单、节点统计、域层级分布、5 大服务域归属）不在本文档，由 depgraph + 自动化派生视图维护。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Application
# 架构原则：应用（Application Principles）

---

## §1 定位 / Position

本文档是**应用架构的永恒指导原则**。

**保留内容**：方法论、设计原则、不变约束——模块归属原则、五大核心服务定位、容错与幂等设计、C4 视图分层、运行时三平面正交视图。

**不保留内容**（派生/动态数据，由各自自动化系统维护）：
- 全域清单与统计 → `generated/domains/index.md`（depgraph 派生，待生成）
- 域层级分布 → depgraph `domains` 表
- 节点/边统计数字 → depgraph `nodes`/`edges` 表（时点快照）
- 5 大核心服务域归属 → depgraph
- 跨域依赖矩阵 → `../01_global_architecture_diagram/cross_domain_matrix.md`（由 `generate_cross_domain_matrix.py` 派生）
- 治理代码拓扑 → `scripts/script-manifest.yaml`（SSoT）

**与其他原则文档关系**：
- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- [business_principles.md](business_principles.md)：业务架构原则
- [information_principles.md](information_principles.md)：信息架构原则
- 本文：应用架构原则（模块归属/5 大服务/容错幂等/C4/运行时平面）

---

## §2 C4 视图分层（永恒框架）

### 2.1 C4 四层定义（永恒）

应用架构采用 C4 模型分层描述：

| 层级 | 内容 | 派生方式 |
|------|------|---------|
| **C4-L1 System Context** | 系统上下文（参与者 + 外部系统） | 半派生（参与者框架永恒，外部系统清单派生）|
| **C4-L2 Container** | 容器（部署单元） | 派生 |
| **C4-L3 Component** | 组件（按域分解） | depgraph 派生 |
| **C4-L4 Code** | 代码（类/函数级） | 不绘制（git log 是真源）|

### 2.2 C4-L1 参与者框架（永恒）

| Actor | Type | Role |
|-------|------|------|
| **Independent Operator** | Human (internal) | 系统拥有者；负责策略配置、风险决策、日常监控 |
| **AI Collaborators** | System (internal) | 发散+收口工作流 |

**永恒约束**：AI 协作者的 R/A 角色永远为空（仅限 Consulted），AI 产出必须由人签字承接才落盘。

### 2.3 C4 图表位置（派生）

> **注**：C4-L1/L2/L3 图表由 `scripts/governance/d5_architecture/generators/` 自动生成，不在本文档硬编码。

---

## §3 模块归属原则 / Module Placement Principles

### 3.1 域归属判定（永恒流程）

新模块归属哪个域？

1. 查询 depgraph `domains` 表
2. 按功能职责匹配 `description` 字段
3. 无法匹配时，评估是否需要新增域（需 Owner 批准）

**永恒约束**：
- 所有域平级，无父子关系
- 新增域只需 INSERT 到 `domains` 表，不修改生成器
- 架构与功能域层级保持一致：功能域平级 → 物理路径平级；能平铺绝不嵌套

### 3.2 跨域依赖规则（永恒铁律）

- 跨域依赖 **MUST** 在 depgraph `edges` 表登记
- **禁止循环依赖**（由 `arch_constraints` 表约束）
- 跨域依赖强度由 `coupling_strength` 字段标注
- 依赖关系先行铁律（防幻觉/防漂移治本规则 L1）：任何模块施工前（写第1行业务代码前），MUST 先通过 `apply_depgraph.py` 将该模块的依赖关系登记到 depgraph 设计态（status=planned）

### 3.3 容量管理（永恒二元规则）

**容量治理二元规则**：单域 production_nodes ≤150 通过，>150 必须拆分，无例外（ARCH-CAP-002 v1.0.8）。

- 单域节点上限：150（默认）/ 200（高度耦合可放宽）
- 容量报告见 `../03_governance_reports/capacity_report.md`（自动派生）
- 超容域必须拆分（需 Owner 批准）

---

## §4 Vibe Coding 2.0 五大核心服务（永恒定位）

### 4.1 五大服务一句话定位（永恒框架）

| 缩写 | 服务全称 | 一句话定位 |
|------|---------|-----------|
| **LSG** | LLM Security Gateway | LLM 交互的"安全闸"，四层防御，fail-closed |
| **CE** | Context Engine | AI 编码的"中枢神经" |
| **Orc** | Agent Orchestrator | Vibe Coding 2.0 的"任务引擎" |
| **VMS** | Vector Memory Service | 知识与决策的"向量记忆库" |
| **FLE** | Feedback Loop Engine | 系统自调节的"闭环大脑" |

### 4.2 与域架构的关系（永恒定位）

5 大核心服务属于 `layer_id=L1_platform` 的跨层支撑域，为业务域提供 AI 基础设施能力。

> **注**：5 大服务的具体域归属见 depgraph `domains` 表，不在本文档硬编码。

### 4.3 LSG 唯一 fail-closed 原则（永恒铁律）

**与其余 5 大核心服务的 degraded=True 降级不同**，LSG 是唯一必须 fail-closed 的服务。

详细设计原则见 [security_principles.md §4](security_principles.md)。

---

## §5 容错与幂等设计（永恒铁律）

### 5.1 幂等性铁律（永恒）

**所有写操作 MUST 支持幂等重试**。

特别强调：
- **HO-4 订单提交**（Portfolio → Broker）：幂等设计 + broker ACK回执持久化，**订单重发重复是量化红线**
- Idempotency Key 命中率作为 SLO-3 的 SLI

### 5.2 容错原则（永恒）

- **失败不阻塞**（DLQ + 告警）
- **降级而非崩溃**：5 大核心服务中 4 个（CE/Orc/VMS/FLE）允许 degraded=True，LSG 例外（fail-closed）

### 5.3 回滚设计（永恒双轨 Checkpoint）

- **git commit** — 代码与文档回滚
- **DB dump** — 数据回滚（SQLite JSONL / pg_dump）

---

## §6 运行时三平面正交视图（永恒框架）

运行时三平面横切所有域，**不改变域的业务决策**：

| 平面 | 延迟范围 | 用途 |
|------|---------|------|
| **Hot** | < 10ms | 实时关键路径（订单提交、风控检查） |
| **Warm** | 10ms - 1s | 准实时（信号生成、组合优化） |
| **Cold** | > 1s | 离线（回测、归因、报告） |

**永恒约束**：三平面是正交视图，与域划分独立——同一域可同时包含 Hot/Warm/Cold 组件。

> **注**：详细平面映射见 `runtime_planes_principles.md`。

---

## §7 Architecture Runway / 架构预留通道

> 详见各视图 Runway 章节。合计 37 条 P3 能力挂载点。

---

## §8 视图边界 / Boundaries

### 8.1 本文档覆盖

- C4 视图分层框架（§2）
- 模块归属原则（域归属判定/跨域依赖规则/容量管理）（§3）
- Vibe Coding 2.0 五大核心服务定位（§4）
- 容错与幂等设计铁律（§5）
- 运行时三平面正交视图（§6）
- Architecture Runway（§7）

### 8.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| 全域清单与统计 | `generated/domains/index.md`（depgraph 派生，待生成）|
| 域层级分布 | depgraph `domains` 表 |
| 节点/边统计数字 | depgraph `nodes`/`edges` 表（时点快照）|
| 5 大核心服务域归属 | depgraph |
| 跨域依赖矩阵 | `../01_global_architecture_diagram/cross_domain_matrix.md`（自动派生）|
| C4 图表 | `scripts/governance/d5_architecture/generators/`（自动生成）|
| 治理代码拓扑 | `scripts/script-manifest.yaml`（SSoT）|
| ACL 落盘位置 | `security_principles.md` |
| 供应商注册表 | `architecture_model/technology/vendor_registry.yaml`（待创建） |
| 运行时平面详细映射 | `runtime_planes_principles.md`|
| LSG 详细设计原则 | `security_principles.md` §4 |

### 8.3 与其他原则文档关系

- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则（LSG 详细设计）
- [integration_principles.md](integration_principles.md)：集成架构原则
- [business_principles.md](business_principles.md)：业务架构原则
- [information_principles.md](information_principles.md)：信息架构原则
- 本文：应用架构原则（模块归属/5 大服务/容错幂等/C4/运行时平面）

---

> **文档维护原则**：本文档只包含永恒指导原则。任何随 depgraph 演进、域数量变化、节点统计更新的内容，均不应写入本文档——它们由各自自动化系统维护。
