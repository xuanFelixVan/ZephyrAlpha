---
module_id: VIEW-04PRINC-GOVERNANCE
title: Architecture Principles — Governance / 架构原则：治理
doc_type: architecture_view
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
language: zh
created_by: human_plus_agent
valid_from: 2026-07-30
superseded_by: null
supersedes: VIEW-09-GOVERNANCE-ARCH
tags:
- governance-principles
- three-layer
- policy
- factory
- runtime
- ai-autonomy
- ssot-validator
summary: 治理架构永恒原则精简版。仅保留三层治理边界（Policy/Factory/Runtime）、D2-B 三角闭环、四档执行约定、D3-B AI 自治预留原则、D4 激活触发条件、Runtime Plane 边界铁律。派生数据（46 治理系统归属/激活 Sprint/物理路径）在 governance_systems_registry.yaml + depgraph。
date: '2026-07-30'
ttl: permanent
---

# 架构原则：治理（Governance Principles）

> 精简版 v2.0（2026-07-30）：保留三层模型 + D2-B 闭环 + 四档执行 + D3-B 预留 + D4 激活 + Runtime Plane 边界铁律。删除物理位置清单（depgraph 有）、视图边界重复节、已删文档引用。

---

## §1 三层治理边界（Policy / Factory / Runtime）

治理三层**横切整个系统的所有域**，与业务域是**平级正交**的"尺子 + 纪委 + 审计处"。

| 层 | 大白话 | 职责 | 典型产物 |
|---|---|---|---|
| **Policy 层** | 规章制度部门 | 定规则/存规则/版本化/append-only review | Markdown 规则、KB 决策记录、规则 DSL |
| **Factory 层** | 纪委工具组 | 把规则编译成可执行检查器 + 工具链管理 | linter/type-checker 配置、fitness function、arch_guard |
| **Runtime 层** | 巡查队+审计处 | 拦截+审计+反馈回写 Policy | pre-commit、CI、Policy-as-Code sidecar、audit-log |

**三层关键理解**：
- 治理三层与业务层是**平级正交**的横切关系（不是"上下层"）
- 治理三层**管所有层**，包括治理层自己（自治）
- Policy → Factory → Runtime → 审计回写 Policy 构成**三角闭环**（D2-B）

> 三层物理位置由 depgraph 维护，不在本文档硬编码。

---

## §2 D2-B 三角闭环

**拍板**：**Policy → Factory → Runtime → 审计回写 Policy**（带反馈环）

### 2.1 四条核心接口

| 接口 | 触发时机 | 协议 |
|---|---|---|
| **① Policy→Factory** | Policy 规则新增/变更（git commit） | policy_compiler：Markdown/YAML → 检查器配置 |
| **② Factory→Runtime** | git commit / CI push / 交易执行 / AI 决策 | pre-commit hook / CI workflow / 函数调用 |
| **③ Runtime→Audit** | 每次检查器执行后 | append-only 写入审计 ledger |
| **④ Audit→Policy** | 定期（周/月）+ 事件驱动 | 聚合审计反馈 → PR 提案 |

### 2.2 四档执行约定

| 档位 | 行为 | 使用场景 |
|---|---|---|
| **deny** | 直接拒绝 | L3 三件套 / 量化红线 / OCP 冻结 |
| **dryrun** | 仅记录不拦截 | 新规则过渡期（7-14 天观察） |
| **warn** | 警告但放行 | 非强制规则 / 建议项 |
| **disabled** | 临时关闭 | 紧急场景 / 故障诊断 |

**档位升级路径**：dryrun（7-14d）→ warn（7d）→ deny → 紧急时降 disabled → retrospective 决定回滚。

---

## §3 D3-B AI 自治预留（只预留不实施）

**拍板**：**三层都预留 AI 员工口子**（Policy 花名册 + Factory 命名空间 + Runtime 审计 schema）

| 层 | 口子类型 |
|---|---|
| **Policy** | AI 员工花名册 / AI 行为规则 / AI 决策记录模板 |
| **Factory** | AI Operator 命名空间 / 接口协议 / 脱敏规则编译器 |
| **Runtime** | AI 决策日志 schema + ledger / AI 行为审计 / 防泄密运行态 |

**预留原则**：只预留不实施——只定义命名规则 + 路径规则 + 接口名。不建目录、不写代码、不激活系统。激活时机由 §4 T3 触发。

> 具体组件命名见 `architecture_model/governance_systems_registry.yaml` 的 `ai_employee_openings`。

---

## §4 D4 激活路径（方案 B 稳健分三轮）

**拍板**：**OQ-026 方案 B 稳健分三轮激活**（先激活发布守卫，然后施工，最后业务）

| 轮次 | 激活内容 |
|---|---|
| 第一轮 | L3 三件套 + L4 架构守卫 |
| 第二轮 | AI Safety 三件套 + L5 OCP 契约冻结 |
| 第三轮 | L6 Policy-as-Code |
| **T4** | L7 SBOM（真实资金/外部审计）|

### T0-T7 激活触发条件

| 触发条件 | 触发后的动作 |
|---|---|
| **T0** scaffold 基础奠基完成 | **SSoT Validator 激活**（KBG-0021）：阻塞 experimental 下游任务直至全库一致性 100% 通过 |
| **T1** 真实资金接入 | L7 SBOM + SEC/OPS 从 skeleton→active |
| **T2** 多人协作 | VIB-01 升级 + B-01 GRB 激活 |
| **T3** AI 自治升格 | D3-B 口子从"预留"→"实施" + VIB-14 激活 |
| **T4** 外部审计合规 | L7 SBOM + SEC/OPS 实质化 |
| **T5** F 函数达阈值 | F 函数进 CI Gate |
| **T6** 用户主动激活 | 按需激活对应子系统 |
| **T7** 5 大核心服务达成熟度阈值 | LSG + Sandbox + Scanner 红队评估通过 → 允许接入外部协作 |

> 具体 Sprint 编号与阈值见 `architecture_model/governance_systems_registry.yaml`。

---

## §5 Runtime Plane 边界铁律（关键澄清）

**问题**：治理三层叫 Policy / Factory / **Runtime**，执行三平面叫 Hot / Warm / **Cold**，经常被误解为"Runtime 平面 = GOV Runtime 层"。**这是错误的**。

| 维度 | 治理 Runtime 层 | 执行 Runtime Plane（Hot/Warm/Cold）|
|---|---|---|
| **切片维度** | 治理维度（谁管规则）| 执行维度（代码何时以什么延迟跑）|
| **切片方式** | 按规则生命周期切 | 按延迟预算 + 技术栈切 |
| **所有 Plane 都有治理 Runtime？** | — | **是**（各 Plane 均有对应的治理拦截点）|
| **Policy 层的 Plane？** | — | **无**（规则文本不执行）|
| **Factory 层的 Plane？** | — | **Cold**（linter/编译器在构建期批量执行）|

**命名约束铁律**：**在任何文档中禁止单独使用 "Runtime" 一词**——必须带限定词：
- ✅ **Runtime Plane** = 运行平面（执行维度）
- ✅ **Governance Runtime Layer** = 治理 Runtime 层（治理维度）
- ❌ **Runtime**（单独）= 歧义

---

> **文档维护原则**：本文档只包含永恒治理原则。任何随治理系统激活、Sprint 演进变化的内容，均不应写入本文档。
