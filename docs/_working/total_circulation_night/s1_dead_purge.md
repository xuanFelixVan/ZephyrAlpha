---
created: 2026-09-30
ttl: task_bound
title: S1 死信清淤与存活闸补链工作簿（A1 车道 st-circ-a1-20260930）
session: st-circ-a1-20260930
---

# S1 死信清淤与存活闸补链工作簿（车道 A1）

> 任务源=裁定#459 延伸+深挖矿处方；总包骨架=00_skeleton.md 第 1 批（A1）。
> 六向台账口径：上游触发/下游消费/输入/输出/真源锚/耗时账。

## 0. 交付摘要

| # | 任务 | 状态 | 落点 |
|---|------|------|------|
| 1 | WinError233 管道瞬态入瞬态类 | 完成 | commit_queue_landing.py:194-209（+3 串） |
| 2a | LANDING-TIMEOUT（git 墙钟超时）归环境类 | 完成 | landing:201（"timeout after"）+ :2850（OSError 捕获加宽）+ :3056-3068（COMMIT_FAILED 截收） |
| 2b | TTL-METADATA "execution failed" 归环境类 | 完成 | landing:220-229（_TRANSIENT_GATE_ENV_MARKERS/_is_transient_env_failure）+ :3056-3068 |
| 3 | 存活闸补齐自动重试链（B5 拾取/enqueue 自举/belt drain） | 完成 | commit_queue.py:2188-2208（drain 拾取闸）+ landing:3789-3808（pool 拾取闸=belt 生产主通道）+ try_bootstrap_drain/_cmd_enqueue/_cmd_requeue 经 drain_queue 同闸覆盖 |
| 4 | 静窗清淤 dead-archive --days 1 | 租约忙让窗（见 §4） | 未强清，汇报 |

测试：新增 13 用例全绿（详见 §3）；既有套件 landing 90 绿 / integration 32 绿 / belt 31 绿 / commit_queue 117 绿+2 既存红（他队语义之争，§5）。

## 1. 六向台账

### 1.1 任务 1+2：瞬态环境失败扩面（landing 侧）

- 上游触发：git 子进程 OSError [WinError 233]（管道对端瞬断，存量死信 77 封/7 天单项最大伪命中）；_run_git 墙钟强杀 "timeout after Ns (killed)"（存量 6 封）；ttl_gate 检查器子进程起不来 "check_frontmatter_metadata.py execution failed"（COMMIT_FAILED 伪装，存量 1 封在册/挖矿口径 19 死）。
- 下游消费：drain 泛化异常出口（commit_queue.py:2253-2260 瞬态截收→_drain_env_requeue）、pool 泛化异常出口（landing:_pool_process_item except 分支→_pool_env_failure_exit）、COMMIT_FAILED 结果出口（landing:3056）、死因三分类/处方（commit_queue.py:305-308 env 标记表，服务存量 84 封历史死信 requeue 判读）。
- 输入：异常实例或 reason 文本（大小写不敏感子串匹配）。
- 输出：env 类判定 → 项退回 pending + env_retry/attempts 计数（≤3/≤5 防活锁）→ 耗尽死信带 env 处方；绝不无声死信。
- 真源锚：landing:194-229（两标记表+统一判据 `_is_transient_env_failure`，复用 :197 判据思路单一真源）；session_worktree 90s 心跳判据=活性 reap 真源（SessionRegistry.list_active），本闸以 heartbeat exited 终态+注册表在册性为准（Lane D 0c20042f29 既定口径，情报行号 :1348 已漂移）。
- 耗时账：读齐+施工+测试约 2.5h（含 A3 热文件冲突让位重排一轮）。

### 1.2 任务 3：存活闸补链（全链自动重投出口全覆盖）

- 上游触发：pending→processing 认领（drain 与 pool 双路）——死会话袋旧循环=拾取→landing 失败→死信/退回→无人认领下轮复读。
- 下游消费：drain 拾取闸（commit_queue.py:2188）置鬼直落 dead/；pool 拾取闸（landing:3789，belt daemon bootstrap_drain_with_landing→drain_queue_pool 生产主通道）；enqueue 自举（_cmd_enqueue:3899 try_bootstrap_drain）/CLI drain/status/requeue 自举/belt daemon watchdog 全部经 drain_queue/pool 同闸覆盖——统一 helper=`_session_ghost_dead`（commit_queue.py:1878，Lane D 落地，本批零复制直接复用=内收）。
- 输入：项 session_id + runtime_root（heartbeat.jsonl 末行 status + session_registry.json 在册性）。
- 输出：meta.ghost=true + dead_reason=ghost_session:* + 处方（接管会话 requeue 可恢复，CLI 手动 requeue 不受闸限）；判定不了 fail-open 放行。
- 真源锚：裁定#459 册（0c20042f29）；闸语义总注释 commit_queue.py:1865-1876（"两个重投点"已扩为全链清单）；drain env 分支提取 `_drain_env_requeue`（:1945）供环境专类与瞬态截收两出口同闸零分叉；pool env 分支提取 `_pool_env_failure_exit`（landing:3704）同理。
- 耗时账：拾取闸两处+helper 提取约 1h；测试 13 用例约 1h。

