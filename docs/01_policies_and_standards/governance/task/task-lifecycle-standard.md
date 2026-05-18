---
module_id: GOV-TASK-004
title: "任务生命周期治理标准"
doc_type: standard
status: active
version: "2.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "定义任务生命周期的治理规则：取消权限、优先级裁决、优先级变更权限、P0 通胀保护、超时豁免、升级治理。施工细节（状态机、门禁、超时检测）已迁移至 03_modules/l01_infrastructure/task-system/blueprint.md（MOD-INF-006）§5.2-§5.5。"
tags: [task, lifecycle, priority, escalation, governance, cancellation, authority]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§7", why: "metadata-registry.md §7 定义的任务卡字段 schema 为优先级和状态枚举的 SSoT"}
ai_autonomy: immutable_core
---

# 任务生命周期治理标准

> GOV-TASK-004 | v2.0.0 | 治理决策规则（状态机/门禁/超时 → `task-system/blueprint.md` §5.2-§5.5）

## 1. 目的与范围

任务生命周期的关键决策点权限边界和治理策略。

| 问题 | 本标准回答 |
|------|-----------|
| 谁有权取消？ | P0/P1 → Owner；P2-P4 → AI 可自主（须记录原因） |
| 冲突时谁优先？ | P0>P1>P2>P3>P4 → safety_level H>M>L → created_at 先到先得 |
| 谁可以改优先级？ | 升级 → AI 提议 Owner 审批；降级 → Owner 独占 |
| P0 太多怎么办？ | ≥3 黄色警戒；≥5 红色冻结 |
| 何时必须升级？ | P0 BLOCKED>2session / 任何 BLOCKED>5session / P0 FAILED×2 |

**适用**：SQLite `tasks` 表所有任务 + AI 执行任务决策权限 + 手动任务权限流程。

**不在此范围**：

| 内容 | 去这里找 |
|------|---------|
| 10 状态机转换规则 | `task-system/blueprint.md` §5.2 |
| G0-G6 门禁检查项 | `task-system/blueprint.md` §5.3 |
| 超时检测实现 | `task-system/blueprint.md` §5.4 |
| 任务卡字段定义 | `task-card-standard.md` |
| 任务关闭验证 | `task-closure-standard.md` |

---

## 2. 治理规则

### 2.1 取消权限

**取消路径**：只能从"未完成"状态发起取消（PENDING / FAILED / BLOCKED / WAITING / READY）。终态（VERIFIED / CANCELLED）不可取消——如需返工，创建新任务。

| 优先级 | 谁可以取消 | 条件 |
|--------|-----------|------|
| P0 / P1 | Owner 审批 | AI 不得单方面取消 |
| P2 / P3 | AI 可自主取消 | 必须在 Session Log 中记录取消原因 |
| P4 | AI 可自主取消 | 需在 Session Log 记录原因 |

---

### 2.2 优先级定义

| 优先级 | 定义 | 典型场景 |
|--------|------|---------|
| P0 | **阻断级** — 系统不可用、数据不可逆损坏、主线阻塞无 workaround | 构建失败、规则冲突导致 AI 无法施工 |
| P1 | **紧急** — 核心功能受阻但存在 workaround，影响多个消费者 | 关键功能退化、正则退化 |
| P2 | **重要** — 单一消费者阻塞或"埋雷"任务（延期做会变成架构重构） | 技术债务清理、SSoT 拆分 |
| P3 | **常规** — 正常开发和治理任务 | 新功能开发、文档更新 |
| P4 | **低优** — 锦上添花的改进、实验性探索 | 美化、重构非关键模块 |

> **SSoT 声明**：优先级字段的枚举值定义以 `metadata-registry.md` §7 中 `priority` 字段为准。本表是对各优先级的语义说明，不是字段定义。

---

### 2.3 优先级裁决规则

当多个任务竞争同一资源（同一 AI session、同一文件）时，按以下顺序裁决：

