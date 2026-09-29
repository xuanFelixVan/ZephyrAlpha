---
created: 2026-09-30
ttl: task_bound
title: 提交链路全流通·E7 队列序列化+落地（挖矿）
session: M3
---

# E7 — 提交队列序列化与落地（serializer worktree / 八相位落地 / converge / integrity 基线 / stats_lock / advance_dev）

> 挖矿代理 M3 ｜ 2026-09-30 盘面实测行号（较种子行号漂移，冲突以本文为准）。
> 真源：`scripts/commit_queue.py`（3592 行，clean 无占用）、`scripts/governance/commit_queue_landing.py`（4029 行，**工作区 MM=他会话占用中**，占用登记见 §0）。

## §0 自审闸三态

| 段 | 状态 | 依据 |
|---|---|---|
| commit_queue.py 全部（enqueue/lease/cascade/drain 串行带/CLI） | 【挖干】 | clean，六向齐 |
| landing 序列化前置（ensure_worktree/_sync_worktree/幂等/冲突/snapshot/prestage/CAS/converge/integrity 旗组） | 【挖干】 | 逐锚点本日核实（只读挖矿不受 MM 影响；**手术/改码禁入**直至占用释放） |
| **stats_lock 停世界临界区**（D1） | **【不可挖】** | landing.py 全文件工作区 MM（`git status` 短标 MM，`git diff --stat`=20 行 18+/2- 未提交）；session_registry 无该文件直接 claim（现锁册仅 2 个注册表 catalog 被 st-zc9-lane-r2-20260930 持有）；总包骨架 §三 B 段已排队"等解锁，盯队列"。D1 手术单已备：`docs/_working/commit_speedup_campaign/10_D1_D2/D1_stats_lock.md`，占用释放后按单施工 |
| 池化 CAS 重放/门禁链零适配 | 【挖干】（门禁本体归 E3） | 锚点齐 |

## §1 组件全清单

### 1.1 `scripts/commit_queue.py`（队列面）

| 组件/功能 | 锚点 file:line | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|
| 队列根与原子写 | :397（resolve_queue_root，`.runtime/commit_queue/`）、:428-436（`_atomic_write`=tmp+flush+**fsync**+os.replace） | 每次 | _atomic_write 2KB 件 med 1.19ms/p95 1.39ms（D1 §2.3 微基准） | RULE-ONE 同款 |
| 路径校验 | :474（`_validate_relpath` 拦穿越/绝对/.git/密钥） | enqueue+落地双侧对称 | ~0 | 红队对称（landing :2102-2108 同口径） |
| 入队 `enqueue_item` | :915（session 线程锁 :1025-1026；入袋即完成） | AI 提交改道正门 | 含引导提交（autocrlf 链落 CRLF 为环境事实，ef1a02fdd6 披露） | 锁忙自动改道入队（宪法 §2） |
| SerializerLease | :1118（O_EXCL+TTL+僵尸 PID；66 号 §8 语义 :48） | drain/pool 起 | — | 单写者互斥旧路径 |
| 级联标记 `_mark_cascade_stale` | :1460（glob pending 全量 :1042 旧锚现 :1460 体内；read_text+json.loads 每候选；命中重写 fsync）；串行带调用点 :1929 | 每件落地后 | **纯扫描 0.096ms/件、命中重写 +1.74ms/件；生产形态 83 件 med 144.3ms**（D1 §2.3，拟合 T≈0.096N+1.74h 吻合） | 同步，**池内被 stats_lock 包裹=D1 缺陷核心** |
| 基底重校验 `_revalidate_stale_base` | :1536 | stale 旗命中 | git 读若干 | 判据不改（D1 §4.6 不动面） |
| 串行传送带 `drain_queue` | :1746（slow ledger :1955，阈值 `_SLOW_ITEM_LEDGER_SECONDS=300` :181；级联 :1929） | k=1 降级路径 | — | 逐字节=k=1 降级等价锚（test_k1_matches_legacy_byte_for_byte） |
| 死信通知 | :1279（`_notify_task_board_dead_letter` 开 sqlite；docstring 自decl"失败不阻断排空"） | 每笔死信 | 锁内 sqlite（D1 面） | 旁路 |
| CLI | :3501 enqueue / :3527 status（触发一次排空尝试）/ :3532 drain / :3542 requeue / :3562 cleanup（done/ TTL，**dead/ 永不清理**）/ :3566 dead-archive（--execute 动盘）/ :3580 health（只读四态计数） | 人工/编排 | — | requeue=死信取回重建快照新 qid 排队尾 |

