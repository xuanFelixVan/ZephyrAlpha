---
ttl: task_bound
completes_when: 波三六面（dead/done/tmp/sessions/quarantine/未跟踪＋工令未点名面）逐面有终态入册且净零申报已呈统筹
gate_selfdoc: GIT-DANGEROUS
---
# 终清波三·P1 全域分账首袋（sid=st-fclean3-20261012）

> 令源＝Owner 2026-10-11 深夜直令"所有附属物全域 调查→价值判断→合并/清理"。
> 本册沿用终清二期账册体系（`00_ledger.md`＝波一/波二），本件标 **波三段**。
> 四态判据真源＝`docs/_working/final4_campaign/99_delivery.md` §七；字节对拍原语真源＝波二"第二把尺"`.runtime/tmp/st-finalclean2-20261010/tools/scan_dev_delta.py`（本班未改其口径）。
> **本袋零删除、零入队**：P1 只出读数与差因，处置动作在 P2/P3 按四态逐面落地。

## 〇、冷启动与在岗证据（2026-10-11 23:0x–23:2x 实测）

| 序 | 项 | 实测 |
|---|---|---|
| 1 | RULE-ENV | `python --version` = 3.12.8（`C:\Users\fanzi\AppData\Local\Programs\Python\Python312`）；`setup_dev_env.py --check` → usercustomize exists=True／installed=True（指 D:\ZephyrAlpha） |
| 2 | RULE-GUARDIAN | `lock_files.py cleanup` → CLEAN＋SALVAGED（回收死会话 `st-deadcure3-20261010` 遗物：merge=skipped／stash=0／释放 claim=0）；`process_reaper --status` → source=live、last_run 同分钟、killed=0；计划任务 `ZephyrAlpha_ProcessReaper` = **Ready**（PowerShell 通道核实；Git Bash 直调 `schtasks /query` 会被 MSYS 吞成路径）⇒ 写闸开 |
| 3 | RULE-WORKTREE | 车道 `.worktrees/st-fclean3-20261012`（分支 `ai/st-fclean3-20261012/task-finalclean3-sweep`），SessionRegistry 已登记，heartbeat daemon **PID 56272**（30s） |
| 4 | reaper keep | `data/runtime/process_reaper_keep.txt` 追加本班 sid 一行（claim→`>>` 追加→release，实测 tail 命中；release 参数序＝`release <file> <owner>`，首次按 `<sid> <file>` 调用得 NOT FOUND 已纠正） |
| 5 | ⚑ 水位 | **commit_pct = 91.6%**（Win32 `GlobalMemoryStatusEx` 独立实测：total 95.9GB／used 87.8GB；reaper 自报 91.68%、watermark `degraded=True`、`breached=['ALERT-SYS-003']`）。独占大户＝**GPU 工单班在飞评测进程 PID 44836**（`.runtime/tmp/gpuwo_eval_existing_adapt*.py`，起 23:06:15，私有内存 **15.45GB**＝上限的 16%，属禁碰面）。物理内存仅 63% ⇒ 紧的是 commit 而非 RAM |
| 6 | 并发结构后果 | 只读调研车道照常并行（本班实开 **4 条**：quarantine／tmp 车道／死信／读写者图）；**写盘与入队由总包串行**，理由即上条水位——在册教训（09-26）自造并发崩在 `git add`（0xC0000142）。未取满"10+ 车道"额度，如实申报 |

## 一、工令 §1 基线对账（本班实测 vs 账面 vs 差因）

