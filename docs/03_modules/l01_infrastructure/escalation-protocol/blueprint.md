---
module_id: "MOD-INF-022"
title: "升级/委托协议蓝图 — 规则驱动升级 + 自动委托"
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
summary: "ZephyrAlpha 升级/委托协议蓝图——规则驱动的自动升级（非人工审批）+ 自动委托（按能力匹配）。三级升级（自主→auto_guard→blocked）+ 委托协议（Agent→Agent 任务交接）。对标 Anthropic ask-before-act 自动化版 + Rasa escalation rules。"
tags: [escalation, delegation, human-in-the-loop, approval, governance, infrastructure]
priority: P1
depends_on:
  - {target: "MOD-INF-018", at: "§2.1", why: "Agent RBAC——升级级别与权限级别对齐"}
  - {target: "MOD-INF-007", at: "§2", why: "Gate Engine——升级触发器与门禁的集成"}
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——升级/委托决策写入审计"}
---

# 升级/委托协议蓝图 — 规则驱动升级 + 自动委托

> **module_id**: MOD-INF-022 | **version**: 0.2.0 | **status**: draft | **layer**: cross_layer

> **对标**：Anthropic ask-before-act（自动化版——规则驱动而非人工驱动）+ Rasa escalation rules + Terraform auto-apply（失败自动升级处理策略）。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-022 |
| 代码落位 | `src/zephyr/escalation/` |
| 运行时平面 | Warm memory（任务执行中实时判定） |
| 核心职责 | 规则驱动的自动升级 + 按能力自动委托——能自动绝不人工 |

### 1.2 核心职能（一句话）

**Escalation Protocol 是 AI 的"请示制度"——但请示对象是规则引擎，不是人类。** 升级由规则自动判定，委托由能力自动匹配，人类只在 blocked 场景下介入。

### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 1 人 + AI，99% AI 维护 | 升级不能依赖人工审批——规则驱动自动升级 |
| 10+ 并发对话 | 升级判定必须实时且无阻塞 |
| 多 IDE 并发 | 委托协议必须跨 IDE 统一 |

---

## 2. 核心架构

### 2.1 三级升级策略（决策 D-022-01）

> **决策 D-022-01**：升级级别与 MOD-INF-018 权限级别对齐——自主(always_allow) → auto_guard → blocked。取消 needs_approval 人工审批层。升级由规则引擎自动判定，不依赖人类。
>
> **决策依据**：与 MOD-INF-018 三层权限 95/4/1 分布一致。人工审批是最稀缺资源，升级判定应该是规则驱动的自动决策。

```yaml
escalation_levels:
  level_1_autonomous:
    permission: "always_allow"
    description: "AI 自主决策——95%的操作"
    rule: "操作在 Agent 能力矩阵内 + 不涉及 blocked 资源"
    action: "直接执行"

  level_2_auto_guard:
    permission: "auto_guard"
    description: "先干后验——4%的操作"
    rule: "操作涉及架构 YAML / 批量修改 / 接口契约变更"
    action: "AI 先执行 → 自动护栏后验 → 失败自动回滚"

  level_3_blocked:
    permission: "blocked"
    description: "绝对禁止——1%的操作"
    rule: "操作不可逆 / 涉及安全敏感内容 / 熔断器 OPEN"
    action: "硬阻断 + 审计告警 + 通知 Owner（异步）"
```

### 2.2 自动委托协议（决策 D-022-02）

> **决策 D-022-02**：委托由能力自动匹配，不依赖人工指定。当 Agent 不具备某项能力时，自动委托给具备该能力的 Skill Pack（架构师/实现者/治理员）。
>
> **决策依据**：1人+AI场景，委托应该是自动的能力匹配，不是人工的任务分配。对标 K8s scheduler 自动调度。

```yaml
delegation_rules:
  capability_mismatch:
    trigger: "当前 Skill Pack 不覆盖所需能力"
    action: "自动切换到覆盖该能力的 Skill Pack"
    example: "实现者 Skill Pack 遇到架构设计任务 → 自动委托给架构师 Skill Pack"

  capacity_exceeded:
    trigger: "当前对话 token 预算超限"
    action: "将剩余子任务委托给新对话"
    example: "对话 token > 6000 → 将未完成子任务写入任务卡 → 新对话接续"

  specialist_required:
    trigger: "任务涉及安全/合规/审计"
    action: "自动委托给治理员 Skill Pack"
    example: "代码修改涉及 LLM Security → 自动委托治理员 Skill Pack 评估"
```

### 2.3 升级规则引擎

```yaml
# escalation_rules.yaml —— 规则 SSoT
rules:
  - id: "ESC-001"
    condition: "修改文件数 >= 5"
    escalate_to: "auto_guard"
    guard_checks: ["drift_detector", "schema_validation"]

  - id: "ESC-002"
    condition: "修改 architecture-model/ 下 YAML"
    escalate_to: "auto_guard"
    guard_checks: ["yaml_syntax", "cross_layer_contract"]

  - id: "ESC-003"
    condition: "删除 ttl:permanent 文件"
    escalate_to: "blocked"
    reason: "不可逆操作"

  - id: "ESC-004"
    condition: "熔断器 OPEN"
    escalate_to: "blocked"
    reason: "系统熔断状态"

  - id: "ESC-005"
    condition: "auto_guard 后验失败 3 次"
    escalate_to: "blocked"
    reason: "持续失败需人工介入"
```

---

## 3. 文件组成

| 文件 | 职责 |
|------|------|
| `escalation_engine.py` | 升级引擎——规则驱动的自动升级判定 |
| `delegation_manager.py` | 委托管理——按能力自动匹配 Skill Pack |
| `escalation_rules.yaml` | 升级规则 SSoT——条件→升级级别映射 |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | 升级规则引擎 + escalation_rules.yaml + 自动委托 | 📋 Backlog |
| experimental | 与 RBAC/Gate Engine 集成 + 审计闭环 | 📋 Backlog |
| beta | 升级模式分析 + 规则自动优化 | 📋 Backlog |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-022-01 | 三级升级与权限对齐，取消人工审批层 | 2026-05-05 | 与 MOD-INF-018 三层权限一致，人工审批不可行 |
| D-022-02 | 委托由能力自动匹配，不依赖人工指定 | 2026-05-05 | 1人+AI，委托应该是自动调度 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.2.0 | 两项决策写入：D-022-01 规则驱动升级 + D-022-02 自动委托；取消人工审批层 |
| 2026-05-05 | 0.1.0 | 初始创建——三级升级策略 + 委托协议 + 审批流 |