### 1.2 `scripts/governance/commit_queue_landing.py`（落地器，八相位）

**A2 分段装表**：`_timed_phase` :1389 → `landing_phase_stats.jsonl` :1368（`_emit_landing_phase_stat` :1406，`_pool_process_item` finally :3610-3614 三出口全覆盖——成功/死信/环境失败件都有账）。

| 相位 | 锚点 file:line | 功能 | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|---|
| ① worktree | :1572-1626 `ensure_worktree` | 幂等就位：注册+目录在→复用 :1593-1595；注册残留→prune+safe_rmtree 重建 :1596-1603；半成品→物理清 :1604-1612；`worktree add -b` :1620-1623；`_provision_env` PG+CH :1563-1570 | 每工首个单项 | 2026-08-29 事故治本：目录在而 .git 链接丢失→git walk-up 打穿主仓（:1591-1592 git_link_ok 检查） | 单写者无竞态 |
| ② sync | :1628-1656 `_sync_worktree` | `reset --hard refs/heads/dev` :1644 + `clean -fd` :1646（journal 瞬态 0.5s 重试降级 :1648-1656，12+ 死信实证治本）；自愈 guard reset/孤儿 commit | **每件处理前** | 触发 post-checkout 钩（B0_1 A6 UNKNOWN） | §11 #6 不变量机械实现 |
| ③ conflict | :1692 起（`_changed_paths_between` :1687、`_already_landed` :1661-1678 三重幂等：landed_id+is-ancestor :1669-1671 / 标记 grep :1672-1677 / noop 哨兵 :1666-1668） | 每件 | git 读 2-3 | 重放不双落 |
| ④ snapshot | :2094-2165 `_apply_snapshot` | blob 落盘：`_validate_relpath` :2106；delete :2110-2115；**注册表族三向合并** :2124-2130（is_registry_mergeable，W2 治本：陈旧快照 blob 一写抹 103 条已提交身份）；**写后读回自验** :2141-2163（M5.1 rsync -c 语义，静默丢失→snapshot_retry 计数闸退 pending/死信） | 每件 | blob read+write+sha256×2 | 路径校验/合并/自验全内置 |
| ⑤ prestage | :2170-2229 `_prestage_snapshot` | add/rm 进 index（gate 链 staged-diff 前置）；gitignored 混入 `check-ignore --no-index` 前置点名 :2193-2201（Mode A 治本，死信带可行动处方）；pathspec-from-file :2202-2224 | 每件 | 2-3 git 子进程 | 失败→COMMIT_FAILED 死信不静默 |
| （gates） | :2869 `_record_phase(self,"gates",...)` | 各工独立 gateway 跑全门禁链（E3/E4；`_GlobalCommitLock` 按 worktree 键控→工间零锁竞争） | 每件 | 单条 commit 墙钟 112s med（E5 账） | 门禁一套不裁 |
| ⑥ cas | :2231-2278 `_advance_dev` | `git update-ref refs/heads/dev <new> <old>` :2270；**双锁统一**：CAS 前抢 `_GlobalCommitLock`（timeout=30 fail-open 退裸 CAS :2247-2268；#ARCH-327 教训：异常类型必须进正文 :2259-2261） | 每件落地 | **1.25s/次**（触发 reference-transaction 钩，E6 账）；锁窗 <1s | **唯一串行落地点**；失败=CasConflict→重放/死信 |
| ⑦ converge | :2401-2467 `_converge_main_workspace` | 主区受限收敛（66 号 §9.7 受控放松 2026-08-23）：仅当文件==old 逐字节才快进写 new（零 WIP 丢失）；**RB1 条件式 index 收敛臂** `_converge_index_one` :2385-2399（wt==new 前提下三分判型：index==new=already / index==old=残影 `restore --staged --source=<new>` 清之 / 异于两者=他会话 staged WIP 禁碰；双开关 off/.live/缺省 shadow 只判不动，ef1a02fdd6）；审计 `main_workspace_sync.jsonl` :139、:2451-2459 | 每件落地后（fail-open 不改 LandingResult） | **med 0s / max 1887s**（b0_readme 收敛段 152/0/1887）；2151 条 skipped_dirty 主体=残影病根，RB1 治本 | 永不改主区脏文件 |
| ⑧ baseline | :2518-2551 `_refresh_integrity_baseline_main_repo` + :2497-2516 `_record_integrity_refresh_intent` | **flag 分流**（调用点 :2981-2989 串行支、:3063-3071 池化支）：mode=snapshot→主仓同步 spawn `validate_rules_integrity.py --register`（timeout=180 :2538-2544）；mode=head→只记意图（append_intent，去抖键 head_sha，N 件→1 刷） | 每件落地后 | **snapshot 态实测 mean 46.1 / med 6.2 / max 300.7 s/件（b0_readme）；head 态 0.026-0.110s（flags.yaml:127 n=17/n=120）** | fail-open |

