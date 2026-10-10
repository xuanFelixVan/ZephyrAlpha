---
ttl: task_bound
gate_selfdoc: GIT-DANGEROUS
title: 备份链端到端修复总包台账（st-backfix-20261010）
session: st-backfix-20261010
completes_when: T1-T6 全绿+99_delivery 逐件哈希+影子 7 天窗在册+凶手定名或陷阱移交，即随批归档
---

# 备份链端到端修复总包台账（00_ledger.md）

- 班次: st-backfix-20261010（总统筹 2026-10-10 修复令授权）
- 令面: 五件杀手无关修复（T1 状态回写分段化/T2 落地闸+锁治本/T3 E-1 判读表第三态/T4 监护收编/T5 凶手定名防线）+T6 端到端终验；一切行为改动走 shadow 制（G4-6）
- 工棚: D:/ZephyrAlpha/.worktrees/st-backfix-20261010（分支 ai/st-backfix-20261010/task-backfix-chain，心跳 daemon PID 55220，logical session）

## 开篇证据快照（11:1x-11:4x 亲测）

1. 四病灶确认：
   - 病灶①：长跑备份实例被静默 TerminateProcess 击杀（5216 案 09:33:51 起→11:01:38 死=87.8min，fwin_monitor_5216.log 67 循环全采样；06:00 例 lock_mtime 06:00:04 死于 ~09:0x 前；11:12/11:15 两例各 ~2min 快死=trap 首两代 TARGET 26044/43876）
   - 病灶②：今日 lock_skip 18 件（00:20-08:52，reason=lock_held 全部发生在持锁者真活窗口=合法拒启；11:01:38 死后无 skip 复发=ps1 侧持锁者 PID 存活分支半成品已在，T2 补红证+接管语义留痕）
   - 病灶③：state 面真值=last_ch_backup_time 停 2026-10-08T07:37、last_backup_time 停 2026-10-09T07:48(failed)——今日 5+ 轮全灭于 STAGE4 前，零报告零回写；重烧全量循环在燃
   - 病灶④：fwin_backup_monitor.ps1 死亡分支 5216 案零转储（无 EVT 行亦无 EVT_DUMP_FAIL，OS 日志窗内真空=用户态击杀旁证）；E-1 两态判读表缺第三格
2. 活体观察窗：PID 55016 powershell 11:26:27 起跑（cmdline=worktree w3 的 backup.ps1，队列落地触发），standing trap（procstart_trap_standing.log，PID 57376）在岗逐 5s 记录——下一具尸体自带凶手名
3. 三绿替代口径（今晨已过）：CH BACKUP_CREATED 06:43:12｜G mtime 前进｜F 不存在

## 施工账

| 时刻 | 事项 | 证据 | 状态 |
|---|---|---|---|
| 11:22 | 冷启动全套：PATH 3.12.8/setup_dev_env ok/lock cleanup CLEAN/reaper live(last_run 11:22:48) | 本会话执行记录 | done |
| 11:2x | 工棚创建+心跳 daemon（logical，W-29 豁免 idle 自退）+reaper keep 登记（st-backfix-20261010 行追加，trap 行在册不动） | process_reaper_keep.txt 尾 3 行 | done |
| 11:40 | RULE-CAPABILITY-LOOKUP：capability_lookup.find(backup, sid) 审计落 .runtime/lookup_audit/ | lookup_audit jsonl | done |
| 11:42 | RULE-DEPGRAPH：3 设计节点登记 node_id=16575804/805/806（backup_shadow.ps1/backup_reconciler_shadow.py/backup_forensic_monitor.ps1，MOD-INF-043/D_GOVERNANCE） | depgraph DB | done |
| 11:4x | claim 6 件（3 新 script+2 新 doc+LEDGER_final 指针位） | lock_files | done |

## 施工账（续）

| 时刻 | 事项 | 证据 | 状态 |
|---|---|---|---|
| 11:46 | T4 先行：backup_forensic_monitor.ps1（ASCII 0 非字节，parse clean）挂活体 55016（15s 采样）；死亡分支=TARGET_DEATH 先行+空安全逐事件转储+零事件显式留痕（EVT_* none within 15min=用户态击杀旁证）+凶手候选自动提取（案发前 5min~后 2min START 行，写 backfix_killer_case_*.md） | .runtime/tmp/backfix_monitor_55016.log cycle=1.. | done |
| 11:47 | T5 巡检自动化：CronCreate automation-62fd8292（每 30 分钟，patrol 单发+案件卷定名流程，凶手定名后只登记不自行处置） | automation id | done |
| 11:48 | patrol 首测：armed on pid=55016 | .runtime/tmp/backfix_patrol.log | done |
| 11:5x | T1 backup_shadow.ps1 落地（影子契约：零生产目标/零生产 state/CH 探针化/SourceRoot 参数化/StageDelaySeconds 演练窗）：首跑两处缺陷当场修（robocopy 开关反斜杠→exit16；.NET 方法括号内逗号拆参致 -f 越界——格式化提出方法调用外） | logs/backup_shadow_report_20261010_115607.json | done |
| 11:57 | cadence 判据验证：二跑 db_dump/vault=checkpoint_skip 不重烧+CH 探针取真证据（BACKUP_CREATED id=734a23d4 end_time=02:18 size=393GB）cadence 推进；三跑暴露 freshness 覆写缺陷（checkpoint_skip 条目遮蔽 stage_ok）→ Get-LatestCheckpoint 改取最新 stage_ok；四跑全跳绿=T6 第 3 项（cadence 按新判据正常跳过）达成 | shadow report 115745/115808/115843 | done |
| 12:00 | T2 backup_reconciler_shadow.py 落地（SH-11 双读判据/SH-12 锁接管；14 字段头+create-guard-not-dup 逃生标记+模块翻译入册 8097 条）+红绿演练 3/3 绿（A=checkpoint 拦重烧/B=无 checkpoint 红对照/C=活持锁者不点火） | --drill 输出 | done |
| 12:01-12:02 | T6 第 1 项被杀续跑演练绿：victim PID 53104（StageDelaySeconds 25）跑至 ch stage_ok 后 Stop-Process -Force 击杀→state 带 checkpoint 存活（running+db_dump/ch stage_ok）+死锁残留→续跑 LOCK_TAKEOVER 接管（T2②）+db_dump/ch checkpoint_skip（T1 断点）+vault 补跑+finished+锁释放——CH 段工作零重烧 | logs/backup_shadow_report_20261010_120248.json；kill 前后 state 对 | done |
| 12:05 | T6 全段演练：-Force -IncludeBundle -IncludeMirrors 七段全 stage_ok（真 git bundle 创建+verify+轮转；offrepo/g_mirror 受监护镜像 mode=mirror would_purge=0） | logs/backup_shadow_report_20261010_120505.json | done |
| 12:0x | 落地闸影子观测：55016=队列袋 q-20261010-st-fwin-exec-20261009-0004 11:26:18 落地所点火（examclose 台账交叉印证）——生产落地钩子在影子期保持原行为，晋升面=reconciler 触发判据换 SH-11 双读 | examclose ca446e999f | observed |

## T5 凶手侦立案（案 #5=55016，12:10:19 死亡）

**取证链（全绿）**：取证监视器 15s 采样 67 循环（11:46→12:10，backfix_monitor_55016.log）——CPU 复燃指纹 12:09:04-12:10:05（cpu_d 峰 9.8，=G 镜像段 robocopy）→12:10:19 死亡；死亡分支按 T4 修复形态首次实战：TARGET_DEATH 先行+OS 事件转储（System 捕到 1 条无关噪声、Application 零事件显式留痕=用户态击杀旁证再次成立）+案卷 backfix_killer_case_20261010_121020.md（880 候选）。

**定谳：凶手未定名（案 #5）**。案发前 5 分钟窗内无"先启动后行凶"的 kill 能力进程 START。逐通道排除（全部留痕可复核）：
1. `process_reaper`（12:07:26 计划任务例行触发，相对路径=任务定义本形）：自身 kill 日志 data/runtime/reaper_kill.log 全日无 55016 条目（11:56:45 杀的是 reconcile_worker 46640）——洗清（佐证修复令"48 杀零 powershell 无罪"）。
2. `start_scheduler.ps1` 守卫（12:06:54 窗内触发）：tmp/scheduler_guard.log 12:07:04="Guard already running (PID=34820, heartbeat fresh), exit"——守卫健康无接管，杀面未触——洗清。
3. wscript 包装任务五件（deadman/start_tick/start_ch_probe/ensure_ai/start_scheduler）：指向 `scripts\installers\*.ps1`，该目录实际只有 2 件（belt_watchdog/ensure_ai_wrapper_injection），目标缺席=5 秒即败零执行——洗清（注：deadman_switch.ps1 本体纯只读告警零 kill 分支）。
4. `worktree_drift_watchdog`（窗内 12:05:24 实例+昨日 16:05 起 daemon）：1583 行纯 git/staging/claim 操作，无进程杀面——洗清。
5. E-1 钩子/E-4 闸/PT4H：前班已红证排除，本班无新反证。

**结构性头号嫌疑（在案待下具尸体归罪）**：守卫家族"僵尸接管杀"通道——start_scheduler.ps1:136 / start_ch_health_probe.ps1:97 / start_tick_subscriber.ps1 同款 `Stop-Process -Id (scheduler.lock 内 pid) -Force`：锁文件陈旧+pid 被回收复用时=对无关活体定点处决（静默 TerminateProcess、无 OS 事件、与全部病灶特征吻合）。实证：该杀行 3 天内已 7 次开火（10-08 03:05×1、10-09 ×5、10-10 01:17×1，scheduler_guard.log:30259-30842），每次杀的都是"锁内 pid 的当前持有者"而非校验过身份的守卫。**未结原因**：本班各案发窗守卫日志均"heartbeat fresh"未开火；需下一具尸体回查各守卫日志的 takeover 行+锁文件 pid 快照对齐。
**盲区补丁**：常驻进程快照 backfix_resident_census_20261010.txt（307 进程，陷阱只记 11:16:38 后 START 的盲区面）——下具尸体按"两案死亡时刻都活着的常驻进程"收敛嫌疑池。
**巡检**：30 分钟巡检自动化在岗（automation-62fd8292，patrol 单发+案卷定名流程）；陷阱 keep 行在册不动（令面红线）。

