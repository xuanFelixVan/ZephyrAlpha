---
module_id: POL-BRANCH-STRATEGY-001
title: Branch Strategy Policy / 分支策略
doc_type: policy
ttl: permanent
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: '2026-07-07'
supersedes: null
superseded_by: null
placement_note: "定义 ZephyrAlpha 项目的 git 分支策略。消除 master vs dev 双分支幻觉源，确立单一主分支模型。承接 100% AI 开发模式的分支生命周期治理需求。"
related_rationale: []
related_open_questions: []
tags:
  - branch-strategy
  - git
  - single-main-branch
  - lifecycle
  - ai-development
summary: 定义 ZephyrAlpha git 分支策略。单一主分支模型（dev 即主分支），master 为 dev 的 FF 镜像。session/* 分支命名约定与生命周期。分支 3 个月未合并即废弃。消除双分支幻觉源。
date: '2026-07-07'
---

# Branch Strategy Policy
# 分支策略

---

## 0. 读者指南

| 章节 | 内容 | 主要读者 |
|------|------|----------|
| §1 | 策略动机：为什么需要明文分支策略 | 所有人 |
| §2 | 单一主分支模型 | 所有人 |
| §3 | 分支命名约定 | 实现者 |
| §4 | 分支生命周期 | 所有人 |
| §5 | 禁止事项 | 所有人 |

---

## 1. 策略动机

### 1.1 问题

ZephyrAlpha 是 1 人 + 100% AI 开发项目，纯本地仓库（无 remote）。历史遗留 master + dev 双分支导致：

1. **双真源幻觉**：AI 查 `git log master` 看到 3 个月前过期快照，查 `git log dev` 才是真实状态。双真源=幻觉温床。
2. **停滞累积**：AI 不会主动让 master 追随 dev，master 只会越落越多（已验证：master 曾停滞 3 个月）。
3. **命名误导**：历史分支名 `arch034-merge` 混淆了 ARCH-034 议题（模块合并）与分支合并，引导 AI 误判架构语义。
4. **悬挂分支累积**：AI 不会主动清理分支，50+ 陈旧分支制造导航噪音。

### 1.2 本策略的解决

确立明文分支策略：
- **单一主分支模型**：dev 即主分支，master 为 dev 的 FF 镜像
- **命名约定**：session/* 前缀 + 时间戳，禁止议题性分支名
- **生命周期**：3 个月未合并即废弃
- **定期对齐**：master 定期 FF 到 dev

---

## 2. 单一主分支模型

### 2.1 主分支：dev

- **dev 是唯一主开发分支**，所有提交的目标分支
- AI 对话启动后第一件事（session_worktree_start）即在 dev 上工作
- 所有 session_worktree_commit 最终 merge 到 dev

### 2.2 镜像分支：master

- **master 是 dev 的 FF 镜像**，不承载独立开发
- master 定期通过 fast-forward 追随 dev：`git branch -f master dev`
- master 的作用：保留"主干"语义标记，供外部工具/CI 引用
- **禁止**在 master 上直接 commit（所有提交必须经 dev）

### 2.3 对齐频率

- **每次重大里程碑后**：master FF 到 dev
- **至少每 2 周**：检查 master 是否滞后 dev，若滞后则 FF
- 对齐操作：`git branch -f master dev`（纯 ref 更新，不触碰工作区）

---

## 3. 分支命名约定

### 3.1 合法分支名

| 模式 | 用途 | 生命周期 |
|------|------|----------|
| `dev` | 主开发分支 | 永久 |
| `master` | dev 的 FF 镜像 | 永久 |
| `session/sess-NNNNN-YYYYMMDDHHMMSS` | session_worktree 临时分支 | 任务级（start→commit→merge→删除） |

### 3.2 非法分支名

- **禁止**议题性分支名（如 `arch034-merge`、`fix-bug-123`）：议题编号应在 commit message / 注释中引用，不在分支名中
- **禁止** `docs/blueprint-*` 前缀：蓝图由生成器自动产出，不需要分支
- **禁止** `trae-redteam-*` 前缀：红队测试结论沉淀到文档，不需要分支
- **禁止** `feature/*`、`bugfix/*` 等 Git Flow 命名：本项目不用 Git Flow

### 3.3 session 分支命名格式

```
session/sess-{5位序号}-{YYYYMMDDHHMMSS}
```

示例：`session/sess-29092-20260707174831`

- 序号由 `generate_session_id()` 自动生成
- 时间戳为 session 启动时间
- 任务完成后 merge 到 dev 并删除分支

---

## 4. 分支生命周期

### 4.1 session 分支

1. **start**：`session_worktree_start(session_id)` 创建分支
2. **commit**：`session_worktree_commit(session_id, files, message)` 提交到 worktree
3. **merge**：`session_worktree_merge(session_id)` 合并到 dev
4. **abort**（可选）：`session_worktree_abort(session_id, files)` 放弃并清理

### 4.2 废弃判定

- **session 分支**：任务完成（merge 或 abort）后立即删除
- **任意分支**：**3 个月未合并到 dev 即判定为废弃**
  - 废弃分支应删除（`git branch -D`）
  - 若分支含未吸收的有价值改动，先 cherry-pick 到 dev 再删除
  - 若无法 cherry-pick（文件结构变化），直接删除（改动已无价值）

### 4.3 清理责任

- AI 在每次会话开始时检查悬挂分支（`git branch` 列表过长时主动清理）
- 清理遵循"先报告→再执行"原则

---

## 5. 禁止事项

1. **禁止**在 master 上直接 commit
2. **禁止**长期保留未合并的 session 分支（超过 1 周应评估 merge/abort）
3. **禁止**议题性分支名（议题编号用 `#ARCH-NNN` 在 commit message 引用）
4. **禁止**裸 `git commit`（必须通过 session_worktree_commit 或 GitCommitGateway）
5. **禁止** `git push --force`（本地仓库无 remote，无此需求）
6. **禁止**保留弃用的 worktree 目录（.aidrafts/ 不入库）

---

## 附录 A：历史教训

| 事件 | 教训 |
|------|------|
| master 停滞 3 个月（2026-04~07） | 双分支模型在 100% AI 开发下无法自动维护，需明文策略 |
| arch034-merge 分支名误导 | 分支名不应引用议题编号，议题编号是永久引用标记 |
| 51 个悬挂分支累积 | AI 不会主动清理，需生命周期规则强制废弃 |
| .aidrafts/sess-26204 误入库 | session_worktree 运行时产物必须 .gitignore |

---

## 附录 B：自动化债务声明

> **架构债务登记**（2026-07-08 架构师审查裁定）

本策略文档中以下规则属于**君子协定**（依赖 AI 自觉执行，无 gate/reconciler 自动化保障），在 100% AI 开发模式下不会自发触发。与项目硬约束"永久系统必须全自动"存在张力，登记为架构债务，待后续 reconciler 落地后消除。

| 债务编号 | 规则位置 | 规则内容 | 自动化状态 | 缓解措施 |
|----------|----------|----------|------------|----------|
| DEBT-BRANCH-001 | §2.3 | 至少每 2 周检查 master 是否滞后 dev，若滞后则 FF | 君子协定，无自动触发 | AI 重大里程碑后可能自觉执行；历史教训：master 曾停滞 3 个月 |
| DEBT-BRANCH-002 | §4.2 | 任意分支 3 个月未合并到 dev 即判定为废弃 | 君子协定，无自动触发 | 无；悬挂分支将持续累积（历史已达 50+） |
| DEBT-BRANCH-003 | §4.3 | AI 每次会话开始时检查悬挂分支 | 君子协定，无自动触发 | 无；依赖 AI 自觉 |

**消除路径**：未来可新增 `branch_hygiene_reconciler`（post-commit 检测 master 滞后 dev + 列举过期悬挂分支并 warn），当前优先级不够，不创造无价值代码（向内收原则①）。在 reconciler 落地前，AI 读到本声明即知这些规则需自觉执行，且 master 滞后属预期行为（非异常）。