### 1.3 池化（k 工通道池）

| 组件 | 锚点 file:line | 功能 | 耗时账/语义 |
|---|---|---|---|
| `drain_queue_pool` | :3303（k=resolve_pool_workers :3152；k≤1 逐字节降级 :3328-3330；池级单 lease+单心跳） | 投机并行验证+串行落地 | **现值 k=6**（thresholds.yaml:290 `commit_queue_landing_pool_workers: 6`，k=6 试轮 Owner 09-26 批 CPU 69% 水位；k=4 为 st-k4-20260923 原设计） |
| `make_worker_landing` | :3174 | 每工独立 worktree/分支/gateway | gateway `project_root=worktree` + `registry/roster_root=主仓根` :2553-2572（q-0006/q-0007 名册/import 同源治本） |
| `_pool_claim_item` | :3247-3297 | FIFO+车道优先，原子 rename pending→processing=互斥点；幽灵回写 :3291-3293 | 认领即互斥（D1 §4.1 依据） |
| `_run_pool_wave` | :3380-3477 | `stats_lock=threading.Lock()` **:3391 每波一把**；波首 `_recover_orphans` :3394；D3 工不得早退（err_streak<20 吞错续跑，09-24 三工停领→单工把一波开到 17 点、18 件/时→2-4 件/时实证）:3419-3440 | 工棚级复活 |
| `_pool_process_item` | :3491-3642 | B5 attempts 拾取即死信 :3518-3538；stale 重校验收进计数闸（M3 移交 38 笔逃逸治本）:3540-3559、:3481-3488；路径锁 :3545/:3564（同路径项门禁段前串行化）；env 分支计数+退 pending+终止本波 :3566-3607 | A2 finally :3610-3614 |
| **D1 停世界段【不可挖】** | **:3616-3639** | `with stats_lock:` 内含：_atomic_write :3620 + os.replace :3621 + **`_mark_cascade_stale` :3623（O(N) 全 pending 扫描+fsync）** + 死信支 sqlite 通知 :3637；四工共享锁内完全串行 | **实测 144.3ms/次（83 件同 base，D1 §2.3）；四工 overlap ratio=1.00**；波内累计扇出 O(landings×pending)。注意：landing(item) 本体在 :3565 **锁外**（设计正确段） |
| CAS 重放 | `_pool_cas_replay` :2999-3074、`_replay_commit_without_gates` :3077-3116、`_commit_tree_same_message` :3118 | 冲突：注册表同册=条目级三向合并重放吸收零丢失；无重叠=commit-tree re-parent（不重跑门禁）；非注册表同路径=死信零覆盖 | 重放仍触发钩链（E6 账） |

### 1.4 旗标现值（2026-09-30 实核 config/flags.yaml + thresholds.yaml）

