---
ttl: task_bound
title: QCure作业簿·fullflow
session: st-qcure-20260925
---
# fullflow 作业簿

## 1 环节定义与边界
"全流通"基线盘点：全模块/全管线/全灌水/全运行。以 ROOR（docs/registry_of_registries.yaml）+
alignment_checklist + functional_domain_registry 为索引，对主要业务块回答四问：真源入口？
守护在跑否（schtasks+.runtime 双证）？最近成功时间？断没断？**只盘点不重启不修复**——
修复全部登记矿脉，施工阶段由总包裁定。取证时点 2026-09-25 01:20-01:30。

## 2 六向台账

### ①上游输入（盘点索引）
- ROOR：docs/registry_of_registries.yaml（tier0 核心源码级 REG-GATE/SCRIPT/PIPE/CAP/DRIFT/SKILL…实读 L26-120）
- 对齐：docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md（宪法 §8 真源，未逐条展开）
- 域册：docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml（按 ROOR 锚定，未全读——归因：本次以运行态为主，域册全读留施工期）
- 调度面：`schtasks /query /fo csv` grep zephyr 全谱 45 项（含禁用 6 项，实证输出见②）

### ②下游消费（三色运行态总表）
| 业务块 | 真源入口 | 守护/计划任务 | 最近成功证据 | 色 |
|--------|----------|---------------|--------------|----|
| 数据集成器/抓数管线 | python -m zephyr.data（src/zephyr/data/cli.py） | ZephyrAlpha_DataScheduler **正在运行**（1:19 起，wscript→start_scheduler.ps1，XML 实证）；IntradayFundFlow 10:05×5、BoardIndexRealtime 9:20、AltFxECB 23:30 | .runtime/fetch_perf/fetch_perf_20260925.jsonl mtime 09-25 01:21 | 绿 |
| secbuild 板块线 | src/zephyr/data/scheduler.py:434（两槽 close_final=T日15:10，st-secbuild-20260923 批2） | IndexMinuteEOD 15:10 + SectorSnapshot 16:40（XML: scripts/data/run_sector_snapshot.py） | logs/index_minute_eod.log 09-24 15:10；SectorSnapshot 今日 16:40 待跑 | 绿 |
| AutoRuntime Core | python -m zephyr.trading（宪法 §7） | **无专属计划任务**；TradingWatchdog 已禁用（lastresult 267011=从未运行） | TickSubscriber 正在运行（1:22 起）供 tick 数 | 黄 |
| 模拟盘/盘后链 | scripts/run_post_settlement.py、start_paper_session_daily.ps1 | PostSettlement 15:30、PaperSession 9:25、SimBridgeExecute 9:35 | PostSettlement 昨 15:30 result=0 + data/runtime/post_settlement_last_run.log 09-24 15:30；PaperSession 昨 9:25 result=0 | 绿 |
| CH/数据库链 | DatabaseService（宪法 §7）；CH 备份双链 | CHHealthProbe **正在运行**；CH-OptimizeMerge-Weekly 09-27 3:30 | logs/ch_health_probe.log 09-25 01:24 活写（388KB）；.runtime/pg_probe_state.json 01:20 | 绿 |
| AI 层 | ai_layer（redline/scheduling/switch_engine…） | **NightlySentiment 已禁用**；PatternMining 9:01、C4Exam 09-26 14:00、FactoryLaneC 09-26 10:00、OllamaServe 就绪 | NightlySentiment 末跑 09-16 result=-2147024894（0x80070002 文件缺失） | **红** |
| 图书馆 | docs/library/INDEX.md + python -m zephyr.library.lookup（宪法 §6.2） | LibraryLedgerBackup 每日 3:30、LibraryLedgerDrill 10-1；library_ledger_backup 在 reaper keep 清单 L149 | 任务就绪+keep 保护（本体 manual，无日跑痕迹——查无更深 mtime，归因：ledger 备份产物在 G 盘） | 绿 |
| GPU/训练矩阵 | run_f06_grid.ps1（F06Grid XML 实证）+ factory_grid_executor | F06Grid 09-26 23:00 就绪；MeasureCalibration 09-26 6:17；ResourceSampler 链 5 任务就绪 | .runtime/logs/grid_t1_20260924.log 09-25 01:22 活写 194KB（c4/wfa 跑批中）；torchrun keep 保护 L27 | 绿 |
| 仪表盘 | src/zephyr/frontend/dashboard/app_panel.py + api_server.py（蓝图头 STARTUP=manual） | **无常驻计划任务**；keep 清单 L3 有 zephyr.frontend.dashboard.api_server（仅防误杀非自动拉起） | 存活证据查无（.runtime 无 dashboard 心跳文件） | 黄 |
| 备份冷储链 | backup.ps1 六阶段（keep L152-153 注记） | DailyBackup 09-25 6:00、WeeklyVMBackup 09-26、IOCheck-Monthly 10-1、ZEPHYR-RESTORE-DRILL 10-1 4:30 | logs/backup_report_20260924_*.json ×4（19:16→23:09 四轮，git_bundle status=skipped/fresh）；F:/zephyr_cold 00_manifest 09-25 00:00、50_archive 00:52；G:/backup working_vault 09-24 12:09 | 绿 |
| 治理/提交链（横切） | git_commit.py→gateway→commit_queue | BeltDaemon/WorktreeDriftWatchdog/ProcessReaper/DeadmanSwitch **均正在运行**；GateFullTreeAudit 3:30、TTLRejudgeDaily 18:05 | .runtime/commit_queue 09-25 01:20 活跳；ttl_rejudge_daily.log 09-24 18:11；session_registry.json 01:21 | 绿 |
| QMT 桥 | QMTWatchdog 8:45（data/runtime/qmt_watchdog.log） | QMTWatchdog 就绪 + SimBridgeExecute 9:35 | qmt_watchdog.log 09-24 12:55（今日未到点） | 黄 |