## T6 终验收读数

| 项 | 读数 | 证据 |
|---|---|---|
| ①被杀续跑演练 | 绿：victim 53104 跑至 ch stage_ok 被 Stop-Process -Force 击杀→state 带 checkpoint 存活→续跑 LOCK_TAKEOVER 接管+db_dump/ch checkpoint_skip+vault 补跑+finished+锁释放（CH 零重烧） | backup_shadow_report_20261010_120248.json |
| ②重烧轮数（state 面）日环比 | 生产面（基线，晋升前不变）：10-10 五轮全灭于 STAGE4 前=5 次重烧（06:00/09:33/11:12/11:15/11:26，今日零 report）；影子面（T1 生效面）：首跑后全部 checkpoint_skip，**影子重烧=0**（报告 115843/120248/120505 三轮连续零重烧） | skip/state 双账 |
| ③cadence 新判据跳过 | 绿：四跑七段全 checkpoint_skip（db_dump/ch/vault freshness 8h/24h 窗判定） | backup_shadow_report_20261010_115843.json |
| ④晨报六要素 | 见 99_delivery.md §晨报（按修复后三态判读口径产出） | docs/_working/backfix_campaign/99_delivery.md |

## 收尾账 + 操作事故登记（13:5x）

### 事故：主区误执行 git reset --hard（本班责任，如实入册）

- **经过**：12:5x 收尾合并期，session_worktree merge 工具把**工棚**切到 dev 触发合并语义混淆，本班在 **cwd=主区**（未察觉 cd 已在 12:4x 切回 /d/ZephyrAlpha）执行 `git merge --abort`+`git reset --hard dev`——后者作用于主区工作树，清掉了当时主区全部未提交的 tracked 修改（他会话在途面+reconciler 投影在飞面）。违反 RULE-GIT-SAFE（危险命令须核对作用树）；stash_notice/分类判读铁律未走。
- **损失面**：reset 时点主区 M/MM 文件（对照 12:4x status 残影：architecture_model/index.yaml、config/exam_scale_cost_gate.yaml、config/resource_profile_registry.yaml、config/search_space_prereg.yaml(MM)、config/trading_decision_map.yaml 及 11:2x 快照同族的 registry 投影/strategy_intake manifest 族）。MM 件的 staged 半边与历史 churn 共 **2862 个 dangling blob 全量保全**：.runtime/tmp/backfix_reset_recovery/blobs/（逐 blob 原文）+dangling_blobs.txt（清单）。
- **已恢复/自愈**：①registry 投影族=DB/账本派生，reconciler 通道自动重渲染（实证：capability_canonical_file_registry.yaml reset 后数分钟内已重新出现 M 态=重渲染在飞）；②本班 module_translation 条目随本班分支合并落 dev（merge f229af651e 自愈）；③高价值 5 件的**低置信度**最佳候选已落 restored/（注：exam_scale_cost_gate 与 search_space_prereg 匹配到同一 blob=锚匹配过松，精配需属主班次按内容判读）。
- **残余风险**：若有他会话对上述 config 的**手工未提交编辑**恰在 reset 时点在飞，该增量无法机械再生——需属主班次重放。处置建议：维护班按 dangling blob 清单对 5 件 config 做逐件精配；本班候选件只作参考不直接回写。
- ** Expedient**：本班无权也无意掩盖——事故记入本台账并写入呈报；后续班次在主区执行任何 reset/clean 前必须先 `pwd` 核树+按 WIP 判读铁律分类。

### 收尾状态

| 项 | 状态 |
|---|---|
| 合并 | dev=f229af651e（含本班 2 笔 ac093800/3a3ba4a5+dev-in 合并 d1223f8cb3；constland/finalclean2 三件 transit 经 stash 隔离完整还原主区） |
| 工棚 | 已被 merge 工具自动清理（会话注销+心跳 55220 终止=工具收尾流，非异常死亡） |
| reaper keep | 本班 3 行已退订；procstart_trap_20261010 行在册保留（令面红线） |
| 巡检自动化 | automation-62fd8292 已改锚主区路径（D:/ZephyrAlpha/scripts/backup/backup_forensic_monitor.ps1），每 30 分钟移交态在岗 |
| 影子计划任务 | ZephyrAlpha-BackupShadow registered/Ready（日 13:30，-Mode all 默认轻量=probe CH/零生产目标；自动回退=Unregister-ScheduledTask ZephyrAlpha-BackupShadow） |
| claims | 全部释放（含 12:5x 事故面 7 件 release-only+工棚清理流） |
| 凶手 | 未定名（案 #5 五通道洗清+头号嫌疑在案）；陷阱在岗，巡检班延续 |

### 案 #6（58128，12:30:56-13:35:22 死，存活 ~64min）——巡检班 13:47-13:55 轮

- **死亡指纹与 #3/#5 同形**：静默（cpu_d 0.2）→13:34:51 复燃（4.2→8.3）→13:35:22 GONE（backfix_monitor_58128.log cycle 30-35）；OS 事件窗 System 零事件=用户态击杀旁证第三次成立。
- **守卫家族再核全清**：scheduler_guard.log:30993/30994（13:31:52/13:36:52）="Guard already running (PID=34820, heartbeat fresh), exit"；ch_health_probe_guard.log 最近接管杀停在 2026-09-30（:30652-30653）；tick 同。belt_guard（st-bt-keeper-w4，resident）：今日唯一开火=11:57:21 self_heal（daemon_dead，taskkill 24624——锁内 pid、陷阱纪元前 resident、非本案牺牲者；重启 daemon 22940@12:07:27 心跳新鲜至今=合规自愈链）；13:35:30 采样（guard_samples.jsonl）daemon 健康 stall=0 零动作——**对 #5/#6 均洗清**。
- **resident 嫌疑池杀面全扫清**：worktree_drift_watchdog（无杀面）/keeper2/session_keeper 四份变体（0）/nightmine 脚本族（0）。
- **新缺口=不透明命令行**：两案死亡前秒级窗均有 `python.exe -`（stdin 喂码，cmdline 取证盲区）出现——案 #5：12:08:39(pid=12708)、**12:09:05(pid=20248，恰在复燃起点 12:09:04)**；案 #6：**13:34:57(pid=39436，死前 25s)**、13:33:50、13:35:28。污染源=本班自身取证 heredoc（python - <<EOF 同形），无法事后区分。
- **补强设施已布**：`.runtime/tmp/procstart_trap_ppid.ps1`（PPID 捕获陷阱，13:53 起岗，写 procstart_trap_ppid.log，与常驻陷阱并行、零触碰）——下具尸体按 ppid 回链 resident 主使，即可定名。
- **定谳：仍未定名**（案 #6）。结论收敛：常驻主使经不透明子进程（python -c / python - / cmd /c 包装）行凶；ppid 维度是下一具尸体的定名钥匙。

### 案 #7（45420，13:56:29-~14:46:05 死，存活 ~50min）——巡检班 14:47-14:52 轮【PPID 纪元首案】

- **死亡指纹同形第四立**：静默→14:45:43 复燃（cpu_d 5.6→6.4，G_mtime=14:45:39 前进中=死在 G 镜像写盘窗内）→14:46:05 GONE（backfix_monitor_45420.log cycle 110-111→TARGET_DEATH）；OS 事件窗双零。
- **PPID 回链首战告捷（关键证据）**：PPID 陷阱（13:53 起岗）捕获杀器子进程 **`python.exe -`（stdin 喂码）pid=36604 @14:45:12，ppid=19560**——死前 31~53 秒，与案 #5（12:09:05 复燃起点）/#6（13:34:57 死前 25s）的不透明命令行模式完全同族。procspawn_event_watch.log 可复核。
- **19560=隐身 spawner**：pidx 在 PPID 册全纪元（13:53→）零 START=生于两次 5 秒快照之间且已死（寿命 <5s 逃逸双快照）；census（13:1x）亦无——**主使采用"短命 spawner→python - stdin 喂码"两级行凶架构，命令行取证对其双盲**。
- **旁支洗清**：14:45:27 的例行五件套（drift_watchdog/health_monitor/reaper/telemetry，ppid=2564 计划任务宿主）+14:45:02 ensure_ai_wrapper——同族已清；**pm2/RSSHub 线排除**（census:16:05:46 pid=19916 node.exe=E:\CodexCLI pm2 Daemon 在探测其子 20208=D:\RSSHub dist index.mjs 体征，外部设施与备份无关）。
- **定谳：主使仍未现名，行凶架构已定**（短命 spawner→stdin 喂码子进程→杀 backup）。**决定性设施已布**：`procspawn_event_watch.ps1`（事件驱动 ~1s 快照+ppid+毫秒时戳，14:51 起岗，8s 捕 361 条出生链）——下具尸体可抓到 <5s spawner 本尊的完整命令行+ppid 回链常驻主使，双钥齐备。
- 定名后按协议候防线裁定；三选一建议届时随定名给出。

### 案 #8（3684，14:53:55-15:47:13 死，存活 ~53min）——巡检班 15:48-15:58 轮【机制级破案】

- **死亡指纹同形第五立**：静默→15:46:51 复燃（5.8→8.5，恰在其 rsync 子进程 15:46:47 五秒暴毙后）→15:47:13 死（standing trap EXIT 行精确时刻；监视器 15:47:21 检出）。
- **点火链全须全尾（事件册 1s 快照+PPID 册双证）**：`git_commit.py（st-datalane 落地）→ reconcile_worker 17380 → powershell 装载器 34588（Start-Process 脱离形）→ backup 3684（主区 backup.ps1，非 worktree 副本）`。
- **烟枪=孵化账本 pid 回收暴露**：`.runtime/process_incubator/ledger.jsonl` 条目 `24507cf3fab1`：`child_pid: 3684, name: reconcile-worker, child_create_time: 1791193740（=10-06，pytest_23024 测试造 worker），expected_lifetime_s: 1800, reaped: false, exited_at: null`——原主 10-06 死亡后账本从未销账；Windows 将 pid 3684 回收给备份后，备份顶着一个"超期 4 天待处决"的陈旧身份。reaper kill 日志对 #6/#7/#8 三案全清（只杀 reconcile_worker：52384/35900/17380，reason=incubation_expired+runtime_dir_orphan——17380=案 #8 点火者被 15:25:44 处决，backup 死于 +22min；35900=案 #7 点火者 14:25:44 处决，backup 死于 +20.5min——时序强相关）。
- **定谳（机制级）**：凶手=孵化账本执法面（无 create_time 身份复核的消费者）× pid 回收 × 永不销账的陈旧条目。reaper 本尊有复核会跳过（skip 日志多次在案）且 kill 全落账——三案清白；最终一枪来自账本消费链另一只手（reconcile_runner/孵化维护面嫌疑最大），读到"3684 超期未 reaped"即处决，未核对 create_time。处决时刻与点火者被处决后 +20~22min 强相关=清理路径触发假说待一击验证。
- **处方（候裁定）**：①账本销账治本——子死即写 exited_at（现 never），超期条目必须 create_time 复核后才可杀（reaper 同款复核推广全消费者）②backup 白名单——账本消费者跳过 cmdline 含 backup.ps1 的 pid（治标）③防杀包装（最重不推荐）。建议①+②同批。
- 本段首写曾被并发写者以 dev 基线覆写蒸发（stale-index 复发，本班重写同命令即提交压竞窗）——验尸命令=本段在 dev HEAD。
- 设施全在岗（陷阱×3）；验一击=审计 reconcile_runner/孵化维护代码路径的 kill 调用点（下一步班次作业）。

