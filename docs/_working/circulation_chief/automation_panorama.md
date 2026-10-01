---
ttl: task_bound
---

# 自动化全景核查报告（st-ffchief-20261001）

- 采集时间：2026-10-01 13:07–13:16 +08:00（快照，分钟级时效）
- 采集口径：`Get-ScheduledTask` 全量过滤 + `psutil.process_iter` 全进程 cmdline 扫描 + `.runtime/session_registry.json`（S4-D 分片读侧聚合）+ `.runtime/locks/heartbeat_*.pid`（131 个）+ `data/runtime/process_reaper_keep.txt`（218 个有效条目）
- 活性判定口径（源码真源 `src/zephyr/security/access_control/session_concurrency.py` L8）：`last_heartbeat` 由 heartbeat_daemon 每 30s 刷新；`last_activity` 仅 register/claim_file/register_dependency 刷新，heartbeat 不刷新；daemon 设计 idle>1800s 自动退出；pid=0 会话按心跳新鲜度(90s)判活
- 本报告为只读核查产物，零写操作（除本文档）、零进程处置；所有"杀/清"仅为建议，处置权在 Owner/总包

---

## §1 自动化总表

### 1.1 Windows 计划任务（52 个：Ready 38 / Running 8 / Disabled 6）

| 任务 | 触发 | 执行体 | 存活/状态 | 合规态 |
|---|---|---|---|---|
| ZephyrAlpha_BeltDaemon | Logon+Time 每1分钟 spawn-if-absent | commit_belt_daemon（PID 11620 在跑） | Running | 合规（队列正门基础设施；§2 观察项 G1） |
| ZephyrAlpha_WorktreeDriftWatchdog | Logon+Time 每5分钟 | worktree_drift_watchdog --daemon（PID 9080） | Running | 合规（G1 观察） |
| ZephyrAlpha_DataScheduler | Logon+Time 每5分钟 | start_scheduler.ps1 → zephyr.data.scheduler（PID 21944） | Running | 合规（数据排产主链） |
| ZephyrAlpha_TickSubscriber | Logon+Time 每5分钟 | start_tick_subscriber.ps1 → tick_subscriber（PID 2352） | Running | 合规 |
| ZephyrAlpha_CHHealthProbe | Logon+Time 每5分钟 | start_ch_health_probe.ps1 → ch_health_probe.py（PID 18764） | Running | 合规（只读探针，G2） |
| ZephyrAlpha_BoardIndexRealtime | Daily 09:20 | board_index_realtime.py（PID 18228） | Running | 合规 |
| ZephyrAlpha_OllamaServe | Logon | ollama.exe serve | Running | 合规（LLM 本地底座） |
| ZephyrAlpha_ProcessReaper | Logon+Time 每10分钟 | process_reaper.py | Ready（上次运行 13:07:27，killed=1/reported=13/breaches=1） | 合规（RULE-GUARDIAN 在岗） |
| ZephyrAlpha_MetaqAuditReconcile | Daily 03:50 | check_meta_question_audit_reconcile.py --days 1 | Ready | **违规 V1**：计划任务驱动的 reconciliation，§9.3 禁 cron/Timer reconciler |
| ZephyrAlpha_DeadmanSwitch | Logon+Time 每5分钟 | deadman_switch.ps1 | Ready | 合规（G1） |
| ZephyrAlpha-AI-Wrapper-Inject | Time 每1分钟 | ensure_ai_wrapper_injection.ps1 | Ready | G1 观察：PT1M 永续高频 |
| ZephyrAlpha_EvaporationBlackbox | Time 每5分钟 | evaporation_blackbox.py（只读快照，keep 册 L27 自述） | Ready | G2 观察：Timer 驱动只读哨兵 |
| ZephyrAlpha_DecisionChainSentinel | Daily 09:40 | decision_chain_sentinel.py（盘前只读探针） | Ready | 合规（G2） |
| ZephyrAlpha_DailyBackup | Daily 06:00 | backup.ps1 -Mode all | Ready | 合规（备份总仓 G 链） |
| ZephyrAlpha_WeeklyVMBackup | Weekly 06:00 | backup_ch_vm.ps1 -AutoCheck | Ready | 合规 |
| ZEPHYR-RESTORE-DRILL | Time 04:30 | restore_drill.py | Ready | 合规（恢复演练） |
| ZephyrAlpha_LibraryLedgerBackup / Drill | Daily 03:30 / Time 04:00 | library_ledger_backup.py backup/drill | Ready | 合规 |
| ZephyrAlpha_CH-OptimizeMerge-Weekly | Weekly 03:30 | run_optimize_merge_hidden.ps1 | Ready | 合规（CH 维护） |
| ZephyrAlpha_IOCheck-Monthly | Monthly | io_check_task.bat | Ready | 合规 |
| ZephyrAlpha_AltFxECB | Weekly 23:30 | fx_ecb_ingest.py --days 7 | Ready | 合规 |
| sector_board_synth_eod / sector_eqw_intraday | Daily 15:50 / 15:40 | sector_*_runner.ps1 | Ready | 合规 |
| ZephyrAlpha_SectorSnapshot | Daily 16:40 | run_sector_snapshot.py | Ready | 合规 |
| ZephyrAlpha_IndexMinuteEOD | Daily 15:10 | collect_index_minute_eod.py | Ready | 合规 |
| ZephyrAlpha_IntradayFundFlow | Daily ×5（10:05/11:05/13:35/14:35/15:05） | collect_sector_fund_flow.py --once | Ready | 合规 |
| ZephyrAlpha_NightlySentiment | Daily 22:30 | run_nightly_sentiment.py | Ready | 合规 |
| ZephyrAlpha_PaperSession | Daily 09:25 | start_paper_session_daily.ps1 | Ready | 合规 |
| ZephyrAlpha_SimBridgeExecute | Daily 09:35+13:05 | run_sim_bridge_execute_daily.ps1 | Ready | 合规 |
| ZephyrAlpha_QMTWatchdog | Daily 08:45+12:55 | qmt_watchdog.ps1 | Ready | 合规 |
| ZephyrAlpha_ConfigCheck | Daily 08:05 | config_effect_checker | Ready | 合规 |
| ZephyrAlpha_GateFullTreeAudit | Daily 03:30 | run_fulltree_gate_audit.py | Ready | 合规 |
| ZephyrAlpha_TTLRejudgeDaily | Daily 18:05 | run_ttl_rejudge_daily.ps1 | Ready | 合规 |
| ZephyrAlpha_PatternMining | Daily 09:01 | fix_pattern_miner run_once | Ready | 合规 |
| ZephyrAlpha_MeasureCalibration | Weekly 06:17 | measure_calibration | Ready | 合规 |
| ZephyrAlpha_ResourceSamplerScan | Logon+Time 每10分钟 | resource_sampler scan | Ready | 合规（G1） |
| ZephyrAlpha_ResourceSamplerWriteback / ResourceViewPublish / ResourceMorningReport / ResourceRegenCheck(每1h) | Daily/Hourly | resource 生成器族 | Ready | 合规 |
| ZephyrAlpha_C4Exam | Weekly 14:00 | run_c4_exam.ps1 | Ready | 合规 |
| ZephyrAlpha_F06Grid | Weekly 23:00 | run_f06_grid.ps1 | Ready | 合规 |
| ZephyrAlpha_RSSHub | Logon | pm2 resurrect（D:\RSSHub） | Ready | 合规（外部依赖底座） |
| ZephyrAlpha_TraeCacheCleanup | Logon | clean_trae_cache.ps1 | Ready | 合规 |
| ZephyrAlpha_C4Exam_OneShot0915 / _Full0916 | Time 一次性（已过期） | run_c4_exam.ps1 | **Disabled 未删** | G3：到期残骸，建议删除 |
| ZephyrAlpha_FactoryLaneC_OneShot0915 / _Full0916 | Time 一次性（已过期） | run_factory_lane_c.ps1 | **Disabled 未删** | G3：到期残骸，建议删除 |
| ZephyrAlpha_FactoryLaneC | Weekly 20:00 | run_factory_lane_c.ps1 | **Disabled** | 登记在案（车道C 停用） |
| ZephyrAlpha_TradingWatchdog | Logon+Time 每5分钟 | start_trading.ps1 | **Disabled** | 登记在案（交易看门停用） |
| ZephyrAlpha_WeeklyRest | Weekly 05:00 | weekly_rest_guard.ps1 | **Disabled** | 登记在案 |

