---
module_id: POL-WORKSPACE-GOV-001
title: Workspace Governance Policy / 工作区治理规则
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
placement_note: "定义 ZephyrAlpha 工作区未提交改动的治理规则。消除 auto-sync 产物噪音，规范 .gitignore 维护，评估历史数据丢失。承接 100% AI 开发模式的工作区治理需求。"
related_rationale: []
related_open_questions: []
tags:
  - workspace
  - governance
  - auto-sync
  - gitignore
  - data-governance
summary: 定义 ZephyrAlpha 工作区治理规则。auto-sync 产物分类与处理策略（还原优先），.gitignore 维护规则，历史数据（bdpan）评估。消除工作区噪音幻觉源。
date: '2026-07-07'
---

# Workspace Governance Policy
# 工作区治理规则

---

## 0. 读者指南

| 章节 | 内容 | 主要读者 |
|------|------|----------|
| §1 | 策略动机：为什么需要工作区治理 | 所有人 |
| §2 | auto-sync 产物处理策略 | 实现者 |
| §3 | .gitignore 维护规则 | 实现者 |
| §4 | 历史数据治理 | 所有人 |
| §5 | 工作区检查清单 | 所有人 |

---

## 1. 策略动机

### 1.1 问题

ZephyrAlpha 的 GitCommitGateway 在每次提交后自动触发多个 reconciler 重新生成产物（dashboard、catalog、path-tree 等）。这些产物是**被 track 的**，导致：

1. **永久噪音**：工作区永远有 modified 文件（auto-sync 产物），AI 每次看到 `git status` 都需要判断"这些改动是否相关"
2. **过期快照幻觉**：AI 可能基于工作区中的旧版 auto-sync 报告做决策，而真源是生成器代码
3. **.gitignore 漂移**：运行时产物（.aidrafts/、access/ 等）偶发误入库
4. **历史数据丢失静默**：stash 事故导致数据文件丢失，无机制检测

### 1.2 本策略的解决

定义工作区治理规则：
- **auto-sync 产物**：还原优先（不提交工作区残留）
- **.gitignore 维护**：运行时产物必须登记
- **历史数据评估**：丢失即评估是否恢复

---

## 2. auto-sync 产物处理策略

### 2.1 auto-sync 产物定义

GitCommitGateway post-commit 自动触发的 reconciler 重新生成的文件，包括：

| 文件 | 生成器 | 性质 |
|------|--------|------|
| `docs/.../_registry/catalogs/rule_catalog_registry.yaml` | rule_catalog reconciler | 派生产物 |
| `docs/.../_registry/catalogs/registry_master_index.yaml` | registry_master_index reconciler | 派生产物 |
| `docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_*.md` | path-tree reconciler | 派生产物 |
| `data/asset_index/unified-asset-index.yaml` | asset_index reconciler | 派生产物 |
| `data/reports/dashboard.json` | dashboard reconciler | 运行时快照 |
| `data/reports/reconciliation-report.md` | reconciliation reconciler | 运行时快照 |
| `data/scans/raw-asset-scan.json` | asset scanner | 运行时快照 |
| `data/architecture_health/latest.json` | health reconciler | 运行时快照 |
| `data/classified/classified-assets.json` | classifier | 运行时快照 |
| `scripts/governance/meta/rules_integrity_db.json` | integrity checker | 运行时快照 |

### 2.2 处理策略：还原优先

- **工作区中 auto-sync 产物的 modified 状态**：`git checkout -- <file>` 还原到 HEAD 版本
- **理由**：auto-sync 产物的真源是生成器代码，不是文件本身。工作区残留的 modified 是噪音，下次 GitCommitGateway 提交会自动重生成并提交
- **禁止**手动提交工作区中的 auto-sync 产物残留（会被下次自动提交覆盖，制造无意义 commit）

### 2.3 例外：主动触发的全量重生成

当生成器代码本身变更（如 reconciler 逻辑修改）导致需要全量重生成时：
- 通过 `git commit` 提交生成器代码变更
- post-commit 自动触发重生成并提交产物
- **不需要**手动提交工作区残留

---

## 3. .gitignore 维护规则

### 3.1 必须忽略的运行时产物

| 路径 | 理由 |
|------|------|
| `.aidrafts/sess-*/` | session_worktree 工作目录（临时，运行时；只忽略 worktree 目录，不忽略 gitlink 文件，便于清理误入库的 gitlink） |
| `access/` | ClickHouse 系统产物（metadata dumps） |
| `metadata/` | ClickHouse 系统产物 |
| `*.db` / `*.sqlite3` | SQLite 运行时数据库 |
| `__pycache__/` | Python 编译缓存 |
| `.trae_cache/` | IDE 缓存 |
| `.ailocks/` | AI 文件锁运行时状态 |

### 3.2 维护责任