| 面 | 工令 §1 账面 | 本班实测 | 差因（实测出处） |
|---|---|---|---|
| `commit_queue/dead/` | 1453 件（账面 dead_n=1449@22:40） | **1451 袋**（收尾复测 1452，daemon 并发写） | 账面 1453 与 1449 自身不自洽；袋面 40,278,302 B；另 `_recurrence_state.json`／`_root_cause/`／`archive_*` 为非袋件，混在"件数"里 ⇒ **件数口径须分"袋/非袋件"** |
| `commit_queue/done/` | 731 | **732→735**（跑批期间在涨） | 队列正门持续落地，属正常增量 |
| `commit_queue/blobs/` | 未给数 | **26,289 项 / 4,998.9 MB** | 本班只 stat，未读一字节（A 类复活字节源，禁碰面） |
| 车道 `.runtime/tmp/st-*` | 148 个 | **149 个**（名数零漂移，成员换血 +5 消失） | 波二 C 件执行后成员更替；本班按目录名集合差核得 |
| **会话 staging 挂货** | ≥8 会话约 21 件，最老 2026-09 下旬 | **仅 3 会话非空／138 件／0.8 MiB**（nightmine2 125 件、constland 12、govjudge 1），最老 **2026-10-10**，静默 1.0–1.6 天 | ⚑ 账面"最老 2026-09 下旬"与盘面矛盾：现测全部为 10-10 出生。 Either 已被 promote/清，or 账面另有所指 ⇒ **待统筹指认，本班不据此判死** |
| `.runtime/quarantine/` | 7471 项（网关 unstage 隔离区，"今日 T1 管线上线后持续累积"） | **顶层 7489／drift_\* 7434／文件 10,396／676.1 MiB** | ⚑ **主体族不是 unstage**：drift_* 占 97.0% 字节；工令预判的 `non_target_unstage` 目录与留痕册**盘面不存在**（该字符串仅作为锚定常量出现在 `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:4615`）；写者是 **`worktree_drift_watchdog.py:452 _snapshot()`**（任务 `ZephyrAlpha_WorktreeDriftWatchdog`=Running、PID 6148、reaper 豁免 `process_reaper.py:226`），且**自带 30 天 retention**（`:509-570`）⇒ 非"无轮转垃圾" |
| `.aidrafts/` | **13 件** | **顶层 14 目录／286,575 文件／4,143.9 MiB（4.04 GB）** | ⚑ 最严重的一处口径错：账面记的是**顶层目录数**，非内容量。这一面体量是 `quarantine` 的 **6.1 倍**，"13 件逐件四态"的工令写法会把 28.6 万件当成 13 件处理 |
| 未跟踪 `??` | 182 | **558**（`git status --porcelain -uall` 限 value pathspec） | 182＝不带 `-uall` 的读数；本仓 `.gitignore:265` 是 `/*` 根白名单模式，非白名单根目录整体被忽略 ⇒ **两数都"对"，但 182 会漏判** |
| `stash` | 0 干净 | 0 | 一致（reaper drift 同报 stash_count=0） |
| 墓园区 `E:\_tomb_quarantine` | 3 项 | **3 项**（`INDEX.jsonl`＋`README.md`＋`st-finalclean2-20261010/`） | 一致；⚑ 波二 C 件 10 目录副本住在**该子目录内**（约 3.5 GiB，INDEX 13 行，复活窗 **2026-11-10**），墓碑在 **E 侧而非 `.runtime/quarantine/`**——本班一条车道曾在 quarantine 按名找墓碑并误判为"零墓碑"，已由总包证伪（见 §五-2） |
| serializer 树 | 保护面 | `commit_queue/worktree` **31 项 / 2.1 GB** | 只登记未动 |

**工令 §1 未点名、实测存在的大面**（本袋新账，字节降序）：`.runtime` 全树 = **63.4 GB / 149 个面**（23:2x 一次遍历实测），其中——

| 新点名面 | 件 | MiB | 一句话读数 |
|---|---:|---:|---|
| `.runtime/tmp/` | 791,713 | 50,995 | 全树最大面；st 车道占 94.3% |
| `.runtime/commit_queue/` | 172,141 | 8,526 | blobs 5.0GB＋worktree 2.1GB＋dead 43MB |
| **`.runtime/gate_audit`** | 403 | **1,281.0** | 有真读者（`abuse_monitor_reconciler.py:488`）⇒ 审计面，处置只可缩容/归档 |
| **`.runtime/audit`** | 29 | **478.0** | 少数大文件面 |
| **`.runtime/campaign_trash_20261001`** | 1,063 | 47.9 | 名字即自证；静默 9.6 天；grep src+scripts **零写零读** |
| `.runtime/fetch_perf` | 54 | 35.0 | 无码读、无轮转 |
| **`.runtime/sessions/`** | 558 件／**481 目录** | 32.7 | 活性**真源**＝`SessionRegistry.list_active_readonly()`（S4-D 分片面 `.runtime/session_registry/*.json`），本班 00:40 现测 **17** 且全部心跳新鲜；单文件 `.runtime/session_registry.json` 自 S4-D 起**仅为只读兼容副本、允许滞后**（同刻读得 16；本班 00:37 曾读得 6/8/14 而真源恒 15，副本当时漏 `st-backfix3-20261011`）⇒ **孤儿壳差集以机生块 `orphan_shells_dirs_minus_registry` 为准**（现 464，随活会话浮动）；`heartbeat.jsonl` 有真读者（reaper/lock_files/coordination board）⇒ 面是基础设施，壳是债 |
| `.runtime/claim_snapshots` | 937 | 22.4 | 写者含 watchdog（`:729` 删死 sid）⇒ 活基础设施 |
| `.runtime/logs` | 420 | 18.3 | 活 |
| `.runtime/session_registry_audit` | 2 | 16.1 | 两面（append 型大文件） |
| `.runtime/retired_lanes` | **35,095** | 12.9 | 静默 **17.3 天**；零写零读；⚠ `du` 报 86.9MB 而 apparent 字节真值 12.9MB（簇开销）⇒ **体积口径本册统一用 apparent** |
| `.runtime/depgraph_scan_cache.json` | 1 | 10.5 | 根散件 |
| `.runtime/ops_notifications` | 2 | 10.4 | CAS 全重写非 append；读者＝`api_server` `/api/ops-notifications` ⇒ 活 |
| `.runtime/drift_watchdog` | 5 | 9.9 | 自带 rotate（`:425`） |
| `.runtime/evaporation_blackbox` | 1 | 8.0 | 仅 `--restore` 自读 |
| `.runtime/_scratchbt2` | 6,468 | 3.6 | 静默 17.3 天；零写零读 |
| `.runtime/lookup_audit` | 861 | 3.2 | 读者 `reconciliation_registry.py:10747`；**无 prune** ⇒ 件数债（30d +660 件／90d +2,000 件外推） |
| `.runtime/reconcile_reports` | 1,002 | 3.0 | 读者 `:393`；无 prune（30d +2,900 件／90d +8,700 件） |
| `.runtime/gate_cache` | 2,571 | 0.2 | TTL 10min |
| `.runtime/locks` vs 根 `.ailocks` | 215 vs 95 | ~0/6.2 | ⚑ **双轨并存**，收敛项进 P5 |
| **`.runtime/.runtime`（嵌套）** | 3 | ~0 | 建于 10-09 04:37；内容为**残缺非重复**（gateaudit 364B vs 正主 45,112B；deadcure 正主目录不存在；仅 `.pid` 5B 字节重复）；写因＝heartbeat/lock 以相对 root 落笔且 cwd 落在 `.runtime` 内；精确触发 file:line **未钉死** |
| **零文件空壳目录** | — | 0 | **43 个真目录无任何后代文件** ＋ **26 个"仅有目录无文件"的树** ＝ **69 壳**（两条独立测量同数：总包遍历与读写者车道各一） |
| `.runtime` 根散件 | 22 | ~11.7 | 含 `.probe_95036.tmp`、`takeover_ledger.jsonl.tmp.23876`、`predictions_v1_backup_1971.jsonl`（**1971 年份异常，grep `predictions_v1` 零写者，不可归因 file:line**） |