### 1.2 常驻进程/守护（非计划任务体系）

| 名称 | PID | 启动 | 属性 | 合规态 |
|---|---|---|---|---|
| commit_belt_daemon | 11620 | 10-01 10:46 | 提交链 Belt（由 BeltDaemon 任务保活） | 合规 |
| worktree_drift_watchdog --daemon | 9080 | 09-30 13:05 | 工作树漂移看门 | 合规 |
| write_audit_daemon --daemon | 12860 | 09-30 13:54 | 写审计 | 合规 |
| zephyr.data.scheduler | 21944（+ps1/vbs 壳 22796/27928） | 10-01 02:37 | 数据排产 | 合规 |
| tick_subscriber | 2352（+壳 9736/18144） | 09-30 13:07 | 行情订阅 | 合规 |
| ch_health_probe | 18764（+壳 19776/24312） | 09-30 22:57 | CH 探针 | 合规 |
| board_index_realtime | 18228 | 10-01 09:20 | 盘中指数 | 合规（交易日进程） |
| git_commit.py --session st-fullscore（在飞） | 22940 + checker_supervisor 36400 | 13:09 | 瞬态提交链 | 合规 |
| heartbeat_daemon ×9 + nohup 壳 ×1 | 见 §2 | 10-01 03:54–11:59 | 会话心跳守护 | **7/9 为僵尸续命（§2）** |
| c10 会话 keeper（bash while-true） ×4 | 3788/18848/21020/31196 | 10-01 03:34 | 25s register 循环 | **违规 V2（sleep-loop+活性伪造）** |
| session_keepalive.ps1（chief7） | 31236 | 10-01 09:29 | 60s×8h session_worktree_start 循环 | **违规 V3（sleep-loop+活性伪造）** |