### 1.3 任务 4：静窗清淤

- 上游触发：Owner 静窗令；dead-archive 三闸（年龄/revival 互斥/落地校验）自足安全。
- 下游消费：.runtime/commit_queue/dead_archive_<日>/ 袋+manifest（mv 非删可逆，RB2）。
- 输入：days=1（339 封 ≤1d 候选，实测 00:20 时点）。
- 输出：见 §4 执行记录。
- 真源锚：commit_queue.py dead_archive_letters（:2928）；安全五条=租约存活整体拒绝。
- 耗时账：租约忙让窗 3×60s+尾段重试。

## 2. 逐项 file:line（汇报口径）

任务 1（WinError233 入瞬态）：
- scripts/governance/commit_queue_landing.py:194-209 `_TRANSIENT_GIT_MARKERS` 补 "winerror 233"/"管道的另一端"/"no process on the other end"（:201 亦补 "timeout after" 供任务 2a）
- scripts/commit_queue.py:305-308 `_DEAD_REASON_ENV_MARKERS` 补 4 串（历史死信三分类归 env）
- scripts/commit_queue.py:1933 `_transient_env_failure_of`（drain 侧惰性判据桥）

任务 2（归环境类/env_retry）：
- scripts/governance/commit_queue_landing.py:220-229 `_TRANSIENT_GATE_ENV_MARKERS`+`_is_transient_env_failure`
- scripts/governance/commit_queue_landing.py:2850 `except (RuntimeError, OSError)`（WinError233 是 OSError，捕获面加宽）
- scripts/governance/commit_queue_landing.py:3056-3068 COMMIT_FAILED 伪装截收→`_env_pending_or_dead`（env_retry 计数闸）

任务 3（存活闸）：
- scripts/commit_queue.py:2188-2208 drain 拾取闸（ghost 直落 dead/，封印唯一出口同链）
- scripts/commit_queue.py:1945-1986 `_drain_env_requeue`（Lane D 环境分支提取，两出口共用）
- scripts/governance/commit_queue_landing.py:3789-3808 pool 拾取闸（belt daemon 生产主通道）
- scripts/governance/commit_queue_landing.py:3704-3746 `_pool_env_failure_exit`（pool 环境出口提取）+ :3931-3939 泛化异常瞬态截收
- enqueue 自举/CLI 自举/belt watchdog：经 drain_queue/drain_queue_pool 同闸覆盖（零新增入口代码=内收）

任务 4：scripts/commit_queue.py:2928 `dead_archive_letters`（现成机制，零代码改动）

## 3. 测试对应（新增 13 用例）

| 用例 | 对应任务 |
|------|---------|
| test_commit_queue_landing.py::TestTransientEnvFailureFamilies::test_marker_table_covers_pipe_timeout_and_checker_families | 任务1+2 标记表 |
| …::test_real_gate_violation_not_swallowed_by_env_family | 任务2 对照钉（真违规保持死信） |
| …::test_winerror233_pipe_oserror_returns_to_pending_not_dead | 任务1 |
| …::test_git_wallclock_timeout_returns_to_pending_not_dead | 任务2a |
| …::test_ttl_checker_execution_failed_commit_failed_returns_to_pending | 任务2b（env_retry 计数在袋） |
| …::test_real_ttl_violation_still_dead_letters | 任务2b 对照钉 |
| test_commit_queue_integration.py::TestGhostGatePickupAndBootstrap::test_pickup_of_dead_session_item_deadletters_before_landing | 任务3 B5拾取 |
| …::test_pickup_of_alive_session_item_still_lands | 任务3 对照 |
| …::test_enqueue_bootstrap_drain_gates_dead_owner_item | 任务3 enqueue 自举 |
| test_commit_belt_daemon.py::TestPoolDrainSurvivalGate::test_pool_item_of_dead_session_deadletters_as_ghost_never_touches_landing | 任务3 belt drain（pool 闸） |
| …::test_pool_transient_escape_requeues_not_dead | 任务2 pool 逃逸网 |
| …::test_pool_item_of_alive_session_still_processed | 任务3 对照 |
| test_commit_queue.py::TestGhostSessionGate::test_cli_manual_requeue_not_gated（适配） | 任务3 拾取闸协同演化：ghost 死信可 CLI requeue |