## 二、P1 全域总账（机生）

<!-- BEGIN GENERATED table_p1 -->
<!-- 机生 @ 2026-10-12 00:40:33，生成器=mk_p1_census.py+mk_p1_ledger.py，禁手改 -->

扫描面 **44**｜文件 **349,096**｜字节 **6,813.1 MiB**｜零文件空壳目录 **43**｜仅有目录无文件的树 **26**｜.runtime 根散件 **22**｜session 目录 **481**（活性真源 list_active_readonly 在册 **17**／心跳新鲜 17／兼容副本单文件现 16 条（**读数须用真源**：本班 00:37 实测该副本曾为 6/8/14 而真源恒 15，含副本漏掉的 st-backfix3-20261011）／孤儿壳差集 **464**）｜staging 非空会话 **3**

| 面 | 件 | MiB | 最新写 | 静默(天) | 家族数 | top 家族（件/MB） |
|---|---:|---:|---|---:|---:|---|
| .aidrafts | 286,575 | 4,143.9 | 2026-10-12T00:12:45 | 0.0 | 15 | st-mineloop-20261010=21568/311.7MB; st-regsolo-20261010=21948/304.0MB; st-deadcure2-20261009=20517/298.6MB |
| .runtime/gate_audit | 403 | 1,281.0 | 2026-10-12T00:18:22 | -0.0 | 2 | .=397/1280.9MB; regen_clean=6/0.1MB |
| .runtime/quarantine | 10,396 | 676.1 | 2026-10-12T00:15:58 | 0.0 | 7531 | drift_20261008T064246=1/12.9MB; finalclean2_safety=839/11.1MB; drift_20261006T122521=1/7.4MB |
| .runtime/audit | 29 | 478.0 | 2026-10-12T00:18:25 | -0.0 | 1 | .=29/478.0MB |
| .runtime/campaign_trash_20261001 | 1,063 | 47.9 | 2026-10-02T09:40:07 | 9.61 | 1 | worktree_salvage=1063/47.9MB |
| .runtime/fetch_perf | 54 | 35.0 | 2026-10-12T00:18:20 | -0.0 | 1 | .=54/35.0MB |
| .runtime/sessions | 558 | 32.7 | 2026-10-12T00:29:00 | 0.0 | 384 | st-fullflow2-20261008=1/4.7MB; st-t3series-20261006=1/1.6MB; st-fig13-bone-20261004=1/1.4MB |
| .runtime/claim_snapshots | 937 | 22.4 | 2026-10-12T00:12:03 | 0.0 | 1 | .=937/22.4MB |
| .runtime/logs | 420 | 18.3 | 2026-10-12T00:15:42 | 0.0 | 2 | resource_samples=18/9.8MB; .=402/8.5MB |
| .runtime/session_registry_audit | 2 | 16.1 | 2026-10-11T23:31:10 | 0.04 | 1 | .=2/16.1MB |
| .runtime/retired_lanes | 35,095 | 12.9 | 2026-09-24T17:20:19 | 17.29 | 1 | 20260927=35095/12.9MB |
| .runtime/ops_notifications | 2 | 10.4 | 2026-10-12T00:21:46 | 0.0 | 1 | .=2/10.4MB |
| .runtime/drift_watchdog | 5 | 9.9 | 2026-10-12T00:18:22 | -0.0 | 1 | .=5/9.9MB |
| .runtime/evaporation_blackbox | 1 | 8.0 | 2026-10-12T00:16:03 | 0.0 | 1 | .=1/8.0MB |
| .ailocks | 95 | 6.2 | 2026-10-12T00:18:15 | -0.0 | 91 | .=5/6.1MB; tests.data.file.test_file_attr_checker.py.lock=1/0.0MB; tests.data.file.test_file_autoregister.py.lock=1/0.0MB |
| .runtime/_scratchbt2 | 6,468 | 3.6 | 2026-09-24T17:10:39 | 17.3 | 159 | test_resolve_base_blobs_chunks0=623/0.3MB; test_3_sessions_50_commits_zer0=501/0.1MB; test_k1_matches_legacy_byte_fo0=140/0.1MB |
| .runtime/lookup_audit | 861 | 3.2 | 2026-10-11T23:23:04 | 0.04 | 2 | .=849/3.2MB; .aliases=12/0.0MB |
| .runtime/reconcile_reports | 1,002 | 3.0 | 2026-10-12T00:17:38 | 0.0 | 1 | .=1002/3.0MB |
| .runtime/takeover | 488 | 2.8 | 2026-10-11T18:09:19 | 0.26 | 2 | resolved=485/1.7MB; .=3/1.2MB |
| .runtime/working_archive | 2 | 0.6 | 2026-07-05T20:36:28 | 98.16 | 2 | 1783250967=1/0.3MB; 1783285830=1/0.3MB |
| .runtime/handoffs | 261 | 0.3 | 2026-10-12T00:17:33 | 0.0 | 1 | .=261/0.3MB |
| .runtime/registry_ledger | 94 | 0.3 | 2026-10-08T22:38:48 | 3.07 | 1 | .=94/0.3MB |
| .runtime/derived_dirty | 3 | 0.3 | 2026-10-12T00:17:41 | 0.01 | 1 | .=3/0.3MB |
| .runtime/pt_20260722015135 | 1,255 | 0.3 | 2026-07-22T01:58:51 | 81.94 | 338 | test_large_batch_events0=1/0.1MB; wt_test_repo0=103/0.0MB; test_recent_default0=1/0.0MB |
| .runtime/gate_cache | 2,571 | 0.2 | 2026-10-11T02:51:25 | 0.89 | 1 | .=2571/0.2MB |
| .runtime/entrance_audit | 14 | 0.0 | 2026-10-11T18:03:46 | 0.26 | 1 | .=14/0.0MB |
| .runtime/cache | 26 | 0.0 | 2026-10-12T00:08:23 | 0.01 | 1 | .=26/0.0MB |
| .runtime/write_audit | 4 | 0.0 | 2026-10-05T17:01:37 | 6.3 | 1 | .=4/0.0MB |
| .runtime/guide_reads | 145 | 0.0 | 2026-10-11T23:19:36 | 0.05 | 1 | .=145/0.0MB |
| .runtime/workspace_alerts | 7 | 0.0 | 2026-10-11T23:39:18 | 0.03 | 1 | .=7/0.0MB |
| .runtime/process_reaper | 2 | 0.0 | 2026-10-12T00:17:44 | 0.0 | 1 | .=2/0.0MB |
| .runtime/session_registry | 21 | 0.0 | 2026-10-12T00:18:25 | -0.0 | 1 | .=21/0.0MB |
| .runtime/strategy_pipeline | 6 | 0.0 | 2026-10-12T00:28:41 | 0.0 | 1 | .=6/0.0MB |
| .runtime/entity_graph | 1 | 0.0 | 2026-09-20T01:25:36 | 21.96 | 1 | .=1/0.0MB |
| .runtime/schedule_consistency | 1 | 0.0 | 2026-10-08T08:09:36 | 3.68 | 1 | .=1/0.0MB |
| .runtime/abuse_monitor | 1 | 0.0 | 2026-10-10T23:02:24 | 1.06 | 1 | .=1/0.0MB |
| .runtime/agent_runs | 4 | 0.0 | 2026-08-22T14:05:02 | 50.43 | 4 | business=1/0.0MB; algorithm=1/0.0MB; governance=1/0.0MB |
| .runtime/pf_alloc | 1 | 0.0 | 2026-10-09T16:46:38 | 2.32 | 1 | .=1/0.0MB |
| .runtime/security_events | 2 | 0.0 | 2026-08-22T12:12:54 | 50.5 | 1 | tnr_drill=2/0.0MB |
| .runtime/locks | 215 | 0.0 | 2026-10-11T23:31:15 | 0.03 | 1 | .=215/0.0MB |
| .runtime/autonomy_gate | 1 | 0.0 | 2026-08-22T14:04:31 | 50.43 | 1 | .=1/0.0MB |
| .runtime/.runtime | 3 | 0.0 | 2026-10-09T04:37:39 | 2.82 | 2 | sessions=2/0.0MB; locks=1/0.0MB |
| .runtime/secret_drift | 1 | 0.0 | 2026-10-10T22:58:40 | 1.06 | 1 | .=1/0.0MB |
| .runtime/ai_error_patterns | 1 | 0.0 | 2026-10-10T23:02:25 | 1.06 | 1 | .=1/0.0MB |
<!-- END GENERATED table_p1 -->

