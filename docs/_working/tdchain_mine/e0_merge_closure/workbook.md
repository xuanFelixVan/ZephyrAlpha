---
ttl: task_bound
title: E0 合并队列收口作业簿——台账分支栈+双 s-owner+regcal 五路归 dev
session: st-tdchain-20260917
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# E0 合并队列收口作业簿

## 六向台账

- **目标**：交接令任务 0——把昨晚起晾置的四条分支全部安全落进 dev，最后 depgraph regenerate 收敛。
- **证据**（2026-09-18 03:3x 实测）：
  - P1 已并入（merge=15176ed2b8）、P2a 已并入（merge=db88f03eda）、P2b **未并入**（旧 merge 已 abort，分支完好，e19bc24cf1 在分支上）。
  - orchp3 **未并入**（9098c65245 编排器+4effca93b2 测试隔离修复+2 chore，分支包含 e19bc24cf1）。
  - s-owner001 **未并入**（b4c3c6f26d+23ed6ef080 两 commit，交接包 733f79cb9d：可直接整支 merge，#293 已在 dev 侧登记则冲突按"双条目并存/编号不撞"解）。
  - s-owner002 **未并入，禁整支 merge**（分支头部两枚他车道探针 commit e10ac5acc4/2924601305 不得带入 dev；交接包 5338f109bf：按序 cherry-pick 4376f35627→fa5c8febaf→89dd33dd8a→5338f109bf；fa5c8febaf 的 ruling_registry 与 dev #304 已登记冲突→机械重放"保 dev 已有+跳过重复 #304"）。
  - regcal **未并入**（session/st-regcal-20260917：26ac558beb 协议预注册+a2ab567992 重校准执行，9 文件）。
  - fast_sign 行 30：P2b 重 merge 前须拆分 daily_plan.py 两函数（复杂度 21/23>15，NO-HIGH-COMPLEXITY 门会拦）——在分支 worktree 内拆，不动主区。
  - 主区在飞：本轴目标文件（pipeline_events/daily_plan/ch_tick_kline）零本地编辑；staged 有他会话 14 文件——所有提交走 --enqueue 防连坐。
- **块**：M1 regcal merge → M2 p2b 分支内拆函数+分支提交+merge → M3 orchp3 merge → M4 sowner001 merge → M5 sowner002 cherry-pick×4（cherry-pick --no-commit+git_commit.py 正门）→ M6 generate_project_depgraph.py --force → M7 循环验证（相关测试冒烟）。
- **依赖**：M2 先于 M3（orchp3 含 p2b）；各步前查主区无同文件在飞编辑；合并工具=python scripts/session_worktree.py merge <sid>（正门）或 git merge+gateway --merge-finalize。
- **三态**：挖干（方案定案），执行中。
- **下一步**：按 M1→M7 串行执行，每步 git log -1 --name-only 核归属。

## 合并顺序定案（单写者原则）

M1 regcal（独立域，最无冲突面）→ M2 p2b → M3 orchp3（末棒编排器最后接电）→ M4 sowner001 → M5 sowner002 → M6 depgraph → M7 验证。

## 长尾登记

- s-owner002 交接包 §2 三遗留（OPS-GUARD worktree 队列缺陷 / FINAL 查询 CH Code 181 崩溃 / 探针 commit 不代删）——维护班口径，本环节不修，已在 e3/e8 留意 FINAL 坑。
- 裁定登记合并冲突预案：任何分支带来的 ruling_registry 条目与 dev 冲突时，"保 dev 已有+仅追加缺失条目，编号不撞"。

## 接力情报：p2b 重 merge 的 gate 链实测（flash-nightbuild-20260918 班，09-18 05:2x）

本班已完成 E0 前置：**daily_plan.py 双超标函数已拆**（eval_trigger 21→12 / emit_for_trade_date 23→8，commit a4cb7706 在 ai/st-ledgerp2b-20260916/scenario-engine 分支 tip，37 tests 绿）。E0 重 merge 时将依次撞上以下后冻结 gate（本班逐个实测）：

1. NO-BARE-SQL：分支存量 SQL 常量行 6 处——行级 `# noqa: bare-sql  <理由≥10字>`（注意 bare-sql 后须两个空格）已代打在分支工作副本（未提交，见下）。
2. NO-LONG-PARAM-LIST：scenario_classifier.write_verification 9 参——def 行 noqa 已代打。
3. **TABLE-NAME-REGISTRY（硬拦，未过）**：plan_engine 三文件硬编码 c1_market.kline_index / judgment_daily_plan / judgment_plan_verification / market_kline_etf_60min / judgment_next_day_forecast 等，其中 kline_index 与 judgment_* 五表**不在 TableRegistry**——须先注册（含 schema 文件存在性证明）或迁移 get_registry().table()。此为 CH-024 Phase 5 在 plan_engine 域的欠账，本班按边界不代修。
4. CAPABILITY-LOOKUP-REQUIRED：merge finalize 时 message 须带 `[no-lookup:continuation]`。
5. 干净 merge 姿势：主区暂存区整夜有他会话 staged 内容——**禁直连 merge**；用临时 worktree（`git worktree add -b temp/xxx dev`）→ merge --no-commit → 解冲突 → `git_commit.py --merge-finalize` → 主区 `git merge --ff-only temp/xxx`。capability/module_translation 两注册表必撞 append-append 冲突，双侧并集解析即可。

分支上未提交的 noqa 改动留在 .worktrees/st-ledgerp2b-20260916 工作区（本班 worktree add 后被后续 stash 扫走两轮，恢复动作见 stash 列表），E0 接手时请先 `git status` 该 worktree 并把 noqa 批次提交到分支。
