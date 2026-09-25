---
ttl: task_bound
creation_token: m5-sched-master-health-table-20260925
---

# M5 分册 05：常驻进程 × 健康判据 × 探活命令 总表

> 实测基线=2026-09-25 01:10~01:30。探活全部只读。判据阈值取自各源码 INVARIANTS/注册脚本。
> 心跳文件 BOM 提示：guard 心跳带 UTF-8 BOM（`Out-File -Encoding utf8`），比对时 strip。

| # | 常驻/自动件 | 健康判据 | 探活命令（Git Bash 可跑） | 2026-09-25 基线 |
|---|---|---|---|---|
| 1 | belt 提交传送带 | ① heartbeat_age_s<60 ② lock pid 活 ③ pool_workers=4 | `python -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon --status` | age=0s，pid 23356，绿 |
| 2 | belt 自启任务 | 任务 Running/Ready，触发 PT1M | `schtasks /query /tn ZephyrAlpha_BeltDaemon /v /fo LIST` | Running，绿 |
| 3 | ProcessReaper | last_run 距今 <12min 且 killed 合理 | `python -m zephyr.trading.process_reaper --status` | 01:10:30 scanned=20 killed=0，绿 |
| 4 | DataScheduler guard+child | ① tmp/scheduler.heartbeat 年龄<5min（写频 15s）② 行尾 child_pid 活 | `cat tmp/scheduler.heartbeat` + 进程表核 child pid | guard 17992/child 47472 新鲜，绿 |
| 5 | TickSubscriber guard+child | 同上（tmp/tick_subscriber.heartbeat）；业务面 ticks3.csv 盘中新鲜 | `cat tmp/tick_subscriber.heartbeat` | guard 46316/child 41584，绿 |
| 6 | CHHealthProbe guard+child | 同上（tmp/ch_health_probe.heartbeat）；logs/ch_health_probe.log 持续追加 | `cat tmp/ch_health_probe.heartbeat; tail -2 logs/ch_health_probe.log` | guard 40168/child 8880，绿 |
| 7 | DeadmanSwitch（监护者） | 每 5min 有 fire；tmp/deadman_switch_alerts.log 无新告警=三卫士心跳皆新鲜 | `schtasks /query /tn ZephyrAlpha_DeadmanSwitch /v /fo LIST; tail -5 tmp/deadman_switch_alerts.log` | Ready，绿 |
| 8 | WorktreeDriftWatchdog | ① pythonw 进程在 ② .runtime 审计每日一条 verdict=heartbeat ③ drift 报告新鲜 | `powershell -NoProfile -Command "Get-CimInstance Win32_Process | ? CommandLine -match 'worktree_drift_watchdog'"` | pid 29020，绿 |
| 9 | write_audit_daemon | 进程在（预期寿命 1 天，超龄属正常收割对象非故障） | 进程表 match `write_audit_daemon` | pid 17848，绿 |
| 10 | AI-Wrapper-Inject | PT1M fire，LastResult 非 0x800710E0 | `schtasks /query /tn ZephyrAlpha-AI-Wrapper-Inject /v /fo LIST` | Running，绿 |
| 11 | order_daemon（未接线） | **判据=保持不存在**；若 journal 有 evolution_winner_due 而工单不出=接线缺口 | `grep -rn "OrderDaemon(" src/ --include="*.py" \| grep -v test` → 应仅测试 | 建成未接线（黄） |
| 12 | BoardIndexRealtime | 盘中 CH `board_index_tick` max(ts) 滞后<60s；盘后进程退出=正常 | `python -c "from zephyr.infrastructure.database_service import DatabaseService; ..."`（或 dash 面板看板） | 盘后，进程不在=正常 |
| 13 | SectorSnapshot | 当日 snapshot 行数>0 | CH 查 `sector_constituent_snapshot WHERE snapshot_date=today()` | 09-24 exit 0，绿 |
| 14 | SimBridgeExecute | 每交易日 09:35/13:05 后 sim_bridge_execute.log 追加 exit 0 行；LastResult=0 | `schtasks /query /tn ZephyrAlpha_SimBridgeExecute /v /fo LIST; tail -3 .runtime/logs/sim_bridge_execute.log` | **09-24 无日志+4294770688（红，04 册 S3）** |
| 15 | PostSettlement | 交易日 15:30 后 post_settlement_last_run.log 追加 exit 0/3；LastResult∈{0,3} | `tail -3 data/runtime/post_settlement_last_run.log` | 09-24 exit 0，绿；**注册脚本坏（S1）** |
| 16 | DataScheduler 槽位面 | tmp/scheduler_run.log 持续滚动；catchup_guard 05:30 无 overdue 堆积；哨兵 06:50 产出 | `tail -20 tmp/scheduler_run.log` | 宿主活，绿 |
| 17 | dloop_post / secbuild 两槽 | 交易日 16:45/15:10/09:15 后 Alerter 无 ERROR；总闸文件不存在=启用 | `ls data/runtime/daily_loop_master.disabled data/runtime/sector_state_pipeline.disabled 2>&1` | 闸未落（启用态），绿 |
| 18 | tilib 夜回填 | LastResult=0 且 .runtime/tmp/tilib-probe 日志当日更新 | `schtasks /query /tn tilib_indicator_backfill_nightly /v /fo LIST` | **exit 1 常态化（红，S2）** |
| 19 | 资源族 5 件 | SamplerScan PT10M LastResult=0；RegenCheck exit∈{0,3}=语义内 | `schtasks /query /tn ZephyrAlpha_ResourceSamplerScan /v /fo LIST` | 绿（RegenCheck=3 语义内） |
| 20 | 备份族 | DailyBackup 06:00 exit 0；RESTORE/Drill 月初 267011→月内转 0 | `schtasks /query /tn ZephyrAlpha-DailyBackup /v /fo LIST` | 绿（两 drill 待 10-01 首跑） |
| 21 | news_slow（30 分节拍） | DataScheduler 日志无该槽连续 miss | `grep news_slow tmp/scheduler_run.log \| tail -3` | 宿主活，绿 |
| 22 | OllamaServe / RSSHub | 端口/进程活（低频件，09-20 拉起后无守护） | `powershell -NoProfile -Command "Get-Process ollama,pm2 -ErrorAction SilentlyContinue"` | 未逐项验证（黄） |

## 探活一行流（晨检版，复制即用）
```bash
python -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon --status
python -m zephyr.trading.process_reaper --status | head -3
for f in tmp/scheduler.heartbeat tmp/tick_subscriber.heartbeat tmp/ch_health_probe.heartbeat; do echo "$f => $(cat $f)"; done
powershell -NoProfile -Command 'Get-ScheduledTask -TaskName "ZephyrAlpha*" | % { $i=$_|Get-ScheduledTaskInfo; if($i.LastTaskResult -notin 0,267009,267011,3,1){"{0} LASTRESULT={1}" -f $_.TaskName,$i.LastTaskResult} }'
tail -3 data/runtime/post_settlement_last_run.log; tail -3 .runtime/logs/sim_bridge_execute.log
```
判读：第 4 行只列**语义外**退出码（剔除 0/运行中/从未跑/语义内 3、1）；出现即按 04 册分案。
