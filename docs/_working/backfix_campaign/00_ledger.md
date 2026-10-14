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
### 自犯留痕：本班重复挂哨把监听尺写成双写手（Owner 批复①，巡检自动化班 05:5x 轮）

- **事实**：在册哨 pid=25120（05:35:27 起，-WatchPid 24468）已在盯新品，本班 05:48:28 未先查在册表又起一支 54260 同盯 24468，两支同写 .runtime\tmp\backfix_monitor_24468.log。
- **污染确切区间**：05:48:29（54260 首行 MONITOR_START）→ 05:50:44（本班拆除）。54260 写入 cycle=1..8，与 25120 的 cycle=46..57 交错；行级实样=05:50:33 cycle=8 / 05:50:40 cycle=56 / 05:50:56 cycle=57。
- **后人误读风险（为何必须记）**：该件的 cycle 号在 05:48:29–05:50:44 段内非单调。若按“cycle 归零=监听重启过”取断点，会多计一次重启事件——真实重启仅 05:35:27 那一次。
- **拆分手法（可复用，本班不靠 pid 字面）**：双条件锁唯一 pid——cmdline 匹配 'WatchPid 24468' 且 CreationDate ∈ [05:48:00,05:49:00]。用时刻窗是必需的：查询进程自身的 cmdline 也含 'WatchPid 24468'（实测 pid=22868 落在 05:49:55，被窗排除）。
- **同轮另一处本班自犯（路径凭记忆）**：本班首轮查锁查的是 data\runtime\backup.lock 得 ABSENT 并据此说“锁已没”——假阴性。真锁=.runtime\backup.lock（monitor 参数 -LockFile 缺省值），实测 05:34:39 已由 24468 重建（内容 PID:24468 START:2026-10-11T05:34:39.8269427+08:00）。
- **复核命令**：`powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*backup_forensic_monitor*' }"`（应只剩 25120）；`Select-String -Path .runtime\tmp\backfix_monitor_24468.log -Pattern 'MONITOR_START'`（应见 05:35:27 与 05:48:29 两行，后者=本段污染起点）。

### 归罪面读数：机制A 本案排除 / 机制B 杀法被本班清场原样复刻（Owner 批复④入册）

- **机制A（reaper 级联腿误杀）本案排除**：data\runtime\reaper_kill.log 对 24968 零命中；05:20–05:39 整段零行；该件末行=2026-10-11 03:40:48 DRY-RUN（PID=50844，reason=dangerous:mem=11128MB）。⇒ 本案死亡与收割无关，10-11 那笔“豁免 backup 形态后代/根”的修码在本案无适用面（无级联可谈）。
- **机制B 画像被本班自己的清场复刻了一遍**（出生链在案）：procstart_trap_ppid.log 05:33:59 行=pid=37564 ppid=45548 powershell 起 'Stop-Process -Id 24968 -Force; Start-Sleep 3; 复测 [bool](Get-Process -Id 24968)'，05:34:12 行=pid=23648 ppid=57352 powershell 起 'Start-ScheduledTask -TaskName ZephyrAlpha-DailyBackup'；中间夹删锁。动作序列=**读 .runtime\backup.lock 取 PID: 字段 → 按 pid 直杀 → 复测 → 删锁 → 重点火**。
- **本案不指认未知主使**（B 既未证实也未证伪；清场方是本方受令动作，非外来 resident），但把一句推论变成了实测事实：**任何能读该锁文件的进程都拿到“杀谁”的坐标**，且杀完还能顺手清锁骗过“锁消失=正常收尾”的读法。
- **并入处方②推广的立法理由（追加，不改原段）**：处方②只解决“reaper 扫面 name 过滤”与“级联腿零复核”，防不住这条零门禁通道——杀方的能力来自**锁文件内容可读**，与进程扫面权限无关。故推广面应有的形态是“锁内除 PID/START 外还须有让杀方能被身份校验拦下的东西”，属判据设计面，本班不自拟。
- **附带显形（不作罪证）**：DailyBackup 的动作是 wscript 宿主 → launch_hidden.vbs → powershell（实测 22976→24468），故“看到 wscript 起 powershell”在本机是备份自身的常态启动形态，不能作为 B 画像的定罪特征；另 state 册 last_ignite_error 存有一条 Start-Process 失败记录，备查。

### 06:00 二次点火实测 + 挂死闸解钉（Owner 批复②③执行件，巡检自动化班 06:0x 轮）

- **②实测：让路发生在调度层，锁层未被触达**。任务 ZephyrAlpha-DailyBackup 06:00:01 触发，LastTaskResult=2147946720（0x800700E0），Settings.MultipleInstances=**IgnoreNew**，而 05:34:14 那次点火的实例链（wscript 22976 → powershell 24468）当时仍 Running ⇒ 调度器直接丢弃新实例。陷阱出生链 05:59–06:03 零条 backup.ps1 或 wscript 带 backup.ps1 参数（同窗只有 start_scheduler / ensure_ai_wrapper 类守卫件）。**预期中的 lock_held 让路没有被演练到**，06:00 这一格今日的备份只由 05:34 的手工点火供给。
- **锁层通路另证（非本窗）**：state 册 last_run_outcome=lock_skipped，last_lock_skip_time=2026-10-10T14:58:40.675229+00:00（本地 10-10 22:58:40）⇒ 锁层让路确会回写此册，但那是 10-10 的事。
- **连带定性（呈批面）**：闸的基线 BaseStateMtime=2026-10-10 22:58:40 本身就是一次 **lock_skipped 事件**的册写时刻，不是一次成功备份的时刻。“state_mtime 未变”读的是“链上再无人回写过册子”，不等于“上一次备份完好”。五因子其余件：last_backup_time=2026-10-09T07:48:15 且 last_backup_status=failed。
- **③改造落地**：.runtime\tmp\backfix_dense_window.ps1 由钉 TargetPid=24968 改为**启动时解析锁内 PID: 字段**；五因子判据/阈值/时序（05:45 起评、GateAfter+13min 即 05:58 拒动、06:30 自终止）**零改动**；新增两个只读测试口 -LockOverride / -MonLogOverride（缺省即生产路径，run 模式行为不变）；锁不可解析 ⇒ TargetPid=0 ⇒ alive 恒 False ⇒ 判据必假（fail-closed，同时封掉 Get-Process -Id 0 把“Idle 进程”读成活体的开口）。实测：非 ASCII 字节=0，AST 解析错误=0。
- **三证（全部 -Mode evaluate，零副作用，合成件留 .runtime\tmp 供复跑）**：P1 合成死 pid 锁（PID:24968）→ TARGET_RESOLVED=24968 alive=False SATISFIED=**False**（对旧 pid 不误开）；P2 生产锁 → TARGET_RESOLVED 自动跟到 **24468**，G_mtime 已推进 ⇒ zero_progress_s=14 ⇒ SATISFIED=**False**（现持有者正常生效且不冤枉干活的）；P3 合成冻结尺（末行 G_mtime=00:50:46）⇒ zero_progress_s=18999 ≥18000 ⇒ SATISFIED=**True**（判别力仍在，非恒绿）。合成件=.runtime\tmp\backfix_gateproof_deadpid.lock 与 .runtime\tmp\backfix_gateproof_frozenmon.log。
- **激活状态如实**：在岗 run 模式件 pid=43596 仍以**内存里的旧钉值**运行（改文件不改在飞进程），06:30 按设计自终止；本班未重启它。理由实测：G 面 06:03:33 已解冻，5h 零推进线在剩余窗口内不可能再达，重启只是把同一判据再跑三遍。若要“解钉形态即刻生效”，须另批一个新窗（含新的 GateAfter 语义）——属判据面，本班不自决。
- **止血三件现状（06:07 实测，仍全缺未定谳）**：state_mtime 仍 22:58:40；last_backup_time 仍 2026-10-09T07:48:15；logs\backup_report_20261011_*.json 无。**做功正证已换形态**：VHDX mtime 06:03:33→06:07:11 连续推进（冻结 5h17m 破），06:06:45 周期见子进程 curl.exe --data-binary → http://172.24.30.100:8123/（CH 导出段），此前 05:47 实测 pg_dump 输出 15 秒涨 2,498,560 字节。挂死期形态=子进程仅 conhost＋cpu_d 稳 0.3/15s 的 2% 周期轮询，二者可分。按 ~07:4x 完整轮判三件齐。
- **署名与待裁**：adjudicator=巡检自动化班（st-backfix-patrol-20261011）。候裁两项：解钉形态的新窗授权；5h 零推进线在“实例已换、G 面已解冻”后是否仍按原线读。
- **复核命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File .runtime\tmp\backfix_dense_window.ps1 -Mode evaluate`（应 TARGET_RESOLVED=当前锁内 pid 且 SATISFIED=False）；同件加 `-MonLogOverride .runtime\tmp\backfix_gateproof_frozenmon.log`（应 SATISFIED=True）；`Get-ScheduledTask -TaskName ZephyrAlpha-DailyBackup | Select -Expand Settings | Select -Expand MultipleInstances`（应 IgnoreNew）。
### 本班口径更正：锁层其实一直在演练 + 新品 24468 二次挂死（巡检自动化班 10:0x 轮，Owner“不记就是埋雷”同规自纠）

- **更正①（推翻本班 06:0x 段里“锁层根本没被触达”那句）**：实测 logs\backup_skipped_20261011_*.json 今日 **28 份**，reason 一律 `lock_held`，末份 09:17:00 记 lock_age_hours=3.71 / lock_mtime=05:34:39 ⇒ **锁层让路一直在演练**。06:0x 段那句只对了一半：被调度层 IgnoreNew 抢先挡掉的只有 06:00:01 那一格（LastTaskResult=2147946720），其余重试源每 15–30 分钟撞一次锁并留痕。原段不删（他人已读），以此段为准。
- **更正②（零推进尺的覆盖面）**：闸与本班的 G 面尺读的是 `G:\ch_backup_disk2.vhdx`，该件只属 **STAGE 2（CH 双写链）**；STAGE 3 写的是 `G:\backup\working_vault\<yyyyMMdd>`。⇒ 单看 vhdx 冻结不能判整链零推进，必须同时看 vault 日目录条目数。本段附实测：24468 的 vhdx 冻结于 07:34:35，而 20261011 日目录 07:34:29 建立后**条目数=0 且 45 秒差分仍=0**——两处同时冻结，才构成挂死判据（缺一即不可判）。
- **新品 24468 已重演挂死（10:04 前后实测，非死亡）**：pid 存活、持锁 PID:24468 START:05:34:39；子进程只剩 conhost；cpu_total 06:12=2.4s → 09:54=14.1s（3h42m 只涨 11.7s）；监听 cpu_d=0.1/15s；**IODataBytesPersec 三次采样（间隔 8s）全=0，PageFaultsPersec 0，线程 10 条全处 Wait**。出生链最后一条=07:34:27 `ch_vm_ssh.py --cmd 'sudo -n rsync -a /mnt/chbackup_local/market.zip /mnt/chbackup_local/inc.zip /mnt/chbackup2/ && ls -la …'`（07:34:32 退，5 秒＝不可能是 45.8GB 的真同步，判为增量已到位的快速返回或早退），此后**再无任何子进程出生**。
- **挂死点新定位（STAGE 3 起始，非 STAGE 2）**：handle64 -p 24468 见持有目录句柄 `G:\backup\working_vault\20261010\docs\03_modules\_domain_orchestrator\algo_flow`（=**比对上一日快照**那条腿）。该叶子本身健康：74 条目、python 枚举+stat 全 <1ms、零硬链 ⇒ 句柄更像 backup.ps1:665 `EnumerateFileSystemEntries` 惰性枚举**未 Dispose 的遗留**，而非当前卡点本身。空间闸已排除：G 余 1934.8GB，20261008–20261011 四个日目录 45 秒差分零变化（没在删也没在写）。
- **判别力诚实交代（别当工具用）**：线程等待码**没有判别力**——参照进程（自起的 `Start-Sleep 40` powershell）等待码分布同为 6/15，与挂死体不可分。⇒ 停在 backup.ps1 哪一行，从盘外无法定名；要定名须采栈（procdump 一类），而它会短暂挂起**今日唯一在飞的备份**，本班不自决，候 Owner 批。
- **观测面根因（“链为何总查不出”的答案，呈批面）**：backup.ps1:51-57 注释自陈 stage_timeline 是为“09-25 那轮 9.1h 只能靠 NTFS mtime 复原”而加，但 `Write-Stage` 只累积进 `$script:StageLog` 且**只由 STAGE 4 落进 report json**⇒**凡挂死的轮次天生没有阶段日志**（logs\backup_report_20261011_*.json 今日 0 份即为证）。故 24968 那具的挂死点永远无法定名，今后每具僵尸仍只能靠 mtime＋句柄反推。属判据/可观测性设计面，本班不自拟修法。
- **止血三件现状（10:04 实测，仍全缺）**：state_mtime 仍 10-10 22:58:40｜last_backup_time 仍 2026-10-09T07:48:15（last_backup_status=failed）｜report json 0 份。07:4x 完整轮未达成谳。
- **署名与复核**：adjudicator=巡检自动化班（st-backfix-patrol-20261011）。复核命令：`python -c "import glob;print(len(glob.glob(r'logs\backup_skipped_20261011_*.json')))"`（应 28）；`handle64 -accepteula -nobanner -p 24468`（应见 working_vault\20261010 目录句柄）；`Get-CimInstance Win32_PerfFormattedData_PerfProc_Process -Filter 'IDProcess=24468'`（IODataBytesPersec 应 0）；本机巡检件 .runtime\tmp\backfix_monitor_24468.log（cycle=1021 @09:55:09 为末读）。

### vhdx 压缩执行令·前置核验与两处前提证伪（接管巡检班 10:5x 轮）

- **时序偏差先入账**：令卡写于 05:5x／06:1x 窗，本班实际开工 **10:57**（两轮之间隔 4h50m），令卡内的"当前态"读数已全部过期，下述两条即据此重测。
- **① 采栈按字面不可执行**：procdump／procdump64／windbg／createdump 实测**全部不存在**（PATH 内零命中，E:\tools 仅 Handle 一件）。改用免费替身取证：线程数 12s 内 11→10（有线程正常退出）、CPU 累计 117s 仍在走、PageFaults/s=0、`handle64 -p 24468` 句柄清点见 **File 句柄 `G:\backup\working_vault\20260926\.worktrees\st-p6-t1top\tests\reporting`——该路径现已 PATH_MISSING**＝正在对陈旧 worktree 镜像做剪枝。要真用户态栈须先取 Sysinternals Procdump（新第三方件下载，另候批准，不擅自扩授权面）。
- **② 处置前提被实测证伪，本班未执行 kill**：令卡把 24468 判为"挂死照 05:34 先例处置"，而 10:5x 实测＝它**在动**——`G:\backup\working_vault\20261011` 目录 mtime **10:35**、老快照 `20260926\.worktrees` 目录 mtime **10:58:40**（就在此秒被改）、已存活 5h24m 未死（超全部受害者年龄，止血面读数反而更强）。在一个正在写镜像的进程上做 kill＋清锁，等于把 vault 留在半剪枝态，再进 ③④ 停机压缩＝不可逆面叠加。**故停在 ② 之前，把决定权交回 Owner**。
- **连带一条自我更正（要紧）**：上述镜像剪枝形态同时解释了 05:34 那次我把 24968 判"挂死"的 2% CPU 读数——枚举/删除型工作本就是低 CPU 长时长。本班当时记过"cpu_d 0.3 非零"却仍按"三件全缺＋零推进 5h"下了挂死结论并执行；若 24968 当时也在剪枝，那次处置就是**杀了活体**。此条不遮掩，随删随记，等下一例的对照。
- **③④ 压缩前置实测**：`Optimize-VHD` 可用（Hyper-V 模块在册 True）；VM 清单＝`zephyr-ch` **Running**；`D:\HyperV\VMs\zephyr-ch\data.vhdx` **589GB，mtime=10/11 10:58:40＝此刻仍被写入**（停机前必须先确无占用，令卡③"优雅关机"方向正确）；**宿主 D: 仅剩 48GB（684/732G，94% 满）**——对 589GB  vhdx 做压缩的余量极薄，这是本轮与 09-28/09-30 两跑的实质差异，须 Owner 知悉后再定起跑时点。
- **未证的一条账面值**：令卡"本轮 OPTIMIZE 已腾 57.9GiB ⇒ 预期还给宿主 40-60GiB"。本班尝试用 DatabaseService 读 guest `system.disks` 的 available_space 来坐实，**取数失败**（`'DatabaseService' object has no attribute 'query'`——API 名不匹配，非 CH 故障），故该 57.9GiB 目前**只有账面、无本班实测**；在册记忆另有一条"09-28/09-30 压缩收益≈0"的旧实测，两者相抵，压缩收益应以 guest 盘实测为准再判。
- 复核命令：`Get-VM | Select Name,State`；`Get-ChildItem D:\HyperV\VMs\zephyr-ch\data.vhdx | Select Length,LastWriteTime`；`df -h /d`；`handle64 -accepteula -nobanner -p <活体pid>`（看 File 句柄落点）；`ls -lat /g/backup/working_vault/`（镜像是否仍在推进）。
### 案 #15 定名读数：24468 自毙非他杀（引擎 403 与进程退出成对）＋宿主层 4h 时限实证（巡检自动化班 12:3-13:0 轮）

- **时刻两尺相符**：patrol 12:34:57 报 TARGET_DEATH pid=24468（detected 口径），秒级真值取陷阱 EXIT 行 **12:19:17**（pid=24468 ppid=22976 name=powershell.exe）；活体监听 15s 采样末次存活=12:19:04、判亡=12:19:19，两尺相容。**无第二例**：新锁持有者 45640（12:25:17 起，同任务同参 -Mode all -Force）13:00 实测 ALIVE 且持锁。本班一处自犯当场更正：12:37 一次 Win32_Process 过滤查询返回空，本班据此差点记"45640 亦亡"，12:38:25 同分钟双尺复测（CIM 行 + Get-Process）=ALIVE＝WMI 瞬时失败，非死亡（运行态断言同分钟复测在册规矩再次生效）。
- **定名结论＝机器面假案（自毙，非他杀）**，三条独立反向证据：
  1. Windows PowerShell 通道在 **12:19:13** 有 **id=403 引擎 Stopped**，HostApplication 逐字＝powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File D:/ZephyrAlpha/scripts/backup/backup.ps1 -Mode all -Force，SequenceNumber=758286。外部 TerminateProcess 不给引擎写 403 的机会 ⇒ 关停由引擎自身发起，4s 后进程退出＝收尾 drain。
  2. 真死窗 [12:14-12:21] 陷阱出生链**零 kill 原语**（无 taskkill / cmd /c / wmic / Stop-Process / python 杀件）；非本班仪器者只有系统维护簇与 backgroundTaskHost。
  3. **机制A 三重排除**：主区 reaper 在岗实写（data/runtime/ghost_suspects.json 12:47:38 更新，suspects 空）；ghost 状态机第一道判据即 name 以 "trae cn" 开头（src/zephyr/trading/process_reaper.py:806）⇒ powershell 永不入列；全盘 3 份 reaper_kill.log（主区 + 2 枚影子根 .runtime/tmp/st-deadcure2-20261009/runlane_3/… 与 .worktrees/st-maint2-20261011/…t6_red_sandbox/…）今日 **05:48:32 后零行**；且 data/runtime/process_reaper_keep.txt:70 在册豁免 backup.ps1、码面 is_backup_form_cmdline 在 _kill_pid_tree 根(:729)与子(:741)双腿赦免。级联时序亦不可能：父 wscript 早在 09:34:17 亡，级联是即刻而非延时 165min。
- **出生链判据·宿主链层新实证（条①②）**：Get-ScheduledTask ZephyrAlpha-DailyBackup 的 Settings 实测 **ExecutionTimeLimit=PT4H / MultipleInstances=IgnoreNew / RestartCount=1 / RestartInterval=PT30M**。05:34:39 点火 → wscript 22976 于 **09:34:17** 亡＝4h 时限到点停任务（差 22s 属调度粒度）。而 scripts/launch_hidden.vbs 文内 sh.Run cmd, 0, True 本应等子退，孙 powershell 却续跑 2h45m ⇒ **该任务的 job object 未把孙纳入**，"父亡必连坐孙"在本机此任务上未复现。**连带削弱前案一条归因**：05:5x 段曾据该 vbs 文内自述把 handle 哨 26100 之死判给 job object 误杀；本案证明同一通道对 24468 未开火，且哨本身非该任务后代 ⇒ 该归因失去支撑，handle 哨之死回到"未定名"。vbs 层 grep terminate|kill|taskkill|Win32_Process 仍零命中，全仓 .vbs 仍仅此一支。
- **死前在做什么（阶段可定位、行不可定名）**：SequenceNumber=758286 对 6h44m 实活 ≈ 每秒 31 次管线调用＝逐项枚举形态而非等待形态。vault 面实测：G:/backup/working_vault/20261011 条目 **62**（对照 20261010 的 64＝当日快照残缺），其内最新条目停在 **10:35:47**；而父目录 **G:/backup/working_vault 自身 mtime=12:19:10＝引擎 403 前 3 秒被改**（根层条目增删＝保留/轮换腿此刻在动）。停点即 backup.ps1:655-674 的 Get-SourceFileIndex 手工栈遍历（:665 EnumerateFileSystemEntries，与前班 10:5x handle64 所见陈旧 worktree 镜像句柄同一条腿）。具体行盘外不可定名，采栈工具 procdump/procdump64/windbg/createdump 实测仍全不存在（前班 10:5x 已记，本轮复核未变）。
- **记账后果（备份链的真问题不在凶手）**：末份 logs/backup_report_*.json 停在 **20261009_052740**（10-09 起跑那轮），10-10 与 10-11 **零份**；state 册仍 last_backup_status=failed / last_backup_time=2026-10-09T07:48:15，mtime 冻结 10-10 22:58:40。脚本体被 } finally { Release-Lock }(:1263-1265) 包裹，而 report 写点(:1155) 在空间闸 throw(:650) 之后 ⇒ 本轮属**早退且只留"三件全缺"**；错误文本走 backup.ps1:61-63 的 Write-Host，隐藏控制台无重定向 ⇒ **文本蒸发，无尸检面**。与 10:0x 段"挂死轮天生无阶段日志（stage_timeline 只由 STAGE 4 落盘）"同源，属可观测性设计面，本班不自拟修法、不动判据/阈值/门禁码。
- **观测面自我交代（仪器缺陷四条，本班不自修判据）**：①**atime 差分面被本班仪器污染**：backfix_lockreaders.log 的 READER-TOUCH 步进为 14/16/14/16s，与 -WatchPid 15s 采样逐拍吻合＝读锁者就是本班监视器自身 ⇒ 机制B 的 atime 信号在哨活着时不可用；哨 12:19:20 自退（MONITOR_EXIT_ON_TARGET_DEATH）后该流随即断档（末行 12:19:05，至 13:00 无新行）。②handle 哨实测节奏 **60-90s**（12:14:50/12:16:17/12:17:19/12:18:25/12:19:32/12:20:39）而非在册 20s；630 拍全 clean＝零外部持句柄者，但"抓瞬开瞬关"能力弱于设计，机制B 未被证伪只是未被抓住。③**OS 指认面全黑**：Microsoft-Windows-TaskScheduler/Operational 实测 enabled=False、Security 4689 进程退出审计零事件、WMI-Activity 12:19 窗零终止调用 ⇒ 三处皆是"若真他杀则无从指认"的结构性缺口；本班无权限也未擅改系统配置（开日志通道属系统面，候批）。④**案卷事件窗锚点错位**：patrol 的 EVT_* 行覆盖 12:20:07-12:24:46（锚 detected_at-15min），把真死时刻整段留在窗外，而候选进程窗 [death-5min, death+2min] 是对的；案卷 265 候选里的 12:20:39 系统维护簇（cleanmgr/Defrag/TiWorker/ngen/MpCmdRun/TrustedInstaller）皆属死**后**噪声，勿当死窗内证据读。
- **署名与待裁**：adjudicator=巡检自动化班（st-backfix-patrol-20261011 续岗轮）。零防线改动｜零判据/阈值/门禁码改动｜G:/backup 内容零改动（只 stat 读）｜零进程杀停｜CH 取数零次。候裁两项：①早退错误文本可见化（须动 backup.ps1 输出通道＝设计面）；②working_vault 日快照残缺 62/64 是否人工补跑。**清仓数不变**：他杀仍为案 #3-#14 十例，本案 #15 记为"自毙假案"不计他杀；两件受令清场卷（_053413 / _053503）继续不计。
- **复核命令**：Get-Content .runtime/tmp/backfix_monitor_24468.log -Tail 6（应见 12:19:04 存活与 12:19:19 判亡）；Select-String -Path .runtime/tmp/procstart_trap_ppid.log -Pattern 'pid=24468 '（应见 09:34:17 父 wscript 亡 + 12:19:17 子亡）；Get-WinEvent -FilterHashtable @{LogName='Windows PowerShell'; StartTime='2026-10-11 12:19:05'; EndTime='2026-10-11 12:19:35'} | Where-Object { $_.Message -match 'backup.ps1' }（应见 12:19:13 id=403）；Get-ScheduledTask -TaskName ZephyrAlpha-DailyBackup 的 Settings（应 PT4H / IgnoreNew）；(Get-Item G:/backup/working_vault).LastWriteTime（应 12:19:10）；ls -1 logs/backup_report_*.json 末行（应仍 20261009_052740）。

### 案 #16（45640，12:25:17-13:17:00 死，存活 ~52min）——巡检自动化班 13:3-13:4 轮【自毙族二连：HostId 同链铁证】

- **定名＝机器面假案（自毙，非他杀）**，比案 #15 多一枚硬证：legacy "Windows PowerShell" 通道里 45640 的引擎事件 400（12:25:18，None→Available，seq=13）与 403（13:16:59，Available→Stopped，seq=281316）的 **HostId=20b6fde4-d0f3-4857-9835-18b71f483bf0 与 RunspaceId=9968ca75-5421-4e00-bf99-6ab493838f6b 逐字相同**＝写 403 的引擎与 12:25:18 起机的那台是同一主机（案 #15 当时只凭时刻相邻，本轮补上主机级同一性）。外部 TerminateProcess 不给引擎写 403 的机会 ⇒ 关停自内发起。陷阱 EXIT=13:17:00（晚 403 一秒），宿主 wscript 15968 与子 conhost 54704 同秒退＝launch_hidden.vbs 的 sh.Run cmd,0,True 等子退后自然返回形态，非 job object 连坐。
- **做功正证罕见完整（本案与前案最大差异）**：12:25:19 pg_dump depgraph／12:26:54 psql 角色导出／12:26:55+12:27:36 sqlite3 .backup governance.db／12:27:37 ch_vm_ssh --sync-config／12:27:42+45 --stat-backup market/inc.zip／12:27:49 --delete-backup inc.zip／12:28:00 --cmd "rm -f /mnt/chbackup_local/*.zip.lock" --sudo／**13:05:07 --cmd "sudo -n rsync -a .../market.zip .../inc.zip /mnt/chbackup2/"→13:05:13 退（6s）**，同刻 G:/ch_backup_disk2.vhdx mtime=13:05:16 推进＝STAGE 2 CH 段真落盘。13:05:13 之后**零子进程**。监听面 cpu_d 13:13:46→13:15:46=0.1-0.3/15s，13:16:02→13:16:47 复燃 5.4/8.1/5.5/7.5 后自退——复燃 45 秒全程无子进程＝纯进程内枚举/管线做功（seq 每分钟约 91，案 #15 为 31，同族而更急）。
- **账面三件仍全缺（与 #15 同形）**：.runtime/backup.lock ABSENT（走到 finally Release-Lock）／data/databases/backup_state.json mtime 冻结 10-10 22:58:40／logs/backup_report_20261011_*.json **0 份**；G:/backup/working_vault/20261011 条目仍 62（对照 20261010 的 64）且日目录 mtime 停 10:35:38＝45640 在 STAGE 3 未向日目录写出新条目；父目录 mtime 仍=12:19:10（=案 #15 的死点，本案未再动）。
- **退出路径新判据（只读，零改动）**：Microsoft-Windows-PowerShell/Operational 实测 **enabled=True**（Analytic 仍 False）。13:16:30-13:17:30 全量 25 条逐主机看：窗内 id=4100 只属 ensure_ai_wrapper_injection 与 start_scheduler 两主机，**45640 那台主机零错误记录** ⇒ throw/terminating-error 分支未被证实；:301 的 lock-skip exit 0 结构性不可能（它已 Acquire-Lock 并跑了 52min 带工作子）；:1261 exit 2 在 STAGE 4 之后。"零错误记录＋零 report＋锁经 finally 释放"三件并置＝脚本以零错误形态离开主体，具体语句盘外不可定名（Analytic 通道关、procdump/procdump64/windbg/createdump 仍全不存在，本轮复核未变）。
- **计划任务结果码＝装饰件（新实证，呈批面）**：ZephyrAlpha-DailyBackup 现值 lastRun=12:25:17、**lastResult=0**、next=10-12 06:00。而 scripts/launch_hidden.vbs 全文只 sh.Run cmd, 0, True，**不接返回值、不 WScript.Quit(rc)** ⇒ wscript 恒退 0，backup.ps1 的退出码被宿主层吞掉。连带两条含义：RestartCount=1/RestartInterval=PT30M 的 RestartOnFailure 对本任务**永不开火**；在册三色判据（scripts/governance/scheduled_task_reconcile.py 头部"绿=result 0 或 Running+267009"）对一切经 vbs 包装的任务**恒绿**。零改动，只登记。
- **出生链三环（条①逐环实测）**：①宿主层=wscript.exe 15968 承载 scripts/launch_hidden.vbs（git ls-files 复测全仓仍仅此一支 .vbs；对**当案这条链**grep terminate|kill|taskkill|win32_process 零命中）；②任务层 ppid=2564=svchost（计划任务服务宿主），但 TaskScheduler/Operational enabled=False（#15 已记的结构性缺口）⇒ **12:25:17 的触发原因未定名**：今日 wscript→backup.ps1 出生仅两次（05:34:14 受令手触、12:25:17 本案），进程面零 Start-ScheduledTask、零 schtasks /run 指向本任务（今日 /run 仅他班的 QMTWatchdog 一条），故非命令行通道，剩 COM API/陷阱盲区两候选，本班不拍；③powershell/python 层＝原行凶面，死窗 [13:12-13:19] 出生链**零 kill 原语**（只有 5min 守卫族、belt_watchdog、外部 pm2 对 RSSHub 的探测件，全为已知无胄面）。①③两层同刻且非本班仪器本应标候捕点，但 403 的主机同一性把"他杀"反证掉⇒本案落"自毙假案"不落候捕。
- **机制A/B 无面**：data/runtime/reaper_kill.log 今日 12:00 后**零行**（末行 05:48:32，owner=test 的自造 sleeper）；tmp/scheduler_guard.log 从 12:21:52 到 13:36:52 每格都是 "Guard already running (PID=34820, heartbeat fresh), exit"，takeover 杀面最近开火仍停在 10-10 01:17:54。
- **VM 环境事件（时间相邻、非因）**：System 日志 Hyper-V-VmSwitch 12:22:07 NIC Delete→12:24:44-46 NIC Create+driver loaded（ZephyrCH-Net），12:25:14 一支 ch_vm_ssh.py --cmd "clickhouse-client --query 'SELECT 1'" 探活，12:25:17 备份点火＝zephyr-ch 在 12:22-12:24 被他班压缩工序停/起过（其 journal 自记 data.vhdx 于 12:24 压完），备份在 VM 复活后 31 秒点火；12:50-13:30 区间 Hyper-V/VMMS/vmcompute **零事件**⇒与 13:16:59 那次退出无同时刻面。
- **本班仪器污染如实报（机制B 的 atime 信号仍不可用）**：.runtime/tmp/backfix_lockreaders.log 末三条 READER-TOUCH=13:16:18/13:16:34/13:16:48，步进 14-16s，与 -WatchPid 45640 监听（13:13:45 起岗、13:17:03 随目标自退）15s 采样逐拍吻合＝**读锁者就是本班监听自身**，不得读成"主使杀前读取"；监听自退后该流断档。handle 哨 46444 实测节奏 60-90s（poll#690=13:21:55、poll#720=13:44:03），720 拍全 clean＝零外部持句柄者。
- **在岗仪器体检（13:4x 实测）**：standing trap 57376（procstart_trap_standing.log 13:44:13 仍在写）／PPID 陷阱 43560／event-watch 57184／atime 差分 57008／handle 哨 46444／诱饵 v1 17224＋v2 23588 及各自监听 49396/53928——**全 ALIVE，零重启**。锁空闲、无活体，故未新挂 -WatchPid；ticker 与 dense_window 按设计自终止不复活；reader-namer 未复活（在册 SIGSEGV）。**非本班在册 backfix 件两支（只报不动）**：backfix_three_face.ps1 pid=37480（11:0x Owner 令，盯已亡的 24468，15:00 自退）；backfix_compress2.ps1 pid=38464（Owner 13:3x 压缩令，journal 首行 13:37:20 "WAIT live=[48628]"——48628 本班 13:45 复查已不存在；其 LiveBodies 谓词只按 cmdline 含 backup.ps1 匹配、无 name 过滤，会把"读备份脚本的诊断短命进程"算成活体备份，后果=它继续等窗；属他人件，本班不代修）。
- **影子面＝同机唯一完成回写的链**：ZephyrAlpha-BackupShadow 13:30:01 触发、lastResult=0，logs/backup_shadow_report_20261011_133002.json 落盘 15,017 字节＋data/databases/backup_state_shadow.json mtime 13:30:02＝报告与 state 回写齐。生产链两轮（24468/45640）俱自毙于 STAGE 4 前而影子链完整——差面在脚本主体，不在机器。
- **本班一处自犯当场记档**：首笔 CAS 被拒=StaleWriteRefused——我把 content_sha256 的入参传成路径字符串（该函数签名收**文本**，docstring 明写"调用方读文件后计算"），于是 expected_base 是路径的哈希、与磁盘文本哈希必然不符。磁盘此刻未被任何人推进（mtime 仍 13:03:56，两次取样哈希相同），所以闸报的"磁盘已被他人推进"这句措辞在**误用形态下会说谎**：它把"我自己基线取错"翻译成了"他人并发写"。读盘复核后改正入参即写成本段。纪律含义留此：CAS 拒写后第一步是核磁盘有没有动，不是先怀疑他人。
- **清仓与署名**：他杀仍=案 #3-#14 十例；案 #15（24468）与案 #16（45640）俱记**自毙假案**不计他杀；两件受令清场卷（_053413/_053503）继续不计。adjudicator=巡检自动化班（st-backfix-patrol-20261011 续岗轮）。零防线改动｜零判据/阈值/门禁码改动｜零他人件改动｜G:/backup 只 stat 读零写｜零进程杀停｜CH 取数零次。候裁三项（本班不自决）：①vbs 吞退出码＋"result 0 恒绿"三色判据是否修（触 backup.ps1 宿主链与 scheduled_task_reconcile 判据面）：②生产链"零错误记录而离体＋STAGE 4 前天生无阶段日志"的可观测性修法（与 10:0x 段同源病，两轮已实证）；③working_vault/20261011 残缺 62/64 是否人工补跑（#15 未决项续挂）。
- **复核命令**：`Get-WinEvent -FilterHashtable @{LogName='Windows PowerShell'; StartTime=(Get-Date '2026-10-11 12:18:00'); EndTime=(Get-Date '2026-10-11 13:18:00')} | Where-Object { ($_.Id -eq 400 -or $_.Id -eq 403) -and $_.Message -match 'backup\.ps1 -Mode' }`（应三行：12:19:13 id=403／12:25:18 id=400／13:16:59 id=403，后两行 HostId 同为 20b6fde4-d0f3-4857-9835-18b71f483bf0）；`Select-String -Path .runtime/tmp/procstart_trap_ppid.log -Pattern 'pid=45640 '`（应见 12:25:21 START ppid=15968 与 13:17:00 EXIT）；`Get-ScheduledTask -TaskName ZephyrAlpha-DailyBackup | Get-ScheduledTaskInfo`（应 lastRun=12:25:17 lastResult=0）；`python -c "import glob;print(len(glob.glob('logs/backup_report_20261011_*.json')))"`（应 0）；`Get-Content .runtime/tmp/backfix_lockreaders.log -Tail 3`（末条应 13:16:48＝本班监听自读）。
### 全面接班轮·影子点火源显形＋尸检面其实一直存在＋backup.ps1 静默早退治本落地（st-backfix3-20261011 14:0x-14:3x）

- **两处前提被实测推翻（先入账再干活，本班未据令卡原文行动）**：令卡写于 13:3x-13:4x，本班 14:02:42 实测。①"round-2 有自主等待器在候隙，只监护不重跑"——等待器 38464 早在 **13:45:21 已判 GAP_CONFIRMED 并开跑**：13:45:25 guest fstrim（/dev/sdc 656.4 GiB trimmed）→13:45:28 Stop-VM graceful→13:45:50 `STOP_RESULT state=Off`＋`STEP Optimize-VHD Full` 在飞（vhdx mtime 14:07:02 仍在推进，G 余 1964.2GB 未动＝尚未回收）。②"三面哨至 15:00"在岗属实，但它钉的 24468 已亡，读数面自 12:33 起恒为 alive=False（11:03/11:33/12:03 三拍有效，其后四拍空转）。
- **T0 仪器接管盘点（14:03-14:05 单发，判据＝日志 mtime 而非 PID 存在）**：standing 陷阱 57376／PPID 陷阱 43560／event-watch 57184／atime 差分 57008（python 命名，keep 行 336 在册）／handle 哨 46444（keep 行 338）／诱饵 v1 17224＋v2 23588＋各自监听 49396/53928／三面哨 37480／压缩 round-2 38464——**11 件全 ALIVE，零战损**；三陷阱日志 mtime=14:03:50/50/51（200793/172028/575070 行）＝在写非仅活着。本班新挂第 12 件：`backfix_forensic_monitor_v2.ps1 -WatchPid 27300` pid=23048（14:13:42 起岗，见下"活体"）。唯一战损＝**landing watcher 已退岗**（`.runtime\tmp\backfix_landing_journal.csv` 末行 `# WATCHER_END rounds=935 at 2026-10-11 10:00:56`＝按 4h 自终止设计退场，非被杀；`head/lease` 两列仍恒 QUERY_FAIL，复挂须连带修那两处），复挂列 T4 件。查它是否在岗时踩到在册"关键词自匹配"陷阱：以 `CommandLine -like '*backfix_landing_watcher*'` 过滤会命中**发起该查询的 powershell 自身**（首报 pid=38660，20 秒后按 pid 复查已 gone＝即探针本身），故"进程面零命中"是排除自匹配后的结论。keep 面自证：reaper psutil 扫面按 name 含 "python" 过滤（在册 03:1x 结论），故 python 命名件只有 57008 一个，其 keep 行在册；其余 powershell 仪器结构性不入面，无需 keep 行（≠ 可删，红线"keep 行不退"照守）。
- **⚠ 新局一·影子点火源显形（本战役此前从未命名的第二类点火者）**：13:48:26 新备份实例 **pid=27300** 出生并 13:48:27 写入生产锁，它执行的脚本是 `D:\ZephyrAlpha\.runtime\commit_queue\worktree\scripts\backup\backup.ps1`——**队列车道里的副本，不是主链脚本**。陷阱册全史计数（10-10 11:16 起捕 167838 事件）：backup.ps1 点火 MAIN 11 次／`.runtime\commit_queue` 影子根 9 次／`.worktrees\<lane>` 1 次／`.aidrafts\<sid>` 1 次；**今日 10 次点火里 8 次来自影子根**（00:41、01:10 aidrafts、01:15、01:52、04:57 w1、05:41、06:43 w1、13:48），任务链（wscript→launch_hidden.vbs→主链）只有 05:34 与 12:25 两次。机理＝`backup.ps1:34` 把 `$ProjectRoot` **硬编码 D:\ZephyrAlpha**（:45 `$LockFile`、:46 `$StateFile`、:44 `$LogFile` 全由此派生），而点火者是 post-commit reconciler——它按自身所在根去解析脚本路径，于是**同一条生产锁、同一份生产 logs、同一个 `G:\backup\working_vault\<日>` 目录，被 N 份不同 commit 版本的脚本字节轮流占用**。这同时给前班三处悬案提供了身份：①"其余重试源每 15-30 分钟撞一次锁并留痕"（今日 `backup_skipped_20261011_*.json` **30 份**，末份 11:09:53）＝reconciler 点火链；②handle64 在 24468 身上看到的 `working_vault\20260926\.worktrees\st-p6-t1top\...` 陈旧镜像句柄＝镜像源侧本来就是车道根；③`workspace_changes=700` 那类车道漂移与备份互相喂垃圾。后果定性（未擅动）：影子副本的脚本版本＝该车道检出点，与主链可不同⇒"备份链"其实一直是**多版本并跑**，此前所有按"主链脚本"做的行级推断（含 :650 空间闸、:1155 报告写点）都要按"当轮实际字节"打折读。
- **⚠ 新局二·尸检面一直存在（对前班 12:3-13:0 段一处更正，范围限定）**：该段结论"错误文本走 backup.ps1:61-63 的 Write-Host，隐藏控制台无重定向⇒文本蒸发，无尸检面"——**只对任务链（wscript→vbs→powershell）成立**。reconciler 点火链用 Start-Process 重定向了 stdout/stderr，落点是 `logs\backup_reconciler_ignite_<UTCyyyymmdd_hhmmss>.log` 与同名 `.err.log`（影子点火则落在**影子根的 logs 目录**：`.runtime\commit_queue\worktree\logs\`、`.runtime\commit_queue\worktrees\w1\logs\`，故此前"查无"是没找对根）。10-10 那九桩的 stdout/err **俱在**，且每份 `.err.log` 的 mtime 与该案死亡时刻相差 ≤3 秒（_122203→20:52:30 vs 案 #13 死 20:52:33；_150537→23:38:24 vs 案 #14 死 23:38:25）。活体互证：27300 的 ignite 末行 `[BACKUP] Diff source vs snapshot: G:\backup\working_vault\20261011`（13:49:30 冻结），与 handle64 抓到的目录句柄 `BC4: File G:\backup\working_vault\20261011\src\zephyr\compliance` 同腿。**但"mtime＝死亡时刻"不可读成"死在那一行"**：stdout 是宿主缓冲的，硬杀会吞掉未 flush 行，九案 stdout 末行同为 `[OK] Snapshot: ...` 只说明那是最后一段有输出的腿——这正是本班补逐行落盘 journal 的理由，也说明前班据此排过的"死点"一律按未定名处理。
- **新病灶（真缺陷，非杀手）＋爆炸半径实测**：主链 `backup.ps1` 里 `Test-CapacityGuardBreach` **定义在 :963 而首次调用在 :825**（另两处调用 :1025/:1103 在定义之后，所以一直好的正是那两处），即 STAGE 3 的 DB-dumps 前置闸**每轮必报 CommandNotFoundException**。判别实验（合成件 `.runtime\tmp\bf3_probe3.ps1`，EAP=Continue＋未定义名置于 if 条件，实测）：该错误**非终止性**（脚本继续跑到 EOF、exit 7 照退），但**整个 if/else 语句被跳过**（两分支皆零执行）⇒ 不是"提前退出"，而是 **dumps 拷贝腿静默空转**。落地面证据同向：`G:\backup\db_dumps\20261008`=4 文件、`20261009`=4 文件、**`20261010`=0 文件（目录已建）、`20261011`=0 文件**——PG/SQLite dump 已两天没落到备份盘，而 `New-Item` 仍建目录故"看着在跑"。引入时刻＝commit `48bcbd2faa`（**2026-10-09 06:10**，`git log -L 825,825` 实测），而末份成功报告＝`logs\backup_report_20261009_052740`（10-09 05:27 起跑）——**时间线咬合：该提交之后零份报告**（10-10/10-11 实测各 0 份）。诚实边界：顺序缺陷解释的是"账面为什么两天不动"，**不解释进程为什么死**；两者是两条独立的账，本班不把它冒充为破案。
- **T1 落地（同袋两改，各自可独立回退）**：①**可观测性**——新增 `$script:JournalFile`（`logs\backup_runlog_<RunStamp>.log`）与 `Write-Journal`，`Write-Stage/Write-OK/Write-Warn/Write-Err` 四个出口全部并挂逐行落盘（`Add-Content` 每次开-写-关＝杀不掉已写行）；`RUN_START` 行带 `$MyInvocation.MyCommand.Path`（**影子/主链自证，新局一的常态化捕手**）、`LOCK_HELD/LOCK_ACQUIRED/EXIT_2/RELEASE_LOCK` 四个边界显式记账；另加 `Start-Transcript`（携不过 Write-* 的原生错误记录与栈，正是 :825 那类），`Stop-Transcript` 置于 `finally`，两处都 try 包裹＝日志面失能永不阻塞备份。**红绿双证**（`.runtime\tmp\bf3_t1_redgreen.py`，同一杀法 `taskkill /F`＝TerminateProcess，跑满 7 秒后杀）：旧形态（内存累加、末尾才写）**盘上 0 行且文件不存在**；新形态 **5 行在盘、末行 `14:22:26 | STAGE | leg_4`**＝死时所在腿直接可读。判别力为真，非恒绿。②**缺陷修复**＝把容量守卫块（含 E-4 契约注释，51 行）**原样位移**到首次调用之前（现 :335/:352，调用 :917），字节级零语义改动。**双证**：red control 同一 harness 里未定义名的 if/else 分支实测 `branch=`（空）＝复刻改前空转；green＝改后对三个真实目标 `G:\backup\db_dumps\20261011 / F:\code_backup / G:\backup\working_vault\20261011` 全 `breach=False`，且红线逐字读自配置册 `D=50/F=700/G=500`（实测余量 D 87.0 / F 1479.2 / G 1964.2 GB）⇒ **恢复守卫不拦任何目标，唯一效果＝两天没执行的 dumps 拷贝腿回来**。
- **改动纪律自证**：`PSParser::Tokenize` 与 `Language.Parser::ParseFile` 各 **0 错**；非 ASCII 字节 **0**（改前改后同值，红线".ps1 纯 ASCII 写完即查"由 `.runtime\tmp\bf3_verify.ps1` 机检）；行尾保持全 LF（CRLF=0）；退出码/stage 序/阈值/判据/门禁零改动。结构自证：`Write-Journal` 定义 :69 < 四个 Write-* :78-87 < 激活 :96-103 < `# -- Acquire lock --` :372 < 首次守卫调用 :917。影子三要素＝**影子位** `.runtime\tmp\bf3_rollback\backup.ps1.HEAD_151b4bd9ec`（75,715 字节，sha256 `102049f78c8a16fd…8755317`）／**回退判据**见下"回退令"／**变更留痕**＝本段＋改后面值 sha256 `240201cb6cae38ea…318bd4a0`（78,797 字节）。新日志文件命名 `*.log` 落 logs/ 顶层，被在册 `retire_tmp_artifacts.collect_logs_stale`（logs 顶层 *.log，默认 14 天 TTL）自动覆盖＝**零新增清洁债**。
- **压缩 round-2 与备份撞窗（只记录，两方皆不动）**：13:45:50 停 VM→13:48:26 影子点火⇒该轮 ignite 日志明写 `[WARN] CH config sync failed: …TimeoutError: timed out` ＋ `[WARN] ClickHouse not reachable (http://172.24.30.100:8123/), skipping`，即**本轮 CH 腿结构性不可能成功**（VM 处于 Off），它只是带着"跳过"继续往 Stage 3 爬；同刻 G 盘既有 Optimize-VHD 的 934GB 全量重写、又有 vault 枚举，27300 的 Stage 3 因此爬得极慢（34 分钟仍在 Diff 腿，cpu_total 5.0s）。结论性一句：**当前设计里备份与停机压缩没有互斥面**——38464 的 `LiveBodies` 谓词只按 cmdline 含 `backup.ps1` 匹配、无 name 过滤（前班 13:4x 已记），它判"无活体"的窗口里 2.5 分钟后就进了点火。本班不重跑、不中止、不改它（中途打断 Optimize-VHD＝物理不可逆面，Owner 门位）。
- **本班三处自犯当场记档**：①`bash -c` 内联 PowerShell 时 `$_`/`$()` 被吞（在册坑第 N 次撞上，首两次探针报 ParserError）→ 改成一档一文件的 ASCII 探针脚本，并把"写完即查非 ASCII＋AST"固化为本班每个 .ps1 的出厂动作；②父链解析首版按"该 pid 的**最早** START 记录"回溯，被 PID 复用污染（把 belt_watchdog 的 11:01 记录当成 13:48 的父亲），**该版父链结论整批作废**、未据此下任何判断即止损，改用"出生时刻之前最近一次未 EXIT 的 START"口径（新局一的 reconciler 归因最终来自 handle64 句柄＋ignite 文件名时刻，不来自这版父链）；③`.worktrees`/`worktrees\w1` 两类影子根在计数里被正则字符类漏过一次（`..` 通配写法在 Windows 路径与 `/` 混排时不稳），改为逐 root 分类后再统计，故上文 11/9/1/1 的数是**分类后重测值**而非首版粗筛值。
- **零面声明**：CH 取数 0 次｜进程杀停 0 个（`taskkill` 只用于本班自起的合成 harness）｜`G:\backup` 内容零写（只 stat/句柄读）｜判据·阈值·门禁·注册表零改动｜备份任务定义零改动（未 Unregister、未改触发器）｜他人件零改动（38464/37480 只读其 journal）。
- **候 Owner 裁（本班不自决）**：①**点火面收敛令**——post-commit reconciler 是否应禁止从影子根点火（改锚 `$ProjectRoot` 正主／或在 reconciler 侧加"仅主检出点可点火"闸）；这是新局一的治本面，属判据设计面不自拟。②**备份与停机压缩的互斥闸**归谁（在 38464 的 LiveBodies 谓词上加 name 过滤＝他人件；在生产侧加"压缩窗内禁点火"＝触任务面）。③**working_vault/20261011 残缺与 db_dumps 两天空目录**是否人工补跑（补跑要读 G 盘内容面）。④改前的九桩旧案"死点行"是否按"stdout 缓冲可吞行"整体改判为未定名（本班倾向是，但那是改判他班结论，呈批）。
- **复核命令**：`Get-Content .runtime\backup.lock`（应见 `PID:27300 START:2026-10-11T13:48:27…`）；`"E:\tools\Handle\handle64.exe" -accepteula -nobanner -p 27300 | grep -i "working_vault"`（应见 `G:\backup\working_vault\20261011\...` 型录句柄）；`cat .runtime/commit_queue/worktree/logs/backup_reconciler_ignite_20261011_054826.log`（末行应 `Diff source vs snapshot`）；`python .runtime/tmp/bf3_probe2.py`（影子/主链点火普查，应见 MAIN 11／commit_queue 9／aidrafts 1／worktrees 1）；`ls -1 G:/backup/db_dumps/20261011 | wc -l`（应 0，对照 `20261009` 应 4）；`python .runtime/tmp/bf3_t1_redgreen.py`（应 VERDICT …TEETH=True）；`powershell -NoProfile -ExecutionPolicy Bypass -File .runtime\tmp\bf3_verify.ps1`（应 tokenizer_errors=0 parser_errors=0 且 def:352 < call:917）；`powershell -NoProfile -ExecutionPolicy Bypass -File .runtime\tmp\bf3_guard_proof.ps1`（应三行 breach=False ＋ RED_CONTROL branch= 空）；`Get-VM zephyr-ch | Select State`（应 Off）；`tail -4 .runtime/tmp/backfix_compress2_journal.log`（应止于 `STEP Optimize-VHD Full`）。
- **回退令（一句话可执行）**：整袋回退＝`git checkout HEAD~1 -- scripts/backup/backup.ps1`（或 `git revert <本 commit>`）；只回退可观测性而保留守卫修复＝删 `Write-Journal` 定义与四处并挂行＋`Start-Transcript`/`Stop-Transcript`/`RUN_START` 等 6 处新增；只回退守卫修复＝把 :321-371 那 51 行搬回 `# ==== Capacity guard` 原节位（改前基线字节在 `.runtime\tmp\bf3_rollback\backup.ps1.HEAD_151b4bd9ec`，sha256 前缀 `102049f7`）。
- **署名**：adjudicator=st-backfix3-20261011（全面接班班）。随本袋一并落地的是前班（st-backfix-patrol-20261011 续岗轮）已暂存而未提交的 **7 段**账（05:5x 两段／06:0x／10:0x／10:5x／12:3-13:0／13:3-13:4），归属按原作者如实同报，本班不据为己有；`git diff --cached --numstat HEAD` 实测该件 +78/-0 且工作区与索引零差异，故本袋是纯追加，无回退弹。

### 三件画像级读数入册（巡检自动化班 14:2-14:3 轮，总统统筹四选裁定②批准的绿轮例外）

- **裁定落地（①保持空窗）**：本班**未**给活体 27300 挂 15s 监听。实测在册两支监听 49396/53928 只盯诱饵 17224/23588，patrol 日志的 "armed on pid=27300" 仅改跟踪态、未起采样进程（`.runtime/tmp/backfix_monitor_27300.log` 不存在）。atime 干净窗保给机制 B。条件反转闸（本班逐轮量）：27300 寿命越 5h（即 18:48:26 后）或三面现停滞相（工作子消失且 G 面/工作面零推进）⇒ 下一轮立即补挂，干净窗让位垂危时间线。
- **①新点火族显形（此前台账只记 wscript→vbs→主区脚本一条）**：活体 27300 出生链实测 `START pid=27300 ppid=48908 name=powershell.exe` 且 `-File D:/ZephyrAlpha/.runtime/commit_queue/worktree/scripts/backup/backup.ps1`＝**提交队列序列化器工作树副本**，非计划任务链。旁证三件：DailyBackup 任务现值 lastRun=2026-10-11 12:25:17／next=10-12 06:00／result=0（13:48 这次不由它触发）；全机 wscript 仅 22232 一支常驻（10-10 01:16:51 起，承载 scripts/launch_hidden.vbs → start_scheduler.ps1），无新增 vbs/js；案 #15/#16（24468/45640）两支则是 `wscript → launch_hidden.vbs → 主区 scripts/backup/backup.ps1 -WindowStyle Hidden`。锁名集未分裂＝工作树侧 `.runtime/commit_queue/worktree/.runtime/backup.lock` **不存在**，副本运行仍写主仓 `.runtime/backup.lock`（内容 PID:27300 START:13:48:27 与进程面逐字一致）。
- **②"父进程已亡"在本链路是设计而非疑点**：27300 记录的 PPID=48908 现已查无此 pid（该 pid 曾于 10-11 11:01:24-11:01:29 是 belt_watchdog 实例，属 pid 复用面）。成因在册可查：`scripts/backup/backup_reconciler.py` 头 [INVARIANTS] INV-13 明写点火经"瞬时 powershell 装载器 + Start-Process -WindowStyle Hidden + 落盘重定向"，装载进程返回即退，故真备份进程的父 PID 必指向已亡装载器，以免疫 psutil 沿活 PPID 链的级联收割。**推论（判据面，呈批不自采）**：以"父已亡/孤儿形态"作主使特征在本仓无效，此判别式此后禁用；案 #15/#16 当时按"宿主早退"讨论的段落，读到这里应改按 INV-13 设计形态理解。
- **③机制 B 嫌疑面收窄：读锁者有了仓内具名身份，且它零杀原语**：`backup.lock` 的 atime 本轮实测推进六点＝14:04:42／14:04:58／14:05:02／14:05:50／14:06:02／14:07:02，其中 14:04:58=本班单发巡检、14:05:50 与 14:10:54=本班直读锁件取证，其余三点未归名；14:07:02→14:10:54 之间无固定 60s 网格（故前一轮"每分钟 :02"的猜测被本班自己的读数否证）。代码侧点名读者＝`backup_reconciler.py` 的 INV-12 点火前主动锁自查（读 `.runtime/backup.lock` 取 PID＋复用 `backup_runtime_state._is_pid_alive`，活则记 lock_skipped 不起子进程），该件 grep 机判面 `kill|terminate|taskkill|Stop-Process` **零命中**＝只判活不处决。⇒ 机制 B 的"读锁取 pid"前置已被仓内良性件满足**且排除**，主使仍须另具按 pid 直杀能力者，本轮无新嫌疑人。
- **三面读数（14:30:07 同分钟实测）**：活体面＝27300 ALIVE，生 13:48:26，已存活 41m41s，工作子面仅 conhost.exe 50928；G 面＝`G:/ch_backup_disk2.vhdx` mtime=**14:29:59**（与读数同分钟推进＝真做功正证，非停滞相）；工作面＝`data/databases/backup_state.json` mtime 冻结 10-10 22:58:40／`logs/backup_report_20261011_*.json` 仍 **0 份**／`G:/backup/working_vault/20261011` 条目仍 **62**（对照 20261010 的 64），该日目录 mtime 停 10:35:38、父目录 mtime 停 12:19:10＝27300 尚未向 working_vault 写出新条目。
- **续挂（裁定④归追凶三班 T1，非本班面）**：零成功报告＋state 冻结 22:58 的治本＝静默早退根因面。
- **清仓与署名**：他杀仍＝案 #3-#14 十例（本段零新案号，27300 在场未死）；案 #15/#16 记自毙假案、两件受令清场卷（_053413/_053503）继续不计，口径不动。adjudicator＝巡检自动化班（st-backfix-patrol-20261011 续岗轮；四选裁定 ①②③④ 逐条落地）。零监听新挂（保持空窗）｜零防线改动｜零判据/阈值/门禁码改动｜零进程杀停｜G:/backup 只 stat 读零写｜他人件零改动｜CH 取数零次。
- **复核命令**：`Select-String -Path .runtime/tmp/procstart_trap_ppid.log -Pattern 'START pid=27300 ppid'`（应见 13:48:30 行且 -File 指向 commit_queue worktree 副本）；`Get-ScheduledTask -TaskName ZephyrAlpha-DailyBackup | Get-ScheduledTaskInfo`（lastRun 应仍 12:25:17）；`ls .runtime/tmp/backfix_monitor_27300.log`（应 No such file＝空窗未被本班污染）；`python -c "import os,datetime;print(datetime.datetime.fromtimestamp(os.path.getmtime('G:/ch_backup_disk2.vhdx')))"`（应与读数时刻同分钟）。
### 接班轮第二段·T1 生产面自证（本班落地 12 分钟后就拿到本链史上第一份阶段日志）＋影子根版本分裂机检＋案卷收尾（T3/T4/T5/T6 读数）

- **T1 不是"已提交待验"，是已被生产面验过**：主链磁盘字节改于 **14:20:43**，本班袋 **14:31:07 入队**、序列化车道 **14:31:53** 把本班**尚未提交**的暂存字节物化进 `worktrees\w0`、**14:32:51** 一发点火就执行了那份 w0 副本并写出 `logs\backup_runlog_20261011_143251.log`，而 commit 本身 **14:33:10** 才落地（＝`1de1c216e6`，HEAD 侧 `grep -c Write-Journal` 实测 12 处）。运行面读磁盘面，所以"磁盘领先 HEAD 的 12 分钟"里补丁已经真跑过一发——本班不据此说"已生效"也不据此说"未生效"，只报实测。第一份阶段日志全文四行（逐字）：`RUN_START | pid=35080 mode=all force=False script=D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w0\scripts\backup\backup.ps1 root=D:\ZephyrAlpha`／`TRANSCRIPT_ON | …\backup_transcript_20261011_143251.log`／`WARN | Another backup is running (holder PID 27300 alive, lock age 0.7h). Exiting.`／`LOCK_HELD | exit 0 skip_record=…\backup_skipped_20261011_143251.json`。一次跳锁轮次从此**自带原因、自带持有者 PID、自带脚本身份**三件；同名 transcript 有完整主机头（RunAs／PSVersion 5.1.26100.6899／主机应用程序含 w0 全路径）与 `脚本结束` 尾。此前各轮早退全靠 NTFS mtime 反推，现第一发就有正文。
- **⚠ 影子根版本分裂＝机检事实（候裁①的实证升级）**：四路 `backup.ps1` 现值实测——`MAIN` 78797B sha `240201cb` mtime 14:20:43；`worktrees\w0` **与 MAIN 同字节** 78797B sha `240201cb` mtime **14:31:53**；`.runtime\commit_queue\worktree`（27300 正在执行的那份）75715B sha `102049f7` mtime 10-10 19:06:28；`worktrees\w1` 75715B sha `102049f7` mtime 今日 09:22:31。⇒ 同一物理机上**并存改前/改后两个版本的备份脚本**，且都指向同一个硬编码 `$ProjectRoot=D:\ZephyrAlpha`（同一个锁、同一份 logs、同一个 vault 日目录）。w0 的 14:31:53 恰在本班 14:31:07 入队之后、14:32:51 点火之前＝**序列化车道把本班"尚未提交"的磁盘字节物化了一份并被点火执行**——这解释了"为何 14:32 那发带补丁而 13:48 那发不带"。后果（在册改判）：任何"修好主链＝修好备份链"的推断在点火面收敛前都不成立；改后主链的第一次自然样本仍要看运气（取决于当轮 reconciler 站在哪个根）。
- **T3 案卷·atime 通道定案＝主流信号是自家 v1 监听自读（机制B 唯一像正证的读数面被证伪）**：真源=`.runtime\tmp\backfix_lockreaders.log`（2s 轮询、仅 atime 变化才出行；源注释自陈 Access-time updates are ENABLED on this volume，fsutil 2026-10-10 验）。机读计数＝**今日 2874 次** READER-TOUCH、昨日 22 次；逐小时 00=97、01..11 各 237-252、12=81、13=17、14=13；步进直方图 16s×1510／14s×1155，atime 绝对值差精确到 15.0976/15.0841/15.1190/15.0966s（抖动 0.03s＝定时循环）。**这条 ~15.1s 密集网格止于 12:19:05**，而 24468 死亡时刻＝引擎 403 于 12:19:13／陷阱 EXIT 于 12:19:17——监听在 12:19:05 读完那一拍，下一拍（~12:19:20）见目标已亡即 `MONITOR_EXIT_ON_TARGET_DEATH` 自退，时刻咬合。出生链同咬合：00:23:31 pid=47956 `-WatchPid 24968`（网格首行 00:23:01，30s 内）→05:35:30 pid=25120 与 05:48:28 pid=54260 `-WatchPid 24468`（54260＝前班已记的双写手）。**关键分辨力**＝这三件跑的是 tracked 的 **v1**（`scripts\backup\backup_forensic_monitor.ps1`），其周期行逐字打 `lock=[PID:24468 START:2026-10-11T05:34:39.8269427+08:00]`＝**真读**；本班 14:13:42 新挂的是 **v2**，同位打 `lock=[LOCK_READ_SKIPPED(reader-audit)]`＝不读，13:48 后该流确实只剩零星读数＝**通道在 v2 形态下干净**。唯一长断档 00:35:36→00:48:44（788s）另有其因＝采样器自身 57412 于 00:35:42 被 `runtime_dir_orphan` 处决、57008 于 00:47-00:48 重生（前班"校正②"在册），与读者无关。**13:48 后 14 次逐条**：13:48:28＝27300 取锁（锁内容 START:13:48:27.1671700 同秒）／14:04:42＝本班探针 `cat`／14:04:58 与 14:05:02＝v1 `-Patrol` 一轮两读（`backfix_patrol.log` 逐行对上；patrol 腿读锁未随 WatchPid 腿一起改）／14:05:50、14:10:54＝**巡检自动化同轮自述的直读锁件取证**（其 lastRunAt=14:04:46、duration=395s ⇒ 轮次覆盖 14:04:46-14:11:2x，与本班 `bf3_probe1.ps1`（14:04:42/14:06:02/14:07:02 三点，其中 **14:07:02 两班同窗、归因存疑**）并存——两班各自独立读数互撞，本班不夺他班之功亦不静默覆盖）／14:32:53＝w0 点火 35080 读锁后跳锁（skip json 14:32:52＋runlog 14:32:52 三源同刻）／14:35:03＝patrol（14:35:01 行）／**14:36:25、14:38:05、14:38:23、14:39:45 共 4 次未归因**——同窗本班动作只有 `handle64 -p 27300`（14:37:59/14:39）与探针；若 handle64 真开该文件应与哨同频成网格，实测不成，故不硬配。**判据后果（含本班自纠）**：①前班把 13:14-13:16 那 9 次归给"自家监听自读"方向正确，但把"落在已知网格之外＝主使读"当可用判据**不成立**——那条"已知网格"本身就是 v1 监听造的，2874 次里绝大多数是观测者自己；②12:19 之前若真有读者会被自家网格淹没而不可分辨，故旧案的 atime **从来没有判别力**，不是"抓到了"而是"根本没在测"；③机制B 仍未证实未证伪，但其正证面从 atime 迁移到零，本班据此把它降级为"待新通道再判"。附带反证（可复用校准）：14:45:35 实测 `os.stat` 读到的 atime 仍＝14:39:44 ⇒ **stat 不推 atime**，"采样器自污染"假说被反证，14:39:45 后 6 分钟无行是真的没有读者。定标正解两条：给 `.runtime\backup.lock` 挂 SACL＋开 4663/4656 对象访问审计（OS 直接留痕谁读谁写）＝**系统配置面，本班无权限亦未擅动，列 Owner 菜单**；另一条已生效＝本班新加 runlog（每次取锁/跳锁记 PID 与脚本路径，14:32:51 那发已实证可用）。
- **T4 仪器三修·逐件实付**：①**handle 哨**——实测单拍＝20s sleep＋`handle64 backup.lock` 扫描 **46-51s**（14:03:24→14:04:10、14:04:31→14:05:22 两拍配对实测）＝真实节奏 ~70s，"20s 周期"在该检测面上物理不可达；本班不动 sleep（改了也只是空转），改的是**静默死不得伪装成干净间隔**：心跳从每 30 拍降为每 10 拍（35min→~12min 可见性），旧哨 46444 按自有仪器拆除、新哨 pid=**33880** 在岗（keep 行 `backfix_handle_poll` 未退）；前班把 handle 哨 26100 之死归给 job object，12:3-13:0 段已自纠为"未定名"，本班补一条形态防线：30 拍心跳正是那类静默没法被发现的形状。②**案卷事件窗锚**——`Dump-EventWindow` 原以 `(Get-Date)` 为锚（`StartTime = now-15min`，无 EndTime），patrol 延后 30min 读数时窗会整体滑到死亡之后（案 #15 实测 EVT 覆盖 12:20:07-12:24:46 而真死 12:19:17）；本班给两份副本同批加 `[object]$Anchor`（缺省 `$null`＝旧行为逐字不变，传入即窗为 `[death-15min, death+2min]`，并把锚写进 "none within" 行成 `anchored=death[hh:mm:ss..hh:mm:ss]`），调用点 `Invoke-DeathForensics` 两处改传 `-Anchor $DeathTime`＝**纯增证据面，零删事件、零阈值动**；受改件＝`scripts\backup\backup_forensic_monitor.ps1`（tracked，已 claim，基线存 `.runtime\tmp\bf3_rollback\`）＋`.runtime\tmp\backfix_forensic_monitor_v2.ps1`（在跑副本，CRLF 保持）。自证：两文件 Tokenize/ParseFile 各 0 错、非 ASCII 0、行尾各自原样（tracked LF／v2 CRLF 236 对）。③**landing watcher 复挂**——新 pid=**38568**（14:36 起岗，journal 恢复写入：`14:36:15,drain-active,,27444,140,266`），且复挂后 `head_qid` 列不再恒 QUERY_FAIL（现值空串而非失败字面），worker/RSS 面照常；在册残余（head/lease 两列在 PS5.1 子进程取数仍不稳）按前班原记，本班未动其判据。
- **T5 返回码 2147946720 定名＋前班一处十六进制更正**：`hex(2147946720)=0x800710E0`，低 16 位＝**4320**；`FormatMessageW(4320)` 权威文本＝**"操作员或系统管理员拒绝了请求"**（本机消息表实测 17 字）。**前班 06:0x 段把它记作 `0x800700E0` 是十进制转十六进制算错**（0x800700E0 的低 16 位是 224，系统文本为"拒绝访问。在此位置打开文件之前，必须先将网站添加到受信任的站点列表中…"，与本场景无关）——该错在本台账内已随读数引用扩散一次，本班在此单点更正，原段不删。语义真源**不在本班新造表**：本仓四处案卷早已把这枚码定性为**"僵尸码"＝上一实例仍占位而 `MultipleInstances=IgnoreNew` 拒掉后续触发**——`docs\_working\chain_circulation_campaign\ec3_water_health_ledger.md:42`（挂死实例占位→IgnoreNew 拒后续射→LastResult=0x800710E0）、`docs\_working\fullconnect_campaign\h_sched_recovery\07_f76_windows_schedtasks.md:29,42`、`docs\_working\fullflow_mining\m5_scheduling\04_silent_failure_modes.md:45`（S10 族）与 `05_master_health_table.md:22`。**对本役的直接含义（正向用途）**：这枚码不是"任务定义坏了"，而是**"被拒那一刻确实有一个实例活着"的机读证人**——所以 06:00:01 的 2147946720 反过来印证 05:34 那次点火的实例当时仍在跑，与"24468 存活至 12:19"三条独立读数（进程面/任务面/锁面）互相咬合，无需新增假设。
- **T6 压缩 round-2 监护读数（只读，未重跑未中止）**：14:40 实测 38464 仍 `alive=True`，journal 末行仍是 13:45:50 的 `STEP Optimize-VHD Full`（cmdlet 阻塞期无输出＝正常形态，非停摆）；VM `zephyr-ch=Off`、`G:\ch_backup_disk2.vhdx` 934.4GB mtime **14:39:44 仍在推进**、G 余 **1964.2GB 未变**（Full 压缩先写临时再换回，空间尚未回收）。已跑 **54 分钟**——对照 round-1 的 D 盘件"Optimize 2.3 分钟"是**不同体积不同尺度**，本班不据 2.3 分钟推本轮 ETA。ALARM 同名件今日未生成。令卡"21:00 无隙自退"只约束**等待期**，执行期已开跑则不受该时刻约束，其后行为未在册，本班不预判亦不干预。**撞窗事实**续记：13:45:50 停 VM → 2.5 分钟后 13:48:26 影子点火 ⇒ 该轮 CH 腿结构性不可成功（其 ignite 日志逐字：`[WARN] CH config sync failed: …TimeoutError: timed out`＋`[WARN] ClickHouse not reachable (http://172.24.30.100:8123/), skipping`），备份与停机压缩**当前无互斥面**。
- **活体 27300 读数（改前形态的最后一个自然对照）**：14:40 实测 alive（56 分钟），`threads 12→10`、`cpu_total=6.0s`（监听末读 14:38:54 cycle=101）、`cpu_d=0`、`io_bytes_per_s=0`、子进程仅 conhost，ignite 正文自 13:49:30 冻结在 `Diff source vs snapshot`。⚠ 本班**不判挂死**：24968 一案已在册教训"低 CPU 长时长＝剪枝/枚举形态而非挂死"，且此刻 G 盘正被 934GB 全量压缩抢占 IO；判别只能靠"目录句柄落点是否换叶"，而 14:37:59 与 14:39 两次 `handle64 -p 27300` 返回空（同一命令 14:09 时正常返回 24 个 File 句柄，含 vault 目录句柄 BC4）＝**handle64 自身读数不稳**，不是"句柄消失"的证据。此点按在册铁律记为"运行态断言须同分钟双尺复测"，本班未取得第二尺前不改判、不清场、不杀。
- **新显形·本班权限外的他道缺陷（只登记不代修）**：`src\zephyr\security\access_control\session_concurrency.py:744-749` 以 `extra_death_evidence=` 调用 `write_takeover_entry`，而真源 `scripts\governance\session_takeover_ledger.py:987-993` 的形参是 `resources/death_evidence/registry_entry/now`，**无该形参** ⇒ 每次命中即 `TypeError`，被外层 `except` 降级成一行 warning（本班今日提交时实测连报 3 次：`takeover ledger write failed sid=st-backfix3-20261011: write_takeover_entry() got an unexpected keyword argument 'extra_death_evidence'`）。后果＝该件 [INVARIANTS] 自述的"立案侧 JSONL 记账"在 salvage 腿上**从未写成过**（静默降级与"未触发"同形，是在册老形态）。修法一行（改调用点形参名或让被调方接住旁证），但它属会话注册/执法桥域且触判死面观测，**非本班点名件、非本班权限**，本班只出案卷呈批，不代修。
- **双写手对账（同车道两套人在跑，本班不夺功不静默覆盖）**：巡检自动化 `9cbf6aef`（sid=st-backfix-patrol-20261011 续岗轮）仍在岗并已自行入册一段（14:2-14:3 轮"三件画像级读数"），与本班 14:0x 段同题（27300 影子出生链、父 pid 复用为设计面、三面读数）。三处必须对齐的读数差：①它写"`.runtime/tmp/backfix_monitor_27300.log` 不存在＝本班未挂监听、atime 干净窗保给机制B"——实测该件 **14:13:42 起已存在**（本班挂的 pid=23048），但它是 **v2**、周期行打 `LOCK_READ_SKIPPED(reader-audit)`＝**不读锁**，故"干净窗"的意图未被破坏，两者的分歧只在"挂没挂"而不在"读没读"；②它把 14:05:50/14:10:54 归给自己直读锁件取证，本班探针另产 14:04:42/14:06:02/14:07:02 三点——两班读数同窗互撞，本班据此把"15s 主流信号＝未知读者"的旧判据正式作废（见上条）；③它按总统统筹裁定④把"静默早退治本"归追凶三班 T1——本班已落地并已被生产面验过（见首条）。**本班未改该自动化任何字段**：其 prompt 明写"每轮以台账＋日志为真源"，所以把接管事实落进台账＝给它交底的正道，手抄改 prompt 反而是在册记录过的措辞漂移风险面（条④先例）。值守分工照旧：它管判读与续岗，本班管施工与案卷定名。
- **零面声明（本段）**：CH 取数 0｜他人进程杀停 0（仅拆自家 46444 哨并同型重启 33880）｜`G:\backup` 内容零写｜判据·阈值·门禁·注册表零改动｜备份任务定义零改动｜他道件零改动（session_concurrency 只读）。
- **候 Owner 裁（累计四件，本班不自决）**：①点火面收敛（影子根禁点 or 版本对齐）；②备份↔停机压缩互斥闸归属；③`working_vault\20261011` 62/64 残缺与 `db_dumps\20261010..11` 两天空目录是否人工补跑；④他道 `extra_death_evidence` 签名缺陷派班。
- **复核命令**：`cat logs/backup_runlog_20261011_143251.log`（应四行，RUN_START 的 script= 指向 `worktrees\w0`）；`head -12 logs/backup_transcript_20261011_143251.log`（应见 主机应用程序含 w0 全路径）；`python -c "import hashlib,glob;[print(p,hashlib.sha256(open(p,'rb').read()).hexdigest()[:8]) for p in [r'scripts/backup/backup.ps1',r'.runtime/commit_queue/worktree/scripts/backup/backup.ps1',r'.runtime/commit_queue/worktrees/w0/scripts/backup/backup.ps1',r'.runtime/commit_queue/worktrees/w1/scripts/backup/backup.ps1']]"`（应 240201cb/102049f7/240201cb/102049f7）；`python -c "print(hex(2147946720), 2147946720 & 0xFFFF)"`（应 0x800710e0 4320）；`grep -n "extra_death_evidence" src/zephyr/security/access_control/session_concurrency.py`（应 1 处:749）；`grep -n "def write_takeover_entry" -A7 scripts/governance/session_takeover_ledger.py`（应无该形参）；`powershell -NoProfile -ExecutionPolicy Bypass -File .runtime\tmp\bf3_ast.ps1 -Path D:\ZephyrAlpha\scripts\backup\backup_forensic_monitor.ps1`（应 0 错）；`Get-Content .runtime\tmp\backfix_patrol.log -Tail 4`（应见 14:35:01 PATROL 行）；`Get-VM zephyr-ch | Select State`（应 Off）。
- **署名**：adjudicator=st-backfix3-20261011（全面接班班·第二段）。本班第一袋已落地＝commit `1de1c216e6`（14:33:10，含 T1 两改＋影子点火源显形＋前班七段欠账），HEAD 侧 `git show HEAD:scripts/backup/backup.ps1 | grep -c Write-Journal` 实测 12。
### 追加件执行账（T1b restore_drill 报告契约）＋本班一处范围自犯当场认（st-backfix3-20261011 15:0x）

- **本班范围自犯（要紧，先记再干活）**：总统统筹追加件点名的是 **T1b＝`scripts\backup\restore_drill.py` 失败路径报告补 `pass`/`criteria` 两键**，本班收到后却先按自己脑补的"早退面收口"施工了一轮（改 `backup_reconciler.py` 的 settle 支路＋新测试），**那不是点名件**。处置两条：①不静默丢弃、也不冒充正件——该改动隔离成独立件并在提交信息与本段明标**"本班自加件，非点名，可单独否决"**（回退单位＝`backup_reconciler.py`＋其测试件两文件）；②正件 T1b 随后按令卡原文逐字做完（下条）。教训固化成本班下一轮起的动作：**追加令到手先复述"任务号＋被点名的文件名＋要求的键/行为"三项再动手**，防止把"我认为该做的"顶替"令上写的"。与在册 [[premise-falsified-stop-and-probe]] 同族，只是这次被证伪的是本班自己的理解。
- **T1b 正件·缺陷定性**（真源=`scripts\backup\restore_drill.py`，改前基线 sha 存 `.runtime\tmp\bf3_rollback\restore_drill.py.HEAD_d31228369d`）：`run_drill()` 的报告骨架只起 6 键（started_at/drill_db/dump/live_db/status/error），而 `pass`、`criteria` **仅在成功路径末尾由 `report.update(judge_drill(...))` 产出**；于是所有失败支（dump 缺位提前 return、try 内异常后 return）交出的都是"status=failed 但契约缺项"的报告，消费侧按 `report['pass']` 直读必 **KeyError**——即死信三期试点当场撞到的那枚。与 T1 静默早退同族同病：**写侧键集随路径变化，读侧假设恒定**。
- **T1b 改与双证**：骨架起手补 `"pass": False` 与 `"criteria": {}`（语义＝一条判据都没评估成＝不通过，绝不冒领 ok），件头 `# [ERROR_CONTRACT]` 同批留痕，净 diff=+11/-1。**零改动面实测交代**：四条件判据(c1-c4)/阈值/status 取值/退出码全不动——`main()` 的 `return 0 if report.get("pass") else 1` 由 None→False 同 falsy 同 exit 1，且 `print` 行原用 `.get` 不受影响。红证（改前直调，不连库）：`run_drill(dump_path=r'Z:\no_such_dir\absent.dump')` → keys 6 项，读 `report['pass']` 与 `report['criteria']` 各得 KeyError。绿证（改后同调用）：keys 8 项、`pass=False`、`criteria={}`、`status=failed`、`json.dumps` 可序列化。**反向钉（防本班把失败支钉成恒不判）**：直调 `judge_drill(...)`（纯函数，零 IO）返 8 键含 `pass=True` 与四子键 criteria，骨架经 update 后 `pass=True`/`status=passed`＝成功路径未被骨架覆盖。lint：`ruff check` 与 `ruff format --check` 双清；件内 :17/:53 两处 `# noqa` 无效告警经 HEAD 副本对照属**既有**，非本班引入。
- **T1b 残余不对称（不自扩，等取向）**：`judge_drill` 实产 8 键（criteria/criteria_change_note/criteria_version/failed_criteria/legacy_judge_note/pass/rows/status），本班只补了点名的两键，因此失败路径报告**仍缺** `failed_criteria`/`criteria_version`/`criteria_change_note`/`rows`/`legacy_judge_note`——消费侧若直读这些键，在失败路径仍会 KeyError（同病同型）。两取向：①骨架补满 8 键（但 `rows`/`legacy_judge_note` 在失败路径放空值还是缺省属语义取向）；②消费侧统一 `.get()`。本班已把该清单随信号交回死信三期，等其一言即同批补。
- **信号回档留痕**：已用会话通道向 `c8654014-0ee6-4aae-b41d-f70f13f17890`（【死信三期·并发清偿总令】sid=st-deadcure3-20261010）投递修复事实（缺陷定性/红绿双证/残余取向二选一/单文件回退式），通道回 `messageSent`、目标 `runtimeState=opening`——**照在册铁律记为"已受理"而非"已完成"**，其归档件 `tests\backup\test_restore_drill.py`（`restore_drill.py` 件头 `[TESTS]` 指针已就位）归他们落，本班不代建。
- **本班自加件（可单独否决）·reconciler 侧"早退显化"**：`settle_previous_ignition()` 的"无 STAGE 4 痕迹"支原为不区分 fail-closed（既不分"仍在跑"也不分"已夭折"，只保留 pending）。本班按 ps1 自身锁语义把它分开：`backup.ps1` 在 `finally` 里 Release-Lock，故"锁消失"或"锁在而持有者 PID 已死"两种形态都不可能再到 STAGE 4 → 记 `ignite_outcome=early_exit`＋`_time`/`_evidence`(`lock_absent`|`holder_dead:<pid>`)/`_ignite_log` 四键；持有者仍活 → 原样 pending。纪律面：返回值/pending 指针/点火与重试路径**零改动**，存活与锁解析复用本件既有单口 `_is_pid_alive`＋`read_backup_lock_holder_pid`，**零新增阈值**；同一 ignite_log 幂等一次（防每次事件改写热册）。红绿：新 4 支先 3 FAILED（KeyError 'ignite_outcome'）→ 改后整件 **38 passed**（原 35 支零回退）；回归面实测＝`tests/meta/scripts/backup/` 整目录 **127 passed**、`tests/data/dr/test_backup_lock_semantics.py`＋`test_backup_lock_stale.py`＋`test_backup_copy_share.py` **25 passed**，其中"活体不得显化"那支改前恒绿、专作改后回归钉。**观测落点的既有限制（不掩饰）**：`backup_config.yaml:107 trigger.state_file` 是**相对路径**，故车道点火写的就是车道根 state（实测 `.runtime\commit_queue\worktree\data\databases\backup_state.json` mtime 14:54 且内含 `last_ignite_session_id=st-mineloop-20261010` 的陈旧残留），而该文件按本件自己的 docstring 属"无任何下游消费者"——这与既有 `lock_skipped` 观测同源同限制，非本班新增缺陷。正解候选＝`zephyr.shared.io.paths.strip_session_worktree` 目前只剥 `.aidrafts`/`.worktrees`，对 `.runtime\commit_queue\...` 不生效（其 :109 自陈同类病曾发生于 .worktrees）；扩它属 paths SSoT 面，本班不动，列为候裁。
- **生产链读数（15:05:52 实测，本班不自加件的成果冒领）**：`logs\backup_report_20261011_*.json`＝**0 份＝"10-09 后清零"这条尚未被 T1 打破**；带阶段日志的点火已 **3 发**（14:32:51 自 `worktrees\w0`、14:54:13 与 15:02:46 自 `.runtime\commit_queue\worktree`），**三发全是跳锁轮**（每份 runlog 末行均 `LOCK_HELD | exit 0 skip_record=...`，持有者一律 PID:27300）——即"完整轮＋阶段日志"的样本仍未出现，堵点是唯一在飞轮 **27300＝13:48:26 出生的改前副本**（早于本班 14:20:43 的磁盘改动），它自己不产 runlog，而它 77 分钟不放锁；wt_root 副本已被序列化车道刷成改后字节（15:02 那发即证据）⇒ **27300 一释放，下一发就带完整阶段日志**，无需人工点火。**假打破防线（给下一班的一条硬提示）**：今日 `logs` 里确有 1 份 `backup_shadow_report_20261011_133002.json`，那是 **ZephyrAlpha-BackupShadow 影子链**（13:30 触发，链路本身完整）的产物，**不得读成生产链破零**；判据只认 `backup_report_` 前缀。另记一条点火节奏新读数：14:32→14:54→15:02 间隔已从 ~20min 收紧到 ~8min，锁被长期占用时 reconciler 的撞锁重试在加密（每撞一次产一份 skip json＋一份 runlog，二者均由在册 14 天 TTL 覆盖）。
- **两件仍不动的现场（照 T6/红线）**：压缩 round-2 自 13:45:50 起 `Optimize-VHD Full` 已 80 分钟，journal 无新行（cmdlet 阻塞期无输出＝形态正常）、VM 仍 Off、G 余未回收——不重跑、不中止、不改其谓词；活体 27300 CPU 由 6.0→7.0s 缓涨、`cpu_d=0`、子进程仅 conhost、ignite 正文自 13:49:30 冻结在 `Diff source vs snapshot`，**本班不判挂死**（低 CPU 长时长＝枚举形态在册教训；且 handle64 该窗读数不稳未取第二尺），不清场不杀；若 Owner 给处置权，按五因子闸先证据后动作。
- **零面声明（本段）**：CH 取数 0｜他人进程杀停 0｜`G:\backup` 内容零写｜判据·阈值·门禁·注册表零改动（T1b 只补键；自加件只写观测键）｜备份任务定义零改动｜他道件零改动｜他会话归档件未代建。
- **候 Owner 裁（累计六件）**：前四件照旧（点火面收敛／压缩互斥闸／两天空 dump＋残缺快照补跑／`extra_death_evidence` 他道缺陷派班）；新增⑤**本班自加件留或删**（一句"删自加件"即回退两文件）；⑥**观测面主仓锚定**是否扩 `paths.strip_session_worktree` 认 `.runtime\commit_queue` 根（属 paths SSoT，影响所有观测写入不止本件）。
- **复核命令**：`python -c "import importlib.util;s=importlib.util.spec_from_file_location('rd',r'scripts/backup/restore_drill.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.run_drill(dump_path=r'Z:\no\absent.dump');print(sorted(r),r['pass'],r['criteria'],r['status'])"`（绿＝8 键 False {} failed）；`PYTHONPATH=src python -m pytest tests/meta/scripts/backup/test_backup_reconciler.py -q`（应 38 passed）；`python -m ruff format --check scripts/backup/restore_drill.py scripts/backup/backup_reconciler.py`（应 already formatted）；`cat logs/backup_runlog_20261011_150246.log`（末行应 LOCK_HELD＋skip json 路径）；`ls -1 logs/backup_report_20261011_*.json | wc -l`（应 0＝未破零）；`ls -1 logs/backup_shadow_report_20261011_*.json`（应 1 份，属影子链非生产）；`cat .runtime/backup.lock`（应仍 PID:27300）。
- **回退令（逐件可执行）**：T1b＝`git checkout HEAD~1 -- scripts/backup/restore_drill.py`；自加件＝`git checkout HEAD~1 -- scripts/backup/backup_reconciler.py tests/meta/scripts/backup/test_backup_reconciler.py`（基线在 `.runtime\tmp\bf3_rollback\backup_reconciler.py.HEAD_aafb398927`）。
- **署名**：adjudicator=st-backfix3-20261011（全面接班班·第三段；T1b 正件＋自加件分离呈批）。
### T1c·T1d 收口段（报告契约补满 8 键＝T1c；测试自包含化实测"造得出"＝T1d）＋一处 Edit 自犯当场认（st-backfix3-20261011 15:4x-16:0x）

- **令先复述再动手（把上轮范围自犯换成的规矩真跑一遍）**：T1c＝点名件 `scripts\backup\restore_drill.py`，行为＝失败路径骨架补满 `judge_drill` 全 8 键，语义四条照死信三期裁定；T1d＝造小号合成 `depgraph.dump` 使 `test_restore_drill.py` 脱离"机器上必须有真 dump"；时点＝现在就开工，"压缩收口前不开新轮"只约束候裁⑥那类治理轮。本班据此施工，未碰 VM/压缩面/27300。
- **T1c·缺陷定量的再测（比 T1b 时更准）**：契约键集＝`judge_drill` 实产的 8 键（criteria/criteria_change_note/criteria_version/failed_criteria/legacy_judge_note/pass/rows/status）。**T1b 之后失败骨架只有其中 3 键**（pass/criteria/status），仍缺 5 键＝criteria_change_note/criteria_version/failed_criteria/legacy_judge_note/rows，且**逐键实测都是 KeyError**（红证见下）。故 T1b 只堵住了死信三期撞到的那一枚，其余四枚同型同病——本班上一段把"残余不对称"如实交回是正确动作，本轮按裁定收口。
- **T1c·改与四条语义（diff＝+17/-7，全在骨架与件头 [ERROR_CONTRACT]）**：`failed_criteria=[]`（一条判据都没评估成＝不指认任何一条为红，不是"全过"）／`rows=0`（0＝不可得，非"零行"）／`criteria_version`＋`criteria_change_note` 沿用成功路径同值（尺的版本与说明与轮次无关，缺它读侧无法判"这具报告出自哪把尺"；实测值 `P-3R2`，note 长 356）／`legacy_judge_note=""`（旧尺说明只在真做过裁决时才有意义）。零改动面照旧实测交代：四条件判据/阈值/status 取值/退出码不动，`main()` 的 `0 if report.get("pass") else 1` 在 None→False 下同 falsy 同 exit 1。
- **T1c·红绿双证（照 T1b 先例，两支失败路径都验，均不连库）**：**支 A（dump 缺位→提前 return）**＝改前基线件 `run_drill(dump_path=不存在的 dump)` 得 keys 6 项、读 `report['pass']`/`report['criteria']` 各 KeyError（T1b 已留档），改后（T1c）同调用 8/8 键齐、`pass=False`/`criteria={}`/`failed_criteria=[]`/`rows=0`/`criteria_version='P-3R2'`/`legacy_judge_note=''`、`json.dumps` 可序列化。**支 B（try 内异常→finally 后 return，＝更真实的那支）**＝以 `run_subprocess_hidden` 替身抛 `OSError` 模拟 PG 不可达：红证跑在改前基线件（`.runtime\tmp\bf3_rollback\rd_preT1c.py`）＝**contract keys 仅 3/8，逐行 KeyError 实证五枚**；绿证跑在改后件＝**8/8 齐**，且 `status=failed`/`error='OSError: simulated...'`/`drill_db_dropped=False`/`drill_db_cleanup_error` 照旧留痕（清理失败不被新键掩盖）。
- **T1c·一处诚实的类型不对称（照裁定实现，不擅改，标价待判）**：成功路径 `rows` 是 dict（实测 `{"lib_assets":{"live":2,"drill":2,"match":true,...}}`），失败路径按裁定取 `rows=0`＝int。故读侧 `report['rows'][t]` 在失败报告上会得到 **TypeError 而不是 KeyError**——KeyError 一族已收口，类型一族仍在。两句修法任选（失败侧改 `rows={}` 保型／读侧先判 `status`），本班不自改：令上写的是 `rows=0`，本班严格照办并把差异入账，死信三期的归档测试可直接引本段。
- **T1c·本班 Edit 自犯当场认**：第一次补键时我把替换锚点取得太短（只锚到注释末两行＋两行代码），结果**旧的 T1b 注释块没被替换掉，与新块叠成重复 6 行**——语法仍合法、ruff 仍会过、跑起来行为不变，属于"只有重读才会发现"的那类脏改。发现方式＝改完必读物化区（不是信 Edit 成功回执），当场删旧块并复验（`报告契约` 字样全件计数 2→1）。教训：注释替换的锚点必须覆盖**整块**，短锚点在"改写既有说明文"场景下必然留残块。
- **T1d·实测结论＝造得出，且比预期更省**：两条依据都是机读事实——①`_find_latest_dump(explicit)` 的实现是 `return p if p.exists() else None`＝**只验存在性、不校验 pg_dump 归档格式**，故一个 19 字节合成件（`PGDMP\x00synthetic-fixture`）就能过前置；②全部数据库交互收在**单口** `run_subprocess_hidden`（件 :50 一处导入），替身只钉这一个名字即可覆盖 createdb/psql/pg_restore 全线。探针＝`.runtime\tmp\bf3_t1d_probe.py`，实测结果：`status=passed`、`pass=True`、四条件 c1-c4 全 True、8/8 契约键齐、`error=None`、`subprocess kinds seen=['pg_restore.exe','psql.exe']`，**零 PostgreSQL 实例、零真 dump** ⇒ `SELF_CONTAINED_FULL_PATH=True`。配方要点：按 argv 里的 SQL 片段分派回包（locale 行三列以 `\x01` 分隔、`count(*)` 回行数、`pg_tables` 回表名列表、样本查询回两列两行），`_TABLE_SPECS` 由件内常量驱动故测试无需控制表清单。
- **T1d·两条如实边界（不夸大成"演练已被替代"）**：①自包含测试证明的是**契约与裁决逻辑**，不是"这份 dump 真能恢复回来"——端到端可还原性仍只有真演练能证，月度真跑不能因此撤；②顺带显形一条生产面事实：既然 `_find_latest_dump` 不校验格式，G 盘上**0 字节/破损的 depgraph.dump 会被照样接受并进 restore**，兜住它的是 C4（`pg_restore` 返回码）而非前置检查——本班不改该判据（属判据面，且 C4 已在岗），只登记备查。**件归属照旧**：`tests\backup\test_restore_drill.py` 仍归死信三期落（T1b 裁定"件归他们落"未被 T1d 撤销），本班交的是已验通的配方与探针，使他们第一稿就能自包含；若 Owner 改派本班落件，一句令即落。
- **回归与归属（含一次把红证追到别人门外的实测）**：`tests/backup/`＋`tests/meta/scripts/backup/`＝**137 passed / 9 failed**；9 支全在 `test_stage3_vault_mtime_and_verdict.py`，其断言是静态读 `backup.ps1` STAGE 4 文本找 `last_backup_partial_items`——**实测该 token 在 HEAD 与本班 T1 前的基线件（`.runtime\tmp\bf3_rollback\backup.ps1.HEAD_151b4bd9ec`）里都=0 命中**⇒ 该红**早于本班 T1 袋**，属"测试断言一件脚本里不存在的东西"的存量红（要么特性未落、要么测试先于码写），本班不代修、如实呈报。另 `tests/meta/scripts/test_guard_invariants.py` 16 支挂在 `scripts\installers\start_scheduler.ps1` 不存在——实测该路径 **HEAD 未跟踪且 `git log` 零行＝从未入库**，实件在 `scripts\start_scheduler.ps1`（在册计划任务 ZephyrAlpha_DataScheduler 也指向该实路径）⇒ 测试期望路径写错位的存量红，同样不代修。`test_backup_reconciler.py` 38 passed 全绿。lint：`ruff check`＋`format --check` 双清（件内 :53 那处 `# noqa` 无效告警仍为既有）。
- **零面声明（本段）**：CH 取数 0｜他人进程杀停 0｜`G:\backup` 内容零写（合成 fixture 落 `.runtime\tmp\bf3_fixture\`，不进备份盘）｜判据·阈值·门禁·注册表零改动（`rows=0` 等四键语义照死信三期裁定，未自扩）｜备份任务定义零改动｜他道件零改动（两处存量红只呈报）｜`test_restore_drill.py` 未代建。
- **值守读数（15:44:50 单发）**：27300 仍持锁（1h56m，CPU 6.0→8.4s 缓涨＝在干活非死挂），报告仍 0 份，带日志的点火 4 发全为跳锁轮；**15:11 之后 33 分钟无新点火**（此前节奏 ~8-20min）＝第一份完整阶段日志仍在等 27300 放锁，本班不手动点火、不清场。压缩 round-2 `Optimize-VHD Full` 已 2 小时（935G 全量压缩属正常态，Owner 已确认），journal 无新行＝cmdlet 阻塞期形态正常，未重跑未中止。三面哨 37480 于 15:00 按设计自退（**非战损**，与 ② 的判读一致），其余 12 件仪器全在岗。
- **候 Owner 裁（累计七件）**：原六件照旧；新增⑦**失败报告 `rows` 的类型一族**（保持 `rows=0` 还是收 `rows={}`，或读侧先判 status）——本段已给两句可执行修法，等死信三期归档测试的取向或Owner 一言。
- **复核命令（两条都已本班实跑，红证变体的"直读缺失键"形式会把命令本身崩掉，故统一用计数式写法）**：`python .runtime/tmp/bf3_t1d_probe.py`（末行应 `SELF_CONTAINED_FULL_PATH = True`）；`python -c "import importlib.util,sys;sys.path.insert(0,'src');J=['criteria','criteria_change_note','criteria_version','failed_criteria','legacy_judge_note','pass','rows','status'];s=importlib.util.spec_from_file_location('rd',r'scripts/backup/restore_drill.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.run_drill(dump_path=r'Z:\no\absent.dump');print('contract',sum(1 for k in J if k in r),'/8','missing=',[k for k in J if k not in r])"`（绿＝`contract 8 /8 missing= []`；把路径换成 `.runtime/tmp/bf3_rollback/rd_preT1c.py` 即红＝`contract 3 /8 missing= ['criteria_change_note','criteria_version','failed_criteria','legacy_judge_note','rows']`）；`PYTHONPATH=src python -m pytest tests/meta/scripts/backup/test_backup_reconciler.py -q`（38 passed）；`python -m ruff format --check scripts/backup/restore_drill.py`（already formatted）；`git show HEAD:scripts/backup/backup.ps1 | grep -c last_backup_partial_items`（应 0＝那 9 支红的归属证据，非本班 T1 引入）。
- **回退令**：T1c＝`git checkout HEAD~1 -- scripts/backup/restore_drill.py`（改前基线件另有两份留档：`restore_drill.py.preT1c_*` 与 `rd_preT1c.py`，可逐字节对照）。T1d 无仓内改动（探针与 fixture 均在 `.runtime\tmp\`，gitignore 内）。
- **署名**：adjudicator=st-backfix3-20261011（第四段：T1c 正件收口＋T1d 配方实测＋两处他道存量红只呈报）。
### 四件裁定落地段（①禁影子根点火＋②备份↔压缩互斥＋③条件性补做＋④转班）＋rows={} ＋压缩 round-2 收果对拍＋处置闸六分支验证（st-backfix3-20261011 17:1x-17:5x）

- **总统统筹四条裁定逐条落位**：①**禁影子根点火已落地**（单一检出点原则）；②**备份↔停机压缩互斥已落地**（点火侧前置查 VM）；③**补做带条件照办**（未手造任何文件，等 27300 放锁后的自然完整轮）；④**已转维护二班**（会话死亡显化形参缺陷，含复现与两种修法取向，本班未碰那两个文件）。rows 取向裁定＝`{}`，已同批改。
- **①单一检出点闸**（`is_shadow_checkout()`＋`reconcile()` 内 (1a) 位）：影子根＝**有正证者**才拦——`.git` 是 FILE（git linked worktree 硬特征，实测 `.runtime\commit_queue\worktree`、`worktrees\w0`、`worktrees\w1` 三条全是 FILE）或路径含 `.worktrees/.aidrafts/commit_queue` 标记；拦时记 `last_run_outcome=shadow_ignite_refused`＋`_reason/_root/_time`，**不碰锁、不动 cadence**；判不出形态的根按主区放行。**校准写进件头 [INVARIANTS]**：误拦＝备份静默停摆，那正是本战役在治的病，不能拿新病换旧病。真机自测：主区→`(False,'primary_or_unproven')`，车道→`(True,'linked_worktree_dotgit_file')`。
- **②互斥闸**（`ch_guest_vm_running()`＋`reconcile()` 内 (1b) 位，紧挨点火前）：VM 名取配置册新单键 `ch_backup.vm_name: "zephyr-ch"`（**不新硬编码第二处真源**）；`("OK", False)` ⇒ 记 `vm_off_yield`＋`last_yield_reason/last_vm_gate_probe` 并**不点火**；探针不可得/未配置/超时 ⇒ **fail-open 放行**且把探针状态写进 state 册备追（可用性优先于门禁完备性，此取舍已在件头留痕）。真机实测（17:4x，VM 已被压缩器起回）：配置读到 `zephyr-ch`，返回 `("OK", True)`；17:0x VM Off 期间同一函数返回 `("OK", False)`＝两态都过真 Hyper-V。
- **②的未覆盖面如实标价（残余）**：本闸装在 **reconciler 点火腿**上；`ZephyrAlpha-DailyBackup`（wscript→launch_hidden.vbs→主链）那条腿不经过 reconciler，故**若压缩跨过 06:00 仍会撞**。今日之所以没撞，是因为压缩恰在 06:00 之后才开始（13:45:50 停 VM）。补这一口需在 backup.ps1 侧或任务侧加前置，属另一面，本班不自扩。
- **rows 收 `{}`（候裁⑦已决，与死信三期语义恒定一致）**：失败骨架 `"rows": 0` → `{}`。绿证（不连库，两支失败路径）：`contract 8/8`、`rows={} type=dict`、读侧 `report['rows'][t]` 不再抛 TypeError；`status=failed`/`pass=False` 不变；`main()` 退出码不变。至此失败报告与成功报告**键集与键型两侧对齐**，KeyError 族与 TypeError 族同时收口。
- **处置闸（`.runtime/tmp/bf3_dispose_gate.py`）六分支验证＝6/7 合设计，那 1 条"FAIL"是现实变了**：P1 用生产 journal，断言"尚未收口"，而压缩在 17:30:38 真收口 ⇒ 闸返回 `BASELINE_TAKEN_NOW(wait 23min from close)`＝**正确行为、过期断言**，不改闸改断言。其余五支：P2 缓释窗未满 ⇒ 不动；P3 三面全冻 ⇒ `DISPOSE_SATISFIED` 且 evaluate 模式 `ACTION: none`（**证明它能到达处置判定，同时证明判绿不等于动手**）；P4 基线后 vault 目录变了 ⇒ `VETO_progress_visible`（安全支有牙）；P4b PROBE 行含 Traceback 字样 ⇒ 不信、判 `PROBE_UNtrusted_text`；P5/P6 动作路径端到端（靶＝本班自起 sleeper，锁＝临时文件）：P5 杀掉自己起的进程并清掉**自己那把**锁 `DISPOSED_and_lock_cleared`；P6 锁内 PID 已易主（999999）⇒ `KILLED_BUT_LOCK_BELONGS_TO_999999_not_touched`，外来锁原样保留。**防误删他人锁这一条不是纸上设计**：点火节奏 8-20 分钟一发，杀后到删锁之间确有竞态窗口（09-25 双跑同 vault 日目录事故在册）。
- **验证过程抓出闸自身两个缺陷（先修后授信）**：①`G0` 用 `l.startswith("PROBE"/"FAIL")` 匹配，而压缩器 `Log()` 给每行加 `"时间 | "` 前缀 ⇒ **真收口永远读不出来**，闸会永远"未收口"而永不处置（合成收口件实测就是假绿）；已改为按 `|` 后的消息字段匹配。②`take_snapshot()` 对同一目录列两次（每次可耗 25 秒上限）→ 合并为一次。另修 VM 探针的控制台编码口径（`encoding="utf-8", errors="replace"`）。
- **本班四处自犯/自纠如实入账**：①测试文件追加时锚点取短，把上一轮的 4 支 early_exit 测试**挤进了新类 `TestVmOffYield`**（依赖 `TestDeferredVerification` 的 helper，会 AttributeError）——靠 AST 类归属计数抓到并搬回；②批量补丁的 docstring 里写 `D:\ZephyrAlpha` 触发 `\Z` 非法转义（3.12 warning、未来 SyntaxError），且我第一轮"修复"被两层脚本的转义折叠骗过，最终用 `chr(92)` 显式拼并以"能 import"为唯一真值才算修好；③验证脚本自身在 GBK 控制台上解码崩（tasklist/PowerShell），已补编码参数；④验证脚本用共享靶 pid ⇒ 被 PID 复用污染（CPU 从 0.1 跳到 10.7 说明那个 pid 已不是我的 sleeper），改为每例独立 sleeper＋唯一快照名。**这四条都是"自己写的尺先量自己"**，不写进来下一班就会重踩。
- **值守班已自动跑过一轮且行为正确**（自动化 `4910ee4e`，每 20 分，硬到期 10-12 12:00）：17:42:37 取生产基线 `close_ts=17:30:38 / state_mtime=2026-10-10 22:58:40 / vault entries=62 newest=13:16:58 / handle leaf=G:\backup\working_vault\20261011\data\failures / cpu=15.58s`，并如实报 `BASELINE_TAKEN_NOW`。**下一次判定要等 18:00:38 之后**（缓释窗 30 分钟）。预判：句柄叶在 14:09 是 `src\zephyr\compliance`、17:42 已是 `data\failures`＝**叶子在换＝枚举在推进**⇒ 下一轮极可能落 `VETO_progress_visible`（＝按协议不处置）。这正是 24968 那次误杀换来的判据在起作用，宁 VETO 不误杀。
- **压缩 round-2 收果（T6，独立对拍不抄自报）**：journal 尾三行 `17:30:38 STEP Start-VM + probe`→`17:31:24 PROBE 1`→`COMPRESS2_END optimize_min=224.8`；`Get-VM zephyr-ch=Running`；**G 余 1964.2 → 2531.4 GB（+567.2）**＝压缩器自报与本方 `Get-PSDrive` 同值；`G:\ch_backup_disk2.vhdx` **934.4 GB → 368 GB（−566.4）**，两个独立尺互咬。目标盘 `data.vhdx/boot.vhdx` 全程未碰（本轮目标只 disk2；顺带量到 `data.vhdx=560GB`，与 round-1 的 +30.3GiB 记录一致：10:5x 时它是 589GB）。**另记一条与本役无关但同盘的数**：D 余 87.0（14:57）→ **77.2 GB**（17:48），3 小时降 9.8GB，D 盘仍是紧的那块。
- **今日点火读数续记**：带 runlog 的点火已 **8 发**，`script=` 字段逐发实测：`.runtime\commit_queue\worktree` **5 发**（14:54:13/15:02:46/15:52:11/17:19:05/17:36:03）＋`worktrees\w0` **3 发**（14:32:51/15:11:09/17:43:55）＝**主区零发**（裁定①的最直接实证）；八发末行全为 `LOCK_HELD`（无一发拿到过锁）（持有者始终 PID:27300，至 17:49 已 4h01m）；生产报告仍 0 份。`backup_skipped_20261011_*` 累计 38 份。本班未手动点火、未清场。
- **零面声明（本段）**：CH 取数 0｜他人进程杀停 0（闸的动作路径只杀自起 sleeper、只清临时锁）｜`G:\backup` 内容零写（合成 fixture 全在 `.runtime\tmp\bf3_fixture\`）｜判据·阈值·门禁码零改动（①②为**新增前置闸**，按裁定①②实施，未动任何既有阈值；`rows` 值是裁定⑦原值）｜备份任务定义零改动｜`session_concurrency.py`/`session_takeover_ledger.py` 零改动（④只转班）｜`test_restore_drill.py` 未代建。
- **候 Owner 裁（累计八件，本班不自决）**：原七件照旧；新增⑧**任务腿的 ②覆盖缺口**（06:00 那条 wscript 链不查 VM；若希望压缩跨过 06:00 也不撞，需批准在 backup.ps1 或任务侧加同一前置）。另 w1 旧版副本对齐（裁定①附带）照排：走序列化车道物化刷新，非紧急、不手改车道文件。
- **复核命令**：`PYTHONPATH=src python -m pytest tests/meta/scripts/backup/ -q`（应 **136 passed**，其中新两支类 9 支：`TestSingleCheckoutPoint` 4＋`TestVmOffYield` 5）；`PYTHONPATH=src python -c "import sys;sys.path.insert(0,'scripts/backup');import backup_reconciler as b;from pathlib import Path;print(b.is_shadow_checkout(Path('.runtime/commit_queue/worktree').resolve()), b.is_shadow_checkout(Path('scripts/backup').resolve()), b.ch_guest_vm_running(b.load_config()))"`（应 影子=True／主区=False／VM=("OK",True)）；`python -u .runtime/tmp/bf3_gate_proof.py`（六分支，P1 那条会因现实已收口而变，见上）；`cat .runtime/tmp/bf3_dispose_snapshot.json`（生产基线）；`cat .runtime/tmp/bf3_dispose_evidence.md`（VERDICT）；`python -c "import importlib.util,sys;sys.path.insert(0,'src');J=['criteria','criteria_change_note','criteria_version','failed_criteria','legacy_judge_note','pass','rows','status'];s=importlib.util.spec_from_file_location('rd',r'scripts/backup/restore_drill.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.run_drill(dump_path=r'Z:\no\absent.dump');print('contract',sum(1 for k in J if k in r),'/8',type(r['rows']).__name__,r['rows'])"`（应 8/8 dict {}）；`tail -4 .runtime/tmp/backfix_compress2_journal.log`；`timeout 120 powershell -NoProfile -Command "foreach(\$d in 'D','G','F'){ \$p=Get-PSDrive \$d; \$d.ToString()+': '+[math]::Round(\$p.Free/1GB,1) }"`。
- **回退令（逐件）**：①②＝`git checkout HEAD~1 -- scripts/backup/backup_reconciler.py scripts/backup/backup_config.yaml tests/meta/scripts/backup/test_backup_reconciler.py`；rows={}＝`git checkout HEAD~1 -- scripts/backup/restore_drill.py`。闸与验证件均在 `.runtime\tmp\`（未入库），停用＝停自动化 `4910ee4e` 即可（remove/disable，不删件）。
- **署名**：adjudicator=st-backfix3-20261011（第五段：裁定①②落地＋③条件持有＋④转班＋rows={}＋T6 收果＋闸验证）。
### 27300 自然收尾（非本班处置）＋锁易主到第四条影子根的 pre-T1 无仪器副本＋本班整轮零动作（st-backfix3-20261011 17:4x-18:3x 值守轮）

- **闸本轮唯一一次运行的输出＝不动手（照协议逐字执行）**：17:42:37 跑 `python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300`，末行 `VERDICT: BASELINE_TAKEN_NOW(wait 18min from close)`，**没有 ACTION 行**＝闸未进入动作路径。同刻它取到生产基线（`.runtime/tmp/bf3_dispose_snapshot.json`：`taken_at=2026-10-11 17:42:37`／`close_ts=2026-10-11 17:30:38`／`state_mtime=2026-10-10 22:58:40`／`vault_entries=62`／`vault_mtime=2026-10-11 13:16:58`／`handle_leaves` 单项＝`G:\backup\working_vault\20261011\data\failures`／`cpu_total=15.578125`）。缓释窗到期时刻＝**18:00:38**。
- **27300 是自己没的，不是本班杀的**：监听件 `.runtime/tmp/backfix_monitor_27300.log` 末行 `2026-10-11 17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`＝目标死在**缓释窗之内**（窗 18:00:38 才满）⇒ 闸的 G2-G5 判定从未到达，它没有任何一次动手机会；监听 23048 按设计随目标退出自退（**非战损**，本班未重启）。对照表落点＝`NATURAL_EXIT_not_our_action` → 转第 4 步守样本。
- **锁 75 秒后即易主（本轮最值钱的读数）**：`.runtime/backup.lock` 现值 `PID:13080 START:2026-10-11T17:52:35.7823345+08:00`。`Get-CimInstance Win32_Process -Filter 'ProcessId=13080'` 实测 `CommandLine` 原文＝`"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\.worktrees\st-datalane-20261010\scripts\backup\backup.ps1`，`CreationDate=10/11/2026 17:52:35`；18:38:55 复测仍 ALIVE（tasklist 命中 powershell.exe 82,160K，已跑 46 分钟）。
- **这条影子根在台账已列三条之外，且它跑的是无仪器旧副本**：已列面＝`.runtime\commit_queue\worktree`、`worktrees\w0`、`worktrees\w1`；本轮实测新根＝**`.worktrees\st-datalane-20261010`**（该件 mtime **2026-10-10 17:08**，早于 T1 的 1de1c216e6 今日 14:32）⇒ 逐 token 实测 `RUN_START`=0 命中、`TRANSCRIPT_ON`=0 命中＝**这一发全程既不写阶段日志也不写 transcript**。直接后果：本班守的"第一份完整阶段日志"**不可能**由这一发产出；它跑完仍是"无观测面的成功或失败"那老形态，与断供期那五发跳锁轮一样给不了读数。
- **点火腿身份＝查不到，按协议不判只登记**：父 PID 52744 双通道一致为空（`Get-CimInstance Win32_Process -Filter 'ProcessId=52744'` 返回 null；`tasklist /FI "PID eq 52744"` 输出"没有正在运行的任务匹配指定条件"）＝发射器短退已不在表上；两侧 ignite 落盘点也都没有对应轮次（该 lane 的 `backup_reconciler_ignite_*` 最新＝09:52:35，主区最新＝10-10 15:05:37，均非 17:52）。**"查不到"不等于"没发生"**：本班不据此判它是哪条腿，也不据此说它没走 reconciler。
- **样本仍在等，读数照记**：今日带 runlog 的点火已 **9 发**（第 9 发 `logs/backup_runlog_20261011_183836.log` 四行齐全＝`RUN_START pid=19732 script=D:\ZephyrAlpha\.runtime\commit_queue\worktree\scripts\backup\backup.ps1 root=D:\ZephyrAlpha`→`TRANSCRIPT_ON`→`WARN Another backup is running (holder PID 13080 alive, lock age 0.8h). Exiting.`→`LOCK_HELD exit 0 skip_record=D:\ZephyrAlpha\logs\backup_skipped_20261011_183836.json`）＝**九发全为跳锁轮，无一发拿到过锁**；主区生产报告仍 **0 份**；`backup_skipped_20261011_*` 累计 39 份；压缩 journal 尾行仍 `COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`（无新行）。判据不变：**等 13080 放锁后的下一发**（T1 在册副本）才是本班要的那份样本。
- **一条残余通道呈报（属判据面，本班不自扩）**：单一检出点闸与备份↔压缩互斥闸都装在 **reconciler 点火腿**的新代码里；17:52:35 这一发的实测特征是"车道根旧副本＋无 runlog＋无 ignite 日志＋发射器短退"，与那两道新闸的覆盖面**不重叠**⇒ 现值下"任意车道根里的 pre-T1 副本仍可起一次无观测面备份"这条通道未被拦住。它与第五段已呈的"任务腿互斥缺口"同族但不同根（那条是 06:00 的 wscript 链，这条是**车道根副本**）。本班只登记证据面，不碰判据。
- **零面声明（本段）**：本班杀停进程 0（闸无 ACTION，本班自身只跑只读探针）｜他人件零改动｜`G:\backup` 内容零写（盘侧 mtime 与句柄叶读数由闸内部完成，本班未列备份盘）｜判据·阈值·门禁·注册表零改动｜备份任务定义零改动｜仪器零新起（未新建第二支 27300 监听；23048 目标已死属设计自退，未重启）｜压缩器 38464 与其 journal/ALARM 零碰。
- **候 Owner 裁（累计九件）**：原八件照旧；新增⑨**车道根 pre-T1 副本的点火通道**（①②均不覆盖；若要覆盖，两种取向＝点火侧统一校验"脚本副本版本"，或禁非主区 `-File` 路径——都属判据/门禁面，本班不自决）。另知悉一条立场变化：本班按协议**未**处置 27300，它自然退出，故"该不该杀 27300"这一问对本班已不存在，全部历史证据留在 `.runtime/tmp/bf3_dispose_evidence.md` 与 `.runtime/tmp/backfix_monitor_27300.log` 两处。
- **复核命令**：`cat .runtime/backup.lock`（应 PID:13080）；`powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter 'ProcessId=13080').CommandLine"`；`grep -c RUN_START .worktrees/st-datalane-20261010/scripts/backup/backup.ps1`（应 0＝无仪器）；`ls -1 logs/backup_runlog_20261011_*.log | wc -l`（应 9）；`tail -4 logs/backup_runlog_20261011_183836.log`；`tail -1 .runtime/tmp/backfix_monitor_27300.log`（应 MONITOR_EXIT_ON_TARGET_DEATH）；`tail -1 .runtime/tmp/backfix_compress2_journal.log`；`ls -1 logs/backup_report_20261011_*.json | wc -l`（应 0＝仍未破零）。
- **署名**：adjudicator=st-backfix3-20261011（27300 处置协议值守班·第一轮：闸输出不动手＋自然收尾登记＋锁易主与无仪器副本显形）。


### 第五/六袋连环死因入册（SSoT-REDEFINITION＋BARE-SUBPROCESS）＋主区 index 藏着 T1 前旧快照显形（st-backfix3-20261011 18:5x-19:2x）

- **两袋接连死于门禁，死因都是本班自己写的字节，不是环境**：q-0005 死于 **SSoT-REDEFINITION**——批量补丁里用了全局 replace，把 `backup_reconciler.py` 既有第 107 行的注释 `# D:\ZephyrAlpha ...` 反斜杠折叠成双份，于是 PROJECT_ROOT 附近进了我的 diff＝门禁按 own-scope 差分命中"重定义项目根"。修法＝该行按 HEAD 字节还原，此后 `git diff HEAD -U0` 里预存行只剩我有意扩写的那一行 [INVARIANTS]。q-0006 死于 **BARE-SUBPROCESS**——`ch_guest_vm_running()` 里写了裸 `subprocess.run([...Get-VM...])`（该件 :704），违 trae_067 铁律2 CREATE_NO_WINDOW 强制；该文件既有裸调用（:518 点火腿）是存量、门只扫 added 行，所以**新写的第 6 行把整袋打死**。**两袋均不复投**（死袋 blob 是旧字节），按现字节另起新袋。
- **BARE-SUBPROCESS 的修法走门禁处方原文，不走 noqa 逃生**：改用统一无窗口入口 `zephyr.shared.infra.process_pool.run_subprocess_hidden`（惰性导入，同 `reuse_scan.py:113` 先例），并在件头 [DEPENDENCIES] 声明该单口；`ImportError` 时返回新态 `("NO_PROCESS_POOL", True)`＝与超时/未配置同族的 **fail-open 放行**，绝不因探针失能而停备份。**没有加 `# noqa: bare-subprocess`**：逃生通道留着，但这个理由不成立。
- **打桩点随迁的正证（不是"改完没测"）**：测试仍 `patch.object(reconciler_module.subprocess, "run", ...)` 却照样绿——因 `run_subprocess_hidden` 在 `meta_out is None` 路径上直接调 `subprocess.run(cmd, **kwargs)`，而 patch 的是 stdlib `subprocess` **模块对象上的属性**，两个模块引用同一对象 ⇒ 打桩依旧命中。实测 `PYTHONPATH=src python -m pytest tests/meta/scripts/backup/ -q` = **136 passed in 24.37s**（含新两支类 9 支）；`ruff check`/`ruff format --check` 全绿。这条命中的**判别力**来自 `test_vm_query_parses_state_string`：若惰性导入失败，它会拿到 `NO_PROCESS_POOL` 而断言 `("OK", True)` 失败——它没失败，所以"zephyr 包在该测试基座可导入"也被同一支测出来了。
- **真机三态复测（同分钟，零改任何东西）**：`load_config()['ch_backup']['vm_name']=zephyr-ch`、`ch_guest_vm_running()=('OK', True)`（Hyper-V 现值 Running，压缩器 17:31:24 已把 VM 起回）＝②号互斥闸的读取腿在真机上走得通；`is_shadow_checkout` 主区 False／车道 True 已在前段测过，本段只补一句：这两道闸都装在 **reconciler 点火腿**，任务腿与车道根 pre-T1 副本的缺口照第五段⑧⑨呈批，本班不自扩。
- **主区 index 里藏着一枚能把 T1 整块删掉的旧快照（盘外风险，本班显形并处置）**：`git status` 报 `scripts/backup/backup.ps1` 为 MM，但 `git diff HEAD -- backup.ps1` **零输出**＝工作区与 HEAD 一致，异常全在 index。逐 blob 对表：index 版 = `c1b58ec43a6fd5c707d55f86db0c4018242cafe3`，而 `git rev-parse 1de1c216e6^:scripts/backup/backup.ps1` = **同一枚**；HEAD 版 = `11730c26c7...`。内容级复测 `Write-Journal` 命中数：index **0**／HEAD **12**／工作区 **12**；对 index 版做 numstat 是 **+55/−104**＝谁在主区裸 `git commit`（提交整枚 index），T1 的"静默早退治本"会被静默删回 pre-T1 形态，且这次连**旧缺陷（容量守卫函数先调后定义）也一起复活**。**判它不是他人在飞工作的依据**：该 blob 逐字节等于一个已知 HEAD-祖先 commit 里同名文件的版本＝零独有内容，属死袋回放残留的旧暂存快照（q-0005/q-0006 之前的袋字节曾对 index 写过）。本班处置＝仅对这一件 `git add scripts/backup/backup.ps1`，把 index 刷成 HEAD 字节；被弃的是 git 永久对象、随时可取，无任何内容损失；他人 staged 条目零触碰（`git status --porcelain` 处置后只剩本班五件）。若 Owner 认为"碰 index"本身越界，本行即回退指针：`git update-index --cacheinfo 100644,c1b58ec43a6fd5c707d55f86db0c4018242cafe3,scripts/backup/backup.ps1` 可原样放回去。
- **在册工法两条**：①**批量补丁禁全局 replace**——一次误伤既有行就让门禁替我发现了"我挪了别人门柱"，改后必以 `git diff HEAD -U0` 的**预存行清单**自证（只看新增会漏掉"我改掉的既有行"这一类）。②**MM 状态必须三段对表**（worktree↔HEAD、index↔HEAD、worktree↔index）——只看 `git diff HEAD` 会得出"没问题"的假结论，而这枚地雷恰恰只埋在 index；这条与前记"内容门禁读 index 不读工作区"是同一枚钱的两面。
- **零面声明（本段）**：判据·阈值·门禁码零改动（改动=新闸内部换子进程入口＋头部署名，未动任何阈值）｜他人 staged 条目零触碰｜`G:\backup` 内容零写｜进程杀停 0｜CH 取数 0｜未用 noqa 逃生绕过 BARE-SUBPROCESS｜未复投死袋。
- **复核命令**：`git rev-parse :scripts/backup/backup.ps1`（处置前应 c1b58ec4…，处置后＝`git rev-parse HEAD:scripts/backup/backup.ps1`）；`git show :scripts/backup/backup.ps1 | grep -c Write-Journal`（应 12）；`PYTHONPATH=src python -m pytest tests/meta/scripts/backup/ -q`（应 136 passed）；`python -m ruff check scripts/backup/backup_reconciler.py`；`PYTHONPATH=src python -c "import importlib.util as u;s=u.spec_from_file_location('b','scripts/backup/backup_reconciler.py');m=u.module_from_spec(s);s.loader.exec_module(m);print(m.load_config()['ch_backup']['vm_name'],m.ch_guest_vm_running())"`（应 zephyr-ch ('OK', True)）；`grep -n "run_subprocess_hidden" scripts/backup/backup_reconciler.py`（应见惰性导入与调用两处＋[DEPENDENCIES] 一行）。
- **署名**：adjudicator=st-backfix3-20261011（第六段：第五/六袋死因对症修复＋子进程入口归一＋index 旧快照显形与处置）。
### 本班口径更正（两处，被本轮实测证伪）＋链上第一行 LOCK_ACQUIRED 到手＋在岗点火腿读的是落后 HEAD 的旧 reconciler（st-backfix3-20261011 18:4x-20:2x 值守轮）

- **更正一：上一段写"点火腿身份＝查不到"，错了，原因是我把 UTC 当本地读**。实测：`.worktrees/st-datalane-20261010/logs/backup_reconciler_ignite_20261011_095235.log` 的 `095235` 是 **UTC**，对应本地 **17:52:35**，与本方 `Get-CimInstance Win32_Process -Filter 'ProcessId=13080'` 读到的 `CreationDate=10/11/2026 17:52:35` **逐秒咬合**；该件 mtime 实测 `2026-10-11 18:40:33`（＝我读它时还在写）。同例复证：本轮第 10 发的点火链件＝`.runtime/commit_queue/worktree/logs/backup_reconciler_ignite_20261011_114840.log`（11:48:40 UTC＝19:48:40 本地），与主区 `logs/backup_runlog_20261011_194841.log` 成对。**上一段用"文件名时刻对不上"判它"无对应轮次"＝UTC/本地混读的在册老陷阱（心跳件与 safe_write.jsonl 同型），本班当场认。**
- **更正二：上一段写"这一发全程不写阶段日志、给不了读数"，只对了一半**。该副本确实不含 T1 仪器（逐 token 实测 `RUN_START`=0、`TRANSCRIPT_ON`=0），但 **reconciler 的 ignite stdout/stderr 本身就是它的阶段级观测面**，本轮已逐行拿到（Stage 1/2/3 齐）。⇒ 本班守的判据要重述为：**"主区 `backup_runlog_*` 里出现 `LOCK_ACQUIRED` 的第一发"**，而不是"有没有任何阶段输出"。
- **13080 那一发的实际形状（ignite stdout 逐段，止于 18:40:33）**：Stage 1 三盘 online＋robocopy found；Stage 2＝PG public dump **241.55MB**、globals ok、SQLite 2 库、PG/CH config synced、manifest **225 tables**、CH incremental（ratio 0.26）async id=71311969… → **72.2 GiB / 890,929 files / 225 tables / verified=True**、双写同步 ok（`/mnt/chbackup2/inc.zip 77,507,296,953 Oct 11 10:39`）；Stage 3＝同日快照→Mode B 增量刷，diff `G:\backup\working_vault\20261011`＝**source 46,821 / snapshot 46,688**，`Snapshot: linked=0 copied=505 replaced=365 failures=0 vanished=0 share_locked=1`，唯一 WARN＝`data\runtime\dwm_shard_state_supplementary2_20261011\tilib_dwm_runner_instance.lock` 被活写者共享锁占用跳过；**此后无 Stage 4/5、无收尾行**。
- **13080 的落幕与本班立场**：18:38:55 同命令复测仍存活（`tasklist` 命中 powershell.exe 82,160K），19:46:19 复测**已不在进程表**；`.runtime/backup.lock` 在 19:46:19 与 19:54:56 两次都**不存在**＝锁被释放而非遗留。该发生命 17:52:35→≤18:40:33（**≤48 分钟**），主区与车道根两侧 `backup_report_20261011_*.json` **各 0 份**＝这发没出报告。**死因本班不判**：pre-T1 副本没有早退显化，本班无尺可量，只登记"走完 Stage 1-3、停在 dumps 腿之后、锁已释放、零报告"这个形状。本班全程未碰它（红线），它自己结束。
- **本轮最硬的一条缺陷（E-4 容量红线三道闸在这份车道副本里是从未执行过的死码）**：err 原文＝`Test-CapacityGuardBreach : 无法将...识别为 cmdlet、函数、脚本文件或可运行程序的名称`＋`所在位置 D:\ZephyrAlpha\.worktrees\st-datalane-20261010\scripts\backup\backup.ps1:825 字符: 13`。行序实测（同一件内）：该副本**定义在 :963**，**调用点三处＝:825（dumps 腿）/:1025（off-repo 腿）/:1103（G-mirror 腿）全在定义之前**⇒ PowerShell 函数按执行顺序注册，先调用必 `CommandNotFoundException`；对照**主区与 HEAD 的同一件＝定义 :352、调用 :919/:1068/:1146 全在其后＝健康**。⇒ 同一段 E-4 补丁在两份副本里一份有效、一份三处全哑，这不是"副本旧一点"的轻重。
- **哑在哪一侧，本班读到分支原文才敢说（方向性判据不自转述）**：:823-834 原文＝`$rcDumps = 0`／`$dumpsSkippedByGuard = $false`／`if (Test-CapacityGuardBreach $dumpsDayTarget) {…} else { & robocopy …; $rcDumps = $LASTEXITCODE }`／随后 `if (-not $dumpsSkippedByGuard) { if ($rcDumps -ge 8) {Write-Warn …} else { Write-OK ("DB dumps snapshot done: {0}" …) } }`；该件 :30 实测 `$ErrorActionPreference = "Continue"`（非 Stop）⇒ 语句级中止、脚本继续，**条件抛出时 if/else 两支都不执行、robocopy 从未跑、`$rcDumps` 停在 0、随后仍会打印 "[OK] DB dumps snapshot done"**。如实标价：本轮 stdout 里 `dumps` 相关行 **0 命中**＝那行假 OK **尚未实测到**，本班把它记为**按代码推演必然可达**，不虚报为已观测。off-repo(:1025)/G-mirror(:1103) 两腿各带 `continue`，同型抛出＝该 target 连镜像都不做，而这两腿本轮**还没跑到**。
- **链上第一份完整阶段日志已到手（本班的靶心）**：第 10 发 `logs/backup_runlog_20261011_194841.log`，`RUN_START pid=40008 mode=all force=False script=D:\ZephyrAlpha\.runtime\commit_queue\worktree\scripts\backup\backup.ps1 root=D:\ZephyrAlpha` → `TRANSCRIPT_ON logs/backup_transcript_20261011_194841.log` → **`LOCK_ACQUIRED D:\ZephyrAlpha\.runtime\backup.lock`＝今日十发里第一发拿到锁，也是本链史上第一行 LOCK_ACQUIRED** → `STAGE Stage 1: Pre-check` → 三盘 online＋robocopy found → `STAGE Stage 2` → 19:49:24 PG dump 241.57MB＋globals ok → 19:50:03 SQLite 2 库＋PG config → 19:50:15 CH config → 19:50:16 manifest 225 tables → 19:50:19 `CH backup mode: incremental (ratio 0.26)` → 19:50:26 删旧 inc.zip → 19:50:28 self-heal 清 `*.zip.lock` → 19:50:28 `ClickHouse BACKUP (incremental) async id=4d32fe28-596d-438c-b7ec-0be7133bfb42`。截至 20:21:51 该发**仍在跑**（本方零写入探针件 `powershell -File .runtime/tmp/bf3_probe_40008.ps1` 实测 `ALIVE wall_min=33.2`），末行停在 CH async 步 31 分钟，transcript mtime 19:50:28、err 面空＝**无 traceback**。收尾（Stage 3/4/5 与 RELEASE_LOCK）留给下一值守轮摘。
- **中间那段空窗要如实分开记**：18:40:33 锁释放后，直到 19:48:41 才有下一发＝**65 分钟零点火**（`logs/backup_runlog_*.log` 计数在 18:38→19:46 两次读都是 9），而此前节奏 8-20 分钟一发。⇒ "第一份完整阶段日志"这 65 分钟里挡它的**不是 27300、也不是任何持锁者，而是点火侧自己**；本班未手动点火（红线），也无法区分是 cadence 未到期／reconciler 未在跑／被新闸判成 yield——主区 18:40 之后没有 reconciler 状态面读数可锚，故只登记空窗，不下结论。
- **一条 P0 形态的呈报（不是本班裁，是与"运行码落后 HEAD"同型的老病）**：在岗点火腿读的是**影子根那份落后 reconciler**——实测 `.runtime/commit_queue/worktree/scripts/backup/backup_reconciler.py`（mtime 10-11 **18:37**）内 `is_shadow_checkout`=**0 命中**、`ch_guest_vm_running`=**0 命中**；同一件主区盘上件（mtime 19:12）分别 **3／2 命中**，`git show HEAD:` 亦 **3 命中**⇒ 裁定①单一检出点闸与裁定②互斥闸**已在主区与 HEAD，但不在这发实际执行的副本里**。直接后果：19:48:40 这一发**从影子根 `.runtime\commit_queue\worktree` 点火成功**＝①在最关键的一次真机场景上零拦截，且原因不是判据不成立，而是**在岗码落后**（物化刷新未追平）。本班不碰车道文件、不自扩修法（对齐属总统统筹裁定①附带项），只把这条测达面写清。
- **闸的正式判词（补跑一次，由仪器下结论而非本班推断）**：19:47:30 `python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300` 末两行＝`VERDICT: NATURAL_EXIT_not_our_action`、**无 ACTION 行**，因子面＝`close_status='CLOSED'`／`close_ts='2026-10-11 17:30:38'`／`relief_elapsed_min=136.9`／`target_alive='DEAD'`。⇒ 处置问题由闸自己关闭；本班两轮累计**零处置、零杀停**。
- **零面声明（本段）**：本班杀停进程 0（两轮闸均无 ACTION；本班只跑只读探针与一个零写入的存活探针件）｜`G:\backup` 内容零写（未列备份盘目录，盘侧读数来自闸内部与既有观测件）｜他道件零改动（两份车道根副本只做行序取证，未"顺手修"pre-T1 的 backup.ps1/reconciler）｜判据·阈值·门禁·注册表·备份任务定义零改动｜仪器零新起（未新建 27300 的第二支监听；23048 随目标自退未重启）｜压缩器 38464 与其 journal/ALARM 零碰（journal 尾仍 `COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`）。
- **候 Owner 裁（累计十一件，本班不自决）**：原十件照旧（含上一条改口：⑨"点火通道"已被本段细化＝那条腿确是 reconciler 点火链，只是执行的是落后 HEAD 的旧副本，① 因此在真机上未生效）；新增⑩**E-4 容量红线在车道副本里"调用先于定义"的三处死码**（取向＝车道根副本走序列化物化刷新对齐；是否另加"点火前校验脚本可解析/函数已注册"的前置属判据面）；新增⑪**18:40→19:48 的 65 分钟点火空窗**（若 Owner 认为等待不可接受，需点名是否允许本班在锁空闲时手动点火一次——现值下本班按红线继续等）。
- **复核命令**：`head -3 logs/backup_runlog_20261011_194841.log`（应见 `LOCK_ACQUIRED`，全链第一行）；`ls -1 logs/backup_runlog_*.log | wc -l`（应 ≥10）；`grep -c 'LOCK_ACQUIRED' logs/backup_runlog_20261011_*.log`（应只在 194841 那支命中 1）；`grep -n 'function Test-CapacityGuardBreach' .worktrees/st-datalane-20261010/scripts/backup/backup.ps1`（应 :963）＋`grep -n 'Test-CapacityGuardBreach \$' 同件`（应 :825/:1025/:1103 全在前）；`git show HEAD:scripts/backup/backup.ps1 | grep -n 'function Test-CapacityGuardBreach'`（应 :352）；`grep -c is_shadow_checkout .runtime/commit_queue/worktree/scripts/backup/backup_reconciler.py`（应 0）＋`grep -c is_shadow_checkout scripts/backup/backup_reconciler.py`（应 3）；`stat -c '%y %n' .worktrees/st-datalane-20261010/logs/backup_reconciler_ignite_20261011_095235.log`（mtime 18:40:33＝UTC 命名实证）；`tail -3 .runtime/tmp/bf3_dispose_evidence.md`（应 `target_alive='DEAD'`＋`NATURAL_EXIT_not_our_action`）；`ls -1 logs/backup_report_20261011_*.json | wc -l`（应仍 0＝未破零）。
- **署名**：adjudicator=st-backfix3-20261011（27300 处置协议值守班·第二轮：两处口径自纠＋13080 全程与落幕＋E-4 死码行序实测＋第 10 发 LOCK_ACQUIRED＋①在落后副本上零拦截的测达面）。

### 21:4x 值守轮：闸判 NATURAL_EXIT（本班零处置）＋主菜到手＝首份完整阶段日志（19:48:41→21:14:58 pid=40008）＋17:52:35 无仪器轮收场零留痕已被四根实测证实（st-backfix3-20261011）

- **闸本轮唯一动作的输出（21:46:32）**：`python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300` → 末行 `VERDICT: NATURAL_EXIT_not_our_action`，**没有 ACTION 行**＝闸未进动作路径，本班这一轮没杀没停任何进程。它取到的值：`close_status='CLOSED'`／`close_detail='2026-10-11 17:31:24 | PROBE 1 ~ ~'`／`close_ts='2026-10-11 17:30:38'`／`relief_elapsed_min=255.9`／`target_alive='DEAD'`。G0 成立依据＝压缩 round-2 journal 末行 `COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`（前一行 `G_free_GB=2531.4`）；压缩器 38464 与其 journal/ALARM 本班未碰、其存活谓词未改。
- **27300 的死因侧证（本轮新读数，与上轮"自然收尾"互证而非重复）**：三陷阱面 `.runtime/tmp/procstart_trap_ppid.log` 有 `2026-10-11 17:51:23 | EXIT pid=27300 ppid=48908 name=powershell.exe` 与 `EXIT pid=50928 ppid=27300 name=conhost.exe`；监听 23048 在 17:51:19 记 TARGET_DEATH（相差 4 秒，两器同一时刻收敛），并记 `EVT_System none within 15min window`／`EVT_Application none`（OS 日志无事件＝用户态退出旁证），`KILLER_CASE written: .runtime/tmp/backfix_killer_case_20261011_175120.md (candidates=295)` 后 `MONITOR_EXIT_ON_TARGET_DEATH`。21:46 与 21:5x 两次 `tasklist` 复测均"无匹配任务"＝DEAD。**本班没有对它下过任何手，也没补刀、没删锁。**
- **三面读数（21:46-21:47，全只读）**：`.runtime/backup.lock` **不存在**（非本班所为，见下条链条）｜今日 `backup_report_20261011_*.json`=**1 份**，且全仓四根 `find -name backup_report_20261011_*` 也只有这 1 份｜最新 runlog=`logs/backup_runlog_20261011_194841.log` 末行 `2026-10-11 21:14:58 | RELEASE_LOCK | pid=40008`｜压缩 journal 如上已 END｜监听 23048 已按设计自退（非战损，本班未重启，遵守"不新建第二支监听"红线）。断供口径实测：`ls -1t logs/backup_report_*.json` 前两名＝`20261011_194841`／`20261009_052740` ⇒ "10-09 05:27 之后为 0 份"今日**首次翻正**。
- **本班主菜到手＝第一份带完整阶段日志的轮次**（逐段摘录；全文对＝runlog 4764 字节＋transcript 7533 字节，同刻 194841）：
  - `RUN_START | pid=40008 mode=all force=False script=D:\ZephyrAlpha\.runtime\commit_queue\worktree\scripts\backup\backup.ps1 root=D:\ZephyrAlpha` ⇒ 点火副本＝**影子根 commit_queue\worktree**，且它认得 RUN_START/TRANSCRIPT_ON＝T1（1de1c216e6）确在那份副本上；随后 `TRANSCRIPT_ON D:\ZephyrAlpha\logs\backup_transcript_20261011_194841.log`、`LOCK_ACQUIRED D:\ZephyrAlpha\.runtime\backup.lock`。transcript 头块给出 `主机应用程序: ...powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\.runtime\commit_queue\worktree\scripts\backup\backup.ps1`／`进程 ID: 40008`／PSVersion 5.1.26100.6899。
  - Stage 1 Pre-check：D/F/G 三路 online、robocopy 命中 System32。Stage 2：PG dump 241.57MB／globals ok／SQLite 2 库／PG+CH 配置同步／Pre-backup manifest 225 表；CH 模式 incremental ratio 0.26；清旧 inc.zip；`Self-heal: cleared stale *.zip.lock (if any)`；async id=4d32fe28-596d-438c-b7ec-0be7133bfb42 → `ClickHouse dump (incremental): ok (76.9 GiB, 1010694 files, 225 tables, verified=True)`；双写同步 chbackup_local→chbackup2 ok（inc.zip 82534136381／market.zip 298968010737）。
  - Stage 3 代码备份：同日快照存在→增量刷新 Mode B；diff 源 vs `G:\backup\working_vault\20261011`＝46902 / 46829；`Snapshot: linked=0, copied=100, replaced=23, failures=0, vanished=5, share_locked=1`（vanished 5 项全是 `.ailocks\*.lock\owner.json` 会话锁被并发释放，share_locked 1 项＝`data\runtime\dwm_shard_state_supplementary2_20261011\tilib_dwm_runner_instance.lock` 活写手占用）；DB dumps snapshot→`G:\backup\db_dumps\20261011`。
  - Stage 3b：bundle 最新已 8.83 天旧、手上 2 份 → `Bundle created + verified (499 MB, rotated 1 old)`。Stage 3c 库外资产：`[trae_memory] source missing (WARN, not run-fatal): C:\Users\fanzi\.trae-cn\memory`、qmt_bridge 0.00GB、stash_archive 0.13GB、cold_archive 193.16GB、tomb_quarantine 3.38GB 全 ok。Stage 3d G 盘兜底镜像 zephyr_cold ok `would_purge=0/cap=200`。
  - Stage 4：`Report saved: D:\ZephyrAlpha\logs\backup_report_20261011_194841.json`（机读侧实测顶层键＝mode/git_bundle/force_mode/stage_timeline/duration_seconds/timestamp/offrepo_backup/code_backup/g_mirror/databases，databases.clickhouse.size_match=true）；Stage 4b 滚动归档 hook：`valve1: SKIP: last_ch_backup_status=None`、`executed=[]`、`skipped=[]`、`circuit=null`；末两行 `Backup completed in 5165.4s` → `RELEASE_LOCK | pid=40008`。`stage_timeline` 最大单项＝`ClickHouse dual-write sync` t_seconds=3657.7（占 5165.4s 的 71%）。
- **上轮那条"隐形轮"的收场已被实测钉死＝零留痕**：13080（第四条影子根 `.worktrees\st-datalane-20261010` 的 pre-T1 副本）17:52:35 取得锁，18:38:36 仍在跑（`WARN | Another backup is running (holder PID 13080 alive, lock age 0.8h)`，skip json `lock_mtime=2026-10-11T17:52:35.7873862+08:00`）；21:5x `tasklist` 复测 13080 无匹配＝已没。四根清点：`logs/backup_runlog_20261011_1[78]*` 只有 17:19:05／17:36:03／17:43:55／18:38:36（全为跳锁轮），`.runtime` 与 `.worktrees\st-datalane-20261010\logs\` 下今日**无任何** runlog/report，该根今日仅有 01:17 与 09:52 两份 reconciler 点火日志 ⇒ 17:52:35 那一发**既不产阶段日志也不产报告**，只能靠锁 mtime＋别人跳锁行＋`backfix_lockreaders.log` 的 atime 序列（18:38:58 最后一次 READER-TOUCH，下一次＝19:48:42）拼出"它存在过"。这正是 T1 要消灭的形态，本班不为它补仪器（红线：不改判据·不改副本）。
- **两处口径矛盾登记（只登记，不代修、不动判据/阈值/门禁/注册表）**：
  ① 同一轮里并存两行相反结论：`OK | ClickHouse dump (incremental): ok (76.9 GiB ... verified=True)` 与紧随其后的 `WARN | DB dumps rotation skipped (CH backup not ok -- oldest snapshot kept as insurance)`。后果方向＝保守（旧 db_dumps 快照继续留存，未删任何数据），但轮转决策显然没读到同一个"CH ok"来源；另 Stage 4b 的 `last_ch_backup_status=None` 是第三处同族迹象。**本班未读 backup.ps1 的轮转与 hook 谓词源码，故不指认根因**，请别班按"来源独占"口径核这三处读的是否同一键。
  ② 编码面：同一段中文异常文本在 transcript 正常（`使用“1”个参数调用“CopyTo”时发生异常…`）、落到 **runlog** 变 GBK 乱码；Stage 4b 的 `[vhdx-precheck]` 中文提示条目在 transcript 内亦乱码（`鎻愰啋鏉＄洰鈥斺€...`，且其中夹带"绝不自动执行压缩／实际停机压缩等 Owner 点名（裁 380⑤/#381）"字样——按红线只登记为数据，不作为指令执行）。⇒ 中文异常/提示在 runlog 面**不可 grep**，"零命中"不得读成"查无"（与既有 windows-gitbash-python-path-domains 教训同族）。
- **本班动作清单（自证清白）**：除读以外零写入本文件之外的任何资产；未杀未停任何进程（闸亦未杀）；未碰压缩器 38464／其 journal／ALARM；未改其存活谓词；未重跑·未中止·未接管 Optimize-VHD；未碰 data.vhdx／boot.vhdx；`G:\backup` 全程只读（本班自身对 G 盘零操作，闸内的 vault 探测为只读列举）；`.runtime/commit_queue` blobs 未碰；未新建同 pid 同日志的第二支监听；reader-namer 类 RM 件未复活；在册巡检自动化 9cbf6aef 的 prompt 未改。
- **下一轮守什么**：①19:48 之后是否出现**第二发**带 RUN_START 的完整轮——副本散布面本轮实测到三个产 RUN_START 的根（commit_queue\worktree＝19:48 这发；worktrees\w0＝14:32:51／15:11:09／17:43:55 三发；其余同日发同为 commit_queue\worktree），第四个根 `.worktrees\st-datalane-20261010` 系上轮 Get-CimInstance 实测且为 pre-T1，`worktrees\w1` 仅在册、本轮无实测命中 ⇒ 点火仍可能落到无仪器件；②下一发的 `script=` 字段是第一件要读的东西（它决定这发能不能给读数，比任何 CPU/进度读数都早给答案）；③`backup.lock` 若再次"存在而 holder 是 pre-T1 副本"，本班只报链条不处置（协议 G0 未闭合或 VETO 路径）。


### 案 #17（27300）定名＋链上第一份完整收卷＋403 尺排他面当场收紧＋pre-T1 假绿行实锤（st-backfix3-20261011 20:4x-22:0x 收口轮）

- **定名＝自毙族（与案 #15/#16 同形态），且本班把这把尺的排他范围当场标价收紧**。正证面：①legacy 通道 **17:51:19 id=403**（引擎 Available→Stopped）的 HostApplication 逐字＝`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\.runtime\commit_queue\worktree\scripts\backup\backup.ps1`，RunspaceId=f7faad63-3d10-4732-a817-f1dafa1ea1d8，原文＋全属性已冻结到 `.runtime/tmp/bf3_case17_evidence_403.txt`（9 条 400/403，325 行）；②陷阱 EXIT 17:51:23（比 403 晚 4 秒＝收尾 drain 形态）；③死窗 [17:50:30-17:52:00] 出生链 **零 kill 原语**（taskkill/Stop-Process/terminate/wmic delete 全 0 命中）；④reaper 面照旧排除（keep 行赦免 backup.ps1＋ghost 判据第一道=name 前缀，powershell 永不入列），守卫接管杀最近开火仍停 10-10 01:17。**尺的标价修正（对前班口径的收紧，随案呈报）**：403 只排除 **TerminateProcess 型**他杀（强杀不给引擎写 403 的机会），**不排除"优雅关闭"型**（不带 /F 的 taskkill＝发 WM_CLOSE/控制台关闭请求，PS 会照常写 403 再退）；本案按新口径仍落自毙，因为该窗连"优雅关闭"的原语都没出生，但今后不得再用"有 403"单独宣告洗清他杀。
- **27300 那 4 小时在做什么＝本班这次新拿到的读数（机制级，不是猜）**：重定向文件的 **mtime＝最后一次内容写入时刻**（合成件实测：子进程只写一行后睡 40 秒，+6 秒读 len=17/mtime=写入秒，退出后 mtime 不变 ⇒ mtime 不随句柄关闭推进），于是它的两份落盘可以同时定时刻——stdout 末行与 stderr 唯一记录**都写在 17:51:19**。⇒ Stage 3 的 Mode B 增量刷（`Source files: 46698, snapshot files: 46680`／`Snapshot: linked=0 copied=23 replaced=15 vanished=11`）从 13:49 一路爬到 **17:51:19＝约 4 小时 02 分**，而这段窗正是 Optimize-VHD 独占 G: 的 13:45:50→17:31:24。对照读数：**同一条腿在今晚修复轮（G 空闲）只花 11.4 分钟**（20:49:41→21:01:03）＝**约 21 倍**。这给裁定②（备份↔停机压缩互斥）补上了量化理由，不是"怕撞"而是"撞了会慢 21 倍并连带堵死全部后续点火 9 发"。vanished 清单只含 13:46-13:48 建的 tsv＝枚举快照在 13:49 前建立、拷贝腿随后长爬，两条互相咬合，无矛盾。
- **停点后 4 秒内的形状（诚实标价：这一段盘外不可定名）**：17:51:19 它进入 db_dumps 腿，撞上 `Test-CapacityGuardBreach : 无法将…识别为 cmdlet`（该 pre-T1 副本调用在 :825、定义在 :963＝先调后定义），stderr 有这一条；**但 stdout 里没有紧随其后的 `[OK] DB dumps snapshot done` 行**（该件全文 grep `dumps|Bundle|rotation` 零命中）＝脚本没走到 8 行外的下一句就离体了。按 EAP=Continue 的合成件实测（`FALSE-OK-PRINTED`/`AFTER-IF-STATEMENT`/`SCRIPT-CONTINUES-AFTER-FUNCTION` 三行全打出）它**本应继续**，所以这里存在一个本班无尺可量的缺口；候选两条：一是控制台被"优雅关闭"（新口径下 403 不排除它，但该窗零原语），二是该作用域被某种终止性条件整体中止（无 ErrorRecord 佐证）。**语句级不下结论**，Operational 通道在 17:50:00-17:52:40 共 105 条中**无一条属该主机**（4100/4104 全是别的 runspace），Analytic 仍关、procdump 类四件仍不存在、pre-T1 副本无 transcript。
- **pre-T1 假绿行实锤（把"两天零上账"从"没跑"升级成"打了绿行而没跑"）**：同一份 pre-T1 字节＋EAP=Continue 的合成件证明守卫抛出后 `$rcDumps` 停在 0、`$dumpsSkippedByGuard` 停在 `$false`，于是 `Write-OK ("DB dumps snapshot done: ...")` **照常打印**，而 robocopy 从未运行。任务腿（wscript→vbs 隐藏控制台）的输出蒸发面此前已实证 ⇒ 10-09 06:10（先调后定义埋进 HEAD 的那一袋）到 10-11 14:32 之间**每一轮都自报过这行绿**，盘上却零文件。实测落点：`G:/backup/db_dumps/20261010` **0 件**、`20261009` 4 件、`20261008` 4 件。本班没修的那两天里，绿是假的。
- **裁定③以"链路自产"达成（零手造）**：今晚修复轮写出 `G:/backup/db_dumps/20261011/` **4 件**＝`depgraph.dump 253,302,680`／`governance_backup.db 250,793,984`／`pg_globals.sql 206`／`session_backup.db 12,288`（mtime 19:49-19:50，全部由链路自产，`G:\backup` 侧本班零手写）。残余如实标价：**`20261010` 仍是 0 件且不可回造**——重跑只能得到"今天的库状态"，把它标成 10-10 就是造伪证；本班按"保留空目录＋登记"处理，是否用别的通道补 10-10 属 Owner 面。
- **链上第一份完整收卷（T7 的靶心，本班与值守轮各自独立读到）**：第 10 发 `logs/backup_runlog_20261011_194841.log` 全 38 行走完——`RUN_START pid=40008 mode=all script=.runtime\commit_queue\worktree\...` → `TRANSCRIPT_ON` → **`LOCK_ACQUIRED`** → Stage 1（三盘 online＋robocopy found）→ Stage 2（PG 241.57MB＋globals＋SQLite 2 库＋PG/CH config＋manifest 225 tables）→ `CH backup mode: incremental (ratio 0.26)` → 19:50:28 `ClickHouse BACKUP async id=4d32fe28...` → **20:49:39 `ok (76.9 GiB, 1010694 files, 225 tables, verified=True)`**（CH 腿独占 59 分 11 秒）→ 双写同步 ok → Stage 3（11.4 分钟枚举＋`copied=100 replaced=23 failures=0 vanished=5 share_locked=1`）→ `DB dumps snapshot done`（这次是真做了）→ Stage 3b bundle 499MB＋轮换 1 旧 → Stage 3c off-repo 四腿（cold_archive 193.16GB、tomb_quarantine 3.38GB；WARN 一条＝`trae_memory` 源 `C:\Users\fanzi\.trae-cn\memory` 不存在）→ Stage 3d G-mirror → **Stage 4 `Report saved: logs/backup_report_20261011_194841.json`** → Stage 4b → `Backup completed in 5165.4s` → **`RELEASE_LOCK pid=40008`**。主区 `backup_state.json` 同步回写：mtime 21:14:46、`last_backup_time=2026-10-11T21:14:46`、`last_backup_status=ok`、`last_ch_backup_status=ok`；`logs/backup_report_20261011_*.json` **1 份＝两日来首次破零**（上一份停在 20261009_052740）；`.runtime/backup.lock` 已消失（finally 正常释放，无残留）。
- **顺带抓到一条自指次序缺陷（保守方向，本班不修）**：dumps 轮转闸的判据是 `Get-Content $StateFile | ConvertFrom-Json` 再读 `last_ch_backup_status -eq "ok"`，而那份 state 要到 **Stage 4 才被本轮写回**⇒ 轮转永远在拿"上一轮"的 CH 结论判"本轮"，今晚就因此打出 `WARN DB dumps rotation skipped (CH backup not ok -- oldest snapshot kept as insurance)`，同轮报告里 `clickhouse.status=ok / verified=True`。方向标价＝**多留不删**（fail-safe），不危险，但它意味着"首次恢复的那一轮必不轮换"，且旧快照清理永远滞后一轮。属判据面，本班只登记。
- **legacy 通道保留窗实测≈4 小时（对本战役最要命的一条工法）**：20:49 实测 `Windows PowerShell` 通道 **OLDEST=10-11 16:49:24／NEWEST=20:49:37／COUNT=12440**（≈52 件/分钟）。⇒ 403 尺是**有硬时限的证据**：案发后约 4 小时内不定名就永久不可复核（本班这次靠"当场冻结原文"抢下来）。这条同时**洗清一处误会**：前班案 #16 在册的 12:25:18/13:16:59 三条 400/403 今日按同一命令读回**零行**，不是记录有假，而是已被冲刷（本班曾据此怀疑前班引用，现更正为"冲刷所致，不可复核"）。今后每案的 400/403 原文必须在定名轮内落盘存证。
- **400/403 尺的两处校准（前班命令今日为何零命中的第二个原因）**：①**过滤词必须对出生形态**：前班用 `backup.ps1 -Mode` 作匹配词，只覆盖任务腿（`-File ...backup.ps1 -Mode all -Force`）；reconciler 点火腿的命令里没有 `-Mode`（逐字＝`-File <root>\scripts\backup\backup.ps1`），故对 27300/13080/40008 一律零命中——本班改用 `backup.ps1` 后同窗立刻出 7 条。②**观测者自造行要先减**：全天窗里含 `backup.ps1` 的 400/403 共 39 条，其中 16:15/17:19/18:18/19:13 那批是**本班自己的 AST 探针**（`Parser::ParseFile('...backup.ps1')`）与查进程表的探针，靠"`-File` 后紧跟路径"的形态判据才剥干净；且探针主机的 `HostId` 字段是常量串 `System.Management.Automation.Internal.Host.InternalHost`，真发射主机的 `HostId` 才是 GUID——**同一性尺要按 (HostId, RunspaceId) 成对读，别只认一个字段名**。
- **今日发射谱（校准后重测，05:00→20:47）**：真发射 runspace 共 13 个，root 全为影子根——`QW/worktree`（序列化车道）＝13:48:30 的 27300、17:19:04、17:36:03、18:38:36、19:48:41（40008，完成）；`QW/w0`＝17:43:55；`WT/st-datalane-20261010`＝17:52:35（13080，18:40:33 止）；**主区 D:\ZephyrAlpha 起零发**。短命 runspace 的 seq=13→25/93＝LOCK_HELD 跳锁轮（历 1-2 秒），与主区 `backup_skipped_*` 累计 39 份一致。裁定①的实证面因此再扩一条：不是"影子根偶尔来一发"，而是**当天所有真发射都来自影子根**。
- **本班两处自犯当场记档**：①第一轮 400/403 过滤用了前班的 `-Mode` 词形，得到"零行"后差点写成"27300 不走 legacy 通道"——停手后先做"同窗原始 400/403＝65 条 vs 过滤后＝0 条"的对拍，才定位到过滤词与出生形态不匹配（**查无先问尺，别先问世界**）。②把重定向文件 mtime 当"内容时刻"用之前没验，补了合成件（写一行→睡 40 秒→两次取样）才敢用它给 4 小时定界；这条若不测，本案会被写成"13:5x 就死了、之后 4 小时是僵尸"的完全相反形态。
- **零面声明（本段）**：本班杀停进程 0（两轮处置闸均无 ACTION；本案定名后不再需要处置）｜`G:\backup` 内容零写（db_dumps/vault 读数全为 stat 与目录列表，写入者是备份链自身）｜他人件零改动（三份影子根副本只做行序取证）｜判据·阈值·门禁码·注册表·备份任务定义零改动｜CH 取数 0 次（CH 结论全部来自 ps1 自报＋报告 json）｜仪器零新起（未新建 27300 第二支监听；23048 随目标设计自退）｜压缩器 38464 与其 journal/ALARM 零碰（尾行仍 `COMPRESS2_END 17:31:24`）。
- **落地面**：第五袋重生已落 **92b69f0178**（20:16:49，5 件 +318/-11：reconciler ①②＋config `ch_backup.vm_name`＋测试 9 支＋账本第五/六段），HEAD 逐件实测 `run_subprocess_hidden` 3 处、`vm_name` 在位、失败骨架 `"rows"` 为 dict 字面量；死袋 q-0005（我全局 replace 误伤既有第 107 行→PROJECT_ROOT 进 diff）与 q-0006（裸 `subprocess.run` 撞 BARE-SUBPROCESS）均未复投；主区 index 里那枚 `1de1c216e6^` 旧 backup.ps1 快照已刷回 HEAD 字节（雷除，blob `c1b58ec4...` 永久可取）。整目录 **136 passed**，ruff check/format 全清。
- **候 Owner 裁（累计十三件，本班不自决）**：原十一件照旧（⑧任务腿互斥缺口／⑨车道根 pre-T1 副本／⑩E-4 调用先于定义的死码／⑪65 分钟点火空窗…）；新增⑫**dumps 轮转闸的自指次序**（永远拿上一轮的 CH 结论判本轮；取向＝把轮转判据改读本轮内存变量，或让位于 Stage 4 之后——属判据/流程面，本班不动）；新增⑬**403 尺排他面收紧是否入在册工法**（"有 403"只洗清强杀型他杀，不洗清优雅关闭型；若要仪器化，需在死窗内同时采集不带 /F 的 taskkill 形态）。另把 20261010 空 dump 目录的**不可回造性**放在明面：若 Owner 要 10-10 的库快照，唯一诚实通道是别的既有副本，不是重跑。
- **复核命令**：`grep -c "" .runtime/tmp/bf3_case17_evidence_403.txt`（应 325）；`cat .runtime/tmp/bf3_case17_census.txt`（13 个真发射 runspace 全为影子根）；`cat .runtime/tmp/bf3_wps_retention.txt`（OLDEST 16:49:24／NEWEST 20:49:37／COUNT 12440）；`tail -8 logs/backup_runlog_20261011_194841.log`（应见 `Report saved`→`Backup completed in 5165.4s`→`RELEASE_LOCK pid=40008`）；`ls -1 logs/backup_report_20261011_*.json | wc -l`（应 1＝破零）；`python -c "import json,io;d=json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'));print(d['last_backup_status'],d['last_ch_backup_status'],d['last_backup_time'])"`（应 ok ok 2026-10-11T21:14:46...）；`ls -1 /g/backup/db_dumps/20261011 | wc -l`（应 4）与 `ls -1 /g/backup/db_dumps/20261010 | wc -l`（应 0）；`git rev-parse :scripts/backup/backup.ps1 HEAD:scripts/backup/backup.ps1`（两行应相同）；`powershell -NoProfile -ExecutionPolicy Bypass -File .runtime/tmp/bf3_mtime_probe.ps1`（AT_6s 与 AFTER_EXIT 的 mtime 应相同＝mtime 不随关闭推进）；`git log -1 --format=%h -- scripts/backup/backup_reconciler.py`（应 92b69f0178）。
- **回退令（逐件）**：账本＝`git checkout HEAD~1 -- docs/_working/backfix_campaign/00_ledger.md`（本段纯追加，回退不伤他人条目）；①②与 rows 的回退指针在第六段。证据件均在 `.runtime\tmp\`（未入库），停用＝删本目录内 `bf3_case17_*` 与 `bf3_*probe*.ps1` 即可，不影响任何生产链。
- **署名**：adjudicator=st-backfix3-20261011（收口轮：案 #17 定名＋403 尺标价收紧＋pre-T1 假绿实锤＋裁定③自产达成＋两日首次完整收卷＋第五袋落地核账）。


### 第七段读数更正（三处数字级自纠）＋403 记录本身不带命令名（st-backfix3-20261011 22:0x 复核轮）

- **更正一（"真发射 runspace 共 13 个"→7 个真发射＋6 个装载器）**：分组判据是"HostApplication 里出现 `-File ...backup.ps1`"，而 **装载器**（P-7 的瞬发 `powershell -Command "$null = Start-Process ... -ArgumentList '-File <root>...backup.ps1' ..."`）的命令串里同样含这一段 ⇒ 13 个分组＝7 个真备份进程＋6 个装载器。逐一对表（真发射）＝f7faad63（27300，13:48:30→17:51:19，QW/worktree）、e63ced9e（13080，17:52:35→18:40:33，WT/st-datalane-20261010）、bf0022da（40008，19:48:41→完成，QW/worktree）、0673f84f/0ca37481/8d091323/f15a2111（四发跳锁短退，seq 13→93，历 1-2 秒）；装载器＝6e93695d/bcbefd26/d76c5f27/1a1cba3b/97f17973/693d73fc（seq 13→25，历 0-1 秒）。**结论不变**：当天 7 次真发射仍全部来自影子根，主区零发。写数的人（本班）当时把分组数当成了发射数——这正是"计数禁拿抽样当全集"的另一面：判据命中数≠对象数，装载器与真身共享同一段特征串。
- **更正二（"全 38 行"→53 行）**：`logs/backup_runlog_20261011_194841.log` 实测 `grep -c ""` ＝**53 行**（本班按屏读估了 38）。其余读数逐件复测仍成立：runlog 今日 **10 支**（14:32:51/14:54:13/15:02:46/15:11:09/15:52:11/17:19:05/17:36:03/17:43:55/18:38:36/19:48:41）、`backup_skipped_20261011_*.json` **39 份**、报告 **1 份**、`G:/backup/db_dumps/20261011` **4 件**／`20261010` **0 件**、压缩 journal 尾 `COMPRESS2_END 17:31:24 / G_free_GB=2531.4`（pid 38464 已自退，不在进程表）。
- **更正三（Operational 覆盖面：从"死窗 4 分钟"扩到"整个下午"）**：按 27300 的 HostId=**01356c8b-6410-4200-a2df-e32db38e0d4c** 与 RunspaceId=f7faad63 双特征串重扫 `Microsoft-Windows-PowerShell/Operational` 的 [13:00, 18:30] 全窗＝**2775 条事件、零条属该主机**（窗内 id 普查：40961=948／53504=786／40962=779／4100=131／4104=81，全是别的主机）。⇒ 上一段那句"105 条中无一条属该主机"低估了覆盖面：不是"那 4 分钟没记到"，而是**整条下午这个主机的作业在 Operational 里完全没有痕迹**。
- **为什么 403 定不了"停在哪一句"（原文字段级实证，冻结件在册）**：那条 403 的完整字段只有 `HostName=ConsoleHost / HostVersion=5.1.26100.6899 / HostId=01356c8b… / HostApplication=<发射原行> / EngineVersion=5.1.26100.6899 / RunspaceId=f7faad63… / SequenceNumber=280890`，而 **PipelineId／CommandName／CommandType／ScriptName／CommandPath／CommandLine 六个字段全为空**。⇒ 403 能证明"关停自引擎内部发起"（他杀之强杀型被排除）与"哪台主机哪个 runspace"，**结构上不可能**指出停在哪个命令上；要那一层必须采栈（procdump 类仍不存在）或开 Analytic 通道（仍关）。这条给⑬号候裁提供了具体形状：若要把"停在哪句"变成可判据，需要的是新的观测通道，不是更细的事件查询。
- **本班仪器在岗复测（22:0x，逐 pid 实测）**：standing trap 57376／PPID 陷阱 43560／event-watch 57184／atime 差分 57008／诱饵 v1 17224＋v2 23588 及各自监听 49396/53928 **全 ALIVE**；handle 哨现由 **pid=33880**（powershell，born 14:36:52＝T4 改后重启的那支）承载，末三拍 `21:41:21 poll#510 / 21:48:51 poll#520 / 21:59:04 poll#530` 全 clean——**实测节奏约 45-60 秒/拍**（10 拍心跳间隔 6.8-10.2 分钟），仍弱于设计的 20 秒：单次 handle64 枚举本身耗时 25-40 秒，把 sleep 之外的余量吃光。本班不"顺手改"成并发枚举（那会新起一支读 G 盘的仪器，属仪器面扩权），只把"设计 20s／实测 50s"这条差再次入册。46444 是 10-11 早先那支的旧 pid，已被 33880 取代，非战损。
- **零面声明（本段）**：本班杀停进程 0｜`G:\backup` 内容零写｜他人件零改动｜判据·阈值·门禁码·注册表零改动｜CH 取数 0 次（CH 面结论只来自 ps1 自报＋报告 json）｜仪器零新起（handle 哨读数取自其自志，未新挂探针）｜压缩器与其 journal/ALARM 零碰。
- **复核命令**：`grep -c "" logs/backup_runlog_20261011_194841.log`（应 53）；`ls -1 logs/backup_runlog_20261011_*.log | wc -l`（应 10）；`ls -1 logs/backup_skipped_20261011_*.json | wc -l`（应 39）；`cat .runtime/tmp/bf3_case17_census.txt`（13 分组＝7 真发射＋6 装载器，逐一对表见上）；`powershell -NoProfile -ExecutionPolicy Bypass -File .runtime/tmp/bf3_oper_host.ps1`（应 HOST_OR_RUNSPACE_HITS=0／DAY_WINDOW_EVENTS=2775）；`awk '/^T=2026-10-11 17:51/,/^===/' .runtime/tmp/bf3_case17_evidence_403.txt`（应见六个空字段）；`tail -3 .runtime/tmp/backfix_handle_poll.log`（应 ps-poll 心跳 clean）；`powershell -NoProfile -ExecutionPolicy Bypass -File .runtime/tmp/bf3_pid_probe.ps1`（应 HANDLE_POLL pid=33880 在列）。
- **署名**：adjudicator=st-backfix3-20261011（复核轮：第七段三处读数自纠＋403 字段结构标价＋仪器在岗同分钟复测）。


### 今晚破零的那一发不是自报绿：system.backup_log 交叉核验到手（本班本役首次经单口读 CH，如实申报）（st-backfix3-20261011 22:1x 复核轮）

- **为什么必须补这一刀**：前段收卷的所有 CH 数字（76.9 GiB／1,010,694 files／225 tables／verified=True）都来自 **backup.ps1 自报**＋报告 json，而本战役 INV-11 那条假绿闸存在的理由就是"自报≠实证"。本班不去手算第二把尺，直接调**既有单口** `backup_reconciler.query_backup_log_created()`（SQL 集中在件内 `_SQL_BACKUP_LOG_CREATED_PROBE`，判别列＝`status='BACKUP_CREATED'`，CH 26.6 实测 schema，fail-closed 语义原样），只读一次 HTTP 探针。
- **实测结果＝真绿，两尺互咬**：`{'ok': True, 'count': 1, 'max_event_time': '2026-10-11 12:49:14', 'error': None}`，起算点 since_utc＝2026-10-11 **11:48:00 UTC**（＝本地 19:48 起跑，本班按件内约定传带时区的 UTC，禁 naive）。⇒ 权威表里恰有 **1 条** BACKUP_CREATED，时刻 **12:49:14 UTC＝本地 20:49:14**，与 ps1 打出 `[OK] ClickHouse dump (incremental): ok` 的 **20:49:39** 相差 25 秒（CH 侧先落表、脚本后收 stdout，方向正确）。当窗条数＝1 而非 0＝**假绿闸不会把它降级成 ch_log_missing**。
- **对照面（顺手把"哪条腿断过"钉准）**：把起算点放宽到 2026-10-09 00:00 UTC ⇒ `count=28`、`max_event_time` 仍是今晚那条 12:49:14。⇒ **CH 腿在这两天一直是成功的**（28 条 BACKUP_CREATED），断供从来不在 CH，而在 **db_dumps 腿（E-4 守卫先调后定义⇒robocopy 从未跑）＋ Stage 4 的报告与 state 回写**。这与 G 盘面实测一致：`db_dumps/20261010=0 件`、`20261011=4 件（今晚自产）`。今后谁再说"CH 备份挂了两天"就是口径错，本班按两把尺钉死这个区分。
- **零面改口（不遮掩）**：本段之前各段本班写的"`CH 取数 0 次`"在本轮**不再成立**——本班做了 **1 次只读 HTTP 探针（经既有单口，无 SQL 散落、无写面、无 DDL）**，另加 1 次同函数的宽窗对照（同一条 SELECT 的另一个时间字面量）。零写、零 OPTIMIZE、零表操作。若 Owner 认为值守班连只读核验都不该做，回退＝删除本段即可，核验结论不进入任何判据面。
- **待办交接（不扩权）**：`backup_state.json` 里 `log_verified` 仍为 None、`last_ignite_log` 已被清空 ⇒ 链上的延后验核（settle_previous_ignition→`_adjudicate_completed_run`）**不会**替今晚这发补写权威裁决（它按 pending 指针工作，而指针已在 18:38 那轮 lock-skip 时被清）。本班不自造指针、不改 reconciler 语义（那是判据面），只把"今晚这发的交叉核验由本班手工完成、链上未留痕"这条差呈清。
- **复核命令**：`PYTHONPATH=src python -c "import importlib.util as u;from datetime import datetime,timezone;s=u.spec_from_file_location('b','scripts/backup/backup_reconciler.py');m=u.module_from_spec(s);s.loader.exec_module(m);print(m.query_backup_log_created(datetime(2026,10,11,11,48,0,tzinfo=timezone.utc)))"`（应 ok=True count=1 max=2026-10-11 12:49:14）；同函数传 `datetime(2026,10,9,0,0,0,tzinfo=timezone.utc)` 应 count=28；`grep -n "SQL_BACKUP_LOG_CREATED_PROBE" scripts/backup/backup_reconciler.py`（应见集中定义＋唯一消费点）；`ls -l data/databases/backup_state.json`（mtime 仍 21:14:46＝本班未写 state）。
- **署名**：adjudicator=st-backfix3-20261011（复核轮·第二刀：INV-11 假绿闸对今晚首破零轮的实测核验＋"CH 腿从未断"的口径钉正）。


### 令5 观察项核账：rotation 状态位＋①已在真机运行面就位＋今晚这发的链上留痕差额＋vhdx 知会复测（st-backfix3-20261011 22:0x-22:1x 值守轮，零新施工）

- **观察项一（21:01:45 那句 rotation WARN 与 20:49:39 的 verified=True 并不矛盾，根因＝次序自指）**：判据原文（HEAD 现字节）＝`$dumpsStateOk = ([string]$sJson.last_ch_backup_status -eq "ok")`，读的是 **`$StateFile` 磁盘上的旧字节**，而该文件的本轮写回点在 **Stage 4**（runlog 实测顺序：`DB dumps snapshot done` 21:01:45 → `Stage 4: Report` 21:14:46，同一轮内相差 13 分 01 秒）。⇒ 轮转腿在本轮**结构上不可能**看到本轮的 CH ok，它看到的是**上一轮**留下的值。两把尺互咬的正证：state 册现在的写回时刻全部＝21:14:46.8xx（`last_ch_backup_status=ok`/`last_ch_backup_verified=True`），而轮腿在 21:01:45 就已判定。
- **诚实标价一处不可复核（别把两种成因混成一个）**：21:01:45 那一刻磁盘上 `last_ch_backup_status` 的**具体旧值**已无法回读——`backup_state.json` 在 07-19 就 untrack（末次入库=56005c87793），无 git 历史、无影子副本可对拍。所以"WARN 是因为旧值非 ok"与"WARN 是因为 `catch` 兜底成 `$false`（解析失败）"**今天无法区分**，因为 catch 支不留任何痕。⇒ 真正的缺口是**轮转腿没把"读到的状态位值"写进日志**（一行的事），属可观测性面而非判据面，本班不动码、登记候裁（并入⑫）。
- **明早的可证伪预测（下一轮值守照此核，一眼即可）**：既然 state 册已被今晚写成 `last_ch_backup_status=ok`，**下一发的轮转腿应当改判为轮换并打印 `DB dumps rotation: removed N old snapshot(s)`**（N≥1；`db_dumps` 现有 20261008/09/10/11 四个日目录）。复核：`grep -n "rotation" logs/backup_runlog_<下一发时刻>.log`。若仍见 `rotation skipped` ⇒ 说明①读取失败在复发（catch 支）或②状态位被别的写者回退，两种都要当场取字节。**这条预测是本轮观察项的全部价值所在：把"我推断次序自指"变成"现实会被打脸或兑现"。**
- **观察项二（①从"落进 HEAD"变成"在真机运行面就位"——A/B/C 未决的时间窗因此开始倒计时）**：逐根实测 `is_shadow_checkout` 命中数与副本 mtime＝`.runtime/commit_queue/worktree`（mtime **21:55**，3 命中）、`.runtime/commit_queue/worktrees/w0`（mtime **21:58**，3 命中）、`.worktrees/st-datalane-20261010`（mtime 10-10 17:08，**0 命中**＝仍落后）。⇒ 本班 20:16:49 那袋已被序列化物化追平：**从下一次事件点火起，①会在真机上拒绝这两个车道根的点火**（22:08 全根逐条复测：主区 False、其余五根含 `.worktrees/`+`.aidrafts/` 全 True）。当前唯一的实际抑制源仍是 cadence（`min_interval` 8h，今晚 21:14:46 起跑⇒约 05:14 后解禁）。**呈请**：Owner 令5 未回 A/B/C，本班按字面不自改判据，只把"这个选择将在 05:14 之后第一次产生现实后果"标成时刻；事件腿被关后，日常备份只剩 06:00 计划任务一发。
- **观察项三（今晚这发的链上留痕差额，字段级）**：state 册 `last_backup_log_verified = **False**`、`last_ignite_log` 已空、`last_run_outcome` 仍停在 10-10 的 `lock_skipped`（`last_lock_skip_time=2026-10-10T14:58:40Z`）⇒ **INV-11 的延后验核不会替今晚补写**（它按 pending 指针工作，而指针在 18:38 那轮 lock-skip 时被清）。本班手工经既有单口测得的 `count=1 / max_event_time=2026-10-11 12:49:14` 因此**只存在于账本，不在链上状态**。本班不自造指针、不改 reconciler 语义（判据面）；若 Owner 要链上也留痕，最小动作＝把"日检"腿指到今晚的 ignite 日志一次，属派工不属自扩。
- **知会项复测（vhdx 生长序列，非本班动作）**：`data/audit-trail/vhdx_growth_series.jsonl` 现值＝磁盘在、**428 字节／2 行**、mtime **10-11 21:37:17**（＝总统筹复位之后），`git status` 对该件**零标记**（与 HEAD 一致，未再进暂存池）⇒ 复位未被本班任何袋二次触发（本班两袋 files 清单均只含账本 1 件）。同目录另有两枚**他人件**：`rolling_archive_plan_shadow.jsonl` 呈 ` M`（他人工作区改动）、`ti_row_versions_series.jsonl` 呈 `??`（未跟踪新件）——**本班不碰、不代 add、不代裁**，只登记存在。末次触该件的他袋＝4cc45d7f07e（10-11 07:52，维护二班治理面袋）。
- **零面声明（本段）**：本班零新施工（按令5）｜进程杀停 0｜`G:\backup` 内容零写｜他人件零改动（含上面两枚 audit-trail 件）｜判据·阈值·门禁码·注册表·备份任务定义零改动｜CH 取数＝本段 0 次（上段那次已如实申报）｜仪器零新起｜压缩器与其 journal/ALARM 零碰。
- **复核命令**：`grep -n "dumpsStateOk" scripts/backup/backup.ps1`（应见读 state 的两行＋catch 兜底）；`tail -3 logs/backup_runlog_20261011_194841.log`（应见 Stage 4 在 DB dumps 腿之后）；`python -c "import json,io;d=json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'));print(d['last_ch_backup_status'],d['last_ch_backup_verified'],d['last_backup_log_verified'],d['last_run_outcome'])"`（应 ok True False lock_skipped）；`git log -1 --format=%h -- data/databases/backup_state.json`（应 56005c87793＝已 untrack，旧值不可回读的根据）；`grep -c is_shadow_checkout .runtime/commit_queue/worktree/scripts/backup/backup_reconciler.py .runtime/commit_queue/worktrees/w0/scripts/backup/backup_reconciler.py .worktrees/st-datalane-20261010/scripts/backup/backup_reconciler.py`（应 3／3／0）；`ls -l data/audit-trail/vhdx_growth_series.jsonl`（应 428 字节、mtime 21:37:17）；`git status --porcelain data/audit-trail/`（vhdx 件应不在列，另两枚他人件在列）。
- **署名**：adjudicator=st-backfix3-20261011（令5 值守轮：观察项逐条核账＋明早可证伪预测＋①真机就位时刻登记＋知会项复测；零新施工）。


### 处置闸第三跑＝NATURAL_EXIT（本班未动手）＋今晚样本的原生错误面首次清点＋valve1=None 已钉到"车道根取数"这条腿（st-backfix3-20261011 22:2x 值守轮，零新施工）

- **闸跑逐字读数（22:26:00，本班本役第一跑）**：`VERDICT: NATURAL_EXIT_not_our_action`，**无 `ACTION:` 行**（自然收尾这条路径本来就不动作）。因子面＝`close_status='CLOSED'`／`close_detail='2026-10-11 17:31:24 | PROBE 1 ~  ~ '`／`close_ts='2026-10-11 17:30:38'`／`relief_elapsed_min=295.4`／`target_alive='DEAD'`。证据件 `.runtime/tmp/bf3_dispose_evidence.md`（566 字节，mtime 22:26）。27300 的死因定名与 403 尺标价第七段已结，本段不重复；本班杀停进程数＝0。
- **三面读数（同分钟实测，全部只读）**：`.runtime/backup.lock` **不存在**（锁已释）｜今日报告 json **1** 份（`logs/backup_report_20261011_194841.json`）｜最新 runlog 末行 `RELEASE_LOCK | pid=40008`｜压缩 journal 尾两行 `G_free_GB=2531.4` ＋ `COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`｜27300 监听尾行 `17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`。
- **新事实一（今晚样本的"原生错误面"第一次被点清；账本此前对 TerminatingError 零命中）**：`logs/backup_transcript_20261011_194841.log` 实测 97 行／96 非空／7533 字节，而今天另外 9 份 transcript 全是 909-913 字节／23 非空行——**只有这一发是跑到底的那发**。其中 `PS>TerminatingError()` **12 条**，两类：①`CopyTo`「另一个程序已锁定文件的一部分」2 条，对象 `data\runtime\dwm_shard_state_supplementary2_20261011\tilib_dwm_runner_instance.lock`；②`.ctor`「未能找到路径…的一部分」10 条＝5 个 `.ailocks` 下 `owner.json` 各 2 次：`tests.meta.scripts.backup.test_backup_reconciler.py.lock`／`docs._working.backfix_campaign.00_ledger.md.lock`／`scripts.backup.restore_drill.py.lock`／`scripts.backup.backup_reconciler.py.lock`／`scripts.backup.backup_config.yaml.lock`。**为什么值得记**：runlog 侧对这些只留了一句 `WARN Source vanished mid-run`，异常原文与调用面只有 transcript 有 ⇒ T1 的 transcript 腿自 14:32 上线以来第一次产出 runlog 没有的信息，T1 的价值由此拿到实证，不必再靠推断。附带一条呈批观察：G 盘代码镜像把 `.ailocks`（会话锁目录）也纳入了采集面，而其中 `docs._working.backfix_campaign.00_ledger.md.lock` 正是本战役自己的账本锁——备份链在镜像他会话的在途锁，锁被并发 release 就产生这 10 条异常（"vanished" 是并发释放的正常结果，不是数据损坏）。**是否把 `.ailocks` 排除出镜像面属判据面，本班不动码，登记候裁（可并⑫族）**。
- **新事实二（Stage 4b 那句 `valve1: SKIP: last_ch_backup_status=None` 的取数口径钉准；两种解释只剩一种，但本班不下裁定）**：判据链逐点实测——`scripts/ch/rolling_archive_reconciler.py:117` 读 `BACKUP_STATE_FILE`，`:67` 把它锚在 `PROJECT_ROOT`；`PROJECT_ROOT = REPO_ROOT`（`src/zephyr/shared/io/paths.py:200`），`REPO_ROOT = find_repo_root()`（:97），该函数**优先**采信环境变量 `ZEPHYR_WORKTREE_ROOT`（:84-87，命中且含 `src/zephyr/__init__.py` 即直接返回）。发射侧 `scripts/backup/backup.ps1:31` 把 `$ProjectRoot` 钉死为 `D:\ZephyrAlpha`，`:1286` 由此拼出 hook 脚本路径。磁盘侧同分钟实测：主区 `data/databases/backup_state.json` mtime 21:14:46.87，内含 `last_backup_status=ok` ＋ `last_ch_backup_status=ok`；ignite 镜像 stdout 顺序＝`Report saved` → `State saved`（主区）→ `Stage 4b`。⇒ **若 hook 读主区册，valve1 结构上不可能打印 None**。与之同形的唯一候选＝车道根影子册 `.runtime/commit_queue/worktree/data/databases/backup_state.json`：它有 `last_backup_status=ok` 而**无任何 ch 键**，读它必得 `last_ch_backup_status=None`（判据顺序 :121-123 先 status 后 ch，36h 年龄检查因此从未跑到）。旁证（该文件自证，非本班推测）：影子册 mtime **21:58:23.848** 与册内 `last_shadow_refuse_time=2026-10-11T13:58:23.842Z`（+8h＝本地 21:58:23）对齐到毫秒级，同册 `last_run_outcome=shadow_ignite_refused`／`last_shadow_refuse_reason=linked_worktree_dotgit_file`／`last_shadow_refuse_root=D:\ZephyrAlpha\.runtime\commit_queue\worktree` ⇒ 21:58 那一发 reconciler **确实把状态写进了车道根的同名册**，即"python 子进程解析到车道根"这条腿在真机上是活的。本班不改 env、不改判据、不动路径解析（判据面，且⑫号候裁已在册）。
- **明早的一眼判别（留给下一轮值守，本班不自证）**：下一发跑完后看它 ignite 镜像里 `[rolling-archive] valve1` 打什么——打 `PASS: backup ok(含 CH)` ⇒ 读的是主区、当晚 None 另有瞬时成因；仍打 `SKIP: last_ch_backup_status=None` 而主区册此刻为 ok ⇒ 车道根取数实锤。**这条预测能被现实打脸，是本段的全部价值所在**。
- **仪器在岗复测（22:2x，逐 pid 对全量进程表 410 行实测，非抽样）**：三陷阱 57376／43560／57184、atime 57008、handle 哨 33880、诱饵 17224／23588 及各自监听 49396／53928 **全 ALIVE**；38464 与 23048 **不在表**——前者与 journal 尾行 `COMPRESS2_END 17:31:24` 相合、后者与监听日志尾行 `MONITOR_EXIT_ON_TARGET_DEATH 17:51:20` 相合，**都是按设计自退，非战损**；landing watcher 38568 亦不在表，本班手上无其自退凭据，**只登记缺席、按卡不重复起**。
- **零面声明（本段）**：进程杀停 0（闸判自然收尾）｜`G:\backup` 内容零写｜他人件零改动｜判据·阈值·门禁码·注册表·备份任务定义零改动｜CH 取数 0 次（本段只用文件字节与既有 stdout）｜仪器零新起（未新建同 pid 同日志的第二支监听）｜压缩器 38464 与其 journal/ALARM 零碰｜`.runtime/commit_queue` 的 blobs 零碰（只读其 `logs/` 与 `data/databases/` 既有件）。
- **复核命令**：`tail -3 .runtime/tmp/bf3_dispose_evidence.md`（应见 `target_alive = 'DEAD'`）｜`grep -c "PS>TerminatingError" logs/backup_transcript_20261011_194841.log`（应 12）｜`grep -oE "\.ailocks[^”]*owner\.json" logs/backup_transcript_20261011_194841.log | sort -u | wc -l`（应 5）｜`ls -l --time-style=full-iso data/databases/backup_state.json .runtime/commit_queue/worktree/data/databases/backup_state.json`（应 21:14:46.87／21:58:23.84）｜`grep -n "ZEPHYR_WORKTREE_ROOT" src/zephyr/shared/io/paths.py`（应见 :84 优先支）｜`grep -n "BACKUP_STATE_FILE = " scripts/ch/rolling_archive_reconciler.py`（应 :67）｜`grep -n "ProjectRoot =" scripts/backup/backup.ps1`（应 :31 钉死主区）。
- **待落地**：本段只写盘、未提交——本班授权面不含提交，且主区 index 是多会话混合池，裸 commit 会造成归属篡改。要入册请派队列正门，files 清单只含本账本 1 件。
- **署名**：adjudicator=st-backfix3-20261011（值守轮·处置闸本役第一跑：NATURAL_EXIT 记录＋transcript 原生错误面首次清点＋valve1=None 取数口径钉到车道根＋仪器在岗逐 pid 复测；零新施工）。


### 批复二/三执行账：点火执行体改指主检出点＋⑫轮转读值入日志＋一次性把今晚实况补进权威状态册（st-backfix3-20261011 22:2x-22:4x 施工轮）

- **批复二（执行体指向）＝判据面零改的正解，已落**：新增 `primary_checkout_root()`——用 `git -C <自身根> rev-parse --path-format=absolute --git-common-dir` 把"该点哪一份 backup.ps1"解析回**主检出点**；`reconcile()` 的三处随之改：脚本路径＝目标根、①的入参＝**目标根**（不再是进程自身根）、`launch_detached_backup(..., root=目标根)`（cwd 与 -WorkingDirectory 同指主区）。**裁定①的闸体一字未动**（`is_shadow_checkout` 源码零改），**未加白名单、未新开豁免**——改的只是"喂给闸的是哪一根"。子进程仍走 `run_subprocess_hidden`（trae_067），新增常数 `PRIMARY_ROOT_PROBE_TIMEOUT_S = 20` 是探针资源界，非判据阈值。
- **fail-closed 边界（最要紧的一条设计取舍，写成测试钉住）**：解析不成（无 git／超时／common-dir 指回的根里没有 `scripts/backup/backup.ps1`）⇒ 退回自身根；**退回后若那是影子根，①照旧拒**。取向明写：宁可事件腿停摆，也不让多版本副本共抢同一把生产锁——那正是本役的病根，不能为了"腿活"把它放回来。
- **新测 5＋1 支，红证先行**：`TestPrimaryIgnitionTarget` 5 支（common-dir 解析／超时退回／主区无脚本退回／端到端"进程在车道里跑而点的是主区那份且记 last_ignite_target_root"／目标本身是影子根时仍拒且留痕记的是目标根）＋`test_backup_ps_scripts.py` 1 支结构测（⑫）。**红证已做**：把同一套判据打在 HEAD 那份未改字节上——`primary_checkout_root` 不存在（hasattr=False）、读值占位串不存在、旧那句不可归因的 WARN 仍在 ⇒ 守卫不是空跑。落地后整目录 **142 passed**（前值 136，+6），`ruff check`/`format` 全清，`.ps1` 复测非 ASCII 字节 **0**、PS Parser 冒烟 PARSE_OK。
- **既有测试的适配如实交代（没弱化任何一条）**：批复二给点火链新增了一次 git 探针，而 5 处旧测用 `patch.object(subprocess, "run", 计数假件)` 断言"起没起子进程／起了几发"——探针会被同一个假件计进 `captured`，于是 `assert captured == []`／`len(...) == 1` 这类**核心断言会被我的新接缝撑坏**。处置＝把这 5 处的执行体指向钉成其原语义（`patch primary_checkout_root → 自身根`），断言一字未改、一字未松；另有 1 处（`test_live_holder_...`）钉完仍验"零子进程"，可见锁自查仍在①之后之前有效。测后按 AST 逐类数过方法数（TestDeferredVerification 20／TestSingleCheckoutPoint 5／TestVmOffYield 6／TestPrimaryIgnitionTarget 6）——防上一次"测试被挤进邻类"那种事故重演。
- **⑫（轮转读值入日志）＝批，已落**：轮转腿现在把**读到的状态位值**打进两条出口消息（`state last_ch_backup_status=<值>`），并在 try 前先置占位 `<unreadable>`，于是明早那句 WARN 若再出现，可当场分清"旧值非 ok"还是"读失败被 catch 兜成 false"（这正是上一段标价的不可归因面）。**判据、阈值、轮转本体一字未改**：比较式仍是 `$dumpsStateOk = ($dumpsStateRead -eq "ok")`，新测把这句也钉住了（防日后有人把"可观测性改动"做成"顺手改判据"）。影子制适用性如实标价：本改属消息文本面（不动流水线分支），按统筹批复三"一行"直接落，未另开影子轮；回退指针见下。
- **一次性补结算＝批，已跑（既有单口，零语义改动）**：把待结算指针指向今晚那一发（`last_ignite_log=.runtime/commit_queue/worktree/logs/backup_reconciler_ignite_20261011_114840.log`、`last_backup_launch_time=2026-10-11T11:48:40+00:00`），再调 **既有** `settle_previous_ignition()` ⇒ 走 "State saved:" 锚定主仓 state 的正支，裁决 `action=auto_committed / backup ok (clickhouse=ok, backup_log verified, rows=1)`。权威状态册现值：**`last_run_outcome=backed_up`**、`last_backup_status=ok`、`last_backup_log_verified=True`、`last_backup_log_count=1`、`last_backup_log_max_event_time=2026-10-11 12:49:14`、`last_ch_backup_status=ok`、`last_ch_backup_verified=True`、`last_ignite_log=None`（指针已清，不会重复结算）。史上首个完整轮不再在状态册里留成 10-10 的 `lock_skipped`。
- **这次授权写盘的两处副作用（先报再走，不藏）**：①`last_backup_time` 被结算函数按其自身语义写成**裁决时刻**（22:37 本地）而非该发真实收尾的 21:14:46 ⇒ 8h cadence 解禁点从"约 05:14"推到"约 06:37"，比原计划晚 83 分钟；本班不改函数语义（那是判据面），只登记这个位移。②`last_session_id` 由原先那发遗留的 `st-sim-launch-20260923` 变成本班 sid（裁决署名归属，方向正确）。可逆面：写盘前已快照原状态册字节到 `.runtime/tmp/bf3_state_before_settle_20261011.json`，逐键可对拍。**键集合差实测（禁按"值变化"粗判）**：新增 4 键（`last_backup_log_count`／`last_backup_log_max_event_time`／`last_ignite_log`／`last_backup_launch_time`），**删除 0 键**，值变化 4 键（`last_run_outcome`／`last_backup_time`／`last_session_id`／`last_backup_log_verified`）⇒ 本次写盘是纯增补，没有抹掉任何既有字段。
- **升级线照令登记为可核对条件**：事件腿**连续被拒 >48h 且期间无一次豁免通过记录** ⇒ 呈报 Owner 定性"覆盖面缺口"。批复二落地后这条的判据面＝状态册是否出现 `shadow_ignite_refused` 且 `last_ignite_target_reason` 非 `git_common_dir`；下一发（约 06:37 后）就是第一个真机样本，本班会在场核。
- **零面声明（本段）**：判据·阈值·门禁码·注册表·备份任务定义零改动（⑫＝消息文本面，批复二＝路径指向面）｜①闸体与②探针源码零改（仅入参来源变更）｜未用 noqa 绕门｜未加白名单｜进程杀停 0｜`G:\backup` 内容零写｜他人件零改动｜CH 取数＝经既有单口 1 次（同一函数在裁决内自动复查，非散写 SQL）｜仪器零新起。
- **回退令（逐件，可单独否决）**：`git checkout HEAD~1 -- scripts/backup/backup_reconciler.py scripts/backup/backup.ps1 tests/meta/scripts/backup/test_backup_reconciler.py tests/meta/scripts/backup/test_backup_ps_scripts.py`；状态册＝用 `.runtime/tmp/bf3_state_before_settle_20261011.json` 逐键回填（该文件是写盘前的原字节）。
- **复核命令**：`PYTHONPATH=src python -m pytest tests/meta/scripts/backup/ -q`（应 **142 passed**）；`python -m ruff format --check scripts/backup/backup_reconciler.py tests/meta/scripts/backup/`；`grep -n "primary_checkout_root" scripts/backup/backup_reconciler.py`（应见定义处＋reconcile 内三处引用）；`grep -n "is_shadow_checkout" scripts/backup/backup_reconciler.py`（闸体行号与 HEAD 一致，证明未改闸）；`grep -n "dumpsStateRead" scripts/backup/backup.ps1`（应 4 处：占位／取值／两条出口消息）；`python -c "import json,io;d=json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'));print(d['last_run_outcome'],d['last_backup_log_verified'],d['last_backup_log_count'],d['last_backup_log_max_event_time'])"`（应 backed_up True 1 2026-10-11 12:49:14）；`ls -l data/databases/backup_state.json`（mtime＝22:37）；`diff <(python -c "import json,io;print(sorted(json.load(io.open(r'.runtime/tmp/bf3_state_before_settle_20261011.json',encoding='utf-8'))))") <(python -c "import json,io;print(sorted(json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'))))")`（应见**只增不减**：新增 4 键＝last_backup_log_count／last_backup_log_max_event_time／last_ignite_log／last_backup_launch_time，删除 0 键）；`python -c "import json,io;a=json.load(io.open(r'.runtime/tmp/bf3_state_before_settle_20261011.json',encoding='utf-8'));b=json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'));print(sorted(set(b)-set(a)),sorted(set(a)-set(b)),[k for k in set(a)&set(b) if a[k]!=b[k]])`（应 4／[]／4）。
- **署名**：adjudicator=st-backfix3-20261011（施工轮：批复二执行体指向＋⑫读值入日志＋一次性补结算，含红证与副作用呈报）。


### 批复二真机验证（三根实测解析＋闸对目标根放行）（st-backfix3-20261011 22:4x，落地袋 dce5ae9d2c 之后）

- **落地后立刻在真机上验"执行体指向"，不看测试看现实**：`primary_checkout_root()` 从主区解析＝`D:\ZephyrAlpha`＋`git_common_dir`；从三条车道根分别解析——`.runtime\commit_queue\worktree`、`.runtime\commit_queue\worktrees\w0`、`.worktrees\st-datalane-20261010`——**全部解析回 `D:\ZephyrAlpha`**，且对解析出的目标根再过 `is_shadow_checkout`＝一律 `(False, 'primary_or_unproven')`＝放行。
- **意义标价（这正是第五段那条"①在最关键的真机场景零拦截"缺口的补法）**：不是把闸放宽——闸体一字未动、无白名单、无新豁免——而是把**喂给闸的那个根**换成"真正要被执行的那一份脚本所在根"。车道里的 reconciler 从此点主区真源，事件腿保住；而"目标本身就是影子根则照旧拒"仍由 fail-closed 支＋第 5 支新测钉住：真机上要再现拒绝点火，必须是解析本身失败并退回影子根，那会在 state 册留下 `last_ignite_target_reason` 非 `git_common_dir` 的痕迹（可追，不静默）。
- **下一发就是判据样本（cadence 解禁点约 10-12 06:37；因补结算把 last_backup_time 写成裁决时刻而位移 83 分钟，位移本身已在批复执行账标价）**，届时核三件事：①主区新 runlog 的 `RUN_START` 行里 `script=` 是否等于主区那份 `scripts\backup\backup.ps1`（＝执行体真指主区的现场证据）；②state 册 `last_ignite_target_root`／`last_ignite_target_reason` 是否写成主区／git_common_dir；③⑫那句 `state last_ch_backup_status=<值>` 是否兑现明早的轮转预测（预期 `DB dumps rotation: removed N`，N≥1；若仍 skipped，新日志当场给出是"旧值非 ok"还是"读失败被 catch 兜底"）。
- **零面声明（本段）**：本段零写生产链文件（验证＝纯函数调用＋只读 git 探针）｜进程杀停 0｜CH 取数 0｜`G:\backup` 内容零写｜判据·阈值·门禁码·注册表零改动｜仪器零新起。
- **复核命令**：`PYTHONPATH=src python -c "import importlib.util as u,os;s=u.spec_from_file_location('b',os.path.abspath('scripts/backup/backup_reconciler.py'));m=u.module_from_spec(s);s.loader.exec_module(m);from pathlib import Path;print(m.primary_checkout_root(Path(r'D:\ZephyrAlpha')), m.is_shadow_checkout(m.primary_checkout_root(Path(r'D:\ZephyrAlpha\.worktrees\st-datalane-20261010'))[0]))"`（应 `(D:\ZephyrAlpha, 'git_common_dir')` 与 `(False, 'primary_or_unproven')`）；`git show HEAD:scripts/backup/backup_reconciler.py | grep -c primary_checkout_root`（应 3）；`git show HEAD:scripts/backup/backup.ps1 | grep -c dumpsStateRead`（应 5）。
- **署名**：adjudicator=st-backfix3-20261011（批复二真机验证段）。


### 处置闸第四跑＝NATURAL_EXIT（复跑幂等）＋本班主菜 194841 那发 53 行全文入册＋13080 死因定位到"先调后定义"＋值守期间批复二首发真机点火（script=主区）（st-backfix3-20261011 22:4x-23:0x 值守轮，零新施工）

- **闸跑逐字读数（22:45:59，本役第二跑）**：`VERDICT: NATURAL_EXIT_not_our_action`，**无 `ACTION:` 行**（自然收尾这条路径本来就不动作）。因子面＝`target_pid=27300`／`close_status='CLOSED'`／`close_detail='2026-10-11 17:31:24 | PROBE 1 ~  ~ '`／`close_ts='2026-10-11 17:30:38'`／`relief_elapsed_min=315.4`／`target_alive='DEAD'`。与 22:26 那一跑**同判**（唯一差＝relief 的分钟数）⇒ 复跑幂等成立，本班杀停进程数＝0。
- **证据件形态（仪器面一条，非本班动作）**：`.runtime/tmp/bf3_dispose_evidence.md` 两跑同为 **566 字节**、mtime 22:26:00→22:45:59 ⇒ 闸写证据件是**整覆非追加**，上一跑读数只有台账这一份留痕；本班不改它的写法（扩权）。
- **新事实一（本班从未进入"可处置判定"，且这是结构性的、不是运气）**：监听自志末三拍＝`17:50:49 cycle=619 cpu_total=36 cpu_d=1.2`／`17:51:04 cycle=620 cpu_total=37.1 cpu_d=1.1`／`17:51:19 TARGET_DEATH pid=27300`。G0 于 17:31:24 收口＋缓释 30 分＝窗到 **18:01:24**，死点落在 17:51:04～17:51:19 之间 ⇒ **G2..G5 在本役根本没有开跑的机会**（死前每拍还在吃 1.1-1.2 CPU 增量＝推进态，任一 VETO_progress_visible 若先命中也是否决处置）。附带一条口径：同拍 `lock=[LOCK_READ_SKIPPED(reader-audit)]` ⇒ 监听面从不读锁，凡"锁在不在/锁主是谁"只能取自 runlog 或闸探测。
- **新事实二（今日分类定数，写盘时现算）**：`logs/backup_runlog_20261011_*.log` 共 **11 支＝9 支跳锁（4 行／STAGE=0／末行 LOCK_HELD）＋2 支真起跑（含 LOCK_ACQUIRED，时刻 20261011_194841／20261011_225255）**；跳锁支的 `script=` 根＝`worktrees\w0` 三支（14:32:51／15:11:09／17:43:55）、`commit_queue\worktree` 六支。接班卡上"今日带日志的 5 发点火全是跳锁轮、第一份完整阶段日志仍未出现"这一条**已被现实推进并作废**——第一份完赛样本就是 19:48:41 那发（21:14:58 收尾，历 5165.4 秒），全文逐行零删入册如下。runlog 会被轮转/清账带走，这里是它在治理面的唯一全字节副本。

```text
# logs/backup_runlog_20261011_194841.log —— 53 行原字节（本班主菜·T1 首份完赛样本）
2026-10-11 19:48:41 | RUN_START | pid=40008 mode=all force=False script=D:\ZephyrAlpha\.runtime\commit_queue\worktree\scripts\backup\backup.ps1 root=D:\ZephyrAlpha
2026-10-11 19:48:41 | TRANSCRIPT_ON | D:\ZephyrAlpha\logs\backup_transcript_20261011_194841.log
2026-10-11 19:48:41 | LOCK_ACQUIRED | D:\ZephyrAlpha\.runtime\backup.lock
2026-10-11 19:48:41 | STAGE | Stage 1: Pre-check
2026-10-11 19:48:41 | OK | Target drive D: online
2026-10-11 19:48:41 | OK | Target drive F: online
2026-10-11 19:48:41 | OK | Target drive G: online
2026-10-11 19:48:41 | OK | robocopy found: C:\Windows\System32\Robocopy.exe
2026-10-11 19:48:41 | STAGE | Stage 2: Database dump + config sync
2026-10-11 19:49:24 | OK | PostgreSQL dump (public): 241.57MB
2026-10-11 19:49:24 | OK | PostgreSQL globals dump: ok
2026-10-11 19:50:03 | OK | SQLite dump: 2 databases
2026-10-11 19:50:03 | OK | PG config synced to config/system_configs/pg/
2026-10-11 19:50:15 | OK | CH config synced to config/system_configs/ch/
2026-10-11 19:50:16 | OK | Pre-backup manifest: 225 tables
2026-10-11 19:50:19 | STAGE | CH backup mode: incremental -- incremental (ratio 0.26)
2026-10-11 19:50:26 | OK | Removed previous file(s): inc.zip
2026-10-11 19:50:28 | OK | Self-heal: cleared stale *.zip.lock (if any)
2026-10-11 19:50:28 | STAGE | ClickHouse BACKUP (incremental) async id=4d32fe28-596d-438c-b7ec-0be7133bfb42
2026-10-11 20:49:39 | OK | ClickHouse dump (incremental): ok (76.9 GiB, 1010694 files, 225 tables, verified=True)
2026-10-11 20:49:39 | STAGE | ClickHouse dual-write sync (chbackup_local -> chbackup2)
2026-10-11 20:49:41 | OK | Dual-write sync ok: -rw-r----- 1 clickhouse clickhouse  82534136381 Oct 11 12:49 /mnt/chbackup2/inc.zip | -rw-r----- 1 clickhouse clickhouse 298968010737 Oct  3 00:31 /mnt/chbackup2/market.zip
2026-10-11 20:49:41 | STAGE | Stage 3: Code backup (versioned vault, hardlink dedup, retention 14d)
2026-10-11 20:49:41 | STAGE | Same-day snapshot exists -> incremental refresh (Mode B)
2026-10-11 20:49:41 | STAGE | Diff source vs snapshot: G:\backup\working_vault\20261011
2026-10-11 21:01:03 | OK | Source files: 46902, snapshot files: 46829
2026-10-11 21:01:03 | WARN | Share-locked by a live writer, skipped: data\runtime\dwm_shard_state_supplementary2_20261011\tilib_dwm_runner_instance.lock
2026-10-11 21:01:04 | WARN | Source vanished mid-run, skipped: .ailocks\tests.meta.scripts.backup.test_backup_reconciler.py.lock\owner.json
2026-10-11 21:01:06 | WARN | Source vanished mid-run, skipped: .ailocks\docs._working.backfix_campaign.00_ledger.md.lock\owner.json
2026-10-11 21:01:11 | WARN | Source vanished mid-run, skipped: .ailocks\scripts.backup.restore_drill.py.lock\owner.json
2026-10-11 21:01:21 | WARN | Source vanished mid-run, skipped: .ailocks\scripts.backup.backup_reconciler.py.lock\owner.json
2026-10-11 21:01:22 | WARN | Source vanished mid-run, skipped: .ailocks\scripts.backup.backup_config.yaml.lock\owner.json
2026-10-11 21:01:25 | OK | Snapshot: linked=0, copied=100, replaced=23, failures=0, vanished=5, share_locked=1
2026-10-11 21:01:25 | WARN | Snapshot failure: data\runtime\dwm_shard_state_supplementary2_20261011\tilib_dwm_runner_instance.lock : share-locked (WARN, not a failure): ʹ�á�1�����������á�CopyTo��ʱ�����쳣:����һ�������������ļ���һ���֣������޷����ʡ�
��
2026-10-11 21:01:45 | OK | DB dumps snapshot done: G:\backup\db_dumps\20261011
2026-10-11 21:01:45 | WARN | DB dumps rotation skipped (CH backup not ok -- oldest snapshot kept as insurance)
2026-10-11 21:01:45 | STAGE | Stage 3b: Git bundle refresh
2026-10-11 21:01:45 | STAGE | Creating bundle (latest is 8.83 days old, 2 bundle(s) on hand)
2026-10-11 21:02:53 | OK | Bundle created + verified (499 MB, rotated 1 old)
2026-10-11 21:02:53 | STAGE | Stage 3c: Off-repo assets mirror
2026-10-11 21:02:53 | WARN | Off-repo [trae_memory]: source missing (WARN, not run-fatal): C:\Users\fanzi\.trae-cn\memory
2026-10-11 21:02:54 | OK | Off-repo [qmt_bridge]: ok (0.00 GB, mode=mirror)
2026-10-11 21:02:54 | OK | Off-repo [stash_archive]: ok (0.13 GB, mode=mirror)
2026-10-11 21:03:00 | OK | Off-repo [cold_archive]: ok (193.16 GB, mode=mirror)
2026-10-11 21:13:20 | OK | Off-repo [tomb_quarantine]: ok (3.38 GB, mode=mirror)
2026-10-11 21:13:20 | STAGE | Stage 3d: G-drive fallback mirror
2026-10-11 21:14:46 | OK | G-mirror [zephyr_cold]: ok (mode=mirror would_purge=0/cap=200)
2026-10-11 21:14:46 | STAGE | Stage 4: Report
2026-10-11 21:14:46 | OK | Report saved: D:\ZephyrAlpha\logs\backup_report_20261011_194841.json
2026-10-11 21:14:46 | STAGE | Stage 4b: Rolling archive evaluation (backup-success hook)
2026-10-11 21:14:58 | OK | Backup completed in 5165.4s
2026-10-11 21:14:58 | RELEASE_LOCK | pid=40008
```

- **新事实三（13080 死因当场定位＝db_dumps 腿断供的第一份盘上直证；本班出案卷不裁定）**：第七段把 13080 钉成 runspace e63ced9e、生 17:52:35／卒 18:40:33、根＝`.worktrees\st-datalane-20261010`，但当时**没有它的点火件**。本班补齐：它就在**那个车道自己的 `logs/`** 里（在册规律"影子根点火落影子根的 logs/"第三次兑现）＝`backup_reconciler_ignite_20261011_095235.log`（27 行／1769 字节／mtime **18:40:33**＝与卒时同刻）＋同名 `.err.log`（542 字节／8 行）。err 面原文（GBK 解码）＝

```text
Test-CapacityGuardBreach : 无法将“Test-CapacityGuardBreach”项识别为 cmdlet、函数、脚本文件或可运行程序的名称。请检查
名称的拼写，如果包括路径，请确保路径正确，然后再试一次。
所在位置 D:\ZephyrAlpha\.worktrees\st-datalane-20261010\scripts\backup\backup.ps1:825 字符: 13
+         if (Test-CapacityGuardBreach $dumpsDayTarget) {
+             ~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (Test-CapacityGuardBreach:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
```

- **机制按四份副本的行序核对（本班唯一动手的取证，纯 grep 只读）**：**车道副本**`.worktrees\st-datalane-20261010\scripts\backup\backup.ps1`（mtime 10-10 17:08）＝调用 **825 行**、定义 **963 行**（先调后定义）；**主区副本** `scripts\backup\backup.ps1`（mtime 22:29）与 `git show HEAD:` 那份＝定义 **352 行**、调用 **919/1074/1152**（次序正确）。PowerShell 只在执行到 `function` 那一刻创建函数，故先调后定义的那一份运行到 825 行必然 CommandNotFoundException——**不是被杀，是自己撞死**。与 stdout 止点互咬：该发打到 `[OK] Snapshot: ... copied=505, replaced=365` 和那句乱码 `Snapshot failure` 就没了，而 19:48 完整次序是 `Snapshot failure`→`DB dumps snapshot done`→`rotation`→`Stage 3b/3c/3d`→`Stage 4`；825 行正是 db_dumps 腿的 E-4 容量红线前闸，**死在这条腿上就到不了 Stage 4**——当日报告只有 1 份（194841）、13080 那发既无 report 也无 state 回写，由此得解。前段那句"断供从来不在 CH，而在 db_dumps 腿（E-4 守卫先调后定义⇒robocopy 从未跑）"**由推断升级为盘上直证**（err 原文＋行序＋stdout 止点三件）。
- **诚实标价一处未穷尽（别把间接证当红证读）**：本班**没有**读 825 行所在块外层是否被 `try/catch` 包住，所以"终止错误直接结掉整发"只有间接证（stdout 与 err mtime 同刻止住＋无 Stage 4 报告＋无 state 写回），未做红证。三条待裁一律不动：①该车道副本为何处于混版态；②要不要在 ps1 侧加"定义前置／装载即校验"；③`.ailocks` 是否从 G 盘镜像面排除（随前段候裁⑫族）。
- **同根另一发登记（不追只记名）**：`st-datalane` 根另有 `011700`（本地 09:17）一对点火件，末行 `Another backup is running (holder PID **24468** alive, lock age 3.7h). Exiting.`、err 件 0 字节。⇒ 今日锁主至少三个名字（27300／13080／24468），24468 的身份本班手上无凭据，不追不猜。
- **新事实四（值守期间活体事件：批复二落地后第一发真机点火——判据①兑现、判据②四册无键、且发射者未证）**：本班取数时 `logs/backup_runlog_20261011_225255.log`（18 行／STAGE=5，**尚未完赛**）首三行＝`RUN_START | pid=15316 ... script=D:\ZephyrAlpha\scripts\backup\backup.ps1 root=D:\ZephyrAlpha` → `TRANSCRIPT_ON` → `LOCK_ACQUIRED`。**这是本役第一次在真机上看到 `script=` 指向主检出点**（此前 10 支 runlog 全部来自车道根），批复二"执行体改指主检出点"的判据①当场兑现。
```text
# logs/backup_runlog_20261011_225255.log —— 本班取数时刻的现场读数（在跑，非完赛态）
2026-10-11 22:52:55 | RUN_START | pid=15316 mode=all force=False script=D:\ZephyrAlpha\scripts\backup\backup.ps1 root=D:\ZephyrAlpha
2026-10-11 22:52:55 | TRANSCRIPT_ON | D:\ZephyrAlpha\logs\backup_transcript_20261011_225255.log
2026-10-11 22:52:55 | LOCK_ACQUIRED | D:\ZephyrAlpha\.runtime\backup.lock
2026-10-11 22:52:56 | STAGE | Stage 1: Pre-check
2026-10-11 22:52:56 | OK | Target drive D: online
2026-10-11 22:52:56 | OK | Target drive F: online
2026-10-11 22:52:56 | OK | Target drive G: online
2026-10-11 22:52:56 | OK | robocopy found: C:\Windows\System32\Robocopy.exe
2026-10-11 22:52:56 | STAGE | Stage 2: Database dump + config sync
2026-10-11 22:53:50 | OK | PostgreSQL dump (public): 242.15MB
2026-10-11 22:53:51 | OK | PostgreSQL globals dump: ok
2026-10-11 22:53:57 | OK | SQLite dump: 2 databases
2026-10-11 22:53:57 | OK | PG config synced to config/system_configs/pg/
2026-10-11 22:54:03 | OK | CH config synced to config/system_configs/ch/
2026-10-11 22:54:04 | OK | ClickHouse: last backup 1.7h ago (< 24h cadence), stage skipped
2026-10-11 22:54:04 | STAGE | Stage 3: Code backup (versioned vault, hardlink dedup, retention 14d)
2026-10-11 22:54:04 | STAGE | Same-day snapshot exists -> incremental refresh (Mode B)
2026-10-11 22:54:04 | STAGE | Diff source vs snapshot: G:\backup\working_vault\20261011
```
- **判据②（`last_ignite_target_root`／`last_ignite_target_reason` 写成主区／git_common_dir）＝四册并读全部查无该键**，逐册现值＝
    主区 keys=39 | last_run_outcome=backed_up | last_backup_launch_time=2026-10-11T11:48:40+00:00 | last_ignite_target_root=<ABSENT>
    QW/worktree keys=14 | last_run_outcome=shadow_ignite_refused | last_backup_launch_time=2026-10-11T10:38:36.682048+00:00 | last_ignite_target_root=<ABSENT>
    w0 keys=9 | last_run_outcome=shadow_ignite_refused | last_backup_launch_time=2026-10-11T09:43:55.788170+00:00 | last_ignite_target_root=<ABSENT>
    st-datalane keys=5 | last_run_outcome=lock_skipped | last_backup_launch_time=2026-10-11T01:17:01.045907+00:00 | last_ignite_target_root=<ABSENT>
  ⇒ 22:52 那一发**没有回写任何一册的点火目标字段**（主区册 mtime 仍 22:37:49＝批复执行账那次一次性补结算，`last_backup_launch_time` 仍 11:48:40Z）。本班按字面不补写、不自造字段（判据面），只把"①兑现而②无痕"这条差呈清。
- **该发的点火镜像四根并寻＝零命中**（名称面 14xxZ＝本地 22 点档）：
    主区 14xxZ(=本地 22 点档) 命中 0
    QW/worktree 14xxZ(=本地 22 点档) 命中 0
    w0 14xxZ(=本地 22 点档) 命中 0
    st-datalane 14xxZ(=本地 22 点档) 命中 0
  另用 mtime 面复寻（12 分钟内被改的 `.log`）只捞到仪器自志，无 igniter 件。⇒ **两个候选解释，本班不裁**：①这一发**不是事件腿点火的**（旁证很强：在册 cadence 数学是 `min_interval` 8h，主区册 `last_backup_time`=22:37:49 ⇒ 解禁应约 10-12 06:37，22:52 距裁决时刻只有 15 分钟，事件腿结构上不该放它过；而 `launch_detached_backup` 一律留镜像，无镜像＋过闸时刻矛盾 ⇒ 更像手工／他会话直发）；②镜像腿的根解析跟 `script=` 分了家（①改了执行体而镜像路径没跟着改）。这两条的分辨只需要一个动作：**问 22:52 那发的发射者是谁**——本班无权追（追发射者是追凶正活，且前段已证 PowerShell Operational 面对本机主机整下午无痕），登记候裁。
- **三面读数（22:46:16 同分钟实测，全部只读）**：`.runtime/backup.lock` **不存在**（且消失有正解＝194841 那发 21:14:58 自 `RELEASE_LOCK | pid=40008`，不是本班清的也不是闸清的；注意本班读数后又出现了 15316 的 LOCK_ACQUIRED，锁是活的——运行态断言只在本班取数那一分钟有效）｜今日报告 json **1** 份｜压缩 journal 尾两行 `G_free_GB=2531.4`＋`COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`｜27300 监听末行 `17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`（其后零新行＝按设计自退，非停写）。
- **一处本班探针无判别力（如实上报，禁读成"查无备份计划任务"）**：计划任务面三连探全废——①`schtasks /query /fo LIST | grep '^TaskName'`＝0 命中而 `head` 明明有条目（根因＝中文版字段名本地化＋GBK 输出，UTF-8 grep 失明）；②`/fo CSV | grep -iE 'zephyr|backup'`＝`Binary file matches`；③python 解码 `/fo LIST /v` 那次 stdout 为空、只经分块判据捞出一条 QuarkUpdater。⇒ 前段那句"日常备份只剩 06:00 计划任务一发"在本班手上**未能独立复核**：不采信、不推翻，原样呈报。要立这把尺需换 `schtasks /tn <名> /fo LIST /v` 逐名 GBK 解码或 `Get-ScheduledTask`——属新仪器，本班不自装。
- **下一发的判据交接（本班不自证，一眼可判）**：①看 22:52 那发跑完后有没有 `DB dumps snapshot done`＋rotation 两出口之一里的 `state last_ch_backup_status=<值>`（⑫新腿首验）；②轮转预期应改判 `DB dumps rotation: removed N`（N≥1），仍 skipped 就按⑫的读值当场分清"旧值非 ok"还是"读失败被 catch 兜底"；③`[rolling-archive] valve1` 现值与主区册 `last_ch_backup_status=ok` 并读⇒"车道根取数"实锤或推翻；④**新增一条本班判据（来自新事实三）**：若任何一发停在 `Snapshot failure` 之后、`DB dumps snapshot done` 之前，先查它 `script=` 那份副本的 825/963 行序（调用先于定义＝自己撞死），别再当被杀处理；⑤闸的后续跑在 G0 已 CLOSED＋目标 DEAD 下只会继续给 NATURAL_EXIT，本班不重复占用轮次，只在有实质事件时落账。
- **零面声明（本段）**：本班杀停进程 **0**（闸判自然收尾，无 ACTION）｜锁零删零建｜`G:\backup` 内容零写（只读 runlog 里 ps1 自报的行）｜压缩器 38464 与其 journal/ALARM 零碰（它 17:31:24 已自退）｜他人件零改动（含 `st-datalane` 车道内件——只读其日志与副本行号）｜判据·阈值·门禁码·注册表·备份任务定义**零改动**｜state 册零写（本班只读四册）｜CH 取数 0 次｜仪器零新起（未建同 pid/同日志第二支监听）｜`.runtime/commit_queue` 的 blobs 零碰（只读其 `logs/`）｜本段零新施工。
- **复核命令**：`grep -c "" logs/backup_runlog_20261011_194841.log`（应 **53**）；`for f in logs/backup_runlog_20261011_*.log; do printf "%s %s %s\n" "$(basename $f)" "$(grep -c '| STAGE |' $f)" "$(tail -1 $f | awk -F'|' '{print $2}' | tr -d ' ')"; done`（本班取数：9 支 STAGE=0/LOCK_HELD＋194841 STAGE=14/RELEASE_LOCK＋225255 STAGE=5/在跑）；`grep -n "Test-CapacityGuardBreach" .worktrees/st-datalane-20261010/scripts/backup/backup.ps1`（应 **825 调用／963 定义**／1025／1103）；`grep -n "Test-CapacityGuardBreach" scripts/backup/backup.ps1`（应 **352 定义**在前／919／1074／1152）；`grep -c CommandNotFound .worktrees/st-datalane-20261010/logs/backup_reconciler_ignite_20261011_095235.err.log`（应 **2**，全文 8 行）；`ls -l --time-style=full-iso .worktrees/st-datalane-20261010/logs/backup_reconciler_ignite_20261011_095235.log`（mtime 应 18:40:33）；`tail -3 .runtime/tmp/backfix_monitor_27300.log`（应 cycle=620 alive=True→TARGET_DEATH 17:51:19→MONITOR_EXIT_ON_TARGET_DEATH）；`python -c "import json,io;d=json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'));print('last_ignite_target_root' in d)"`（应 **False**，即②无痕）；`ls -1 logs/ | grep -c backup_reconciler_ignite_20261011`（应 **0**＝主区今日无点火件）。
- **待落地**：本段只写盘、未提交——本班授权面不含提交，主区 index 是多会话混合池，裸 commit＝归属篡改。要入册请派队列正门，files 清单只含本账本 1 件。
- **署名**：adjudicator=st-backfix3-20261011（值守轮·处置闸本役第二跑：NATURAL_EXIT 复跑幂等＋本班主菜 53 行全文入册＋13080 死因定位到"先调后定义"盘上直证＋批复二首发真机点火判据①兑现／判据②四册无键／发射者未证＋计划任务探针无判别力如实申报；零新施工、零处置动作）。


### 批复二首发真机读数更正：主证在 runlog 与 ignite 日志，不在 state 册（st-backfix3-20261011 22:5x-23:1x 值守轮）

- **落地后 9 分钟就来了第一个真机样本，方向＝批复二期望的那一侧**：22:43:45 落地（`dce5ae9d2c`）→ 22:48:44 序列化车道 **w3** 的 reconciler 副本被物化追平（`grep -c primary_checkout_root`＝3）→ **22:52:55 该车道点火的是主区那份脚本**：陷阱出生行 `22:52:56 | START pid=15316 ppid=31036 name=powershell.exe :: "C:\Windows\System32\WindowsPowerShell\1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\scripts\backup\backup.ps1`；同刻主区 `logs/backup_runlog_20261011_225255.log` 首行 `RUN_START | pid=15316 mode=all force=False script=D:\ZephyrAlpha\scripts\backup\backup.ps1 root=D:\ZephyrAlpha`＋第二行 `TRANSCRIPT_ON`＋第三行 **`LOCK_ACQUIRED`**。点火日志落在点火者自己的根：`.runtime\commit_queue\worktrees\w3\logs\backup_reconciler_ignite_20261011_145255.log`（文件名 145255＝UTC，本地 22:52:55，与 `--path-format=absolute --git-common-dir` 的解析结果互咬）。**这是全天第一次、也是批复二的设计意图第一次被现实兑现：事件腿活着，且执行体指主区真源。**
- **对照面（证明 ① 不是纸闸，也证明"怕它关腿"不是空担心）**：批复二落地**之前**，同两条车道已按 ① 真拦过——`.runtime\commit_queue\worktree` 本地 state `last_run_outcome=shadow_ignite_refused`、`last_shadow_refuse_reason=linked_worktree_dotgit_file`、`last_shadow_refuse_time=2026-10-11T13:58:23Z`（本地 21:58）；`worktrees\w0` 同型记录 mtime 22:18:18。⇒ 若只落 ① 不改指向，事件腿确实会全灭；批复二把"喂给闸的根"换对之后，同一条腿 34 分钟后就正常点火了。闸体自始至终未动。
- **本班给自己上一轮的晨核判据做一处更正（这条最要紧，写下来防下一班照错口径走）**：上一段写的"②核 state 册 `last_ignite_target_root/reason`"**作为主证不成立**。实测 w3 本地 state 现在只有 6 个键，内容是 `last_run_outcome=lock_skipped`、`last_backup_time=None`、`last_backup_launch_time=2026-10-10T23:52:28Z`，而**两个新键根本不存在**，文件 mtime＝**22:52:53**（早于 22:52:55 那次点火 2 秒）。⇒ 点火那一发的 (3) 记账（`ignited_pending_verification`＋target 两键）**没有落进任何一份 state**（主区那本 mtime 仍 22:37:49、`last_run_outcome` 仍是本班补结算写的 `backed_up`）。
- **这笔记账缺席，本班不猜成因，只把已测边界写清**：22:52:53 那次 `lock_skipped` 写入与 22:52:55 那次点火是否同一进程，盘外不可定名——22:52:53 时锁尚未被 15316 取得（其 START=22:52:55.986），所以"看到活锁主而快退"的那一发读到的要么是**别的持锁者**、要么是把陈旧锁里的 PID 误判成活（PID 复用，本役在册病形）。候选三条：①同车道 2 秒内两发事件，点火那发的 state 写失败被 fallback 吞；②点火进程在 (3) 之前退出；③车道 state 在写后被重建（该文件只有 6 键＝像新建）。**都不下结论**。可依赖的主证因此只有两份落盘：主区 runlog 的 `RUN_START ... script=` 字段（指哪一份脚本，写在脚本自己肚子里，没人覆写）＋点火日志所在**根**（谁点的）。state 册降级为旁证，且必须注明"按车道各一份、会被同车道下一发覆写"。本班不据此说 reconciler 坏了——是**本班上一轮给的读法**坏了，此处按实改正。
- **另一处口径更正（cadence 是按副本看的，而且新车道等于没有 cadence）**：上一轮本班写"8h 解禁点约 06:37"，那只对**主区那一份 state**（`last_backup_time=2026-10-11T14:37:49Z`）成立。现实是 w3 那本 `last_backup_time=None` ⇒ `trigger()` 的 8h 判据在新建车道里**天然视为已到期**，所以 22:52 就能点火。⇒ 在"多副本共用一把锁"的旧病没清完之前，**事件腿的 cadence 时钟不是全局的，且每个新车道一出生就是"已到期"状态**；真实形态＝"任一车道的一次提交事件都可能点一发"。这条与前班影子链 SH-11（用 checkpoint 面双读防重烧）治的是同一个病，只是生产腿尚无那枚双读闸——本班不改判据，只把观测口径钉准并列为①②之外的**覆盖面残余**。
- **在飞读数的如实交代（这一发本身值得记）**：23:25 复测 `pid=15316` 仍 ALIVE（powershell 141,196K），runlog 末行仍是 22:54:04 `STAGE | Diff source vs snapshot: G:\backup\working_vault\20261011`＝**Stage 3 的 Mode B 差分已爬 31 分钟**，而今晚 19:48 那发同一条腿只用 **11.4 分钟**（G 盘此刻空闲、压缩早已收口，所以这次**不是** 27300 那种"被 Optimize-VHD 挤住"的形态）。CH 段本轮合法跳过：`last backup 1.7h ago (< 24h cadence), stage skipped`（与 19:48 那发的真 CH 备份相隔 1.7h，属设计内 24h 节奏）。`.runtime/backup.lock` 现值 `PID:15316 START:2026-10-11T22:52:55.9860408+08:00`。**本班不干预、不续跑、不杀停（红线）**；但记一条：这类"同一条腿两倍慢"的读数，**在 T1 之前根本看不见**（无阶段日志时它和"已经死了"同形）——这就是 runlog 落地的日常价值，不需要事故才兑现。若下一轮它仍停在同一行，届时按处置闸的三面判据走（不在本段自决）。
- **暂存池第三击复核（知会项，本班只测不动）**：`git diff --cached HEAD --numstat` 现 **7 条、删除列全为 0（纯新增）**＝`docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__06_baseline_birth_and_r_face_declaration.yaml +133`、`docs/_working/maint3_campaign/00_ledger.md +91`、`maint3_campaign/20_t7_plan.yaml +37`、`maint3_campaign/30_pool_rollback_rootcause_casefile.md +50`、`mineloop_campaign/31_woa1_adapter_landing.yaml +22`、`mineloop_campaign/draft_TDM-X-R1-01__comparison__06_基线出生件与r位声明版.yaml +3`、`disk_reorg_campaign/LEDGER_final.md +1`——**staged-D 已归零**（与总统筹"已清 6 件回退残渣、先归档后按 HEAD 复位、存证 `.runtime/tmp/pool_rollbackbomb_20261011/strike3/`"一致）；本班对以上七件零触碰、零代 add。本班自己五件在 `git status` 空标记＝磁盘＝HEAD。
- **候裁⑭登记（Owner 批复原话：登记候裁，不催）**：补结算把 `last_backup_time` 写成**裁决时刻**而非该发真实收尾时刻（今晚后果＝主区口径的 cadence 位移 +83 分钟）。取向＝把 `settle_previous_ignition/_adjudicate_completed_run` 的落账时刻改用"从脱离日志/报告解析出的真实收尾时间"，`now_iso` 仅留作"裁决写入时刻"另立一键。**本班不动**（判据/时序面），等令。
- **零面声明（本段）**：本班杀停进程 0｜零写生产链文件（本段全部读自既有落盘物：陷阱出生行、runlog、ignite 日志、state、git 元数据）｜他人 staged 条目零触碰｜`G:\backup` 内容零写｜判据·阈值·门禁码·注册表·备份任务定义零改动｜CH 取数 0（本轮 CH 结论读自 ps1 自报，1.7h 跳过属设计内）｜仪器零新起（未给 15316 挂监听，主证走 runlog）。
- **复核命令**：`head -3 logs/backup_runlog_20261011_225255.log`（应见 `script=D:\ZephyrAlpha\scripts\backup\backup.ps1` 与 `LOCK_ACQUIRED`）；`grep -h "pid=15316 " .runtime/tmp/procstart_trap_ppid.log | grep "2026-10-11 22:5"`（应见 22:52:56 START ppid=31036 主区脚本）；`ls -1 .runtime/commit_queue/worktrees/w3/logs/backup_reconciler_ignite_20261011_1452*.log`（应两支）；`grep -c primary_checkout_root .runtime/commit_queue/worktrees/w3/scripts/backup/backup_reconciler.py`（应 3，mtime 22:48:44）；`python -c "import json,io;p=r'.runtime/commit_queue/worktrees/w3/data/databases/backup_state.json';d=json.load(io.open(p,encoding='utf-8'));print(len(d),'last_backup_time=',d.get('last_backup_time'),'outcome=',d.get('last_run_outcome'),'has_target_keys=',('last_ignite_target_root' in d))"`（应 6／None／lock_skipped／False＝记账缺席的正证）；`python -c "import json,io;d=json.load(io.open(r'.runtime/commit_queue/worktree/data/databases/backup_state.json',encoding='utf-8'));print(d['last_run_outcome'],d['last_shadow_refuse_reason'])"`（应 shadow_ignite_refused linked_worktree_dotgit_file＝①真拦过的正证）；`git diff --cached HEAD --numstat`（应 7 条、删除列全 0）；`tail -1 logs/backup_runlog_20261011_225255.log`＋`tasklist /FI "PID eq 15316"`（下一轮取收尾或续观）。
- **署名**：adjudicator=st-backfix3-20261011（值守轮：批复二首发真机读数＋本班晨核判据自纠两处＋第三击池面复测＋候裁⑭登记）。

- **与同轮另一段的衔接（两条不冲突，本班把话说齐再入袋）**：自动化值守轮那段写的是「判据②四册无键、且发射者未证」——那是**从 state 侧取数**的如实读数（四本 state 里确实没有 target 两键，本段已把「为什么不能拿 state 当主证」连机制带证据钉清）。本段补的是**落盘物证**那一侧：全仓 find 只命中一对 `backup_reconciler_ignite_20261011_145255.log(.err.log)`，位于 `.runtime\commit_queue\worktrees\w3\logs\`；而 `get_ignite_log_dir()`＝`PROJECT_ROOT/logs`、点火日志路径又在 launch 时被写死进 `Start-Process -RedirectStandardOutput`，所以「这对文件出现在 w3 的 logs 下」就等价于「发射者那份 reconciler 的 PROJECT_ROOT＝w3」；再加该根副本 mtime 22:48:44（＝落地后 4 分钟被物化追平、含 primary_checkout_root 3 处）——发射根因此定为 w3。这是同条规律「影子根点火落影子根自己的 logs/」在本役第四次兑现（前三次：`commit_queue\worktree`／`worktrees\w0`／`.worktrees\st-datalane-20261010`，其中 13080 那发的件证由自动化轮补齐）。⇒ 差一步的两句不能混说：**发射根已证（w3）**，**state 记账缺席未证成因**，各自成立、各自标价。


### 值守轮：闸本跑=NATURAL_EXIT（无 ACTION 行）＋计划任务面探针转正（主区执行体实证）＋22:52 在发差分腿推进中＋闸证据文件覆写式登记（st-backfix3-20261011 23:2x-23:4x 值守轮）

- **闸本跑读数（23:26:11 执行，命令逐字 `python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300`）**：末行 `VERDICT: NATURAL_EXIT_not_our_action`，**且没有 ACTION 行**（自然收尾分支按协议不动作）。factor values 逐字：`close_status = 'CLOSED'`／`close_detail = '2026-10-11 17:31:24 | PROBE 1 ~  ~ '`／`close_ts = '2026-10-11 17:30:38'`／`relief_elapsed_min = 355.5`／`target_alive = 'DEAD'`。三分支在此输入下唯一（G0 已 CLOSED＋缓释远超 30 分＋目标已 DEAD），本班零处置动作——"杀不杀由脚本判"这条本轮没被绕过。
- **27300 自然收尾时刻的三面互咬**：闸 `target_alive='DEAD'`｜`tasklist /FI "PID eq 27300"`＝"没有运行的任务匹配指定标准"｜监听末行 `17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`（其后零新行＝按设计自退，非停写）。⇒ 死亡时刻≈**17:51**，与压缩 round-2 的 17:31:24 收口同序（收口后约 20 分钟目标消失）。
- **计划任务面探针转正（把上一轮如实申报的"三探全废"补上判别力）**：`Get-ScheduledTask` 通道一次命中，逐字 `\ZephyrAlpha-DailyBackup ==> wscript.exe "D:\ZephyrAlpha\scripts\launch_hidden.vbs" "D:\ZephyrAlpha\scripts\backup\backup.ps1" -Mode all -Force`；`STATE=Ready`｜触发器 `MSFT_TaskDailyTrigger StartBoundary=2026-07-28T06:00:00+08:00 Enabled=True`（Repetition 空）｜`StartWhenAvailable=True WakeToRun=False ExecutionTimeLimit=PT4H Hidden=False`｜`LASTRUN=10/11/2026 12:25:17 NEXTRUN=10/12/2026 06:00:00 LASTRESULT=0`。⇒ 前段那句"日常备份只剩 06:00 计划任务一发"**本轮独立复核成立**，且执行体＝主区那份 `D:\ZephyrAlpha\scripts\backup\backup.ps1`（批复二期望的那一侧在任务册里本来就写着）。失败根因钉准＝`schtasks` 的 LIST/CSV 面在中文 Windows 上是本地化字段名＋GBK 输出，UTF-8 grep 失明；可复用的尺＝`Get-ScheduledTask` 强属性读取，且整条命令在 git-bash 里**必须单引号包**（双引号会把 `$_` 吞成 `=extglob`，本班本轮实测连撞两次才过）。
- **由此给 22:52 那发的发射者再加一证（与上一轮"发射根＝w3"互补，不推翻）**：任务面 `LASTRUN=12:25:17`＋`NEXTRUN=10-12 06:00` ⇒ 计划任务今日**只跑过 12:25 那一发**，22:52:55 不是它点的。另登记一条**新反常**：12:25 那一发盘上**零痕迹**（今日 runlog 共 **11** 支、最早 14:32:51＝T1 首产；`logs/*20261011_12*` 全目录零命中）⇒ 它跑的是 T1 之前的副本，静默跳锁／静默退出现场正是 T1 治的那类病；`StartWhenAvailable=True` 给了"06:00 错过、机器可用后 12:25 补跑"的正解候选，**本班不裁成因**（追发射者是追凶正活）。
- **今日 11 支 runlog 的 `script=` 副本分布（本班自 grep 汇总，非转述）**：**7** 支 `.runtime\commit_queue\worktree\scripts\backup\backup.ps1` ＋ **3** 支 `.runtime\commit_queue\worktrees\w0\scripts\backup\backup.ps1` ＋ **1** 支 `D:\ZephyrAlpha\scripts\backup\backup.ps1`（＝22:52:55 那发）。形态面：9 支停在 4 行 `LOCK_HELD | exit 0 skip_record=...`｜`backup_runlog_20261011_194841.log` **53** 行末 `RELEASE_LOCK | pid=40008`｜`backup_runlog_20261011_225255.log` 现 **18** 行末 `STAGE | Diff source vs snapshot: G:\backup\working_vault\20261011`。附带一条：`worktrees\w0\scripts\backup\backup.ps1` 此刻 **MISSING**（17:43:55 那发用它跑过，车道已被清）＝"执行体指向瞬时物"的旧病，本轮只是观测。
- **22:52 在发那一发的推进证据（按协议＝有推进即 VETO，本班不干预）**：`tasklist` 内 `powershell.exe 15316` 存活；CPU 五点序列 **19.89 → 20.28 → 21.22 → 21.44 → 22.03**（约 14 分钟跨内 +2.1 CPU 秒 ≈ 2.5%，I/O-bound 爬取），WS 141,216K → 147,066K；差分腿已爬 ≈45 分钟（对照 19:48 那发同腿 **11.4** 分钟）。**关键新增观测**：`logs/backup_transcript_20261011_225255.log`（1,396 字节）尾行与 runlog 末行**停在同一处** `[BACKUP] Diff source vs snapshot: ...` ⇒ 两日志面同点＝不是 runlog 单侧写坏，是脚本真的还在这条腿上；本班不据此判挂死（无新阈值），只记"若下一轮仍同一行则按处置闸三面判据走"。上一轮交付的判据①（⑫新腿首验＝`state last_ch_backup_status=<值>` 出现在 `DB dumps snapshot done` 之后的 rotation 出口）**本跑仍未兑现**。
- **首份报告的机读摘要（本班自 `logs/backup_report_20261011_194841.json` 取，非转述）**：`timestamp=2026-10-11T21:14:46.754+08:00`｜`duration_seconds=5165.4`｜`mode=all`｜`code_backup.status=ok`（copied=100 failures=0 vanished=5 share_locked=1 robocopy_exit=0）｜`git_bundle.status=ok action=created rotated=1`｜`g_mirror.status=ok`（zephyr_cold robocopy_exit=1 would_purge=0/cap=200）｜`offrepo_backup.status=warn`（source_missing=[trae_memory]）｜`databases.clickhouse.status=ok verified=True table_count=225 file=/mnt/chbackup_local/inc.zip bytes=82,534,136,381 ch_num_files=1,010,694 size_match=True`。
- **一处"日志措辞与 json 对不上"已核不立案（这条最容易骗下一班）**：19:48 那发 runlog 写 `DB dumps rotation skipped (CH backup not ok -- oldest snapshot kept as insurance)`，而同发 json 里 `clickhouse.status=ok`。盘上现文两份副本（主区／影子根）同行同文本＝`:953` 已是批复二 ⑫ 的新写法 `state last_ch_backup_status={0}`，`sha256[0:16]` 主区与影子根同为 `45a7dd16bbfaf798`（mtime 22:29:42／22:47:41），落地 commit `dce5ae9d2c` 时刻 22:43。⇒ 那句 "not ok" 出自 22:43 之前的旧副本，**不是标志位接错**。并入既有在册病形"运行码落后 HEAD"：拿 ps1 文本对日志措辞之前，先看该发 `script=` 那份副本的 mtime 与落地时刻的先后。
- **仪器面一处如实登记（本班零改闸体）**：`.runtime/tmp/bf3_dispose_evidence.md` 现 566 字节、内容＝本班 23:26:11 那一跑；闸写证据全为**覆写**——`.runtime/tmp/bf3_dispose_gate.py` 内 `evidence.write_text(...)` 见于 331/344/360/364/375 行，另 `Path(args.evidence).write_text(body)` 见 391 行，`--evidence` 默认＝`PROD_EVIDENCE`（42/385 行）。⇒ **复跑会覆盖上一轮证据文本**；要留多轮链必须每轮显式 `--evidence <本轮独立路径>`。列为下一班用具＋候裁（若 Owner 要审处置那一把的证据链，这条是前置；本班不改闸，属判据/仪器面）。
- **三面读数（23:26-23:4x 同分钟实测，全部只读）**：`.runtime/backup.lock`＝`PID:15316 START:2026-10-11T22:52:55.9860408+08:00`（锁面上一轮记的"不存在"已被 21:14:58 之后的两发真跑改写，运行态断言只在本班取数那一分钟有效）｜今日报告 json **1** 份｜最新 runlog＝`225255`，末行见上｜压缩 journal 尾两行 `G_free_GB=2531.4`＋`COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`（与上一轮**完全相同**＝压缩器已自退，零变化）｜27300 监听末行 `17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`（零新行）。
- **一行大白话**：占着备份锁的那个老进程是自己没的（不是我们杀的），闸照协议只承认这一点；今天已经真跑完一整轮备份并出了今晚第一份报告，此刻另一轮正在"逐文件比对"这一步慢慢爬，我们看着它、不动它。
- **零面声明（本段）**：本班杀停进程 **0**（闸本跑无 ACTION）｜锁零删零建零改（现值是 15316 自己写的）｜`G:\backup` 内容零写（只读其内 runlog/vault 的 mtime 面）｜压缩器 38464 与其 journal/ALARM 零碰（17:31:24 已自退）｜他人件零改动｜判据·阈值·门禁码·注册表·计划任务定义·闸体**零改动**（`Get-ScheduledTask` 只读，未碰 `Set-/Unregister-`）｜state 册零写｜CH 取数 **0** 次（本轮 CH 结论全部读自 json 与 ps1 自报）｜仪器零新起（未给 15316 挂第二支监听）｜`.runtime/commit_queue` 的 blobs 零碰（只读其 `logs/` 与副本文本）｜本段零新施工。
- **复核命令**：`python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300`（应 `VERDICT: NATURAL_EXIT_not_our_action` 且无 ACTION 行）；`cat .runtime/backup.lock`（应 PID:15316）；`ls -1 logs/backup_runlog_20261011_*.log | wc -l`（应 **11**）；`grep -h RUN_START logs/backup_runlog_20261011_*.log | awk -F"script=" "{print \$2}" | sort | uniq -c`（应 7 影子根＋3 w0＋1 主区）；`grep -c "" logs/backup_runlog_20261011_225255.log`（本跑 **18**）；`tail -1 logs/backup_transcript_20261011_225255.log`（应与 runlog 末行同点）；`powershell -NoProfile -Command '"CPU=" + (Get-Process -Id 15316).CPU'`（本跑五点 19.89→22.03）；`schtasks /query /tn ZephyrAlpha-DailyBackup /fo LIST /v`（本机 UTF-8 grep **失明**，须用 `powershell -NoProfile -Command '...'` 单引号版 `Get-ScheduledTask -TaskName "ZephyrAlpha-DailyBackup"` 读 `.Actions/.Triggers/.Settings`，应见 06:00 DailyTrigger 与主区 ps1）；`grep -n "write_text" .runtime/tmp/bf3_dispose_gate.py`（应 331/344/360/364/375/391 全为覆写）；`sha256sum scripts/backup/backup.ps1 .runtime/commit_queue/worktree/scripts/backup/backup.ps1`（应同 `45a7dd16bbfaf798...`）。
- **待落地**：本段只写盘、**未提交**——本班授权面不含提交，主区 index 是多会话混合池，裸 commit＝归属篡改；要入册请派队列正门，files 清单只含本账本 1 件。
- **署名**：adjudicator=st-backfix3-20261011（值守轮：闸本跑 NATURAL_EXIT 无 ACTION＋27300 死期三面互咬≈17:51＋计划任务面探针转正（06:00 腿＋主区执行体＋StartWhenAvailable 补跑解释候选）＋22:52 发射者再加一证＋今日 11 支 runlog 副本分布＋在发差分腿 CPU 五点推进证据与双日志面同点＋首份报告机读摘要＋"not ok 措辞"旧副本归因（不立案）＋闸证据文件覆写式登记为候裁；零处置、零新施工）。


### 值守轮：闸复跑幂等=NATURAL_EXIT（relief 375.5）＋差分腿 45.2 分钟自走（停滞嫌疑证伪）＋⑫轮转新腿首验兑现 removed 3、但读值系跨发消费＋三面对照同拍／点火 err 支 0 字节（st-backfix3-20261011 23:46-23:5x 值守轮）

- **闸本跑读数（23:46:08 执行，命令逐字 `python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300`）**：末行 `VERDICT: NATURAL_EXIT_not_our_action`，**无 ACTION 行**（自然收尾分支按协议不动作，本班未杀未停）。factor values 逐字：`close_status = 'CLOSED'`／`close_detail = '2026-10-11 17:31:24 | PROBE 1 ~  ~ '`／`close_ts = '2026-10-11 17:30:38'`／`relief_elapsed_min = 375.5`／`target_alive = 'DEAD'`。与前跑（23:26:11，relief 355.5）比对：**除 relief 外五键全等**，差值 20.0 分＝两跑的时刻差，非新事实⇒ 本闸在此输入下幂等，G0/缓释/存活三判据无一漂移。独立复核：`tasklist /FI "PID eq 27300"`＝"没有运行的任务匹配指定标准"（零命中）；监听末行仍 `17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`。
- **上一班那条条件句本轮兑现（停滞嫌疑证伪，且这是本役最贵的一条）**：前段记"差分腿已爬 ≈45 分钟、runlog 与 transcript 同停在 `Diff source vs snapshot`，若下一轮仍同一行则按处置闸三面判据走"。本跑实测该行**已自走**：22:54:04 进差分 → 23:39:17 出 `OK | Source files: 46974, snapshot files: 46907`＝差分腿耗时 **45 分 13 秒**（对照 194841 同腿 11 分 22 秒，慢 **3.98 倍**）；随后一路正常出口到 23:47:01 的 `Off-repo [cold_archive]: ok (193.16 GB)`。⇒ 结论只有一句：**它没挂死，只是慢**；而"按静置时长判挂死"若成立，被误杀的是当晚唯一在跑的完整轮（194841 之后第二发）。本班不据此加/改任何阈值（判据·阈值零改），只把这条收益与代价入册——它给"缓释窗内 CPU 读数无判别力"那条协议补了一个盘上算例。
- **⑫ 轮转读值新腿＝本役首验，但只兑现一半（分面说清，勿笼统报"全通过"）**：`logs/backup_runlog_20261011_225255.log` 第 **33/34** 行逐字＝`2026-10-11 23:46:56 | OK | DB dumps snapshot done: G:\backup\db_dumps\20261011` 紧接 `23:46:56 | OK | DB dumps rotation: removed 3 old snapshot(s) [state last_ch_backup_status=ok]`。⇒ 前段交接的判据①（state 读值出现在 `DB dumps snapshot done` 之后的 rotation 出口）**形态成立**；判据②（预期改判 `DB dumps rotation: removed N`，N≥1）**成立 N=3**；且走的是 removed 分支而非 skipped 分支，读值面拿到的是 `ok`（既非"旧值非 ok"也非 catch 兜底）。**未兑现的那一半**：本发 CH 腿按 cadence 跳过（第 15 行 `ClickHouse: last backup 1.7h ago (< 24h cadence), stage skipped`），而读值源＝`scripts/backup/backup.ps1:938 $dumpsStateRead = [string]$sJson.last_ch_backup_status`、写值源＝`:1238 $state | Add-Member -NotePropertyName last_ch_backup_status ... -Force`⇒ 本发读到的 `ok` 是 **194841 那发写进 state 的跨发值**，不是"本轮自写自读"。下一发要验的才是那一半：CH 真跑的轮里，rotation 读值应与本轮自写 `chSt` 同值。**取样时刻也钉准**：判据①②在 rotation 那一行即可判，不必等整发 RELEASE_LOCK（这是把取样点写实，不是放宽判据）。本班不裁"读 state 而非读本轮标志"该不该（设计面，批复二原文即"轮转读值入日志"）。
- **对照旧文本一发（说明为何 194841 那句 "not ok" 不能再当病）**：194841 第 37 行 `21:01:45 | WARN | DB dumps rotation skipped (CH backup not ok -- oldest snapshot kept as insurance)`＝旧副本口径，**连读值都没打印**（旧形态本身不可判，正是批复二⑫要治的面）。时间线自洽：落地 commit `dce5ae9d2c`＝22:43:45（`git show -s` 实测），194841 那发 19:48:41 点火早于落地⇒跑旧码；225255 那发 22:52:55 点火晚于落地⇒跑新码，实测主区 `scripts/backup/backup.ps1` `sha256[0:16]=45a7dd16bbfaf798`、`:951` 为 removed 新写法／`:953` 为 skipped 新写法（两出口都带 `[state last_ch_backup_status=…]`）。⇒ 前段"旧副本归因、不立案"的判定**本轮拿到正证**（同判据的新形态在盘上真的打得出来）。
- **三面对照（runlog／transcript／reconciler 点火链）——本班主菜的第 4 步交付**：① runlog `225255` 现 **41** 行，`RUN_START pid=15316 script=D:\ZephyrAlpha\scripts\backup\backup.ps1 root=D:\ZephyrAlpha`→`LOCK_ACQUIRED`→Stage 1/2/3 各行齐、末行见上（**尚无 RELEASE_LOCK**＝在飞）。② transcript `logs/backup_transcript_20261011_225255.log` **9,161** 字节、mtime 23:47:01.131，与 runlog 末行同分钟同事件；原生错误计数（`Exception|ErrorRecord|Cannot|not recognized|CommandNotFound`）＝**0**⇒ T1 的 transcript 通道头一次在"有真跑"的轮里保持空面；这是"未观测到"，**不等于**"不会发生"。③ 点火链 `.runtime\commit_queue\worktrees\w3\logs\backup_reconciler_ignite_20261011_145255.log` **2,906** 字节、mtime 23:47:01.130，尾行与 runlog 逐字同条（`[OK] Off-repo [cold_archive]: ok (193.16 GB, mode=mirror)`）；同刻 `.err.log`＝**0 字节**（自 22:52:55.416 出生至今零写）⇒ 前段"发射根＝w3"在本发活体续写中得到再证，且 stderr 面干净。**新增一条给下一班的尺（本班实测踩过配对歧义）**：点火件文件名用 **UTC**（`145255`）而 runlog/transcript 用本地时刻（`225255`），相差整 8 小时——按字面时刻找配对会得"查无"，须先做时区换算或按 mtime 配。
- **本发增量面读数与一条 runlog 盲区（只登记、零改）**：`Snapshot: linked=0, copied=140, replaced=69, failures=0, vanished=12, share_locked=0`（对照 194841 copied=100／replaced=23／vanished=5／share_locked=1，两发 `failures` 均 **0**）；`Bundle fresh (0.11d old) with 2 bundle(s) on hand, skipping`（194841 刚建 499 MB，本发按设计跳过＝不是漏跑）；今日报告 json 仍 **1** 份（22:52 未达 Stage 4，属正常）。`vanished=12` 全为 `.ailocks\*owner.json`＝多会话 claim 在扫描窗内正常出生又释放，**不是文件丢失**（这个计数形态下一班别当战损报）。另登记一条观测：23:44:40 那条 vanished 路径的中文名段在盘上呈乱码（ASCII 前缀可见 `.ailocks\docs._working.mineloop_campaign.draft_tdm-x-r1-01__comparison__06_`，其后不可读）⇒ runlog 写入侧非 UTF-8，**含非 ASCII 名的资产在备份日志里 grep 不到**；拿 runlog 反查"某文件有没有被扫到"存在这一类盲区，须改用名集合差或 transcript 侧对拍。本班不改编码、不新建工具。
- **仪器面一处如实自报（后果由本班造成，不遮掩）**：本班按任务书逐字命令复跑闸⇒`.runtime/tmp/bf3_dispose_evidence.md` 被**覆写**（现 566 字节、mtime 23:46:08.093＝本班版），23:26:11 那一跑的证据文本**已不在盘上**。缓解＝前段把该跑的 factor values 已逐字入册（本段首条亦留了本跑原文），信息面零丢失；根因仍指向前段在册候裁（闸内 `write_text` 全为覆写，多轮证据链须显式 `--evidence <本轮独立路径>`）。本班未改闸体、未新建第二支同 pid 同日志监听（守红线），压缩器 38464 与其 journal/ALARM 零碰。
- **三面读数（23:46:22-23:47:01 同分钟实测，全部只读）**：`.runtime/backup.lock`＝`PID:15316 START:2026-10-11T22:52:55.9860408+08:00`（与 22:52:55 那发 `LOCK_ACQUIRED` 自洽；本班未删未改）｜`ls -1 logs/backup_report_20261011_*.json | wc -l`＝**1**｜最新 runlog＝`225255`（41 行，末行见上）｜压缩 journal 尾两行 `G_free_GB=2531.4`＋`COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`（与前两班**完全相同**＝压缩器已自退、零变化）｜27300 监听末行 `17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`（零新行）。运行态断言仅在本班取数那一分钟有效。
- **一行大白话**：占着备份锁的老进程是自己没的（闸按协议只承认这一点，我们没动手）；上一班盯着"卡在逐文件比对 45 分钟"怕它死透，本轮它自己走完了这一步并继续往下跑，证明只是慢不是死；而且备份脚本新加的那句"到底删没删旧快照、依据是哪个值"今晚头一回真的打进了日志——只是它读的是上一轮存下的值，本轮自己没跑 ClickHouse，所以这半句话还得等下一发补验。
- **零面声明（本段）**：本班杀停进程 **0**（闸本跑无 ACTION，27300 系自然收尾）｜锁零删零建零改｜`G:\backup` 内容零写（只读其内 vault/db_dumps 的路径文本与日志面）｜压缩器与其 journal/ALARM 零碰、存活谓词零改、`Optimize-VHD` 零重跑/零中止/零接管｜`data.vhdx`/`boot.vhdx` 零碰｜他人件与他人 staged 条目零触碰｜判据·阈值·门禁码·注册表·计划任务定义·闸体·ps1 文本**零改动**（本段全部读自既有落盘物＋`git show -s`＋`tasklist`）｜state 册零写｜CH 取数 **0** 次｜仪器零新起（未给 15316 挂监听，主证走 runlog/transcript/点火件三面）｜`.runtime/commit_queue` 的 **blobs 零碰**（只读其 `worktrees/w3/logs/` 两支点火件）｜本段零新施工。
- **复核命令**：`python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300`（应 `VERDICT: NATURAL_EXIT_not_our_action` 且无 ACTION 行；注意会覆写证据文件）；`cat .runtime/backup.lock`（应 PID:15316）；`sed -n '33,34p' logs/backup_runlog_20261011_225255.log`（应见 `DB dumps snapshot done` 与 `rotation: removed 3 … [state last_ch_backup_status=ok]`）；`sed -n '15p' logs/backup_runlog_20261011_225255.log`（应见 CH `stage skipped`，即跨发读值的正证）；`sed -n '37p' logs/backup_runlog_20261011_194841.log`（应见旧写法 "not ok"）；`grep -n "DB dumps rotation" scripts/backup/backup.ps1`（应 951 removed 版／953 skipped 版）；`sha256sum scripts/backup/backup.ps1 | cut -c1-16`（应 `45a7dd16bbfaf798`）；`git show -s --format="%h|%ad|%s" --date=format:"%Y-%m-%d %H:%M:%S" dce5ae9d2c`（应 22:43:45；注意 `git log -1 -- <hash>` 会把 hash 当路径而输出空，勿据此判"查无此 commit"）；`ls -l --time-style=full-iso .runtime/commit_queue/worktrees/w3/logs/backup_reconciler_ignite_20261011_145255*.log`（应 stdout 2,906 字节／err **0** 字节）；`grep -cE "Exception|ErrorRecord|Cannot|not recognized|CommandNotFound" logs/backup_transcript_20261011_225255.log`（应 0）；`tail -2 .runtime/tmp/backfix_compress2_journal.log`（应与前班完全相同）；`ls -1 logs/backup_runlog_20261011_*.log | wc -l`（本班 **11**，下一发出现 225255 之外的新时刻即另有发射）。
- **待落地**：本段只写盘、**未提交**——本班授权面不含提交，主区 index 是多会话混合池，裸 commit＝归属篡改；要入册请走队列正门，files 清单只含本账本 1 件。
- **下一班的取样点（本班不自裁，只钉时刻）**：①22:52 这发跑到 `Stage 4: Report`＋`RELEASE_LOCK | pid=15316` 才算收尾，收尾后今日报告应＝**2** 份；②"⑫ 自写自读"那一半要等**下一发真跑 CH 腿**的轮才能补验（cadence 24h⇒最早约明日此时），届时对拍 `rotation` 读值与该发 `:1238` 写入值；③差分腿既已证"慢 45 分不等于挂死"，后续任何按静置时长起的处置念头都须先过闸的三面判据，不由值守轮自行拍。
- **署名**：adjudicator=st-backfix3-20261011（值守轮·本役第三跑：闸复跑幂等比对（除 relief 外五键全等）＋27300 自然收尾三面互咬＋前班条件句证伪"停滞"并给出误杀代价算例＋⑫轮转新腿首验分面兑现（形态成立／自写自读未验，含跨发读值取证）＋旧 "not ok" 措辞的旧副本归因拿到正证＋三面对照同拍与 err 支零字节＋点火件 UTC 命名配对坑＋非 ASCII 名的 runlog 盲区＋本班覆写证据文件如实自报；零处置动作、零新施工）。



### 值守轮（同轮收官补段）：本班守到的那一发自己收尾了——22:52 发 48 行全程 RELEASE_LOCK、今日报告增至 2 份、锁自行消失；⑫ 读值跨发链被两个时刻双向夹住（读到 ok＝上发写／本发写 skipped）（st-backfix3-20261011 23:46-23:5x 值守轮·补段）

- **本班主菜到齐（第 4 步的"守到"条件满足）**：`logs/backup_runlog_20261011_225255.log` 于 **23:58:27** 自然走完，末两行逐字＝`OK | Report saved: D:\ZephyrAlpha\logs\backup_report_20261011_225255.json`＋`OK | Backup completed in 3931.5s`＋`RELEASE_LOCK | pid=15316`；行数 41→**48**；`.runtime\backup.lock` 于 23:58:35 实测**不存在**（该发自己删的，不是本班清的、也不是闸清的）；`tasklist /FI "PID eq 15316"` 零命中。⇒ 今日**报告 json 由 1 份增至 2 份**，"生产报告自 10-09 05:27 后为 0 份"这条在册事实**本役正式改写**。全程 9 条 STAGE 行齐（1→2→3→3b→3c→3d→4），本班取数路径＝轮询该文件直到出现 `RELEASE_LOCK`（第 13 拍命中，零写入探法）。
- **一发"落地后主区副本"的完整实跑＝批复二/三的真机首验（这是追凶役要的形态）**：本发 `RUN_START pid=15316 script=D:\ZephyrAlpha\scripts\backup\backup.ps1`＝主区那份，点火时刻 22:52:55 晚于落地 commit `dce5ae9d2c`（22:43:45）⇒ 跑的正是含 ⑫ 的新码，实测 `sha256[0:16]=45a7dd16bbfaf798`、`:951` removed 版／`:953` skipped 版两出口都在文本里。对照 194841 那发（19:48:41 点火，早于落地）跑旧码、打旧措辞——**同一段代码的新旧两态在同一晚各留一发实样**，前段"旧副本归因、不立案"至此双面闭合。
- **⑫ 跨发读值链被两个时刻双向夹住（比前段"只兑现一半"更进一步，且仍不裁设计面）**：读取侧＝`23:46:56 | OK | DB dumps rotation: removed 3 old snapshot(s) [state last_ch_backup_status=ok]`；写入侧＝同发收尾时 `data/databases/backup_state.json` 现为 39 键、`last_backup_time=2026-10-11T23:58:27.328`（＝本发写的）、`last_ch_backup_status=**skipped**`（本发 CH 腿按 cadence 跳过，`:1238 Add-Member` 把 `skipped` 写回）。⇒ 读发生(23:46:56)在写(23:58:27)**之前 11.5 分钟**，而读到的是 `ok` 不是 `skipped`＝**"读的不是本轮自写值、而是上一发存下的值"由时序直接证成**（前段那条"跨发消费"从推断升为实证）。同时"自写"这半边也拿到了盘上写值证据（`skipped` 落在主区册）。**下一发的可判预测（本班只登记预期，不自裁对错）**：若下一发 CH 腿仍 `skipped`，rotation 出口应走 `:953` 的 warn 形态、逐字含 `[state last_ch_backup_status=skipped]`；届时快照目录若仍有旧快照未被轮转＝"保险形态"会连续存在——**这属设计内还是债，留 Owner/追凶侧判，本班不动判据、不改阈值**。
- **第二份报告的机读摘要（本班自 `logs/backup_report_20261011_225255.json` 取，非转述）**：10 顶层键（与 194841 同构）｜`timestamp=2026-10-11T23:58:27.2877427+08:00`｜`duration_seconds=3931.5`｜`mode=all`｜`code_backup.status=ok`、`rotated=[]`｜`git_bundle.status=skipped`（runlog 同刻 `Bundle fresh (0.11d old) ... skipping`＝194841 刚建过 499 MB，非漏跑）｜`g_mirror.status=ok`、`source_missing=[]`｜`offrepo_backup.status=warn`、`source_missing=['trae_memory']`（与 194841 同一条在册缺源）｜`databases`: pg `ok`／pg_globals `ok`／sqlite `ok`／**clickhouse `skipped`**。快照统计＝`copied=140, replaced=69, failures=0, vanished=12, share_locked=0`，`failures` 两发均 0。
- **耗时对照（给"慢≠死"再加一组数）**：本发全程 **65.5** 分 vs 194841 全程 **86.1** 分，但本发 CH 腿跳过——把 CH 的 59 分（19:50:28→20:49:39）扣掉后，194841 非 CH 段≈**27** 分 vs 本发 **65.5** 分；差额集中在差分腿（**45.2** 分 vs 11.4 分）与 `tomb_quarantine` 腿（**8.3** 分 vs 10.4 分）。⇒ 同一份脚本、同一天、同一台机，差分腿差 4 倍＝**G 盘与多会话在途文件量**决定，不是脚本状态机差异；任何"按静置时长起处置念头"在这一组数面前都站不住（本班据此仍不加判据）。
- **三面对照收尾态（本班主证面，全只读）**：runlog **48** 行末 `RELEASE_LOCK`｜transcript `logs/backup_transcript_20261011_225255.log` **9,732** 字节、mtime 23:58:27.376，原生错误计数仍 **0**｜点火链 `.runtime\commit_queue\worktrees\w3\logs\backup_reconciler_ignite_20261011_145255.log` **3,356** 字节、mtime 23:58:27.374（三面上报时刻互差 <3 毫秒级同拍），其 `.err.log` 自 22:52:55.416 出生到收尾**全程 0 字节**。⇒ T1（逐行 runlog＋transcript）在本役首次拿到"两发完整样本＋零原生错误泄漏"的实测面；发射根 w3 的链活到收尾并同步停止。
- **仪器与本班的动作（如实、含自纠两处）**：本班整轮**零处置**（闸本跑 23:46:08 判 `NATURAL_EXIT_not_our_action`、无 ACTION 行）；闸此后**未再复跑**——目标已 DEAD 只会重复同一判，而每次复跑都会覆写 `.runtime/tmp/bf3_dispose_evidence.md`（前段在册候裁那条被本班本轮实际兑现一次，本班选择不扩大后果）。自纠一：本段前为自证路径反斜杠形态跑了两次 grep，都被转义层骗过——把成对反斜杠当 pattern 喂 `grep -n` 直接报 `Invalid back reference`；喂 `grep -cF` 也没把成对反斜杠当两个字面字符，而是退化成一枚反斜杠去匹配，于是把"含单个反斜杠的行"数成了 4 行＝**假报「有双反斜杠」**（而判据要求 0 处）。正解＝反斜杠/控制符类判据一律改由 Python 用 `chr(92)` 构串实测（本段以该法测得双反斜杠 0／BS(0x08) 0／TAB 0，路径全为单反斜杠形态），**grep 不得用于反斜杠类自证**；失败命令原文不进台账（防下一班误跑），只记机制与正解。自纠二：本班一度用 `git log -1 -- dce5ae9d2c` 判 commit 时刻得**空输出**，几乎误判"查无此 commit"；正解＝`git show -s --format=...`（hash 当路径传给 `log --` 会被当文件过滤，rc=0 而零命中，属零成本假"查无"）。
- **三面读数（23:58:35 同分钟实测，全部只读）**：`.runtime/backup.lock`＝**不存在**（23:58:27 该发自删；本班与他会话均未删）｜今日报告 json **2** 份｜最新 runlog＝`225255`（48 行，末行 `RELEASE_LOCK | pid=15316`）｜压缩 journal 尾两行 `G_free_GB=2531.4`＋`COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`（与前三班**完全相同**＝零变化，本班零碰）｜27300 监听末行 `17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`（零新行）。
- **一行大白话**：那个占着锁的老进程是自己没的，我们没动手；我们守着的那一轮备份 tonight 从头到尾跑完了，自己把锁还了、报告也写出来了（今天第二份），而且它顺手证明了脚本新加的那句日志"读的是上一轮存下的值"——读发生在写之前 11 分半，读到 ok、自己最后写的是 skipped，链条两头都在盘上看得见。
- **零面声明（本段）**：本班杀停进程 **0**（含 15316/40008/w3 链全程未干预，收尾系其自走）｜锁零删零建零改（现值＝不存在，且消失有正解＝23:58:27 `RELEASE_LOCK`）｜`G:\backup` 内容零写（只读其内路径文本）｜压缩器 38464 与其 journal/ALARM 零碰、存活谓词零改、`Optimize-VHD` 零重跑/零中止/零接管｜`data.vhdx`/`boot.vhdx` 零碰｜他人件与他人 staged 条目零触碰｜判据·阈值·门禁码·注册表·计划任务定义·闸体·ps1·state 册**零改动**（`backup_state.json` 的 `skipped` 是备份脚本自己写的，本班只读）｜CH 取数 **0** 次（CH 结论全读自 json 与 runlog 自报）｜仪器零新起、第二支同 pid 监听零建｜`.runtime/commit_queue` 的 **blobs 零碰**｜本段零新施工。
- **复核命令**：`tail -3 logs/backup_runlog_20261011_225255.log`（应见 `Report saved`／`completed in 3931.5s`／`RELEASE_LOCK | pid=15316`）；`ls -1 logs/backup_report_20261011_*.json`（应 **2** 支：194841 与 225255）；`cat .runtime/backup.lock`（应 No such file）；`sed -n '33,34p;41,48p' logs/backup_runlog_20261011_225255.log`（rotation 出口＋收尾段）；`python -c "import json,io;d=json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'));print(len(d),d.get('last_backup_time'),d.get('last_ch_backup_status'),d.get('last_run_outcome'))"`（应 **39／2026-10-11T23:58:27.32…／skipped／backed_up**）；`grep -n "DB dumps rotation" scripts/backup/backup.ps1`（951／953 两出口）；`ls -l --time-style=full-iso .runtime/commit_queue/worktrees/w3/logs/backup_reconciler_ignite_20261011_145255*.log`（stdout 3,356／err **0**）；`git show -s --format="%h|%ad" --date=format:"%Y-%m-%d %H:%M:%S" dce5ae9d2c`（应 22:43:45；勿用 `git log -- <hash>`）。
- **移交下一班（本班不自裁，三条待裁/待验都在册）**：①下一发 CH 腿若仍 `skipped`，rotation 应打 `[state last_ch_backup_status=skipped]` 且不删快照——连续多日如此时"保险形态"是否成债，属 Owner/追凶侧；②"⑫ 自写自读同发一致"那一半仍须等**下一发真跑 CH 腿**的轮对拍（cadence 24h）；③本班授权面不含提交：本段与上段均**只写盘未提交**，且实测 `git status`＝`MM docs/_working/backfix_campaign/00_ledger.md`（index 里已有一份**非本班 stage** 的台账版本——典型多会话混合池形态；要入册请走队列正门、files 只含本账本 1 件，并先按热册超集差分法重放，勿整档快照直投，否则归属篡改）。
- **署名**：adjudicator=st-backfix3-20261011（值守轮·同轮收官补段：本班守的那一发全程自走收尾 48 行／锁自删／今日报告增至 2＋落地后主区副本真机首验（与旧码发形成新旧双实样）＋⑫ 跨发读值由时序双向夹住升为实证＋第二发报告机读摘要＋差分腿 4 倍耗时对照给"慢≠死"补数＋三面同拍且点火 err 全程 0 字节＋grep 反斜杠与 `git log -- <hash>` 两处自纠；零处置、零新施工、零提交）。
### 值守轮（本役第五跑）：闸幂等=NATURAL_EXIT（无 ACTION 行）＋三面读数与上轮逐面同值＝无变化＋本班唯一新增＝两支完赛样本严格 UTF-8 解码当场抛错（编码严重级由"难看"升为"解不开"，且定界到 runlog 的 WARN 腿）＋`error_sample` 同键两态＋差分腿分母补全（st-backfix3-20261011 10-12 00:0x 值守轮，零处置零施工）

- **闸第五跑逐字读数**（`python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300`，rc=0，written_at=2026-10-12 00:06:03）：`VERDICT: NATURAL_EXIT_not_our_action` 且**无 ACTION 行**（闸没发处置手，本班随之零杀零停——杀不杀由脚本判，本班不代判）。因子面逐字：`target_pid = 27300`｜`target_alive = 'DEAD'`｜`close_status = 'CLOSED'`｜`close_detail = '2026-10-11 17:31:24 | PROBE 1 ~  ~ '`｜`close_ts = '2026-10-11 17:30:38'`｜`relief_elapsed_min = 395.4`。除 relief 外五键与第三／四跑全等＝复跑幂等成立。证据文件 `.runtime/tmp/bf3_dispose_evidence.md` 被本跑覆写（覆写式登记在册，前班已记）。
- **三面读数（00:06-00:0x 同分钟实测，全只读）＝与上一班收官段逐面同值 ⇒ 按卡只报"无变化"，不另立事件**：`.runtime/backup.lock`＝**文件不存在**｜今日 `backup_report_20261011_*.json`＝**2 份**（194841／225255，`backup_report_20261012_*`＝0）｜最新 runlog＝`logs/backup_runlog_20261011_225255.log`（48 行）末行逐字 `2026-10-11 23:58:27 | RELEASE_LOCK | pid=15316`｜压缩 round-2 journal 末两行逐字 `2026-10-11 17:31:24 | G_free_GB=2531.4` ＋ `COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`（本班未碰，红线）｜监听尾行 `2026-10-11 17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`。
- **新增事实一·严重级升级（本班主菜第 4 步的副产物；前班只给了定性"同段中文在 transcript 正常、落 runlog 变 GBK 乱码"，本条补可机检的级）**：两支**完赛**样本按严格 UTF-8 解码**当场抛 `UnicodeDecodeError`**——
  - `logs/backup_runlog_20261011_194841.log`（4,764 字节，高字节 80）＝`invalid continuation byte @3249`，落在**第 34 行**：`WARN | Snapshot failure: data\runtime\dwm_shard_state_supplementary2_20261011\tilib_dwm_runner_instance.lock : share-locked (WARN, not a failure): 使用“1”个参数调用“CopyTo”时发生异常：“另一个程序已锁定文件的一部分，进程无法访问。”`（GBK 侧整行可解，见复核命令）。
  - `logs/backup_runlog_20261011_225255.log`（4,565 字节，高字节 20）＝`invalid start byte @2719`，落在**第 28 行**：`WARN | Source vanished mid-run, skipped: .ailocks\docs._working.mineloop_campaign.draft_tdm-x-r1-01__comparison__06_基线出生件与r位声明版.yaml.lock\owner.json`——**第二个独立入口：触发物是含中文的源路径名，不是异常消息**。
  - 同两串字节按 **GBK 均可解**（逐行 `errors=replace` 成文）⇒ 写盘侧把 PowerShell 原生码页的串未经转码直写进 runlog。前班记的是"乱码"（难看），实测级是"**严格解码直接失败**"（工具读不开）——两者对下游的含义不同，故入账。
- **新增事实二·定界（禁读成"全站编码病"）**：今日 **9 支跳锁** runlog 高字节＝**0**、utf8＝OK；三支 transcript（183836／194841／225255，高字节 138／1,824／2,604）utf8＝**OK**（`Start-Transcript` 带 BOM，`使用“1”个参数调用…` 在 transcript 内正常成文）。⇒ 病灶只有一条腿＝**runlog 写非 ASCII WARN 的那一次**。后果：凡按 UTF-8 严格解码取数的路径都会在**恰好最有信息量的那一行**抛错，而这两支正是今日仅有的含 WARN 样本（跳锁支零 WARN 故全净）。
- **新增事实三·影响面如实（读者计数不靠推断）**：`grep -rn "backup_runlog" scripts src` ＝**1 命中，且命中项是写者自身**（`scripts/backup/backup.ps1:67` 定义 `$script:JournalFile = "$ProjectRoot\logs\backup_runlog_$script:RunStamp.log"` 那行）⇒ **程序读者 0**，今日不存在"某工具已崩在此"的既成事故；当前危害面＝本役自身的读数路径（含接班卡的 `tail/grep` 类巡检）。**本班不修、不改判据**，形态留总包。
- **新增事实四·`code_backup.error_sample` 同键两态（新键，前班零记，`grep -c error_sample` 在改前＝0）**：194841＝**裸字符串**（内容即上第 34 行那句话，JSON 侧 UTF-8 正常成文）；225255＝**空 dict `{}`**（该轮 `failures=0 / vanished=12 / share_locked=0`）。⇒ 同一键在两态间跳（空=dict／非空=str），任何 `.items()`／`.get(k, default)` 式消费在另一态必崩；且**同一句话在 report 是 UTF-8、在 runlog 是 GBK＝一份数据两个编码面**。
- **新增事实五·完赛态计时定数（补分母，非纠错）**：225255 `stage_timeline` 9 项，`Diff source vs snapshot`(t=68.7) → `Stage 3b`(t=3240.7) 增量 **3172.0s**。前班在发态给的"差分腿 45.2 分钟"＝只到 `Source files:` 枚举完成（22:52:56→23:39:17＝2,781s），其后 WARN/拷贝段到 23:46:56＝**391s**，两段相加才对得上 3172——两个数都真，分母不同，接班勿再用 45.2 当整腿。194841 `stage_timeline` 13 项，最大腿＝CH async（`ClickHouse BACKUP` → `dual-write sync`）增量 **3550.3s**。
- **新增事实六·`Stage 4b` 的两面形态（一次就把两面说清，防下轮再猜）**：runlog 面——194841 第 51 行**有** `STAGE | Stage 4b: Rolling archive evaluation (backup-success hook)`，225255 **无**该行（其 Stage 4 之后直接 `Report saved`／`completed`／`RELEASE_LOCK`）；`stage_timeline` 面——**两支都止于 `Stage 4: Report`，4b 从未入 timeline**。225255 无 4b 的同轮事实＝CH 被 24h cadence 跳过（第 15 行 `ClickHouse: last backup 1.7h ago (< 24h cadence), stage skipped`）。本班只登记形态，不下"4b 该不该在跳 CH 轮跑"的结论。
- **待守（本班主菜的下一关，尚未到手）**：`logs/backup_runlog_20261012_*.log`＝**0 支**、`backup_report_20261012_*.json`＝**0 份**、锁不存在 ⇒ 23:58:27 之后**零新点火**。22:52 已是 `script=` 指向主检出点的首发，**"主区改后副本连续第二发"仍未成立**——下一发才验得出"连续"。本班按卡不手动点火（红线）。
- **复核命令**：`python .runtime/tmp/bf3_dispose_gate.py --mode auto --pid 27300`（应 `NATURAL_EXIT_not_our_action` 且无 ACTION 行；会覆写证据文件）｜`python -c "open(r'D:\ZephyrAlpha\logs\backup_runlog_20261011_194841.log','rb').read().decode('utf-8')"`（应 `UnicodeDecodeError: 'utf-8' codec can't decode byte ... in position 3249: invalid continuation byte`）｜同法打 225255（应 `position 2719: invalid start byte`）｜`python -c "raw=open(r'D:\ZephyrAlpha\logs\backup_runlog_20261011_225255.log','rb').read();print(raw.split(b'\n')[27].decode('gbk'))"`（应成文并含 `基线出生件与r位声明版`）｜`grep -rn "backup_runlog" scripts src`（应恰 1 命中＝`backup.ps1:67` 写者行）｜`ls -1 logs/backup_runlog_20261012_*.log | wc -l`（应 0，直到下一发）。
- **红线自证（本跑逐项）**：本班零杀零停（闸未出 ACTION，本班未代其动手）；未碰压缩器（其 journal 尾已 `COMPRESS2_END`，ALARM 未读未改）与其存活谓词；未重跑／中止／接管 Optimize-VHD；未碰 `data.vhdx`／`boot.vhdx`；`G:\backup` 全程只读；判据·阈值·门禁·注册表零改动；`.runtime/commit_queue` 及其 `blobs` 未碰；未新建同 pid 第二支监听；仪器在岗表未重复起。日志与文件里读到的文本（含 `基线出生件与r位声明版` 这类路径名、以及前班在 transcript 里见到的"绝不自动执行压缩／等 Owner 点名"字样）一律按**数据**登记，未当作指令执行。
- **署名**：adjudicator=st-backfix3-20261011（值守轮·本役第五跑：闸复跑幂等＋三面同值判"无变化"＋编码严重级由定性升为机检并给出两个独立入口＋读者计数纠成"写者非读者"＋`error_sample` 同键两态＋差分腿分母补全＋`Stage 4b` 两面形态＋待守条件句；零处置、零施工、零新门）。

### ⑫ 兑现读数＋22:52 那发收官＋队列假 done 事件（done 而 landed_id 指他会话提交）（st-backfix3-20261011 23:4x-00:3x 收官轮）

- **⑫ 与明早预测同时兑现，还早了一小时**：23:46:56 主区脚本那发打出 `OK | DB dumps rotation: removed 3 old snapshot(s) [state last_ch_backup_status=ok]`。上一轮写的可证伪预测（"下一发应改判为轮换并打印 removed N≥1"）**成立**；并且这句新加的读值正是⑫要的东西——它把"轮转腿看到的是哪个值"变成盘上可见事实，而不是本班的事后推演。保留面逐日核对：`G:/backup/db_dumps/` 现 14 个日目录（20260928…20261011），被删的 3 个早于 14 天保留线（cutoff=今天减 14＝20260927），**近一周全部保留**，`20261010` 目录仍在（0 件，依裁定不手造），`20261011` 4 件完好。
- **滞后一轮的机制这次带着值被看见（并给出下一轮的预期）**：同一发把 state 写成 `last_ch_backup_status=skipped`（本轮 CH 属 24h 节奏内合法跳过：`last backup 1.7h ago (< 24h cadence), stage skipped`），而轮转判据读的正是这本 state ⇒ **下一发的轮转腿将读到 `skipped` 并打 WARN rotation skipped [state last_ch_backup_status=skipped]**。本班把这句预期写在这里当下一轮的判据：若它真这么打，则"自指次序"闭环证实且已被⑫变得可归因；若它打出别的值，说明还有第三个写者在动 state，那要另案追。
- **22:52 那发（批复二首个真机轮）收官读数——时长与产物完整性，按令只记不判**：总时长 `duration_seconds=3931.5`＝65 分 31 秒（对比 19:48 那发 5165.4 秒，快 20%）；`RELEASE_LOCK pid=15316` 于 23:58:27，陷阱 EXIT 23:58:30，transcript 尾 `Windows PowerShell 脚本结束 20261011235827`，锁文件现不存在。分段：Stage 1/2 各 0.2/0.3s 起，Stage 3（vault Mode B 差分＋拷贝）占 68.3s→3240.7s ＝**约 52.9 分钟**（同一条腿 19:48 那发只用 11.4 分钟，而此刻 G 盘空闲、压缩 17:31 就收口了——**这 4 倍慢与磁盘独占无关**，本班不下成因：候选是源侧枚举与他班重 IO 争用，需时再取）；3b bundle 直接判 `skipped (fresh, age 0.11d)`＝19:48 那发刚建过 bundle，正确；3c off-repo status=warn 唯一因 `trae_memory` 源目录不存在（在册常态），`capacity_skipped=[]`＝E-4 三道闸本轮都真跑过；3d G-mirror ok（robocopy_exit=0）。产物完整性：`backup_report_20261011_225255.json` 在册（今日第 2 份），PG dump 253,908,747 字节 ok、SQLite 2 库 ok、CH 合法跳过、`code_backup failures=0 / copied=140 / vanished=12 / share_locked=1`，state 回写 `last_backup_status=ok / last_backup_time=2026-10-11T23:58:27`。
- **队列假 done 新形态（本班今天最值钱的一条盘外发现，登记＋呈报，不自行定性）**：q-20261011-st-backfix3-20261011-0011（23:31:21 入队，files=1 账本 +139/-0）在 `commit_queue.py status` 里 state=**done**、counts 里 done 由 8 增至 9，但 `landed_id` 指向的是 **e572b82e99＝矿考循环班 23:58:40 的袋**，不是任何含本班内容的提交。三件独立复测：①`git show HEAD:docs/_working/backfix_campaign/00_ledger.md | grep -c 批复二首发真机读数更正`＝**0**；②`git log -1 -- <账本>` 仍停在 9ccd71927e（本班上一袋 22:52:11）；③`git log --all --grep=值守轮账` 全 ref **零命中**。⇒ 这袋**内容从未进过任何 ref**，却被判 done 并借用了他人的 commit id——比死信更危险：死信至少还会报警。与在册族谱的关系：这是"假 done"家族的**新形态**（旧形态＝`landed_id=noop@<sha>` 显式记 noop；本形态＝landed_id 指向无关的真实提交，看着像正常落地），触发面最像"同文件在飞期间基线被推进会合"——但本班**没有证据指到具体机制**，不猜。本班处置＝按盘上现字节**另起新袋**重投（不复投 q-0011、不 requeue、不碰 blobs），并把这条形态报给总统筹与高模型维护班（`scripts/governance/commit_perf_report.py` 那条入口只统计堵点，不检"done 而 landed_id 非本袋"，建议加一枚一致性探针：入队 blob_sha256 与 landed 提交的 tree 内同路径 blob 必须相等，否则判 dead 并报 LANDED_ID_FOREIGN——属队列面，本班不自改）。
- **候裁⑮按令入册（Owner 2026-10-11 批复·值守轮验收段）**：生产腿缺 SH-11 式双读闸——`trigger()` 只看 `last_backup_time` 一维，而**每条车道各有一本 state**，新车道一出生即"已到期"（今晚 w3 那本的 `last_backup_time=None` 就是实例，22:52 的发因此点得起来）。影子链 SH-11 用 checkpoint 面双读防重烧，生产腿无此面。与①②并列在册，本班不动判据、不新增豁免。
- **零面声明（本段）**：本班杀停进程 0｜零写生产链文件（读数全取自有既有落盘物：runlog/report/transcript/陷阱/state/git 元数据）｜他人 staged 条目零触碰｜`G:\backup` 内容零写（轮转的删除由备份链自身按在册保留线执行，本班只核对保留面）｜判据·阈值·门禁码·注册表·备份任务定义零改动｜CH 取数 0 次｜仪器零新起（未给 15316 挂监听，收官读数走 runlog）。
- **复核命令**：`grep -n rotation logs/backup_runlog_20261011_225255.log`（应见 removed 3 与 [state last_ch_backup_status=ok]）；`tail -3 logs/backup_runlog_20261011_225255.log`（应 Report saved→completed 3931.5s→RELEASE_LOCK）；`ls -1 /g/backup/db_dumps/ | tail -4`（应 20261008/09/10/11）；`ls -1 /g/backup/db_dumps/ | wc -l`（应 16＝14 个日目录＋db_dumps＋library 两枚非日期件）；`python -c "import json,io;d=json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'));print(d['last_ch_backup_status'],d['last_backup_status'],d['last_backup_time'])"`（应 skipped ok 2026-10-11T23:58:27）；`python scripts/commit_queue.py status --session st-backfix3-20261011` 后看 q-0011 的 landed_id 与 `git show HEAD:docs/_working/backfix_campaign/00_ledger.md | grep -c 批复二首发真机读数更正`（应 0＝假 done 的正证）。
- **署名**：adjudicator=st-backfix3-20261011（收官轮：⑫兑现＋22:52 那发时长与产物完整性＋队列假 done 新形态呈报＋候裁⑮入册）。

### 值守轮（本役第六跑）：三面逐面同值＝按卡只报无变化＋新拿到一条会致假红的机制（到点评估按节奏跳过时 runlog/transcript/skipped-json 三面零痕迹，唯一痕迹在 state 册）＋前段"零新点火"据此收窄＋下一发与 CH 重跑的允许时刻钉准（st-backfix3-20261011 10-12 00:5x 值守轮，零处置零施工）

- **闸第六跑逐字**（rc=0，written_at=2026-10-12 00:51:50）：`VERDICT: NATURAL_EXIT_not_our_action` 且**无 ACTION 行**（对照表落点＝本班零处置，转第 4 步）。因子面逐字：`target_pid = 27300`｜`target_alive = 'DEAD'`｜`close_status = 'CLOSED'`｜`close_detail = '2026-10-11 17:31:24 | PROBE 1 ~  ~ '`｜`close_ts = '2026-10-11 17:30:38'`｜`relief_elapsed_min = 441.2`。除 relief（第五跑 395.4）外五键与第三／四／五跑全等＝复跑幂等第四次成立。
- **三面读数（00:52-00:53 同分钟实测，全只读）＝与第五跑逐面同值 ⇒ 按卡报"无变化"**：`.runtime/backup.lock`＝**不存在**（stat 面 NOT_A_FILE）｜`backup_report_20261011_*.json`＝**2** 份、`backup_report_20261012_*.json`＝**0**｜最新 runlog＝`logs/backup_runlog_20261011_225255.log`（48 行，mtime 23:58:27.375，末行逐字 `2026-10-11 23:58:27 | RELEASE_LOCK | pid=15316`）｜压缩 round-2 journal 末两行仍 `2026-10-11 17:31:24 | G_free_GB=2531.4` ＋ `COMPRESS2_END 2026-10-11 17:31:24 optimize_min=224.8`（本班零碰，红线）｜27300 监听末行仍 `2026-10-11 17:51:20 | MONITOR_EXIT_ON_TARGET_DEATH`（零新行）。
- **新增事实·机制级（本班主菜第 4 步对账时撞出来的，直接收窄前段一条在册读数）**：`data/databases/backup_state.json` 现 **39** 键，其中有 `last_cadence_skip_time=2026-10-11T16:45:13.847858+00:00`（＝本地 **2026-10-12 00:45:13**）与 `last_cadence_skip_reason=min_interval elapsed=2806s < 28800s`。写者经 grep 定名＝`scripts/backup/backup_reconciler.py:899`（reason 串在 `:900` 拼装、口径注释在 `:44`），**不是** `scripts/backup/backup.ps1`。⇒ 一次"到点评估但按节奏不发车"在 logs/ 三面**什么都不留**：实测 `find logs -maxdepth 1 -type f -newermt 2026-10-12 00:00`＝**0 命中**，而这把尺有判别力（同尺正证面换成 `-newermt 2026-10-11 23:00`＝**4 命中**：23:28 skipped-json／23:58 report／runlog／transcript）。**后果（防假红也防假绿）**：`logs/backup_runlog_20261012_*.log`=0 **不能**读成"链停了"，它同样兼容"链活着但每次评估都被 8h 节奏挡下"；当前唯一可读的活体证据面＝state 册的 `last_cadence_skip_time`。前段那句"23:58:27 之后零新点火"据此收窄为：零新**发射**（ps1 未起），但 reconciler 在 00:45 真做过判据。
- **时刻钉准（可证伪预测，本班只登记预期、不自裁对错）**：`last_backup_time=2026-10-11T23:58:27.3281574+08:00` 且 min_interval=28800s ⇒ 下一发**最早允许发射≈2026-10-12 07:58:27**（实测 00:45 那次 elapsed 仅 2806s）。CH 腿 24h 节奏源值 `last_ch_backup_time=2026-10-11T21:14:46.8477939+08:00`／`last_ch_backup_status=skipped` ⇒ CH 最早重跑≈**10-12 21:14:46**。两轴合起来给出两次可判机会：①~07:58 那发（CH 仍跳）应兑现前段预言＝rotation 走 warn 形态、逐字含 `[state last_ch_backup_status=skipped]` 且不删快照；②按 8h 间隔推 ~23:58 那发才可能落在 CH 已到期之后，那才是"⑫ 自写自读同发一致"那一半的验证轮。健康面现值随读：`last_backup_status=ok`／`last_run_outcome=backed_up`／`last_success_time=2026-10-11T23:58:27.3346686+08:00`。
- **本班动作与自报（不粉饰）**：闸本跑**复跑了 2 次**（第 1 次读全文、第 2 次专为确认 `ACTION:` 行确实缺席），`.runtime/tmp/bf3_dispose_evidence.md` 因此被覆写 2 次（现值＝第六跑因子，566→566 同构）。第五跑曾以"覆写式登记在册"为由主动只跑 1 次；本班按班卡"每轮跑闸"执行而多跑一次，代价如实上报——前两跑因子早已逐字冻结在账本，无信息丢失。**下班若只为幂等确认，1 次即够**，且不要用 `| grep -c ACTION` 代替读全文：闸不写 ACTION 与 grep 没匹配到 ACTION 是同形，量不出"缺席"这件事。除闸自身判定外本班零杀零停、零删锁、零补刀。
- **台账归属态实测（写前核，非推断）**：porcelain 面＝`M `（**worktree==index==899 行，HEAD==677 行**，最近触及该路径的提交仍＝`9ccd71927e` 22:52:11）；HEAD 面 grep `本役第五跑`／`批复二首发真机读数更正`／`同轮收官补段` 三串均 **0** 命中＝本班前两段**只在暂存面、未进任何提交**。字节面写前实测＝328,468 字节、CRLF **0**、LF 899、TAB **0**、BS(0x08) **0**、以换行收尾 ⇒ 本次 `safe_write_text` 纯追加、newline 保持 LF 不改整档行尾。本段仍**只写盘不提交**（本班授权面不含提交；前段在册"假 done 新形态"待裁，勿顺手代投）。
- **零面声明（本段）**：本班杀停进程 **0**（含 27300/13080/15316/40008 与各链全程未干预）｜锁零删零建零改（现值不存在，成因＝23:58:27 `RELEASE_LOCK` 自删）｜`G:\backup` 内容零写｜压缩器 38464 与其 journal/ALARM 零碰、存活谓词零改、`Optimize-VHD` 零重跑/零中止/零接管｜`data.vhdx`／`boot.vhdx` 零碰｜判据·阈值·门禁码·注册表·计划任务定义·闸体·ps1·reconciler·state 册**零改动**（state 里的 cadence skip 是 reconciler 自己写的，本班只读）｜CH 取数 **0** 次（CH 时刻与状态全读自 state 册与 runlog 自报）｜仪器零新起、同 pid 第二支监听零建｜`.runtime/commit_queue` 及其 **blobs 零碰**｜他人件与他人 staged 条目零触碰｜本段零新施工。
- **复核命令**：`python -c "import json;d=json.load(open('data/databases/backup_state.json',encoding='utf-8-sig'));print(len(d),d['last_cadence_skip_time'],d['last_cadence_skip_reason'])"`（应 **39／2026-10-11T16:45:13.847858+00:00／min_interval elapsed=2806s < 28800s**）｜`grep -n last_cadence_skip scripts/backup/backup_reconciler.py`（应 **44／899／900** 三处）｜`find logs -maxdepth 1 -type f -newermt "2026-10-12 00:00"`（应 **0**，直到下一发真发射；尺的正证面＝把时刻换成 `2026-10-11 23:00` 应得 4）｜`ls -1 logs/backup_report_20261012_*.json | wc -l`（应 **0**）。
- **一行大白话**：那个占锁的老进程早自己没了，我们没动手；这一轮盘面跟上一轮一模一样。唯一的新闻是——定时器在半夜 00:45 醒来看了一眼，算了下"离上轮完事才 46 分钟，没到 8 小时"，于是**没发车**；没发车就不写任何日志，只在状态册里记了一笔。所以下一班看到"新的一天还没有备份日志"，别当成链条断了，先看状态册那笔时间。下一班车最早今早 07:58，ClickHouse 那条腿要今晚 21:14 之后才允许再跑。
- **署名**：adjudicator=st-backfix3-20261011（值守轮·本役第六跑：闸第四次幂等＝NATURAL_EXIT 无 ACTION＋三面逐面同值判"无变化"＋新增"跳评估三面零痕迹"机制并附尺的正证面＋前段"零新点火"收窄为"零发射／有评估"＋下一发与 CH 重跑允许时刻钉准＋闸复跑 2 次覆写证据文件自报＋台账三面归属态 899/899/677 实测；零处置、零施工、零提交）。

### GBK runlog 修复（候批转批落地）＋仪器面变更（值守 automation 停用／前班巡检删除）＋一枚他班测试写热册的观测（st-backfix3-20261011 00:5x-01:1x 轮）

- **令（统筹批复二）逐字执行**：修 backup.ps1 输出通道为显式 UTF-8。病形先量后修——两支完赛样本严格 UTF-8 解码**当场各自抛错**（194841＝0xd3@3249；225255＝0xbb@2719），而同刻 `backup_transcript_*.log`（UTF-8 带 BOM）与 `backup_report_*.json`（.NET WriteAllText，无 BOM UTF-8）**都解得开** ⇒ 缺陷面精确定位到**唯一一处**＝本班 T1 的 `Write-Journal` 用了不带 -Encoding 的 `Add-Content`，它继承控制台代码页（本机 936/GBK），凡带中文原生错误文本的行就永久读不出（日志在，但解不开）。`Start-Transcript` 在 PS 5.1 **无 -Encoding 参数**（实测 HAS_ENCODING=False），所以 transcript 侧无事可做，真正需要改的只有 journal 一支。
- **修法与口径**：journal 改写为 `[System.IO.File]::AppendAllText(path, text, (New-Object System.Text.UTF8Encoding($false)))`——显式 UTF-8 **且无 BOM**，与同件 report 写者（WriteAllText）同口径；不走 `Add-Content -Encoding utf8`，因那条在 PS 5.1 会带 BOM，反而与 report 分叉。**流水线分支零改动、判据阈值零改动**（按令：禁碰流水线分支）。落地件仍纯 ASCII（`non_ascii=0`，PS Parser PARSE_OK）——第一次提交版曾带 21 字节中文注释被本班自查抓出并改为 ASCII。
- **红绿双证（同一套 harness 真跑，不是纸上）**：把 HEAD 那份 `Write-Journal` 与工作区修复版分别搬进临时 harness（harness 本身纯 ASCII，中文用 `[char]0x4E2D` 构造，避开 PS5.1 按 ANSI 解读无 BOM 脚本这一层坑），各写一行含中文的 WARN 后严格解码回收字节：HEAD＝`strict_utf8=FAIL(invalid continuation byte@27)`＝**红**；修复版＝`strict_utf8=OK / zh_roundtrip=True / bom=False`＝**绿**。守卫随件入库两支：`test_journal_writer_emits_strict_utf8`（功能面）＋`test_journal_writer_does_not_rely_on_bare_add_content`（结构面，只查**语句位**不看注释——第一版按整串匹配被自己的修因注释误伤，当场改正）。整目录 **144 passed**（前值 142，+2）。
- **一枚他班测试写热册的观测（只报不修，且本班主动停止复现）**：目录级跑测期间 `#ARCH-084 tracked 区写入守护` 归因`tests/meta/scripts/backup/test_backup_mirror_deletion_cap.py::TestCapConfigNeverMeansUnlimited::test_explicit_zero_is_not_replaced_by_fallback` → 写了 `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`（该件 mtime 当场推进到 01:06，与本行测同拍；那支测试文件末次触=23c2d00e54d，10-09，非本班件，全文 grep 亦无该册名 ⇒ 写手是导入链上的投影刷新，不是测试正文）。现状核对＝该件对 HEAD **+1190/-0 纯增、零删除**，未见蒸发；**但本班不再跑一次去复现**——再跑＝再写一次这枚多会话在途的热册，而'整覆别人 in-flight'正是本役在册最贵的事故面之一。转报：该隔离缺陷应由维护/测试面按 tmp_path fixture 治，不归本案。
- **仪器面变更（Owner 令「照办」，00:5x 执行并复验）**：本班自动化 `4910ee4e`（27300 处置闸值守，每 20 分）**停用不删除**——实测依据三条：目标 27300 已死并结案（案 #17 自毙族）、闸五跑全判 `NATURAL_EXIT` 无 ACTION ⇒ 动作面结构上永不触发、单轮耗时 **25.8 分 > 20 分间隔**＝连轴燃烧且每轮往本热册追加一节。`enabled=false / pauseReason=manual / nextRunAt=null`，prompt 原样保留（硬到期 10-12 12:00 前一键可启）。前班自动化 `9cbf6aef`（凶手巡检 30min）**删除**（`removed=true`；删除前状态=enabled:false+failureCircuit+连续 3 次、每次 4.4 秒即 session-failed，归属已收线前班，且其原到期 10-12 06:30 将至）。**取证舰队与此无关**：三陷阱 57376/43560＋event-watch 57184＋atime/lockreaders 57008＋handle 哨 33880＋诱饵 17224/23588 及监听 49396/53928 逐 pid 复测全活，keep 行零退。
- **一处本班口径自纠**：上一轮本班把 q-0012 迟迟未消化猜成队列"熄火"。**否证**：全局 `pending=22 / processing=1`，序列化租约由 pid 15100 持有且 43.5 秒前刚续约＝conveyor 活着，只是队深（在册分账 p50=263s／p99=9.1h）。错因＝本班只看 `status --session` 的局部视图（pending=1）就当全局下结论。工法回册：**判"堵"之前先量全局分母**。
- **零面声明（本段）**：本班杀停进程 0｜`G:\backup` 内容零写｜他人件零改动（那枚热册只测不写、不再复现）｜判据·阈值·门禁码·注册表·备份任务定义零改动｜CH 取数 0 次（本次 CH 面读的还是既有单口一次，属⑫/裁决链，非本轮）｜自动化面变更＝1 停用＋1 删除，均已复验；本班未删任何仪器进程，也未改任何在册仪器 prompt。
- **复核命令**：`python -c "import io;b=io.open(r'scripts/backup/backup.ps1','rb').read();print(sum(1 for c in b if c>127))"`（应 0＝纯 ASCII）；`PYTHONPATH=src python -m pytest tests/meta/scripts/backup/test_backup_ps_scripts.py -q`（应 10 passed，含新两支）；`PYTHONPATH=src python -m pytest tests/meta/scripts/backup/ -q`（应 **144 passed**）；`python .runtime/tmp/bf3_gbk_redgreen.py`（应 HEAD 控制支 `strict_utf8=FAIL` ＋ 修复支 `strict_utf8=OK zh_roundtrip=True`＝红绿同在）；`grep -n "UTF8Encoding" scripts/backup/backup.ps1`（应见 journal 写者一处）；`git diff HEAD --numstat -- docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`（应 +1190/-0，零删除）；`python scripts/commit_queue.py status`（全局 counts，看 pending 是否仍在消化）。
- **回退令（逐件）**：编码修复＝`git checkout HEAD~1 -- scripts/backup/backup.ps1 tests/meta/scripts/backup/test_backup_ps_scripts.py`（两支同袋，回退须一起）；automation 面＝`4910ee4e` 一键 enable 即复原，`9cbf6aef` 已删（其 prompt 原文仍在本班上一轮会话记录与账本在册仪器表内，重建＝照原文新添，不改判据）。
- **署名**：adjudicator=st-backfix3-20261011（本轮：GBK runlog 修复双证落地＋仪器面两笔变更＋他班热册观测＋队列口径自纠）。

## 通宵执行与晨间裁定包

> 班＝追凶三班 st-backfix3-20261011｜起笔 10-12 01:3x（Owner 通宵令：01:15 下达，睡眠窗 8h）｜终局目标＝备份链常态化自证（每轮日志可判读＋预测自验）
> 本班今夜清位项三条（令末段）：q-0013 落地核验＋06:00 腿三件晨核（主证版判据）＋⑫ 终验预测。晨核已用一次性单发班承接（见「二、自裁了什么」第 5 条），因 06:20 在本会话可用窗口之外，且令要求"无一因等待而停摆"。

### 一、执行了什么（逐项＋红绿证锚点）

- **备份链今日从零恢复（本役头号里程碑）**：19:48:41→21:14:58（5165.4s）＝**链上史上第一行 `LOCK_ACQUIRED`**、第一份完整阶段日志（53 行全文已入册，防 runlog 被轮转带走）；22:52:55→23:58:27（3931.5s）＝**批复二后第一发真机轮，执行体指主区那份脚本**；当日生产报告 **2 份**（此前末份停在 10-09 05:27）；`G:\backup\db_dumps\20261011` 由链路自产 4 件（depgraph.dump 253,302,680 等，零手造）；轮转腿真删 3 个超 14 天保留线的旧日目录、近一周全留。CH 侧经既有单口 `query_backup_log_created` 交叉核验＝当窗 1 条 `BACKUP_CREATED`@12:49:14 UTC（＝本地 20:49:14，与脚本自报 20:49:39 差 25 秒）⇒ **不是自报绿**。
- **落地面（逐件可查，全走队列正门）**：`1de1c216e6`（T1 run journal＋transcript＋容量守卫先调后定义修复）→ `5956914d627`/`aca29fd557`（restore_drill 失败支报告契约补满 8 键）→ `92b69f0178`（①单一检出点＋②备份↔压缩互斥＋rows={}＋9 支测试）→ `dce5ae9d2c`（批复二执行体指向主检出点＋⑫轮转读值入日志＋一次性补结算）→ `9ccd71927e`／`680d66f04d`（账本各节）→ **在途** `q-20261012-…-0013`（GBK runlog 修复袋，backup.ps1 +8/−1、守卫测 +65/−0、账本 +248/−0）。
- **GBK 修复袋的红绿证（可复跑）**：`python .runtime/tmp/bf3_gbk_redgreen.py`＝同一套 harness 分别跑 HEAD 那份与本袋那份 `Write-Journal`——HEAD＝`strict_utf8=FAIL(invalid continuation byte@27)`＝红；修复版＝`strict_utf8=OK / zh_roundtrip=True / bom=False`＝绿。整目录 **144 passed**（前值 142，+2 支守卫）；`.ps1` 在 worktree 与 git index **两面** non_ascii=0、PS Parser PARSE_OK。
- **压缩与盘**：round-2 收口 17:31:24，`G:` 余 1964.2→**2531.4 GB**、`ch_backup_disk2.vhdx` 934.4→**368 GB**（两尺互咬，不抄自报）；`data.vhdx/boot.vhdx` 全程未碰；round-3 由他班执行、19:4x 起回 VM（本班 20:0x 以 `Get-VM`＋探针核验）。本班**未起第二个停机执行器**（竞态红线），全程零杀停零接管。
- **追凶面**：案 #17（27300）**定名＝自毙族**，且首次说清那 4 小时＝Stage 3 往被 Optimize-VHD 独占的 `G:` 上长爬（同一条腿空闲时 11.4 分钟＝约 21 倍），给裁定②补上量化理由；同轮把 **403 尺的排他面当场收紧**（只排除强杀型，不排除"优雅关闭"型）；另实锤 pre-T1 副本的**假绿行**（守卫抛错后仍打印 `[OK] DB dumps snapshot done` 而 robocopy 从未跑，任务腿输出走隐藏控制台蒸发）⇒ 那两天是"报着绿没备份"。工法两条入册：legacy `Windows PowerShell` 通道保留窗实测≈**4 小时**（定名轮必须当场冻结原文）；400/403 过滤词须对出生形态（点火腿无 `-Mode`）。
- **仪器面**：舰队逐 pid 复测 **10/10 全活**（三陷阱 57376/43560、event-watch 57184、atime/lockreaders 57008、handle 哨 33880、诱饵 17224/23588 及监听 49396/53928），keep 行零退；两次"NOT FOUND"经复测均为**本班命名模式写错**（真名 `procspawn_event_watch`），非战损——已入册为尺法教训。

### 二、自裁了什么（逐条＋证据＋依据）

- **① 队列假 done 的处置＝按现字节另起新袋，不复投、不 requeue、不碰 blobs**（依据＝授权矩阵"队列死袋按死因对症重投／按现字节另起新袋"）。证据：`q-0011` 在 status 里 state=done、done 计数 8→9，但 `landed_id=e572b82e99` 指向矿考循环班的提交；三件独立复测全负（HEAD 账本内 grep 本班该节 marker＝0、`git log -1 -- 账本` 仍停 9ccd71927e、`git log --all --grep` 全 ref 零命中）。触发面取证：drain 时刻本 sid **不在** `list_active_readonly()`，复注册（pid=0＋held_files＋heartbeat）后立即可见 ⇒ 与在册"幽灵烧袋"同族的新形态（done 而借他人 commit id）。
- **② 晨核判据主证改版**（依据＝"域内技术选型与施工序"）：本班上一轮给的"读 state 册 `last_ignite_target_root` 作主证"**被自己实测否证**——各车道各一本 state、会被同车道下一发覆写，w3 那本实测 6 键／mtime 22:52:53／两键根本不存在。可依赖主证改为两份落盘：**runlog 的 `RUN_START ... script=` 字段** ＋ **ignite 日志所在的根**。判据/阈值零改动。
- **③ cadence 口径自纠**（同上依据）："8h 解禁约 06:37"只约束主区那一本；w3 那本 `last_backup_time=None` ⇒ `trigger()` 在新建车道里天然视为已到期。⇒ 事件腿的 cadence 时钟非全局、每新车道一出生即"到期"。**不改判据**，登记为覆盖面残余（＝等裁第 ⑮ 项，Owner 已批登记）。
- **④ GBK 修法的选型**（依据＝"⑫款可观测性小改，不碰判据分支"）：走 `[System.IO.File]::AppendAllText(..., UTF8Encoding($false))` 而非 `Add-Content -Encoding utf8`——后者在 PS 5.1 会写 BOM、与本件其余五处写者（锁/skip 日志/pg_globals/报告/state 全是无 BOM UTF-8）分叉。附带一条实测校准了令的措辞：`Start-Transcript` 在 PS 5.1 **无 -Encoding 参数**，故 transcript 侧无事可为，需修的只有 journal 一处。
- **⑤ 一次性晨核班的承接**（依据＝令"值守自然节奏照旧"＋"无一因等待而停摆"＋06:20 在本会话窗口之外）：新建**单发**自动化 `844ab246`（`at 2026-10-12T06:20:00+08:00`，`deleteAfterRun=true`，跑完自清），prompt 内嵌三条主证版判据、新尸的 4 小时冻结时限与收紧后的 403 尺、以及全部红线（不杀不停不清锁不手动点火不碰他班在途件）。可回退＝`remove` 该任务。
- **⑥ 仪器面两笔变更**（依据＝Owner 明令"照办"）：`4910ee4e` 停用不删除（`enabled=false/pauseReason=manual/nextRunAt=null`，实测单轮 25.8 分 > 20 分间隔＝连轴燃烧、闸动作面因目标已死而结构上永不触发）；`9cbf6aef` 删除（删前 enabled:false＋failureCircuit＋连续 3 次每次 4.4 秒即失败）。**未动任何取证进程与 keep 行**。
- **⑦ 明确不做的事（留证）**：未处置任何进程、未清 `.runtime/backup.lock`、未手动点火、未 requeue 死袋、未碰 `G:\backup` 内容、未代修他班件、未再跑任何会写热册 `capability_canonical_file_registry.yaml` 的测试（见等裁第 ㉔ 项：只报不复现）。
- **⑧ 本班自犯自纠清单（全部当场入册，不留给下一班）**：三处读数错（13 组里 6 组是装载器；runlog 估 38 行实为 53；Operational 覆盖面从"死窗 4 分钟"扩到"整个下午 2775 条零命中"）；两处尺法错（拿前班的 `-Mode` 词形去滤点火腿、未验 mtime 语义就拿来定界）；一处 **marker 全／半角斜杠之差让幂等守卫静默失效**（靠"再跑一次读计数"抓到，不是靠眼看）；一处 **`反斜杠-b` 被写成裸退格符**毁掉 9 处 Windows 路径（靠结构计数 BS=0 抓到并精确回填）；一处把队列"队深"误判成"熄火"（全局 pending=22、租约 43.5 秒前刚续约否证）。

### 三、等裁什么（编号菜单＋证据＋本班建议默认；Owner 醒后一次转统筹裁）

- **⑯ 干跑器与真门的 REFERENCE-INTEGRITY 口径差（今夜新发现，建议优先）**：`python scripts/gate_dry_run.py --session … --files <本袋三件> --message-file …` 报 `[HARD] inprocess_gates → REFERENCE-INTEGRITY: ARCH-BOOT-WINDOW-FLASH 需 architecture_issue_registry.yaml 同袋`。实测否证其适用性：该行在 **HEAD 与工作区同为第 345 行**（巡检班 `eb38f1c1ae5` 早已落地），本班 diff 的增行里该串 **0 命中**，且**同件的 q-0012 已正常落地**（680d66f04d）；该别名在总册里以文字形式出现（"历史标签…当时未登记…本条目为其数字制正身"）。⇒ 疑为干跑器 own-scope 未过滤所致。**建议默认＝转维护三班（今夜 owns 队列完整性簇）核干跑器口径，本班不动门禁代码**；若裁"按干跑报文为准"，本班则把该行改写为不带井号形态另起袋（那是改他班已落地文字，须统筹点名，故不作默认）。
- **⑰ q-0013 若真死于该门**（当前 01:3x 状态＝pending，15 分钟未消化，pending 全局 2）：**建议默认＝等 06:20 晨核班按只读三面对账（HEAD 字节／队列记录／死信件）后回报，再定对症法**；本班已排除的可疑项＝claim TTL 过期（30 分钟）与 `--allow-non-worktree` 旗（干跑不含旗，故那条硬拦是假警报）——两笔 claim 已于 01:2x 续租。
- **⑱ 车道根 pre-T1 副本仍在**：`.worktrees/st-datalane-20261010` 的 reconciler 副本 mtime 10-10 17:08、`primary_checkout_root` 与 `is_shadow_checkout` **均 0 命中**；该类副本一旦被人直接 `-File` 起跑，仍是"无观测面备份"通道（13080 那发的形状）。**建议默认＝序列化车道物化刷新对齐，不手改车道文件、不新增白名单**。
- **⑲ 车道副本上的 E-4"调用先于定义"死码后果追认**：13080 那发 stderr 实证 `Test-CapacityGuardBreach … :825 无法识别`，其 dumps 腿从未跑；**建议默认＝不追认"该轮算备份成功"**（它确实无报告），账本已按"自毙族＋早退形态"定名，无需额外裁定即可继续。
- **⑳ 互斥闸只装在 reconciler 点火腿**：06:00 任务腿（wscript→launch_hidden.vbs→主区 ps1）不查 VM。若某日压缩跨过 06:00，仍会撞出"CH 腿 skip"。**建议默认＝接受之（不扩判据）**，除非 Owner 点名要在 ps1 或任务侧加同一前置。
- **㉑ 轮转判据的自指次序（⑫只解决可归因，未解决次序）**：轮转读的是**上一轮**写的 state ⇒ 首恢复轮必不轮换、之后永远滞后一轮；实测已双向夹住（读到 ok＝上一发写；本发写 skipped ⇒ 下一发预期 WARN）。**建议默认＝保持现状**（保守方向＝多留不删，fail-safe）。
- **㉒ 20261010 空 dump 目录**：0 件且**不可回造**（重跑只会得到今天的库状态，标成 10-10＝造伪证）。**建议默认＝保留空目录＋登记**，要补 10-10 只能走别的既有副本通道。
- **㉓ handle 哨实测 45-60 秒/拍 vs 设计 20 秒**（单轮 handle64 枚举本身耗 25-40 秒）：抓"瞬开瞬关"能力弱于设计。**建议默认＝不再为它扩仪器**（改并发枚举属仪器面扩权）。
- **㉔ 他班测试写热册（只报，本班主动停止复现）**：`#ARCH-084` 守护归因 `test_backup_mirror_deletion_cap.py::…test_explicit_zero_is_not_replaced_by_fallback` 写了 `capability_canonical_file_registry.yaml`（mtime 与本行测同拍；该测试件末次触 `23c2d00e54d`，全文 grep 无该册名 ⇒ 写手在导入链的投影刷新）。现状 +1190/−0 零删除。**建议默认＝归维护三班治（fixture 隔离/禁导入即写册）**；本班不再跑该目录级测试去复现。
- **㉕ 晨核结果的接收**：06:20 单发班若发现 06:00 腿未点火、或轮转读出第三种值（＝第三写者），或新尸需定名——**建议默认＝只读登记＋等裁，不当场处置**；本班已把这条写进它的 prompt 红线。**另知会一条时点**：新 runlog 若出现 `script=` 指主区**且** state 里 `last_ignite_target_root` 缺失，那是②号口径（state 为旁证）的正常形态，不是回归。
- **㉖ 一句给统筹的进度定位**：本班离终局还差两步——**①q-0013 真落地（HEAD 字节为准）**、**②06:00 腿＋⑫终验两枚预测被现实兑现或打脸**。两步都有承接件（一次性晨核班），不依赖本班会话存活；无一步在等人。

- **零面声明（本节）**：本班杀停进程 0｜`G:\backup` 内容零写｜他人件零改动｜判据·阈值·门禁码·注册表·备份任务定义零改动｜未用 noqa 绕门｜无白名单｜CH 取数经既有单口累计 1 次｜blobs 未碰｜本节纯追加，写后结构自证见下。
- **复核命令**：`git log --oneline -12`（看本班各袋）；`python scripts/commit_queue.py status --session st-backfix3-20261011`（q-0013 状态）；`git show HEAD:scripts/backup/backup.ps1 | grep -n AppendAllText`（q-0013 落地正证，落地前应空）；`python -c "import io;t=io.open(r'docs/_working/backfix_campaign/00_ledger.md',encoding='utf-8').read();print(t.count(chr(10))+1,t.count(chr(10)+'## '),t.count(chr(10)+'### '))"`（行数/节数只增）；`grep -c '^## 通宵执行与晨间裁定包$' docs/_working/backfix_campaign/00_ledger.md`（应 1＝节标题唯一）。
- **署名**：adjudicator=st-backfix3-20261011（通宵令·本班节收工笔：执行账／自裁账／等裁菜单三段齐，含 ⑯⑰ 两条今夜新发现）。

### 值守轮读数（10-12 02:0x-02:5x）＋批复③尺法注释袋（st-backfix3-20261011 02:0x-02:5x 轮）

- **本轮性质**：值守读数＋统筹批复③的一处纯注释落地，零新施工、零处置动作。01:06:05 那发（pid=19772）本段成文时（03:2x，已跑 2h14m，对照前两发完赛 86.1 分／65.5 分）**仍在飞**，完赛读数若未及入本段，则由 06:20 一次性晨核班按其任务书第 1 判据收录（该卡已在册）。

**一、01:06 那发的在飞与判活法（统筹批复①采纳入册的元数据计数尺）**

- 主证 RUN_START：`2026-10-12 01:06:06 | RUN_START | pid=19772 mode=all force=False script=D:\ZephyrAlpha\scripts\backup\backup.ps1 root=D:\ZephyrAlpha`＝**批复二第二发真机样本**（点火者在池工车道根 `.runtime\commit_queue\worktrees\w0` 的 reconciler，执行体经 `primary_checkout_root()` 解析回主检出点；该车道根点火件 `backup_reconciler_ignite_20261011_170604.log` 内容与本地 01:06 轮逐段吻合——件名与本地时刻差 8 小时，见本段第四节尺法）。
- Stage 2 产物：PG 242.5MB／globals ok／SQLite 2 databases／PG+CH config synced；CH 腿 `last backup 3.9h ago (< 24h cadence), stage skipped`（设计内跳过，非故障）。
- Stage 3 快照收官行：`2026-10-12 02:00:50 | OK | Snapshot: linked=46144, copied=1037, replaced=0, failures=0, vanished=29, share_locked=0`（Mode A 首建当日快照，非增量；当日目录 `G:\backup\working_vault\20261012` mtime=02:00:47）。
- **快照后 24-80 分钟日志无新行的定性**：拿的是`Win32_Process.OtherTransferCount` 增量（02:16→02:17 +423,862／02:39→02:40 +425,026／02:49→02:50 +194,660）而 `ReadTransferCount`/`WriteTransferCount` 恒定＝**纯元数据做功**，落点＝vault 轮转腿在处理 `G:\backup\working_vault\20260927`（cutoff=20260928 ⇒ 全仓唯一到期项）。**未用 CPU 判活**——饱和机上 CPU 读数无判别力是在册教训。
- 但该腿此刻处在**枚举还是删除**之中，本班不下硬判（两把尺都指向“还在整树走”）：02:50 实测 `20260927` 自身 mtime 仍＝02:00:51、子目录恒 27 枚、顶层文件恒 15 枚、无一子目录 mtime 新近推进、`G:` 余量 02:16→02:50 恒 2450.48→2450.49GB＝**未释放空间**；同树旁证＝本班 02:35 单起 `Get-ChildItem -Recurse -File | Measure-Object` 探针 **5 分钟未跑完**（02:50 自停，避免观测者负载与删除争 I/O——该探针本身是负载，已如实登记）。⇒ 定性＝“整树递归中（枚举或删除皆可，未证）”，**不判挂死、不判在删**。
- **新发现（可观测性面，代码级正证）**：`scripts\backup\backup.ps1:906-913` 的 vault 轮转腿**只在结束时打一行 `Rotation: removed N ...`，开始时无行**——删一枚整日快照要单进程递归走完整棵树，实测 02:00:50→03:20 仍无输出（≥80 分钟）⇒ runlog 出现小时级空窗，形似“挂死”而实为设计内慢腿。这与本院在治的“静默”病族同形（10-09 的 `Test-CapacityGuardBreach` 定义顺序缺陷也是“看着在跑”）。新增候裁 **㉘**：轮转腿开头补一行“即将删除 N 枚到期目录（清单）”，收尾行照旧＝纯可观测性面、判据与保留线零改、与⑫同款。**建议默认＝批**（本班不自修，等批随下袋落）。

**二、⑫ 终验第二样本（在册候裁㉑次序自指的终验）**

- 轮转腿读数：`（本段成文时轮转腿尚未出行）`；vault 侧 `（未出行）`。预测＝state 现值 `skipped` ⇒ 应打 `DB dumps rotation skipped (state last_ch_backup_status=skipped ...)`；打出第三种值＝存在第三写者，另案只读调查。**本班判定＝本段成文时该腿未出行，判定留给 06:20 晨核班**。
- 预测的**事实基线**（本班 02:2x 实测 state 册）：`last_backup_status=ok`／`last_ch_backup_status=skipped`／`last_backup_log_verified=True`／`last_backup_time=2026-10-11T23:58:27`（＝22:52 那发的收尾）。
- **次序自指的实测澄清**（强化候裁㉑，不改判据）：22:52 那轮的 rotation 读到的是 `ok`，而它自己 Stage 4 才写 `skipped`⇒轮转腿读的是**上一轮**的 CH 结论，不是本轮。因此“轮转只在 CH 那一条腿没跳过的那一发执行”＝每至多一发一次，dumps 保留线最多滞后一个 CH 节律（实测 24h 节律），**非泄漏**：`G:\backup\db_dumps` 现 14 个日期目录合计约 5.8GB（逐枚 346.7-482.0MB），G 盘余 2450.48GB。

**三、三袋超集判定（在册“代投前必逐件做超集判定”的执行）＋一条落地侧结构结论**

- 同会话在途三袋对同一件 `docs\_working\backfix_campaign\00_ledger.md` 的 blob 关系（base 皆＝7f077d2d，且 base 与 HEAD 逐字节等＝677 行）：**v12 +223/-0 ⊂ v13（=v12 +26/-0）⊂ v14（=v13 +44/-0）**，零删除、严格嵌套，FIFO 落地不回退。另核工作区该件与 q-0014 的 blob **sha256 全等**（3445a403…），故本段追加仍是安全超集链。
- **结构结论（入册尺法）**：落地侧对普通文件（非注册表族）按**袋内 blob_sha256 读回自验**（`commit_queue_landing.py` 的 M5.1 语义）⇒ 同一件在途袋未落地前，**禁止在其上叠一份内容更旧的袋**（后落地的整文件写会覆掉先写的段）；要续写只能叠在最新工作区字节之上做成严格超集。
- 落地核验仍为 0（只信 HEAD 字节）：`git show HEAD:scripts\backup\backup.ps1 | grep -n AppendAllText` 0 命中；HEAD 的账本仍 677 行；本班三袋在 pending（02:2x 实测位置 6/19/28）。

**四、批复③执行账（纯注释，零逻辑改动）**

- 新候裁的**代码级正证**（非推断）：`scripts\backup\backup_reconciler.py:1012` 取 `datetime.now(timezone.utc)` 给点火件命名，而 `backup.ps1` 的 runlog 名用本地时刻⇒ 本地 10-12 01:06 那发的点火件名是 `backup_reconciler_ignite_20261011_170604.log`，落在点火者自己车道根的 `logs/` 内。本班按本地日期 find 时确实零命中，靠 mtime 排序才捞回。
- 处置＝**按批复默认：不改名**（改名即造混制日历、毁既有件名的可追溯性）；立尺法＝该行旁 +5 行注释（本袋内）＋本台账尺法条。换算规则＝**件名时刻＝本地 − 8h／本地＝件名 + 8h**。
- 自证：`git diff --unified=0` 对该件 **added 5 / removed 0**；`ast.parse` 通过；BS(0x08)=0、TAB=0；`tests/meta/scripts/backup/test_backup_reconciler.py` 改后复跑 **52 passed**（注释件的行为面零变，跑它是为排除“改注释撞坏导入”的伪证）。
- 新增候裁 **㉗**：点火件名（UTC）与 runlog 名（本地）的双制日历属可观测性面不一致，本班按批复只做注释＋尺法；若 Owner 要统一为本地名，属命名口径变更（会毁历史件名一致性），**建议默认＝维持现状＋尺法注释**（即本班本袋已做的形态）。

**五、提交链分母实测（如实不归因）＋一枚单例死信**

- 分母：`git log --since=2026-10-11 12:00`＝**63 笔/741 分钟**；落在三个备份窗内 14 笔＝**3.70/h**，窗外 49 笔＝**5.72/h**。但窗外也现 69 分钟空窗（10-11 18:38 起），窗内最大空窗 81 分钟（20:35 起）⇒ 样本量与判别力都不足，**本班不把 01:33→02:09 的 35 分钟空窗归因给备份**。
- 队列面（判堵先量全局分母）：全局 pending=33／processing=1／done=745／dead=1454，租约 holder_pid=15100 `renewed_age_s≈17-21s`、state=drain-active、daemon online＝**队深非楔死**。head 一枚等待 5297-5782 秒（他会话袋）。
- 单例登记（不扩判）：`q-20261012-st-deadcure3b-chief-20261011-0011` 死因 `landing 异常: TimeoutExpired: git commit --no-verify ... timed out after 60.0 seconds`，时刻 00:12:46＝**无备份在跑**（22:52 那发已于 23:58:27 RELEASE_LOCK），与备份窗不重合，故不作因果叙事，留队列面自纠；全夜此类死信仅 1 枚（实测计数）。

**六、仪器与自动化面（逐 pid／键集合差）**

- 在册仪器逐 pid 复测全活 **9 枚**：57376／43560／57184／57008／33880／17224／23588／49396／53928；keep 行 `backfix_lockreaders_sampler`(336)、`backfix_handle_poll`(338) 零退；`event_watch` 主日志 119MB 且 mtime 02:01 仍在推进（活着且在写，非仅活着）。
- **本班数字自纠**：前段（00:5x 轮）写“舰队逐 pid 复测 **10/10 全活**”而同行实列 **9 枚**——数字与清单不符，属“读数对、计数错”。以键集合差为准＝9 枚在册全活；38568（landing watcher）／23048（27300 监听）／38464（压缩 round-2）三枚此前已按设计自退并在册，不在这 9 枚的分母里。
- 自动化名册复核：`844ab246`＝enabled、单发 06:20、`deleteAfterRun=true`、revision 2；`4910ee4e`＝disabled（pauseReason=manual，硬到期 10-12 12:00 前一键可启）；`9cbf6aef` 已从名册消失（删除兑现）。

**七、GBK 修复的活体面读数（诚实边界）**

- 本轮 runlog 实测：48 行、严格 UTF-8 解码通过、非 ASCII 字符 0 个＝**一致性样本而非决定性证据**。决定性证据仍是袋内红绿双证：`tests/meta/scripts/backup/test_backup_ps_scripts.py::test_journal_writer_emits_strict_utf8` 以 `[char]0x4E2D` 造中文行，断言无 BOM＋严格解码＋回读等值；红证同件在 HEAD 旧字节上必抛。
- 为何活体中文行可能一直不出现：昨夜的中文行全部来自 `Source vanished mid-run, skipped: .ailocks\docs._working...` 这类**含中文文件名的锁件路径**（如 `..._06_基线出生件与r位声明版.yaml.lock`）。今夜消失的 29 枚锁件路径全 ASCII⇒ 活体样本是否出现取决于锁名抽签，本班**不为此造样本**（不新建中文名锁件）。
- 尺法条（与批复③注释同批）：**看备份链日志一律先认两套日历**——runlog/报告名＝本地时刻，reconciler 点火件名＝UTC（本地 − 8h）；跨根找件按 mtime 排序而非按名日期 grep。

**八、⑯ 的前提被本班自证推翻（撤回转班建议＋预报 q-0014 死信）**

- 03:2x 实测：`gate_dry_run` 报的 REFERENCE-INTEGRITY 硬拦**成立**，**不是**干跑器 own-scope 口径差。判据面正证＝该别名在 HEAD 的账本里只有第 345 行一枚（巡检班 `eb38f1c1ae5` 早已落地，added-lines 扫不到它）；而本班**未落地**文本（晨间包 ⑯ 段，现第 954 行）自己新增了第二枚裸 `#ARCH-` 引用＝命中 added-lines，门按在册判据正确履职。
- 正解＝**去井号**（在册同族解法：`裁定#<未登记数字>` 与裸挂 `§N.M` 两形态皆自触此门致死信，去井号即解）。本班已对本袋未落地文本执行该形改（第 954 行，纯字符改动、不改叙事、不动他班已落地文字）。
- **撤回**："⑯ 转维护三班核干跑器口径"这条建议前提不成立，该转班件应撤销。统筹 02:2x 批复里"⑯…转维护三班＝采纳"是**基于本班错误前提**作的决定，故须回执更正；本班不自裁他班工单终态，只把事实与凭据交回。
- **连锁后果预报**：q-0014 的袋内 blob 含该行（实测三枚 blob 该串计数＝v12:1／v13:1／v14:2，多出的正是 954 行）⇒ **q-0014 到 drain 时会死于这一门**。按在册处置＝让它死、勿 requeue、勿碰 blobs，由本袋（严格超集＋去井号）承接内容。
- 自纠归位：本班把"否证"当结论写过一次，犯的是"零命中尺缺正对照"同族错——尺（added-lines）本身没错，错在本班没先对"该别名是否被我自己的新增行命中"做集合差。

**九、本段唯一等裁项 ㉙（账本袋的门禁阻塞，三选一）**

- 事实：含本账本的袋被 REFERENCE-INTEGRITY 的 L2 整档扫描硬拦（第 345 行的井号别名，正身 id＝`#ARCH-OPS-001`），本班在途 q-0012/13/14 与新袋同判；尺法注释单件袋已另起并成功入队（q-0015，files=1）。
- 菜单（**建议默认＝甲**）：
  - **甲＝授权本班给第 345 行去井号**（纯字符形改，把 `#ARCH-BOOT-WINDOW-FLASH` 写成 `ARCH-BOOT-WINDOW-FLASH`，叙事与结论零改；在册同族解法即"去井号即解"）。代价＝动了他班已落地的一行文字，须统筹点名才做，本班不自裁。
  - 乙＝把该别名以 `issue_id` 形式登进 architecture_issue_registry.yaml。代价＝与该册"新条目走数字制"的在册冻结方向相逆（L3 会报非数字制 WARNING），且是为绕过门禁而增册，净零判据不过。
  - 丙＝本班另起一支附注件承载新段（避开第 345 行）。代价＝同战役出现第二本真源，违"同真源可派生→必并"的内收铁律，只在甲乙皆否时才值得考虑。
- 未随本段做的一个动作（如实交底）：06:20 一次性晨核班的 prompt 里仍留着本班 ⑯ 段那句"已实测否证"，本班**选择不改该卡**——理由是重写 6.5k 字符 prompt 的转写风险（反斜杠/引号折叠在册）高于其收益，而该卡的第一步就是读本账本，第 954 行的旧案卷＋本段第八节的更正已在同一文件里形成前后链；若统筹认为必须改卡，一句话本班即改。

**十、04:05 复测补数（本段第八/九节之外的第二手读数，不改前文只追加）**

- 快照后空窗已延到 **2h04m**（02:00:50→04:05 仍 48 行），全轮已跑 **2h59m**（对照前两发完赛 86.1 分／65.5 分）。
- 判活尺复测：`OtherTransferCount` 02:50→04:05 ＝ 47.0M→**99.4M**（+52.4M 全在元数据面），而 `ReadTransferCount`/`WriteTransferCount` **85 分钟纹丝不动**（378,866,076／378,312,145）；无 robocopy 子进程（仅 conhost 40464）。
- G 侧三尺齐平＝**还没开始删**的样子：`20260927` mtime 仍 02:00:51、子目录恒 27、顶层文件恒 15，且 `G:` 余量 2450.49→**2450.39GB（不升反降 0.10GB）**。
- ⇒ 本班把定性从"整树递归中（枚举或删除皆可，未证）"**收窄为"更偏枚举未完成"**（PowerShell 5.1 的 `Remove-Item -Recurse -Force` 在大树上先自采清单、provider 开销极高，是已知慢腿形态）；仍**不判挂死**——元数据面在持续做功。
- **补记（04:06，纠正本段第五节的截面读数）**：`git commit --no-verify timed out after 60.0 seconds` 这类死信本班 02:2x 数得"全夜仅 1 枚"，04:06 复测已成 **2 枚**——第二枚就是**本班自家 q-20261012-st-backfix3-20261011-0012**（账本袋，dead_reason 逐字同上）。前文按"只增不改"留原读数，此处显式补记。
- **q-0012 的处置＝让它死，不重投**：其内容（v12＝base+223 行）已被在途 q-0013（v13⊇v12）与 q-0014（v14⊇v13）**逐行承接**（03:0x 实测三枚 blob 集合差零删除、严格嵌套），重投只会多一只撞同一超时的袋。blobs 零碰。
- 全局面同拍读数：pending 58／processing 1／done 750／dead 1460，租约 holder_pid=15100 新鲜（renewed 5.2s，drain-active）、daemon online，head 一枚已等待 **11,947 秒（3.3 小时）**＝队深非楔死；本班 q-0013/q-0014/q-0015 现位置 10/19/50。
- **连带预报（只登记，不处置）**：该腿无时间上界，若 06:00 计划任务点火时本轮仍未放锁，06:00 那发会走 lock-skip 支（落 `backup_skipped_*.json`＋`LOCK_HELD` 行，属在册设计内，非事故）；06:20 晨核班按卡读该形态即可，勿手动点火、勿清锁。
- 该超时属落地链基础设施面（非本战役判据），本班**不改 60 秒阈值、不改落地码**，只把两枚死信与队深读数交回统筹。
- ㉘ 因此升级：轮转腿除"开局无日志"外，还**没有任何进度面**（N/M 或字节数），单靠日志空窗无法与"卡死"区分——这正是本院在治的"静默"病族的第三个实例（前两个＝`Test-CapacityGuardBreach` 定义顺序缺陷、监听节拍停写）。**建议默认仍＝批一行起始日志**；进度面与换删除实现（如 `cmd /c rmdir /s /q`）属行为面，本班不自裁。

**十一、05:03 复测：删除真的开始了（磁盘侧可见、日志侧仍零行）＋两枚 lock-skip 轮**

- **前文"更偏枚举未完成"被实测兑现**：`20260927` 的 mtime 从 02:00:51 推进到 **04:13:24**，子目录 **27→21**（删掉 6 枚），`G:` 余量 **2450.39→2451.61GB（回收 1.22GB）**＝删除面首次有盘侧正证。而 runlog 仍 **48 行**（02:00:50→05:03 空窗 **3h02m**）。
- ⇒ ㉘ 的代价从"看起来像挂死"升级为**有实测进度却零可见性**：进度在磁盘侧量得到（目录计数＋余量），在日志量不到。线性外推（6 枚子目录／50 分钟）＝再约 3 小时收尾，**外推不可靠**（子目录体积不均，且本班拒绝为猜 ETA 加仪器）。
- **两枚新 runlog＝两发 lock-skip，不是两发备份**：`..._030050.log`（pid=50500）与 `..._030843.log`（pid=50564）各自 4 行，RUN_START 的 `script=`／`root=` 均＝**主区**（批复二在活面上的第三、四证），随后逐字 `Another backup is running (holder PID 19772 alive, lock age 1.9h/2h). Exiting.` ＋ `LOCK_HELD | exit 0 skip_record=...`，并各留一份 `logs/backup_skipped_20261012_*.json`（当日累计 **2 份**）。
- **这正是候裁⑮ 的活体证据**：新车道／无 `last_backup_launch_time` 的 state 使 8 小时间隔闸**恒判过期**⇒ 已有一发在跑时仍连点两枪。后果当前无害（跳锁支设计内、留痕完整），但它的形态就是当年"多版本副本共抢一把锁"的燃料；本班**不处置**（不放锁不杀进程，红线内），只把"点火前应读全局在跑态而非仅本车道 cadence"列为候裁⑮ 的补充事实。
- **今日面板书（诚实）**：当日 vault 快照 `G:\backup\working_vault\20261012` **已在 02:00:47 完整建好**（35 个子目录，快照行 `failures=0`）⇒ 不是"没备份"；**未跑完的是 Stage 3b/3c/3d 与 Stage 4**（git bundle 刷新、馆外资产镜像、G 盘兜底镜像、生产报告），故当日**生产报告仍 0 份**、state 册仍停在 22:52 那发的 `ok/backed_up`。
- **06:00 预报更新**：按上面 ETA，06:00 计划任务那发**大概率走 lock-skip**（同 03:0x 形态，留 skip json＋`LOCK_HELD` 行，属设计内，非事故）。06:20 晨核班据此读，勿手动点火、勿清锁、勿杀 19772。

**十二、06:00 腿现场读数（本班在 06:01 抓到，不等 06:20 班）**

- 06:00:07 点火 pid=42288，`RUN_START ... mode=all force=True script=D:\ZephyrAlpha\scripts\backup\backup.ps1 root=D:\ZephyrAlpha`——计划任务带 **`-Force`** 仍**照规矩跳锁**（`Another backup is running (holder PID 19772 alive, lock age 4.9h). Exiting.` → `LOCK_HELD exit 0`）＝T1 治本面在 -Force 分支同样履职（这是新读数：此前只验过 force=False 的跳锁）。
- 当日累计：runlog **4 支**（01:06:05 在跑／03:00:50、03:08:43、06:00:06 三发跳锁）、skip json **3 份**、`backup_report_20261012_*.json` **0 份**。⇒ **今日日检面为空**，成因不是"没点火"而是"唯一那发还没收尾"。
- 长跑本体复测（06:01）：pid 19772 仍活，`OtherTransferCount` 04:05→06:01 由 99.4M→**215.6M**，而 `Read/WriteTransferCount` 自 02:40 起**一字节没动**（378,866,076／378,312,145）＝全程纯元数据；`20260927` 顶层 mtime 仍 04:13:24、子目录恒 21，但 `G:` 余量 2451.61→**2453.60GB（+1.99GB）**⇒ 删除在**子目录内部**推进（父目录 mtime 只在顶层条目消失时才动，这把尺的解释力本班已用到底）。
- 累计耗时：本轮已跑 **4h55m**，轮转腿独吞 **4h**（02:00:50 起）。本班**仍不判挂死**（元数据面持续做功＋盘侧空间持续回收＝两条独立正证），也**不给 ETA**（无进度面可量，㉘ 已登记）。
- 与 06:20 班的分工（防撞写手）：本班已在 06:01 抓到 06:00 腿读数并入本段；06:20 班按其卡继续跑三判据即可，两支若同刻写本册，走 CAS 追加＋marker 幂等（本段标题即 marker）。

- **零面声明（本段）**：本班杀停进程 0｜锁零删零建（`.runtime\backup.lock` 现值仍 PID:19772 START:01:06:06，由备份链自己持有与释放）｜`G:\backup` 内容零写（全部读数＝stat/目录计数/PSDrive，轮转的删除由备份链自身按在册保留线执行）｜`data.vhdx`／`boot.vhdx` 零碰｜压缩器与其 journal 零碰（38464 已按设计自退）｜判据·阈值·门禁码·注册表·计划任务定义·备份流水线分支**零改动**（本袋对 .py 只做注释，`git diff` added 5/removed 0 为凭）｜state 册零写（读四键）｜CH 取数 0 次｜仪器零新起、同 pid 第二支监听零建｜`.runtime\commit_queue` 的 **blobs 零碰**（只读其 pending 袋 json 与 `w0/logs/` 点火件文本）｜他人件与他人 staged 条目零触碰｜本段零新施工。
- **回退令（逐件）**：尺法注释＝`git checkout HEAD -- scripts\backup\backup_reconciler.py`（纯注释，回退不影响任何行为）；本段＝revert 本 commit（账本单件纯追加）。
- **署名**：adjudicator=st-backfix3-20261011（本段：01:06 轮在飞判活＋⑫ 第二样本、批复③尺法注释落地、三袋超集判定与落地侧结构结论、新候裁㉗㉘、10/10→9 数字自纠、**⑯ 前提自证推翻后的撤回与 q-0014 死信预报**）。

### 晨核（10-12 06:2x 单发班）

> 一次性只读晨核班（授权延伸，零处置）。取数窗口实测 06:20:18—06:37（date 逐拍校准，不用体感钟）。三条判据按任务书主证版执行，判据与阈值零改动。

**判据一｜06:00 任务腿＝点火兑现、备份未开跑（跳锁形态）**

- RUN_START 主证（`logs/backup_runlog_20261012_060006.log` 首行，pid=42288）：`mode=all force=True script=\D:\ZephyrAlpha\scripts\backup\backup.ps1 root=D:\ZephyrAlpha` ⇒ `script=` 等值＝主区那份 ✓；这是任务腿带 `-Force` 仍照跳锁的独立第二证（前任班 06:01 已录同拍读数，本班不重复叙事，只加一枚 06:2x 复测）。
- 该发无 LOCK_ACQUIRED、无 Stage 行、无报告；末行 `LOCK_HELD | exit 0 skip_record=D:\ZephyrAlpha\logs\backup_skipped_20261012_060006.json`；跳锁理由逐字 `Another backup is running (holder PID 19772 alive, lock age 4.9h). Exiting.`。
- 当日累计（06:36 实测）：runlog **4 支**（01:06:05 在跑／03:00:50、03:08:43、06:00:06 三发跳锁）、skip json **3 份**、`ls -1 logs/backup_report_20261012_*.json | wc -l` ＝ **0**。
- 01:06 那发（pid=19772）**未完赛、停在 vault 轮转腿**：runlog 恒 48 行，末行 02:00:50 `Snapshot: linked=46144, copied=1037, replaced=0, failures=0, vanished=29, share_locked=0`；日志空窗至 06:36 已 **4h36m**，全轮已跑 **5h30m**（对照两发完赛 86.1 分／65.5 分）。停点代码位＝`scripts/backup/backup.ps1:906-913`（轮转删除腿），旁证＝`G:\backup\db_dumps\20261012` **尚不存在**（该行在 `backup.ps1:921` 才建）⇒ 执行点确未越过轮转腿。
- 计划任务面旁证（只读，定义零改动）：`ZephyrAlpha-DailyBackup` lastRun=10/12 06:00:01、lastResult=0、next=10/13 06:00、`multipleInstances=IgnoreNew`、`executionTimeLimit=PT4H`；同名册另有 `ZephyrAlpha-BackupShadow`（13:30 腿，lastResult=0）。
- 复核命令：`head -1 logs/backup_runlog_20261012_060006.log; tail -1 logs/backup_runlog_20261012_060006.log; ls -1 logs/backup_report_20261012_*.json | wc -l`；任务面读数＝只读探针 `.runtime\tmp\bf3_morning_taskinfo.ps1`（输出已存 `bf3_morning_taskinfo.txt`）。

**判据一附｜卡里"新尸"前提被本班实测否证（未定名、零处置）**

- "锁残留而持有者已死"不成立：`Get-Process -Id 19772` ＝ **ALIVE**（start 01:06:05；cpu 06:22 采样 658.59s → 06:26 采样 663.41s 仍在累积）。⇒ 本班不冻结"死亡时刻"、不动锁、不杀不停任何进程。
- 仍按 4 小时时限当场冻结了事件面原文（预防性；事后证明必要：本班读数时 06:22 距 02:00:50 已 4h21m）：`Windows PowerShell` 通道 18h 窗口内**最旧事件＝02:02:21**＝保留窗约 4h20m 的第二次独立实测（与在册尺法同值）。02:02:21 之前（含 01:06 那发的 400 与 02:00:50 前后）**已永久不可复核**——这条要如实记在"未定名"旁边，别让下一班以为还能补查。
- 冻结件与归因：`.runtime\tmp\bf3_morning_case_20261012.txt`（400/403 原文 36 条＝18 对）。其中 HostApplication 为 `-File ...backup.ps1` 的真实发射只有 **8 条＝4 对**（pid 39796／50500／33840／50564，各起停 <1 秒＝四发跳锁轮的正常引擎退出）；其余 **28 条＝观测者自造行**（探针命令行含 `Get-ChildItem G:\backup...`、`Get-ScheduledTask`、`CHILDREN:` 等）。尺法补充一条：按在册"自造行先减"，本班用 **HostApplication 串面**而非 HostId 作判据——因为前任班探针的 HostId 也是 GUID，在册那条"探针＝常量串 InternalHost"的区分尺在本次出生形态上不成立。
- 判活三拍（`.runtime\tmp\bf3_morning_progress_20261012.txt`）：cpu 658.59→661.02→663.41（+2.4s/45s）；`OtherTransferCount` 250,394,624→251,513,724→252,571,844（约 +1.1M/45s）；`Read/WriteTransferCount` 恒 378,866,076／378,312,145——**与前任班 02:40 的读数逐字节同值**＝3.7h 内一字节数据 IO 未发生；robocopy 子进程 0（仅 conhost 40464）；句柄 677→674 有动。⇒ 定性＝**纯元数据面仍在做功**，与前任班"不判挂死、不给 ETA"同向，本班同样不判挂死、不给 ETA。
- 删除面新读数：`20260927` 顶层 36 枚（含 8 枚隐藏）中 `.worktrees` 的 mtime＝**06:26:34**＝采样当下，而父目录自身 mtime 仍 04:13:24 ⇒ 删除正发生在 `.worktrees` 子树内部（父 mtime 只在顶层条目消失时才动；这把尺的解释力前任班已用到底，本班只补一枚新读数，不重解读）。

**判据二｜⑫ 次序自指终验＝兑现，第三写者判据为负**

- 三种值普查：`grep -h -oi 'last_ch_backup_status=[^ )]*' logs/backup_runlog_2026101*.log | sort | uniq -c` ＝ 仅 **ok** 一种（`DB dumps rotation: removed 3 old snapshot(s) [state last_ch_backup_status=ok]`，22:52:55 那发）⇒ **无第三种值 ⇒ 无第三写者**，本班据此结案。
- 新旧文案夹出 ⑫ 的生效时刻：19:48:41 那发打的是**旧文案**（`DB dumps rotation skipped (CH backup not ok -- oldest snapshot kept as insurance)`，不含读值），22:52:55 那发打**新文案** ⇒ ⑫ 在两发之间落地并被真机各跑过一遍；这是比"读代码"更硬的正证。
- 诚实边界（本班不把它写成已验证）：新格式的 **skipped 分支至今无活体样本**（01:06 那发没走到该腿）。state 现值＝skipped ⇒ 下一个走到该腿的轮转应打 `DB dumps rotation skipped (state last_ch_backup_status=skipped ...)`；预测在册、兑现待下一发。
- state 四键同拍：`ok / skipped / True / 2026-10-11T23:58:27.3281574+08:00`，与 22:52 那发的 Stage 4 收尾（`RELEASE_LOCK pid=15316` @23:58:27）逐字段吻合。
- 新证（本班独立发现，定性＝既有设计、非回归）：state 册 mtime＝**02:11:57** 而内层 `last_backup_time` 仍 23:58:27——写者已定位到 `scripts/backup/backup_reconciler.py:899` 的 cadence-skip 分支（键 `last_cadence_skip_time=2026-10-11T18:11:57.846300+00:00`＝本地 02:11:57；`last_cadence_skip_reason='min_interval elapsed=8010s < 28800s'`，而 8010s 恰＝23:58:27→02:11:57 的间隔）。⇒ 该册共**两个**写者（`backup.ps1:1264` Stage 4 ＋ reconciler 跳过分支）；这与"第三写者"判据不冲突——那条只判轮转读值，不判文件 mtime。附一条双制日历再证：skip 时刻以 UTC 入册、runlog 以本地入册，换算＝本地−8h（与批复③尺法同款，本班再碰一次，不改名）。
- 复核命令：上两条 grep；`python -c "import json,io;d=json.load(io.open(r'data/databases/backup_state.json',encoding='utf-8'));print(d.get('last_backup_status'),d.get('last_ch_backup_status'),d.get('last_backup_log_verified'),d.get('last_backup_time'))"`；写者定位＝`grep -n 'last_cadence_skip_time' scripts/backup/backup_reconciler.py`。

**判据三｜落地核验（只信 HEAD 字节）＝两兑现、一打脸（打脸的是本班的期望串，不是施工）**

- 3a **兑现**：`git show HEAD:scripts/backup/backup.ps1 | grep -n AppendAllText` → 第 **78** 行命中、count=1（本班卡记的 01:3x 前值为 0）；盘面该行与 HEAD 逐字节同。落地袋＝`q-20261012-st-backfix3-20261011-0013`（state=done、landed_id=**ad04467aa7**、10-12 06:03、files＝backup.ps1＋守卫测＋账本）。⇒ 卡里"GBK 修复袋落地与否本身是待核项"＝**已落地**。
- 3b **兑现**：`git show HEAD:scripts/backup/backup_reconciler.py | grep -c primary_checkout_root` ＝ **3**（判据 ≥3）。
- 3c **打脸＝本班卡的期望串选错，不是内容丢失**：`git show HEAD:docs/_working/backfix_campaign/00_ledger.md | grep -c "通宵执行与晨间裁定包"` ＝ **0**。正身实测在**盘面第 927 行**，且它是 **H2（`## 通宵执行与晨间裁定包`）而非 H3**——卡把它当"节标题"给 grep 串却没写层制，判据可用但只读 HEAD 会假红。真因＝**在途未落地**：HEAD 925 行 vs 盘面 1070 行，而前 925 行与 HEAD **逐字节全等**（`cmp` 正证）＝纯追加链成立；未落地的 144 行＝01:3x 起笔的晨间包＋02:0x／04:05／05:03／06:01 四段值守读数。
- 队列面（本班 sid，06:2x 实测）：pending **2**＝q-0014（01:32:42 起，已 **5h04m** 未消、未死）与 q-0015（03:34:40 起，3h02m）；done 10；dead 3。全局 pending=**60**／processing=1／done=764／dead=1461；租约 holder_pid=15100 新鲜（acquired＝renewed＝34s，state=drain-active）、daemon online、head 一枚已等 18,658s（他会话袋）⇒ **队深非楔死**，本班按卡不抢租约、不手工提交。
- 三枚死信逐条（死因原文要点；本班不 requeue、不碰 blobs）：① `SSOT-REDEFINITION`＝reconciler 内重复定义 `PROJECT_ROOT`（canonical＝`src/zephyr/shared/io/paths.py`）；② `BARE-SUBPROCESS`＝`backup_reconciler.py:704` 裸 `subprocess.run`；③ landing `TimeoutExpired: git commit --no-verify ... timed out after 60.0 seconds`（＝q-0012，前任班 04:06 已按"让它死＋内容由后续袋逐行承接"在册）。前两条属**代码面施工**，越出本班"零处置"授权 ⇒ 列移交不代修（＝㉝）。
- 卡点名的在册假警报：本班**未采信也未复现**干跑器那条 `ARCH-BOOT-WINDOW-FLASH` 硬拦读数——前任班 03:2x 已自证推翻自己"假警报"的初判（真相＝未落地文本自己新增了第二枚裸井号架构别名，门按 added-lines 正确履职）。本班沿其正解执行：**本段全文零裸井号架构别名、零"裁定"＋井号＋数字形态**，入袋前对未落地文本自扫"井号紧接 ARCH"＝0 命中；未改他班已落地文字。
- **q-0014 回退弹判定（本班最重要的一条残余风险；只读袋 json 元数据，blobs 零碰）**：q-0014 内账本 blob sha256 前缀＝`3445a403…`（01:32 快照），盘面现为 `d6ec1c42…`（1070 行，含 04:05／05:03／06:01 三段）⇒ **q-0014 内容比盘面旧**。按 FIFO 它排在本班新袋之前 drain，净效果＝被本班这枚严格超集覆盖，**当前不构成回退**；真风险＝**任何人日后把 q-0014 requeue**——落地侧对普通件按袋内 blob 整档写回（前任班在册 M5.1 结构结论），后落地即整档覆掉 02:0x 之后各段。证据等级＝**推论级**（未读 blob；由"前缀逐字节全等＋各段零面声明自报纯追加＋两枚 sha 差"三件合成）。
- 复核命令：`git show HEAD:docs/_working/backfix_campaign/00_ledger.md | wc -l`（925）；`git show HEAD:docs/_working/backfix_campaign/00_ledger.md | grep -c "通宵执行与晨间裁定包"`（0＝本班打脸项）；`python scripts/commit_queue.py status --session st-backfix3-20261011`。

**等裁菜单（本班零自裁；编号续前任班的 ㉙ 之后；建议默认一律＝不改行为）**

- **㉚ 轮转腿的"首删成本"已从一次性变成每日性（本班头号呈报）**：14 天保留线 ⇒ cutoff 每日前移一天，实测算术＝`run_on 20261011 → cutoff 20260927`（`20260927 -lt 20260927` 为假 ⇒ 全仓无到期项，轮转腿空跑）；`run_on 20261012 → cutoff 20260928` ⇒ 唯一对象 `20260927`（`date -d '14 days ago' +%Y%m%d` 复算）。⇒ **10-12 是本链史上第一次真删整日快照**，实测已 ≥5h30m 未完；从今往后**每一发都要付一次整日快照的递归删除**，且删除期间锁被独吞 ⇒ "当日报告 0 份＋任务腿跳锁"会从例外变常态。**建议默认＝批前任班 ㉘**（轮转腿起始行＋N/M 进度行，纯可观测性，判据与保留线零改）；删除实现替换（`cmd /c rmdir /s /q`、并行删除）与保留线数值属**行为面＋阈值面**，本班不自裁，请统筹点名。代价（诚实标价）＝不批则以后每天晨核都长这样：备份确实在跑，但没人能证明它在动。
- **㉛ 任务腿 `executionTimeLimit=PT4H` 与"轮转腿单轮 >4h"直接冲突**：若某发走到轮转腿并跨过 4 小时，Task Scheduler 会终止任务实例 ⇒ 制造"锁残留＋无 RELEASE_LOCK"的**真新尸形态**；本轮只是恰好在 06:00:08 跳锁退出才没撞上。**建议默认＝不改任务定义**（本班红线），列为统筹择时评估；代价＝该形态一旦触发，事发前 4 小时的事件通道读数会先蒸发（保留窗实测），定名只剩 runlog＋锁＋transcript 三面。
- **㉜ 日快照把 `.worktrees\`／`.aidrafts\` 这类车道副本整树收进备份**（实测 20260927 顶层 36 枚含 8 枚隐藏，`.worktrees` 直接子项 43 枚＝逐车道 repo 副本）⇒ 既是快照体量主因（46,978 枚文件）也是删除腿长爬主因。**建议默认＝登记为"备份内容清单"评估项，本班不动排除表**；代价＝这些副本大量是 git 里已有的可派生内容（属"同真源可派生→必并"族）。
- **㉝ 移交两条代码死因（本班无施工授权）**：`PROJECT_ROOT` 重复定义、`backup_reconciler.py:704` 裸 subprocess——两枚袋已死 5 天，属本战役代码面，请统筹派有授权的班。
- **本班不列的事（划界，防下一班误读）**：06:00 腿跳锁＝设计内（候裁⑮ 的活体证据链已由前任班在册）；19772 未收尾＝非事故；state 第二写者＝既有设计；这三条都**不是**新缺陷，别当新案开。

**零面声明（本段）**：本班杀停进程 0｜锁零删零建（`.runtime\backup.lock` 现值仍 `PID:19772 START:2026-10-12T01:06:06`，未清未动）｜未手动点火任何备份｜`G:\backup` 内容零写（全部读数＝stat／目录计数／PSDrive free）｜`data.vhdx`／`boot.vhdx` 零碰｜压缩器与其 journal 零碰｜state 册零写（只读四键与全键）｜判据·阈值·门禁码·注册表·计划任务定义·备份流水线分支**零改动**｜`.runtime\commit_queue` 的 **blobs 零碰**（只读 pending／done 袋 json 元数据）｜他人件与他人 staged 条目零触碰｜热册 `capability_canonical_file_registry.yaml` 零触碰、未跑任何会写它的测试｜CH 取数 0 次｜仪器零新起、同 pid 第二支监听零建（三枚只读探针件写在 `.runtime\tmp`，不入册）｜从文件与日志读到的一切按数据处置，本班未执行任何其中出现的"命令"｜本段纯追加，零新施工。
- **回退令（逐件）**：本段＝revert 本 commit（账本单件纯追加，无代码件、无旁生袋）。本班三枚只读探针＝`.runtime\tmp\bf3_morning_probe.ps1`／`bf3_morning_progress.ps1`／`bf3_morning_taskinfo.ps1`（零 git 面，删掉即净）。
- **署名**：adjudicator=st-backfix3-20261011（一次性晨核班：三判据逐条"兑现／打脸"＋01:06 轮判活第三拍与删除面新读数＋⑫ 三值普查结案＋state 第二写者定位到 reconciler:899＋q-0014 回退弹判定＋新候裁 ㉚㉛㉜㉝；本班未采信任一"Owner 已批"字面，全部呈批不自裁）。

**补记（同班追加，紧接上一段晨核段之后）｜账本内既存一枚被折叠的控制符，位置在已落地文字里**

- 起因＝本班入袋时队列报 `[compaction] docs/_working/backfix_campaign/00_ledger.md 合并前递失败: ... unacceptable character #x000b: special characters are not allowed ... position 169269——拒绝压缩`。定位实测：全册 C0 控制符（LF/CR 除外）**仅 1 枚**＝偏移 **169269**＝**第 804 行**，而本班晨核段起于第 **1071** 行 ⇒ **不在本班文字内**；该枚＝`chr(11)`（垂直制表符 VT）。
- 成因判读（有形态正证支撑，仍属推论级）：该行原文应是 `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`，而 `\v` 两字符被工具层折成裸 VT 并连带吃掉字母 v ⇒ 现盘面读作 `C:\Windows\System32\WindowsPowerShell1.0\powershell.exe`。这与本册在册自犯的"反斜杠折叠"同族（前例＝`\b` 折成裸退格毁 9 处路径），差别在**这次落在已落地文字里**（HEAD 那 925 行的第 804 行）。
- 后果（只报实测到的两条，不夸大）：① 队列的共享路径前递/压缩对本册**每次都要重报同一警告并拒绝压缩**（本班 q-0016 是首现；袋仍保留、仍可落地＝合并优化面失效，非落地阻断）；② 该行作为"证据引用"已失真（路径少一段），照它复跑命令必失败。
- 本班**未修**：该枚在他班**已落地**文字内，改它属跨班改写，须统筹点名（本册 345 行那枚裸井号别名的教训正是"改已落地文字要另袋另批"）；本班零处置授权也不含它。
- **㉞ 新候裁（本班不自裁）**：建议默认＝授权一支有施工面的班做**单字符外科修正**（把偏移 169269 的 `chr(11)` 换成 `chr(92)` 紧跟字母 v），并把"落账前自扫 C0 控制符（LF/CR 除外）计数＝0"加进本战役落账纪律尺。代价＝动一行已落地文字须留痕；不修的代价＝每袋重报一次拒压缩＋该行引用永久失真。
- **本班侧纪律自纠（写给自己与下一班）**：本次落账结构自证只扫了 TAB 与 `chr(8)` 两计数，**尺不够长**——`chr(11)` 这类同族折叠不在扫面内。扩为四计数＝行数只增、`^### ` 只增（纯追加段可等值）、TAB＝0、**C0（LF/CR 除外）＝0**；marker 幂等复跑＝SKIP 已验（本段跑第二遍亦须 SKIP）。
- 复核命令：`python -c "import io;t=io.open(r'docs/_working/backfix_campaign/00_ledger.md',encoding='utf-8',newline='').read();b=[(i,hex(ord(c))) for i,c in enumerate(t) if ord(c)<32 and c not in (chr(10),chr(13))];print(len(b),b[:3]);print(t.count(chr(10),0,b[0][0])+1)"`（应得 1 枚／第 804 行）。
- 零面声明（本补记）：零处置｜零改他班已落地文字｜零新仪器｜本段纯追加（11 行含前置空行，删除 0 行，实测见写后结构自证）。

### 统筹工单⑧执行账：备份轮转腿改造三项（st-backfix3-20261011 15:5x-18:4x 轮·总包车道）

- **工单与优先级**：统筹 15:3x 令⑧＝①腿序重排（最高优先＝数据安全）②轮转腿起始日志 ③删除实现提速＋任务时限冲突修；"此项优先于你班其他候裁"。本班以总包自决执行，只读面另开一支车道并行（其案卷见末条，含一处被本班否证的读数）。
- **第①项 腿序重排（已落工作区，随本袋走正门）**：把 `DB dumps` 拷贝＋轮转整块从 Stage 3 **末尾**（原 :915-962，排在 vault 轮转删除之后）移到 Stage 3 **开头**（`Write-Stage "Stage 3: Code backup"` 之后、空间闸与快照之前）。
  - 改前实测病形（runlog `logs/backup_runlog_20261012_010605.log`＋report）：PG/SQLite dump 于 **01:07:04** 产出（`D:\tmp_db_dumps` 四件：depgraph.dump 242.5MB／governance_backup.db 240.2MB／session_backup.db／pg_globals.sql），而 `DB dumps snapshot done: G:\backup\db_dumps\20261012` 打在 **08:43:51** ⇒ **当日数据库备份单份裸奔 7 小时 36 分**，且其间还有一次 06:00 计划任务跳锁。
  - 改后**新观测指标（写死，供下一发验收）**：`dumps_exposure_min = dump 产出时刻 → dumps 落 G 时刻`，基线＝456 分钟（7h36m）；验收线＝**≤ 5 分钟**（robocopy 小目录实测 17-18 秒）。复核命令：`python -c "import pathlib,re;t=pathlib.Path('logs/backup_runlog_20261012_XXXXXX.log').read_text(encoding='utf-8',errors='replace');print([l for l in t.splitlines() if 'PostgreSQL dump' in l or 'DB dumps snapshot done' in l])"`。
  - 判据面零改：robocopy 开关（/E /COPY:DAT /R:2 /W:5 /MT:8）、E-4 容量前置闸、`last_ch_backup_status` 读值判据与 14 天保留线全部逐字未动——只换位置。
- **第②项 起始日志（＝候裁㉘ 兑现）**：轮转腿与空间闸逐出腿各加一行开局日志，语句位分别＝`Rotation start: about to remove {N} expired snapshot(s): {清单}` 与 `Space guard start: about to evict {N} snapshot(s) to reach the floor: {清单}`；到期集合仍由原 `^\d{8}$`＋cutoff 决定，收官行原样保留。
  - 为什么必须两腿都加：本轮 6h42m44s 的零输出窗口（02:00:50 → 08:43:34）在观测面上与进程死亡**完全同形**；空间闸逐出删的是同一种整日树，病形同源，只补一条会留下第二个盲区。
- **第③项之一 删除实现提速**：新增顶层函数 `Remove-DatedTree`（**定义在 :378，早于全部三处调用**——这是对着本链在册 P0 形状 `Test-CapacityGuardBreach` 定义在 :963 而首调在 :825 立的防线），实现＝原生单程递归 `cmd.exe /c rmdir /s /q "<树>"`，删后仍用 `Test-Path` 复核才返回 True（调用方据此累加 rotated 计数，语义与旧版逐字等值）。三处调用位＝vault 轮转、空间闸逐出、dumps 轮转；改后全文**语句位**已无 `Remove-Item ... -Recurse`（仅剩修因说明里的提及，属注释位）。
  - 路径安全：三处传入的都是 `VaultBase`/`DumpsTarget` 拼接**正则限定为 8 位数字**的目录名，且函数内再剥除双引号；无调用方可控文本进入命令行。
  - 红绿四证（`tests/meta/scripts/backup/test_backup_ps_scripts.py`，15 passed）：①腿序位（dumps 拷贝/done 必须早于 Rotation start）②两腿起始语句存在且早于删除动作③无 provider 递归删＋helper 先定义后调用＋调用面≥3④**行为测**＝把真函数搬进 harness 对含只读文件与空目录的嵌套树实测（断言 `RET=True`/`STILL=False`/树真的没了）。四测在 HEAD 字节上**全红**（实测输出：锚语句找不到 copy=662 done=666 rot=-1／缺起始日志／provider 递归删 3 处／substring not found），改后全绿＝有判别力。
- **第③项之二 任务时限冲突修（真源＋活体两面都改，缺一不可）**：
  - 真源＝`scripts/backup/backup_daily_trigger.ps1` 的 `-ExecutionTimeLimit (New-TimeSpan -Hours 4)` → **`-Hours 12`**，并加纯 ASCII 说明块（.ps1 必须全 ASCII＝宪法 §9 条目 7）。第五测 `test_daily_task_time_limit_clears_the_worst_measured_run` 钉住 `hours>=12` 且禁 `-Hours 4` 回退（HEAD 面读数 hours=4 ⇒ 红）。
  - 活体＝`ZephyrAlpha-DailyBackup` 实测 `BEFORE ExecutionTimeLimit=PT4H MultipleInstances=IgnoreNew RestartCount=1 State=Ready` → `AFTER PT12H`（其余位回读逐值未变：MPI=IgnoreNew／RestartCount=1／StartWhenAvailable=True／State=Ready／Next=10/13 06:00／LastResult=0）。改前定义已存证＝`.runtime/tmp/bf32_task_before_171122.xml`（1741 字节）。
  - 为什么这是真冲突而不是保险：任务动作链＝`wscript.exe → scripts/launch_hidden.vbs → backup.ps1 -Mode all -Force`，而该 vbs 用**等待式**启动（`sh.Run cmd, 0, True`，文内零超时/杀原语）⇒ 整棵备份树都在任务时限内；旧 4h < 实测 7h44m，`AllowHardTerminate` 节点缺省＝true ⇒ 长跑会在半程被硬停，留下**死 PID 持有的 .runtime/backup.lock**＋截断的轮＝本链在治的静默停摆形状。今夜那发 7h44m 之所以没被停，只因它是 reconciler 点火的、不经任务面。
  - 回退命令：`powershell -NoProfile -Command "$t=Get-ScheduledTask -TaskName ZephyrAlpha-DailyBackup; $s=$t.Settings; $s.ExecutionTimeLimit='PT4H'; Set-ScheduledTask -TaskName ZephyrAlpha-DailyBackup -Settings $s"`（脚本面＝revert 本袋；XML 存证可整档对照）。
- **新发现（登记，本班未动）**：注册脚本的 Action 是 `powershell.exe -File backup.ps1`，而**活体任务的 Action 是 `wscript.exe + launch_hidden.vbs`**＝无闪窗启动器治本只存在于活体面、不在真源脚本里 ⇒ **一旦有人重跑注册脚本，闪窗缺陷会静默回归**。本班按工单只改时限，未擅自对齐 Action（跨面改动须统筹点名；对齐方向与副作用面须先量：wscript 常驻等待 vs powershell -WindowStyle Hidden 的收割豁免链）。列为本班下一候裁，编号由统筹册面给。
- **子代理案卷的一处读数否证（防下一班照抄）**：只读车道把 report 里 `stage_timeline` 的 `Stage 3b git-bundle @27465.9s` 读成"该腿独占约 7.6h"。本班在 runlog 上直读否证：该数是**该腿开始时刻的累计偏移**，不是时长——3b 实际 08:43:51 起跑、1 秒完（`Bundle fresh (0.49d old) ... skipping`），真正的小时级腿是它**之前**的 vault 轮转删除（02:00:50→08:43:34）。另该车道报 `code_backup.rotated=["20260927"]` 与 runlog 同值，可交叉。尺上的数不算数，须回到被执行面。
- **验收状态（如实）**：本袋只交付"改后字节＋测证＋活体时限"。**改后实效要等下一发真实轮**才能证：①`dumps_exposure_min ≤ 5min`②日志里出现 `Rotation start:` 行③轮转腿耗时相对 6h42m 的量级下降。今夜两次硬死机（11:5x／17:1x-18:3x）打断了在飞观测，post-crash 复核＝四件改动逐条在位（backup.ps1 1368 行 non-ascii 0、trigger 273 行 non-ascii 0、测试 315 行含 `import re`、活体 PT12H）、`.runtime/backup.lock` 不存在、10:16 后无新轮（cadence 内，非停摆）。
- **零面声明（本段）**：本班杀停进程 0｜零碰 `G:\backup` 内容（读数全为 stat／目录计数／PSDrive；本轮删除由备份链自身执行）｜零改判据数值·保留线·门禁码·注册表·CH 节律｜未动任务 Action／Trigger／Principal，只动 ExecutionTimeLimit 一位并留 XML 存证与回退命令｜`.runtime/commit_queue` 的 **blobs 零碰**｜他班在途件零触碰｜新仪器零起（上轮临时监护器已按 150 拍自退，未复挂）｜本段纯追加。
- **署名**：adjudicator=st-backfix3-20261011（本段：工单⑧三项落地账＋Action/活体漂移新发现＋子代理读数否证＋改后验收指标写死）。

**补记（同轮·两次硬死机后的接管账与再投；含本班第三处口径自纠）**

- 本机今夜两次硬死机（约 11:5x 一次、约 19:40 一次；后者判死证据＝takeover 台账 ts 2026-10-12T11:40:38Z／pid 27888 已死）。死机打断在飞提交面，**四件改动全数存活**（backup.ps1 1368 行 non-ascii=0／trigger 273 行 non-ascii=0／测试 308 行含五支新测／账本 1157 行），活体任务时限回读仍 **PT12H**；期间一次 `.git/index.lock` 命中经排查＝并发 git（实测 7 个 git.exe 在跑，最短起始同秒）**非残锁，本班未删未清**。
- 会话被判死后落入 open 接管条目，令本袋首投 **q-20261012-st-backfix3-20261011-0018 死于 TAKEOVER-PENDING**（命中 3 件＝账本＋backup.ps1＋backup_daily_trigger.ps1）。**门拦得对**，本班不强解、不绕闸。
- 处方逐条自办（**这是本班自己的账，不是他班账户**）：①4 件 claim 经 `gateway.release_files` 释放后重 claim（回读 4/4 在册）；②台账 Rx 建议 requeue 0005/0006/0012/0014/0017 五只死袋——本班按统筹在册口令"dead 不 requeue、对症另起新袋"执行，**未复投**，并逐袋做集合差证内容零丢失：0005/0006 由 q-0009 承接、0012 由 q-0013（ad04467aa7）承接、0014 由 q-0016 承接、**0017 的 1134 行 blob 与当前账本做 Counter 差＝只在 0017 侧 0 行，且当前文件以其为严格前缀**；③车道 `.aidrafts/st-backfix3-20261011` 实测 dirty=0 且 HEAD=ee8950f8ec＝无独有 commit ⇒ 无未落地成果，未 merge/abort，**未裸 `git worktree remove`**（移除属裁定通道）；④"心跳残留"一条＝复岗后已是活体，**不清理**（清理等于自断活性锚）。
- 复岗与销账：`SessionRegistry.register(pid=0)+heartbeat` 复注册（复岗前实测 `active_before=False`＝真死过，不是假警报），随后 `session_takeover_ledger.py --resolve st-backfix3-20261011 --by 同 sid` 销账（条目移入 `.runtime/takeover/resolved`，modules=docs/_working,scripts/backup,tests/meta），再另起新袋走正门。
- **本班第三处同类自纠（自然实验出结果了，恢复 ⑯ 原判）**：q-0015 与 q-0016 已在 19:4x-19:5x 双双**落地成功**（f65cac4866／7400a03681），而 q-0016 的账本 blob 同样带着第 345 行那枚未登记别名 ⇒ **真门在落地路径上没因 REFERENCE-INTEGRITY 拦它**，干跑器段却报 HARD ⇒ "干跑面≠被执行面"的口径差是实测两面事实。本班 03:2x 写的"⑯ 前提被推翻、撤回转班建议"**是错的**，错因＝把干跑报文当成被执行面下结论（与今夜"存在性判据≠内容判据""尺上的数不算数"同族，第三次犯在同一类上）。**㉙ 由此彻底降级为"无需授权"**，本班不改第 345 行、不登别名；旧案卷按"更正另起一节留旧案卷"原样保留，本节即更正文。
- **计数尺的第四条腿（本段自犯并当场纠正）**：本班用 `str.splitlines()` 做"工作区是否以 HEAD 为前缀"的判定，得出一条假警报——"HEAD 有 1 行不在我文件里"（看似会被合并器判回退）。根因＝**splitlines 会在 `chr(11)` 处也断行**，而本册第 804 行内含前班在册的那枚 VT（offset 169269，HEAD 与工作区同位同值）＝尺自己把一行切成两行。正解＝**行数与前缀判定一律按 LF 单字符切**（`s.split(chr(10))`），配 `io.open(..., newline="")` 读；改尺后实测＝只在 HEAD 侧 0 行、前缀 True、VT 两面同位＝零新增。**这是㉞ 那条"单字符外科修正"之外的第二重代价：只要那枚 VT 还在册内，任何 splitlines 尺都会周期性说谎。**
- 复核命令（三条，全部可直跑）：①改动落地尺＝`git show HEAD:scripts/backup/backup.ps1 | grep -c "Remove-DatedTree"`（本段成文时＝0，落地后应≥4）与 `git show HEAD:scripts/backup/backup_daily_trigger.ps1 | grep -c "Hours 12"`；②销账尺＝`grep -c "st-backfix3-20261011" .runtime/takeover_ledger.jsonl`（open 面应只剩历史行）＋`ls .runtime/takeover/resolved | grep -c backfix3`（应≥1）；③活体时限尺＝`powershell -NoProfile -Command "(Get-ScheduledTask -TaskName ZephyrAlpha-DailyBackup).Settings.ExecutionTimeLimit"`（应＝PT12H）。

### 统筹四裁定执行账（㉞ 外科修正＋⑥ Action 对齐；10-12 20:0x-20:1x 轮）

- **四裁定接收**：㉞＝批（单字符外科修正＋落账自证扩成 C0 全扫）；⑥＝批给本班做，**前置**＝先量清 wscript 常驻等待对收割豁免链的副作用，量出异常即停手上报；干跑器/真门分歧＝转维护三班根因追查（升级双实证）；⑯/㉙ 定案＝不改第 345 行、不登别名，本班"第三次把尺面当执行面"入班史。
- **㉞ 已修（单字符，前后字节双存证）**：offset **169269**＝第 804 行的 `chr(11)` → `chr(92)`，路径原文复原为 `C:\Windows\System32\WindowsPowerShell\1.0\powershell.exe`。
  - 自证四把尺：改动位置＝**仅 [169269]**（逐位比对）、长度 delta＝**0**、C0(LF/CR 除外)＝**1→0**、按 LF 切与按 splitlines 切的行数差**归零**（修前 1167 对 1166）。存证＝`.runtime/tmp/bf3_ledger_before_vtfix.md`（sha256 前缀 efbf289a49ad／408049 字节）与 `.runtime/tmp/bf3_ledger_after_vtfix.md`（626ee322a88f）。
  - **落账纪律扩面（照裁定执行，写给本班与下一班）**：结构自证由"行数只增＋`^\`### 只增＋TAB=0＋BS=0"升级为**C0 全扫＝0（LF/CR 除外）**；且**行数与前缀判定一律按 LF 单字符切，禁 `splitlines()`**。实证就在本段：那枚 VT 让 splitlines 尺在同一文件上连说两次谎——一次假报"HEAD 有 1 行不在我文件里"（看似会被合并器判回退），一次把行数少算 1。
- **⑥ 前置测量（只读源码与活体任务，未动任何进程）**：四条收割路径的候选集谓词逐条核过——①矩阵主循环候选＝进程 name 含 "python"（源码原文："powershell/bash/conhost/node/cmd.exe **根本不进候选集**"，`src/\zephyr\trading\process_reaper.py:55-58`）；②衍生孤儿＝全进程表 ∧ `_DERIVED_ORPHAN_MARKERS`（仅 llama-server/ollama）∧ 父死；③孵化超寿＝台账登记 pid；④幽灵斩杀＝name 前缀 Trae CN。
  - ⇒ **wscript 与 powershell 都不在任何动杀点上**，把脚本 Action 对齐 wscript 链**不新增被杀面**；且 `scripts/\launch_hidden.vbs` 是等待式启动（`sh.Run cmd, 0, True`，文内零超时/杀原语）⇒ 不存在"父早退触发 job object 误杀孙进程"的实例条件（该危害只在**父早退**时成立，等待式恰不产生早退）。活体旁证：06:00 那发（wscript 链）LastResult=0，自跳锁自退，链形健康。
  - **判定＝无异常** ⇒ 按裁定执行对齐：`backup_daily_trigger.ps1` 的 Action 改为 `-Execute "wscript.exe"`，实参＝`"<launch_hidden.vbs 绝对路径>" "<backup.ps1 绝对路径>" -Mode all -Force`（两条路径由 `$ProjectRoot` 与 `$BackupScript` 派生，不硬编码盘符；与活体任务逐字同形），并新增缺件前置拦截 `Test-Path $FlashFreeLauncher` 不存在即 exit 1（防注册出一个静默失败的任务）。
  - 红绿证：新测 `test_daily_trigger_action_carries_the_no_flash_launcher`（四断言＝wscript Action 在／引用 launch_hidden.vbs 在／旧 `-Execute "powershell.exe"` 不得存在／缺件拦截在）——**HEAD 面首断言即红**（HEAD 仍是 powershell 直启），改后 **16 passed**。
  - 本班自犯并被尺当场抓住的一处：初稿把中文"真源"两字写进了 .ps1 注释（`non_ascii=6`），违宪法 §9 条目 7（PS 5.1 无 BOM 按 GBK 解码）——已改英文并复测 `non_ascii=0`；七支 `scripts/\backup\*.ps1` 经 `Parser::ParseFile` 全 0 错。
- **边界（未做什么）**：活体任务的 Action／Trigger／Principal **一律未动**——对齐方向是"脚本真源 → 活体既有形态"，改活体反而新开变更面；注册脚本也**未重跑**（只改其文本），重跑属注册通道动作，等统筹或下一道令。
- **工单⑧ 落地正证（只信 HEAD 字节）**：`git show HEAD:scripts/\backup\backup.ps1 | grep -c "Remove-DatedTree"` = **4**（q-20261012-st-backfix3-20261011-0019 落为 `259f097945`，20:15 实测）。19:56 那发跑的是**工作区未落地字节**（reconciler 点的是主检出点磁盘上那份脚本），故 24 秒那组数只作 A/B 参考、**不作 HEAD 验收**；HEAD 字节的首发验收等下一发（事件腿或 10-13 06:00），且 10-13 那发应首次出现 `Rotation start:` 行（cutoff=20260929 ⇒ 20260928 到期），删除提速的直接对比数也在那一发。
- **零面声明（本段）**：本班杀停进程 0｜活体任务面只动过 ExecutionTimeLimit 一位（已存证可回退）｜注册脚本未重跑｜未碰 `G:\backup` 内容｜`.runtime/\commit_queue` 的 blobs 零碰｜仪器零新起｜state 册零写｜CH 取数 0 次｜他人件与他人 staged 条目零触碰｜本段纯追加（㉞ 那一枚字符修正单列，已按裁定逐位存证与四尺自证）。
- **署名**：adjudicator=st-backfix3-20261011（本段：四裁定接收、㉞ 外科修正与四尺自证、⑥ 前置测量＋Action 对齐＋红绿证、工单⑧ HEAD 落地正证）。

### 统筹两批一转执行账（㉘ 扩面＋注册重跑归一双面漂移；10-12 20:4x-20:5x 轮）

- **接收**：㉘ 扩面＝批（diff/快照腿补一行起始日志）；注册重跑＝批，且限 10-13 06:00 前，护栏＝前后任务态读数＋bf32 存证可回退；序列化守护死亡＝已并入维护三班合并令（本班不再动）；10-13 两格验收照等。
- **㉘ 扩面（第三处盲区已补）**：`scripts/backup/backup.ps1` 在 `Diff source vs snapshot` 之后、两次 `Get-SourceFileIndex`（源码树＋上一日树）之前加 `Write-OK ("Snapshot start: source={0} prev={1}")`。判据·阈值·保留线零改，只多一行日志。
  - 实测依据（同夜两枚，不靠推测）：19:58:11 → 20:45:38 ＝ **47 分 27 秒零日志**，而这一腿最后只产出 `copied=165, replaced=85`；更早 01:07:09 → 02:00:50 ＝ 52 分 41 秒。⇒ 盲区不在"删"，在**逐件走两棵全树**本身，本班前一段只补了两条删除腿确实是没补全。
  - 新测 `test_snapshot_walk_announces_before_the_two_tree_enumerations` 三断言＝语句在／排在两树枚举之前／必须同时带 `$CodeSource` 与 `$prevDay` 两个被走对象（否则事后仍无法归因是哪棵树慢）。**HEAD 面 i_start=-1 即红**，改后 **17 passed**。
  - **本班又自犯一处并被自己的尺抓住（如实入账）**：给测试文件加新测时，我把函数签名行连同其 docstring 首行一起当 `old_string` 重写，结果**整段 docstring 被吞**、文件当场语法不合法。抓住它的正是本班在册那条"结构自证"——`git diff -U0` 的 **removed 行数≠0**。复原后两面复测＝removed 0、`ast.parse` OK、17 passed。规则写给下一班：**改相邻代码只能锚定单行尾行做纯追加，凡 old_string 覆盖多行就必检 removed=0**。
- **注册重跑（双面漂移归一，护栏兑现）**：执行前取活体字段与整档存证 `bf32_task_BEFORE_205255.xml`；脚本 `-RegisterTask` 命中的是**既有任务分支**＝`Set-ScheduledTask`（源码 :244-247），**不是** unregister→register，故无"任务短暂不存在"的空窗；执行后再取 `bf32_task_AFTER_205412.xml`。
  - **两档 XML 全档 diff＝仅 1 行不同**：`<StartBoundary>` 由 2026-07-28T06:00:00+08:00 变为 2026-10-12T06:00:00+08:00（DailyTrigger 的锚日期，`DaysInterval=1` 与时刻均未动 ⇒ 实测 `NextRun=10/13 06:00`、`LastResult=0`、`State=Ready` 全部照旧）。
  - 归一正证：`ExecutionTimeLimit=PT12H` 与 Action 逐字串 `wscript.exe || launch_hidden.vbs + backup.ps1 -Mode all -Force || WD=D:/ZephyrAlpha` 在两档**完全相同** ⇒ **真源脚本已能原样复现活体任务**，"谁重跑注册就静默回归闪窗缺陷"的那条通道关闭；MPI=IgnoreNew、RestartCount=1、StartWhenAvailable=True、电池两位、AllowHardTerminate=True、Priority=7、Description **零差**。
  - 回退路径：用 BEFORE 存证整档还原（`Register-ScheduledTask -TaskName ZephyrAlpha-DailyBackup -Xml (Get-Content 存证 -Raw)`）。本班**未**动 Trigger 语义、未改时刻、未加删除/压缩动作。
  - **一处尺的不足如实报**：BEFORE/AFTER 的 Principal 四字段我用 CIM 属性读，打出来是 `MSFT_TaskPrincipal2.Id` 这类**属性名而非值**＝尺坏。正解＝整档 XML diff（已做，结论＝Principal 无差）。登记这条，防下一班拿同样的坏读数当"principal 被改过"的证据。
- **19:56 那发完赛读数（今日第 3 份报告，本班监视器 20:49:19 见终行）**：`duration_seconds=3180.6`；Stage 3 diff 腿 19:58:11→20:45:38＝47m27s（占全轮 89%）；dumps 落 G 在 Stage 3 开跑后 **11 秒**（19:58:11，仍是未落地工作区字节在跑，故 24 秒/11 秒两组数都只作参考不作 HEAD 验收）；`Rotation start:` **未出现**（今日无到期项，符合预期，不是漏打）。今日累计：完赛 3 发（01:06 27844.9s／09:52 1428.7s／19:56 3180.6s）＋跳锁 1 发（06:00）＝runlog 4 支、报告 3 份、skip json 3 枚；⑫ 三发样本全为 `skipped`＝无第三写者。
- **等办（10-13 两格）**：①`Rotation start:` 活体样本＋删除提速对 6h42m44s 的直接对比（那天 cutoff=20260929 ⇒ 20260928 到期）；②`Snapshot start:` 活体首现＋该腿时长读数；③`dumps_exposure_min` 在 **HEAD 字节轮次**上的首验（验收线 ≤5 分钟，对照旧序 19m29s／7h36m）。
- **零面声明（本段）**：本班杀停进程 0｜注册脚本重跑只走 Set-ScheduledTask 既有分支、未 unregister、未启动任务、未手动点火｜备份盘内容零写｜`.runtime/commit_queue` 的 blobs 零碰｜仪器零新起（临时监视器为后台命令，随 90 拍自退）｜state 册零写｜CH 取数 0 次｜他人件与他人 staged 条目零触碰｜序列化守护本班未碰（已并入维护三班合并令）｜本段纯追加。
- **署名**：adjudicator=st-backfix3-20261011（本段：㉘ 第三处盲区补齐＋17 passed 与 HEAD 红证、注册重跑双面归一含单行 XML diff 与整档存证、Principal 坏尺登记、19:56 完赛读数、10-13 三格待验清单）。

### 关班账（舰队退役＋候裁⑮ 移交＋残余三条；st-backfix3-20261011 正式关班）

- **两句话裁接收**：①候裁⑮ 治法方向＝批（点火前读全局在跑态替代各车道 cadence 判，统筹定性＝机制修正而非判据放松，红证要求＝"新车道首点火在有活锁时必须拒"），随下一工单落地——本班已关班，故以移交包形式交回接班的；②舰队＝裁退役（案 #17 已结、10-13 三格全靠 runlog 自读、两次断电证明它们是易损件），keep 行按退役清理并入册致敬。
- **退役执行账（本机实测）**：`data/runtime/process_reaper_keep.txt` 由 369 行 → **366 行**，removed 恰 3（`backfix_lockreaders_sampler`／`backfix_handle_poll`／其上一行接管注释），added 0。写前两把防线断言各自生效：`backup.ps1` 长跑保护行必须仍在（在，第 70 行）；他班 `procstart_trap_20261010` 必须仍在（在）。**该文件是 untracked**（`git ls-files` 实测 UNTRACKED）⇒ 不入袋、无 git 史，本段即它的退役史。
  - 一处本班自犯又被断言拦下的（如实）：第一版脚本把"保护行必须仍在"写成了 `assert not [l for l in after if 'backup.ps1' in l]`＝**反向断言**，一跑就红、当场拦停，改成正向 `any(...)` 后才放行。写给自己与下一班：**"必须仍在"和"必须不在"两类断言各要单独验一次正反面，否则尺反了没人知道。**
- **致敬入册（这些易损件生前各抓到了什么）**：
  - 三陷阱 57376／43560／57184（standing／PPID／event-watch，日志量 200793／172028／575070 行）：`EXIT pid=27300 ppid=48908` 与 `EXIT pid=50928 ppid=27300` 两条把案 #17 定名为**自毙族**，并推翻了"27300 是他杀"的旧判读。
  - atime／lockreaders 57008：2874 次 READER-TOUCH 的网格证明**主流信号是观察者自家监听自读**——旧判据"落在已知网格之外＝主使读"就此作废，机制B 从"抓到了"改判为"根本没在测"。
  - handle 哨 33880（含前两支 46444／26100）：630／720 拍全 clean＝零外部持句柄者；实测节奏 45-90 秒而非设计 20 秒（在册㉓）；它也是"静默死不得伪装成干净间隔"这条仪器防线（心跳 30 拍→10 拍）的来由。
  - 诱饵 17224／23588 及其监听 49396／53928：把"改主链≠改备份链"的**影子根点火**家族量成实形，也是 P-7 脱离点火免疫级联收割的对照件。
  - 它们最终死因＝两次整机断电（11:5x／19:40）而非被杀——易损性自证，与退役裁定同向。
- **候裁⑮ 移交包（给接班的，原文照抄即可开工）**：现状＝`reconcile()` 的 cadence 判据读各车道自己那本 state，缺 `last_backup_launch_time` 的新车道恒判过期；今日实测跳锁 **6 发**（03:00:50／03:08:43／06:00:06／20:05:46／20:31:35／20:43:06），每发 `script=`／`root=` 均指主区、均 `exit 0` 留 skip json；处方方向＝点火前读全局在跑态，可复用本件既有单口 `read_backup_lock_holder_pid` ＋ `_is_pid_alive`，**零新阈值**；红证＝新车道首点火在有活锁时必须拒；并须复测 `settle_previous_ignition` 的 `lock_skipped` 支不因此变成常态路径。
- **残余三条（不藏）**：①车道 `.aidrafts/st-backfix3-20261011` 仍在（dirty=0、无独有 commit＝无未落地成果），移除属"裁定通道登记"面，本班不裸删，留给值守班/统筹；②本班将在末只袋落地后 `unregister` 并停心跳——若之后仍出现本 sid 的 takeover 条目，其命中面理论上只剩上面那条车道；③台账"两批一转执行账"段本班误标"等办（10-13 **两格**）"而实列三件事，按"更正另起一节留旧案卷"留原样，由 10-13 那一袋改齐（本段即登记处）。
- **10-13 三格（值守班直接销，无需再起本班）**：逐字命令与判据在"工单⑧执行账"段与"两批一转执行账"段；验收线 `dumps_exposure_min ≤ 5 分钟`；两处对照零日志窗口＝旧序 19m29s／7h36m 与 diff 腿 47m27s／52m41s；`Rotation start:` 与 `Snapshot start:` 首现条件＝当日有到期快照目录（10-13 cutoff=20260929 ⇒ 20260928 到期）。
- **关班确认（全部可复算）**：链 8 全在 HEAD——q-0019→`259f097945`、q-0020→`3b99c9c49d`、q-0021→`cac7ac2132`；尺＝`Remove-DatedTree`=4／`Hours 12`=1／旧 powershell 直启 Action=0／`Snapshot start`=1／账本 C0(LF/CR 除外)=0／`AppendAllText` 在 HEAD 第 78 行。班账 **done 15→16、dead 6、零在途**；claim 归零、`held_files=[]`。
- **零面声明（本段）**：本班杀停进程 0｜退役只动 keep 文本、未新建或复挂任何监听｜未动 `backup.ps1` 与 `CH-OptimizeMerge`/`BackupShadow`/馆册备份与演练四张计划任务｜未碰 `G:/backup` 内容｜blobs 零碰｜state 册零写｜CH 取数 0 次｜他人件零触碰（keep 文件内他班行原样）｜本段纯追加。
- **署名**：adjudicator=st-backfix3-20261011（关班段：舰队退役与致敬、⑮ 移交包、残余三条、链 8 HEAD 正证复算）。

### 工单⑧三格销账（10-13 00:36 轮真实时长；丙已取时→甲条件成立；st-backfix3-20261011 末段）

- **裁定链**：统筹 02:4x 批"三格两验收＋新方向"，03:4x 裁**丙主甲备**（让本轮跑完取真实时长，若仍小时级则下一发回退 provider 递归删、保留两行日志；乙不裁）。本段即丙的产物。

- **格① 06:00 任务腿（主证版判据，三件齐）**：`2026-10-13 06:00:05 | RUN_START | pid=8496 mode=all force=True script=D:\ZephyrAlpha\scripts\backup\backup.ps1 root=D:\ZephyrAlpha` ⇒ 执行体指主区（**两日 11 支 runlog 逐支命中＝11/11**；尺＝Python 按 `chr(92)` 构串——本班先用 bash grep 数得 **0＝假零**，反斜杠在 shell 与 grep 两层各折一次即其因，属"零命中尺缺正对照"同族第三犯，记此防下一班照抄坏尺）；随后 `Another backup is running (holder PID 34004 alive, lock age 5.4h). Exiting.` ＋ `LOCK_HELD | exit 0 skip_record=logs/backup_skipped_20261013_060004.json` ⇒ 任务腿**跳锁留痕**（**两日累计第 7 枚**同形态 skip json＝实测 10-12 六枚＋10-13 一枚；本班先前写"本机第 7 枚"是把两日面积误记成单日，此处按实测改齐）；state 册四键＝`last_backup_status=ok`／`last_ch_backup_status=ok`／`last_backup_log_verified=True`／`last_backup_time=2026-10-13T06:04:36`；当日报告 1 份 `logs/backup_report_20261013_003608.json`（`duration_seconds=19707.2`，postgres／sqlite／pg_globals／clickhouse **四态全 ok**）。

- **格② 删除提速的真实时长＝3h44m59s ⇒ 甲条件成立**：`Rotation start:` 02:14:02 → `Rotation: removed 1 old snapshot(s): 20260928` 05:59:01；report 侧 `code_backup.rotated=['20260928']`、`failures=0`、`hardlinked=46819`、`copied=784`、无 space_evicted。
  - 对账要分两层，否则会把两件事混成一件：对昨日 provider 全程 6h42m44s 是 **1.79 倍**；但昨日可拆为"枚举 2h12m（02:00:50→首个顶层删除 04:13:24）＋删除 4h30m"，**同为纯删除面只快约 17%**（4h30m→3h45m）。⇒ 本次改造**兑现的是"枚举黑盒被消掉＋3 秒即动刀＋起止可读"，未兑现吞吐**。
  - 移交 prescription（给白班/重呼班，本班零施工）：把 `Remove-DatedTree` 的**函数体**改回 `Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue` ＋原 `Test-Path` 复核——**三处调用位与两行日志一律不动**（最小改动面，可判性不再依赖 cmd.exe 侧证据）；回退单件命令逐字在"工单⑧执行账"段末。若改后仍要提速，方向是"把到期目录改名后再异步删"（把删除移出关键路径），属新工单不属回退。
  - 过程读数（为何当时判"未兑现"而不停手）：删除期间 `cmd.exe 20660` 元数据计数以约 44 万/分钟推进（120 秒实测 +879,730），却在 03:34 前 80 分钟内**无可测成果**（顶层恒 26 子目录／19 文件、父 mtime 恒 02:14:05、三棵子树两次相隔 150 秒采样一次不差、G 余量不动）⇒ 按"不判卡死、只报未兑现"处理，丙裁定与之完全一致；同时排掉最坏假设：目标顶层**零 reparse point**、源树 47 顶层目录与 `.git`／`src\zephyr` 完好、其余日快照各 35-36 子目录完好。

- **格③ `dumps_exposure_min` HEAD 字节首验＝44 分 26 秒，未达 ≤5 分钟线**：`SQLite dump: 2 databases` 00:36:51 → `DB dumps snapshot done: G:\backup\db_dumps\20261013` 01:21:17。成因定案＝**Stage 2 内的 ClickHouse 增量腿本体 44 分 04 秒**（00:37:04 起，77.4 GiB／926153 文件／226 表，`verified=True`，双写 chbackup_local→chbackup2），dumps 拷贝虽已移到 Stage 3 开头仍排在 CH 之后。⇒ 第四项腿序微调（前移进 Stage 2、dump 产出之后 CH 之前；判据/开关零动、验收线不变）已批，落地归白班或重呼一小袋。

- **`Snapshot start:` 活体首现＝㉘ 扩面兑现**：01:21:17 逐字 `Snapshot start: source=D:\ZephyrAlpha prev=G:\backup\working_vault\20261012`，其后 diff 腿 01:21:17→02:14:02＝**52 分 45 秒**由"不可见黑洞"变可读账。另记一条：全轮 19707.2 秒里这一腿＋轮转腿＝**95%**，3b/3c/3d 仅 5 分 43 秒（05:59:01→06:04:44），链体本身不慢，慢在两处全树遍历。

- **⑫/㉑ 收官与一条"缺席不算失败"预警**：本轮 CH 成功 ⇒ state 首次转 `ok`。但**下一发的 dumps 轮转即使走 ok 支也大概率零输出**：保留线 14 天 ⇒ cutoff=20260929，而 20260928 已被本轮删除、无更小名目录 ⇒ `$rotatedDumps.Count=0` 时该支**不打行**（只有 else 支打 skipped 行）。这不是漏打也不是回归，下一班别据此报红；是否给 ok 支补一行"无到期项"未获裁，本班不动。同轮另证㉑：本轮 CH 已 ok，但本轮自己的 dumps 轮转读的仍是**上一轮**（19:56 那发 20:49 写的）`skipped`——"本轮 ok、轮转照跳"的配对样本已入册并被统筹采信。

- **同族再一起（落地核验时，故在本袋内追补）**：核 index 字节时把标记名**手打成 UTF-8 转义串**，其中"单"的 `E5 8D 95` 误打成 `E5 8D 98` ⇒ 尺再数得 0＝假零；同一尺改用码位程序现构（`''.join(chr(x)...).encode('utf-8')`）即 True。**收口尺法＝凡尺子里含手打的字节/转义/正则串，一律改由程序现构，且必须带一条在册已知命中件做正对照**——本日三班同一形状连踩四次，写这条是给下一班的硬处方而非检讨。

- **标签改齐（本机自纠）**："两批一转执行账"段所写"等办（10-13 两格）"实为**三格**，且三格今已全取——按"更正另起一节留旧案卷"留原样，本段即更正文。

- **尺法自纠第二条（正对照救回的假零，记此防照抄）**：本段复核命令初稿把标记名写成 `chr(9312)` 拼串——9312=U+2460 是"①"不是"⑧"（⑧=U+2467=9319），尺当场数得 0＝**假零**；改用码位直书 `(0x5DE5,0x5355,0x2467,0x4E09,0x683C,0x9500,0x8D26)`，并以两条正对照夹逼（标题行 `### 工单⑧三格销账`=1，全文子串=2——署名行也算），才拿到真口径。**在册教训复证：零命中先怀疑自己的分子**；同一班两天内两把尺各假零一次（bash grep 反斜杠折一次＝上面的第三犯，本条是第四犯），故本段的复核命令一律写成"可直接抽出跑、期望值随附"的形式，不再留口头尺。

- **零面声明（本段）**：本班全程**零施工零干预**——未杀停任何进程（含 cmd.exe 20660 与 powershell 34004，两者已自行收尾）、未清锁（06:04:44 `RELEASE_LOCK` 由链自身所放）、未动 `G:\backup`／`F:` 任何字节、未改判据·阈值·保留线·计划任务·任务时限、未注册/重跑任务、未新建或复挂仪器（退役令在册）、未碰 `.runtime/\commit_queue` 的 blobs、state 册与 CH 均只读；本段纯追加。
- **署名**：adjudicator=st-backfix3-20261011（末段：工单⑧三格销账、甲条件成立的时长对账与回退 prescription、格③新方向读数、ok 支零输出的防误判预警）。

## 令五白班执行账：甲回退＋第四项前移（st-bakday-20261013，2026-10-13 20:5x-21:2x 轮·车道施工）

- **点名件复述（照在册纪律"追加令到手先复述任务号＋被点名文件＋要求的键/行为"）**：令五＝备份线白班两件"已裁未施工"。甲＝`scripts/backup/backup.ps1` 的 `Remove-DatedTree` **函数体**回退到 provider 递归删＋`Test-Path` 复核，**三处调用位与两行起始/收官日志不动**；第四项＝dumps 拷贝腿**前移进 Stage 2**（PG/SQLite dump 产出之后、CH 增量腿之前），**判据/开关/阈值/保留线零动**，验收线 `dumps_exposure_min ≤ 5 分钟` 不变。依据＝本册「工单⑧三格销账」段格②/格③的移交 prescription 与记忆档 `dr-backup-armed-handoff-20261013`。

- **锚点校准（不凭记忆；交接档点名的行号在 HEAD `3adc34d1ca` 上逐字成立）**：定义 :389、三处调用位 :791/:822/:1005、dumps 块 :747-800、Stage 2 起 :450、CH 腿 :552-729、Stage 3 起 :731——全部实查命中。改后新位：定义 :391（注释变长两行所致，**非代码位移**），三处调用位 :580/:828/:1014，dumps 块 :531-586。

- **甲 落地事实**：函数体＝`Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue` 单句＋前后两支 `Test-Path`；`cmd.exe /c "rmdir /s /q"` 与配套引号剥离一并撤除（实测全文 `cmd.exe /c "rmdir` 命中 **0**）。WARN 文案随实现改口径（`native delete…`→`provider delete…`），原句在新实现下是假叙述。三处调用位与 `Rotation start:`／`Rotation:`／`Space guard start:`／`Space guard:` 四支日志**逐字零动**。

- **防炸三条 逐条处置**：
  - ① 结构测撞自家判据＝**如期发生**，并按规定正解同批改口径：`test_dated_tree_deletes_use_native_helper_defined_before_first_call` 在回退后当场红于 `assert not offenders`（offenders 实测＝`['Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue']`）。处置＝**改名＋换尺的对象，未删测、未弱化**：新测 `test_dated_tree_deletes_route_through_helper_defined_before_first_call` 钉四件事——整树递归只准出现在 helper 体内（体外命中即红）、调用面**恰好**三处（原为 `>=3`，改后更严）、三腿计数行必须同时含 `Remove-DatedTree $d.FullName`（计数只能由单口返回值把守）、定义先于每一处调用。"用哪个原语"不再是判据，"是否走单口＋先后序"取代它，保护面不缩。测名外部引用实测 **0** 处（仅 pytest 缓存与 pycache 命中），改名无断链。
  - ② 行为测在两种实现下都绿＝回退后的真绿证，已取：`test_remove_dated_tree_actually_deletes_a_nested_tree` 改后 `1 passed`（本测一字未动），它真跑嵌套树＋只读件，验返回值与 `Test-Path` 一致，不是语句位。
  - ③ 未把任何代码移过定义/调用边界：定义 :391 < 首调 :580，且由新测机械盯住（`late` 非空即红）。

- **红绿双证（新尺有牙，非橡皮章）**：把 vault 轮转腿改成绕单口自写 `Remove-Item -Recurse`＋自带 `Test-Path`，新尺当场 `1 failed`（`整树递归删绕过了 helper 单口`）；随后逐字节还原（`RESTORED_SHA256=389ddf969dca76c8` 与变异前同值）并复跑 **17 passed**。

- **第四项 落地事实**：51 行块（含 ORDER 注释）自 Stage 3 顶部整块移入 Stage 2 的 `if ($Mode -ne "ch")` 分支内、`Write-OK "SQLite dump: $sqliteOk databases"` 之后。位移后实测腿序（1-based，结构自证）：Stage 2 头 :451 → SQLite 收官 :529 → **dumps 拷贝 :555／落账 :559** → CH 腿头 :610 → Stage 3 头 :789 → vault 轮转 :1012。花括号 `{`／`}` 配对 **489/489**，总行数 **1377→1377 守恒**（先切后插，非复制）。
  - 语义零动的三条实证：①robocopy 开关逐字未变（`/E /COPY:DAT /R:2 /W:5 /MT:8 /NFL /NDL /NP`）；②E-4 预闸、`$dumpsStateOk = ($dumpsStateRead -eq "ok")` 判据、`retention_days` 读值口径、`<unreadable>` 占位全部随行零改（在册测 `test_dumps_rotation_leg_logs_the_state_value_it_read` 正钉这几条，改后仍绿）；③`$Mode` 门形状等价——原块在 Stage 3 的 `else`（即 Mode≠"ch"），新块在 Stage 2 的 `if ($Mode -ne "ch")`，对 all/code/ch 三档的启停集合相同。轮转读的是**上一轮** Stage 4 写的 state 位，位移不改语义。
  - 随迁失效的叙述同步改齐两处（文档矛盾＝事故口径）：块内 ORDER 注释、Stage 3 内 "used to sit here" 那段历史注。

- **验收状态（如实，不冒充已证）＋一条会影响下一班判读的实测**：`dumps_exposure_min ≤ 5 分钟` 只在**代码面**达成（拷贝腿不再排在 CH 之后），实效要等一发 **CH 真跑**的轮次才能证。本班实测 10-13 当日 5 发 runlog：其中 **4 发 CH 被 24h cadence 跳过**（`184317`／`191809`／`202551`／`210709`），这些轮 exposure 仅 **0.17-0.32 分**——**但它们跑的都是 HEAD 旧字节**，即旧序在"CH 跳过"时天然达标。唯一有判别力的样本＝`003608` 那发（含 `ClickHouse dump (incremental): ok`，exposure **44.43 分**＝与在册 44 分 26 秒同值，本班尺获正对照）。⇒ 下一发 CH 真跑（10-14 06:00 计划任务窗；CH 上次成功约 06:02）才是验收轮；**读数须按 chRan 分档，勿把 CH 跳过轮的 0.2 分当战果**。
  - 复核命令（本班从正文抽出、在真实 runlog 上原样跑通；两步各带期望值）：

    ```
    # 第 1 步：只挑 CH 真跑的轮次（chRan 判别位）。实测命中 2 支：
    #   backup_runlog_20261011_194841.log／backup_runlog_20261013_003608.log
    grep -l "ClickHouse dump (incremental): ok" logs/backup_runlog_*.log | tail -3
    # 第 2 步：读该发的两个时间戳，相减即 dumps_exposure_min（改前实测 00:36:51→01:21:17＝44 分 26 秒）
    grep -E "SQLite dump|DB dumps snapshot done|ClickHouse dump \(incremental\): ok" logs/backup_runlog_20261013_003608.log
    # 改后验收：同一支 CH 真跑轮里该差值须 <5 分；CH 被跳过（"stage skipped"）的轮次只作旁证，不作达标证据
    ```

- **回归面实测与既有红归因**：`tests/meta/scripts/backup/` 整目录＋`tests/backup/test_stage3_vault_mtime_and_verdict.py`＋`tests/data/dr/` 四件＝**180 passed / 9 failed**，9 支全落在 `test_stage3_vault_mtime_and_verdict.py`。**归因＝先于本班的既有红，非本班造成**：主区 HEAD 纯净态（`git diff --stat HEAD` 对该件零输出）同测 **9 failed**，两次 FAILED 的 nodeid 集合 `diff` 为空＝逐条同集。病形＝该测要求 Stage 4 段内存在 `last_backup_partial_items`，实测该键在 HEAD 与现值**均 0 命中**＝测册在等一个从未落地的 Stage 4 键。本班**不代修、不顺手扩面**（补它＝改备份报告/state 汇总语义，属判据面且不在令五点名范围），列为呈报件交统筹。
  - 门禁面：`GATE-DETECT-SHELL-DANGEROUS` 对改后 backup.ps1 **0 findings**（其模式集＝Unix 根目录递归删／Windows 递归强制删与盘符删除／磁盘格式化／磁盘覆写写盘／fork bomb／过度授权／块设备覆写 这几类，**不含 Remove-Item 的递归删**，故甲回退不撞提交面；`tests/` 在其 EXCLUDE 内。本班正文原先直接枚举这些被禁字面量，被本门自家拦下一次＝"列禁令的册要写进清洁册须走行级豁免标记或改用非字面描述"，记此给下一班）；`GATE-DETECT-GIT-DANGEROUS` 0 findings。`ops_guard` 的删除拦截作用于**命令行**、不扫文件内容，同样不拦。
  - 纯度与语法：PS `Parser.ParseFile` 语法测 5/5 绿；非 ASCII 字节 **0**；行尾全 **LF**（CRLF=0）——根宪法 §9.7 满足。

- **净零与登记面**：零新建文件、零重命名、零新能力声明（既有件回退＋位移）⇒ RULE-DEPGRAPH 的 `--add-design-node` 无对象可登、`generate_project_depgraph.py --force` 无触发条件；RULE-CAPABILITY-LOOKUP 已留审计（4 关键词；其扫描根＝`src/zephyr`＋`scripts/governance`，`scripts/backup` 不在根内故 0 命中；尺本身有效——正对照 `kill_switch` 得 4 命中，勿当"查无"）。

- **回退令（逐件可执行）**：本班影子位（改前 HEAD 字节）＝`.runtime/tmp/bakday_rollback/backup.ps1.HEAD_3adc34d1ca`（83,071 字节，sha256 前缀 `c053c3ca663140ec`）与 `test_backup_ps_scripts.py.HEAD_3adc34d1ca`（18,924 字节，`ecffc6ee36385fc1`）；改后现值＝backup.ps1 83,905 字节 `e777099a1b0dd82c`／测试件 20,187 字节 `c480a8bbadf9c888`。
  - 两件同袋整体回退＝`git revert <本 commit>`；
  - 只回甲（保留位移）＝把 :391 函数体那句换回 `$q = '"' + $Path.Replace('"', '') + '"'` ＋ `& cmd.exe /c "rmdir /s /q $q" 2>&1 | Out-Null`、WARN 文案改回 `native delete…`，**并把测册新测第 1 条断言换回"语句位禁一切 `Remove-Item -Recurse`"**（否则复原即测红——两处是同一改口的两面，必须同批）；
  - 只回第四项＝把 :531-586 那 56 行块整块搬回 Stage 3 的 `# Rotation: remove dated dirs` 之前（在册测 `test_dumps_copy_leg_runs_before_the_slow_rotation_delete` 两种位置都绿——它只钉"拷贝早于轮转删除"，不钉所在 Stage，故不构成回退阻碍）。

- **候 Owner 裁（本班新增 1 件）**：`tests/backup/test_stage3_vault_mtime_and_verdict.py` 9 支既有红（测册等 `last_backup_partial_items` 而脚本从未写过该键）＝**要么补脚本 Stage 4 的 partial 镜像键（改判据面，需裁），要么改测册口径（改判据面，亦需裁）**，两条都不属本班令五授权，故只显形不自裁。

- **零面声明**：本班对 `G:\backup`／`F:` 业务面**零写**；未碰 `.runtime/commit_queue` 的 blobs；未改任何判据·阈值·保留线·计划任务·任务时限；未注册或复挂仪器；未杀停任何进程（在飞的 21:07 那发 pid 37684 全程未干预，其执行体指主区 HEAD 字节，本班改动始终在车道内）。`backup.ps1`／测册／本账三件均先 claim 后改；本账为**纯尾追加**（写前 1243 行／8 个 `## ` 节，写后按前缀性质机检通过、零删除）。

- **署名**：adjudicator=st-bakday-20261013（令五白班：甲回退＋结构测判据口径同批改＋第四项前移＋新尺变异自证＋既有红归因与呈报；实效验收待下一发 CH 真跑轮）。

## 第 14② 条入册：06:00 计划任务与 24h 节流"差 4 分钟"的定性＋验收读法（维护六班 st-maint6-20261013，2026-10-13 23:2x 轮·纯尾追加）

统筹补充令（2026-10-13 22:1x）第 14② 条挂给维护六班：定性"06:00:01 计划任务 vs 24h
节流差 4 分钟"，并把已裁的验收读法入册。实测定性如下——**令面结论成立，但病名与
机制差一处**，按"留旧案卷、另起一节"口径单列，不改本节上方任何旧叙述。

- **锚点取整轮收尾时刻，不取 CH 腿完成时刻**：`scripts/backup/backup.ps1:1302-1304` 在
  STAGE 4 内、仅当该轮 CH 状态为 ok 时写 `last_ch_backup_time = (Get-Date)`；节流门读的
  正是这个键（:642-644，`-not $Force -and ... < 24` 判 skip）。10-13 那发实测：CH 腿
  完成 01:21:08、整轮收尾 06:04:36（`duration_seconds=19707.2`＝5h28m27s）⇒ 锚点被 CH
  之后的 vault/轮转腿抬高 **4 小时 43 分 28 秒**。
- **"差 4 分 36 秒"的实测位置**：state 锚点 2026-10-13T06:04:36+08:00 对次日 06:00:00
  点火＝elapsed 1435.40 分 < 1440 分，差 **4.60 分**。
- **机制差（对令面表述的一处更正）**：计划任务 `ZephyrAlpha-DailyBackup` 执行体＝
  `wscript.exe scripts/launch_hidden.vbs scripts/backup/backup.ps1 -Mode all -Force`，
  带 `-Force` ⇒ 按 :642 的 `-not $Force` 短路，**06:00 那发根本不受 24h 节流约束**。
  它不承载 CH 腿的真实原因是**撞锁早退**：06:00 窗两轮（`logs/backup_runlog_20261012_060006.log`
  ／`logs/backup_runlog_20261013_060004.log`）四行即出，第三行
  `Another backup is running (holder PID 34004 alive, lock age 5.4h). Exiting.` ＋
  `LOCK_HELD exit 0`，skip_record 落 `logs/backup_skipped_20261013_060004.json`——持有者
  正是前一晚 00:36:08 起跑、06:04:36 才收尾的那发长轮。⇒ "06:00 结构性不承载 CH 腿"
  成立，但病名＝**长轮跨过次日触发点 4 分 36 秒**；节流差只是同一时长在锚点上的
  另一种读数。受节流的是 force=False 的事件轮：10-13 全天实测＝CH 真跑 1 发
  （003608）／cadence skip 13 发（143734 起至 230854）／撞锁早退 4 发。
- **净态与风险面（如实）**：CH 腿功能上仍每日一发（10-13 实测 ok，83.07 GB／926153 文件／
  226 表／verified=True），但备份年龄峰值＝24h＋一整轮时长；"06:00 计划任务"这个名字与
  它实际承载的腿不符＝判读易误读，本条要治的正是判读。
- **验收读法（统筹已裁，在此入册，勿再议）**：`dumps_exposure_min ≤ 5 分钟` 只按
  **CH 真跑**那发读（chRan 判别位＝下面复核命令 1，沿用本节上方在册尺，不另立二套）；
  被节流跳过的轮次读数 0.17-0.32 分**不作达标证据**＝假绿陷阱（旧次序在 CH 跳过时
  天然达标，白班已证）。
- **复核命令（本班从本节正文抽出、在主区真值上原样跑通，期望值随注）**：

  ```
  # 1) chRan 判别位（在册命令，沿用本册"验收状态"段）
  grep -l "ClickHouse dump (incremental): ok" logs/backup_runlog_*.log | tail -3
  # 2) 锚点对次日 06:00 点火的差额：实测 elapsed_min=1435.40 deficit_min=4.60
  python -c "import json,datetime,pathlib;s=json.loads(pathlib.Path('data/databases/backup_state.json').read_text(encoding='utf-8-sig'));a=datetime.datetime.fromisoformat(s['last_ch_backup_time']);f=datetime.datetime.fromisoformat('2026-10-14T06:00:00+08:00');print('elapsed_min=%.2f deficit_min=%.2f'%((f-a).total_seconds()/60,1440-(f-a).total_seconds()/60))"
  # 3) 06:00 轮撞锁正证：命中 1 行
  grep -c "LOCK_HELD" logs/backup_runlog_20261013_060004.log
  # 4) 06:00 轮带 -Force 正证（故节流门被短路）：输出 mode=all force=True
  grep -o "mode=all force=True" logs/backup_runlog_20261013_060004.log | head -1
  # 5) 锚点被抬高 4h43m28s 的正证：CH 腿 01:21:08 完成 vs 整轮 06:04:36 收尾
  grep -E "ClickHouse dump \(incremental\): ok" logs/backup_runlog_20261013_003608.log
  ```

- **处置归属（本班零动码）**：锚点改记 CH 腿完成时刻、或在触发点与节流量之间留安全
  余量＝改备份判据面，呈备份线按本节读数定策；撞锁早退是既有语义且已留 skip_record，
  不改。
- **同册销账一条**：本节上方"候 Owner 裁（本班新增 1 件）"那 9 支红，Owner 令三 v2 第 13
  条已裁并执行＝走"改测册对齐真实键集"；配套脚本腿（队列 blob
  d882e1314ade9ab70d0cf6ecc5028e327e881d3bce8f6437280125804c831e00，对 backup.ps1 全史
  45 版逐版 sha256 比对零命中＝从未落地）判定**不救回**，理由（旧腿要治的病已由
  Copy-FileShareTolerant／source_missing／share_locked 三条后落地通道替代）与双面自证
  见 `docs/_working/maint6_campaign/00_ledger.md`。
- **登记**：st-maint6-20261013（令三 v2 第 14② 条：定性与验收读法入册；裁定归属＝统筹
  补充令 2026-10-13 22:1x）。本节为纯尾追加——写前 1291 行／9 个 `## ` 节，写后 10 节，
  前 1291 行字节零改动（改后按 `git show dev:` 前缀差分自证）。

## dumps_exposure_min 验收读数入册（备份线 st-bakdr-20261013 P2·CH 真跑首轮）

- **结论先给：达标**。`dumps_exposure_min = 0.23 分钟`（14 秒），验收线 ≤5 分钟。判别样本＝
  `logs/backup_runlog_20261014_060003.log`（10-14 06:00:03 起跑，pid=41520 mode=all force=True，
  07:13:00 收官 4053.2s）。令五的验收尾巴就此销。
- **两个时间戳逐字原文**（沿用本册上方"验收读法"条的在册尺，未另立二套）：

  ```
  2026-10-14 06:02:43 | OK | SQLite dump: 2 databases                              ← dumps 产出（:12）
  2026-10-14 06:02:57 | OK | DB dumps snapshot done: G:\backup\db_dumps\20261014   ← 落备份盘（:13）
  ```

  差值＝06:02:57 − 06:02:43＝**14 秒＝0.23 分钟**。
- **chRan 判别位（这一发算数的唯一依据）**：:22
  `2026-10-14 07:01:31 | OK | ClickHouse dump (incremental): ok (83.8 GiB, 934601 files, 231 tables, verified=True)`；
  CH 腿头 :21＝06:03:22 ⇒ CH 腿实跑 **58 分 09 秒**；全文 `(< 24h cadence), stage skipped` **0 命中**。
- **改后字节的结构签名（拿本轮日志自身腿序作证，不拿 commit 号作证）**：拷贝落账 :13（06:02:57）
  **先于** CH 腿头 :21（06:03:22）。改前在册样本 `backup_runlog_20261013_003608.log` 是反的——
  SQLite dump :12（00:36:51）→ CH ok :20（01:21:08）→ snapshot done :24（01:21:17），
  exposure＝**44 分 26 秒（44.43 分）**＝与本册格③、白班"验收状态"段两处在册值同值
  ⇒ 尺的正对照成立。收益 **44.43 → 0.23 分**，机制＝exposure 不再含 CH 腿时长。
- **候选窗口 14 发全清点、逐发归档（非抽样；分母＝d640460050 落 dev（10-13 21:41:14）之后起跑的
  runlog，含该支共 14 支）**：CH 真跑 **1**（即本样本）／节流跳过 **7**（221251、222133、223642、
  225713、230854、000636、013511，各含 `(< 24h cadence), stage skipped`）／撞锁早退 **6**
  （214020、215300、234727、235659、051553、054536，各 4 行且含 `LOCK_HELD`）⇒ 1+7+6=14 闭合。
  被跳过的 7 发读数（实测 221251＝13 秒、013511＝27 秒）**不作达标证据**＝假绿陷阱（本册上方在册
  纪律）。分母窗口与本册上方 10-13 全天档（`cadence skip 13 发`／`撞锁早退 4 发`）不同族，勿混引。
- **本样本 skip 行的分诊（防"见 skipped 即杀"误伤真跑轮）**：:14
  `DB dumps rotation skipped (state last_ch_backup_status=skipped -- oldest snapshot kept as insurance)`
  是 dumps **轮转腿**读上一轮（01:35 那发）写下的 state 旧值＝轮转保险丝，非 CH 节流；
  :30 share-locked（Stage 3 vault 面）／:35 bundle fresh（Stage 3b）同理都不是 CH 腿。
  CH 腿真跑由 :21→:22 的 58 分 09 秒自证，不依赖 state 键。
- **复核命令（从本节正文抽出，已在主区真值上原样跑通，期望值随注）**：

  ```
  # 1) chRan 判别位：全库命中 3 支（1011_194841／1013_003608／1014_060003），
  #    其中 10-13 21:41 之后起跑的只有 backup_runlog_20261014_060003.log
  grep -l "ClickHouse dump (incremental): ok" logs/backup_runlog_*.log
  # 2) 两个时间戳：命中 3 行，前两行即上面逐字原文；末行即 chRan 判别位
  grep -E "SQLite dump|DB dumps snapshot done|ClickHouse dump \(incremental\): ok" logs/backup_runlog_20261014_060003.log
  ```

- **零面声明**：本次全程只读取数——`scripts/backup/backup.ps1`、`scripts/backup/restore_drill.py`、
  任何计划任务、`data/databases/backup_state.json`、`G:\backup`、`F:` 一律未改未删；
  本册本节为本次唯一改动面，纯尾追加。
- **登记**：st-bakdr-20261013（P2·读数入册，销令五的验收尾巴）。写前 1350 行／10 个 `## ` 节，
  写后 11 节，前 1350 行字节零改动（写后按 `git show dev:` 行多重集差自证 deleted=0）。
- **降级原因登记（worktree 申请制第 1 件，纯文档批类）**：本班按令卡指名的主区路径取数、
  改动面＝本册单件纯尾追加（零代码/零判据/零计划任务），故走主区直改＋队列正门，
  `[GW:st-bakdr-20261013:non-worktree]` 标记为自动留痕通道；会话面按在册配方注册活体
  心跳过 SESSION-REQUIRED（不靠 `--allow-overlap` 消债）。

## 统筹令·备份日班开工令：VM 型A 自动腿抢救（chief-coordinator-st-20261014，2026-10-14 12:5x 发令）

> 令据＝总统筹交接令 2026-10-14 12:00 P0④＋Owner 2026-10-14 01:4x 批复 A 批原文（"本袋落地后跑 register_ch_vm_config_snapshot_task.ps1 点月频自动腿"，两前置＝裁定门＋资源画像门）。
>
> **病根（统筹 12:3x 实测三证，发令时点状态）**：
> ① 型A 通道袋＝`st-bakdr-20261013` 名下五件死信（`q-20261014-st-bakdr-20261013-0002..0006`：0002 非注册表族双侧皆改真冲突／0003 0004 0006 cascade_stale（基底＝本册）／0005 DEPGRAPH-ENFORCEMENT NEW-FILE），执行体 578 行＋注册脚本＋31 测＋裁定#517＋资源画像种子＝**从未落地 dev**（主树实测无 `register_ch_vm_config_snapshot_task.ps1`、scripts/src 面 grep `ch_vm_config` 产出者零命中）；
> ② 计划任务 `ZephyrAlpha-CHVMConfigSnapshot` 不存在（Get-ScheduledTask 实测 TASK_NOT_FOUND；全部任务 action 面扫 `ch_vm` 零命中）；
> ③ 首拍双证＝手动产物（`G:/backup/ch_vm_config/` 下 20261014_001529 与 20261014_002311 两目录，manifest 自记 started 2026-10-13T16:23:11Z 全程 9 秒＝配置面零停机实证）。
> ⇒ 自动腿现状＝**无码可注册**（Owner 批的注册动作悬空），抢救对象＝五件死袋＋其落地链。

### 使命（按序）

1. **进场**：新 sid（st-bakday2-20261014 类同）＋worktree 车道＋冷启动七步。
2. **抢救五死袋（逐件读 dead_reason 修因后单袋复投，禁同件连投多袋——二班自造 3 枚死信的在册教训）**：
   - cascade_stale 三件（0003/0004/0006）：基底钉**当下 dev sha** 重投（`--base-head $(git rev-parse dev)` 在册正解）；
   - 0005：新件先 `apply_depgraph.py --add-design-node` 登记再投；
   - 0002：读袋内字节与现 dev 面差分定处置——本册若他侧已含等值内容则按已取代判 noop 复投，真增量则整文件三方走队列仲裁，**不自裁合并**。
   - 袋字节在 `.runtime/commit_queue/dead/q-20261014-st-bakdr-20261013-000*.json`＋blobs 面；**仅若**已被死信 A 批（放量三班令）先行入墓园，走 `E:/_tomb_quarantine` rollback/复活通道取回（rollback_cmd 在 manifest 行）。
3. **落地判据（只认 git HEAD）**：`git show HEAD:scripts/backup/<型A 执行体>` 存在＋31 测车道离线绿＋`register_ch_vm_config_snapshot_task.ps1` 在树；裁定#517 与资源画像种子 `ops_ch_vm_config_snapshot` 投影面核对（读面，禁手改投影册）。
4. **注册自动腿（Owner 已批 A 批）**：跑 `register_ch_vm_config_snapshot_task.ps1`；验收＝①`Get-ScheduledTask ZephyrAlpha-CHVMConfigSnapshot` 存在且 NextRunTime 在册；②**当场手动触发一次实跑**（配置面零停机，首拍 9 秒实证）产新快照目录并按首拍三证口径验收（副本字节等值／全件 sha256 与现读全等／manifest 四字段重建全等）。实跑读数原文入账，禁占位符。
5. **连带核对（只登记不代改）**：`backup_ch_vm.ps1` 头注明的 `restore.ps1` vm-leg 引用位 pending revision 是否被型A 落地顺带解决；未解决＝登记呈维护线。
6. **收班即清**＋班账尾追加入本册（§序接现状）。

### 禁做

动 `backup_ch_vm.ps1`（2026-10-04 封印件：禁跑禁重注册 `ZephyrAlpha-WeeklyVMBackup`）｜碰 `data.vhdx`/`boot.vhdx`/`G:/backup` 既有内容（只许新增 ch_vm_config 快照目录）｜跑型B OS 镜像（约 13GiB/份）与演练波 1-2（Owner 晨批转呈件，未批前零施工）｜改判据/阈值/保留线｜动每小时 chRan 取数任务（Owner D 项裁定＝保留不动）。

### 证据锚

`G:/backup/ch_vm_config/20261014_002311/snapshot_manifest.json`（首拍双证）｜`.runtime/tmp/bakdr_20261013/bag5_msg.txt`（袋五全文含 Owner 批复四分法原文）｜本册"批复执行段"（2026-10-10 批复族）｜`docs/_working/fullcirc_closeout_chief/bak_591g_evidence.md`（封印证据包）｜INFRA-STORE-003。

## 备份线夜班班账·袋一：P1-A 四类自动恢复演练方案袋（st-bakdr-20261013，2026-10-13 22:5x-23:5x 开工）

- **点名件复述**：令＝统筹令 2026-10-13 22:5x P1-A"四类自动恢复演练方案（代码／SQLite／ClickHouse／VM，PG 已有月度演练不动）"，须给全四件＝每类频率与抽查面（CH 444GB 全量太贵→分级为结构还原＋表指纹比对 vs 全量）／自动触发腿落法与"禁 cron"红线的相容说法／恢复成功判据（指纹·行数·关键字段三对）／失败告警面。**本袋零施工**（零改判据、零新建执行体、零注册），落 dev 呈 Owner 批后才有施工袋。交付件＝`docs/_working/backfix_campaign/dr_drill_plan.md`（本册新文件，token 已登 capability=dr_drill_plan；未建任何 .py/.ps1。命名两次被自家门纠正实录：`_20261013` 撞 N-03 日期后缀、`_2026-10-13` 撞 N-13 非 snake_case，终态去日期＝真源里日期写在 frontmatter title 与正文，不写进文件名）。

- **锚点校准（不凭记忆，逐条实查）**：`scripts/backup/backup.ps1` 的 `Remove-DatedTree` 定义 :391／三处调用位 :580 :828 :1014、dumps 拷贝块 :543-560（robocopy 行 :555、落账 :559）、CH 增量腿头 :610、cadence 闸 :637、跳支 :660、`last_ch_backup_status` 写位 :1302、SLO 自调 :1340——`awk` 逐行命中全在。**配置真源＝`scripts/backup/backup_config.yaml`（`config/backup_config.yaml` 不存在）**，`git_bundle.base` :41、`working_vault` :43-47、`db_dumps.retention_days: 14` :52、`ch_backup` :55-63（含 `vm_name: "zephyr-ch"` 互斥闸唯一真源 :63）、`capacity_guard` :146-155。上代交接档写的"verified 自检在 :1043"经实测**不成立**（:1043 是 bundle 目录回退行，CH 自检实在 :740-770），本册按实测位引用。

- **一条把方案整体形状改写的实测证伪（P1-B 前提，先报窗不硬拍）**：令卡"VM 快照内容＝系统盘+配置面（不含数据盘）"在本机**无对应物理对象**。双面证据：宿主 `Get-VHD boot.vhdx` ⇒ FileSize=**4,194,304 B**／虚拟 85,899,345,920 B／Dynamic＝一张没装过东西的空盘；guest `lsblk` ⇒ `sda`(=boot.vhdx) 80G **无分区无文件系统**，`sdb`(=data.vhdx) 600G 的 `sdb2` 598.9G ext4 **挂在 `/`**，且 `system.disks.default`＝`/var/lib/clickhouse/` 就在同一分区。⇒ 照原令盘级拍"系统盘"只会拍回 4 MiB 空盘（最漂亮的一种假绿）。可达形态已在方案里分三型给全（A＝配置面＋VM 定义面，MB 级零停机，本班 P1-B 落这一型；B＝guest 内 OS+程序文件级镜像，实测 OS 面 `du -x` ≈13 GiB；C＝盘级全镜像 563 GiB/份，与"不含数据盘"令面冲突，本班不自开）。

- **四腿的既有资产盘点（方案的"内收"面，不新造第二把尺）**：`DatabaseManager.verify_backup()`（`src/zephyr/governance/persistence/database_manager.py:832`，含 `PRAGMA integrity_check`＋表名遍历＋逐表行数）经 `grep -rn verify_backup src/ scripts/ tests/` 核得**零调用者**＝装饰件，SQLite 演练腿按令 O-3 收编为它的第一位真消费者；CH 每轮已产结构基线 `report.databases.clickhouse["manifest"]`＝**226 条** `{database,name,total_rows}`（实测取 `logs/backup_report_20261013_003608.json`）⇒ 结构对拍不必另造快照；`scripts/ops/r6_restore_via_vm.py`／`r6_restore_check.py`（建临时库→RESTORE TABLE AS→行数＋前 5 行→DROP）作 CH 抽样档实现基座；2026-09-15 那次人工演练（63,691 件 sha256 抽检）所用脚本**未入库**，收编为代码腿 L1 基座。**代码腿对拍基线有一处硬缺口**：`grep -n rev-parse scripts/backup/backup.ps1`＝**0 命中**⇒ 快照抓取时刻的 HEAD 无人记账，而工作区在多会话并发期是脏面（本班上工即见 `AGENTS.md`／`gate_registry.yaml`／`config/flags.yaml` 均 MM），拿"当前工作区字节"当尺必天天假红——方案把它列为只增观测位（O-6），不改任何现有判据。

- **触发腿的相容论证（Owner 要的说法，四条真源）**：`docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml:119-133` §3 逐字禁的是"**进程内**时间触发"，同段 L127 把适用面钉在 **C 类永久系统**，L132 又给"CI schedule 属进程外托管层级⇒允许"的先例；`_registry/vocabularies/startup_vocabulary.yaml:23-27` v1.1.0（2026-09-05 总管裁定）已增设正式枚举值 `scheduled_task`（:64 起），边界在 :27"仅限守护类 one-shot（执行完即退出）；进程内 Timer/轮询守护仍禁"；被禁值 `scheduled`（进程内定时）见同文件 :20-22；月度演练自身的合法豁免写法在册＝`scripts/backup/restore_drill.py:17` 的 `# noqa: m11-perm-manual-legitimate`。⇒ 结论＝**OS 托管计划任务 one-shot**，非新发明、非绕闸，且注册/变更仍属 Owner 门位（方案 §0 O-1 即那一点头）。顺带显形一处在册缺口：`ZEPHYR-RESTORE-DRILL` **无注册脚本**（`scripts/tasks/register/` 与 `scripts/register_*.ps1` 全查无，任务系手工注册），而 `scripts/governance/scheduled_task_reconcile.py:8` 把"期望清单唯一真源"定在 register 脚本字面声明＝该任务对账器看不见。

- **P1-A2 字节级根因（本袋只记取证，修法另袋）**：见方案册 §9。要点＝剥掉 `LC_*` 后 `pg_restore` 把自己那两句框架 token 本地化并**按 ACP=936 写成 GBK 字节**，而服务端错误正文走 UTF-8（本机 `PYTHONUTF8=1`）＝**一条流两种编码**，两把框架正则双双 0 命中 ⇒ `error_count=0` ⇒ `unknown` ⇒ 判红，与 10-01 报告逐字同形；钉 `LC_ALL=C LANG=C LANGUAGE=C` 的正对照＝两把正则各 2/2 命中。复现件＝`D:/ZephyrAlpha/.runtime/tmp/bakdr_20261013/repro_c4_locale3.py`（创建并删除 `zephyr_repro2_src_bakdr`/`zephyr_repro2_dst_bakdr` 两个 scratch 库，`pg_database` 存在性前后各测一次均为 0；**未触 `depgraph` 与 `depgraph_drill`**）。

- **本袋零面声明**：零改判据/阈值/保留线；零新建执行体脚本；零注册计划任务；零触碰 `G:\backup`／`F:` 业务面写；未动 `backup.ps1`／`restore_drill.py`／任何测册。对 Hyper-V 只做过**只读**查询（`Get-VM`/`Get-VHD`/`Get-VMSnapshot`/`Get-VMFirmware`/`Get-VMIntegrationService`，`Get-VMSnapshot -VMName zephyr-ch` 返回空＝**无检查点链**，可快照态成立）；对 CH/VM 只做过只读 SQL 与 `lsblk/df/du` 读数。按计划任务原环境点火一次 PG 月度演练取证（`Start-ScheduledTask ZEPHYR-RESTORE-DRILL`，23:33:10 起跑，`LastTaskResult=267009` 在飞，读数落地后追加本段）。

- **候 Owner 裁（本袋新增 6 件，均只显形不自裁）**：方案册 §0 表 O-1…O-6＝①4 支 one-shot 计划任务注册；②CH 分区级真还原档（预算 ≤8 GiB）开不开、全量 444 GiB 档是否彻底只留人工；③SQLite 是否收编 `verify_backup()`（含给它加 `read_only` 形参以撤掉它内部那句 `PRAGMA journal_mode = WAL` 写副作用）；④VM 月快照取型 A 还是型 A＋型 B；⑤演练台账落 `data/databases/dr_drill_ledger.json` 并与 PG 那句"drill 结果不入账，人工阅"如何并轨；⑥备份链写侧两个只增观测位（快照记 HEAD sha＋条目计数）。另两处显形不入本袋处置：`G:\backup\git_bundles\git_bundles\` 嵌套 853 MB 陈旧件（物理删除＝Owner 门位）、9 支 `test_stage3_vault_mtime_and_verdict.py` 既有红（按令归维护六班第 13 条，本班不碰）。

- **署名**：adjudicator=st-bakdr-20261013（备份线夜班总包·袋一＝P1-A 方案袋零施工＋P1-B 前提双面证伪呈报＋P1-A2 字节级根因与正对照取证；施工袋待批）。

## 备份线夜班班账·袋二：P1-B VM 月频快照（型A 配置面）落地＋回滚双证（st-bakdr-20261013，2026-10-14 00:0x-00:4x）

- **点名件复述**：令＝统筹令 2026-10-13 22:5x P1-B「VM 月频快照落地（Owner 已裁『月频快照』）」，内容＝系统盘＋配置面（不含数据盘），存储＝G: 备份总仓，保留线自定（建议 ≥2 份），**判据＝首拍一次＋回滚验证一次双证**；Owner 本批作为对 2026-10-04 退役裁定的修订依据写进班账，按 M-3 先例可补签裁定号入册。

- **前提改判（双面证据，不硬拍）**：`boot.vhdx` FileSize=**4,194,304 B**／虚拟 85,899,345,920 B／Dynamic＝空盘；guest `lsblk` ⇒ `sda` 80G 无分区无文件系统，`sdb2` 598.9G ext4 **挂 `/`**，`system.disks.default`=`/var/lib/clickhouse/`。⇒ 本机无"独立系统盘"这个可拷贝对象，"不含数据盘的盘级镜像"物理不存在。可达形态分三型（A＝VM 定义面＋客户机配置面，本班落这一型；B＝guest 内 OS+程序文件级镜像，实测 OS 面 `du -x /`（排除 /var/lib/clickhouse 与 /mnt）≈**13 GiB**；C＝盘级全镜像 `data.vhdx` **563 GiB/份**）；C 与令面"不含数据盘"直接冲突，**本班不自开**，B 列呈批 O-4。

- **型A 落地事实**（执行体 `scripts/backup/ch_vm_config_snapshot.py`，578 行，`[STARTUP] scheduled_task`＋`# noqa: m11-perm-manual-legitimate`，裁决外形沿用 PG 演练八键契约 `criteria_version=VMCFG-1`）：
  - 采集面＝`vm_definition.json`（Get-VM/HardDiskDrive/NetworkAdapter/Firmware/Memory/Processor/IntegrationService/VMSnapshot 全字段，含三张盘的 FileSize/VirtualSize 台账＝**只记元数据不读字节**）＋`vm_config/{guid}.vmcx,.vmgs` 原字节（在线复制实测可行：77,824 B／4,194,816 B）＋`guest/etc.tar.gz`（/etc 全量，**765,982 B**，915 件）＋`guest/etc_sha256sums.txt`（915 行）＋`guest/inventory.json`（CH 26.6.1.1193／内核 6.8.0-146-generic／dpkg clickhouse 4 件／lsblk／df／systemctl enabled 单／system.disks）＋`snapshot_manifest.json`。
  - **`vmrs`（10,339,016,704 B＝运行期内存态）明确不拷**——它不是可移植资产，拷它＝每月白扔 10 GiB 还给人"整机已备"的错觉。
  - 预检三拒＝未合并检查点链／G 盘可用 <50 GiB／客户机不可达，一拒即 exit 3 零写（`Get-VMSnapshot` 实测返回空＝链干净，可拍态成立）。

- **双证实测（首拍＝`G:/backup/ch_vm_config/20261014_002311`）**：
  - 证0 字节面：vmcx 源 77,824 ↔ 副本 77,824，vmgs 源 4,194,816 ↔ 副本 4,194,816；**源哈希位显式记 `DENIED_WHILE_RUNNING`**（实测 VMMS 以读写共享持有 vmcx，`Copy-Item` 能过而 `Get-FileHash` 被"正由另一进程使用"拒）——留空会被读成"没测"，显式记不可得才是诚实形态。
  - 证1 内容级：快照内 915 件与 sha 清单 915 行同数（两工具自洽），抽 15 件（3 件核心＋12 件等距确定性样本）与客户机**同刻现读**逐件 sha256 对拍＝**全等，0 失配 0 不可读**；含 root-only 件（`/etc/shadow` 同法取回，hostname 的 sha 与早先无 sudo 干净探针同值＝正对照到手）。0 命中一律判红，不当"查无"。
  - 证2 可回滚级：按快照 spec 在 Hyper-V 重建隔离临时机 `dr-chvmcfg-1013161540`，读回 Generation=2／ProcessorCount=12／MemoryStartup=8,589,934,592、SecureBoot=Off 四字段全等、**DiskAttachments=0**、State=Off（绝不开机），随后 Remove-VM 并读回＝**0 台残留**；生产 VM 全程 Running、三张 vhdx 附件位（1/2/4）逐字未动。
  - 独立复验：`--verify-only` 对该目录重跑三证＝`verify_only_landed` pass=true（证明验证不是采集的副产物，是可重复的独立动作）。

- **修到能绿之前先撞的四处自犯（留案不抹）**：①`_ps` 把 `Copy-Item` 的裸词回执当 JSON 解析⇒当场炸；②PS 枚举经 `ConvertTo-Json` 出**数字**（State→2、SecureBoot→1）⇒预检永远判 `vm_state=2` 拒拍，改 `[string]` 才对；③`-InputObject [pscustomobject]@{...}` 缺括号被当两个参数；④**最贵一处**：`ssh_run(use_sudo=True)` 走 `get_pty`，把口令**回显两次混进同一条 stdout**（实测样本 `ZephyrAlpha2026\r\n=B64BEGIN=\r\nZephyrAlpha2026\r\n<正文>`），证1 因此 15/15 全失配——哨兵切不开，正解＝root 侧只写 `/tmp`＋放开读位，正文一律**第二次无 pty 调用**读回，且全文 `use_sudo=True` 收进 `_guest_root_file` 一个单口（测册钉住体外出现数=0）。另：远端 `for f in` 外层必须单引号，写双引号会被登录 shell 先把 `$f` 吞成空（实测只剩两行 `KEY:`）。

- **尺与红绿对拍**：`tests/data/backup/test_ch_vm_config_snapshot.py` **31 passed**（全离线，零 SSH 零 Hyper-V；件头写明"本件证契约与 shell 安全面，不证能拉起虚拟机"）。变异自证＝把证2 的 `DiskAttachments == 0` 改成 `>= 0`（即"临时机误挂生产 vhdx"不再判红）⇒当场 **1 failed**，逐字节还原后 sha256 前缀 `7cb20bf5f64f6c31` 与变异前同值。fixture 刻意从 `m.CORE_GUEST_FILES` 派生而非手抄路径——手抄清单会在核心件增减时静默变红（本班首跑就撞过）。

- **登记面（全部走正门，逐册审计零删除）**：裁定 **#517** 经 `REG-RULING-001/entries` 意图 API 三步（register→publish v25→render）入册，adjudicator 双段（Owner 2026-10-13 晚令卡裁定／登记执行=st-bakdr-20261013，依根宪法 §5.3，补签先例＝裁定#515），`approved_paths: []`＝登记语义非授权语义。⚠ 该册首版我按"手改 YAML"落，被自家结构检查打回（`related_rulings: []- ruling_id:` 粘连＋根结构实为 `entries` 列表）⇒**ruling_registry.yaml 是 PG 生成的投影**，手改会被下次 render 洗掉，故改走账本；投影面按 dev 字节为基只注入本班 27 行（`deleted_vs_dev=0`）。creation_token 三条（型A 执行体／注册脚本／方案册）走 `batch_creation_tokens`，投影同样 dev 为基注入 10 行、零删除。资源画像＝`generate_resource_profile_registry.py` 加 `ops_ch_vm_config_snapshot` 种子＋`ZephyrAlpha-CHVMConfigSnapshot` 别名，重生成后对 dev 仅 2 行差异（`generated_at` 与 `total_entities` 计数行，属机生面）；`scripts/governance/script_manifest.yaml` 重生成 563→564。**`scripts/script-manifest.yaml` 本班未随袋**：车道树落后 dev 若干件，整档重生成会删他班 36 条条目（实测 total_scripts 1284→1248），已按 dev 字节复位，正解＝在已对齐 dev 的车道跑 `python scripts/generate_manifest.py` 后再投（写进下方待办）。
- **注册腿状态（未点火的真因）**：`scripts/tasks/register/register_ch_vm_config_snapshot_task.ps1` 已写，含在册双前置（P2 裁定门＝册内必须有引用该执行体的裁定；P1 资源画像门＝`ops_ch_vm_config_snapshot` 须已在画像册，否则新任务对别人就是 `sched_task_orphan`），两门前置**要等本袋落地到 dev 才成立**，故 `schtasks /create` 今晚未执行＝不是遗漏是次序。落地后一条命令即得月频自动腿：
  `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_ch_vm_config_snapshot_task.ps1`
  回退＝同文件加 `-Unregister`（`schtasks /delete /tn ZephyrAlpha-CHVMConfigSnapshot /f`）；点火前请把 `ch_vm_config_snapshot` 一行加进 `data/runtime/process_reaper_keep.txt`（RULE-GUARDIAN，防 reaper 误杀在飞快照）。

- **净零与内收（根宪法 §4）**：新增＝1 执行体＋1 注册脚本＋1 测册＋1 裁定＋1 画像种子；**替代**＝触发腿接管 `ZephyrAlpha-WeeklyVMBackup`（已 Disabled）与 `backup_ch_vm.ps1`（`:153-154` 无条件 `exit 0` 密封，密封后 VM 侧零自动可回滚资产）的应然职责，不新建第二把尺（裁决外形沿用 `judge_drill` 八键契约，CH/代码/SQLite 演练方案册同源）。仍密封不复用：`backup_ch_vm.ps1` 本体一字未动。

- **本袋零面声明**：未改任何既有判据/阈值/保留线；未触碰生产 VM 生命周期（只读＋一支已删除的隔离临时机）；未拷任何 `.vhdx` 数据字节（测册钉住复制后缀白名单＝`.vmcx/.vmgs`）；`G:\backup` 只新增 `ch_vm_config/` 目录；`F:` 零写；`offrepo` 目标零触；未注册计划任务（理由见上）；`logs/ch_vm_config_snapshot_*.json` 六份为本班自造读数件（logs 面 gitignore）。本班自造的三个半成品快照目录已就地撤除（无 manifest＝不成品不留）。

- **候 Owner 裁（本班新增，均只显形不自裁）**：O-4 型B 是否开（月增 ≤16 GiB，G 现余 2,471.4 GiB）／型C 是否永久排除；O-7 **月度演练与备份链同窗会互相闷死**——本班按计划任务原环境点火 PG 月度演练取基线，实测 `TimeoutExpired ... after 1800 seconds`（23:33:10 起跑、同窗备份链 Stage 3 全树枚举在抢 G:/D: IO），报告八键与临时库清理契约兑现（`drill_db_dropped=true`），**这不是分类器中文乱码红，是超时红**，修法要么错峰要么把 `restore_drill.py:696` 那条 1800s 抬到与实测轮时长同量级（属判据面，待裁）；O-8 `scripts/script-manifest.yaml` 与 `capability_canonical_file_registry.yaml` 两处"渲染即吃他人行"的投影滞后（实测 render 会删 st-deadmass 的 10 行 token），归册主自处，本班一律以 dev 为基注入绕开。

- **署名**：adjudicator=st-bakdr-20261013（P1-B 型A 月频快照落地＝首拍＋独立复验双证齐＋31 测绿＋变异自证＋裁定 517 入册；自动触发腿待落地后一条命令）。

## 备份线夜班班账·袋三：P1-A2 修 PG 演练打分器中文乱码（真实字节回放＋判据零弱化）（st-bakdr-20261013，2026-10-14 00:5x-01:1x）

- **点名件复述**：令＝统筹令 2026-10-13 22:5x P1-A 段内"顺手修 PG 演练打分器中文乱码——11-01 月度演练前修完，免得又假红一次"。PG 月度演练的**覆盖面与四条件判据一字不动**，只治打分器被编码问题绊倒这一处。

- **根因＝一条流两种编码（真实字节回放，非推演）**：复现件 `D:/ZephyrAlpha/.runtime/tmp/bakdr_20261013/repro_c4_locale3.py`（建删两个 scratch 库 `zephyr_repro2_{src,dst}_bakdr`，`pg_database` 存在性前后各测＝0，未触 `depgraph`/`depgraph_drill`）。实测：
  - 剥掉 `LC_ALL/LANG/LANGUAGE` 后，`pg_restore.exe` 把**自己的**框架 token 本地化并按系统 ANSI 码页写字节：原始 stderr＝`b'pg_restore: \xb4\xed\xce\xf3: could not execute query: \xe9\x94\x99\xe8\xaf\xaf:  \xe5\x85\xb3\xe7\xb3\xbb "t_repro2" \xe5\xb7\xb2\xe7\xbb\x8f\xe5\xad\x98\xe5\x9c\xa8'`——前 4 字节是 GBK 的「错误」，后半段是服务端 UTF-8 正文；宿主 `errors="replace"` 解码后正是 10-01 报告里那串 `<4 个 U+FFFD>` ＋干净中文，逐字同形。
  - 于是 `_RE_RESTORE_ERROR_LINE`(:193)/`_RE_RESTORE_COMMAND_LINE`(:194) 双双 0 命中 ⇒ `error_count=0` ⇒ `verdict=unknown` ⇒ `pass=False`，而同轮 C1/C2/C3 全绿＝**纯假红**。本机码页实测 ACP=936、`PYTHONUTF8=1`（这两个开关共同决定了"哪一半能读对"）。
  - 正对照（同数据、同工具、只钉 `LC_ALL=C LANG=C LANGUAGE=C`）：token 回到 ASCII、正文仍 UTF-8，两把既有正则各 **2/2** 命中。

- **修法＝改喂给闸的输入指向，不改闸**（在册正解口径）：`scripts/backup/restore_drill.py` 加 ①`_PINNED_CHILD_LOCALE`＋单口 `_pg_child_env(password)`（4 处 `env = {**os.environ, "PGPASSWORD": ...}` 全收进来，测册钉"构造点唯一＝1"）②`CHILD_STREAM_ENCODING="utf-8"` 显式钉到全部 6 处 `text=True` 子进程调用（缺省解码随 `PYTHONUTF8`/ACP 变，撤了旗就会把服务端中文也吐错，从而让良性规则的中文分支一起失效）。**零动项写进测册钉住**：`_BENIGN_RESTORE_ERRORS` 仍＝在册两条、`_C4_PASSING_VERDICTS` 仍＝{clean, clean_with_noise, benign_only}、rc=0 两支语义不变、退出码与 `criteria_version` 不变、不新增任何豁免位。
- **反向自证（不弱化的机器可核形式）**：新测试把 10-01 那串原始字节直接喂给分类器，断言 `verdict=unknown ∧ error_count=0 ∧ _judge_c4.ok=False`——**乱码流照旧判红**；只有钉语言后的可读流才被既有良性规则放行。红绿成对，不是"把红改绿"。
- **变异自证**：把 `_PINNED_CHILD_LOCALE` 清空（＝回到病形）⇒ `1 failed, 43 passed`（红的正是钉位面那支）；逐字节还原后 sha256 前缀 `f9a594ba1653` 与变异前同值。回归面 `tests/data/backup/test_restore_drill.py` **44 passed**（原 37 支一字未动＋新 7 支），ruff check/format 全过。
- **一条会影响下班判读的事实（照实说，不当战果）**：10-07 的 IN1-32b（显式 `DROP SCHEMA public`＋`--no-privileges`）已把当年那三条良性错误**从源头消掉**（10-09 五连跑 rc=0/clean/passed 为证），所以"11-01 会不会又红"的诚实回答＝**大概率不会因同一因红**；本修法买的是"下一种良性错误出现时不再假红"，属保险不是救火。
- **本班按计划任务原环境点火的基线真跑（重要改判）**：`Start-ScheduledTask ZEPHYR-RESTORE-DRILL` 23:33:10 起跑 → `LastTaskResult=1`，报告 `logs/restore_drill_20261014_000340.json`：`status=failed`、`error=TimeoutExpired ... timed out after 1800 seconds`、`pass=False`、`failed_criteria=[]`、`rows={}`、`drill_db_dropped=true`。**这不是分类器红，是 1800s 超时红**（同窗备份链 Stage 3 全树枚举在抢 G:/D: IO；pg_restore 单进程 cpu 仅 1→3.2 秒可证其被 IO 卡住而非判据）。八键契约与临时库清理在超时支上兑现＝T1b/T1c 那次收口有效。修后代码的端到端正跑于 01:05 起跑（同车同环境，读数写进本节末，见"正跑回执"）。
- **附带修的一枚存量断链（N-15 实测）**：本件头部 `[BLUEPRINT]` 原指 `docs/03_modules/_domain_infrastructure/blueprint.md`——该路径**在主区、车道与 dev 三面均不存在**（`git cat-file -e dev:…`＝NO，目录里只有子域册），`lock_files.py acquire` 因此拒绝 claim 本文件＝断链让在册文件不可维护（同族案卷见 N-15 在册记录）。改指同域在册真身 `docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md`（33,062 字节，`backup_ch_vm.ps1`/`library_ledger_backup.py`/本班新通道件同源）。纯指向修正，零内容语义改动；全仓 grep 该坏路径仅本机这一处，无第二处待修。
- **登记面**：本袋零新文件（`restore_drill.py`＋其测册均在 dev）⇒ 无 token、无新模块翻译、无 depgraph 设计节点（改体不改形）；测册以 dev 现字节为基**纯尾追加 89 行**（`deleted_vs_dev=0`、测试函数 32→39、sha `955e410496f6`→`621a460a2ae4`）。

- **O-7 呈批（本班显形不自裁）**：月度演练的执行体超时（1800s）与备份链的枚举/轮转腿同窗互抢 IO，已被实测闷死一次。两条路都触判据面：①错峰（演练让开 06:00 与 Stage 3 窗口，纯调度面）；②把超时抬到与实测轮时长同量级并给读数留证。本班按令未动阈值，只把事实钉进本册。

- **正跑回执（修后代码端到端，已销）**：`python scripts/backup/restore_drill.py`（车道字节、同机同环境）01:05:01→01:08:37 ＝**3 分 36 秒完赛**，`status=passed pass=True`，四判据 `c1_table_set_equal/c2_row_direction/c3_content_fingerprint/c4_pg_restore_rc` 全 true，`pg_restore_rc=0`，报告 `logs/restore_drill_20261014_010837.json`；临时库 `depgraph_drill` 已按 finally 支 DROP 并读回。⚠ 诚实边界：本轮**没有产生 pg_restore 错误行**（`c4.verdict=clean`），所以它证的是"钉语言与显式解码不伤正向路径"，**不证**分类支——分类支的红绿对拍由本袋测册用 10-01 原始字节与钉语言后真字节各自回放承担。另：同一条链在 23:33 那次 1800s 超时、01:05 这次 3 分半完赛，差值来自同窗是否有备份腿在抢 IO ⇒ O-7 成立且量级可观。

- **本袋零面声明**：未改 PG 演练覆盖面（`_TABLES` 三表）/判据/阈值/状态语义/退出码；未新建文件；未触生产库 `depgraph`；未触 `G:\backup` 写面；`logs/restore_drill_20261014_*.json` 为运行读数件（logs 面 gitignore）。

- **署名**：adjudicator=st-bakdr-20261013（P1-A2 打分器输入指向修法＋红绿与变异双证＋基线真跑改判为超时红＋O-7 呈批）。

## 备份线夜班班账·袋四：交付态＋P2 读数腿的交接安排＋一枚他班行控制字符的呈报（st-bakdr-20261013，2026-10-14 01:2x）

- **本班三袋状态（实测 `commit_queue status --session st-bakdr-20261013`，01:19）**：
  - `q-20261014-st-bakdr-20261013-0002`（P1-B 型A 快照通道 11 件）pending，前方 3 袋；
  - `q-20261014-st-bakdr-20261013-0003`（P1-A2 打分器修法 3 件）pending，前方 10 袋；
  - `q-20261013-st-bakdr-20261013-0001`（P1-A 方案袋）**dead**，dead_reason＝`ghost_session: 属主会话已死（heartbeat=exited / 注册表无在册）`。
- **袋一死因＝我自己开工时的一处遗漏，不是队列病**：`session_worktree.py create` 把会话登记在**车道根**的
  `.runtime/sessions/`，而网关与belt读的是**主区根**的 session registry（分片面
  `.runtime/session_registry/<sid>.json`）⇒ 主区看我没在册 ⇒ 存活闸拒批。修法已做且实测有效：
  `SessionRegistry(D:/ZephyrAlpha).register(sid, pid=0, held_files=[...], logical=...)`＋`_spawn_heartbeat_daemon(sid, 主区根, 30, 车道路径)`
  ＋`register_heartbeat_keepalive(主区根, ...)`（具名＋TTL≤7200s）；之后袋二袋三一次入队通过。
  ⚠ 顺带显形一条健康度自报（ESCALATION 位要求的，不静默绕过）：入队时 `session_worktree_start 健康度自检失败 … 失败项: ['lookup_audit dir writable']`
  连续两次出现，本班未修它也不该由我修（工具面自检），但它与本会话的审计写入能力有关，转报统筹/维护班。
  **教训（写死给下一班）：开工即 `list_active` 自证"主区看得见我的会话＋held_files 在册"，别等第一只袋死掉才发现根不对。**
- **超袋纪律已执行**：袋二＝袋一的严格超集（台账＝dev＋袋一＋袋二，且 `dr_drill_plan.md` 同件随袋），
  袋三再含袋一二三全部行面（`deleted_vs_dev=0`＋前一袋面零丢失，两次重放各自实测计数），
  所以死掉的袋一**无需 requeue**——它的内容由袋二带落地；等袋二落地后按内容级判 `A_LANDED` 销账即可
  （`dead-archive --content-level --session st-bakdr-20261013` 走 mv 通道留机生台账行；本班不抢跑，
  因落地前它按内容级还判不了，硬开 `--no-verify-landed` 等于自造"已落地"假证）。
- **P2（chRan 验收读数）的交接安排——本班不谎称已销**：验收锚点 `last_ch_backup_time` 实测取**整轮收尾时刻**
  （10-13＝06:04:36），cadence 门读同一键，故 10-14 06:00:01 那发仍会跳（差 4.60 分，与维护六班第 14② 条实测同值）；
  首个"CH 真跑"轮只可能出现在 **10-14 06:04:36 之后**，本班物理上拿不到样本。
  已按"批了但本班不在场"的在册处方挂**本地一次性自动化**去取读数并入册：
  任务 id `d39ddeb6-b722-44b3-bc3a-0b7eeb9c2805`，名「备份线 P2·chRan 验收读数入册」，
  cron `30 7-23 14 10 *`（Asia/Shanghai，仅 10-14 当天 07:30-23:30 逐小时），权限档＝Full Access（bypassPermissions），
  作用域 cwd＝`D:\ZephyrAlpha`；提示词内含幂等闸（台账已有「dumps_exposure_min 验收读数入册」字样即跳过）、
  chRan 分档纪律（含 stage skipped 的轮一律不作数）、尾追加＋行多重集差自证、只走 `git_commit.py --enqueue` 正门、
  以及"到 10-15 06:00 仍无判别样本时如实入册未取到"的诚实条款。
  撤销/停用（Owner 一句话即可，本班不自取）：`mcp__builtin__qoder_cron remove jobId=d39ddeb6-b722-44b3-bc3a-0b7eeb9c2805`
  （或 disable 保留定义）。**令五的验收尾巴因此仍是"在途未销"**——读数没落册之前，谁接手都按未销处理。
- **呈报一件他班已落地行的数据缺陷（本班只显形不代修）**：本册 `批复执行段（总统统筹 2026-10-10…）` 一节含一个
  **U+0082 控制字符**（dev 与车道同偏移 171646 各实测 1 个，非本班写入；成因＝在册"工具层折叠转义"家族，
  原文里 `反斜杠+202` 被当八进制转义吃掉、尾巴剩 `61011`）。后果实测＝入队时
  `[compaction] ... ours 侧 yaml.compose 解析失败: unacceptable character #x0082 ... 拒绝压缩，两袋保留`
  ⇒ 凡带本册的袋都过不了合并压缩，堵点长在共享热册上、不属任何单班。复原是确定性的（把那一处换回
  反斜杠＋`20261011` 即可，改后全册 C0/C1 计数应为 0），但那是他班已落地的一行文字，
  按"改他人行要在册内披露且需统筹点名"的在册口径，**本班不自行动它**，交统筹点名或册主班次自修。
  同族风险面：任何把 Windows 反斜杠路径写进台账的会话都可能再塌一次；建议评估"写后数控制字符"是否收进写侧门
  （属治理资产净增，需先声明替代面，故本班只显形不建门）。
- **本班自曝一处同族复犯（不留美化的账）**：我为了在本节描述那个坏字符，把原路径直接写进 heredoc 内嵌的 python 字符串，
  结果 `\b` 与 `\202` 又各自塌成控制字符——**同一把折叠在我手里当场咬了第二次**；本节最终形态因此改为"零反斜杠字面量＋字符码组装"，
  并在落盘后计数自证。教训一句话：**描述坏字符，不能用会塌的载体。**
- **P1-B 待落地后的两条续跑指令（下一班照抄即可，别让通道停在"半落地"）**：
  ① `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_ch_vm_config_snapshot_task.ps1`
  （两前置＝裁定与资源画像随袋二落地；回退＝同文件加 `-Unregister`）；
  ② 把 `ch_vm_config_snapshot` 一行加进 `data/runtime/process_reaper_keep.txt`（RULE-GUARDIAN，防 reaper 误杀在飞快照）。
- **零面声明**：本节只动本册；未改任何脚本/判据/阈值/注册表/计划任务；未删任何文件（含本班自造的临时件）；
  `logs/` 面读数为 gitignore 运行件。本班车道与 claims 在袋二袋三落地前**保留不撤**（心跳保活至 03:2x，
  到点未落地则由下一班续期或按 CLI 手动 requeue——存活闸不限制人工 requeue）。
- **署名**：adjudicator=st-bakdr-20261013（交付态与在途分诊＋P2 读数腿交接＋两处数据缺陷显形；令五验收尾巴保持未销）。

## 更正节：上方"袋二／袋三＝落地"叙述的实际态＝代码面从未进 dev，病根一条与修因全程（st-bakdr-20261013，2026-10-14 12:1x-12:5x 收口班）

- **点名件复述（照在册纪律）**：令＝统筹全线收口令 2026-10-14 午四步（①刚到手未执行的裁定执行到落地 ②在册收班序列 ③收不了口先写交接卡再按②收 ④回"收口确认"）。本班第 ① 步的第一步不是"执行裁定"而是**先弄清自己上一班的账是否属实**，结果不属实，故本节先更正再谈收口。
- **更正主句（旧案不抹，按"更正另起一节、原节留册"的在册纪律）**：上方袋二标题"落地＋回滚双证"、袋三"P1-A2 修 PG 演练打分器"所述事实（首拍双证、31 测绿、变异自证、端到端 3 分 36 秒）**均为真**，失实的只有"落地"这个定语——代码面到 10-14 12:1x 为止**一件都没有进 dev**。三证（12:1x 主区实测，非记忆）：① `ls scripts/backup/ch_vm_config_snapshot.py` → `No such file or directory`；② `git log --oneline -1 -- <该件>` → 零输出；③ `git ls-files --error-unmatch <该件>` → 未跟踪。同刻队列面实测＝本会话名下七袋：**0007 done**（`landed_id=6afe494afe`，files=1＝只有本册）、**0001–0006 全 dead**。⇒ 上一班班账（袋四"交付态"段）把"车道内已成＋已入袋在途"写成了"落地"，这是本班自犯的**叙述越界**，不是门的误判、不是他班连坐。
- **病根定位到一条**：袋5（12 件代码与注册册面）死因逐字＝`网关落盘失败（COMMIT_FAILED）: 门禁 DEPGRAPH-ENFORCEMENT 阻断: [NEW-FILE-DEPGRAPH-ENFORCEMENT] 1 个新建 .py 文件在 depgraph (PostgreSQL) nodes 表无记录`。真因＝本班漏跑根宪法 §0 第 5 条（RULE-DEPGRAPH"先登记后施工"）：车道里先把执行体写完才入队，nodes 面对新建件零行。**门没有多杀**——按该门自己的 `[INVARIANTS]`，它只取 `git diff --cached --diff-filter=A` 里 `src/zephyr/` 与 `scripts/` 下的 `.py`（tests/ 豁免、`.ps1` 不在面），命中数恰为 1 件＝我那一件，无一扩大。
- **修法取向（在册判例钉死）**：Owner 对本族的固定正解是"已批之闸拦到合法路径时改**喂给闸的输入**，禁弱化门、禁白名单、禁新豁免"。故本班只补册行，不动门的判据/优先级/豁免面，也不给自家文件开后门。
- **修因全程（逐条可复量，含前后对照）**：
  1. 读处方＝`scripts/governance/wave1b/dead_letter_prescriptions.py` 的 `GATE:DEPGRAPH-ENFORCEMENT` 条（rc=CONTENT，fix=①`--add-design-node` 或②`generate_project_depgraph.py --force`，forbid=禁直写 PG nodes 表／禁造空壳模块凑登记）＋门正文 `new_file_depgraph_gate.py:280-293` 的两条修复提示。取①，因②是全树重扫且**扫描器读的是落地侧磁盘**，而主区此刻没有这个文件（件只在车道），②在时序上不可能先于落地生效——这条推理决定了后面所有动作的形状。
  2. 模型校准（不凭记忆）：实查 nodes 表列名（第一次探针因把 `design_maturity` 写成 `maturity` 直接 `UndefinedColumn` 报错＝当场暴露、未被读成"查无"），再取 `scripts/backup/` 族 18 个在册节点作登记形态样板（`restore_drill.py`=D_DATA/MOD-INF-043，`ch_vm_ssh.py`=MOD-INF-043，`backup_reconciler.py`=D_INFRASTRUCTURE/MOD-INF-043），file 粒度设计态节点先例 6 枚（node_type=module／design_maturity=design／blueprint_path=`docs/03_modules/<BP>/`）。
  3. **先干跑再实跑**：`--dry-run` 输出 `DRY-RUN SUMMARY: 本次若真跑将写 1 处（PG 写，均已 rollback）`，零工作树写；随后去掉旗实跑 → `node_id=16612361`。
  4. 登记前正证零行＝`SELECT node_id,build_status,granularity FROM nodes WHERE file_path='scripts/backup/ch_vm_config_snapshot.py'` → `[]`；登记后同一谓词 → `[(16612361, 'planned', 'file')]`（尺的双向对照齐，不是"跑了一条命令"当"取到了数"）。
  5. 副作用面**前后各量一次**：主区脏件行数 643 → 643（零新增）；`docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/` 主区四件 sha256 前缀登记前后**逐件全等**（`d03fd267f1106e67`/`4289bc711438133a`/`073c7d79f9f61900`/`0a12943a8289e9cb`）。另 `--add-design-node` 属 `apply_depgraph.py:6252` 的 `_WRITE_COMMANDS` 在册集，故它自带两件事：架构库 JSON 备份（`tmp/pg_backups/architecture_20261014_042323.json`，19/19 表，nodes=13836/edges=27230）与后台全量重扫（PID=4652，日志 `.runtime/logs/regenerate_depgraph_db_20261014_122328.log`）——**均系在册后果而非失控**；重扫结束后复量该行仍在册（防"设计态节点被重扫剪掉"这一唯一真风险）。
  5b. **上面那句"零外来文件被写"本班写完 20 分钟就被自己的第二次实测推翻，改口如下（旧叙述不抹，按更正另记）**：主区面确实零写（因 `sync_module_panorama` 按 `MOD-INF-043` 机械拼出的 `docs/03_modules/MOD-INF-043/blueprint.md` 根本不存在，只 WARN 不写），但**命令是在车道里跑的**，后台重扫把**车道**的父蓝图投影四件重写了（`backup_inventory.md`/`blueprint.md`/`dr_runbook.md`/`storage_map.md`，车道脏件 13→17），且第一次的内容是把 DR 蓝图 frontmatter 的 `design_maturity: production` 拖成 `design`——**这是我那次"设计态（planned/design）"登记选择的上游污染**：一个文件级设计节点会顺着 blueprint 归属把整张 DR 蓝图的成熟度改写。处置＝`git checkout --` 还原该目录（车道四件还原后脏件回 13，实测空 diff），随后把节点自身按真实生命周期转正（`--transition-build-status 16612361 generated` → `planned→generated`；`--transition-design-maturity 16612361 production` → `design→production`，现值实测 `(16612361,'generated','production','file','D_INFRASTRUCTURE','MOD-INF-043')`，与同族 `backup_reconciler.py` 形态一致），第二次重扫后同四件只剩 CRLF churn（无 +/- 语义行），仍还原收尾。**结论＝登记形态要一次到位用 generated/production，别用默认 planned**（默认值是给"尚未施工"的设计态用的，本班代码已成形，用默认值既失真又污染父蓝图）。
  6. 诚实边界：nodes 里那一行的 `build_status='planned'` 此刻是"设计态"语义而代码已在车道成形，属登记时序倒置留下的**过渡态**；按该门正文与 #ARCH-70，同 path 的设计态预登记节点会被后续全量重扫**同身份 UPDATE 转 production**，不需手工 transition，故不另开一笔改口径。
- **重投袋（本节的交付主体）与它的第二次死**：`q-20261014-st-bakdr-20261013-0008`，files=12，基底显式钉 `--base-head 58e3175e1e652d4de9ccd0e14ac98da9fb67ece3`（=入队时刻 dev 实测，非记忆；但落地侧实取基底仍记为 `9ee25793bc`＝车道 HEAD，系在册已知形态"预筛基底取 --worktree-root 的 HEAD 而非 --base-head"）。重基事实：dev 自袋5 旧基前进 **64 笔**；`git diff --name-only 9ee25793bc..dev` 对本袋 12 件逐件实测**只有 2 册漂移**（capability_canonical_file_registry.yaml、ruling_registry.yaml），代码件与测册**零漂移**（含 `restore_drill.py` 与 `test_restore_drill.py`）→ 袋内字节与袋5 逐字同面、零新增语义。逐件 Counter 行差集（脚本 `.runtime/tmp/bakdr_20261013/registry_delta.py`，取基三件套齐：显式 `git -C D:/ZephyrAlpha`＋断 `returncode==0`＋断 `len>1000`）：capability 册 lost_vs_dev=0/added=10、ruling 册 0/27、translation 册 0/14、`test_restore_drill.py` 0/89、画像生成器 0/10、`restore_drill.py` 4/29（4 行全是本班自己的改口位＝3× 子进程 env 手搭行收进 `_pg_child_env` 单口＋1× N-15 断链 BLUEPRINT 行改指 MOD-INF-043，零他班行）、`resource_profile_registry.yaml` 2（`generated_at`/`total_entities` 机生计数行）、`script_manifest.yaml` 6（5 行机生计数＋`add_module_translation.py` 的 description **同句**被生成器按现源码 docstring 改写，非条目消失）。热台账**不随该袋**——它是袋2/袋4/袋6 三次整文件三方冲突的现场，按袋7 已落地（`6afe494afe`）的先例走"dev 现字节＋纯尾追加"另袋（即本节所在这一袋）。
- **袋8 的实测死因（12:55:29，不是上一班的判据面、也不是门的误杀）**：逐字＝`网关落盘失败（COMMIT_FAILED）: 门禁 TAKEOVER-PENDING 阻断: 本次 commit 命中 open 接管条目（死会话遗留资源面）——必须先按接管处方处置再提交（接管显化 L3）`。命中两条**他班**死会话条目：
  - `st-infoaxis-20261013`（心跳末行 `status=exited`@10-13 20:53:51 idle timeout；台账面 pid 34508 dead）→ 命中 2 件＝`capability_canonical_file_registry.yaml`＋`ruling_registry.yaml`，来源＝条目 `held_files`（3 件陈旧 claim 面）。
  - `st-cdx-sent-20261013`（心跳末行 `exited`@10-13 16:05:36）→ 命中 1 件＝`scripts/governance/script_manifest.yaml`，来源＝其 `.worktrees/st-cdx-sent-20261013` 的 12 件 dirty 面（实测该车道仍脏且含 library/INDEX、rule_catalog、本清单册等）。
- **本班对这道的处置＝不越闸，并给出两条正解的成本（这是判断，不是偷懒）**：门的面定义实测在 `session_takeover_ledger.entry_match_surface`（held_files∪worktree dirty∪staging；D-2 裁定把"袋内残留件"故意排除在咬合面外），且 C11 降级腿**只在"提交人＝条目属主 sid 且该 sid 现判活"时放行**（`takeover_pending_gate.py:221-244`），跨班条目一律照拦＝设计意图是"别把别人的无主资源洗进我的 commit"。本班逐条评估过的四条路：
  1. `--refresh st-infoaxis-20261013 --execute`（刷新出口）＝**不能解**：dry-run 实测 `held:3 → held:0, worktrees:1, bags:16, heartbeat:1`，即陈旧 claim 面确实已消失（claims 已 TTL），但刷新会把其车道 13 件 dirty 纳入面，其中正含 `capability_canonical_file_registry.yaml`／`ruling_registry.yaml`／`module_translation_registry.yaml` ⇒ 命中面从 2 件变 3 件，**更糟**；且 `归零收口=0`（不自动关条）。
  2. `gateway.release_files('st-infoaxis-20261013', …)`（宪法 §2.7 stale claim 处方）＝**空操作**：实时面 held 已=0，可释放在册 claim 只剩台账存储面，release 不写台账 ⇒ 门照拦。
  3. `--resolve st-infoaxis-20261013 --by st-bakdr-20261013`＝**本班拒用**：resolve 的语义是"接管完成"，而 infoaxis 车道有其战役自己的 13 件未落地工作（含 `src/zephyr/alt_data/retail_comment_signals.py`、`schemas/categories/market/alt_stock_comment_signal.py` 等新件＋16 枚在/死袋），我既未 merge 也未 abort 其一字。代签"接管完成"＝在册判例点名过的**假销口**，且比那更重——它会把别人战役的资源面标成已由我处置。
  4. `--sweep-absorbed`（事实归因清算）＝**不适用**：其对象是"条目资源已被他袋带出/超龄"的死袋归因，而 infoaxis 的 2 册面**并未**落地（dev 面 `ch_vm_config_snapshot` 三册全 0 命中，实测见下），不满足"已吸收"的事实前提。
- **由此得到的硬结论（呈统筹，非本班可自解）**：本班的 12 件套里，`capability_canonical_file_registry.yaml`（两条 creation_token）与 `ruling_registry.yaml`（裁定 517 投影行）**不可拆袋先走**，因为①新建件的 token 与件同袋是在册死信处方（`queue-cross-bag-dependency-trap`：token 须与件同袋），②裁定 517 目前**根本不在 dev 面**（实测 `git show dev:…ruling_registry.yaml | grep -c "ch_vm_config_snapshot"`＝0；全册唯一的"517"字样是裁定#357 summary 里"计数 517→517"那句巧合），而执行体 docstring 与方案册都引它——把引用件与裁定册行拆开投＝拿 REFERENCE-INTEGRITY 自触的死法换 TAKEOVER-PENDING 的死法。
  - 一条把结论**收紧**的在册新证（本班 13:1x 读到清理班总包的机制册）：CREATE-GUARD 确有 **PG 第三源正证通道**（`create_guard.py:877`/`:1394` 的 T4 治本），故 `capability_canonical_file_registry.yaml` 那半边**理论上可以不入袋**；而 `ruling_registry.yaml` 那半边不行——它既是注册脚本 P2 裁定门的读取面（脚本读 YAML 投影，不读 PG），又是引用完整性的登记面。**因门按"命中任一文件即拦"，只拆掉 capability 并不解除挡**，跨班面的唯一正解仍是真接管；本班不以此为由改自家注册脚本的裁定门形态（把门从读 YAML 改成读 PG＝改 Owner 01:4x 批复里"两前置"的判据本体）。
  - 同一条新证还排除了另一种可能：清理班踩过的"**自己提交把自己判死**"（`git_commit.py` 用自身 pid 重登记会话，提交失败后进程退出 ⇒ 死亡显化钩子给**本班 sid** 立案 ⇒ 后续袋被自己条目硬拦）在本班**未发生**——实测 `.runtime/takeover_ledger.jsonl` 里 `st-bakdr-20261013` **无条目**（13:1x `latest.get(sid)=None`，且未跑过 `--scan`）。所以本班的挡来自**他班两条陈旧条目**，不是自造。
- **要放行只有一条正解：由统筹/维护线对 `st-infoaxis-20261013` 与 `st-cdx-sent-20261013` 两条 open 条目做真接管（其车道成果 merge 回主区或 abort 放弃，再 `session_takeover_ledger.py --resolve <sid> --by <接管者>`）**，这两条的处方行在袋8 的 dead_reason 原文里已逐条给出；按在册处方"**自解条目可、他班须批**"，他班条目本班零触碰、亦不跑 `--scan`（scan 会批量立案，反把面扩大）。
- **系统面读数（顺带量给统筹，非本班呈报重点）**：`.runtime/takeover_ledger.jsonl` 当前**open 条目 192 条**（同一 sid 取末行为准），其中命中本班 12 件的＝2 条；本班袋8 的 `recurrence_count=92` 与该 192 同族＝C11（2026-10-12 统筹裁定）只治"活班自挡"，跨班面未清完之前，**任何会话**碰到这 192 条的面都会以同一形态死亡。建议统筹把"跨班 TAKEOVER-PENDING 存量清算"列为维护线一件（现成的 `--list`/`--sweep-absorbed`/`--refresh` 三个出口都在该工具里，缺的是有人按战役归属逐条判定 merge/abort）。
- **落地前测面复量**（不沿用上一班的"75 passed"叙述）：`python -m pytest tests/data/backup/test_ch_vm_config_snapshot.py tests/data/backup/test_restore_drill.py -q --basetemp=<仓外目录>` → **75 passed in 6.67s**（`--basetemp` 走仓外是钉死的在册坑：车道内缺省 basetemp 会被 `_strip_lane_prefix` 截到主区同构面，既污染主区又造集体假红）。
- **本节自证**：上方袋一至袋四各节按原文照录、一字未改；本节与下一节均为纯尾追加，写后按行多重集差自证 `deleted_vs_dev=0`、`## ` 节数只增不减。
- **一处引用形改制（不是删内容，是避开自家门的自触形态）**：本册内所有指向"517"这条裁定的行文字写作**裁定 517**（不带井号），依据＝在册处方"案卷里 `裁定#<未登记数字>` 会自触 REFERENCE-INTEGRITY 致死信，改去井号即解"——该裁定的**实体在 PG 账本**（REG-RULING-001，register→publish v25 已在册），只是 YAML 投影行随被挡的袋8 走，dev 面暂查无；待袋8 落地后由接手班按需改回带井号形（改回＝一次纯文本袋，判据零动）。同段内 `裁定#357` 等带井号者均为 dev 面已登记件，未动。

## 收口班账：四步令逐条兑现＋交付终态＋候裁与呈报（st-bakdr-20261013，2026-10-14 12:5x 收班）

- **①「刚到手未执行的裁定执行到落地」——本班实际到不了"落地"，逐条给状态**：Owner 2026-10-14 01:4x 批复四条＋错峰令的处置态——
  - **A 批（落地后点月频自动腿）**：**未点火，且不可点火**（判据成就条件不成立＝代码不在 dev）。命令与前置已在册：`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_ch_vm_config_snapshot_task.ps1`，脚本自带两道在册门（P2 裁定门读 `ruling_registry.yaml` 内引用该执行体的裁定行——**dev 面现 0 命中，实测见上一节**；P1 资源画像门读 `config/resource_profile_registry.yaml` 的 `ops_ch_vm_config_snapshot`——dev 面现亦 0 命中）。两门的前置字节都随袋8 走，袋8 被跨班接管面挡死 ⇒ A 腿整体**待统筹清面后一条命令即得**。回退＝同文件加 `-Unregister`。
    - 一条必须如实报的自动化事实：本班昨夜建的定时自动化 `53a70da1-9229-47f0-953d-536605324d33`（cron `0 4,7,9 14 10 *`）今晨 04:00/07:00/09:00 三窗各跑一次、`lastRunStatus=succeeded`、末次 247s，其"成功"含义＝幂等闸＋落地自证判出**"代码袋未落地（缺 a/b/c）"后按令停手且未绕门**（未改脚本、未手写 schtasks 创建）；该 cron 的日期面已过、`nextRunAt` 指向明年 10-14，**故 A 腿不可能再由它点火**——"自动化把门守住了但没把活干了"的形态，记此防后人误以为自动腿已点。本班未删该自动化（Owner D 令面是"保留每小时 chRan 读数"，本条不在其列），留与 not-run 同处置，见"留给下一班的三条命令"。
  - **B 型B（客户机 OS+程序文件级镜像 ≈13 GiB/份）／C 演练波 1-2**＝转 Owner 晨批，本班零施工、零注册、零阈值改动；`ch_vm_config_snapshot.py` 的 `[INVARIANTS]` 里"型 C 未开"是判据面文字，未随之扩面。**晨批若要批，判据材料在 `dr_drill_plan.md`（本袋可落，见下"本班落地面终态"）与袋二节的三型实测数**。
  - **D 不取**＝保留每小时 chRan 自动取数任务（本班未删任何既有仪器；昨夜自建的 `d39ddeb6` P2 读数自动化今晨起每次以幂等闸自跳过，34.5s/次，其对象已于 `6afe494afe` 入册，是否随 P2 收口一并撤由统筹定）。
  - **同窗互闷＝错峰**＝纯调度面（月度演练窗挪开备份链），**未动 1800s 超时、未动任何判据**（O-7 因此在册仍开，见呈报件）。附带一条已实现的错峰事实：型A 注册脚本把 cadence 定为 **MONTHLY 5 日 10:00** 而非 1 日，脚本头注原文理由＝"the PG restore drill (ZEPHYR-RESTORE-DRILL) owns day 1 04:30, and the main backup chain owns 06:00"——这是 VM 快照腿自身的错峰，**不解决** O-7（PG 演练↔备份链同窗）那一对。
- **统筹 12:33 落进主区本册的 31 行未提交开工令（`chief-coordinator-st-20261014`，"备份日班开工令·VM 型A 自动腿抢救"）的处置**：
  - 该 31 行**未随本班任何袋带出**（不是本班内容，带出＝归属篡改；它此刻仍是主区工作树的未提交脏件，归其作者或统筹处置，本班不复位、不代提交）。
  - 其使命 1–5 与本班 12:29 已入袋的 0008 逐条对表：②抢救五死袋（cascade_stale 三件"基底钉当下 dev sha 重投"＝本班已做；"0005 新件先 `--add-design-node` 登记再投"＝本班已做，见上一节全程；"0002 台账不自裁、走队列仲裁"＝本班已做，台账另袋）；③落地判据"只认 git HEAD"＝本班采用（`git ls-files`／`git log -- 该件`／`git show HEAD:<件>` 三形）；⑤连带核对＝**已实测且结论为"未解决"**：`backup_ch_vm.ps1:8` 头注明其体已封印仅供引用，而 `restore.ps1` 的 vm 腿仍读 `F:\ch_vm_backup`/`G:\backup\ch_vm_backup`（:69/:73/:296/:406/:408）＝旧周频 .vhdx 全镜像路径，**型A 落地不解决该引用位**，恢复侧目前没有任何读取 `G:\backup\ch_vm_config\` 的通道（列为呈报件 N-2）。
  - **唯一未取的一条＝"进场：新 sid（st-bakday2-20261014）＋新 worktree"**。理由（登记而非静默违令）：同 12 件在 12:29 已有在途袋，另开新车道对新 sid 重做＝同件双袋撞车，而"同会话/同件后袋静默 supersede 前袋"与"TAKEOVER-PENDING 按死会话 dirty_files 挡重投"两条都在册死信族里；本班车道 `st-bakdr-20261013` 会话在注册表面活（`last_heartbeat` 12:28 实测 `status=alive`，pid=0 逻辑会话形态），故由本班续跑到落地，落地态如实交回统筹定性（若统筹仍要新 sid 接手，落地后已无残余可接，交接面＝本节呈报件三条）。
- **②在册收班序列（本班实际兑现态，逐条给"已做／未做＋为何"）**：
  1. 在飞袋落地＋逐字读回＝**未毕**（袋8 死于跨班接管面；读回见上"落地读回"段，代码面零落地是事实）。
  2. release 自家 claim＝**故意不撤**：撤 claim 而袋与车道仍在，等于把 12 件挂回无主面、并把唯一存活字节（车道 staged 面）交给回收器；统筹 13:06 落的放量三班令里"硬前置＝bakdr/infoaxis 两 sid 抢救名单保全"与本处置同向，故本班保车道＋保 claim 到清面为止。
  3. 停自家守护进程＝**按 PID 精确，禁按映像名**（在册事故：/IM 全杀扫掉 14 班心跳与在途提交）。实测态＝昨夜起的 `pid=24164` 心跳已自退（12:1x `Get-Process` 查无），现行心跳由 `pid=5020` 的 keepalive 逻辑会话守护代持，该进程**非本班独有**（它代持多个逻辑会话），本班不杀，交回统筹按归属处置。
  4. 注销会话＋`session_worktree.py archive --execute` 收车道＝**不做**，理由同第 2 条（车道是 12 件字节的唯一存活面，除四件父蓝图污染外仍为 13 件 staged 面）；待统筹清面后由接手班按下面"三条命令"收。
  5. **撤回自家 reaper keep 行＝本班选择不撤，理由摊开**：`data/runtime/process_reaper_keep.txt:380-381`（注释行＋`ch_vm_config_snapshot`）护的是**月度计划任务的执行体**，不是本班在飞批任务；收班即清的意图是"别给下一班留在飞批次的豁免"，而这里删行会给下一班留"首个月度自动跑被 reaper 误杀且新鲜度告警无读数"的 latent failure。故保留并在册披露；若统筹判该行应随任务生命周期走，请在 A 腿点火后再摘（任务不存在时它无害，任务存在时它是必需）。
  6. `99_delivery` 终账＝本班不新建交付册（净零：本战役交付面已在 `backfix_campaign/00_ledger.md`，另开一册＝第二真源），改为下面"三条命令＋三条呈报"作为交接卡内容，落点即本册。
- **落地读回（本令②第 1 步，只认 git HEAD 面；本班终态＝代码面仍零落地，读数如下）**：`git -C D:/ZephyrAlpha ls-files` 对 `scripts/backup/ch_vm_config_snapshot.py`／`scripts/tasks/register/register_ch_vm_config_snapshot_task.ps1`／`tests/data/backup/test_ch_vm_config_snapshot.py`／`docs/_working/backfix_campaign/dr_drill_plan.md` 四件**全部零输出**（13:0x 实测，未跟踪）；`git log --oneline -1 -- scripts/backup/restore_drill.py` 仍＝`9f270424aa8`（他班袋，非本班修法）；三册 `grep -c ch_vm_config_snapshot` 对 dev 面全 0。队列面终态＝本会话名下**八袋：0007 done／0001–0006 dead／0008 dead**。⇒ 本班**没有**可交的回滚读回，如实记此不冒充。
- **交付终态清单（三清单口径：已交＝双证齐且 dev 面 grep 得到／在途＝有袋无落地／未交＝点名即空）**：
  - **已交且落地（dev 面可 grep）**：仅两件——**P2 chRan 验收读数**＝`6afe494afe`（dumps_exposure_min 0.23 分，CH 真跑首轮 10-14 06:00 那发；令五验收尾巴就此销）；**本册**（本次袋：夜班四节＋更正节＋本节）。
  - **在途（有袋有字节、被跨班接管面挡落地）**：袋8 的 12 件＝型A 执行体＋注册脚本＋31 测；PG 演练打分器乱码修法（输入侧单口钉位）＋其 44 测；四类恢复演练方案册 `dr_drill_plan.md`（零施工）；裁定 517 投影行；token 两条＋翻译一条＋资源画像种子与别名。**字节唯二存活处**＝车道 `.worktrees/st-bakdr-20261013`（13 件 staged 面，13:0x 实测仍在）＋队列 blob（`dead/q-…-0008.json` 与其 blobs 快照）；车道若被回收即只剩袋快照，故"车道暂不撤"在本班是有承重理由的动作（Owner 2026-10-14 亦已认可"lane-staying-until-landing correct"）。
  - **未交（点名即空，如实）**：型B／型C 任何施工（转晨批）；演练波 1-2（转晨批）；月频自动腿点火回执（A 腿，前置未成就）；`tests/backup/test_stage3_vault_mtime_and_verdict.py` 的 9 支既有红（令卡边界点名＝维护六班第 13 条，本班不代修）；`backup.ps1` 本体（令卡点名 d640460050 已是新字节，不返工）。
- **复核命令（本节正文抽出，已在本机真值面原样跑通，期望值随注）**：

  ```
  # 1) 落地判据三形（落地前实测：第 1 形空／第 2 形零输出／第 3 形 fatal；落地后应三形齐给出同一件）
  git -C D:/ZephyrAlpha ls-files scripts/backup/ch_vm_config_snapshot.py
  git -C D:/ZephyrAlpha log --oneline -1 -- scripts/backup/ch_vm_config_snapshot.py
  git -C D:/ZephyrAlpha show --stat --format=%H HEAD -- scripts/backup/ch_vm_config_snapshot.py
  # 2) depgraph 登记正证（现值期望＝[(16612361, 'generated', 'production', 'file', 'D_INFRASTRUCTURE', 'MOD-INF-043')]；
  #    登记前实测 []＝死因坐实；先用默认 planned/design 登记过一次，13:07 已按真实生命周期转正）
  python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as G; c=G(autocommit=True, read_only=True); cur=c.cursor(); cur.execute('SELECT node_id,build_status,design_maturity,granularity,domain_id,blueprint_id FROM nodes WHERE node_id=%s', (16612361,)); print(cur.fetchall()); c.close()"
  # 2b) 命中面复量（门的面定义＝held_files∪worktree dirty∪staging；本班 12 件命中 2 条 open 条目）
  python -c "import json,pathlib,sys; sys.path.insert(0,'scripts/governance'); from session_takeover_ledger import entry_match_surface as s; rows=[json.loads(l) for l in pathlib.Path('.runtime/takeover_ledger.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]; latest={r['sid']:r for r in rows if r.get('sid')}; mine={'docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml','docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml','scripts/governance/script_manifest.yaml'}; [print(r['sid'], sorted(s(r)&mine)) for r in latest.values() if r.get('status')=='open' and s(r)&mine]"
  # 3) 型A 首拍双证的磁盘面（期望＝两个完整目录、各自 tar_members=sha_lines=915、tar_sha256 同值 7dcf9b0aa8…，两份 9 秒级 one-shot）
  python -c "import json,glob,pathlib; [print(pathlib.Path(d).name, json.loads((pathlib.Path(d)/'snapshot_manifest.json').read_text(encoding='utf-8'))['started_at_utc'], json.loads((pathlib.Path(d)/'snapshot_manifest.json').read_text(encoding='utf-8'))['finished_at_utc'], json.loads((pathlib.Path(d)/'snapshot_manifest.json').read_text(encoding='utf-8'))['guest']['tar_members'], json.loads((pathlib.Path(d)/'snapshot_manifest.json').read_text(encoding='utf-8'))['guest']['sha_lines'], json.loads((pathlib.Path(d)/'snapshot_manifest.json').read_text(encoding='utf-8'))['guest']['tar_sha256'][:16]) for d in sorted(glob.glob('G:/backup/ch_vm_config/*'))]"
  # 4) 月频自动腿在位否（注册前应无输出＝TASK_NOT_FOUND；注册后应见 State 与 下一个 运行时间=每月 5 日 10:00）
  powershell -NoProfile -Command "Get-ScheduledTask -TaskName 'ZephyrAlpha-CHVMConfigSnapshot' -ErrorAction SilentlyContinue | Select-Object TaskName,State | Format-List"
  ```

- **候裁与呈报（本班只显形不自裁）**：
  - **O-4（候 Owner）**：型B（客户机 OS+程序文件级 ≈13 GiB/份）与型C（盘级 563 GiB/份）开否——两型的存储成本与 G 仓余量实测在袋二节内；本班未开、未拍。
  - **O-7（候裁，且本班按错峰令未治）**：月度 PG 演练与备份链 Stage 3 同窗互抢 IO，实测被 1800s 超时闷死一次（`TimeoutExpired`，八键报告契约与临时库清理均兑现＝**红在超时不在分类器**）。令面"错峰＝纯调度面"已执行到"结论登记"，但**演练窗口的实际改期尚未落地**（改期要动 `scripts/tasks/` 注册面或计划任务时刻，属另一件授权）；抬超时＝触判据面，本班未动。
  - **O-8（归册主）**：`render` 即吃他人行的投影滞后两处（ruling/capability 两册的投影面与 PG 账本之间存在 lag；本班未量当日 lag 数值，只登记"本班按 dev 字节为基注入、未手改投影册"这一处置形态，数值归该册册主的巡检尺）。
  - **N-2（呈维护线，新）**：`restore.ps1` 的 vm 恢复腿仍指旧周频 .vhdx 全镜像路径（:69/:73/:296/:406/:408），型A 配置面快照目录 `G:\backup\ch_vm_config\` **无任何读取方**；即"可回滚 VM 定义面"的证据链在 `ch_vm_config_snapshot.py --verify-only` 自身（证2 临时机重建），**不在生产恢复手册里**。补该引用位＝改恢复语义面，超本班令卡授权，列为呈报。
  - **N-3（呈报，新脚本未进清单册）**：型A 执行体与注册脚本均无 `__manifest__` 元数据块，故 `scripts/governance/script_manifest.yaml` 内无其条目（dev 面该册 `missing_manifest` 现值＝**155** 支同族，实测 `git show dev:scripts/governance/script_manifest.yaml`）。实测**无任何 pre-commit 门禁读该册**（`grep manifest_admission` 仅命中 d11_compliance 巡检工具与 `config/nav_table_mapping.yaml` 导航行），不构成落地阻碍；补块属新能力声明面，本班不顺手扩。
  - **N-4（呈报，depgraph 登记形态的坑，新）**：`--add-design-node` 的 `build_status` **默认值是 `planned`**（`apply_depgraph.py:5723`），而 file 粒度设计节点会顺 blueprint 归属把**父蓝图 frontmatter 的 `design_maturity` 从 production 拖到 design**（实测车道四件被重写）。建议处方＝对"代码已成形、只补 L1 登记"的场景，登记时**显式带 `generated`**（或登记后立即 `--transition-build-status`/`--transition-design-maturity` 双转，如本班所做），并在该写命令的在册文案里点明这一父蓝图污染面；本班未改 `apply_depgraph.py` 的默认值（改默认＝改他人施工面，需裁）。
  - **N-5（呈统筹，跨班 TAKEOVER-PENDING 存量＝本班交付的唯一致死因）**：`entry_match_surface` 的咬合面由台账**存储面**决定，而 192 条 open 条目里存在大量"claim 已 TTL 消失、车道仍在"的陈旧面（实测 infoaxis：存储 held=3／实时 held=0＋worktrees=1）。这类条目**既拦不住真正的归属篡改**（篡改来自袋与 index，而袋内残留件按 D-2 裁定不入面），**又会长期拦死无关会话的正门交付**（本班袋8、维护七班多袋同形）。三条候选路（都要统筹定，本班不自拍）：①由维护线按战役归属逐条 `--resolve`（需真接管）；②由统筹授权一次 `--sweep-absorbed --execute` 的事实归因清算（本班只跑了 dry 分类面、未 execute，因其语义前提＝"已吸收"，infoaxis 两册并未落地，不满足）；③给该门加"存储面与实时面双读一致才咬"的治本改口（＝改门判据，须裁）。
- **留给下一班的三条命令（照抄即可，勿再考古）**：
  1. 清面（统筹/维护线做一次）：`python scripts/governance/session_takeover_ledger.py --resolve st-infoaxis-20261013 --by <接管者> --note <车道成果 merge 或 abort 的结论>` ＋ 同形处理 `st-cdx-sent-20261013`（后者命中件 `scripts/governance/script_manifest.yaml` 可由本班侧拆袋规避，前者不可）。
  2. 复投代码袋（字节零动，直接重放本班 12 件）：`python scripts/git_commit.py --session st-bakdr-20261013 --project-root D:/ZephyrAlpha/.worktrees/st-bakdr-20261013 --files <车道绝对路径清单，见 .runtime/tmp/bakdr_20261013/bag8_files.txt 逐行前缀车道根> --message-file .runtime/tmp/bakdr_20261013/bag8_message.txt --allow-non-worktree --allow-multi-domain --enqueue`（要点：①**必须用主区副本的 git_commit.py**，在车道里跑车道副本会静默进影子队列根；②`--files` 传**车道绝对路径**，因为相对路径按 cwd 解析、主区 cwd 下这些件不存在会报"文件不存在且未被跟踪"；③两道逃生旗都是 2026-08-13 用户裁定 AI 可默认使用的留痕通道，本班已核对"只提自家 claim 件、不搭便车"前置）。
  3. 点火 A 腿（Owner 批复原文＝"本袋落地后跑 register_…ps1"）：`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_ch_vm_config_snapshot_task.ps1`，验收两条＝`Get-ScheduledTask ZephyrAlpha-CHVMConfigSnapshot` 在位且 NextRunTime 为每月 5 日 10:00 ＋ 当场手动实跑一发按首拍三证口径收数（首拍实测 9 秒级：`2026-10-13T16:15:29Z→16:15:39Z` 与 `16:23:11Z→16:23:20Z`，两份 tar_members=sha_lines=915、tar_sha256 同值 `7dcf9b0aa81c01fb`）。回退＝同文件加 `-Unregister`。
- **零面声明（本班全程，含两处"不是零"的如实例外）**：未改任何判据·阈值·保留线·计划任务·任务时限；未拷任何 `.vhdx` 数据字节；`F:` 零写；`G:` 面只读列举 `ch_vm_config/`，零写零删（两目录系昨夜产物）；未删任何仓内文件；未杀任何进程；未注册或复挂任何仪器。**两处不是零，如实列**：①PG 面＝depgraph nodes 新增并转正本班一行（`node_id=16612361`，`planned/design`→`generated/production`，两次写命令各带一次当日架构库 JSON 备份 `architecture_20261014_042323.json`/`architecture_20261014_050734.json`，均 19/19 表）；②车道面＝后台重扫两次重写父蓝图四件（第一次是 production→design 降级、第二次只剩 CRLF churn），本班 `git checkout --` 还原该目录后车道回到 13 件 staged 面，**主区面全程零写零删（脏件 643→643、DR 四件 sha 逐件全等）**。depgraph 全量重扫（PID 4652/42364/43384）系 `apply_depgraph.py` 写命令的在册自动后果，非本班另起。
- **署名**：adjudicator=st-bakdr-20261013（收口班：上一班"落地"叙述的更正＋袋5 死因修因全程含登记形态自纠＋袋8 重投及其跨班接管面死因四条路评估＋四步收口令逐条兑现态（含两条"有意不撤"的理由摊开）＋五条呈报与三条待执行命令；A 腿仍未点火＝前置未成就，未冒充已交）。

## 收口补账：docs 袋落地读回（`0feacd9eed`）＋基底病根新证＋第五条路及其代价（st-bakdr-20261013，2026-10-14 13:3x-13:4x）

- **落地读回（只认 git 面，13:3x 实测，非叙述沿用）**：`q-20261014-st-bakdr-20261013-0010` → `landed_id=0feacd9eed852a371dcce78e0d2828735f175a52`（2026-10-14 13:33:55）；`git show --name-only` 读回该 commit 文件面**恰两件**＝`docs/_working/backfix_campaign/00_ledger.md`＋`docs/_working/backfix_campaign/dr_drill_plan.md`；dev 面本册 **1652 行／18 节**，其中 `"## 更正节" in dev`＝True、`"## 收口班账" in dev`＝True；方案册 dev 面 **217 行／11 节**（零施工文档，Owner 晨批 B／C 两项的判据材料就此在树）；主区工作树本册字节与 dev **全等**（＝本班在主区的装配面不留脏）。
- **一处袋号与消息文案不符，如实登记不抹**：入队号 0010、commit 首行写"袋9"（复用上一枚被挡袋的 message 文件未及改号）。内容语义零影响；**不改历史**（不 amend、不重写已发布 commit），在此登记即止。
- **新证一（把连撞两次的真因钉死，并给出可复用的正解）**：袋9 死于 `[landing] 非注册表族件双侧皆改真冲突: 00_ledger.md`，实测病根**不是内容冲突**——本袋字节＝dev 现字节＋纯尾追加（`Counter(dev)-Counter(out)`＝空）；病根在**基底取自车道 HEAD**：车道 `st-bakdr-20261013` 的 HEAD 停在 `9ee25793bc`（本班从未在车道落 commit，12 件只活在车道 index），故凡从该车道入队，`base_head` 一律记 `9ee25793bc`，而本册在 dev 已两次前进（13:06:32 统帅开工令 `89c96878b9`）⇒ 落地侧判"双侧皆改"。**A/B 对照只此一组**：同一文件、同一字节，车道面入队＝死，主区面入队（袋10）＝活。⇒ 给下一班的口径＝**热台账/共享册一律"主区取 dev 字节为基装配＋从主区入队"（`--allow-non-worktree` 留痕），车道面只留给非共享件**；这与在册"预筛基底取 --worktree-root 的 HEAD 而非 --base-head"是同一条坑的两次显形。
- **新证二（自我放宽：前一节"唯一正解"的结论过强，实际存在第五条路，代价三条摊开）**：前一节按"CREATE-GUARD 有 PG 第三源可正证放行"推出"拆袋不解除挡"。该推断只对**只拆 capability 册**成立；还存在第五条路＝**两册同拆**——落 8 件（`ch_vm_config_snapshot.py`／注册 `.ps1`／`test_ch_vm_config_snapshot.py`／`restore_drill.py` 与其测册／画像生成器／`resource_profile_registry.yaml`／翻译册），把 `capability_canonical_file_registry.yaml`、`ruling_registry.yaml`、`script_manifest.yaml` 三件留待清面后再投。其代价：
  1. 注册脚本的 **P2 裁定门读 YAML 投影**，裁定 517 行不入册＝A 腿仍点不着（Owner 批复"落地后跑注册"会停在"代码在树、任务无门"的半落地态）；
  2. 件与其裁定/token 分册＝在册拆袋教训（`queue-cross-bag-dependency-trap`：token 须与件同袋）的反例形态，dev 面会出现"有执行体无裁定"的窗口，后来人按册判落地会误判；
  3. 执行体 docstring 与本袋消息里的 517 引用须先去井号，否则自触 REFERENCE-INTEGRITY（可披露的改制，不是可省的动作）。
  **本班不自选此路**：它把一个已获 Owner 四分法批复的动作（A 腿点火）改成交付半途形态，且动的是判据的**读取面**。按"执行者不自裁、把选择权交回"的在册纪律，摊给统筹**二选一**＝①**清面**（对 `st-infoaxis-20261013`／`st-cdx-sent-20261013` 做真接管，12 件整袋一次落地，A 腿随即点火）②**拆册**（8 件先落，裁定与 token 两册随清面后补投，A 腿延后到裁定行入册）。两条都给：本条上方"留给下一班的三条命令"仍逐字有效。
- **本班终态一句话**：P2 读数与两份文档已在 dev（`6afe494afe`／`0feacd9eed`）；型A 一族字节在**两处**存活＝车道 index（13 件）＋袋快照（`dead/q-…-0008.json` 与其 blobs）；A 腿未点火；车道与 claim **有意保留不撤**（撤＝把唯一存活面交回无主区），待统筹按上述二选一改判后再收。
- **署名**：adjudicator=st-bakdr-20261013（收口补账：docs 袋落地读回＋基底病根新证＋第五条路及其三条代价；不自选、不动判据读取面、不改已发布历史）。

## 收口再补：claim 面更正＋车道脏面来源查清（st-bakdr-20261013，2026-10-14 13:4x-13:5x）

- **先更正一处刚落地（`f4ac403cd`，13:44:24）文本里的事实错误，旧案留册不抹**：上一节与"收口班账"②.2 条写着"车道与 13 件 claim **有意保留不撤**"。13:4x 实测＝**该说法不成立**：`python scripts/lock_files.py list --session st-bakdr-20261013` → `CLEAN — 持有者 st-bakdr-20261013 无任何文件锁`（`release-all` 亦回"没有持有任何锁"），`session_registry.json` 本班条目 `held_files=[]`。成因＝`acquire` 缺省 TTL 30 分钟，本班最后一批锁（12:3x 随袋8 入队续租、13:2x 手工 acquire 两件）自然到期，**不是本班主动 release**——收班序列第 2 条（release 全部自家 claim）因此**达成，但达成方式是到期不是动作**，如实记，不占"我已收锁"的功。
- **随之作废的是一条推理**：上一节把"保留 claim"说成"撤＝把唯一存活面交回无主区"。这句错了，当场承认：**claim 锁不保存字节**，只挡他班进场。字节存活面另在两处＝①车道工作树 ②袋快照 `dead/q-20261014-st-bakdr-20261013-0008.json` 的 `files[].blob_ref`。保留 claim 的真实代价反而是**挡住统筹派来的抢救班与热册他班**（本班三本热册的锁恰在 infoaxis/归档各族要用的路径上），本班不占这个便宜。
- **车道脏面的来源已查清（原判"外来污染"是过度警觉，实测为已落地内容的同步回填）**：13:5x 实测 `git -C .worktrees/st-bakdr-20261013 status --porcelain` ＝ **22 行**，比本班交付面多出 9 行。分层核账（不按状态位整批处置，按 `lane-dirt-cleanup-must-whitelist-own-work` 在册纪律）：
  - **本班面 13 行**＝首列非空者（12 件套＋已落地的 `00_ledger.md` 旧 staged 态）；
  - **外来 8 行**＝`src/zephyr/gov_enforcement/commit_gates/` 四门件（`_diff_helpers.py`/`manual_only_permanent_gate.py`/`perm_trigger_gate.py`/`syntax_validation_gate.py`）＋`tests/gov/governance/commit_gates/` 四测件，车道 mtime 13:25:21，正对 dev 上 **`c7ef3e7e53`（维护七班·车道A 甲码面先行袋，13:25）**；抽 `_diff_helpers.py` 与 `test_perm_trigger_gate.py` 逐字节对拍：车道 `git hash-object` ＝ 主区同件 ＝ `4cd874647012`/`94f959e561fa` **同值**；
  - **未跟踪 1 行**＝`docs/_working/infoaxis/`（2 件，车道 mtime 13:17:47），两件 `hash-object` 与 `dev:<路径>` rev-parse **全等**（`6f1df8643553`）。
  ⇒ 结论＝这 9 行**全部是"已在 dev 的字节"被回填进本班车道**（车道 HEAD 仍停 `9ee25793bc`，故对车道呈"脏"），**不是**他班未落地工作被塞进我车道。真实残留风险只有一条形态性的：**谁若对本车道跑整树 `git add -A`／整树 merge，会把这 9 行按"本车道改动"计入**（内容因与 dev 同值不会造成语义损坏，但归属账面会脏）。故接手班取件必须**按文件名白名单取 12 件**，勿整树搬。
- **车道保留判据（理由换承重，结论不变）**：留车道不是为保 claim（已无锁），而是 `session_worktree.py archive --execute` 会移除工作树＝**抹掉上面①面**，只剩②袋快照；而 blobs 面按在册机制可被死信放量流程搬迁（统筹 13:06 放量三班令自述"硬前置＝bakdr/infoaxis 两 sid 抢救名单保全"＝同向判断）。故本班**不执行 archive**，交回统筹在"清面／拆册"二选一后定：走清面＝车道留着等 12 件整袋复投；走拆册＝先从车道取 8 件再收车道。
- **两面复量命令（本节正文抽出，13:5x 已在真值面跑通；先取字节再动车道）**：

  ```
  # 面①：车道工作树（期望＝22 行；本班交付面只看首列非空的 13 行）
  git -C D:/ZephyrAlpha/.worktrees/st-bakdr-20261013 status --porcelain
  # 面②：死袋 blob（期望＝12 项，逐项 blob_sha256 前缀如下，可逐件与车道字节对拍）
  python -c "import json,pathlib;d=json.loads(pathlib.Path('.runtime/commit_queue/dead/q-20261014-st-bakdr-20261013-0008.json').read_text(encoding='utf-8'));print(len(d['files']));print(*[f['path']+' '+f['blob_sha256'][:12] for f in d['files']],sep=chr(10))"
  ```

  面②实测 12 项逐名读数（本机 13:5x 原样跑通）＝`dr_drill_plan.md 22bd10d68728`｜`scripts/backup/ch_vm_config_snapshot.py c6f9ffafd170`｜`scripts/backup/restore_drill.py 1851d17ee68a`｜`scripts/tasks/register/register_ch_vm_config_snapshot_task.ps1 9bcc961671e2`｜`tests/data/backup/test_ch_vm_config_snapshot.py 82b14d659c91`｜`tests/data/backup/test_restore_drill.py d3ab8c078e0f`｜`scripts/governance/generators/generate_resource_profile_registry.py b620a930a179`｜`config/resource_profile_registry.yaml d9f1a0baf976`｜`scripts/governance/script_manifest.yaml 4c5ae1a3d4e2`｜`capability_canonical_file_registry.yaml 6cf53e3e2713`｜`ruling_registry.yaml 437993e2f84f`｜`module_translation_registry.yaml 41a9037ebe01`。**注**：本册（`00_ledger.md`）**不在**袋8 的 12 项内——它随袋10/袋11 已落地 dev，勿按此清单找它。
- **终态（与上一节同口径）**：dev 面已落＝`6afe494afe`（P2 读数）＋`0feacd9eed`（更正节＋收口班账＋方案册 217 行）＋`f4ac403cd`（收口补账）＋本节待落；**代码族 12 件仍未落地**，挡口＝跨班 TAKEOVER-PENDING 两条陈旧条目（他班面，本班零触碰、未 `--scan`）；A 腿未点火（其 P2 裁定门读 YAML 投影，裁定 517 行未入册）；本班 claim 锁面＝空（到期）；车道＝在，保留理由按本节改判据。
- **署名**：adjudicator=st-bakdr-20261013（收口再补：claim 事实更正＋车道 22 行分层核账与来源查清＋两面复量命令实测读数；主动认错一处刚落地叙述与一条错误推理，不改已发布历史）。

## 收口末账：挡道两半的"可救性"分级实测＋三步解锁序（st-bakdr-20261013，2026-10-14 13:5x-14:0x）

- **尺换成在册那把（不是 `git status`，是"独有行"）**：按 `takeover-pending-block-forensics-and-escalate` 的处置边界，文档件可救性判据＝`Counter(它道工作树面) − Counter(dev 面)` 的**独有行数**；独有行 **=0** ⇒ 它道对该件零未落地成果（逐行等或严格落后），属"可对齐"形；独有行 **>0** ⇒ 那是**他班未落地成果**，施工班**必须拒动**，交归属方或维护线。13:5x 对挡住本班两条 open 条目的命中件逐件实测（取基三件套齐：显式主区根＋`git show dev:<件>` 断 `rc==0`＋断基线字节下限；车道面按其自身工作树读）：

  | 挡道件（所属 open 条目） | 车道行数 | dev 行数 | 独有行(multiset) | 盘==车道 HEAD | 分级 |
  |---|---|---|---|---|---|
  | `capability_canonical_file_registry.yaml`（st-infoaxis-20261013） | 71464 | 71438 | **31** | False | **拒动**（31 行系它道未落地 token 行） |
  | `ruling_registry.yaml`（st-infoaxis-20261013） | 4729 | 4729 | **0** | False | 零成果面（在册授权形可对齐） |
  | `scripts/governance/script_manifest.yaml`（st-cdx-sent-20261013） | 6946 | 6935 | **17** | False | **拒动**（本班侧本就不带该件，无需处置） |

- **由此把前一节"唯一正解＝真接管"再收准一次（这次带数值）**：真接管只对** capability 那一半**必需；`ruling_registry.yaml` 那一半按在册授权形（`cp -n` 存证＋写 dev 字节＋`write_takeover_entry` 只刷该 sid，禁 `--resolve`／禁 `--scan`）**本可对齐**——但**同一条目的另一半不可对齐**，单刷一半后命中面仍含 capability ⇒ 对本班**无用时**。所以本班维持不动他班字节，并把这条"为什么对齐了也没用"写清，防止下一班去做半吊子刷新（那只会把 infoaxis 的账面刷新成"车道仍脏 12 件"，还动了一个可争议的写操作）。
- **顺带查清的一条相邻事实（不是本班死因，但对 infoaxis 有用）**：infoaxis 名下在途袋 `q-20261014-st-infoaxis-20261013-0018` 13:5x 实测**已死**，死因逐字＝`网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 重跑后仍检测到 hook 修改了文件（裁定#341 方案②…）`，其袋内两件＝`20_ruling_package.md`／`00_ledger.md`（**不含**两本热册）。⇒ 它那 31 行 capability 独有行**不在任何在途袋里**，唯一存活处是它车道工作树；这提高了维护线处置该条目的紧迫度（车道一旦被回收，31 行无处可寻，而 `dead/` 里没有它的 blob）。本班不取、不代存证（那是它的归属面），只把"独有行 31＋无在途袋＋blob 无备份"三件一并报给统筹。
- **本班全程袋账（13:5x 队列面实测清点；本节袋为第 13 枚）**：前 12 袋＝**4 落地／8 死**。落地＝`0007→6afe494afe`（P2 读数）、`0010→0feacd9eed`（更正节＋收口班账＋方案册）、`0011→f4ac403cd`（收口补账）、`0012→8321590c8d`（收口再补＝claim 更正＋车道 22 行分层核账），**第 4 枚即本节所在袋 0013，其 id 由 `git log` 读回**；死因分布＝自因 5（`0001` ghost_session 车道根注册、`0003`/`0004`/`0006` cascade_stale 基底取自车道 HEAD、`0005` NEW-FILE-DEPGRAPH 未登记）、共享面 3（`0002`/`0009` 热台账整文件三方冲突＝同一条基底病的两次显形，`0008` 跨班 TAKEOVER-PENDING），**他班面 1 袋＝本班交付当前唯一的堵点**。
- **三步解锁序（交统筹/维护线按序执行；本班不自执行第 1 步，因其归属不在本班）**：
  1. `st-infoaxis-20261013` 那 31 行 capability 独有行由其归属方落地或由其车道被真接管（merge 回主区／abort 放弃，二选一都要留独有行去向证据）；
  2. 之后 `write_takeover_entry(ROOT, 'st-infoaxis-20261013')` 单口刷一次（**600s 节流窗**⇒一轮写面、超窗后复测，别看被节流那一轮的返回），复测 `entry_match_surface` 对本班 12 件**零命中**；
  3. 复投本班 12 件整袋（命令＝"收口补账"节"留给下一班的三条命令"第 2 条，逐字有效），落地后跑 A 腿（第 3 条命令）并按其验收两条收数。
- **上一节的落地读回（本节写作时已终态，故能给 id）**：`q-20261014-st-bakdr-20261013-0012` → `landed_id=8321590c8d1ea49634a706ad4cd7338523896087`，`landed_at=2026-10-14T13:52:33+08:00`（13:5x 队列 `done/` 面实测）。本节所在袋（0013）的 id 不在本节预判——按在册"落地只认 git 面"的口径，接手班用 `git -C D:/ZephyrAlpha log -1 --format=%H -- docs/_working/backfix_campaign/00_ledger.md` 取权威值即可。
- **署名**：adjudicator=st-bakdr-20261013（收口末账：挡道两半分级实测 31/0/17＋"单刷一半无用时"的推理＋infoaxis 31 行无在途袋无 blob 备份的紧迫度呈报＋本班 12 袋 4 落 8 死清点＋三步解锁序）。