**三色小结：绿 8 / 黄 3 / 红 1。**

### ③机制现状（+业界参照）
- 调度全景 45 项计划任务：核心常驻 8 项 running（DataScheduler/TickSubscriber/BeltDaemon/CHHealthProbe/ProcessReaper/DeadmanSwitch/WorktreeDriftWatchdog/AI-Wrapper-Inject），禁用 6 项（NightlySentiment/TradingWatchdog×2/WeeklyRest/C4Exam_OneShot、FactoryLaneC_OneShot 等一次性残件）。
- 长跑保护面：data/runtime/process_reaper_keep.txt 176 行，按 cmdline 子串豁免——是"什么应该在跑"的事实清单（F2 矿脉：它与计划任务/守护没有机械对账）。
- 业界参照（凭知识引，未在线复核）：Google SRE Production Readiness Review（上线就绪检查单）：https://sre.google/workbook/production-readiness/ ；SLO/error budget（用"最近成功+断点"量化服务健康）：https://sre.google/sre-book/service-level-objectives/ ；cron 死信监控（任务该跑没跑=告警）：https://healthchecks.io/docs/ 。对照：本项目有 deadman/reaper 但缺"计划任务 last-result 巡检面"（F4）。

### ④代码面
- 数据 CLI：src/zephyr/data/cli.py:342-368 子命令 status/list/run/rerun-failed/pause/resume/start/speed-test=**8 个**（宪法 §7 写"7 子命令"——文档计数漂移，F3）。
- secbuild 两槽：src/zephyr/data/scheduler.py:434（板块状态管道 close_final=T日 15:10 槽）。
- AutoRuntime 入口 python -m zephyr.trading 存在（宪法 §7；process_reaper 子命令同包），但无常驻化设施——TradingWatchdog 禁用后无人替补。
- 调度启动链：ZephyrAlpha_DataScheduler XML= wscript.exe launch_hidden.vbs→start_scheduler.ps1（隐藏窗常驻），非一次性任务。

### ⑤运维/呈现面
- 计划任务即运维面：45 项全靠 schtasks 人工查询；无 last-result 聚合视图（ResourceMorningReport 6:31 任务疑似承载晨报，未展开）。
- reaper keep 清单带案例注记（L152 backup.ps1 误杀史、L156-160 各夜战班 worktree 保护）——运维知识沉淀良好但散在文本。
- .runtime 运行痕迹活跃度：logs/fetch_perf/strategy_pipeline/commit_queue 最近 mtime 均 ≤1h（01:21-01:22），系统整体活跳。

### ⑥失败态与数据面
- 红：NightlySentiment 自 09-16 起 0x80070002（脚本/文件缺失）连败后禁用——AI 情绪夜间管线断。
- 黄史（已愈）：backup.ps1 疑遭 reaper orphan_aged 处决，"09-22 19:13 后零完整轮"（keep L152 注记），09-24 上保护后当晚 4 轮 report——恢复但暴露"断 3 天无人知"。
- 黄：AutoRuntime Core 无守护、仪表盘 manual 无心跳、QMTWatchdog 证据停在 09-24 12:55。
- 数据面：fetch_perf/CH probe/pg probe/grid 四路最近 1h 内均有新鲜写入——灌水面（今日）绿。

## 3 缺陷与矿脉清单
- **F1【红·修复件】** NightlySentiment：定位缺失脚本（0x80070002）修复重编或正式退役登记（禁用≠退役，违反"自动关闭"四要素语义）。
- **F2【对账缺失】** "应该跑什么"（keep 清单+schtasks 45 项）与"实际跑成什么"（lastresult）无机械对账——建议生成器化对账件：schtasks lastresult≠0 或应 running 而非 running → 告警（静态清单禁手工维护铁律 §9.5 同构）。
- **F3【文档计数漂移】** 宪法/文档"7 子命令" vs cli.py 实测 8 个——§4 文档矛盾=事故条款，计数改字段/删除硬编码。
- **F4【巡检面】** DailyBackup/PostSettlement 类任务无 last-result 巡检（backup 断 3 天案）——可挂 DeadmanSwitch 或 ResourceMorningReport 顺带读 schtasks lastresult。
- **F5【卫生件】** grid_t1 日志 pandas FutureWarning（pct_change fill_method 弃用告警刷屏 194KB）——translated/_c4_engine.py:416 一行修。
- **F6【黄块扶正】** AutoRuntime Core 常驻化（或明示"手动启动"语义进宪法 §7）；仪表盘心跳文件（写 .runtime/dashboard/heartbeat.json 供 deadman 读）。

## 4 自审闸三态裁定
挂起排期——本环节交付=本三色基线；红黄修复件（F1/F4/F6）登记矿脉待总包裁定施工窗，本环节自身无独立施工面，亦不可封矿（红块是真实断点）。

## 5 长尾清单
- C4Exam_Full0916/FactoryLaneC_OneShot0915/OneShot 一次性残件任务未退役清理（已禁用， hygiene）。
- RSSHub/OllamaServe/TraeCacheCleanup 状态 N/A"就绪"——触发器语义未核（可能是事件型），留施工期核。
- alignment_checklist+functional_domain_registry 全量对读未做（本簿只按 ROOR 走索引，域册全读留施工期）。
- reaper keep 清单 176 行含历史班次残条（st-*-20260918/20/22 等），可按 TTL 清理。
