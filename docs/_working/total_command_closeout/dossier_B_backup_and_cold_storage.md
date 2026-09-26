---
ttl: task_bound
---

# 案卷 B — 灾备 / 冷存线（实测读数，无裁定）

- 核验时点：2026-09-26 约 14:30 +0800
- 落地判据面：`git show HEAD:<path>`，HEAD = `54622bbb`（dev，2026-09-26 13:42:15 +0800）
-  sid 建议：st-backup-cold-20260926-follow
- IO 重项（F/G/E 盘扫描、CH 探针、目录树统计）按窗口纪律处置，见各条「备注」。

## 一、主表

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---|---|---|---|
| 1.1 | 交接书：backup.ps1 含 stage_timeline | `git show HEAD:scripts/backup/backup.ps1 \| grep -c stage_timeline` | 2（文件存在，992 行） | 中 |
| 1.2 | 交接书：backup.ps1 含 error_sample | 同上 `grep -c error_sample` | 1 | 中（计数=1，非多点埋点） |
| 1.3 | 交接书：reconciler 含 launch_detached_backup | `git show HEAD:scripts/backup/backup_reconciler.py \| grep -c` | 2 | 中 |
| 1.4 | 交接书：reconciler 含 settle_previous_ignition | 同上 | 6 | 中 |
| 1.5 | 交接书：reconciler 含「点火前锁自查」 | 同上 grep -c `点火前锁自查` | 字面 0；变体「点火前主动锁自查」命中 L8(INV-12)/L54/L787/L813，实现函数注释 L470 | 中（符号名不符，实体在） |
| 1.6 | 交接书：process_reaper P-19 外层 finally 快照 | `git show HEAD:src/zephyr/trading/process_reaper.py \| grep -c` | `P-19`=0；`finally`=1；文件 1266 行 | 不符（HEAD 码内无 P-19 字样，finally 仅 1 处，需定位归属） |
| 1.7 | 交接书：_kill_pid_tree 有 AccessDenied 分支 | 同上 | `_kill_pid_tree`=4，`AccessDenied`=16 | 中 |
| 1.8 | 交接书：tests/dr/test_backup_lock_semantics.py 在 HEAD | `git ls-tree HEAD -- <p>` | 在，blob `53dcb1d9`；`git status --porcelain` 空（干净）；内含 test 定义 5 例，487 行 | 中 |
| 1.9 | 交接书：heartbeat_daemon.py 流容错 | `git show HEAD:.../heartbeat_daemon.py \| grep -c` | 495 行；`UnicodeDecodeError`=0 `JSONDecodeError`=0 `errors=`=0 `broken`=0；`except`=17 | 待定（见 1.9b 深挖） |
| 1.10 | 交接书：restore_drill.py 含 judge_drill | `git show HEAD:scripts/backup/restore_drill.py \| grep -c` | 5（文件 721 行） | 中 |
| 1.11 | 交接书：tests/backup/test_restore_drill.py 在 HEAD | `git ls-tree HEAD -- <p>` | 在，blob `33b79a0a`；porcelain 空；test 定义 23 例，510 行 | 中 |
| 1.12 | 交接书：services_registry.py 备份探针 | `git show HEAD:src/zephyr/frontend/dashboard/services_registry.py \| grep -ci backup` | 24 次命中（文件 1372 行） | 中 |
| 1.13 | **风险1 特核**：test_services_registry_backup_probe.py 是否仍在 HEAD 跟踪面 | `git ls-tree HEAD -- <p>` ／ `git status --porcelain -- <p>` | ls-tree **在**（blob `1513f7e5`）；porcelain 双行 `D  <p>` + `?? <p>`＝index 记删除＋磁盘副本转未跟踪；磁盘副本 13627 字节 = HEAD 13627 字节，sha256 两侧同为 `1b441500…50be` | 中（HEAD 跟踪面仍在；主区 index 挂删除，工作区内容未变） |
| 1.14 | 交接书风险1：主区 index 有 141 件 staged 删除 | `git status --porcelain \| grep -c "^D "` | 141（porcelain 总行数 459） | 中 |
| 1.6b | 同上（P-19 补读） | `git show HEAD:…process_reaper.py` 定位 | HEAD L1047-1059：外层「无论本轮死在哪一步，状态快照都要落盘」＋`finally`（L1059）＋`except` 记 `reaper 本轮中途失能（快照仍落盘，异常照抛）`；落地 commit 时间轴 `bce9d7a80a` 01:49:26（P-19 治本 v2）→ `dc1c66e651` 02:30:20（P-19 续：_kill_pid_tree AccessDenied） | 中（实体在，标记名 P-19 未入码） |
| 1.9b | 交接书：heartbeat 流容错 | `git show HEAD:…heartbeat_daemon.py` 定位 | HEAD L191 `_ensure_usable_streams()`：`sys.stdout is None → _NULL_STREAM`、`sys.stderr is None → _NULL_STREAM`（pythonw 无控制台实测复现），入口 L465 先调；L456-458 自述；L478 `except BaseException` 入口级兜底＋L489 落痕失败也不回抛 | 中（流容错＝None 标准流兜底，非解码容错） |
| 2.1 | **P-28**：孵化腿是否杀前复验 name/cmdline | 读 `git show HEAD:src/zephyr/trading/process_reaper.py` L982-1040 | 判据链：`pid=rec["child_pid"]` → `pid not in live_pids: continue`（**仅验存在**）→ 寿命 `now>spawned+lifetime` → 白名单/keep 匹配用的是**台账记录的 `rec["cmd"]`**（L1005/L1011），非活体 cmdline；`live_name` 只进日志（P-12 归因）；`create_time` 在 `all_procs` 内可得（L600 快照含 name/ppid/create_time/cmdline）但本腿**从未比对**；随后 `killed=_kill_pid_tree(pid)` 按 PID 树杀 | 不符（无复验；对比腿 `kill_ghost_windows` L717-737 有 recheck＋classify 重跑赦免） |
| 2.2 | P-28：今日 KILLED 行统计 | `data/runtime/reaper_kill.log`（utf-8 读，全 663 行） | 今日（2026-09-26）行 64：tag=KILLED 33 / tag=DRY-RUN 31；KILLED 中 `[FAILED]` 7、无 FAILED 26；今日非孵化腿行 3（`reason=idle_aged`） | 中 |
| 2.3 | P-28：name=svchost.exe 是否真有 FAILED | 同上逐行 | name=svchost.exe 共 20 行，其中 **tag=KILLED 仅 5 行且 5 行全带 [FAILED]**：01:58:34 PID=2628 / 01:58:34 PID=6732 / 01:58:34 PID=2412（另 07:17:33 PID=37420、09:01:37 PID=8628）；其余 15 行是 **DRY-RUN** tag（01:22:11/01:26:20/01:27:50/01:28:43/01:29:31 各 3 行，同 3 PID 反复出现） | 中（FAILED 确在，但「杀成功」面需按 2.4 读） |
| 2.4 | P-28：活体名与台账 cmd 不一致面 | 逐行比对 `name=` vs `cmd=` | KILLED-tag 且活体名非 python/pythonw 共 18 行；其中 7 行 [FAILED]（NgcIso.exe×1、NVIDIA Overlay.exe×1、svchost.exe×5）；**11 行无 [FAILED]（即 `_kill_pid_tree` 返 True）**：02:29:20 backgroundTaskHost.exe、02:32:09/03:27:36/04:17:45×2/07:57:34 conhost.exe、02:52:15/03:01:47/04:21:55/04:27:39/08:27:31 bash.exe；全部 33 行 KILLED 里 name/cmd 一致仅 19 行 | 中（不一致率读数高；「killed=True 但活体是 conhost/bash」为 PID 认人直接后果读数） |
| 2.5 | P-28 时间轴对齐 | `git log --format='%h %ci %s' -- src/zephyr/trading/process_reaper.py` | 该文件近三次改动：`30505c93f6` 01:15:39 → `bce9d7a80a` 01:49:26（P-19 v2）→ `dc1c66e651` 02:30:20（P-19 续，AccessDenied 永不抛）→ HEAD `54622bbbf` 13:42:15（未触该件）。log 读数分段：01:22—01:29 的 15 行 svchost DRY-RUN **早于** dc1c66e651；01:58 的 5 行 FAILED 落在 bce9d7a80a 之后、dc1c66e651 之前；**07:17:33 与 09:01:37 两条 svchost [FAILED] 在 dc1c66e651 之后**＝AccessDenied 治本后该签名仍复现 | 中 |
| 3.1 | **P-26**：06:00 轮 336,678 件定性 | `logs/backup_report_20260926_060003.json`（utf-8-sig） | duration_seconds **7997.2**；`code_backup.status="failed"` 而 `robocopy_exit=0`；copied **336678**、hardlinked **0**、failures **1**、vanished 3；error_sample＝`docs\01_policies_and_standards\sop\audit_prompts_20_ai.md : 设置"LastWriteTimeUtc"时发生异常:"…访问被拒绝。"`；`mode="versioned"`、day_target/prev_snapshot 同为 `G:\backup\working_vault\20260926`（同日增量刷新 Mode B）；顶层 `timestamp=2026-09-26T08:13:20`（＝结束时刻，文件名 06:00:03 是起跑） | 中 |
| 3.2 | P-26：与 13:38 轮对照 | 同目录近 5 份报告 | 133822：status ok / dur 589.7 / copied **63** / hl 0 / fail 0；120348 ok 758.8 19；105457 ok 728.4 22；100018 ok 806.3 49；091502 ok **1943.7** copied **705**。**五轮 hardlinked 恒为 0** | 中（06:00 与其余轮差 3—4 数量级；705 轮的 1943.7s 显示耗时与 copied 不成比例） |
| 3.3 | P-26：stage_timeline 归因 | 同报告 `stage_timeline` | 累计秒：Pre-check 0.3 / Stage2 0.4 / Stage3 247.6 / Mode B 248.5 / `Diff source vs snapshot` 248.5 / **Stage 3b: Git bundle refresh 7795.6** / 3c 7795.6 / 3d 7799 / Stage4 7997.2 → 「Diff 快照」到「Stage 3b」之间 **7547.1s 无任何检查点命名**，主体耗时无阶段标签 | 中 |
| 3.4 | P-26：.worktrees 是否在被排除清单 | `git show HEAD:scripts/backup/backup.ps1` L139-146 / L586-587 | L139 默认 `$ExcludeDirs = @(".git","node_modules","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache",".runtime",".aidrafts","tmp",".venv")`——**无 `.worktrees`**；但 L141-143 若 config（`scripts/backup/backup_config.yaml`，L32 定义）含 `exclude_dirs: [...]` 则整体覆盖默认；robocopy 侧 L586 `$rcArgs += "/XD"; $rcArgs += $ExcludeDirs` | 待定（HEAD ps1 默认清单不含 .worktrees；生效清单须读 backup_config.yaml，见 G-5） |
| 3.5 | P-26：「.worktrees 占 93.8%」分母口径 | 未做全树递归（窗口纪律） | 我的口径 A 读数（轻）：`git ls-files`＝17,775（受版本管理文件数）；`.worktrees` 目录条目＝**52**（`find -maxdepth 1 -type d`＝53 含自身，`-type f`＝0）；`git worktree list`＝**73** 行；仓库根顶层条目＝45。93.8%×336678≈315,800 落在 .worktrees 的声称**无法**用 52×17,775＝924,300（上界，含未跟踪/忽略）或 73×17,775＝1,297,575 反推闭合 | 待定（比例声称未复算，缺全树计数） |
| 6.1 | keep 名单卫生 | `data/runtime/process_reaper_keep.txt` | 总 206 行；注释行 24；有效条目 `grep -vc '^#\|^$'`＝**167**（206−24−空行）；含 `commit_queue` 的行＝L104 `commit_queue`、L107 `commit_queue_landing`、L119 `commit_queue.py drain`；含 `pytest` 的行＝L9 `-c .runtime/tmp/pytest_min.ini`、L11、L12、L32、L77、L80（裸 `pytest`）、L124、L125、L127、L156、L171 | 中 |
| 6.2 | keep 匹配语义（判「参数含路径即永久免死」） | HEAD L273-282 `_is_whitelisted` | `for sub in keep_subs: if sub in cmdline` ＝**朴素子串匹配、大小写敏感、不切分 argv**；调用面两处：L1086 主腿（cmdline＝活体 cmdline）＋L1011 孵化腿（cmdline＝台账记录 cmd）。L9 条目写 `.runtime/tmp/...` 正斜杠，与 Windows 反斜杠 cmdline 不同形 | 中（免死面＝cmdline 任意位置子串命中，非仅程序名） |
| 6.3 | 孵化台账复算 1492/561/438 | `.runtime/process_incubator/ledger.jsonl`（HEAD 代码 L924 定义路径；mtime 14:31 活跃） | 实测总行 **1515**（声称 1492）；`grep -c commit_queue`＝**582**（声称 561）；`grep -c pytest`＝**438**（声称 438，逐位合）；未收口记录（无 reaped 且无 exited_at）＝**1324**，其中 child_pid 已不在进程表＝**1300**（＝98.2% 僵尸账）；open∩commit_queue＝550（其 PID 已死 534）；「open＋PID 活＋已超寿命」＝**23**，其中被 keep/白名单豁免 16、剩 7 为可杀候选 | 不符（前两项数字被现态超出；438 合） |