自动化总数口径：计划任务 52 + 常驻守护/服务 9 + 会话级 keeper/heartbeat 13（9 heartbeat + 4 keeper）+ ZCode 定时自动化 10 ≈ **84 项**（含壳进程不计）。

---

## §2 僵尸守护与孤儿任务清单

### 2.1 会话活性对照（注册表 10 会话 → 真活 1 / 僵尸续命 9 / 死净若干）

| 会话 | 活性证据 | 判定 | 依据 |
|---|---|---|---|
| st-fullscore-20260930 | act=0.8min，git_commit.py 在飞（PID 22940），held=42 | **真活** | 真实治理操作刷新活性 |
| st-c10-t0gpu / st-c10-inv / st-c10-final3 / st-c10-f56ch | act=0min 但由 25s register 循环伪造；pid=0、held=0、logical=False | **僵尸续命** | keeper 循环滥用 register 刷 last_activity |
| st-chief7-20260928 | act=0.2min 但由 session_keepalive.ps1 60s 循环伪造 | **僵尸续命** | 同上；chief7 chat 是否真实在岗不可证 |
| st-menu-w3h-20260930 | act=234min（≈09:18 后零真实活动），3 个心跳守护仍在跳，held=31 未释放 | **僵尸续命** | 心跳在跳、活性锚点已死 3.9h |
| st-menu-w3harvest-20260930 | act=505min，心跳守护 PID 37440 仍在跳 | **僵尸续命** | 同上，8.4h |
| st-circ-g2-20260930 | act=429min，守护 PID 32752 仍在跳，logical=True | **僵尸续命** | 7.2h |
| st-circ-integ-20261001 | act=94min，守护 PID 23344(+nohup 21316) 在跳 | **僵尸续命** | 1.6h |
| st-lanech-20261001 | 已注销（分片仅剩 st-lanech-20261001.6600.tmp 残片；hb pid 文件 40012 已死） | **死净** | — |

### 2.2 僵尸进程名单（处置建议：杀；本代理未执行）