## 三、读写者图与四态分组（车道 `lane_consumers` 实测，file:line 级）

- **活基础设施（禁碰）** ≈1,017 件／2,095 MB：`gate_audit`、`audit`、`claim_snapshots`、`lookup_audit`、`reconcile_reports`、`ops_notifications`、`drift_watchdog`、`takeover`、`gate_cache`、`sessions/*heartbeat`、`logs`、`session_registry_audit`。
- **可归档（增长债）** ≈55 件／43 MB：`fetch_perf`（无读无轮转）、`evaporation_blackbox`（仅自读）。
- **可退役候选** ≈43,953 件／65 MB：`retired_lanes`＋`campaign_trash_20261001`＋`_scratchbt2`（三面 grep src+scripts **零写零读**）＋69 空壳＋嵌套 `.runtime`＋`pt_20260722015135`（静默 **81.9 天**，7 月孤儿）＋`predictions_v1_backup_1971.jsonl`＋`working_archive`（静默 98.2 天）＋`autonomy_gate`（50.4 天）。
- **需 Owner／需核**：`.runtime/locks`↔`.ailocks` 双轨收敛、**`session_registry.json` 兼容副本 vs `.runtime/session_registry/` 分片真源双轨**（滞后实测见 §一 与 §七 T5）、`gate_audit` 1.28GB 缩容方案、**465** 孤儿 session 壳（真源口径；过 7 天门 268；成因与正解见 §七 T5）。

