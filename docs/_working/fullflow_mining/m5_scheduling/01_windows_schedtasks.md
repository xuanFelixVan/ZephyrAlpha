---
ttl: task_bound
creation_token: m5-sched-schtasks-census-20260925
---

# M5 分册 01：Windows 计划任务全景（实测 2026-09-25 01:10~01:30）

> 挖矿会话 st-commitspeed-tbl-20260924。证据命令：`powershell -Command "schtasks /query /fo csv"`、
> `Get-ScheduledTask | ...`、`Get-ScheduledTaskInfo`、触发器 XML 导出。零 commit、只读挖矿。

## 一、环节定义与边界
"什么在什么时候自动跑"的 OS 层。上游=各 register_*.ps1（26 支注册脚本）+ 历史手工注册；下游=本册 02（常驻族）、03（仓内 cron）、04（静默失败）。

## 二、总账
- **项目相关任务 49 个**（ZephyrAlpha* 46 + tilib_indicator_backfill_nightly + RestartMiniQmt + ZEPHYR-RESTORE-DRILL）；另有系统任务（Git Maintenance×3、Wps×3、AliUpdater、NVIDIA、GoogleUserPEH×3 等）与项目无关不展开。
- **禁用 8 个**：RestartMiniQmt、C4Exam_Full0916、C4Exam_OneShot0915、FactoryLaneC_Full0916、FactoryLaneC_OneShot0915、NightlySentiment、TradingWatchdog、WeeklyRest。
- **快照时 Running 6 个**：BeltDaemon、CHHealthProbe、DataScheduler、TickSubscriber、WorktreeDriftWatchdog、AI-Wrapper-Inject（均为周期 re-fire 形态，Running=当次探测/守护实例在跑）。
- LastTaskResult 码：0=OK｜1/3=进程退出码｜267009(0x41301)=运行中｜267011(0x41303)=从未跑过｜267014(0x41306)=超时被杀｜2147942402(0x80070002)=文件不存在。

## 三、静默形态四类（"静默化改造"落点）
| 形态 | 机制 | 任务 |
|---|---|---|
| conhost --headless | conhost 以 headless 会话包 cmd/powershell，真重定向且零闪窗 | BeltDaemon（探测壳）、IndexMinuteEOD、IntradayFundFlow、PostSettlement（09-24 修后） |
| pythonw 直拉 | GUI 子系统天然无窗 | ProcessReaper、WorktreeDriftWatchdog、AltFxECB、BoardIndexRealtime、SectorSnapshot、ConfigCheck、GateFullTreeAudit、MeasureCalibration、PatternMining、Resource 五件（MorningReport/RegenCheck/SamplerScan/SamplerWriteback/ViewPublish） |
| wscript + launch_hidden.vbs | GUI 子系统 SW_HIDE 包 powershell（#ARCH-BOOT-WINDOW-FLASH，2026-09-08 十任务统一改造，design_memos/93） | DataScheduler、TickSubscriber、CHHealthProbe、DeadmanSwitch、TTLRejudgeDaily、AI-Wrapper-Inject、CH-OptimizeMerge-Weekly、DailyBackup、WeeklyVMBackup |
| -WindowStyle Hidden | powershell 自隐（仍有秒级闪窗残留风险） | PaperSession、QMTWatchdog、SimBridgeExecute、TradingWatchdog(禁)、TraeCacheCleanup |
- **QMT 保 Interactive**：guard 三卫士/DeadmanSwitch/PaperSession/SimBridge/QMTWatchdog/RestartMiniQmt 全部 `-LogonType Interactive`——QMT/miniQMT 终端活在本用户会话，改 S4U/SYSTEM 即失明（RestartMiniQmt 禁用仍保 Interactive 即此理）。

## 四、任务全表（按族分组；LastRun=2026-09-24~25 实测）
### A. 守护/常驻族（详见 02 册）
| 任务 | 触发 | 命令行核心 | LastRun/Result | 状态 |
|---|---|---|---|---|
| ZephyrAlpha_BeltDaemon | LogOn+**PT1M** + Time(09-22) | conhost --headless -- powershell -Command `if (-not (Get-CimInstance ...commit_belt_daemon...)) {Start-Process python -m ...commit_belt_daemon D:\ZephyrAlpha}` | 01:15:19 / 267009 | Running |
| ZephyrAlpha_DataScheduler | LogOn+PT5M | wscript launch_hidden.vbs start_scheduler.ps1（guard while-true→python -m zephyr.data.scheduler） | 01:14:29 / 267009 | Running |
| ZephyrAlpha_TickSubscriber | LogOn+PT5M | wscript→start_tick_subscriber.ps1→python -m zephyr.data.tick_subscriber | 01:14:29 / 267009 | Running |
| ZephyrAlpha_CHHealthProbe | LogOn+PT5M | wscript→start_ch_health_probe.ps1→python scripts/ops/ch_health_probe.py | 01:14:29 / 267009 | Running |
| ZephyrAlpha_DeadmanSwitch | LogOn+PT5M | wscript→deadman_switch.ps1（one-shot 读 3 心跳） | 01:14:29 / 0 | Ready |
| ZephyrAlpha_ProcessReaper | LogOn+PT10M | pythonw src\zephyr\trading\process_reaper.py（one-shot） | 01:10:29 / 0 | Ready |
| ZephyrAlpha_WorktreeDriftWatchdog | LogOn+PT5M | pythonw -m ...worktree_drift_watchdog D:\ZephyrAlpha --daemon | 01:15:49 / 267009 | Running |
| ZephyrAlpha-AI-Wrapper-Inject | **PT1M** | wscript→ensure_ai_wrapper_injection.ps1（toolhost 快照补注射） | 01:16:01 / 267009 | Running |