| PID | 进程 | 僵尸依据 | 建议 |
|---|---|---|---|
| 37440 | heartbeat_daemon st-menu-w3harvest | idle 8.4h >> 1800s 自退阈值；pid 文件(24360)陈旧成孤儿 | 杀 |
| 28240 / 24292 / 5724 | heartbeat_daemon st-menu-w3h **×3 重复** | idle 3.9h；同会话三守护互不知晓；无 pid 文件 | 杀（三只全清） |
| 32752 | heartbeat_daemon st-circ-g2 | idle 7.2h | 杀 |
| 23344 + 21316(nohup 壳) | heartbeat_daemon st-circ-integ | idle 1.6h | 杀 |
| 3788 / 18848 / 21020 / 31196 | bash while-true keeper（c10 四会话，25s 循环） | sleep-loop 违规+伪造活性 | 杀（先与 C10 车道 Owner 确认无在途长批） |
| 31236 | session_keepalive.ps1（chief7） | sleep-loop 60s×8h；08:29 起算约 17:29 到期 | 杀或待其 8h 窗口自灭；chief7 须改真实活动续期 |

僵尸进程合计 **12**（含 nohup 壳）。另：13:12–13:14 扫描窗口内出现的 3 个"新 heartbeat_daemon"经 cmdline 核验为本核查代理自身 bash 壳（内嵌脚本含关键字），非守护，已排除。

### 2.3 心跳 PID 文件（131 个 → 有效仅 3）

- 有效（pid 存活且 cmdline 匹配 heartbeat_daemon）：chief7-20260928 / circ-g2-20260930 / fullscore-20260930 共 3 个
- 死 PID：116 个（campaign 09-24～10-01 全数遗留）
- PID 复用假活：12 个（pid 被 conhost/ShellExperienceHost/ollama serve/NVIDIA Overlay/miniquote(QMT) 等无关进程复用，含 c9-f115、c9-finalz、zc-docs、finaldel-final2、menu-t1b6、p2-cens 等）
- 反向孤儿：st-menu-w3harvest 守护(37440)在跑但 pid 文件(24360)已死；st-menu-w3h×3、st-circ-integ 无 pid 文件
- **建议**：128 个陈旧 pid 文件清理；heartbeat_daemon 落盘 pid 时须校验写失败路径（现存 `.runtime/session_registry/` 内 2 个 .tmp 残片：st-circ-a8-20260930.39948.tmp、st-lanech-20261001.6600.tmp，一并清理）

### 2.4 孤儿/残骸任务

- 计划任务一次性残骸 ×4（Disabled 未删）：C4Exam_OneShot0915、C4Exam_Full0916、FactoryLaneC_OneShot0915、FactoryLaneC_Full0916 → 建议删除
- 分片注册表 .tmp 残片 ×2（§2.3）→ 建议删除
- st-c10 系列 keeper 的白名单保护条目 `w3h_keeper`（keep 册 L264）：keeper 若撤，条目一并退役

---

## §3 红线违规清单（对照 AGENTS.md §9.3「永久系统四要素；reconciler 必须事件触发，禁 cron/Timer/sleep-loop」）

