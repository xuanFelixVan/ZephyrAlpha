---
ttl: task_bound
creation_token: m5-sched-daemons-census-20260925
---

# M5 分册 02：仓内常驻族全景（启动/心跳/退出/监护）

> 证据：源码头注 INVARIANTS + 实时进程表（Get-CimInstance，2026-09-25 01:2x）+ 心跳/锁文件实测。
> 健康判据与探活命令汇总见 05_master_health_table.md。

## 一、Belt 提交传送带（zephyr.gov_enforcement.rule_bridge.commit_belt_daemon）
- **是什么**：提交队列补位常驻消费者（主消费者=入队方内联自举；daemon 补夜间/无人窗口）。W5 后 k=4 池化排空（thresholds `commit_queue_landing_pool_workers`）。
- **启动**：计划任务 ZephyrAlpha_BeltDaemon 每分钟（PT1M）探测——`Get-CimInstance` 查 cmdline 含 `commit_belt_daemon` 即跳过，否则 `Start-Process python -m ...commit_belt_daemon D:\ZephyrAlpha`（真源 `scripts/register_belt_daemon_task.ps1`；自动把 `commit_belt_daemon` 写入 reaper keep-list）。
- **心跳**：独立线程 30s 续写 `.runtime/commit_queue/belt_daemon.heartbeat`（st-k4-20260923 线程化：长 drain/池化单波不再心跳假死）；上线即打首个心跳（:784），事件后与空闲窗续期。
- **退出条件**：不自杀（无计划任务重拉前时代设计；现被 PT1M 兜底）；纪元变更原地 re-exec（裁定#281①）。
- **监护**：单例锁 `belt_daemon.lock`（PID+TTL 600s+僵尸检测）；reaper keep-list 白名单。
- **实测**：pid 23356 活；heartbeat age=0s；lock `{"pid": 23356}`。
- 已知盲区（12_belt_daemon_trigger.md）：纪元子树不含 scripts/commit_queue.py（改判据不换血）；lease_unavailable 静默 skipped。

## 二、ProcessReaper 进程清道夫（zephyr.trading.process_reaper）
- **是什么**：全仓孤儿/超龄/失控/幽灵进程 one-shot 扫杀（2026-08-28 裁定取代 ide_health_daemon 常驻模型——常驻监护者自身=残留风险）。
- **启动**：ZephyrAlpha_ProcessReaper LogOn+PT10M，`pythonw src\zephyr\trading\process_reaper.py`（直接脚本路径规避 zephyr/__init__ Timer 引入锁饥饿——08-28 13:55 挂死事故修）。
- **心跳**：无（stateless one-shot；Task Scheduler=唯一生命周期主人）。
- **退出**：每轮跑完即退；ExecutionTimeLimit=10min（OS 自清防僵尸——"reaper 不得变僵尸"自食狗粮）。
- **监护**：白名单 `data/runtime/process_reaper_keep.txt`（cmdline 子串命中即豁免；含 belt、git_commit.py、backup.ps1、各长跑班次登记）。
- **实测**：last_run=2026-09-25 01:10:30，scanned=20 killed=0。

## 三、Guard 三卫士族（DataScheduler / TickSubscriber / CHHealthProbe）
- **启动链**（watchdog 架构，真源 `scripts/register_guard_tasks.ps1` + 各 start_*.ps1）：
  `计划任务(LogOn+PT5M, Interactive, MultipleInstances=Parallel, TimeLimit=0, RestartCount 3×1min)` → `wscript launch_hidden.vbs`（防闪窗）→ `start_*.ps1`（while-true 守护）→ python 业务子进程。
- **单实例真源=脚本级**：文件锁+PID+心跳三判——锁 PID 活但心跳陈旧(>5min)=僵尸接管（杀僵尸+清孤儿）；心跳新鲜=即刻退出（"Guard already running"）。Task Scheduler 是哑发射器，**禁**参与单实例判定（IgnoreNew 曾致 08-06/08-07 两天盘中断供）。
- **心跳**：guard 每 15s 原子写 `tmp/scheduler.heartbeat` / `tmp/tick_subscriber.heartbeat` / `tmp/ch_health_probe.heartbeat`（格式 `ISO|guard_pid|child_pid`，tmp+Move 原子换名）。
- **退出条件**：guard 崩=子进程 finally-kill（防复活后双进程）；runtime<10s 判启动失败等 30s 再试；业务子进程崩=guard 自动重启。
- **监护**：彼此独立 + ZephyrAlpha_DeadmanSwitch（one-shot PT5M，纯 .ps1 零 Python 依赖，读 3 心跳，陈旧>10min(DEADMAN_STALE_MIN 可调) 告警到 `tmp/deadman_switch_alerts.log` + Windows 事件日志；最坏 10-15min 发现）。**Feishu 推送已删（09-15 Owner 裁定：告警走前端晋升页）**——当前告警"落文件/事件日志"≠"推到人"。
- **实测**：三心跳 01:25:09~10 全新鲜；guard_pid/child_pid=17992/47472（scheduler）、46316/41584（tick）、40168/8880（ch probe）；wscript 父 8920/28292/38496。