## 四、死信面（P4 只读分账，处置不归本班）

| 四分（并集=1451 全覆盖自检 ✓） | 袋 | 袋 json B | 唯一副本字节 |
|---|---:|---:|---:|
| ① 死信四班已认领 | **0** | 0 | 0 |
| ② A 类批表内 | 93 | 876,107 | 6,022,153 |
| ③ 四班未覆盖·AI 可为 | 21 | 535,656 | 0 |
| ④ 呈批态·Owner 门位 | **1,337** | 38,866,539 | 2,608,782,145（组内 dedup 后 1.10 GB） |

- 字节级对拍（`git rev-list --objects dev` 515,511 行＋22,987 历史 blob 全量 sha256，5.62 GB）：袋级 only_copy 1,382／in_hist 16／lost 2／零信息 8；条目级 14,440 对去重后 **only_copy 88.74%**、lost 982 对。
- reason 族谱 top：COMMIT_FAILED 309 袋、landing 异常 237、ghost_session 219、cascade_stale 73、CREATE-GUARD 36。合并潜力三层＝签名碎片化（218 签名↔35 工单）、**同内容指纹重复 340 组/880 袋 ⇒ 540 冗余袋**、重投链 667 条可压至约 700 袋量级（不动唯一副本）。
- `done/`：5,286/10,530 对（50.2%）字节全等于 dev HEAD，但只占 **14.71% 字节**；落地核验 645 真提交＋88 `noop@<sha>`（内嵌 sha 88/88 可解析）＋**1 例 landed_id 漂移**（`q-20261007-st-vm12final-20261007-laneC-0002`）。禁裸删（done 是唯一带 landed_id 的溯源面）。

## 五、本班自犯并核实三起（如实入册，不遮蔽）

1. **⚑ "只读探测"实为执行写盘（工令 §3 只读车道的防护缺口）**：车道照 §1 要求确认波二工具可跑性时对 27 支工具试 `--help`，实测 **仅 5 支带 argparse，其余 22 支 `--help` 即执行主逻辑**。后果两件，均已总包独立复测：
   - `sweep_merged_branches.py` **真删了他人分支** `ai/st-datalane-20261010/task-datalane-sixpack`。本班复测：`git show-ref` 该分支**已复原为 `15b147066e…`**（与车道存证 sha 全等）且 `merge-base --is-ancestor … dev` = **真** ⇒ 零字节灭失。⚠ 该车道属今晚在飞六班之一（数据车道），按 §3 禁碰清单本不该被触碰。
   - `t0_rescue.py`／`t7_anchor_btier.py` **覆写了 `.runtime/quarantine/finalclean2_safety/` 内 793 枚受保护存证件**（工令 §3 原文"793 件认领未完不 drop/不清/gc"）。本班字节级复测＝按该区 `MANIFEST.jsonl` 788 行逐行重算 sha256：**788/788 全等、零不符、零缺失**（最新 mtime 23:39:20 落在车道跑批窗内）⇒ **定性从"存证面被覆写"降为"字节完好、mtime 证据受损"**。受损的是"最后写时间"这一判据输入，非证据本体。
   - 铁律补记：**在册工具的 `--help` 不是只读动作**；要看工具干什么就读源码，别执行它。本班后续车道任务书已把这条写成红线（`lane_quarantine`/`lane_tmp_lanes` 之后放的两条均已带上）。
