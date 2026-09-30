---
created: 2026-09-30
ttl: task_bound
title: D2 手术单 — pre-commit 通道出全局锁（staged 指纹回锁复核）
session: st-gate-rationalize-20260929
---

# D2 手术单 — hook 通道出全局锁（蓝图版，待专班施工）

> 立档：2026-09-30 晨（st-gate-rationalize-20260929 总包）。蓝本规格对标 D1 手术单（commit_speedup_campaign/10_D1_D2/D1_stats_lock.md，已按单落地 4bab350d）。
> 依据：Owner 2026-09-30 全批 gate_survival_adjudication §8.8（"hook 通道出锁（staged 指纹回锁复核）"）。
> 本单为设计-only；施工 lane 按本单写码。估时 2.5h（+0.5h 缓冲）。

## 1. 现象与量级

hook 通道（`_run_precommit_channel`，64 hook，own-scope 临时索引）在全局提交锁**内**执行：
`_commit_locked`（git_commit_gateway.py:3301 def；通道调用点 :3875，步骤 5.5）。
通道 p50 44.3s / p90 157s（precommit_channel_stats.jsonl，141 样本；B5 后 gate-test 增量化+5 SKIP 已显著下降，但仍是单笔最大段）。
临界区内每秒都让所有等锁会话停摆——这是提交链路**最后的结构性串行大项**。

## 2. 机理锚点（file:line，2026-09-30 盘面）

| 位置 | 内容 |
|---|---|
| :3301 `_commit_locked` def | 全局锁内的提交主体（锁由 `_GlobalCommitLock` __enter__ 保证） |
| :3869-3871 | 步骤5：`git diff --cached --quiet` 空 staged 短路 |
| :3873-3875 | **步骤5.5 通道调用**（本单迁移对象）：`precommit_block = self._run_precommit_channel(session_id, files)` |
| :3526 `_run_precommit_channel` def | 通道本体：临时索引 read-tree+add（:3398-3415 一带）→ 两段式 Phase-A/B（:3635-3664）→ SKIP 8 台（:470-473 `_PRECOMMIT_CHANNEL_SKIP_HOOKS`） |
| :3882+ | 步骤6：git commit 本体 |
| A1 装表 | `_pc_ms` 通道耗时落账（:3877-3879 一带）——出锁后此账继续有效 |

通道读面=own-scope 临时索引（GIT_INDEX_FILE），**不读共享暂存区**→通道结果只依赖
`files` 清单的内容态，与全局锁保护的共享 index 无写交互——这是"可出锁"的正确性根基。

## 3. 设计（意图描述，不附代码）

**原则：通道前移到锁外执行；锁内以 staged 指纹复核兜底；漂移即锁内重跑（fail-safe）。**

1. **锁外前移**：`commit()` 主流程在构造 `_GlobalCommitLock` 之前、preflight 之后，用与
   `_commit_locked` 相同的入参调 `_run_precommit_channel`（前置条件=staged 面已就绪：
   gateway 的 add/rm 在锁外已完成——核实 `_commit_locked` 之前 add 时点，若 add 在锁内则
   前移点改到「add 完成后、取锁前」，以实锚为准）。
2. **回锁指纹复核**：`_commit_locked` 步骤 5.5 位置改为指纹复核：对 `files` 清单逐文件
   `git show :<path>`（或 `git diff --cached --quiet` + own-scope blob sha 集合）与锁外
   通道运行时快照比对。一致→复用锁外结果；**不一致→锁内原地重跑通道**（此刻锁内重跑
   成本与旧状相同，正确性零损——漂移意味着有人改了同批文件，重跑是唯一安全语义）。
3. **阻断语义不变**：`precommit_block is not None → COMMIT_FAILED`，文案、装表
   （`precommit_channel_stats.jsonl` 两次字段、`commit_block_events` 的
   `GATE-PRECOMMIT-RUN` 事件）、`precommit_channel_blocked` 事件全部原样——本单零判据变化。
4. **不做面（明写）**：Phase-A/B 两段式结构本单不动（另一立项：单趟化需与首过率 9% 的
   快败语义一并重设计）；SKIP 清单、慢尾清单、own-scope 临时索引机制、超时（300s/900s）
   全部不动；`gate-commit-gw` 裸面封锁不动。
5. **重入保护**：锁外通道运行期间他工可能拿到锁先提交——与本案无冲突（own-scope 索引
   隔离）；但须防**重入取锁**：通道代码路径内任何 `run_git` 不得触发嵌套
   `_GlobalCommitLock`（现状核实：通道内无取锁点，写进 docstring 作为不变式）。

## 4. 红测（先红后修，同 D1 纪律）

- **R-D2-a 结构断言**：monkeypatch `_run_precommit_channel` 记录调用线程持有的
  `_GlobalCommitLock` 状态（或以锁文件存在性+线程标记判定）：通道执行时**不得持有全局锁**
  （现码必红：:3875 在 `_commit_locked` 内=锁内）。
- **R-D2-b 漂移重跑断言**：构造锁外通道绿→锁内指纹漂移（测试内篡改一 staged 文件）→
  断言锁内重跑被触发且以重跑结果为准（现码无重跑语义，必红）。

## 5. 语义等价矩阵（差分自证）

场景×新旧双实现对照（旧=HEAD，新=工作区；hook 框架用 2-3 个假 hook 桩，禁真 64 hook 跑满）：

1. 通道绿+锁内无漂移 → commit 成功（基线）；
2. 通道红 → COMMIT_FAILED 文案逐字节一致；
3. 通道绿+锁内漂移 → 重跑绿→成功 / 重跑红→FAILED（两支）；
4. 通道超时（300s/900s 桩）→ 行为与旧一致；
5. SKIP 台不因迁移改变 SKIP 生效；
6. 装表三处（channel stats/block events/耗时账）字段级一致；
7. 空 staged 短路（步骤5）先于通道（迁移后仍短路在先，不白跑通道）；
8. `--skip-preflight`/reconciler-verify 等特殊通道回归绿。

必绿清单：tests/governance/ 下 precommit 通道既有套件（grep `_run_precommit_channel`
的测试文件全量）+ test_commit_chain_campaign_20260922.py + red_blue_pkg14。

## 6. 风险与回滚

| # | 风险 | 缓解 |
|---|---|---|
| 1 | 锁外窗口内 staged 被改（他会话同文件）→ 指纹复核兜底重跑 | §3.2；矩阵例3 |
| 2 | add 时点若在锁内→前移点选错致通道跑在空 staged 上 | §3.1 实锚核查为施工第一步；R-D2-a 加「通道运行时 staged 非空」断言 |
| 3 | 嵌套取锁死锁 | §3.5 不变式+通道内无取锁点核实 |
| 4 | 通道重跑放大（每次漂移都全通道重跑） | 漂移=同批文件被改=旧语义下也必重跑，无放大 |

回滚：单 commit revert（改动集中 git_commit_gateway.py 一文件+新测试）。

## 7. 验收（不接受的伪证）

不接受"不抛异常即通过"/仅计数对比。必须：R-D2-a/b 先红证后绿；矩阵 8 例双实现差分
（文案/事件字段逐字节）；既有通道套件全绿。