| 旗 | 现值 | 锚点 | 语义 |
|---|---|---|---|
| `integrity_baseline_mode.mode` | **"head"** | flags.yaml:124-128；翻转 commit **d2446aff07**（[st-gate-rationalize-20260929][第二波B段·flag翻转]，Owner 2026-09-30 全批 §9.2；实现+测试随 SW19 袋 228ce95188 先落地，head_baseline12 19/19 绿） | **每落地件同步刷新 mean 46.1s/件已消除**（省 46.1/6.2/300.7 + chore(integrity) 记账税；WIP 篡改检测不降级——工作树面继续读）；回滚=改回 snapshot 一个 YAML 值 |
| `git_operations.regen_scope` | "any_worktree" | flags.yaml:48 | main_only=Owner 门位待翻（E6 待办 A6） |
| `git_operations.immutable_tree` | true | flags.yaml:52 | S1 不可变树（ed935c29af 等提速队已翻，d2446aff 同批披露） |
| `commit_queue_landing_pool_workers` | 6 | thresholds.yaml:288-290 | k=6 试轮；1=逐字节降级开关 |

## §2 六向台账

- **上游触发源**：① 各会话提交 LOCK_TIMEOUT/`--enqueue` 改道（E5 gateway）；② git_commit.py 直提改道（M1.2 锁外预检，INVARIANTS :8）；③ requeue/死信取回；④ belt daemon（belt_daemon.lock，commit_queue.py:2662）。
- **下游消费方**：dev ref 新 tip（全仓读取面）；主区 converge 后的工作树/index；done/dead/pending 队列目录；`landing_phase_stats.jsonl`（E9/E10）；`main_workspace_sync.jsonl`（收敛跳过审计）；`bottleneck_ledger.jsonl` slow_item（>300s）；task_board 死信通知；意图账（integrity head 态）→批量刷新事件源。
- **输入面**：队列项 JSON（qid/session_id/files[{path,action,blob_ref,blob_sha256}]/meta{stale,stale_by,env_retry,snapshot_retry,attempts}）；blob 袋；dev HEAD；generator/注册表 mergeable 判定；flags/thresholds。
- **输出面**：LandingResult(ok, landed_id|reason)；落盘 commit（带 `[GW:sid:worktree]` 系标记走全钩链）；done/ 与 dead/ 件（dead 必带 prescription+owner_session）；级联 stale 旗写盘。
- **真源锚**：§1 全部 file:line；不变量真源=landing :8-13 INVARIANTS（永不改主区脏文件/单写者/幂等不双落/门禁一套不裁/瞬态环境失败退 pending 绝不死信/k 池语义）； D1 手术单=`10_D1_D2/D1_stats_lock.md`；耗时真源=`40_B0_derived_offload/b0_readme.md` + `60_deep_dive/deep_dive_r1.md`。
- **耗时账**（b0_readme 表 + deep_dive_r1）：落地件全程墙钟 **760/550/3192s**（mean/med/max，n=174，右删失@300s）；t0→收敛首条 632/443/1812（仅 24/60 窗可定位）；收敛段 152/0/1887；收敛末→件结束 46.1/6.2/300.7（**head 翻转后此段归零**）；**不可归因残余 ≈630s/件**（36/60 窗零收敛记录、19 窗零 gate 记录→A2 装表前无锚点，现 landing_phase_stats.jsonl 已补）；residual 分解：门禁链 48.2%+precommit 16.1%=64.3% 可解释，**剩 ~123s/笔未解释**（deep_dive_r1 §B）；单件 hook 成本与件大小脱钩（1 件 346-658s vs 38 件 33-53s，全仓型 hook 是慢段）；工位面无结构性差（同件四工 ±30%），w0/w3 均值高=尾部事件+失败率（~50% vs w2 30%）。

## §3 缺陷与已修

