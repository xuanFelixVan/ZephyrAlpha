---
module_id: "MOD-INF-021"
title: "回滚/撤销系统蓝图 — Git-native Checkpoint + 自动回滚"
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
summary: "ZephyrAlpha 回滚/撤销系统蓝图——git commit 为天然 checkpoint + auto_guard 后验失败自动触发回滚 + 回滚后仅跑 G0 门禁验证。对标 K8s Rollout Undo + Terraform auto-apply rollback + Claude Code git-based rollback。与现有 rollback_manager.py 集成升级。"
tags: [rollback, undo, checkpoint, recovery, git-native, infrastructure]
priority: P1
depends_on:
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——回滚操作写入审计日志"}
  - {target: "MOD-INF-018", at: "§2.2", why: "Agent RBAC——auto_guard 后验失败触发自动回滚"}
  - {target: "MOD-INF-007", at: "§2.3", why: "Gate Engine——回滚后跑 G0 门禁验证"}
---

# 回滚/撤销系统蓝图 — Git-native Checkpoint + 自动回滚

> **module_id**: MOD-INF-021 | **version**: 0.2.0 | **status**: draft | **layer**: cross_layer

> **对标**：K8s Rollout Undo + Terraform auto-apply rollback（plan 失败自动回滚）+ Anthropic Claude Code git-based rollback。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-021 |
| 代码落位 | `src/zephyr/rollback/` |
| 运行时平面 | Hot memory（回滚操作 < 1s） |
| 核心职责 | auto_guard 后验失败时自动回滚到上一个 git commit |

### 1.2 核心职能（一句话）

**Rollback System 是系统的安全网**——auto_guard 后验失败时自动 `git revert`，回滚后跑 G0 门禁确认安全。零人工介入。

### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 10+ 并发对话 | 回滚不能阻塞其他对话——每个对话独立回滚 |
| 1 人 + AI | 回滚必须自动触发，不能等 Owner 确认 |
| 先干后验模式 | 回滚是 auto_guard 后验失败的自动补救——不是人工操作 |
| 多 IDE 并发 | 回滚基于 git——git 是跨 IDE 统一的状态管理 |

### 1.4 当前痛点

| # | 痛点 | 后果 |
|---|------|------|
| 1 | rollback_manager.py 存在但无完整策略 | 只有骨架，没有自动触发/验证链路 |
| 2 | 没有 checkpoint 机制 | 不知道该回滚到哪个状态 |
| 3 | 回滚后不验证 | 回滚可能引入新问题 |
| 4 | 回滚需要人工触发 | Owner 不在场时问题持续 |

---

## 2. 核心架构

### 2.1 Git Commit 为天然 Checkpoint（决策 D-021-01）

> **决策 D-021-01**：git commit 是天然 checkpoint，不需要额外的快照机制。每次 AI 改代码 → git commit → pre-commit 检查，git commit 本身就是回滚点。回滚 = `git revert` 或 `git reset`。
>
> **决策依据**：工作流已经是 AI 改代码 → git commit → pre-commit 检查。额外 checkpoint 机制是重复投资。git 是跨 IDE 统一的状态管理，天然支持回滚。对标 Claude Code git-based rollback。

```yaml
checkpoint_strategy:
  mechanism: "git commit = 天然 checkpoint"
  no_extra_snapshot: true
  benefit: "零额外开销 + 跨 IDE 统一 + 历史可追溯"

  rollback_methods:
    single_commit:
      command: "git revert {commit_sha}"
      description: "回滚单个 commit——安全，产生新 commit"
      use_when: "auto_guard 后验失败"

    multi_commit:
      command: "git revert {commit_sha1}..{commit_sha2}"
      description: "回滚多个 commit——任务级回滚"
      use_when: "任务 G7 门禁 FAIL 且修复 3 次仍失败"

    hard_reset:
      command: "git reset --hard {commit_sha}"
      description: "硬重置到指定 commit——危险，仅 Owner 手动触发"
      use_when: "熔断器 OPEN 或 Owner 手动触发"
      permission: "blocked——必须 Owner 手动执行"
```

### 2.2 自动回滚触发（决策 D-021-02）

> **决策 D-021-02**：auto_guard 后验失败时自动触发回滚，无需 Owner 确认。回滚操作写入审计日志。Owner 事后异步审阅。
>
> **决策依据**：与 MOD-INF-018 先干后验模式一致。10+ 并发对话不可能等 Owner 确认。自动回滚 + 审计日志 = 安全且高效。

