---
module_id: "DOM-GOV-001"
title: "治理域集成蓝图 — Agent 治理八件套跨模块集成契约"
doc_type: blueprint
status: Draft
version: "0.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-06"
ttl: permanent
construction_progress: not_started
belongs_to: "SYS-MASTER-001"
summary: "ZephyrAlpha 治理域 Level 1 集成蓝图——覆盖 Agent 治理八件套（MOD-INF-018~025）之间的跨模块集成契约。定义 RBAC→Audit→Rollback→Escalation→Drift→Budget→A2A→Agent Spec 之间的数据流、事件流、集成顺序。本蓝图是金字塔 Level 1 体系中的第二个域蓝图（继 MOD-MASTER-001 基建域之后）。触发条件：PS-STD-005 §3.3（域内模块≥5且≥3组跨模块交互——治理域满足：8模块，13+组交互）。"
tags: [domain-blueprint, governance, level-1, agent-rbac, audit-trail, rollback, escalation, drift-detector, budget-enforcer, a2a-protocol, agent-spec, integration-contracts, pyramid-structure]
priority: P0
depends_on:
  - {target: "SYS-MASTER-001", at: "全篇", why: "Level 0 系统总蓝图——治理域是金字塔 Level 1 节点"}
  - {target: "MOD-MASTER-001", at: "全篇", why: "基础设施域集成蓝图——治理域依赖基建域的基础能力（Database/Task System/Gate Engine/Context Engine）"}
---

## G-CT 契约下游锚点（验收）

以下模块蓝图 **MUST** 在正文前部包含「DOM-GOV-001 集成契约锚点」表，列出本模块作为 **G-CT-*** 的消费方或产出方：**MOD-INF-018、019、020、021、022、023、024、025**。

| module_id | 已锚定 |
|-----------|--------|
| MOD-INF-018 | 是 |
| MOD-INF-019 | 是 |
| MOD-INF-020 | 是 |
| MOD-INF-021 | 是 |
| MOD-INF-022 | 是 |
| MOD-INF-023 | 是 |
| MOD-INF-024 | 是 |
| MOD-INF-025 | 是 |

# 治理域集成蓝图 — Agent 治理八件套

> **module_id**: DOM-GOV-001 | **Level**: 1 (域集成蓝图)
>
> 本蓝图是 ZephyrAlpha 金字塔体系中的 **Level 1 治理域集成蓝图**。
> 覆盖模块：MOD-INF-018 (RBAC) / 019 (Spec) / 020 (Audit) / 021 (Rollback) / 022 (Escalation) / 023 (Drift) / 024 (Budget) / 025 (A2A)

## 1. 域定位

治理域负责 ZephyrAlpha 中所有 AI Agent 的**运行时治理**——身份验证、权限执行、操作审计、异常回滚、升级委托、漂移检测、预算控制、多Agent协调。

这8个模块在功能上紧密耦合，在实现上必须按特定顺序推进。本蓝图定义它们之间的集成契约。

## 2. 域内模块清单

| module_id | 名称 | 优先级 | 施工进度 | 核心职责 |
|-----------|------|:---:|:---:|------|
| MOD-INF-018 | Agent RBAC | P0 | 0% | 七层纵深防御+六横切面运行时权限执行 |
| MOD-INF-019 | Agent Spec | P0 | 0% | 蓝图→可加载 Skill 升级引擎 |
| MOD-INF-020 | Audit Trail | P0 | 0% | 不可变审计追踪+密码学Provenance+Agent签名 |
| MOD-INF-021 | Rollback System | P1 | 0% | Git-native + SQLite Checkpoint 智能回滚 |
| MOD-INF-022 | Escalation Protocol | P1 | 0% | 规则驱动升级+自动委托+五层防御架构 |
| MOD-INF-023 | Drift Detector | P1 | 0% | Git-native 运行时漂移检测+自动对账 |
| MOD-INF-024 | Budget Enforcer | P2 | 0% | Token/Cost/Time 三维预算强制执行 |
| MOD-INF-025 | A2A Protocol | P2 | Hold | 多Agent通信协议+冲突仲裁（Phase 4 激活） |

## 3. 域内集成契约（G-CT-*）

### G-CT-001: RBAC → Audit 集成契约

```
方向：MOD-INF-018 (RBAC) → MOD-INF-020 (Audit)
触发时机：每次权限判定完成时
数据流：
  RBAC 产出 → Audit 写入 ← Agent Identity 注入
  - agent_id: str          ← RBAC 从 Agent Identity 获取
  - permission: str        ← RBAC 权限判定结果（allow/approve/block）
  - resource: str          ← 被访问的资源
  - decision_basis: dict   ← 判定依据（角色/策略/上下文）
  - timestamp: datetime    ← 判定时间
  - session_id: str        ← 关联会话
解决循环依赖方案：RBAC 在每次权限判定完成后主动调用 Audit.write()。
  Audit 不需要反向调用 RBAC——Audit 只记录事实，不验证权限。
  调用链：Agent → RBAC.check() → RBAC 返回 result → RBAC 调用 Audit.write(result)
  这意味着 RBAC 单向依赖 Audit。Audit 不依赖 RBAC。
```