套件读数：test_commit_queue_landing 90 绿 / test_commit_queue_integration 32 绿（含 186s 重型真落盘件）/ test_commit_belt_daemon 31 绿 / test_commit_queue 117 绿 + 2 既存红（§5）。

## 4. 清淤执行记录（dead-archive --days 1）

- 00:20 dry-run 尝试：serializer 租约存活（pid=26144）→ DeadArchiveError 整体拒绝（安全闸正常工作）。
- 等 60s×3 重试：pid 26144→34288（belt 在持续排空他会话队列件）→ 仍忙，按纪律不强清。
- 候选面（--days 1）：339 封（885 封总量中 ≤1d 部分；其中 WinError233 77/LANDING-TIMEOUT 6/execution failed 1 经本批改判后全部归 env 类可安全归档或 requeue）。
- 处置：让窗汇报；后续静窗由维护班执行 `python scripts/commit_queue.py dead-archive --days 1 --execute`（dry-run 先行）。

## 5. 让位与冲突登记

1. **scripts/governance/commit_queue_landing.py 让位一轮**：A3（st-circ-a3-20260930）在我读文件期间落入热册三连改道（+51/-1 staged）；即时释放 claim 让位，后经 16min 静默窗确认其件自洽完整（类+判据+抛点+不变量四件齐）后叠加施工，**A3 成果零回退原样保留并随本 commit 落地**（其件携带 in-code 署名"A3 任务1 st-circ-a3-20260930"）。
2. **tests/governance/test_commit_queue.py 既存 staged 外来件吸收**：基线上已有他队 staged 的 41 行死代码删除（G5 双面尺误缩进进 `_hand_dead_bag` 函数体 return 之后=永不可收集的孤儿测试块）；本批对该文件仅有 TestGhostSessionGate::test_cli_manual_requeue_not_gated 适配（拾取闸使死会话袋在 landing 前出局），提交时该删除随文件面吸收（披露如上）。
3. **既存红登记不代修**：TestRegistrationGate 两用例（test_enqueue_item_registered_file_passes_and_carries_face / test_requeue_channel_passes_when_registered）在无本批改动的 HEAD 基线上即红（TTL 检查器缺席时 requeue 预检硬拒 vs 用例期望 degraded 放行——C-2 预检语义之争），属他队在途语义演化，按"他会话在途违规不代修"登记让位。
4. 测试哨兵注记：pool 测试哑 landing 须实现 `_item_paths`+`repo_root`（路径锁与 phase 账本 anchor 在 landing 调用前被触）。

## 6. 执行留痕

- 提交路径（三折）：①主区直提被外队 staged 死信件连坐（st-menu-t1b5 的 macro_regime_sensor.py 死于 ALGO-NOTE-SYNC 后滞留主区 staged-new，BLUEPRINT-FORMAT 扫全暂存面拦直提）→ ②按宪法 §2.6 改走正门 `--enqueue`：袋 0001 死于 COMPLEXITY-GUARD NO-LONG-PARAM-LIST（_pool_env_failure_exit 8 参>7，worktree 落地全门禁链比主区预检严实证）→ `_PoolLedger` dataclass 降至 6 参重投 0002 → ③袋 0002 死于 **belt daemon 基建级 TypeError（Popen.__init__ unexpected 'timeout'）**，同窗 st-circ-a3-0006/0007 同型双死（多车道受害，非本袋内容）。
- TypeError 根因取证：G2 车道未提交的 process_pool.py 捕证件（run_subprocess_hidden meta_out Popen 形态）被常驻 belt daemon 在其**中间编辑态**加载；daemon re-exec 需「已提交代码 epoch 变更 + 安全点租约空闲」双条件——今夜队列持续繁忙 re-exec 被 perpetually 推迟，内存旧版（timeout 未 pop）持续杀袋。现行盘面版已含 `timeout_s = kwargs.pop("timeout", None)` 治其标。处置=等队列空窗安全点 daemon 换代后重投（专人专事：daemon 重启归维护班，本车道不越权杀进程）。
- 会话注册：session_worktree_start(allow_workspace_drift=True)（夜战多车道主区直改现状 145 文件在途脏，commit-only 车道带漂移旗注册；心跳 daemon pid=22548）。
- 偏差：①belt daemon 模块本体（commit_belt_daemon.py:768-846 run_daemon）零改动——其 drain 全链委托 bootstrap_drain_with_landing→pool，闸落 pool 拾取点即覆盖（情报行号映射见 §1.2）；②reason=session_dead 语义由 Lane D 既定 ghost_session 前缀承载（同一判活 helper、同一 env 处方、可 requeue），未另造第二死因串（内收）；③既存红 2 例（TestRegistrationGate）基线即红，他队语义之争不代修（§5.3）。