```yaml
auto_rollback_flow:
  trigger: "auto_guard 后验失败（pre-commit FAIL / CI FAIL / drift 检测 FAIL）"

  step_1_detect:
    who: "auto_guard 护栏"
    what: "检测到后验失败"
    output: "失败原因 + 受影响的 commit"

  step_2_rollback:
    who: "Rollback Executor"
    what: "自动执行 git revert"
    command: "git revert --no-edit {commit_sha}"
    note: "不等待人类确认"

  step_3_verify:
    who: "Rollback Verifier"
    what: "回滚后跑 G0 门禁验证"
    detail: "仅 G0（文件存在性 + YAML 语法），不跑全量门禁"

  step_4_audit:
    who: "Audit Trail (MOD-INF-020)"
    what: "回滚操作写入审计日志（ProvenanceStandard 级别）"

  step_5_notify:
    who: "通知系统"
    what: "异步通知 Owner——回滚已执行，原因：XXX"
    note: "通知是异步的，不阻塞任何操作"
```

### 2.3 回滚后仅跑 G0 门禁（决策 D-021-03）

> **决策 D-021-03**：回滚后只跑 G0 门禁（文件存在性 + YAML 语法），不跑全量门禁（G1-G7）。回滚是紧急操作，不能因为 G7（集成测试）失败而卡住。全量门禁留给下一次正常 commit。
>
> **决策依据**：回滚的目的是恢复到已知安全状态，不是做全量验证。上一次成功 commit 已经通过了全量门禁，回滚到那个 commit 理论上是安全的。G0 门禁足以确认文件完整性。

```yaml
post_rollback_verification:
  gate_level: "G0 only"
  checks:
    - "文件存在性——回滚后的文件是否都在"
    - "YAML 语法——关键 YAML 文件是否可解析"
    - "import 可达性——Python 文件是否可 import"
  skip:
    - "G1-G7 门禁——留给下一次正常 commit"
    - "pytest——留给下一次正常 commit"
    - "ruff——留给下一次正常 commit"
  rationale: "回滚到上一次成功 commit = 恢复到已验证状态，G0 足以确认完整性"
```

### 2.4 回滚策略矩阵

```yaml
rollback_strategies:
  auto_guard_failure:
    trigger: "auto_guard 后验失败"
    method: "git revert --no-edit {commit_sha}"
    verification: "G0 门禁"
    permission: "自动——无需 Owner"
    audit_level: "ProvenanceStandard"

  task_failure:
    trigger: "任务 G7 门禁 FAIL 且修复 3 次仍失败"
    method: "git revert {commit_sha1}..{commit_sha2}"
    verification: "G0 门禁"
    permission: "自动——无需 Owner"
    audit_level: "ProvenanceStandard"

  manual_rollback:
    trigger: "Owner 手动触发"
    method: "git reset --hard {commit_sha}（危险）"
    verification: "G0-G7 全量门禁"
    permission: "blocked——必须 Owner 手动执行"
    audit_level: "ProvenanceFull"
```

---

## 3. 文件组成

| 文件 | 职责 |
|------|------|
| `rollback_executor.py` | 回滚执行器——git revert / git reset 封装 |
| `rollback_verifier.py` | 回滚验证器——G0 门禁验证 |
| `auto_rollback_trigger.py` | 自动回滚触发器——监听 auto_guard 后验结果 |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | RollbackExecutor（git revert 封装）+ G0 验证 + 自动触发器 | 📋 Backlog |
| experimental | 任务级回滚 + 与 auto_guard 集成 + 审计闭环 | 📋 Backlog |
| beta | 回滚仪表盘 + 回滚频率统计 + 回滚模式分析 | 📋 Backlog |

---

## 5. 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | git revert 冲突——回滚的 commit 与后续 commit 有冲突 | 中 | 高 | 回滚失败时写入审计告警 + 通知 Owner 手动处理 |
| R2 | 频繁自动回滚——auto_guard 后验失败率高 | 中 | 中 | 统计回滚频率，持续优化 auto_guard 规则 |
| R3 | 多 IDE 并发回滚——两个对话同时回滚同一文件 | 低 | 高 | git revert 是原子操作，冲突时第二个 revert 会失败并告警 |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-021-01 | git commit 为天然 checkpoint，不额外创建快照 | 2026-05-05 | 工作流已是 git commit → pre-commit，额外快照是重复投资 |
| D-021-02 | auto_guard 后验失败自动回滚，无需 Owner 确认 | 2026-05-05 | 与先干后验模式一致，10+ 并发不可能等确认 |
| D-021-03 | 回滚后仅跑 G0 门禁，不跑全量 | 2026-05-05 | 回滚是紧急操作，全量门禁留给下一次正常 commit |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.2.0 | 三项决策写入：D-021-01 git-native checkpoint + D-021-02 自动回滚 + D-021-03 G0验证；重构为 git-native 模型 |
| 2026-05-05 | 0.1.0 | 初始创建——Checkpoint 模型 + 三级回滚策略 + 验证器 |
