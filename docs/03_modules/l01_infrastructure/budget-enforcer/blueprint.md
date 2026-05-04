---
module_id: "MOD-INF-024"
title: "Token/Cost 预算强制执行蓝图 — 自动降级 + 成本审计"
doc_type: blueprint
status: draft
version: "0.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: not_started
summary: "ZephyrAlpha Token/Cost 预算强制执行蓝图——将 token 追踪升级为自动降级执行。三级预算（会话/任务/全局）+ 四级降级（警告→压缩→最小→停止）+ 成本审计。对标 Anthropic cache-aware token management + ISACA cost governance。"
tags: [budget, token, cost, enforcement, degradation, infrastructure]
priority: P2
depends_on:
  - {target: "MOD-INF-008", at: "§2", why: "Context Engine——token 预算分配的消费者 + 上下文压缩"}
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——预算超限事件写入审计"}
  - {target: "MOD-INF-022", at: "§2", why: "Escalation——预算超限触发升级"}
---

# Token/Cost 预算强制执行蓝图 — 自动降级

> **module_id**: MOD-INF-024 | **version**: 0.2.0 | **status**: draft | **layer**: cross_layer

> **对标**：Anthropic cache-aware token management + ISACA cost governance + Context Engine token_budget 的运行时执行层。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-024 |
| 代码落位 | `src/zephyr/budget_enforcer/` |
| 运行时平面 | Hot memory（每次 API 调用前检查） |
| 核心职责 | 强制执行 Token/Cost 预算——超预算自动降级，零人工介入 |

### 1.2 核心职能（一句话）

**Budget Enforcer 是系统的财务总监**——AI 不能无限消耗 token，超预算自动降级。全程自动，不需要 Owner 介入。

---

## 2. 核心架构

### 2.1 三级预算体系

```yaml
budget_levels:
  session_level:
    description: "单次会话预算"
    default: 8000
    hard_limit: 12000
    action_on_exceed: "降级到最小上下文"

  task_level:
    description: "单任务预算"
    default: 4000
    hard_limit: 6000
    action_on_exceed: "暂停任务 + 委托给新对话"

  global_level:
    description: "全局日预算"
    default: 100000
    hard_limit: 150000
    action_on_exceed: "全局只读模式"
```

### 2.2 四级自动降级（决策 D-024-01）

> **决策 D-024-01**：降级全程自动，不需要 Owner 介入。四级降级：警告→压缩→最小→停止。每级自动触发，无需审批。
>
> **决策依据**：与先干后验模式一致。预算超限是技术问题，不是审批问题。自动降级比人工干预更及时。

```yaml
degradation_strategy:
  level_1_warning:
    trigger: "预算使用 > 70%"
    action: "WARNING 日志 + 建议减少上下文"
    auto: true

  level_2_compress:
    trigger: "预算使用 > 85%"
    action: "强制压缩上下文——DocCompressor aggressive 模式"
    auto: true
    integration: "Context Engine (MOD-INF-008)"

  level_3_minimal:
    trigger: "预算使用 > 95%"
    action: "最小上下文——仅保留 AGENTS.md + 当前蓝图 §3"
    auto: true

  level_4_halt:
    trigger: "预算使用 > 100%"
    action: "硬停止——仅允许只读操作 + 审计告警"
    auto: true
    audit_level: "ProvenanceStandard"
```

### 2.3 成本审计

```yaml
cost_audit:
  storage: "JSONL——data/audit/cost-audit.jsonl"
  fields:
    - "timestamp"
    - "session_id"
    - "task_id"
    - "tokens_used"
    - "budget_level"
    - "degradation_action"
  purpose: "Owner 异步审阅成本趋势 + 优化预算配置"
```

---

## 3. 文件组成

| 文件 | 职责 |
|------|------|
| `budget_tracker.py` | 预算追踪器——实时 token 消耗统计 |
| `budget_enforcer.py` | 预算执行器——超预算触发自动降级 |
| `degradation_manager.py` | 降级管理器——按策略执行上下文压缩 |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | BudgetTracker + 三级预算配置 + 四级降级 | 📋 Backlog |
| experimental | 与 Context Engine 集成 + 成本审计 | 📋 Backlog |
| beta | 成本仪表盘 + 预算预测 + 多模型成本对比 | 📋 Backlog |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-024-01 | 四级自动降级，不需要 Owner 介入 | 2026-05-05 | 预算超限是技术问题不是审批问题，自动降级更及时 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.2.0 | 决策写入：D-024-01 四级自动降级；成本审计改为 JSONL |
| 2026-05-05 | 0.1.0 | 初始创建——三级预算体系 + 降级策略 + 预算执行器 |