| 3.4b | P-26：生效排除清单（G-5 闭合） | `git show HEAD:scripts/backup/backup_config.yaml` L34 | `exclude_dirs: [".git", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".runtime", ".aidrafts", "tmp", ".venv"]`——**清单内无 `.worktrees`**；同文件 L32 `source: "D:\\ZephyrAlpha"`、L44 `working_vault.base: G:\\backup\\working_vault`；磁盘文件与 HEAD 一致（porcelain 空） | 中（.worktrees 未被排除＝方向与声称一致） |
| 4.1 | **P-27** 唯一硬失败件只读位 | python `os.stat`＋`stat.S_IWRITE`＋`GetFileAttributesW`（未用 attrib） | 路径存在；`st_mode`＝**0o100444**；`S_IWRITE` 位＝**False**（只读成立）；`S_IREAD`＝True；`dwAttr`＝0x21→READONLY 位 True；size 82,225；mtime **2026-09-25T00:54:08** | 中（before 读数＝只读；本卷未修改该件） |
| 4.2 | P-27 与 P-26 关联性 | 06:00 报告 error_sample vs 路径 | 报告 `error_sample` 指向同一文件（`…设置"LastWriteTimeUtc"时发生异常:"…访问被拒绝。"`），`failures=1` 与只读位互证 | 中 |
| 5.1 | 灾备运行态 `data/databases/backup_state.json` | python json 读（utf-8-sig，28 键） | `last_backup_time=2026-09-26T13:48:12.3818844+08:00`；**无 `status` 键**→真名 `last_backup_status="ok"`；**无 `log_verified` 键**→真名 `last_backup_log_verified=False`；`last_run_outcome="lock_skipped"`；`last_ch_backup_status="skipped"`（`last_ch_skip_reason="24h cadence (last 13.0h ago)"`）；`last_session_id=st-sim-launch-20260923`；`last_ch_vm_backup_time=2026-09-26T06:54:36` success=True path=F:\ch_vm_backup；`last_ch_vm_autocheck_result="full_backup_done"`；`last_ch_vm_version="ClickHouse server version 26.6.1.1193"`；`last_ch_backup_verified=True`（09-25 15:06 inc.zip 88,580,255,288 B）；文件 mtime 13:48:12 | 中（声称的键名两个不存在，取到的是同义键；`last_backup_status=ok` 与 `last_run_outcome=lock_skipped` 并存） |
| 5.2 | 最新 3 份报告 status/时长序列 | `logs/backup_report_*.json` 按 mtime | 133822 ok 589.7s copied63 / 120348 ok 758.8s copied19 / 105457 ok 728.4s copied22（再往前 100018 ok 806.3s copied49、091502 ok 1943.7s copied705）；060003 为唯一 failed 7997.2s | 中 |
| 5.3 | 三计划任务 State/NextRunTime（只读） | `Get-ScheduledTask`＋`Get-ScheduledTaskInfo` | ZephyrAlpha-DailyBackup｜Ready｜Next 2026/9/27 6:00:00｜Last 2026/9/26 6:00:01｜LastTaskResult 0；ZephyrAlpha-WeeklyVMBackup｜Ready｜Next 2026/10/3 6:00:00｜Last 2026/9/26 6:00:00｜Result 0；ZephyrAlpha_ProcessReaper｜Ready｜Next 2026/9/26 14:37:22｜Last 2026/9/26 14:31:28｜Result 0 | 中（三任务在册，未改；Reaper 6 分钟节奏且 14:31 轮 Result=0） |
| 7.1 | 冷存清单行数与 .bak sha | python＋sha256 实算 | `F:\zephyr_cold\50_archive\by_project\zephyralpha\archive_manifest.jsonl` 存在，**2515 行**（声称 2210）size 780,665，sha256[:8]＝c36d01d5；同目录 `.prepathfix_20260926.bak` size 716,572，sha256[:8]＝**299f80dd**（全值 `299f80dd7b6dcfd29a031d5cf4c2493758bf9b73852fe4f4e22175277f4e75ac`，与 drawers 登记逐位合） | 不符（行数声称取的是改锚前 2,210 这条「仍记 E 原址」子集数，非现行数） |
| 7.2 | `00_manifest\drawers.jsonl` 第 11 行 | python readlines[10] | 全文 **11 行**，第 11 行＝2026-09-26 审计班 P-1 登记：`"archive_manifest.jsonl 改锚前全量副本（2,515 行，其中 2,210 行仍记已删卷宗 E:/zephyr_cold_archive 原址）"`，改锚规则＝前缀替换 E:\zephyr_cold_archive\ → F:\zephyr_cold\50_archive\by_project\zephyralpha\，「零删除：本 .bak 即改前原件全量副本」 | 中 |
| 7.3 | 盘符可达性（df 级） | python `os.listdir`＋`shutil.disk_usage` | F:\ 可达（7 项）free 167.6 GiB／总 1863.0；G:\ 可达（6 项）free **1454.4 GiB**／总 3726.0；E:\ 可达（71 项）free 296.0 GiB；D:\ free **40.8 GiB**／总 731.2 | 中（无不可达盘；D 侧余量 40.8 GiB 低于 config `working_vault.free_floor_gb: 60` 的口径对象为 vault 所在盘 G，非 D） |
| 8.1 | **CH 全库 system.\* 永久失败**声称 | DatabaseService reader `execute` | `SELECT count() FROM system.macros` → **返回 [(0,)]**；`FROM system.parts` → **[(29053,)]**；`system.databases` → [(5,)]；**未抛错** | 不符（探针面可查，与「永久失败」相反） |
| 8.2 | 「一张表攒 >100 零字节破损件」 | `SELECT count() FROM system.parts WHERE bytes=0` | **0**；按表分组 `WHERE bytes=0 GROUP BY table` → **空集**（注：列名是 `bytes`，首轮用 `size` 触发 ServerException Code 47 Unknown identifier，属探针写法问题非服务端故障） | 不符（系统表面读不到零字节破损件；文件面未查，见 G-9） |
| 9.1 | g_mirror 是否仍含 ch_vm_backup（HEAD 现态） | `git show HEAD:scripts/backup/backup_config.yaml` L65-73 | HEAD targets **仅 `zephyr_cold` 一条**；`ch_vm_backup` 目标不在；注释自述「2026-09-24 ch_vm_backup 目标移除…不再 /MIR」 | 中（HEAD 无该镜像目标） |
| 9.2 | 「6b7749d4a8＝反向复活」声称 | `git log --oneline -3 6b7749d4a8`／`git show 6b7749d4a8 -- scripts/backup/backup_config.yaml` | 该 commit（2026-09-24 11:28:50，标题为审计收官轮）对 config 的 diff：`-`「ch_vm_backup 目标移除」注释 → `+`「阶段4.6 改址…镜像仅剩冷库+ch_vm_backup」并 **`+` 重新写入 `- id: ch_vm_backup / source: F:\ch_vm_backup / target: G:\backup\ch_vm_backup`**；其前邻 `e3cff4e6fc`（09-24 11:26:36，即摘除动作）仅早 **2 分 14 秒**＝被同文件覆盖式回退 | 中（「反向复活」在 diff 面成立） |
| 9.3 | 复活之后是否已再纠正 | `git log -6 -- scripts/backup/backup_config.yaml` | `3cdafddf1d` 2026-09-25 20:56:35「ch_vm_backup 策略切换固化重落（前落被 stale-index 回退）」＝HEAD 前最后一次改动，现态已无该目标 | 中 |
| 9.4 | G 侧 data.vhdx 事实 | python `os.path.getsize`（只 stat） | `G:\backup\ch_vm_backup\data.vhdx` **存在 635,189,592,064 B（591.5 GiB）**；`boot.vhdx` 4,194,304 B；源侧 `F:\ch_vm_backup\data.vhdx` 643,175,546,880 B（600 GiB）、`boot.vhdx` 同 4 MiB、另有目录项 `zephyr-ch`；G:\backup 顶层＝ch_vm_backup/db_dumps/git_bundles/offrepo/predelete_deltas/README.md/working_vault；**`G:\backup\ch_vm_archive` 不存在**（`e3cff4e6fc` 标题用词为 ch_vm_archive，HEAD 注释与实盘用 ch_vm_backup） | 中（差值 F−G＝7,985,954,816 B≈7.4 GiB，两侧非同尺寸） |
| 10.1 | restore_drill 建库语句（P-22） | `git show HEAD:scripts/backup/restore_drill.py` L64/L105-113 | L64 `_SQL_CREATE_DRILL_DB = "CREATE DATABASE " + _DRILL_DB`——**无 TEMPLATE、无 LC_COLLATE、无 ENCODING 子句**；规避面＝L111 `_PK_ORDER["lib_assets"] = 'asset_id COLLATE "C"'`（钉 COLLATE）；码内注释自述实测：演练库 datcollate 继承 template1＝「Chinese (Simplified)_China.936」，生产库 depgraph datcollate＝「C」，不钉则两侧各取前 N 零交集（lib_assets common=0、lib_events 各取尾 common=0） | 中（靠钉 COLLATE 规避成立；LC_COLLATE/TEMPLATE 未修） |
| 3.6 | P-26：全树文件计数（分母口径实定，非重 IO） | python `os.scandir` 全树遍历，应用 config L34 排除清单＋`*.pyc/*.db-wal/*.db-shm`，52 目录全走 | **`.worktrees`＝497,798 件**；主树（去 .worktrees）＝40,810（目录内）＋27（根散文件）＝**40,837**；源树合计＝**538,635**；**`.worktrees` 占比＝92.42%**（elapsed 3.2s＋0.2s，属轻 IO）；.worktrees 内 52 目录中 **7 个为空**（0 件），非空者众数 ≈17.2k（top：st-ailayer-final-20260924 17,899 / csx-pkg7 17,760 / csx-pkg9 17,754） | 中（声称 93.8% vs 实测 92.42%，方向合、数值差 1.4pt；主树 top 目录：data 21,111、docs 8,491、src 4,040、tests 3,872） |
| 3.7 | 336,678 与全树计数的口径关系 | 3.1 报告字段 vs 3.6 全树 | 现态全树 538,635 ＝ 13:38 轮的 **8.5 倍**、06:00 轮 copied 的 **1.6 倍**；06:00 轮是 Mode B「同日夜快照增量刷新」，其 copied 为 diff 集非全量——故 93.8% 的比例声称对应的是**全树占比口径**，而 336,678 是**增量计数口径**，两者不同轴 | 中（比例声称可由全树口径近似支撑，但不能由 336,678 反推） |