### G-CT-002: Audit → Rollback 集成契约

```
方向：MOD-INF-020 (Audit) → MOD-INF-021 (Rollback)
触发时机：Audit 检测到异常操作签名时
数据流：Audit 的 anomaly_detector 产出异常事件 → Rollback 消费
```

### G-CT-003: Rollback → Escalation 集成契约

```
方向：MOD-INF-021 (Rollback) → MOD-INF-022 (Escalation)
触发时机：回滚失败或回滚后验证不通过（Rollback auto_guard 后验失败）
数据流：Rollback 的 rollback_result 产出 → Escalation 消费（触发人工升级）
```

### G-CT-004: Escalation → RBAC 集成契约

```
方向：MOD-INF-022 (Escalation) → MOD-INF-018 (RBAC)
触发时机：升级到人工审批时需要验证审批人权限
数据流：Escalation 的 approval_request → RBAC 验证 human_approver 的代理权限
```

### G-CT-005: Drift → Rollback 集成契约

```
方向：MOD-INF-023 (Drift) → MOD-INF-021 (Rollback)
触发时机：Drift 检测到可自动修复的漂移
数据流：Drift 的 drift_event（含 fix_suggestion）→ Rollback 执行自动修复
```

### G-CT-006: Budget → Escalation 集成契约

```
方向：MOD-INF-024 (Budget) → MOD-INF-022 (Escalation)
触发时机：预算告急（Burn Rate > 阈值 或 全局预算耗尽）
数据流：Budget 的 budget_alert → Escalation 启动升级流程
```

### G-CT-007: Spec → RBAC/Audit 集成契约

```
方向：MOD-INF-019 (Agent Spec) → MOD-INF-018 (RBAC) + MOD-INF-020 (Audit)
触发时机：Skill 加载时
数据流：Spec 的 Skill.manifest 中的 permissions 声明 → RBAC 注册权限策略
       Spec 的 Skill 执行 → Audit 记录 Skill 操作审计
```

### G-CT-008: A2A → RBAC/Escalation 集成契约

```
方向：MOD-INF-025 (A2A) → MOD-INF-018 (RBAC) + MOD-INF-022 (Escalation)
激活条件：Phase 4（A2A 从 Hold 激活时）
```

## 4. 域内施工顺序

**Phase 1（必须先建的基础）**：
1. MOD-INF-020 Audit Trail——审计是治理的基础设施，其他模块都需要写入审计
2. MOD-INF-018 Agent RBAC——权限执行是治理的核心门禁

**Phase 2（依赖 Phase 1）**：
3. MOD-INF-021 Rollback System——依赖 Audit 记录回滚操作
4. MOD-INF-022 Escalation Protocol——依赖 RBAC 验证升级权限 + Audit 记录升级

**Phase 3（依赖 Phase 2）**：
5. MOD-INF-023 Drift Detector——依赖 Rollback 执行自动修复
6. MOD-INF-024 Budget Enforcer——依赖 Escalation 处理预算告急

**Phase 4（后期激活）**：
7. MOD-INF-019 Agent Spec——依赖以上全部治理模块就绪
8. MOD-INF-025 A2A Protocol——多 Agent 场景，Phase 4 激活

## 5. 循环依赖解决裁定

**原问题**：MOD-INF-018 (RBAC) 声明依赖 MOD-INF-020 (Audit)，MOD-INF-020 (Audit) 也声明依赖 MOD-INF-018 (RBAC)——形成循环依赖。

**裁定**：
- **Audit 不依赖 RBAC**。Audit 只记录事实（谁做了什么、什么时候、什么结果）——不需要知道谁有权做。Agent Identity（agent_id）由调用方（RBAC）在调用 Audit.write() 时作为参数传入，Audit 直接使用。
- **RBAC 单向依赖 Audit**。RBAC 在权限判定完成后主动写入 Audit 记录。
- **打破循环的具体方案**：修改 MOD-INF-020 Audit Trail 蓝图的 depends_on，移除对 MOD-INF-018 的依赖。

## 6. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 八件套全部 0% 施工 | 治理域空有蓝图无法运行 | 按 Phase 1→2→3 顺序逐步激活 |
| RBAC/Audit 循环依赖误回 | 两个模块互相阻塞 | 本裁定永久解决——Audit 单向接收 RBAC 写入 |
| A2A 依赖所有其他模块 | Phase 4 才可能激活 | 明确 Hold 状态，不阻塞 Phase 1/2/3 |

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|------|
| 0.1.0 | 2026-05-06 | 初始创建——治理域 Level 1 蓝图，定义八件套集成契约和施工顺序。打破 RBAC↔Audit 循环依赖。 | 