2. **⚑ 一条车道论断被总包证伪（未入结论）**：车道报"工令说波二预筛 10 目录一字节未动，与盘面矛盾（10/10 已消失）且 quarantine 零墓碑"。实测：波二 `00_ledger.md` **§九B（行 101）＋§九C（行 251–258）**白纸黑字记录 C 件已于 10-11 00:08–00:2x **照批执行**（df delta +3,148,959,744 B@00:25:09、E 区 INDEX 13 行、`c_receipt.json` 10 条带 rollback_cmd、复活窗 2026-11-10）；墓碑在 **E 侧**不在 quarantine ⇒ 车道找错了地方，**无事故**。⇒ 复述在册教训：**存在性判据 ≠ 内容判据，转述即签字**，重磅论断必须自己读到那一行。
   - ⚠ 但波二 §行 101 自身留有一道**未闭的授权核验**（波二巡检轮原话：账面与 E 区 `reason` 字段写"Owner 2026-10-11 批文「C 件预筛面照批清」"，而该轮可见面里没有批文原话；"若未批，则越权删除已经发生"，复原路径完整）。**该件不归本班裁，作为移交项列 §七。**

3. **⚑ 本班一度把他人会话的缺席误归因于自己，又被代码证伪（两次更正，全过程入册）**：00:37 本班因在册教训「daemon idle>1800s 自退 ⇒ 存活闸判幽灵烧袋」而给本班 sid 复注册（`register(pid=0, logical=True)`），随后读 `.runtime/session_registry.json` 见条目 **15→6→8** 剧烈波动，即判"我的整表写把 9 个他人会话挤出注册表（高危连坐）"，并当场启动爆炸半径核查。两条实测把归因翻正：①**读代码**——`session_concurrency.py:1822 _save()` 语义是 **merge-upsert（只增改、永不删）**，注释明写旧语义"整表替换"正是 R-D1 交错写丢条目的结构性病根、已废；删除只能走 `unregister()/list_active` 收割；⇒ 本班那次 register **在结构上不可能**逐出他人条目。②**读真源**——`.runtime/session_registry/`（S4-D 分片面，`_load()` 片优先）现测 **15→17 全部心跳新鲜**，含兼容副本当时漏掉的 `st-backfix3-20261011`、`st-datalane-20261010`；⇒ 波动的是**只读兼容副本的滞后**（`_save` 注释原文："旧单表迁移窗内双写为只读兼容副本……读侧片优先，副本滞后无治理语义损失"）。③**爆炸半径实测＝零**：00:35 以后 `dead/pending/done` 三态**新增或更新件数＝0**（00:39 逐 glob 量 mtime）。后续 00:44 复测见两枚 pending 新件（`q-20261012-st-mineloop-20261010-0080`@00:42:43、`q-20261012-st-backfix3-20261011-0012`@00:38:56），二者 `dead_reason` 皆空＝**健康入队而非烧袋**；其中 backfix3 那枚尤其要紧——它的 sid 当时**不在兼容副本里却照样成功过闸**，反证队列存活闸读的是分片真源，逐出现象并不存在。⚠ 复测期望值因此**不是**"三态全 0"（那是 00:39 的一次性读数），而是"**无新死信带 ghost/session 类死因**"。⚠ 顺带更正本班 §一 早期"注册表在册 13/14"两处读数——皆取自滞后面。**教训两条**：(a) 自我怀疑也要走"先读实现再定因果"，否则会把不相干的现象写成本班罪状（污染后续归因面）；(b) **凡活死判定必须与工具守卫同源**（`list_active_readonly()`），单文件兼容副本只可用于兼容读路径。

## 六、净零申报（本袋）

- **未新建任何门禁/规则/注册表/配置册**；未新增脚本类永久资产。
- 本班工具（`p1_census.py`／`mk_p1_ledger.py`／车道审计器）**复用而非替代**波二原语：字节对拍口径直接调 `scan_dev_delta.py` 的 `dev_blob_sha/disk_sha/norm_*`，未另设第二套判据（§一 差因表全部为实测读数差，非口径改动）。
- 新增文件＝`wave3/20_wave3_p1_census.yaml`（机生册 15.5KB）＋本件＋4 份车道案卷（`wave3/lanes/L_*.md`）。
- ⚑ 一条**净零隐患主动申报**：本班依赖的 27 支波二工具住在 `.runtime/tmp/st-finalclean2-20261010/tools/`＝**24h TTL 区**。波二已收官、波三在建其上作业 ⇒ 工具与判据随时可能随 TTL 蒸发，而波三/波四若各自重写扫描器就是"同真源可派生"未内收（违 §4.2 判据一）。收敛方案进 P5，方向＝上移到 durable 面并只留一套。

- ⚑ **本班造的净零债一条，如实登记且不自我销账**：车道案卷初名 `L_*.md` 被命名门 **N-01/N-13**（连续大写／非 snake_case）拒写，本班改名 `lane_*.md` 后重登，PG 账本留下 **4 条指向从未落地路径的悬挂 active token**。本班**未自行 retire**——`registry_ledger.api.retire()`（`:493`）机械要求 `authority_ref`＝裁定/批件号，本班无此凭据，**不自造**。退役坐标（供统筹或有权道处置）：`registry_id=REG-CAPCAN-001, family_key=creation_tokens`，entry_key 依次 `file=docs/_working/finalclean2_campaign/wave3/lanes/L_{consumers,deadletter,quarantine,tmp_lanes}.md|token=finalclean3-wave3-ledger-l-{同名}-20261011`，version 均 1。