## 二、新增发现（交接书未提）

- N-1 `scripts/backup/restore_drill.py` HEAD L8 自述判据版本 `P-3R2`，并明文写「文本主键必须钉 COLLATE "C"（演练库 datcollate 继承 template1，与生产库 C 不同，不钉则两侧取样行集零交集）」；L111 实现 `lib_assets: 'asset_id COLLATE "C"'`。＝P-22「钉 COLLATE 规避」在 HEAD 实存且写进不变式声明。
- N-2 `backup_reconciler.py` L8 INV-13 自述：post-commit 通道「只点火不托管」，`backup.ps1` 经瞬时 `powershell Start-Process -WindowStyle Hidden` 脱离启动，目的是让备份进程「在收割器扫描时不是 worker 的活的后代」从而免疫级联收割。＝非托管免疫设计在 HEAD 内，且其成立条件与 P-28 的 PID 认人问题是两条独立面。
- N-3 `backup_reconciler.py` L393 注释自认：主动锁自查「只是少起一个注定撞锁的子进程的优化」，真正锁语义在别处（非唯一防线）。
- N-4 error_sample 在 backup.ps1 仅 1 处命中，与 stage_timeline 的 2 处不对称——单点采样而非全链路采样。

- N-5 06:00 轮报告自相矛盾读数：`code_backup.status="failed"` 与 `robocopy_exit=0` 并存，且降级由 `failures=1` 单件驱动——单文件写时间戳被拒即把 336,678 件整轮标 failed（P-26 与 P-27 同一根因两面）。
- N-6 近 5 份报告 `hardlinked` **恒为 0**，而 Stage 3 检查点名自称「versioned vault, hardlink dedup」——去重通道在现态读数上无产出，同日夜间每轮仍全量遍历。
- N-7 同报告 `git_bundle.status="skipped" reason="fresh" age_days=0.3`，而 Stage 3b（Git bundle refresh）标签前后正是 7547s 空窗——耗时不在 bundle 名义动作上；`offrepo_backup.cold_archive` 记 `robocopy_exit=1 bytes=147,612,158,404`（137.4 GiB），`bytes` 字段语义（总量 vs 新拷）未在报告内声明。
- N-8 `g_mirror.targets.zephyr_cold.robocopy_exit=3` 被判 `status="ok"`（robocopy 3＝1|2＝有拷贝＋目的端多余项）。
- N-9 `databases.clickhouse.status="skipped" reason="service down"` 出现在 06:00 轮报告内——备份链自述 CH 侧未参与。
- N-10 keep/白名单在孵化腿匹配的是**台账 cmd**（L1005/L1011），叠加「豁免分支 `continue` 不写 reaped_ids」＝被豁免记录永不收口；台账现态 1324 条 open 中 1300 条 PID 已死（98.2%），与该机制同向。
- N-11 `.worktrees` 目录实测 **52** 个条目（全为目录，0 文件），而 `git worktree list` 为 **73** 行——交接书「主区 .worktrees 实测 73 个 worktree」把两个口径并成一谈。
- N-12 `data/runtime/reaper_kill.log` mtime＝09:31:38，距核验时点（14:30 后）约 5 小时无新行；同期 `heartbeat.jsonl`/孵化台账仍在写（ledger mtime 14:31）——收割日志静默与台账持续增长并存。