1. **按优先级排序**：P0 > P1 > P2 > P3 > P4
2. **同优先级按 safety_level 排序**：H > M > L
3. **同优先级同 safety_level 按创建时间排序**：先到先得（created_at 更早的优先）
4. **Owner 有最终裁定权**：任何自动裁决结果都可以被 Owner 推翻

---

### 2.4 优先级变更权限

| 变更方向 | 谁可以发起 | 审批要求 |
|---------|-----------|---------|
| 升级（P3→P2→P1→P0） | AI 可提议 | **Owner 审批后方生效** |
| 降级（P0→P1→P2→P3→P4） | Owner 独占 | Owner 决定即可 |
| 超时自动降级 | 系统自动 | 无需审批，但需记录在 Session Log |

> **拒绝后冷却期**：AI 的升级提议被 Owner 拒绝后，48h 内不得就同一任务再次提出升级。避免 AI 高频骚扰 Owner。

---

### 2.5 P0 通胀保护

| 阈值 | 触发条件 | 动作 |
|------|---------|------|
| 黄色警戒 | 当前离线 P0 任务 ≥ **3** 个 | 后续 P0 升级提案必须附带"为什么必须 P0 而非 P1 / 能不能拆成 P1+P2"的论证段落 |
| 红色冻结 | 当前离线 P0 任务 ≥ **5** 个 | **冻结新增 P0**——AI 不得提议升级，系统不接受新 P0 创建。仅 Owner 可以手动解除冻结 |

> **冻结解除后的冷却期**：Owner 解除 P0 冻结后，48h 内不得再次触发 P0 冻结（防止 Owner 刚解冻又被 AI 瞬间触发）。

---

### 2.6 超时豁免治理

以下情况可以豁免超时规则（不触发自动降级或升级）：

- Owner 明确标注"长期阻塞"的任务（在 tags 中添加 `exempt:timeout`）
- 依赖外部第三方（如监管审批）的任务——在 `blocked_reason` 中注明"外部依赖"

---

### 2.7 升级治理

以下场景 AI **必须**升级到 Owner，**不得跳过升级直接做决策**：

| 触发条件 | 升级动作 |
|---------|---------|
| P0 任务 BLOCKED 超过 2 个 session | Session Log 中标记 `escalation:owner` |
| 任何任务 BLOCKED 超过 5 个 session | Session Log 中标记 `escalation:owner` |
| P0 任务 FAILED 2 次 | 等待 Owner 决定：创建替代任务 / 降级 |
| 优先级冲突无法自动裁决 | 等待 Owner 裁定 |

升级通知通过 Session Log 的 `open_questions` 字段传递给 Owner。

**Owner 收到升级后的决策选项**：

| 选项 | 动作 | 后续 |
|------|------|------|
| ① 降优先级 | 将任务降为 P3/P4 | 任务按新优先级重新排队 |
| ② 给 Deadline | 在 open_questions 中回复截止时间 | AI 以 deadline 重排优先级 |
| ③ 取消任务 | 状态 → CANCELLED | 释放所有依赖它的任务 |
| ④ 不变 | 确认当前优先级合理 | AI 继续按原优先级执行 |

---

## 3. 与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| [task-card-standard.md](../../governance/task/task-card-standard.md) | 本标准不定义任务卡怎么写——那是 task-card-standard 的职责。本标准定义"任务写好后怎么被治理" |
| [handoff-protocol.md](../../governance/ai/handoff-protocol.md) | 交接是跨 session 的上下文传递。升级通知通过交接协议的 open_questions 传递给 Owner |
| [metadata-registry.md](../../meta/metadata-registry.md) §7 | 优先级和状态的枚举值 SSoT。本标准引用但不重新定义 |
| [task-closure-standard.md](../../governance/task/task-closure-standard.md) | 关闭是生命周期的终点。本标准定义"谁有权关闭"，关闭标准定义"关闭前要检查什么" |
| [03_modules/l01_infrastructure/task-system/blueprint.md](../../../03_modules/l01_infrastructure/task-system/blueprint.md) §5.2-§5.5 | 施工细节——状态机实现、门禁检查逻辑、超时检测代码、消费者同步规则 |

---