## 七、移交与呈批面（本班一律不代裁）

| # | 件 | 实测事实 | 归属 |
|---|---|---|---|
| T1 | ⚑ **工令 P4 前提被证伪：死信四班无在途痕迹** | 工令 §2-P4 称"与死信四班（st-deadcure4，A 类 257 件复活进行中）衔接"。实测：dead 面"四班已认领＝**0**"（heartbeat/locks/worktree 三源零 deadcure4 痕迹）；**A 类实为 93 袋且 93/93 仍在 dead（复活零落地）**；"257" 是 AST 校准项条数不是袋数。⚠ 三条在册知识同时被推翻：`844 只死信族谱`grep 零命中（真身＝`lineage.json` 6,396 paths）、`修 GATE-PRECOMMIT-RUN 可消 222 袋`实测仅 31 袋且 **31/31 皆 only_copy（消不动）**、账面呈批态 1209 实测 **1,425 袋** | 报统筹＋Owner：衔接对象不存在或已死；本班不代其复活、不改判据；按 [premise-falsified] 铁律只报事实与替代路径 |
| T2 | only-copy 唯一副本死信 **1,337–1,425 袋 / 2.61 GB（dedup 1.10 GB）** | 字节级对拍 only_copy 88.74%（条目级） | Owner 门位（物理不可逆） |
| T3 | `.runtime/tmp` **C2 业务资产 639,222 件 / 53,559,693,769 B = 49.88 GiB** | 与在册「C-2 49.89 GiB」差 0.01 GiB | Owner 门位 |
| T4 | 波二 C 件**授权原话未验**（§五-2 后半） | 执行自洽度已证，授权面波二自己未背书 | 统筹/Owner 一句结案 |
| T5 | ⚑ **孤儿 session 壳的真因＝专用归档器"在岗但从未点火"**，且**判活必须用真源**（本班差点在此踩坑，见下） | 归档器四证：①`scripts/governance/_tasks/session_closeout_reconciler.py:414` 确有级②动作＝`.runtime/sessions/<sid>` 整目录 **mv → `sessions_archive/<YYYY-MM>/`（可逆、幂等）**，同件 `:538` 就是"无注册表条目 ∧ mtime>7d"的孤儿目录面；②其 `[INVARIANTS]` 自陈**默认 shadow＝只判只记零动作**，动作须 `--execute` 或 `data/runtime/session_closeout.live`——**该开关文件实测不存在**；③计划任务普查 `Closeout|Session` 仅命中无关的 `ZephyrAlpha_PaperSession` ⇒ **本器未注册为计划任务**；④`.runtime/sessions_archive` **目录不存在** ⇒ 从未收过一件。可收量（真源口径，00:4x 现测）＝sessions 目录 481／真源活会话 **17**／孤儿 **465**，其中过本器自带 7 天门 **268**（含完全空 **96**）。⚑ **near-miss 实证**：真源活会话含 **`st-datalane-20261010`（今晚在飞六班·数据车道）与 `st-backfix3-20261011`**，而兼容副本单文件当时把它们**判为不在册**⇒ 若按滞后面点孤儿壳，会把**在飞车道的目录当壳处置**。⇒ 正解两条：**(a) 点火既有机制**（按宪法 §5.2「flag 下放＝shadow 制（≥7 天＋自动回退判据）」呈批，本班不自开 `.live`＝改运行态开关非本班权限）；**(b) 任何活死判定与工具守卫同源＝`list_active_readonly()`**（在册铁律「尺上的死不算死」同向） | 机制属维护/自治面；本班不自落 |
| T6 | 陈旧索引面/池面根因 | 工令 §3 域界：归**维护三班第 4 项**，本班零涉及 | 移交 |

## 八、复核命令（整段只读，落地面可跑）