### B. 盘中/交易链（QMT Interactive）
| 任务 | 触发 | 命令行核心 | LastRun/Result | 备注 |
|---|---|---|---|---|
| ZephyrAlpha_QMTWatchdog | Daily 08:45 + 12:55 | powershell -Hidden qmt_watchdog.ps1 | 09-24 12:55 / 0 | QMT 终端活体看门 |
| RestartMiniQmt | Daily 16:00（**禁用**） | powershell -File E:\XtQuant SDK程序化交易\scripts\restart_minimqmt.ps1 | 08-20 / 0 | 库外脚本 |
| ZephyrAlpha_PaperSession | Daily 09:25 | powershell -Hidden start_paper_session_daily.ps1（交易日闸→QMT 活体闸→start_paper_session.py --service） | 09-24 09:25 / 0 | 注册时即 Disabled=92 D3 裁定，现状 Ready（已启用） |
| ZephyrAlpha_SimBridgeExecute | Daily 09:35 + 13:05 | powershell -Hidden run_sim_bridge_execute_daily.ps1（交易日闸→XtItClient 活体闸→sim_daily_runner bridge-execute） | 09-24 13:05 / **4294770688** | ⚠ 见 04 册 §活案 S3 |
| ZephyrAlpha_PostSettlement | Weekly 一~五 15:30 | conhost --headless -- cmd /c python -u run_post_settlement.py >> log | 09-24 15:30 / 0 | 09-24 修复后首跑成功 |
| ZephyrAlpha_TradingWatchdog | （**禁用**） | powershell -Hidden start_trading.ps1 | 1999-11-30 / 267011 | 92 D3：无在产交易进程时不许自动拉起 |

### C. 数据采集/盘后链
| 任务 | 触发 | 命令行核心 | LastRun/Result |
|---|---|---|---|
| ZephyrAlpha_BoardIndexRealtime | Daily 09:20（复活件） | pythonw scripts/data/board_index_realtime.py（尾读 E:/qmt_bridge_sim/ticks3.csv 合成 board_index_tick/1m，ticks3 缺→exit 3） | 09-24 09:20 / 0 |
| ZephyrAlpha_SectorSnapshot | Daily 16:40 | pythonw scripts/data/run_sector_snapshot.py（sector_constituent→snapshot INSERT） | 09-24 16:40 / 0 |
| ZephyrAlpha_IntradayFundFlow | Daily 10:05/11:05/13:35/14:35/15:05 | conhost --headless -- cmd /c pythonw collect_sector_fund_flow.py --once >> logs | 09-24 15:05 / 0 |
| ZephyrAlpha_IndexMinuteEOD | Daily 15:10 | conhost --headless -- cmd /c pythonw collect_index_minute_eod.py >> logs | 09-24 15:10 / 0 |
| ZephyrAlpha_AltFxECB | Daily 23:30 | pythonw scripts/data/fx_ecb_ingest.py --days 7 | 09-24 23:30 / 0 |
| tilib_indicator_backfill_nightly | Daily 02:30 | D:\ZephyrAlpha\scripts\data\backfill_night.bat | 09-24 02:30 / **1** | 
| ZephyrAlpha_NightlySentiment | （**禁用**） | `python.exe scripts/data/run_nightly_sentiment.py`（裸相对路径→0x80070002） | 09-16 / 2147942402 | 已由 schedule.yaml nightly_sentiment 槽替代 |