## 四、WorktreeDriftWatchdog（zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog）
- **启动**：ZephyrAlpha_WorktreeDriftWatchdog LogOn+PT5M re-fire；`pythonw -m ... --daemon`；RestartOnFailure 3 次×10min 退避（#99 内存耗尽事故根修）。单实例=msvcrt 非阻塞字节锁；TimeLimit=0（idle 自退）。
- **心跳**：双频节拍（热文件 10s 快扫+interval 全量）；审计 `.runtime/` 每 UTC 日至多一行 `verdict=heartbeat`（R-05 活性锚，与"零漂移"区分）。
- **退出**：idle 1800s 自退（无活跃会话）；PT5M re-fire 即复活。
- **实测**：pid 29020（pythonw）。

## 五、DataScheduler 内部槽位（调度器常驻，schedule.yaml=排班真源）
- **宿主**：python -m zephyr.data.scheduler（pid 47472，APScheduler 单进程多 executor 线程）。**槽位无独立 pid**（resource_profile_registry.yaml L-1 明示）。
- **executor 池**：realtime(4)/intraday_minute(4)/intraday_sector/default(8)/heavy(2)。
- **特殊槽**（编排型，不入 tasks.yaml）：`dloop_post` 16:45 日循环总扳手（总闸 data/runtime/daily_loop_master.disabled）；`sector_close_final` 15:10 / `sector_pre_open` 09:15 板块状态两槽（总闸 sector_state_pipeline.disabled）；`nightly_sentiment` 08:20；`consensus_crosscheck` 23:30；`daily_alt_fx` 23:35。
- **自愈对账**：`catchup_guard` 05:30（档期 vs progress_store 打卡对账，治 monthly_static 错过 32h 事故）；哨兵 `data_supply_sentinel` 06:50（+托管 quality_sentinel 变异巡检）；`calendar_coverage_check` 07:10；`integrity_check` 23:00（只告警）。
- **完整 25 槽清单**见 03 册。

## 六、订单/结算类
- **order_daemon**（zephyr.ai_layer.scheduling.order_daemon）：L5 工单生成守护，事件驱动消费 SchedulingJournal（零定时器零轮询；journal=唯一真源；单例锁 belt 同款 TTL600s）。**现状：建成未接线**——全仓无生产 spawn 点（仅测试引用、无 __main__、无 register 脚本、无计划任务）；不会静默失败，因为它根本没在跑。
- **PostSettlement**：非常驻，工作日 15:30 one-shot（对账+审计+VaR 归档；exit 0/1/3 语义明确；幂等）。09-24 起 live 任务=好形态。**注册脚本已回退坏形态（04 册 S1）**。
- **SimBridgeExecute**：09:35/13:05 one-shot（交易日闸→XtItClient 活体闸→bridge-execute；env=sim；幂等键防双下单）。
- **PaperSession**：09:25 one-shot 包装（交易日闸→QMT 活体闸→start_paper_session.py --service）。
- **QMTWatchdog**：08:45/12:55 看 QMT 终端活体。

## 七、复活件与盘中单进程（无 guard 段）
- **BoardIndexRealtime**（09:20 pythonw 复活）：盘后自然退出、次日任务拉起；盘中无守护——**中途死=当日实时指数断供到收盘，无人知**（探活见 05 册）。
- **SectorSnapshot**（16:40）：一次性 INSERT，幂等。
- **write_audit_daemon**（pid 17848）：会话/incubator 拉起，预期寿命 1 天，超寿由 reaper 收割；单实例锁。
- **heartbeat_daemon ×2 / session_keeper**（st-metaq-gc-20260924 等）：会话级心跳（30s），会话结束自灭。
- **AI-Wrapper-Inject**（PT1M）：one-shot 补注射 toolhost 快照；历史僵尸实例（0x800710E0）已清。
- **OllamaServe / RSSHub(pm2 resurrect)**：09-20 一次性拉起，无常驻守护。

## 八、监护关系总图（谁死了谁兜）
```
Task Scheduler(OS)
├─ BeltDaemon PT1M ──────────→ probe → belt daemon（锁+心跳线程）
├─ ProcessReaper PT10M ──────→ one-shot 扫杀（keep-list 豁免上述全部）
├─ Guard×3 PT5M ──→ wscript → guard ps1(锁+15s心跳) → python 子进程
│                        ↑死→下次 re-fire≤5min 复活；僵尸→心跳接管
├─ DeadmanSwitch PT5M ───────→ 读 3 心跳，>10min 告警（独立于被监者）
├─ DriftWatchdog PT5M ──────→ pythonw daemon（字节锁+日心跳，idle 1800s 自退）
└─ 其余 one-shot 族（数据/资源/备份/治理）
```

## 九、自审闸三态
**挖干**：常驻族 13 支全部有启动方式/心跳/退出/监护四向实证（源码 file:line+进程表双源）。缺口=无。