| # | 缺陷（实证） | 治本 | 锚点 |
|---|---|---|---|
| 1 | W4 孤魂 301a6ee82a：直提锁与队列 CAS 互不排他 | 双锁统一（CAS 前抢 `_GlobalCommitLock`） | landing :2240-2245 |
| 2 | W2 陈旧快照 blob 一写抹 103 条已提交注册表身份（fb5a7821d） | 注册表族条目级三向合并，不做整文件覆盖 | :2124-2130 |
| 3 | 落地器物化静默丢失（句柄半写/杀软/盘面回滚）拖到 gate 后假死 | M5.1 写后读回 sha256 自验+snapshot_retry 闸 | :2141-2163 |
| 4 | gate 装载失败活锁（HEAD 册坏→全队无限 pending） | M5.2 新鲜子进程判别：同败=死信，fresh 过=env_retry 退 pending | :2602-2612、:2716 |
| 5 | 毒药件无限占队首 | B5 attempts≥阈值拾取即死信（≥3 惩罚退避/≥5 死信） | :3515-3538 |
| 6 | 工线程早退→单工把一波开 17h（09-24 实测 18→2-4 件/时） | D3 err_streak<20 吞错续跑 | :3419-3440 |
| 7 | gitignored 路径混入快照→git add rc=1 整项死且病灶不可读 | Mode A check-ignore 前置点名+可行动处方 | :2190-2201 |
| 8 | clean -fd 撞 SQLite journal 瞬态→12+ 死信饥饿 | 失败 0.5s 重试一次后降级 warning（pathspec 双保险） | :1635-1656 |
| 9 | worktree 目录在而 .git 链接丢失→git walk-up 打穿主仓（2026-08-29 事故） | git_link_ok 复用前提检查 | :1591-1603 |
| 10 | 66 号 §9.7 废止 index 同步后每件落地留残影（main_workspace_sync 2151 条 skipped_dirty 主体） | RB1 条件式 index 收敛臂（残影 restore/他会话 WIP 禁碰/shadow 缺省） | :2385-2399（ef1a02fdd6） |
| 11 | q-0006/q-0007 死信：env 名册读 worktree=provision 时点态 vs import 读主区盘分裂 | roster_root=主仓根（名册+代码同盘同态） | :2553-2572 |
| 12 | M3 移交：stale 重校验 git 读在 try 外，38 笔环境失败逃逸计数闸→项滞留 processing 无限重放 | `_stale_revalidate_counted` 收进 env 闸 | :3481-3488、:3540-3559 |
| 13 | integrity 基线 snapshot 态每件同步 spawn 180s 超时白等（mean 46.1s/件+记账税） | **B0/M1·P3 head 态翻转**（2026-09-30 d2446aff，Owner 批）；snapshot 方法保留为回滚态 | :2483-2551、flags.yaml:126 |
| 14 | regen 再生锁/账/日志每工一把（R2c）+ 产物被下件 reset --hard 抹掉（C5 负收益） | 主区钉根（regen 侧已修，见 E6） | E6 §3.5-6 |
| 15 | #ARCH-327：全局锁加固异常被措辞误读→静默失效数小时 | 异常类型进 warning 正文 | :2258-2267 |

## §4 待办移交

1. **D1 stats_lock 手术【不可挖·占用中】**：段锚 landing:3616-3639；占用=landing.py 工作区 MM（18+/2- 未提交；锁册无直接 claim，现活跃会话 st-zc9-lane-r3-20260930 持有的是 w0 内三文件非本文件）。手术单四小时方案已备（D1_stats_lock.md §4-§9：拆临界区+内存级联索引+batch 化+认领判定入参改"盘旗∪内存 index"+必绿清单 30+ 条+两条确定性红测）。**安全必要条件=§4.4：任何 base 已被本波越过的件绝不允许未重校验就落 dev**（09-24 热册驱逐同型字段级净损）。占用释放后 B 段开工，收益按 §2.4 诚实口径验收（锁持有面+扇出次数，~0.15s/件量级，**不申请"修完即并发达标"**——并发 1.000 的更大成分在门禁链串行段）。
2. **未解释 ~123s/笔**（deep_dive_r1 §B 残余嫌疑）：全局锁等待/落地陈旧/对账扇出——A2 分段装表（landing_phase_stats.jsonl）已就位，移交 E10 用新账回填定性；converge max 1887s 尾部事件单列核查。
3. **RB1 index 收敛臂观察期**：缺省 shadow 只判不动（决策进审计流），`.live` 翻实做与 `off` 关停双开关在 data/runtime/——观察期契约满后由 Owner 门位定翻转（ef1a02fdd6 契约）。
4. **post-checkout 钩计时缺口**（每件 reset --hard 触发，UNKNOWN）移交 E9 装表。
5. 移交 E8：落地成功后 `_run_post_commit_reconcile` 异步扇出（E5 :2838 调用点）与 auto-commit 放大环（B0_1 C1）。
6. k=6 试轮异动回 4（thresholds.yaml:290 Owner 批注）——E10 观测面盯 CPU 水位。