- N-13 **本卷自纠读数**：3.6 的初版实现从仓库根递归时未生效 `.worktrees` 跳过项，把主树读成 538,635（＝全树，含 .worktrees 双计）；改用「逐 top-level 目录」重跑得主树 40,810＋27＝40,837（0.2s）——3.6 采用的是复算值。凡引用本卷占比者按此口径。
- N-14 keep 名单形态读数：L80 是裸子串 `pytest`（任何含 `pytest` 的命令行＝两条腿永久豁免）；L9 `-c .runtime/tmp/pytest_min.ini` 用**正斜杠**，而孵化腿比对的台账 cmd 在 Windows 侧多为反斜杠形如 `D:\ZephyrAlpha\.runtime\...`——该条命中与否取决于 spawn 时的写法，非稳定豁免。
- N-15 任务级成功码与业务级结论脱钩：三计划任务 `LastTaskResult` 均为 0，而其中 DailyBackup 的 06:00:01 那轮报告 `code_backup.status="failed"`；另 5.1 中 `last_backup_status="ok"`（13:48 轮）与 `last_run_outcome="lock_skipped"` 并存于同一 state 文件。
- N-16 9.4 尺寸差未被任何机制收敛：HEAD 已摘除 ch_vm_backup 的 /MIR 目标（9.1/9.3），故 F(600 GiB) 与 G(591.5 GiB) 的 7.4 GiB 差是**冻结后的常态读数**，两侧再无比对/校验通道；`G:\backup\ch_vm_backup` 内除 boot/data 外未见清单类文件（本次只 stat，未枚举该目录全部条目）。
- N-17 06:00 轮 `mode="versioned"` 且 `prev_snapshot == day_target`（同日 20260926）、`rotated: []`、`vanished: 3`；`force_mode=True` 而 `mode=all`。
- N-18 D 盘余量 40.8 GiB（731.2 总），而 config 的 `working_vault.free_floor_gb: 60` 作用对象是 vault 所在 G 盘（G 余 1454.4 GiB），D 侧本不受该地板约束——本条仅登记盘余读数。