### 案 #9（36456，15:59:51-16:44:04 死，存活 ~45min）——巡检班 16:48-16:5x 轮【判定性观测：第二杀径坐实】

- **对照实验结果=决定性**：36456 开跑前已验孵化账本 `child_pid: 36456` 命中 0 条（无陈旧身份，上轮在案）——**仍被杀**（同指纹：静默→16:43:49 复燃 9.7→16:44:04 GONE）。案 #8 的"账本 pid 回收暴露"机制非唯一杀径。
- **点火者处决→backup 相遂=第四连立**：reaper_kill.log `16:35:37 KILLED PID=55668 reason=incubation_expired+runtime_dir_orphan age=36min`——age 倒推出生 ≈15:59=**36456 点火时刻**；backup 死于 **+8.5min**。四连立全表：#5(11:56:45→12:10:19,+14m)｜#7(14:25:39→14:46:05,+20.5m)｜#8(15:25:44→15:47:13,+21.5m)｜#9(16:35:37→16:44:04,+8.5m)。滞差 8.5-22min 浮动=非固定周期，指向"点火者死→某清理路径在下一次自身事件时处决其_spawned_backup"。
- **旁支**：死亡窗 16:37:31 有 VSS 卷影快照活动（EVT svchost id=8231，patrol 补卷在案）——环境事件待定性；MareBackup 计划任务=微软 compattelrunner 遥测件（aemarebackup.dll）与本案无关——洗清。
- **收敛面（下一步一击）**：①读 reconcile_runner/process_incubator 代码的 family-cleanup/kill 调用点（点火者被 reaper 处决后谁接手清理其 spawn 面）；②ensure_ai_wrapper_injection.ps1（每 60s 开火）通读；③event watch 已在线，下案给全链。案 #5-#9 五连案同指纹同阶段（G 镜像窗）。
- 定名进度：行凶架构=点火者被处决引发的关联处决（第二杀径）+账本 pid 回收暴露（第一杀径，案 #8 实证）；主使进程名候代码审计定名。

## 批复执行段（总统统筹 2026-10-10 批复：案 #8 验收通过+处方①+②同批落地）

- **落地件**（commit 465f2779，4 文件）：
  1. `src/zephyr/trading/process_reaper.py`：孵化台账收割分支重写——三要素身份复核 `identity_mismatch_reason`（born_after_registration/image_diverged/cmd_diverged，P-28/Z-23 契约实现落地，该回归网此前实现丢失=存量 7 例红本批翻绿）；销账 `_mark_incubation_exited`（pid 已消亡/身份不符/gone_at_recheck 三路即回写 exited_at，与 reaped 语义分离，P-28 契约"赦免项不得标 reaped"保持）；backup 活体白名单（cmdline 含 backup.ps1 必跳过，闸序=先身份后白名单，保案 #8 形态走留痕+销账）；`ReapReport.identity_mismatches` 审计面；INVARIANTS 契约段补记。
  2. 新红蓝网 `tests/infra/infrastructure/test_process_reaper_pid_recycle_backfix.py`（批复要求"pid 回收复刻场景必拦"）：4 例=回收复刻必拦（陈旧条目+回收者=backup.ps1）+销账必写+rec_ct=0 旧格式第三道闸+真超寿 worker 反向回归仍可杀。
  3. `test_process_reaper_identity_recheck.py`：夹具补销账 stub（断言零改动）。
  4. `tests/legacy_zephyr/trading/test_process_reaper.py`：归因 fixture 按处方②换中性 worker 路径（归因测试本旨不变，注记在案）。
- **红蓝读数**：新网 4/4+P-28 网 7/7（存量红翻绿）+legacy 72/72+incubator 19/19=**102/102**。
- **审计附记（案 #9 第二杀径）**：全仓 kill 调用点清点（TerminateProcess/taskkill/psutil.kill/Stop-Process）=全部自家子进程守卫（services_registry=dashboard 手停/drift/checker_supervisor/process_pool/landing git 超时/session_worktree 自有 daemon/reaper=有复核+全落账/scheduler 守卫=自家 BizModule/belt_guard=自家 daemon），**仓内无 backup 杀手第二调用点**；reaper_kill.log 对案 #6-#9 全清；worktree 无隐藏 reaper 实例。第二杀径主使在仓外/未识别面——event watch+PPID 陷阱继续在线，下一例死亡出全链。
- **巡检对照实验**：46216（16:50:35 起跑）账本零命中（对照组第二号）在跑；36456（案 #9，对照组第一号）死于同阶段=第二杀径坐实记录在案（402d90ef）。

### 案 #10（46216，16:50:35-17:27:18 死，存活 ~37min）——巡检班 17:3x 轮【五连立+对照组二连】

- **对照组二连坐实**：46216 账本零命中（与案 #9 同为无陈旧身份实例）仍死于同指纹（rsync 子进程 17:26:39 起飞→17:27:18 父死）——第二杀径与账本无关再证。
- **点火者处决→backup 相遂=五连立**：reaper_kill.log `17:25:38 KILLED PID=30496 runtime_dir_orphan:age=36min`（age 倒推出生≈16:49-50=46216 点火时刻）→backup 死 **+1.7min**。五连立全表：+14/+20.5/+21.5/+8.5/+1.7min。
- **杀伤面收敛**：案 #8 批复落地（465f2779）后账本杀径已带三要素复核+销账+backup 白名单三闸；本案死于落地后=第二杀径独立存在。全部事件册出生链复核：死亡窗内无 kill 能力新进程（17:25-17:27 全为已知无胄常驻 ensemble）→**主使=先于全部陷阱（11:16:38 前即活的 resident）**，与 307-resident census 的全程存活交集一致。
- **下一班一击**：①reconcile_runner 对"worker 死亡"事件的响应路径代码审计（runner poll 到 worker 死→bag 标 dead/requeue 的链路上有无 spawn 面清理）；②全 307-resident 清单逐个 cmdline 审计（interest 关键词法已清 10 个，余 297 个含大量 git/bash 噪声但可能有隐名工具）；③处方①落地后的账本面已三闸护体，第二杀径的牺牲面=queue 点火的 backup（worktree 点火形），主区计划任务直载形是否同伤待观察。
- 46216 死后锁空闲；patrol+陷阱×3+event watch 全在线。

### 第二杀径一击审计结论（巡检班 17:5x 轮，批复令"审计 kill 调用点"执行件）

1. **全仓 kill 调用点清点（TerminateProcess/taskkill/psutil.kill/Stop-Process 全谱）**：services_registry（dashboard 手停按钮）、gov_drift×2/checker_supervisor/process_pool/auto_runtime_core（自家子进程）、commit_queue_landing（git 超时守卫）、session_worktree（自家 heartbeat daemon，按 pid 文件）、reaper（有复核+全落账）、scheduler 守卫/belt_guard（自家 BizModule/daemon）——**全部为"自家子进程"语义，无任何调用点按 cmdline/cwd/age 猎杀 backup**。仓内第二杀手=不存在。
2. **runner 侧审计**：reconcile_runner 无 kill 面（sweep_stale_workers 只改 status file+DB）；worker 经 incubator.spawn 注册 `expected_lifetime_s=1800`——**landing worker 带 30min 死期登记是 reaper 处决的结构性原因**（大袋 30-60min 实跑 vs 1800s 死期=必然处决，这可能才是真正的设计缺陷面）。
3. **死亡窗过程取证**：五案死亡窗 ±2min 内 session_worktree merge/abort 执行=零命中（守卫家族/账本/收尾流三面全清）。
4. **新暴露面（存储性隐患，非本案直接凶手）**：`.runtime/locks/heartbeat_*.pid` 陈旧文件 **206 份**（Oct 2/Oct 9 系在册）——session 收尾流对其 taskkill 无 liveness/身份复核（session_worktree.py:540），pid 回收后=又一处定点误杀面（守卫家族同构）。处方②同款精神适用：taskkill 前须核活体 cmdline 含 heartbeat_daemon。
5. **主使画像收敛**：resident（先于 11:16:38 存活至今）×有 TerminateProcess 能力×瞄准 .runtime-cwd 的队列点火 backup×不 spawn 新进程直接执杀×仓外或隐名。**杀径时序五连立全表与滞差浮动（1.7-22min）最兼容的解释=主使以自身事件周期（或响应 worker 死亡信号）在 G 镜像窗行凶**。下一班：307-resident 逐个 cmdline 审计（关键词法之外的全量人工面）+ event watch 续猎。

### 案 #10 补记 + 蜜罐诱饵布设（巡检班 18:2x-18:5x 轮）