| # | 级别 | 违规项 | 条款 | 证据 | 处置建议 |
|---|---|---|---|---|---|
| V1 | 硬 | **ZephyrAlpha_MetaqAuditReconcile**：计划任务 Daily 03:50 驱动 check_meta_question_audit_reconcile.py（reconcile 语义） | §9.3 reconciler 禁 cron/Timer | §1.1 任务表 | 改事件触发（审计写入事件/metadata 变更钩子），或由 Owner 裁定豁免登记 |
| V2 | 硬 | **c10 keeper 循环 ×4**（bash while-true sleep 25，register 伪造活性） | §9.3 禁 sleep-loop；#ARCH-HEARTBEAT-002 活性反转治本被绕过 | PID 3788/18848/21020/31196，cmdline 实录 | 撤销；会话确需保活走 heartbeat_daemon 官方通道（自带 idle 自退） |
| V3 | 硬 | **chief7 session_keepalive.ps1**（Start-Sleep 60 × 8h 调 session_worktree_start） | §9.3 禁 sleep-loop | .runtime/tmp/st-chief7-20260928/session_keepalive.ps1 全文 | 撤销或改为事件续期；8h 死窗口到点会自停（唯一具备自动关闭要素的 keeper） |
| V4 | 硬 | **heartbeat_daemon idle 自退失效**：7 实例超 1800s 阈值仍运行（1.6h～8.4h），其中 w3h 会话重复 3 守护 | 四要素·自动关闭失效；#ARCH-HEARTBEAT-002 设计目标未达成 | §2.2 名单 | 杀僵尸实例；排查 run_daemon idle 检测为何未生效（疑旧版本实例或阈值仅对新启动生效） |
| V5 | 硬 | **活性真源失真**：10 会话中 9 个活性不可信（8 伪造+1 心跳续命） | §9.11 指令/数据边界精神+SSOT 活性锚点 | §2.1 对照表 | 收敛 keeper 通道到 heartbeat_daemon 单一机制；register() 增加调用方频率护栏（同 sid 高频 register 视为 keeper 不刷活性） |
| G1 | 观察 | PT1M/PT5M/PT10M spawn-if-absent 看门链 ×8（BeltDaemon、AI-Wrapper-Inject、DeadmanSwitch、CHHealthProbe、TickSubscriber、DataScheduler、WorktreeDriftWatchdog、ResourceSamplerScan） | 非 reconciler，字面不违；但永续高频无关闭条件 | §1.1 | 登记各看门的退役条件（四要素·自动关闭补全），AI-Wrapper-Inject PT1M 建议降频 |
| G2 | 观察 | Timer 驱动只读哨兵（EvaporationBlackbox PT5M、DecisionChainSentinel Daily、CHHealthProbe） | 只读探针非 reconciler | keep 册 L27/L19 自述 | 维持，登记豁免理由（已在 keep 册留痕） |
| G3 | 观察 | 一次性任务残骸未自删 ×4 + 注册表 .tmp 残片 ×2 | 四要素·自动关闭（任务级） | §2.4 | 清理；一次性任务创建时登记到期自删 |

硬违规合计 **5 项**（V1–V5），观察项 3 组。

---

## §4 白名单清理建议（data/runtime/process_reaper_keep.txt，218 有效条目）

当前有进程匹配的仅 14 条；204 条无匹配，**但不能全清**——其中保护计划任务/周期性未来运行的条目必须保留：

**必须保留（保护未来运行，约 45 条）**：
- 计划任务执行体：`backup.ps1`、`backup_ch_vm.ps1`、`ZEPHYR-RESTORE-DRILL`、`restore_drill.py`、`library_ledger_backup`、`evaporation_blackbox`、`decision_chain_sentinel`、`generate_resource_profile_registry.py`、`generate_resource_week_view.py`、`generate_project_depgraph`
- 提交链/队列基建：`commit_belt_daemon`、`git_commit.py`、`heartbeat_daemon`（泛条目）、`commit_queue(.py drain/_landing)`、`pre_commit`/`pre-commit`
- 周期回填/长跑族：`tick_backfill`、`technical_indicator(+_full_refresh)`、`margin_trading_incremental`、`factory_grid_executor`、`t1_t2_handover`、`pytest` 及 `pytest tests/*` 族、`torchrun`/`train_*`（GPU 预留）、`python -m http.server`、`risk_lifeline_*`（F47 预登记）
- 活跃会话在用：`w3harvest`、`synth_board_minute`、`kline_sector_intraday_from_constituents`、`l2_bench`、`hotspot_profile` 等 10-01 登记族（随战役收官再退役）