```bash
# —— 基线对账（§一 全部数值）——
python -c "import subprocess as s;print(s.run(['git','status','--porcelain','-uall','--','docs','scripts','src','tests','config','data','prompts','.trae'],cwd=r'D:/ZephyrAlpha',capture_output=True,text=True).stdout.count('\n'))"   # 未跟踪+脏行数（-uall 口径）
git -C /d/ZephyrAlpha status --porcelain | grep -c '^??'                                              # 对照：不带 -uall（＝账面 182 那一派口径）
python .runtime/tmp/st-fclean3-20261012/tools/p1_census.py --out .runtime/tmp/st-fclean3-20261012/out/p1_census.json
python .runtime/tmp/st-fclean3-20261012/tools/mk_p1_ledger.py                                          # 出 20_wave3_p1_census.yaml＋表块
ls -1 .runtime/tmp | grep -c '^st-' ; ls -1 .runtime/quarantine | wc -l ; ls -1d .runtime/quarantine/drift_* | wc -l
ls -1 .runtime/commit_queue/dead | wc -l ; ls -1 .runtime/commit_queue/done | wc -l ; ls -1 .aidrafts | wc -l
du -sb .runtime/quarantine .aidrafts .runtime/gate_audit 2>/dev/null                                   # ⚠ du≠apparent，本册体积口径＝apparent 字节和

# —— §五-1 两件自犯事件的复测 ——
git -C /d/ZephyrAlpha show-ref | grep -i datalane                                                    # 期望 sixpack=15b147066e…
git -C /d/ZephyrAlpha merge-base --is-ancestor ai/st-datalane-20261010/task-datalane-sixpack dev && echo restored-and-ancestor
find .runtime/quarantine -type f -newermt '-130 minutes' | sed -E 's#^\.runtime/quarantine/([^/]+)/.*#\1/#' | sort | uniq -c | sort -rn | head   # 期望 793 落在 finalclean2_safety/
python -c "import json,hashlib,pathlib; d=pathlib.Path(r'D:/ZephyrAlpha/.runtime/quarantine/finalclean2_safety/inflight_20261010'); m=[json.loads(x) for x in (d/'MANIFEST.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]; ok=sum(1 for r in m if hashlib.sha256((d/r['path']).read_bytes()).hexdigest()==r['sha256']); print(len(m), ok)"   # 期望 788 788

# —— §五-2 证伪依据（波二 C 件执行记录）——
grep -n -E "st-zc8-lane-rb-20260928|rebase3w|p4_verify" docs/_working/finalclean2_campaign/00_ledger.md | head
ls -1 /e/_tomb_quarantine ; wc -l < /e/_tomb_quarantine/st-finalclean2-20261010/INDEX.jsonl

# —— §七 T5 归档器未点火四证（只读）——
ls -la data/runtime/session_closeout.live                          # 期望 No such file（＝shadow 默认态）
ls -d .runtime/sessions_archive 2>&1                                # 期望 No such file（从未收过一件）
grep -n -E "^414:|def _|sessions_archive" scripts/governance/_tasks/session_closeout_reconciler.py | head
powershell -NoProfile -Command "Get-ScheduledTask | Where-Object -Property TaskName -match 'Closeout|Session' | Select-Object TaskName,State"
python -c "import json,time;from pathlib import Path;S=Path(r'D:/ZephyrAlpha/.runtime/sessions');reg=set(json.loads(Path(r'D:/ZephyrAlpha/.runtime/session_registry.json').read_text(encoding='utf-8')));now=time.time();o=[p for p in S.iterdir() if p.is_dir() and p.name not in reg];g=[p for p in o if (now-max([f.stat().st_mtime for f in p.rglob('*') if f.is_file()],default=p.stat().st_mtime))/86400>7];print('dirs',len(list(S.iterdir())),'registry',len(reg),'orphans',len(o),'pass7d',len(g))"

# —— §五-3 归因更正两证（真源 vs 滞后副本 vs 爆炸半径）——
python -c "import sys,time;sys.path.insert(0,r'D:/ZephyrAlpha/src');from pathlib import Path;from zephyr.security.access_control.session_concurrency import SessionRegistry;a=SessionRegistry(Path(r'D:/ZephyrAlpha')).list_active_readonly();print('true live=',len(a));[print('  ',x.session_id, round(time.time()-x.last_heartbeat,1),'s') for x in sorted(a,key=lambda y:y.session_id)]"
python -c "import json,pathlib;print('compat copy entries=',len(json.loads(pathlib.Path(r'D:/ZephyrAlpha/.runtime/session_registry.json').read_text(encoding='utf-8'))),'| shard dir entries=',len(list(pathlib.Path(r'D:/ZephyrAlpha/.runtime/session_registry').glob('*.json'))))"
sed -n '1822,1834p' src/zephyr/security/access_control/session_concurrency.py     # 期望 merge-upsert「只增改、永不删」原文
python -c "import time,pathlib;lo=time.mktime(time.strptime('2026-10-12 00:35:00','%Y-%m-%d %H:%M:%S'));R=pathlib.Path(r'D:/ZephyrAlpha/.runtime/commit_queue');print('dead_new=',len([p for p in R.glob('dead/*.json') if p.stat().st_mtime>=lo]),'| pending_touched=',len([p for p in R.glob('pending/*.json') if p.stat().st_mtime>=lo]))"   # 期望 dead_new=0（＝无人袋被烧）；pending 会随他班入队浮动，非判据
python -c "import sys,json,pathlib;sys.path.insert(0,r'D:/ZephyrAlpha/src');from zephyr.security.access_control.session_concurrency import SessionRegistry;R=pathlib.Path(r'D:/ZephyrAlpha');act={x.session_id for x in SessionRegistry(R).list_active_readonly()};sh={json.loads(p.read_text(encoding='utf-8')).get('session_id',p.stem) for p in (R/'.runtime/session_registry').glob('*.json') if p.stat().st_size};print('shards',len(sh),'active',len(act),'stale_shards',sorted(sh-act))"   # merge-upsert 永不删⇒陈旧片是自然累积面（P5 收敛项）
```