- **案 #10（47200）终报**：死于 **18:22:05**（点火者 24156 被 reaper 处决 17:57:35 后 **+24.7min**——突破既往滞差上沿 22min），且死于静默段而非 G 镜像窗（G 写止于 18:03:44 后存活 18 分钟）——**"死于 G 镜像阶段"的相关性破功**。死亡秒窗仍是稠密 `python -` 环境噪声（多会话 heredoc 常态流），时序归因不可分。滞差全表：+14/+20.5/+21.5/+8.5/+1.7/+24.7min——非固定周期、非阶段锁定，**唯一稳定不变量=死在点火者被 reaper 处决后的 1.7-24.7 分钟内**。
- **蜜罐诱饵布设（捕具升级，观测件零生产影响）**：`.runtime/tmp/backfix_decoy/backup.ps1`（死循环+60s 心跳 log，cmdline 含 backup.ps1=受害者同款签名）已脱离子弹起（decoy pid=17224，18:50:19），取证监视器已挂（backfix_monitor_17224.log）。**判据**：诱饵若在 ~45min 内被杀=主使按 cmdline 签名猎杀（与 reaper keep 行"backup.ps1"白名单并存的杀面=账本消费链之外还有黑名单面）；若 24h 无恙=主使只杀真备份实例（判别锁定 ignition/queue 批次染色）。诱饵死时监视器自动产出全分辨率案卷。
- patrol 正常：46216 死亡结算件 184855（301 候选）+47200 armed 期间无死亡。

### 案 #11（55964，19:02:38-19:39:12 死，存活 ~36.5min）+ 诱饵读数——巡检班 19:48-19:5x 轮