- **新增运行时产物时**：必须同步添加 .gitignore 条目
- **误入库的运行时产物**：`git rm --cached <path>` 取消 track + 添加 .gitignore
- **.gitignore 变更必须 commit**：通过 session_worktree 提交

### 3.3 禁止忽略的文件

- **生成器代码**：`scripts/governance/*.py`、`scripts/generate_*.py`（真源）
- **策略文档**：`docs/01_policies_and_standards/**/*.md`（治理真源）
- **YAML 真源**：`docs/**/_registry/**/*.yaml`（数据真源）
- **被 auto-sync 引用的产物**：虽然是派生的，但被 track 作为快照（见 §2）

---

## 4. 历史数据治理

### 4.1 数据丢失检测

- 工作区中 `data/raw/` 下的文件显示为 `D`（deleted）时，必须评估：
  - 是误删除（stash 事故）→ 从 git history 恢复
  - 是有意退役 → 确认退役后 `git rm` 并记录

### 4.2 bdpan 数据评估（2026-07-07）

| 项目 | 评估 |
|------|------|
| 数据来源 | 百度云一次性包获取（通达信板块分笔历史 Tick） |
| 获取方式 | 无 API 可持续更新，仅一次性包 |
| 消费代码 | 无直接消费模块（仅 asset-scan/classified 记录） |
| 替代方案 | ClickHouse sector_kline / kline_daily 表（K线级别，非 Tick 级别） |
| 丢失情况 | 8 个文件因 stash 事故物理丢失，已从 git history 恢复 |
| 策略 | **保留 git track 作为历史存档**；不主动维护更新；如需新 Tick 数据需重新从百度云下载 |

### 4.3 bdpan 数据清单（git tracked）

```
data/raw/bdpan/tick/index/2004-07/20040726.zip
data/raw/bdpan/tick/index/2016-10/2016-10.tsv
data/raw/bdpan/tick/lof/2025-02/2025-02.tsv
data/raw/bdpan/tick/sector/2011-12/20111229.zip
data/raw/bdpan/tick/sector/2012-05/20120518.zip
data/raw/bdpan/tick/sector/2012-11/20121108.zip
data/raw/bdpan/tick/sector/2012-12/20121224.zip
data/raw/bdpan/tick/sector/2013-03/20130320.zip
```

---

## 5. 工作区检查清单

### 5.1 每次会话开始时检查

```bash
git status --short
```

- 若有 `M`（modified）的 auto-sync 产物 → `git checkout -- <file>` 还原
- 若有 `D`（deleted）的 `data/raw/` 文件 → 评估是否恢复（见 §4.1）
- 若有 `??`（untracked）的运行时产物 → 添加 .gitignore（见 §3.1）

### 5.2 每次提交前检查

- 工作区中只保留**本次任务相关**的改动
- auto-sync 产物残留应先还原再提交
- 运行时产物误入库应先 `git rm --cached` 再提交

---

## 附录 A：历史教训

| 事件 | 教训 |
|------|------|
| 43 个工作区改动噪音 | auto-sync 产物不还原=永久噪音，AI 每次需判断相关性 |
| bdpan 8 文件 stash 事故丢失 | stash 操作 unlink 失败会留下残留，需检测恢复 |
| .aidrafts/sess-26204 gitlink 误入库 | session_worktree 运行时产物必须 .gitignore |
| access/ 目录 untracked 噪音 | ClickHouse 系统产物必须 .gitignore |

---

## 附录 B：自动化债务声明

> **架构债务登记**（2026-07-08 架构师审查裁定）

本策略文档中以下规则属于**君子协定**（依赖 AI 自觉执行，无 gate/reconciler 自动化保障），在 100% AI 开发模式下不会自发触发。与项目硬约束"永久系统必须全自动"存在张力，登记为架构债务，待后续 reconciler 落地后消除。

| 债务编号 | 规则位置 | 规则内容 | 自动化状态 | 缓解措施 |
|----------|----------|----------|------------|----------|
| DEBT-WORKSPACE-001 | §5.1 | 每次会话开始时检查 `git status --short` | 君子协定，无自动触发 | AI 读 AGENTS.md 时被引导执行；GitCommitGateway post-commit reconciler 部分覆盖（auto-sync 产物自动提交） |
| DEBT-WORKSPACE-002 | §5.2 | 每次提交前检查工作区只保留本次任务相关改动 | 君子协定，无自动触发 | session_worktree 物理隔离 + HELD-OVERLAP gate 部分覆盖（文件级冲突阻断） |

**消除路径**：未来可新增 `workspace_hygiene_reconciler`（post-commit 检测工作区残留 auto-sync 产物并自动 `git checkout` 还原），当前优先级不够，不创造无价值代码（向内收原则①）。在 reconciler 落地前，AI 读到本声明即知这些规则需自觉执行。
