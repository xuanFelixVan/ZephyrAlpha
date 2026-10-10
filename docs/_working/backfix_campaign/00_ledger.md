---
ttl: task_bound
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