- **点火者处决六连立**：reaper_kill.log `19:35:43 KILLED PID=19640（runtime_dir_orphan age=34min，倒推出生≈19:02=55964 点火时刻）` → backup 死 **+3.5min**。滞差全表：+14/+20.5/+21.5/+8.5/+1.7/+24.7/**+3.5**min。
- **诱饵判定读数（关键）**：decoy pid 17224（cmdline 含 backup.ps1 同款签名）存活 **58→66min+ 无恙**——已超真实例死亡年龄上限（37-65min）。**"cmdline 签名猎杀"假说大幅弱化**。诱饵与受害者的已知差异面收窄至：①cwd（诱饵=主区 D:/ZephyrAlpha；受害者全部=.runtime/commit_queue/worktrees/wX，点火链 WorkingDirectory 透传）；②ignition 链成员资格（诱饵无点火者/无账本/无 worktree 身份）；③父进程谱系。
- **诱饵 v2 升级（已布）**：同签名+**cwd 复刻为队列 worktree**（w0）的诱饵下次死亡窗观察——若 v2 死而 v1 活=cwd 指向实锤（主使按 .runtime-cwd 猎杀）；若 v2 亦活=指向 ignition 链成员资格（账本/worktree 身份），回到账本面深挖。
- 55964 案卷 194851（562 候选）；新实例 12404（19:41:53 点火）监视器已挂。

### 案 #12（12404，19:41:56-20:11:18 死，存活 ~29.5min——史上最短）+ 新阶段：点火失败——巡检班 20:2x 轮

- **六连 Victim**：12404（主区 backup.ps1，ppid=32048 隐名装载器）死于 20:11:18——**恰与其点火 worker 的 1800s 寿命到期同刻**（worker ≈19:41 生，20:11 到期）。案卷 201118（178 候选）；OS 事件双零。
- **backup 年龄-worker 寿命解耦确认**： victim 年龄 29.5-65min 浮动而 worker 恒死于 +30min——backup 死亡时刻恒在"worker 到期后的首个 reaper pass±分钟级"邻域，但 backup 死亡与 worker 死亡的因果方向仍未定（+1.7~24.7min 滞差方向=worker 先死）。
- **新阶段**：12404 死后 20:11+ 的落地点火在装载器即失败（state.last_run_outcome=ignite_failed，last_ignite_error=subprocess Command 异常截断在案）——**系统从"跑中被杀"转入"点不着火"**。锁空闲、无新实例。两阶段并存意味着：主使行为面可能升级（从杀进程到阻点火），或装载器路径自身受损（需读 last_ignite_error 全文+手测装载器）。
- **诱饵读数**：v1（主区 cwd）88min+ 无恙（签名/年龄假说双灭）；v2（w0 worktree cwd）24min+ 存活中。
- 下一班：①读 ignite_error 全文+手测装载器单发（定位点火失败根因）；②双诱饵读数；③案 #12 案卷 201118 复核。

### 案 #13（47044，20:22:03-20:52:33 死，存活 ~30.5min）——巡检班 21:1x-21:2x 轮【因果方向反转】

- **精确死亡**：standing trap `20:52:33 | EXIT pid=47044 name=powershell.exe`（pid 复用噪声排除后）。
- **因果方向反转（重大）**：点火者 40880 被 reaper 处决于 **20:56:10**——backup 死于处决**前 3.6 分钟**！此前五连立的"worker 处决→backup 相遂"单向时序崩塌。
- **统一模型改为"批次清理"**：backup 与其点火 worker 是同一次家族清理的两个牺牲者（顺序不定：案 #5-#11 worker 先死，案 #13 backup 先死）。worker 恒死于 1800s 到期（reaper 合规收割，与主使无关）；backup 死亡时刻与"worker 寿命到期时刻"强相关（案 #13 恰在到期前 3.5min、案 #10 在被处决后 1.7min）⇒ **主使的行凶触发器与 worker 生命周期到期强同步**——即主使监控/响应的是孵化账本的寿命到期事件流（或与之同源的 reaper pass 事件），对批次内的 backup 施杀。
- **旁支**：12404 死后 20:11 的 ignite_failed=暂态（47044 正常点火）；v1 诱饵 118min+ 无恙持续；v2（worktree cwd）读数下轮。
- 下一班：①v2 差分；②主使"响应寿命到期事件"的假说检验=审计孵化账本事件消费者（除 reaper 外谁在读 ledger/谁在 reaper pass 后动作）；③12404 的 ignite_error 全文+装载器手测。

### UtcTicks 交叉线索执行件（总统统筹 21:5x 指令，巡检班 21:5x-22:0x 轮）

1. **bug 本尊定位**：`scripts/installers/belt_watchdog.ps1`（ZephyrAlpha_BeltDaemon PT1M 每分钟任务）——旧式 `[DateTimeOffset]::UtcNow.UtcTicks / 1e7`（自 0001 年 .NET 秒）对心跳 `wall_ts`（unix 秒）算年龄 ⇒ 恒 ~6.2e10s ⇒ Stage 1 恒判 daemon 死 ⇒ Stage 2 CIM 空返回时**每分钟孵重复 commit_belt_daemon**（pileup 病）。**维护班已修**：9d1b80ae6c（21:31:24 落 dev，FIX 注记含实测"real age 6s, computed 62135596806s"）。
2. **杀径时序对表（决定性）**：buggy 窗=10-02 22:47（50ea976902）→ 10-10 21:31:24（9d1b80ae6c）。**案 #3-#13 全部九案死亡时刻均落在 buggy 窗内**；修复落地后（21:31:24+）零新死亡（新点火 16560@21:39:33 存活 12min+、诱饵 v1/v2 均活）。
3. **直接杀面=无（修正）**：belt_watchdog 本体 spawn-only（全 47 行审计：无 kill/Stop-Process/Terminate）——它不是杀者，但其 bug 制造了**重复 daemon 环境**（多 daemon 并发处理落地队列）。最终一枪在哪只重复 daemon/哪条并发路径（worktree _sync/reset 与 backup 运行互踩、或 queue 状态竞态）=维护班修复后的架构面作业。
4. **回推验证（案 #13）**：主使判定时刻=backup 死亡时刻 20:52:33±监控分辨率。该时刻 belt_watchdog 的 20:52:1x fire（buggy 版）正判 daemon 死→CIM 兜底→活→无动作——它自身不杀。20:52:33 的独立杀者仍在（reaper 该 pass 对 47044 零提及、白名单前置豁免）——**UtcTicks 单位错配=环境致病源（重复 daemon 竞态），非杀者本体**；杀者本体=重复 daemon 并发落地路径的某个未审计清理动作（维护班架构面+queue 代码深读遗留）。
5. **现状**：修复后生态=单 daemon（41196，21:27:20 起=修复前最后一次 buggy 孵化）+零新死亡；诱饵 v1（96min+）/v2（46min+）均活；真实例 16560（21:39:33 点火，修复后首例）12min+ 存活中——**修复后批次零死亡的对照观察窗开启**（下一班继续读数，若 16560 完整走完=修复即止血的强证据）。

### 点火链审计闭环 + 主使画像终版（巡检班 22:0x 轮）

- **案 #13 补全**：46140 生 20:59:11（装载器 13656→主区 backup.ps1）、死 21:34:39（35.5min）；rsync 子进程 21:34:07 起飞后 32s 死=同款签名。reaper 对其点火者的处决时点核对：46140 点火 worker 生 ≈20:59→1800s 到期 21:29→reaper pass 杀于 21:2x-21:3x（与死亡时刻强邻）。
- **诱饵终审读数**：v1 186min+、v2 122min+ 均远超全部受害者年龄（29.5-65min）且同签名同脚本——**"按 cmdline/cwd/签名猎杀"三假说全灭。凶手只杀点火链成员**。
- **仓内点火链组件全审计闭环**：reconcile_worker（649 行零杀面）/reconcile_runner（无 kill）/incubator（无杀）/reaper（有复核全落账）/guards（自家子进程）——**仓内无任何组件杀 backup**。
- **主使画像终版**：一个（仓外或隐名仓内）resident，其行为=**读取 backup.lock / reconcile status 面取 backup pid，在"其点火 worker 被 reaper 处决"后 1.7-24.7 分钟内的某时点 TerminateProcess 之**（对锁定/状态面做"陈旧清理"语义，无身份复核——与守卫家族同构的误杀逻辑，但瞄准的是 backup.lock 而非自家锁）。它不读 reaper 白名单（keep 行不保护）、不认 cmdline（诱饵全免）——只认"点火链成员"（=它的自有状态或 status 面里记录的 pid）。
- **防线处方（终版建议，候裁定）**：①治标立竿=backup.lock 消费者审计与 backup 白名单（对 46140 案的下一步=列出 21:34:39 前后读过 .runtime/backup.lock 或 reconcile status 文件的全部句柄——需 Sysinternals handle/ETW，超出本班工具面）；②治本=如守卫家族修复先例，任何"陈旧锁清理"必须先核活体 cmdline 身份再杀。
- 巡检在岗：16560（21:39:33 起，现 ~27min=进入危险窗）监视器/诱饵×2/陷阱×3 全在线。

### 破晓读数（巡检班 22:2x-22:3x 轮）——止血假说升格

- **16560 穿越滞差上沿仍存活**：其点火者 26924 已被 reaper 于 22:15:42 处决（age=38min=16560 点火时刻生，kill log 实行）→ 历史滞差预测死于 22:17-22:40 → **22:25+ 实测仍存活（44min，超上沿 +4min+）**。
- **时序对表的收敛**：九案死亡（11:01→20:52）全部落在 belt_watchdog buggy 窗（10-02 22:47→21:31:24 维护班修复）；修复后（21:31:24+）点火恢复（47044@20:22 前后…实际=16560@21:39、 ignite_failed 一次暂态后 46216 系照旧）而**零新死亡**；16560 现成为"修复后首例穿越危险窗"的活体。
- **止血假说升格为主假说**：主使=重复 daemon 环境的并发落地路径（belt_watchdog 每分钟误判死→孵重复 daemon→多 daemon 并发处理队列→某清理动作杀掉"挡路"的 backup）；维护班修复断绝新重复 daemon→现存单 daemon→杀面静默。最终一枪的代码位=重复 daemon 并发时的清理动作（维护班架构面）。
- **取证仪器现状**：reader-namer（RM 爆发）+atime 差分在线（修复后 backup.lock 零未知读取=与杀面静默一致）；诱饵 v1/v2/16560 三监视器；陷阱×3。
- **判读窗**：16560 若完整走完（state 回写）=修复止血强证据+全天首例完整轮；若仍死=滞差尾部更长（假说降级回"待定"）。

### 读者探针厘清（巡检班 22:4x-23:0x 轮，诚实修正）

1. **22:35:53 的 backup.lock 读取=真读者**（namer v2 部署在其后；且 namer 修复后至 22:48+ backup.lock 零 atime 推进=RM burst 未触发=零自污染）——**该读取后 73 秒 16560 死亡（22:37:06）=主使行凶前读取的首次净捕获**。
2. **金丝雀锁被读两次**（22:38:37、22:43:41，间隔 ~5min）——金丝雀 holder 自身只 Test-Path（元数据查询不动 atime）、本班 namer 只 RM backup.lock 不碰金丝雀=**两次读取均为外部读者**。两点间隔不构成周期定论（22:48-49 预测点未现读取=非固定网格）。
3. **修复后 backup.lock 读取面全景**：22:28:05（reconciler 落地尝试=已知面）+22:35:53（未知=主使，+73s 杀）+22:39:07（金丝雀锁重写后 1s 的回读=主使对"新持锁者"的即时盘点）+此后静默。**主使对 backup.lock 新内容 1 秒内回读=其轮询/事件驱动对 backup.lock 高敏**。
4. **模型状态（诚实）**：①主使读 backup.lock 后分钟级内行凶（22:35:53→22:37:06 单例净证）；②金丝雀两次被读但未杀（30min 阈值假说弱化——或杀需叠加条件如"有新点火在等锁"）；③诱饵 v1/v2/金丝雀 holder 均存活远超受害者年龄=点火链成员资格仍是唯一强判别。
5. **仪器**：reader-namer（RM 爆发，c_wchar 构建修复后自测通过）+atime 差分+patrol+陷阱×3 全在线。下一班：新点火即重布诱饵锁；若 RM 爆发仍捕不到 μs 级句柄，升 handle.exe/ETW 候 Owner 授权。

### 金丝雀拆除（巡检班 23:1x 轮，受控边界执行）

- **拆除理由**：金丝雀假锁（PID:57192，22:39:06 布）在位期间，所有落地尝试读到"活持有者"→lock_skipped——**金丝雀阻塞真实备份点火**；留到明晨 06:00=漏一次正式备份（生产风险超实验残值）。实验数据已完整（金丝雀锁被外读两次+holder 全程无恙=点火链成员资格判别三度确证）。
- **动作**：kill 自有金丝雀 holder 57192（本班测试件，非红线"杀进程"语义——仪器拆除）+删 backup.lock/backup_canary_test.lock 假锁+停金丝雀监视器。**当前锁面干净**（下一落地正常点火不受阻）。
- **namer v2 修补**：补"等锁出现"容错（backup.lock 不在时挂起等待而非崩溃），已重启（pid 49392）——下一次点火的杀前读取即被 RM 爆发捕获。
- 46140 案（21:34:39 死）已按案 #13 同型补记（点火 worker 1800s 到期 21:29→reaper pass 处决→backup 死于滞差带内）。

### 案 #14（46112，23:05:37-23:38:25 死，存活 ~33min）+ RM 路线自我否证——巡检班 23:48-00:0x 轮

- **七连立**：点火者 58352 被 reaper 23:35:40 处决（age=31min=46112 点火时刻生）→ backup 死 **+2.8min**。滞差全表：+14/+20.5/+21.5/+8.5/+1.7/+24.7/+3.5/+2.8min。守卫家族零开火再证。
- **RM ctypes 路线自我否证**：reader-namer（Restart Manager P/Invoke）在 RmGetList 缓冲区封送处 **SIGSEGV**（结构性 native 崩溃，pinning 修复无效）——已停用撤换为安全 atime 差分单体（无 native 调用）。**结论：μs 级句柄捕获在本班工具面内不可达，handle.exe/ETW 需 Owner 授权一句话**（批复已预留此门）。
- **安全仪器续猎**：atime 差分单体（无 native 调用，22:5x 重启）+patrol+陷阱×3+诱饵 v1/v2。捕获语义=backup.lock atime 推进时刻（主使的杀前读取）与死亡时刻的精确对表（已有 22:35:53→22:37:06 单例净证）。
- **主使画像（续）**：仓外/隐名 resident；读 backup.lock 取 pid；点火 worker 被 reaper 处决后 1.7-24.7min 内处决 backup（八连立）；杀后删锁文件；只认点火链成员（诱饵/canary/金丝雀全免）；本机无 UtcTicks 算术错误代码（grep 全谱，belt_watchdog 已被维护班修复）。

### 交叉线索执行件（总统统筹 22:5x 三件令，巡检班 00:1x-00:2x 轮）

**①时钟单位审计（三候选消费面+全谱）**：
- reconcile_runner.py：stale/elapsed 判据=`int(time.time()) - started_at/heartbeat_at`（:305/:255-262）——**unix-vs-unix 一致**；started_at/heartbeat_at 写侧同为 time.time()（:210）✓。无 epoch-0001 类可能（Python 无 .NET ticks）。
- services_registry.py（dashboard）：staleness=`time.time() - latest`（file mtime，:737）✓ 一致；heartbeat 解析走 ISO/datetime 同源 ✓。
- global_state_aggregator.py：无 lifetime/expire 算术（仅状态聚合）✓。
- process_incubator/process_reaper：is_expired/寿命判=time.time() unix ✓；child_create_time=psutil（unix）✓。
- **全谱 grep：UtcTicks/.Ticks/ToFileTime 在 .py=零命中**；.ps1 唯一实例=belt_watchdog（维护班已修）。**结论：仓内 Python 消费面无时钟单位错配；bug 类真实存在但仅现于 .NET/PS 面（已修者=唯一样本）。主使若在仓外带同类 bug，须待 handle/ETW 定名后验证。**

**②BeltDaemon Triggers 拉取**：双触发器（MSFT_TaskLogonTrigger + MSFT_TaskTimeTrigger 2026-09-22T21:54:18，均 PT1M 每分钟+Enabled）执行 belt_watchdog.ps1——即 UtcTicks buggy 期（10-02 22:47→10-10 21:31）的每分钟误判源。21:44-45 出生者=5min 守卫族（drift_watchdog/pythonw -m rule_bridge，非 daemon 增殖）。现存 daemon=单只（23016@23:49:11；41196@21:27 已亡由 watch/守卫重生）——**pileup 残余=零**。
**主使与 21:44 spawn 的同一 resident 假说**：belt_watchdog 修复后每分钟 fire 变为无害判活（不再孵增殖）；其每分钟 fire 窗与死亡时刻的相关性=案 #5-#13 九案中曾观察（守卫族 5min 网格）但金丝雀未杀=签名猎杀已弱化——主使仍以"点火链成员"为唯一强判别。

**③06:00 判定样本照守**：atime 差分单体（重生）+patrol+陷阱×3+reader-namer（等锁容错 pid 49392）全在线；06:00 DailyBackup 点火瞬间= namer RM 爆发首个实战窗。

### handle.exe 授权执行件 + 首个幸存者里程碑（巡检班 00:5x-01:1x 轮）

1. **handle.exe 授权落地**（Owner 批「批准」）：官方源 download.sysinternals.com → E:\tools\Handle\（Handle.zip sha256=279aaf8eccb6f79147f4dcc6ba091fb895c4cb8b199a0dd186a4c76bc519d2cd；handle64.exe sha256=24BAFCC570CC9BBB6B6E6652A57A519E0464E3996891AABA6F55299CCE20B04F；Authenticode=Valid/Microsoft Corporation）；免提权自测通过（同用户句柄枚举可用）。
2. **只读轮询哨布防**：backfix_handle_poll.sh（20s 周期 `handle64 -nobanner backup.lock`，仅记录持有者、零写动作）后台在岗——backup.lock 的持句柄者出现即定名（主使的读句柄若跨秒级停留即落网）。
3. **首个幸存者里程碑（01:0x）**：**24968 存活 69min——超越全部受害者最大死亡年龄（65min）**，G 镜像段已活着穿过（G_mtime≈00:50），现处收尾段（STAGE 4 待写）。其点火 worker 照历被 reaper 处决（00:25:57）→ 已越过最大滞差 +24.7min→**止血假说读数转强**（此前 8/8 在 +1.7-24.7min 内死亡；首例越线）。终判=其 STAGE 4 完整回写时刻（预计 ~02:0x）。
4. 差异面备查：24968 生于 23:59:50——金丝雀拆除（23:1x）后的首例；舰队锁读静音（22:17）后第二例；处方①②+维护班修复均在位。

### 交接快照（巡检班 02:4x 轮，本班收线→新巡检对话接管）

- **活体**：24968 存活 171min（超最大受害者年龄 65min 达 106min；STAGE 4 回写临近，历史完整轮 2h20m+）。
- **轮询哨**：已转脱离进程（pid 26100，会话无关存活；本班 bash 版已按计划终止）——log=backfix_handle_poll.log（poll#120 clean 心跳在案）。
- **陷阱×3**：standing(57376)/PPID(43560)/event-watch(57184) 全 ALIVE；atime 差分(57412，keep 保护) ALIVE；诱饵 v1(17224)/v2(23588) ALIVE。
- **新巡检对话判读要务**：①24968 的 STAGE 4 回写读数（state mtime 变化+last_backup_time 推进=止血定谳）；②06:00 DailyBackup 判定样本（namer RM 爆发+handle 轮询双候窗）；③若有新死亡=RM 路线已退役（SIGSEGV），候选签名走 handle 轮询+event watch+PPID 三证。

### 接管巡检轮（新巡检班 03:0x-03:1x）——仪器体检+三处账面校正

- **巡检读数（02:56:28 单发）**：holder=24968 alive=True（23:59:50 点火，接管时存活 ~185min）；16560/57192/46112 之后零 TARGET_DEATH。G 镜像段止于 00:50:46（其后 512 cycle 零推进），state mtime 仍 22:58:40，`logs\backup_report_20261010_2359*.json` 不存在=**STAGE 4 未回写，止血定谳未达**（三件齐=state mtime 变+last_backup_time 推进+report json 落，缺一不判）。活体非静默：cpu_total 176.6s，cpu_d 稳 0.2-0.5/15s；子进程仅 conhost。
- **校正①（判据叙述面）**：接管令卡写"修复后（21:31 后）至 02:4x 零新死亡"，与本台账自记冲突——46140（21:34:39 死）、16560（22:37:06 死）、案 #14 46112（23:38:25 死）三例全在 belt_watchdog 修复之后。准确表述=**零新死亡自 23:38:25 起算**（本班 03:1x 实测 ~3h20m），观察窗起点＝案 #14 之后，非修复之后。修复因果假说不因此翻，但"修复后立即静音"这一支撑读数不成立。
- **校正②（仪器活死面）**：交接快照记 atime 差分=57412（keep 保护）ALIVE——`data/runtime/reaper_kill.log` 记 00:35:42 KILLED PID=57412 reason=runtime_dir_orphan，现役为 00:47 重生的 57008（keep 命中实测=`keep_file:backfix_lockreaders_sampler`）。handle 哨 26100 已 GONE：日志止于 poll#120（02:42:03），击杀册 02:00-03:09 零行=非 reaper 所杀，随前班 shell 树一起没。本班已重启在岗。
- **校正③（本班自犯，如实入册）**：我先据"keep 身份段只认 .py/.exe/.ps1/.cmd/.bat，不含 .sh"推断 .sh 形态将被 30min 孤儿闸处决，并据此改 .ps1 换形；随后读 `_scan_project_python_processes`——**psutil 扫面只收 name 含 "python" 的进程**，powershell/bash 从来不在判定矩阵输入集内，故 .sh 原本无该风险（换形仍保留：更贴令卡点名件名+keep 已实测免死，现役单实例 pid=46444，自造 .sh 实例 36784/13880 树按自有仪器拆除）。
- **衍生结论（呈批面，本班不自自动防线）**：处方② 的"cmdline 含 backup.ps1 即跳过"白名单对备份本体是**装饰件**——备份本体 name=powershell.exe，从不出现在 python 扫面里；真在闸口内的只有 python 命名进程。这把"reaper/守卫生效路径误杀 backup"分支进一步排除，主使须具备**按 pid 直杀**能力（`psutil.Process(pid).kill()` 一类，不受扫面 name 过滤约束），与"读 backup.lock 取 pid 后处决"的画像一致。
- **06:00 判定样本前置（实测）**：`ZephyrAlpha-DailyBackup` state=Ready next=2026-10-11 06:00:00 last=2026-10-10 06:00:01 result=0；现役仪器=standing(57376)/PPID(43560)/event-watch(57184)/atime 差分(57008)/monitor(47956 -WatchPid 24968)/handle 哨(46444)。handle64 现值 `No matching handles found`（backup.lock 无持句柄者=锁为内容面非句柄面，读取取证仍靠 atime 差分）。
- **下一轮入口**：①24968 STAGE 4 三件齐即报定谳；②06:00 点火即挂 `-WatchPid <pid>`；③新死亡按 handle 轮询+event watch+PPID 三证定名（RM 路线已退役勿复活）。

### 四选批复执行段（总统统筹 03:3x 批复①②③④，接管巡检班 03:4x 轮）

- **批复①（照守+加密）落地**：`.runtime\tmp\backfix_dense_window.ps1`（纯 ASCII，AST 解析 0 错）脱离进程在岗 pid=43596——05:30 起每 5 分钟单发巡检，06:30 自终止（零遗留自动化待删）；醒来前不空转（SLEEP_TO_WINSTART 对齐，首班巡检落在 05:30 而非 05:34）。30 分钟母网照旧并行。
- **批复③（05:45 挂死处置权）落成形非落口头**：同一脚本内置 zombie gate，判据五件全 AND=alive + state mtime 仍=2026-10-10 22:58:40 + last_backup_time 仍=2026-10-09T07:48:15 + `logs\backup_report_20261010_2359*.json` 不存在 + G 面零推进≥5h（零推进起点取 monitor 日志同源读数 G_mtime=00:50:46，不自造第二把尺）。**时序如实标价**：5h 线在 05:50:46 才越，故动作窗落在 05:45/05:50/05:55 三次尝试；05:58 后**拒动**（宁 withheld 也不在 06:00 Guaranteed 点火本身上清锁，防与新品撞锁）。每次尝试的全部因子+判据逐项值写 `.runtime\tmp\backfix_zombie_gate_evidence.md`，动作行同件留痕（先证据链后动作）。`-Mode evaluate` 只读自评已实测：`zero_progress_s=8968 SATISFIED=False`，五件读数皆有值非崩溃。
- **批复②（补真接，最小面）实现+红绿双证**：真缺口不在我上段的"装饰件"表述里，而在 **`_kill_pid_tree` 级联腿**——`children(recursive=True)` 取回的整棵子树过去**零 cmdline 复核**，点火链形态（python worker → 其 backup.ps1 后代）下处决 worker 必顺带处决备份。落地三件：①新判据单口 `is_backup_form_cmdline()`（name 无关，禁他处再写字面量 `"backup.ps1"`，原 1264 行字面量已改走单口）；②级联腿按该判据过滤后代＋根判拒发（True=无需动作，非 [FAILED]）；③`_proc_cmdline` 守本件"永不抛"契约（2026-09-26 治本条），句柄类错误+鸭子替身缺方法一律降级空串=判不出即按原语义继续，绝不因观测面失能改写收割。头 `[INVARIANTS]` 同步补记。**未扩扫面**（powershell 不入判定矩阵=批复明令）。
  - 红证（改码前实测）：`test_kill_pid_tree_must_spare_backup_form_descendant` / `..._refuses_backup_form_root` 两支 **FAILED**（`backup.terminate_calls==1`＝缺陷复刻）；改码后同两支 **6 passed**（含原有四支：pid 回收必拦/活体 backup 必跳/死条目必销账/真超寿 worker 仍可杀＝反向回归未破）。
  - 回归面实测：`test_process_reaper_identity_recheck.py`＋`tests/legacy_zephyr/trading/test_process_reaper.py`＋`test_v7_pid_reuse.py`＋本文件＝**85 passed / 1 failed**；我一度把 legacy 两支 `TestKillPidTreeNeverRaises` 改红（`_FakeProc` 无 `cmdline`→AttributeError 上抛），已按"永不抛"契约自修并复绿。**残余 1 红非本批**：`test_v7_pid_reuse.py::test_pid_reused_by_innocent_process_is_not_reaped` 断言 `report.reported[0].reason=="incubation_expired_pid_reuse_skip"`，而 465f2779（10-10 17:31，批复①②本体）把该路径改判为 `identity_mismatches`+销账（现场值=`born_after_registration:reg_born=1000.0 live_born=now`）——**防误杀断言 `report.killed==[]` 仍通过**，红的只是回报通道；该测试件最近由 280a3870885（死信恢复 F1b 族 gov-23）恢复，恢复时未跟上 465f2779 语义。**本班不改它**（改他班红蓝网的断言＝改判据面，候处置）。
- **本班仪器面补记**：keep 册 `backfix_handle_poll` 一行经实测才成立——reaper 的 psutil 扫面按 `name` 含 "python" 过滤，故 powershell/bash 仪器**从不入面**（两陷阱 13h 孤儿+.runtime+超龄未死即此因）；keep 行只对 python 命名件有语义（atime 差分 57412 于 00:35:42 被 `runtime_dir_orphan` 处决＝python 命名且当时无 keep 行）。上段"校正③"已把本班一次误判如实入册。
- **复核命令**：`PYTHONPATH=src python -m pytest tests/infra/infrastructure/test_process_reaper_pid_recycle_backfix.py`（应 6 passed）；`powershell -NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\.runtime\tmp\backfix_dense_window.ps1 -Mode evaluate`（只读自评，应 SATISFIED=False 且五因子有值）；`grep -c '^### ' docs/_working/backfix_campaign/00_ledger.md`（本段后应 23）；`git show 465f2779 --stat`（v7 存量红的成因件）。

### 转义损伤修复留痕（接管巡检班 03:3x 轮，字节级零判断改动）

- **现象**：台账内 5 行含裸控制字符——U+0009（制表符）4 处 + U+0008（退格）5 处，全部是路径里的 \t/\b 在写入链里被当转义吞掉所致（\tmp→TAB+'mp'、\backup→BS+'ackup'、\tools→TAB+'ools'）。grep 这些路径必零命中＝引用即假。
- **成因归属**：其中 1 行属前班 00:5x-01:1x 轮（handle.exe 授权执行件里的 E:\tools\Handle），4 行属本班上一段与本段——同一条工具链陷阱（heredoc 里写 \\ 仍会先被吞成单层再被 Python 吃掉），非两班各自笔误。前班那 1 行一并修＝字节级还原其原意，零语义改动，如实在此留痕而非静默改他人文本。
- **修法与自证**：chr(9)/chr(8) → chr(92)+'t' / chr(92)+'b'，CAS 写；写后 TAB=0 BS=0、行数 280→280、改动行数=5（恰为受损 5 行）、删除内容行=0（除被修复行自身旧形态）。今后本战役写路径一律走 chr(92) 拼或 raw 串，禁在传输层写双反斜杠。

### 批复②复投与死信留痕（接管巡检班 04:0x 轮）

- **q-20261011-st-backfix-patrol-20261011-0001 判 dead**（dead_at=03:40:26，family=item:GATE-PRECOMMIT-RUN，recurrence_count=31）：死因命中本班自写代码——`check_any_abuse` ANY-1「函数参数裸 Any」= `_proc_cmdline(proc: Any)`；pre-commit 只在落地 staged 面（own-scope 临时索引）报，入队预检不吃这一下＝"ENQUEUED 绿灯≠落地绿灯"。修法：注解改 `object`（本函数的真实契约=任意带 cmdline() 的对象，缺方法已在 except 面降级空串），复跑 `check_any_abuse`+`ruff check`+`ruff format --check` 三支件全清后才复投。
- **不复用旧袋（不 requeue）**：袋内 files[] 存的是入队时的 blob 快照与 base_blob，requeue 会把**已判死的旧字节**再落一次（我改的 Any 注解与 v7 对齐都不在里面）。正解=以当前字节另起新袋；同 sid 同件的后袋会静默 supersede 前袋条目（在册行为，如实记，不当事故报）。
- 新袋含四件：`src/zephyr/trading/process_reaper.py`、`tests/infra/infrastructure/test_process_reaper_pid_recycle_backfix.py`、`tests/gov/governance/redblue_wave73/test_v7_pid_reuse.py`、本台账。

### 批复②加件：v7 红蓝网通道对齐 + 姊妹件同族红呈报（接管巡检班 04:0x 轮）

- **v7 已修**（Owner 批"按 465f2779 语义对齐断言+留痕"）：`tests/gov/governance/redblue_wave73/test_v7_pid_reuse.py` 的留痕断言由旧通道 `report.reported[0].reason=="incubation_expired_pid_reuse_skip"` 改为新通道三钉=`len(report.identity_mismatches)==1` + `reason` 含 `born_after_registration`（pid 复用的机读标记）+ `report.reported==[]`（反向钉旧通道不得复活/双通道重复记账）。**`assert report.killed == []` 原文原样保留未弱化**（Owner 明令），件首 docstring 同步记通道改判依据=465f2779。实测 `1 passed`。
- **同族红未动，候同一批准**：`tests/trade/trading/runtime/test_process_reaper_identity.py` 3 支红，机理与 v7 同源且更值得看——其中两支（`test_matching_identity_still_reaped`/`test_legacy_record_without_snapshot_still_reaped`）期望 `killed==1` 实得 0，真因不是 dry_run 而是**该件自带的 `_live()` 替身把活体写成 name="innocent"/cmdline="innocent.exe --serve"，与登记记录的 cmd/name 天然不符**⇒465f2779 的 `cmd_diverged` 赦免分支先命中⇒根本走不到收割。这是"替身与登记不同源"的测试自污染，改法有两种（替身 cmd 与登记一致=真验收割；或显式断言赦免=验证据），语义取向不同，**不属本班点名范围，不自决**。
- 判据面纪律：本班只动 Owner 批准的那一支文件的断言通道，未碰任何阈值/判据口径；`_DANGEROUS_*`、寿命阈值、身份复核三要素定义零改动。

### 批复③案卷：落地内存闸与落地 worker 工作集的撞车面（只出案卷，判据零改动）

**尺的更正（本班上一轮混用过两只尺，先纠正）**：dangerous 闸读的是 **RSS**（`_collect_metrics` 取 `proc.memory_info().rss`），而 `commit_pct`（02:58=72.75→03:40=81.78）是**提交电荷**另一把尺，本机 RAM 63.85GB。把二者并列为"在爬的风险"是我上轮的口径混用，如实更正。附带观测：同一闸值在两调用点比较符不一致（判定矩阵 `>` / derived_orphan `>=`）——零影响本案卷结论，记此备查。

**实测数（真源=`data/runtime/reaper_kill.log` 全史，class 由 cmdline 判，±15min 对账 `.runtime/commit_queue/dead/*.json`）**

| 面 | 样本 | 读数 |
|---|---|---|
| dangerous 行全史（09-28→10-11） | 27 | 其中真杀 26、本班只读 dry-run 1 |
| **落地侧**（cmdline 含 commit_queue+worktree） | 11 | RSS **11128-14813MB**，中位 11618MB；真杀 10 次跨 9 天≈**1.1 次/日** |
| 非落地侧（llama/聚合大户等） | 16 | min 312 / med 11036 / max 32488MB（闸的本意对象） |
| 撞车→死袋可证性 | ±15min 内 6 只 | 6 只各带自成因（GATE-VOCAB×2／GATE-PRECOMMIT-RUN／注册表三向合并失败／ghost_session×1），**记"worker 中途消失"者=0** |
| 分母 | done 731 / dead 1419 | 死袋占比 66.0%（多因合计，非本闸专属） |

**结论（案卷级，非裁定）**：闸值 10GB **落在落地 worker 的常态工作集之下**——被 reaper pass 看见的落地 worker 11/11 全部超闸，所以这不是偶发越界而是结构性压线；是否真被杀取决于 pass 是否撞进落地窗（pass 节奏约 10min）。但"杀了会不会坏袋"在**现有账面不可证伪**：真杀 10 次，邻近死袋各有独立成因，无一只记 worker 中途消失——要么杀在非关键阶段、要么队列静默重试而未记账。
**三条候选（走正道呈报，本班一律不动手）**：A 闸值按机分档（如 max(10GB, 25%·RAM)）或按进程身份分级；B 落地 worker 显式豁免＋配"超时必收"上限；C **先补观测面**＝落地侧记 worker 退出码/中途消失账，把真实撞车率测出来再定 A/B。本班荐 **C 先行**：无观测面的判据改动＝第二次盲改（本台账已有"覆盖尺提到即算必假绿""恒绿无配对测试判疑似判据失效"两条在册教训）。

### 批复④：双机制假说段（级联已修／读锁居民在追／06:00 为分水岭）——接管巡检班 04:0x 轮

- **机制A＝级联腿顺带伤亡（本班已修，且如实降级为"非主杀径"）**：`_kill_pid_tree` 递归子树零 cmdline 复核，点火链形态（python worker→其 backup.ps1 后代）下处决 worker 会带倒备份。**但它解释不了观测时序**：级联是"先子后父、同一次动作"，而案 #5-#14 十三例是 worker 被处决后 **+1.7~24.7min** 才死。⇒ 机制A 修的是附带伤亡面（防线价值成立），主杀径另在他处。
- **机制B＝读 backup.lock 取 pid 的仓外/隐名 resident（在追，仍是主假说）**：本轮把能力面钉实了一格——本器扫面按 name 含 "python" 过滤，任何"reaper 合规收割 powershell 备份本体"的分支都**结构性不可能**；反之 `psutil.Process(pid).kill()` 一类按 pid 直杀**不受 name 过滤约束**，与"读锁取 pid→分钟级处决→杀后删锁"的画像一致。三证已就位候下一例：handle 轮询哨（46444，实测免死）＋atime 差分（57008）＋event watch/PPID（57184/43560）。
- **06:00＝分水岭判读**：这次点火是"belt_watchdog 修复＋机制A 修码已入运行面（磁盘现字节）＋金丝雀已拆"三者叠加后的首个 Guaranteed 点火。三件齐（state mtime 变＋last_backup_time 推进＋report json 落）⇒ 杀面收敛到"与 reaper 家族周期同源"的残余，止血定谳；仍落在 +1.7~24.7min 滞差带内 ⇒ 机制B 的 resident 确在，且此时挂着的 monitor/三证将首次给出跨 name 的按 pid 直杀捕点。
- **本班读数（04:0x）**：24968 存活 242min（超全部受害者年龄），G 面零推进 3h12m，STAGE 4 三件全缺；挂死门按批复①保持 5h 线不动（05:50:46 越线，动作落 05:50/05:55 两次尝试，05:58 拒动）。

### 落地验证＋自动化续岗＋陈旧 index 复筛（接管巡检班 04:3x 轮）

- **q-20261011-st-backfix-patrol-20261011-0002 已 done**，落地面三口径实测：`git show HEAD:src/zephyr/trading/process_reaper.py` 含新判据 6 处、`git show HEAD:tests/gov/.../test_v7_pid_reuse.py` 含新通道 5 处、HEAD 侧本台账 `^### ` 计数=28（=本机盘面同值，四段新账俱在）。HEAD 尖端此刻是他班袋（`q-...-st-finalclean2-20261010-0012`，只动它自家账本件），本修复是其祖先——不是"我的袋没落"。
- **拆掉一颗回退弹**：袋落地后主区 index 仍留着这四支的**旧字节**（`index_vs_HEAD` 依次为 +5/-48、+0/-87、+4/-9、+1/-63），即在册的"陈旧 index 只在 merge finalize 才炸"形态；若后续有人从 index 出袋或走 merge，会把已落地的级联修复与 v7 对齐**整档打回**。拆法=按册内既有处方对自己这四路 `git add --`（盘面已等 HEAD，取的是自有件现字节，零他人面）；拆后复验＝四路 index/worktree/HEAD **三面全等、git status 零行**。纪律缺口一并认：本班此前只 claim 了代码与两支测试件，未 claim 本台账就动了它。
- **自动化续岗已建**（Owner 追问"为什么不用 Qoder 自动化"后补正）：本地 cron `id=9cbf6aef-845f-47ab-be1b-a8a17d8a81d9`，名称「备份链凶手巡检·30min（st-backfix-patrol-20261011）」，every=1800000ms，next_run=2026-10-11 05:03:26，**expiresAt=2026-10-12 06:30:00（24h 硬上限，防收线后空转烧轮）**，model=qfmodel（继承本会话），permission=bypassPermissions，outputMode=independent（每轮以台账＋日志为真源，不累积上下文）。prompt 写死：只读取证、定名才落册、判据/阈值/门禁代码零改动、禁杀进程、禁碰 G:、勿重复起在岗仪器、reader-namer 勿复活，以及本班两条自犯换来的铁律（零反斜杠写路径／CAS＋写后控制字符计数自证）。
- **为何先前只用 OS 进程**（排序失误如实记）：机械采样与挂死门用进程=零轮子成本、可复现、留痕确定性优于让模型轮去执行一次 kill；但**跨会话值守恰是自动化的独占地位**，我在发现自动化停摆的当轮只附了一句选项而未立即建，属排序失误，本轮补正。二者分工此后=进程管采样与门（05:30-06:30 加密窗照旧），自动化管判读与续岗。
- **前班判语更正**：令卡"巡检自动化 automation-62fd8292 每 30 分钟常驻"不成立——本地自动化面查无此件＋巡检日志 02:56:28 后 03:17/03:47/04:17 三格零行＝停摆。本班 04:20:43 起以 `backfix_ticker_until.ps1` 补盲，**02:56-04:20 计 84 分钟无 patrol 盲区如实入账**（monitor 15s 采样在此期间未断，故非全盲）。
- 复核命令：`git show HEAD:src/zephyr/trading/process_reaper.py | grep -c is_backup_form_cmdline`（应 6）；`git diff --cached --numstat HEAD -- src/zephyr/trading/process_reaper.py`（应空）；`python scripts/commit_queue.py status --session st-backfix-patrol-20261011`（done=1/dead=1）；`qoder_cron list` 见 9cbf6aef 且 enabled=true。

### 提前点火令执行件（Owner 反拖延直令，接管巡检班 05:3x 轮）

- **令①处置·时刻先对表**：令卡写作 05:0x／零推进 4h10m，本班 **05:33:03 实测**＝零推进 4h42m、存活 5h33m（5h 线原拟 05:50:46 越线，故本次比脚本门提前 17 分钟执行，两者判据同一件不另开口径）。五因子现值：alive=True／state mtime 仍 2026-10-10 22:58:40／last_backup_time 仍 2026-10-09T07:48:15／`logs/backup_report_20261010_2359*.json` ABSENT／G_mtime 冻结 00:50:46。
- **挂死定性补一条硬对照**（不是仅凭"三件全缺"）：24968 cpu_total=364.8s、cpu_d 稳 0.3/15s ≈ 单核 2%＝**周期轮询而非做功**，且子进程面只有 conhost、零工作子；对照 05:34 新实例同尺度下 `kids` 里明确有 `pg_dump.exe -Fc -h localhost -U zephyr -d depgraph` 在跑——"健康实例带工作子、该实例四小时无工作子且近零 CPU"才是本次处置的实证核。动作序＝先证据链后动作：Stop-Process 24968 → 复验 alive=False（05:33:59）→ 删 `.runtime/backup.lock` → 复验 exists_after=False。凭据件=`.runtime/tmp/backfix_zombie_action_evidence.md`（点火前清场凭据）。
- **令②点火·方式偏离如实记**：用 `Start-ScheduledTask -TaskName ZephyrAlpha-DailyBackup` 一次性触发，**未改任务定义/未新增触发器**（可逆且更不侵入，自然点火效果等同；原 06:00 触发器一字未动，届时按令卡预判 lock_held 让路=无害）。实测 05:34:14 state=Running、res=267009（=运行中非失败）；出生链=22976 `wscript.exe` → 24468 powershell（05:34:34），锁面 05:34:39 写入 `PID:24468 START:2026-10-11T05:34:39.8269427+08:00`。
- **新显形（待扫面，非本班权限）**：DailyBackup 的任务动作经 **wscript 宿主**起 powershell，而非直起——与主使画像"仓外/隐名 resident（脚本宿主形态）"落在同一类观测面上。后续定名须把 `wscript → powershell` 这条宿主链一并纳入出生链排查，此前各案卷只查到 powershell 层。
- **令③读数已就位**：新监听 pid=25120（`-WatchPid 24468 -SampleSeconds 15`），首周期即见 pg_dump 子进程＝做功正证；handle 哨(46444)／atime 差分(57008)／三陷阱(57376/43560/57184) 全在岗；完整轮预计 ~07:4x 出定谳（比原计划提前约 1h）。
- **机器面假案显式标注（防下一班误计）**：patrol 于 05:35:03 把我方受令清场记成 `TARGET_DEATH pid=24968` 并写 `backfix_killer_case_20261011_053503.md`（candidates=545），05:34:13 另有同事件二件。**两件案卷皆=本班受令处置，非新增他杀，不得计入案 #15**；连环案清仓数仍=案 #3-#14 十例。旧监听 47956 已随目标消亡自然退出（实测 alive=False）。
- 复核命令：`Get-Content .runtime/tmp/backfix_zombie_action_evidence.md`；`Get-Content .runtime/tmp/backfix_monitor_24468.log -Tail 3`（应见 kids 含 pg_dump）；`Get-Content .runtime/tmp/backfix_patrol.log -Tail 8`（TARGET_DEATH 24968 那条=手杀）；`git show HEAD:docs/_working/backfix_campaign/00_ledger.md` 后数 `^### `（本段落地后应 30）。

### 四选续批执行件（总统统筹 05:5x 条①②③④·接管巡检班 05:5x 轮）

- **条① 宿主链判据入册＋22976 身份查清**：`Get-ScheduledTask ZephyrAlpha-DailyBackup` 的 Actions 实测＝Execute 为 wscript.exe，参数指向本仓自有 **`scripts/launch_hidden.vbs`**（#ARCH-BOOT-WINDOW-FLASH 治本的"无闪窗启动器"），再透传 `-Mode all -Force` 给 backup.ps1。⇒ 22976 **不是仓外隐名件**，是本仓点火链第一环。全仓 .vbs 仅此一支；对该层 grep `terminate|kill|taskkill|Win32_Process` **零命中**＝宿主层无杀原语——此前"仓内无杀手"审计只覆盖 .py/.ps1，本次把 .vbs 这一层补进覆盖面。**缺的是判据不是仪器**：三陷阱日志里 wscript 出生记录分别 1578/2119/2020 行，观测面早有数据，只是定名时没往宿主层看。已按批准把"出生链三环"写进自动化 prompt（①脚本宿主层 wscript/cscript 及其 .vbs/.js 实参 ②任务计划层 Actions 逐字对比 ③powershell/python 原行凶面；两层以上同刻且非本班仪器才标候捕点），**零阈值改动、纯增证据**。附带在册事实：launch_hidden.vbs 文内明写 Task Scheduler job object 会在父进程早退时误杀孙进程——这是前班 handle 哨 26100 之死的最合理解释（非 reaper，击杀册零行）。
- **条② 姊妹件 3 红→5 绿，取向＝"正证用真身份＋赦免显式断"**（`tests/trade/trading/runtime/test_process_reaper_identity.py`）：两支收割正证的活体 name/cmd 改为**从真起的 sleeper 现取**（登记面与活体面同源）。旧替身把活体硬写成 name=innocent／cmd=innocent.exe --serve，与登记 cmd 天然不符 ⇒ 465f2779 的 image/cmd 复核先赦免 ⇒ **那两支"收割正证"其实一直在空跑**（不是断言过时这么简单）。PID 复用那支按 v7 先例对齐新通道（identity_mismatches＋born_after_registration＋reported==[]），`killed==[]` 防误杀钉桩原样保留。另**新增反向钉桩** `test_identity_alignment_is_what_enables_reaping`：同 pid／同 create_time／同 name，只把 cmd 一个要素改歧 ⇒ 必不杀且留痕 cmd_diverged——把"正证不许退化成空跑"钉成一条会见红的测试。legacy 那支的 born 锚退回 spawned_at 这一实现事实也写进 docstring（不再是"不判"）。红证＝改前实测 3 FAILED（04:2x 留档）→ 改后 5 passed；ruff check/format 先双清再入队（防 RUFF-PRECLEAN 烧掉一整轮落地，本袋已吃过一次）。
- **条③ 观测面 v1 已支（只出数不改判据）**：`backfix_landing_watcher.ps1` 15s 周期记落地侧 worker 的 pid/RSS/age，自终止 4h，日志 `.runtime/tmp/backfix_landing_journal.csv`。**本班两处自犯当场改掉**：①分类器初版用"整行含 commit_queue 且含 worktree"，误吃一支 10-07 起跑、4.1 天龄、RSS 0 的 `detect_permanent_file_deletion.py tests/gov/.../test_commit_queue_integration.py`（**参数**里带 commit_queue 就被算成落地 worker）⇒ 收紧为只认路径段相邻（正则字符类含正反斜杠）；②head 列初版取"输出里第一个 qid"，抓到一枚已 done 的 10-04 旧袋＝**假楔死**，差点误报队列卡死 ⇒ 改为只取 head 块内的 qid。**残余缺陷如实报**：head/lease 两列现恒为 QUERY_FAIL（PS5.1 下子进程取数进 catch），worker/RSS 面可用；撞车率归因先以"journal 时间戳 × 队列 store 的 claimed/done 时刻"事后对齐，判据变更仍走正道呈报。
- **条④ 旧自动化已删**：`ee2a753b-4e6a-4e22-b565-a95ca82284c3`（st-t0-matrix-20260924 包自挂监控，disabled/pauseReason=manual 滞留 15 天；其 prompt 自述收官条件含"自动化已自删"却从未执行，属在册"收口后空转"残留）。删除前整段 prompt＋逐字段回滚参数存证于 `.runtime/tmp/backfix_salvage_cron_ee2a753b.md`；该存件系本班手抄、自标一处措辞漂移（原文"cost_trio 全窗扩量"），**逐字节回滚以删除前 `qoder_cron list` 原始返回为准**，不把抄录当字节级真源。
- **邻位读数（非本班件，只报不动）**：landing 侧现有一支 `python -m zephyr.governance.audit.reconcile_worker --payload .runtime/commit_queue/worktree/...`（pid 50788，106MB，龄 13min）。它正是历史九案里"点火 worker 先被 1800s 合规处决"的那一形态；本班 05:34:39 点火的样本 24468 若其 worker 被处决，滞差带即开始计时——观察点已就位（handle 哨＋atime 差分＋三陷阱＋新监听 25120）。
- 复核命令：`Get-ScheduledTask -TaskName ZephyrAlpha-DailyBackup | Select-Object -ExpandProperty Actions`（应见 wscript＋launch_hidden.vbs）；`PYTHONPATH=src python -m pytest tests/trade/trading/runtime/test_process_reaper_identity.py`（应 5 passed）；`Get-Content .runtime/tmp/backfix_landing_journal.csv -Tail 3`；`qoder_cron list`（9cbf6aef 应 revision=2 含宿主链段；ee2a753b 应不在列）。