## 三、无法判定 / 缺口

- G-1 ~~1.6 P-19~~ 已闭合于 1.6b：实体在 HEAD，唯码内无「P-19」字样（grep 0），符号面声称与文本面不符。
- G-2 ~~1.9 heartbeat 流容错~~ 已闭合于 1.9b：是「None 标准流兜底」，非字节/解码容错；交接书用词过宽。
- G-3 1.14 的 141 件 staged 删除未逐件核，是否另含灾备线其他件未判定。
- G-4 ~~2/3/6 项~~ 已展开为 2.x/3.x/6.x 读数。
- G-5 ~~生效 exclude_dirs~~ 已闭合于 3.4b（config L34，无 .worktrees）。
- G-6 ~~93.8% 未复算~~ 已闭合于 3.6：实测 92.42%（全树轻 IO，3.2s，未落入禁区）。
- G-7 2.4 的 11 条「killed=True 且活体名非 python」不能仅凭日志区分「真杀中系统进程」与「目标已自行退出→`NoSuchProcess` 返 True」两种路径（`_kill_pid_tree` 两条皆返 True），需 psutil 侧证据，日志面无。**另**：孵化腿活体 cmdline 从未入日志（只记台账 cmd），故 PID 复用后「实际被打断的是什么进程」在现日志设计下不可事后判定。
- G-8 ~~4—10 项~~ 已展开为 4.x/5.x/7.x/8.x/9.x/10.x 读数。
- G-9 CH 破损件只做了系统表面（8.2 读 0），**未做** CH 数据目录文件级 0 字节 part 扫描（未取 `system.disks` 路径、且属重 IO）；8.1/8.2 的「不符」仅覆盖 system.* 探针口径，不覆盖磁盘文件口径。
- G-10 交接书 1 项「六件」实列 7 件（含 services_registry 探针）；本卷按 7 件逐一读，未判定其计数口径。
- G-11 `restore_drill` 只读码面（HEAD 文本），**未执行**演练（会建/删演练库＝写库动作，超本卷授权）。
- G-12 未跑任何测试（含 tests/dr、tests/backup 三本件内 5/23/22 例仅计数，未执行）；未做任何删除、未清只读位、未 DETACH/RELOAD、未重启任务或服务。
