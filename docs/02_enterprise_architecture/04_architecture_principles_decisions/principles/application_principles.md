---
module_id: VIEW-04PRINC-APPLICATION
title: Architecture Principles — Application / 架构原则：应用
doc_type: architecture_view
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
language: zh
created_by: human_plus_agent
valid_from: 2026-07-30
superseded_by: null
supersedes: VIEW-03-APPLICATION-ARCH
tags:
- application-principles
- fault-tolerance
- idempotency
- quant-redline
- capacity
- cross-domain
summary: 应用架构永恒约束精简版。仅保留不可降级铁律：跨域依赖登记、容量二元规则、LSG fail-closed、幂等性（含 HO-4 量化红线）、回滚双轨、运行时三平面正交。C4 框架/模块归属流程/5大服务定义表等可派生内容已移除（depgraph + b_track yaml 是真源）。
date: '2026-07-30'
ttl: permanent
---

# 架构原则：应用（Application Principles）

> 精简版 v2.0（2026-07-30）：删除 C4 教学理论（TOGAF 通用知识）、模块归属判定流程（已在 depgraph domains 设计态）、5 大服务定义表（已在 b_track yaml）。仅保留 6 条永恒约束。
> 派生数据（全域清单/节点统计/域层级/5 大服务归属/C4 图表/跨域矩阵）不在本文档，由 depgraph + 自动化派生视图维护。

---

## §1 跨域依赖规则（永恒铁律）

- 跨域依赖 **MUST** 在 depgraph `edges` 表登记
- **禁止循环依赖**（由 `arch_constraints` 表约束）
- 依赖关系先行铁律（L1）：施工前（写第 1 行业务代码前）MUST 先通过 `apply_depgraph.py` 登记设计态依赖（status=planned）
- 所有域平级，无父子关系；能平铺绝不嵌套

> 域归属判定流程见 depgraph `domains` 表设计态，不在本文档重复。

---

## §2 容量管理（永恒二元规则）

**单域 production_nodes ≤ 150 通过，> 150 必须拆分，无例外。**

- 上限值与判定口径真源：TRAE-055 / ARCH-CAP-002
- 高度耦合是拆分信号而非放宽理由
- 容量报告见 `../03_governance_reports/capacity_report.md`（自动派生）

---

## §3 LSG 唯一 fail-closed 原则（永恒铁律）

5 大核心服务（LSG/CE/Orc/VMS/FLE）中，**仅 LSG 必须 fail-closed**，其余 4 个允许 `degraded=True` 降级。

- LLM 交互的"安全闸"——失败即阻断，不可降级
- 其余服务：失败不阻塞（DLQ + 告警），降级而非崩溃

> 5 大服务定义与域归属见 depgraph + b_track yaml，不在本文档重复。LSG 详细设计见 [security_principles.md](security_principles.md)。

---

## §4 幂等性铁律（永恒，含量化红线）

**所有写操作 MUST 支持幂等重试。**

- **HO-4 订单提交**（Portfolio → Broker）：幂等设计 + broker ACK 回执持久化——**订单重发重复是量化红线**
- Idempotency Key 命中率作为 SLO-3 的 SLI

---

## §5 回滚设计（永恒双轨 Checkpoint）

| 轨道 | 用途 |
|------|------|
| **git commit** | 代码与文档回滚 |
| **DB dump** | 数据回滚（dump 格式见 `technology_landscape.yaml`）|

---

## §6 运行时三平面正交视图（永恒框架）

三平面横切所有域，**不改变域的业务决策**——同一域可同时包含 Hot/Warm/Cold 组件。

| 平面 | 延迟范围 | 用途 |
|------|---------|------|
| **Hot** | < 10ms | 实时关键路径（订单提交、风控检查） |
| **Warm** | 10ms - 1s | 准实时（信号生成、组合优化） |
| **Cold** | > 1s | 离线（回测、归因、报告） |

> 详细平面映射见 [runtime_planes_principles.md](runtime_planes_principles.md)。

---

> **文档维护原则**：本文档只包含永恒约束。任何随 depgraph 演进、域数量变化、节点统计更新的内容，均不应写入本文档。