### D. DataScheduler 伴生（资源/治理生成器族）
| 任务 | 触发 | 命令行核心 | LastRun/Result |
|---|---|---|---|
| ZephyrAlpha_ResourceSamplerScan | LogOn+PT10M | pythonw -m ...resource_sampler scan | 01:10:29 / 0 |
| ZephyrAlpha_ResourceRegenCheck | PT1H（:21） | pythonw generate_resource_profile_registry.py --check --publish-alerts --auto-regen | 00:21:22 / **3**（检出漂移语义，常态化非零） |
| ZephyrAlpha_ResourceSamplerWriteback | Daily 05:40 | pythonw -m ...resource_sampler writeback | 09-24 / 0 |
| ZephyrAlpha_ResourceViewPublish | Daily 05:50 | pythonw generate_resource_week_view.py --publish-alerts | 09-24 / 0 |
| ZephyrAlpha_ResourceMorningReport | Daily 06:31 | pythonw generate_resource_morning_report.py | 09-24 / 0 |
| ZephyrAlpha_MeasureCalibration | 周期周 06:17 | pythonw -m ...measure_calibration | 09-19 / 0 |
| ZephyrAlpha_ConfigCheck | Daily 08:05 | pythonw -m zephyr.infra_ops.config_effect_checker | 09-24 / **1** |
| ZephyrAlpha_GateFullTreeAudit | Daily 03:30 | pythonw run_fulltree_gate_audit.py --quiet | 09-24 / **1** |
| ZephyrAlpha_TTLRejudgeDaily | Daily 18:05 | wscript→run_ttl_rejudge_daily.ps1 | 09-24 / 0 |
| ZephyrAlpha_PatternMining | Daily 09:01 | pythonw -m zephyr.security.ops.fix_pattern_miner run_once | 09-24 / 0 |
| ZephyrAlpha_C4Exam | Weekly 五 14:00 | powershell run_c4_exam.ps1 | 09-19 / 0 |
| ZephyrAlpha_FactoryLaneC | Weekly 五 10:00 | powershell run_factory_lane_c.ps1 | 09-19 / 0 |
| ZephyrAlpha_F06Grid | Weekly 六 23:00 | powershell run_f06_grid.ps1 | 09-19 / **1** |
| C4Exam_Full0916/OneShot0915、FactoryLaneC_Full0916/OneShot0915 | 一次性（**禁用**） | 同上 | Full0916=267014 超时被杀过 |

### E. 备份/恢复/基建
| 任务 | 触发 | 命令行核心 | LastRun/Result |
|---|---|---|---|
| ZephyrAlpha-DailyBackup | Daily 06:00 | wscript→backup/backup.ps1 -Mode all -Force | 09-24 / 0 |
| ZephyrAlpha-WeeklyVMBackup | Weekly 五 06:00 | wscript→backup/backup_ch_vm.ps1 -AutoCheck | 09-19 / 0 |
| ZephyrAlpha-CH-OptimizeMerge-Weekly | Weekly 日 03:30 | wscript→ch/run_optimize_merge_hidden.ps1 | 09-20 / 0 |
| ZephyrAlpha_LibraryLedgerBackup | Daily 03:30 | python scripts/backup/library_ledger_backup.py backup | 09-24 / 0 |
| ZephyrAlpha_LibraryLedgerDrill | Monthly 10-01 04:00 | python library_ledger_backup.py drill | 267011 从未跑 |
| ZEPHYR-RESTORE-DRILL | Monthly 10-01 04:30 | python scripts/backup/restore_drill.py | 267011 从未跑 |
| ZephyrAlpha-IOCheck-Monthly | Monthly 10-01 09:00 | data\runtime\io_check_task.bat | 09-13 / 0 |
| ZephyrAlpha_OllamaServe | 一次性 | ollama.exe serve | 09-20 / 0 |
| ZephyrAlpha_RSSHub | 一次性 | powershell -Hidden `cd D:\RSSHub; pm2 resurrect` | 09-20 / 0 |
| ZephyrAlpha_TraeCacheCleanup | 一次性 | powershell -Hidden（库外 C:\Users\fanzi\scripts） | 09-20 / 0 |
| ZephyrAlpha_WeeklyRest | Weekly 六 05:00（**禁用**） | ops\weekly_rest_guard.ps1 | 09-20 / 0 |

## 五、注册脚本↔在册任务漂移（净零审查点）
1. **register_post_settlement_task.ps1 已被 bc76efe3bf 回退到坏形态**（`-Argument '... >> log 2>&1'` 直喂 python）——live 任务是 8f0e5feba9 修后的好形态；**重跑注册脚本即复断**。详见 04 册 S1。
2. register_guard_tasks.ps1 模板已同步 vbs（防回退），但 PT5M/Parallel/TimeLimit=0 等以任务实态为准（BeltDaemon PT1M、Reaper PT10M 由各自 register 脚本管）。
3. backfill_night.bat 引用 `.runtime\tmp\tilib-probe\night_probe.py`——tmp 卫生清掉后脚本指空。详见 04 册 S2。

## 六、复核命令（10 分钟）
```
powershell -Command "schtasks /query /fo csv" | grep -i zephyr | wc -l        # 数量
powershell -NoProfile -Command 'Get-ScheduledTask -TaskName "ZephyrAlpha_*" | ForEach-Object { $i=$_|Get-ScheduledTaskInfo; "{0}|{1}|{2}|{3}" -f $_.TaskName,$_.State,$i.LastRunTime,$i.LastTaskResult }'
powershell -NoProfile -Command '(Get-ScheduledTask -TaskName "ZephyrAlpha_BeltDaemon").Triggers | % { $_.Repetition.Interval }'   # PT1M
git show bc76efe3bf -- scripts/register_post_settlement_task.ps1               # 回退证据
```