**可清理（死会话/死战役遗留，约 155 条）**：
- 会话专属心跳守护条目：`heartbeat_daemon st-backup-cold-20260925-audit / st-commitspeed / st-emomine-20260922 / st-emomine-20260923 / st-fms-chief-20260927 / st-sim-launch-20260923 / st-menu-t1b5-20260930`、`st-bca-c-drill-20260926-heartbeat-daemon`、`st-datapack-20260918-*`、`st-igalpha2/st-igchain-20260918-*`、`st-tilib-clear-20260920-*`、`pqmine-20260927\heartbeat_keeper.py`
- 死战役批处理子串：`amend_*` ×5、`exp_*` ×7、`st-disk-ch-20260921`、`st-disk-final-20260922`、`st-gateaudit-20260922`、`st-regfix-laneB-20260922`、`st-metaq-20260923`、`st-maxexec-20260920*`、`csx_`、`qcloseout_20260928`、`rb_extract2_20260925`、`w5_0_scan`、`fig14_fig15`、`test_fig14`、`c4_*` ×3、`l1_*` ×3、`tmp_cm_*` ×2、`tmp_mirror_phase`、`tmp_release_phase`、`biz4_e1c09`、`flashbiz_e4` 等
- 一次性脚本残骸：`fill_gap134.py`、`fillA/fillB/fillCD_*`、`patch_missing_bypair.py`（st-finaldel-valfill-20260930 已终局）、`pytest @D:/.../st-zchief9`
- **册内重复条目合并**：`pytest` ×7（L143/149/208/222/227/232/260）→ 1 条；`commit_queue` ×2（L69/252）；`t1_t2_handover` ×3、`factory_grid` ×3（不同 session 限定符可保留带限定符版、删裸条目）；`fillB_window_0925.py`/`fillB_driver.py` 各 ×2
- 净零对齐（宪法 §4）：本次清理预计 218→约 60 条，删 ampersand 155+ 合并重复 12；清理动作须走 keep 册变更流程（带裁定/登记留痕），非本代理执行

---

## §5 ZCode 定时自动化到期表（10 条）

| # | 自动化 | 现状 | 必要性判定 | 到期/自删计划 |
|---|---|---|---|---|
| 1 | lanech-merge 每15分 | active | **无必要**：commit_queue pending=0/processing=0，st-lanech-20261001 已注销（仅剩 .tmp 残片） | 建议立即停并自删；保留至当日收官确认无回流队列 |
| 2 | chief7-巡检 每2h | active | 必要：总包战役进行中（st-fullscore 提交在飞、多车道未收口） | 战役收官（C10 全落地+merge 回主分支）后自删 |
| 3 | backup-第二链 每日 | active 至 10-05 | 必要（过渡期双链） | 10-05 到期自删 ✓（四要素合规范本） |
| 4 | candle_pattern-DROP 2026-12-15 | active 一次性 | 必要（已定 DROP 决议的执行器） | 2026-12-15 触发后自删（须确认注册时带自删） |
| 5 | battle_map-周一巡检 | active | 必要（低频周期巡检） | 长期保留，季度审计复核 |
| 6 | sim-钱包日账 交易日19:30 | active | 必要（业务日账闭环） | 长期保留 |
| 7 | tick-补数 | completed | 已终态，无动作 | 已结束；注意 tick_subscriber 常驻订阅属计划任务体系，与此自动化无关 |
| 8 | 总包接力 | completed | 已终态 | 已结束 |
| 9 | 夜战清滩 | paused | **无必要**：nightsweep 全系会话死净（心跳 pid 文件 116 stale 中 nightsweep 族全灭） | 建议关闭删除 |
| 10 | GPU交接守望 | paused | **状态矛盾**：守望已暂停但 st-c10-t0gpu keeper 循环（PID 3788）仍在跑 | 二选一：恢复守望并接管 keeper，或撤 keeper 后正式关闭；勿留双头 |

---

## 附：核查方法与局限

- 进程快照非瞬时一致（13:07–13:16 多轮扫描）；`last_activity` 活性口径已对照源码 L8 注释与 L519/L581/L805/L886 实现（register/claim 刷新、heartbeat 不刷新）确认。
- 白名单匹配基于当前存活进程 cmdline 全集（含非 Zephyr 进程，如 ollama/QMT），一次性批跑类条目在"运行窗口外"必然 no-match，故 §4 以"未来运行保护"维度二次过滤，避免误删。
- reaper 上轮（13:07:27）killed=1/reported=13/safety_wires breaches=1：reaper 在岗且有处决动作，被杀者身份未在本次核查范围内展开，建议总包结合 §2.2 处置时回查 reaper 日志，避免撤 keeper 时被 reaper 树级联误伤无关进程。
- 本文档新建已尽 CREATE-GUARD 义务提示：如门禁要求 creation_token 登记，由总包会话补登（本代理零写操作约束下不另行登记）。
