---
ttl: task_bound
title: L09-S6 子模块挖矿簿 · 监控自动化（现存清单实证）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L09
status: MINE 完成（六向封口；schtasks 50 项含状态为本册 PowerShell 只读实测，未触发/未新建任何任务）
---

# L09 · S6 监控自动化

**① 职责一句话**：让"哪条链没跑、哪个数不新鲜、哪笔越了界"在**无人询问的情况下自己浮出水面并被处置**——监控是 L09 的免疫系统，不是装饰品。

**② 现状实测（2026-09-26 本机三源对拍：OS 任务态 + APScheduler 槽 + 消费方 grep）**

### 2.1 平面一：Windows 计划任务（实测 50 项 `Zephyr*`，状态逐条取）
| 状态 | 数量 | 成员（实测） |
|---|---|---|
| **Running** | 7 | `BeltDaemon`、`CHHealthProbe`、`DataScheduler`、`DeadmanSwitch`、`TickSubscriber`、`WorktreeDriftWatchdog`、`AI-Wrapper-Inject` |
| **Ready（有下次触发）** | 34 | 交易面 `PaperSession 09:25`/`SimBridgeExecute 09:35`/`BoardIndexRealtime 09:20`/`IntradayFundFlow 10:05`/`C4Exam 14:00`/`IndexMinuteEOD 15:10`/`PostSettlement 15:30(下次 09-28)`/`SectorSnapshot 16:40`/`TTLRejudgeDaily 18:05`/`AltFxECB 23:30`；守卫面 `QMTWatchdog 08:45`/`ConfigCheck 08:05`/`GateFullTreeAudit 03:30`/`ProcessReaper`；**决策链哨兵 `DecisionChainSentinel 09:40`（本册新计入）**；矿/度量面 `PatternMining 09:01`/`MeasureCalibration 06:17`/`EvaporationBlackbox`/`F06Grid 23:00`/`FactoryLaneC 10:00`；资源面 `ResourceMorningReport 06:31`/`ResourceRegenCheck`/`ResourceSamplerScan`/`ResourceSamplerWriteback 05:40`/`ResourceViewPublish 05:50`；备份面 `DailyBackup 06:00`/`WeeklyVMBackup 06:00`/`CH-OptimizeMerge-Weekly 09-27 03:30`/`IOCheck-Monthly 10-01 09:00`/`LibraryLedgerBackup 03:30`/`LibraryLedgerDrill 10-01 04:00`/`RESTORE-DRILL 10-01 04:30` |
| **Ready 但无下次触发** | 3 | `OllamaServe`、`RSSHub`、`TraeCacheCleanup` ⇒ **在册而未排程**（触发器已过期或纯手工），SKEL 未列此类 |
| **Disabled** | 6 | `C4Exam_Full0916`、`C4Exam_OneShot0915`、`FactoryLaneC_Full0916`、`FactoryLaneC_OneShot0915`、`TradingWatchdog`、`WeeklyRest` |

**对 SKEL §S9-6「schtasks 摘要」的两处勘误（本册状态实测推翻记忆口径）**：
1. SKEL 记 `NightlySentiment` 为"禁用（已由 schedule.yaml 08:20 槽接管）"。实测 **状态=Ready，下次运行 2026-09-25 22:30** ⇒ 未被禁用；与 `schedule.yaml:178` 的 08:20 槽**同时在排** ⇒ **TRD-A03 从"待确认双通道"升级为"已实证双通道并存"**（同一情绪窗可能被两条独立时间源各跑一次，ReplacingMergeTree 幂等能挡重复落库，但挡不住双份 LLM 成本与双份 GPU/CPU 争抢）。
2. SKEL 记"C4Exam 与 FactoryLaneC 一次性两件"为禁用。实测 **基件 `C4Exam`/`FactoryLaneC` 均为 Ready 且在排**，禁用的是其 `_Full0916`/`_OneShot0915` 派生件 ⇒ 口径应为"基件在跑 + 一次性派生件已 Disable"。

### 2.2 平面二：APScheduler 槽（实测 `cron:` 计数=**29**，与 SKEL 一致；头注"16 槽"已漂移）
哨兵族实测在产（SKEL 口径经本册复核）：`catchup_guard 05:30`（对账补跑）／`data_supply_sentinel 06:50`（断供 + 托管 quality_sentinel）／`calendar_coverage_check 07:10`（表侧逐交易日 diff）／`integrity_check 23:00`（**只告警不修**）／`daily_backfill 17:00`（补下载）／`dloop_post 16:45`（失败单次 ERROR，`schedule.yaml:249-253`）。
同文件 `:219-227` 自带 R-021 反例注："新开有名无实的槽位=假通道"——本册据此判定 L09-C04 的宿主选择正确（挂独立 schtasks 而非新开空槽）。

### 2.3 告警管线的真实拓扑（本册最关键的结构性发现）
| 环节 | 实码 | 消费方实测 |
|---|---|---|
| 产生 | `Alerter`（`src/zephyr/data/alerter.py:74`）；出口=日志 `logs/integrator.log`（`:32`）+ `failures_dir` 写文件（`:171-172`，**`open(..., "w")` 覆写式**） | `Alerter.read_failure_file`（`:292`）只被自身用 ⇒ 自读自 |
| 聚合 | `src/zephyr/reporting/alert_aggregator.py`（MOD-RPT-030，`[MATURITY] testing`） | **`[CONSUMERS] （候选：总览页"今日告警"卡、运维自治告警流）` = 候选语态；全仓 grep 无任何 import 方（实测零）** |
| 独立小出口 | `decision_chain_sentinel.py:87` `_DEFAULT_ALERT_LOG = .runtime/logs/decision_chain_alert.jsonl` | **零读者**；且本册实测该文件 **不存在** ⇒ 自 09-25 上线以来一次未发（与 S4 册"max() 尺读不出逐日空洞"互为因果） |
| 展示 | 仪表盘 `status_dashboard`/`app_panel` | 只展示业务态，无告警流面板 |

⇒ **本仓监控的真实形态 = "很多探头 + 一条没有终点的告警总线"**。产报侧普遍接电，**汇聚/分发/处置三段全部空转**，其中 `alert_aggregator` 是已经写出来却没人接的那一节——它是本块最高杠杆的单点（接上它即多路复用，不必为每个探头各造读侧）。

### 2.4 「有产报无消费」/「消费无产报」清单（本册主交付）
| 象限 | 条目 | 证据 |
|---|---|---|
| **有产报 · 无消费** | (1) `alert_aggregator` 聚合结果 | 零 import、CONSUMERS 标"候选" |
| | (2) `decision_chain_sentinel` alert jsonl | 文件 ABSENT + 零读者 |
| | (3) `sim_platform_journal` 三健康检（`data_freshness_ok`/`heartbeat_ok` 16/16 满填、`degraded` 位） | 全表零读侧（S4 册实测 8 命中全为写/跑批/测试） |
| | (4) `integrity_check` 23:00 槽 | 自述"只告警"，无处置方 |
| | (5) `calendar_coverage_check` 逐日 diff 清单 | 经 Alerter 出，落入 2.3 的死总线 |
| | (6) THD-TRD-001..004 阈值册条目 | `status: design`、`consumer: "trading 运行时监控（G2b/G5 接线点）"`=未落，见 2.5 |
| **消费无产报** | (1) 仪表盘"今日决策面板" | 消费 `decision_daily`，但**无"当日该有而行不存在"的产报件**（唯一候选哨兵用错尺，见 S4 册） |
| | (2) Owner 的"连绿天数"判读 | 意图存在（人翻台账），**无任何件产出该结论**；且按行数日差算会被周末行虚增（S4 册 G2） |
| | (3) `kill_switch` 的 `severity_action` 要求"交易级 CRITICAL 告警" | 动作侧（REDUCE_ONLY/CANCEL_ALL/DISCONNECT/AUTO_KILL）在 `trading_kill_switch.py` 定义在盘，**告警侧无产报件** ⇒ 熔断执行了也没人知道为什么 |
| | (4) 时序趋势可视化 | 现无 Grafana/Prometheus（判不引，见 ⑤），也无自研时序面 ⇒ "什么时候开始坏的"不可答 |

### 2.5 17 号文 TRD-A06/15 验收线实测（任务书指定的判定点）
> 验收线=四条交易告警**各有消费代码** + **各演练触发一次**。

| 告警 | 阈值真源 | `source_code` 锚（登记册 `:961-1032` 逐条读） | 消费代码 | 演练痕迹 |
|---|---|---|---|---|
| THD-TRD-001 持仓位置超限 | 登记册 v1.6.0 `:961` | `trading_kill_switch.py::KillSwitchLevel.POSITION_LIMIT`（`:74-142` 在 HEAD） | **无** | **无** |
| THD-TRD-002 日亏熔断 -3% AUM | `:979` | `KillSwitchLevel.DAILY_LOSS`（`:93-99`，86400s 不自动恢复=当日终态） | **无** | **无** |
| THD-TRD-003 断路器断连 | `:997` | `KillSwitchLevel.CIRCUIT_BREAKER`（`:100-107`，→DISCONNECT 600s） | **无** | **无** |
| THD-TRD-004 API 超时/心跳丢失 | `:1015` | `KillSwitchLevel.API_TIMEOUT`（`:108-114`，→AUTO_KILL 120s） | **无** | **无** |

⇒ **0/4 有消费代码、0/4 有演练**。登记册自身 `:21-22` 头注已诚实写明"消费面=交易运行时监控（G2b/G5 sim 部署接线点），**status=design 代码未落**"——即**这不是登记册说谎，是消费方一直没人建**；且四条的 `consumer` 字段四条一模一样指向同一个未落地的"trading 运行时监控"，属**一个未建件被四度引用**（L09-C05 的正确靶心=建这一个件，不是建四个）。
另注：阈值真源分裂——登记册 `value` 存的是告警阈值，动作真源在 `trading_kill_switch`（其五级定义），而 `param_origin` 注明限额绝对值=G7 Owner 签字定案项 ⇒ 三处需一致，目前无自动对拍。

### 2.6 宪法 §9.3 偏差登记（**只登记，未自行改**，遵任务书第 4 条）
> `AGENTS.md` §9 第 3 条："永久系统四要素……**reconciler 必须事件触发，禁 cron/Timer/sleep-loop**"。

| 件 | 形态 | 本册裁定 |
|---|---|---|
| `judgment_settler` / `close_verifier` / `warroom_pipeline` 三段 | 事件链钩子 6/7/10 已在（且钩子头注明文自证"宪法 §9.3 合规……不建 cron/Timer/sleep 循环，节拍由调度器 task_completed 唤醒给"，`pipeline_events.py:875-879`），**同时**又被 `dloop_post` 16:45 计划任务二次驱动 | **真偏差候选**：本应事件驱动的 reconciler 由计划任务再推一遍。是否豁免取决于 L09-C01 裁定（若 cron 定位为"补偿/重放"则可论证为第二道而非主驱动）。**不改，移交 L09-C01 必答子问题** |
| `DecisionChainSentinel`（schtasks 日频 09:40） | 时间基 | **不构成 §9.3 偏差**：检测对象是**事件的缺席**，缺席无法用事件唤醒（同 `data_supply_sentinel`/`catchup_guard` 先例）。登记为"已论证豁免"，防后续车道误当整改项 |
| `NightlySentiment` schtasks + APScheduler 槽双在排 | 双时间源 | 非 §9.3 问题（本就是数据批），属 **TRD-A03 双通道重复触发**问题，本册已升级为"实证并存" |
| `integrity_check 23:00`（只告警） | cron 驱动修复缺位 | 符合"只告警"设计意图，不判偏差；但"告警后无人处置"属 2.4 象限问题 |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：29 APScheduler 槽 + 50 schtasks 任务 + `fetch_perf` 心跳 + 表侧 `max(date)`/日历 diff/7 天节奏闸（quality_sentinel）+ THD-HEALTH-001..004（`health_monitor` MOD-INF-035 阈值真源 fail-closed）。外部：已查无（OS 级任务清单属环境事实，无方法论） |
| ②下游 | 内部：Owner（告警通道，见 2.3 的总线断点）；`quality_assurance_selfdrive`/`agentic_drift_guard`/`autonomy_boundary_gate` 各自写自己的 alerts jsonl（实测 3 处独立告警文件出口，互不汇聚）。外部：SRE "告警→工单→处置"闭环为行业标准体裁 |
| ③算法 | 内部：停更检测/档期对账/达标告警=**症状告警**；缺 burn-rate/多窗思想。外部：Google SRE Workbook Ch.5 "Alerting on SLOs"（sre.google/workbook/alerting-on-slos/，免费全文，发布方 Google，2018 起持续维护）＝症状优先于成因 + 多窗口 burn-rate + **"监控监控本身"**；SKEL §5.2 已对表一次，本册补其**第三条的直接命中**："监控监控本身"正是 2.3 死总线与 S1 册 G1 的标准命名 |
| ④后端 | 内部：①告警出口至少 4 类（Alerter 日志/failures 文件、sentinel jsonl、drift_guard jsonl、autonomy_gate jsonl）**无统一 schema**；②`Alerter` 的 failures 文件是 `"w"` 覆写 ⇒ 历史丢失、不可做"连续 N 日"类判据（这正是 TRD-A01 需要累积而 sentinel 只能自造 jsonl 的根因）；③无 alert 去重/静默期/升级机制 ⇒ 任何"持续型"故障每天重报或永远不报，取决于探头写法 |
| ⑤前端 | 内部：无 Grafana/Prometheus；`status_dashboard`/`app_panel` 自研，无告警面板。外部：Prometheus **Apache-2.0** / Alertmanager 同族 / Grafana **AGPLv3**（2021-04 起），单机自用合规——SKEL §5.2 已判"现规模引入违反净零内收"，本册维持并加一条：**真正缺的不是面板，是统一告警 schema 与消费端**（`alert_aggregator` 已在仓内，先接它才是净零解） |
| ⑥数据字段 | 内部：`fetch_perf` 心跳列（SUCCESS/BLOCKED/PARTIAL）＋ `sim_platform_journal` 三健康位 ＋ `decision_daily` 存在性。**"字段在"≠"数据可得"本块落点**：`degraded`/`heartbeat_ok` 列存在且 16/16 满填，但**无人读=对决策不可得**；反之 `integrity_check` 每天产报却因覆写式文件而**拿不到历史**=想算"连续"而不可得 |

**④ 缺口清单**

| 编号 | 内容 | 状态 |
|---|---|---|
| TRD-A06 / L09-C05 | THD-TRD-001..004 消费面 | 在册；**本册改写靶心**：四条共用一个未建件（"trading 运行时监控"），建一个即四同时销，且须含**演练四连**（验收线后半，当前 0/4） |
| TRD-A01 / L09-C04 | 决策链哨兵 | **已落地（S1 册勘误）**，本册供其尺子缺陷证据（S4 册）与双通道风险 |
| TRD-A03 | NightlySentiment 双通道 | **本册升级为"实证并存"**（状态 Ready + 08:20 槽同在） |
| TRD-A07 | 盘中持仓风控环无 runner | 在册（本册不重复论证） |
| L09-S6-G1（新·本册主项） | **告警总线断点**：`alert_aggregator`（MOD-RPT-030，件已存在、testing）全仓零 import ⇒ 所有探头的出口最终无人汇聚/分发/处置 | 新增·P0 |
| L09-S6-G2（新） | **告警出口至少 4 类且无统一 schema**（Alerter failures / sentinel jsonl / drift_guard jsonl / autonomy_gate jsonl）⇒ 不可能做跨源关联与"连续 N 日"判据 | 新增·P1 |
| L09-S6-G3（新） | `Alerter` failures 文件 `"w"` 覆写 ⇒ 告警史不可回溯 | 新增·P1（与 G2 同批） |
| L09-S6-G4（新） | 在册未排程件 3 个（OllamaServe/RSSHub/TraeCacheCleanup）+ Disabled 遗留 6 个 ⇒ **无"任务台账"机读面**，谁在跑只能每次现查 50 条（本册即为此花了 3 次调用） | 新增·P2 |
| L09-S6-G5（新） | 阈值真源三处（登记册 `value` / `trading_kill_switch` 定义 / G7 Owner 定案）无自动对拍 | 新增·P2 |
| L09-S6-G6（新） | "监控监控本身"缺位：哨兵/调度器自身挂了无人知（=S1 册 G1，两册同源不重复立项） | 新增 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由 / 解锁条件 |
|---|---|---|
| L09-S6-G1 接上 alert_aggregator | **施工（P0，本块最高杠杆）** | 件已存在=零新增规则/零新脚本，纯接线，净零内收满配；不接则本块任何新哨兵都只是往死总线里再插一根。终局全貌下 Owner 一人不可能是 50 个任务 × N 个探头的人工读者 |
| L09-S6-G2/G3 统一 schema + 追加式落盘 | 施工（P1，与 G1 同批） | schema 不定，G1 接完仍是四个孤岛；`"w"→"a"` 改动小但属行为变更 ⇒ 需 own-scope 测试保护。**不可逆点=历史 failures 文件形状**，故 schema 一次定清 |
| L09-S6-G4 任务台账机读件 | **施工（P2）** | 直接命中宪法 §9.5"凡条目列表+计数的清单必须生成器产出，手工维护必然漂移"——SKEL §S9-6 的 schtasks 摘要本身就是一次手工漂移实例（本册两处勘误）。处方=生成器读 `schtasks` + `schedule.yaml` 产机读台账，L09 文档只引不抄 |
| L09-S6-G5 阈值三源对拍 | 挂起排期 | 解锁=G7 仓位参数 Owner 定案落地（值未定案时无法判"漂移"） |
| L09-S6-G6 | 并入 L09-S1-G1 处置（不另立） | 同根 |
| Grafana/Prometheus 全家桶 | **封矿（技术选型层）** | 理由=单机 + 现 29 槽规模，引入五件全家桶违反净零（SKEL §5.2 结论维持）；**但严格限定封的是"引入监控栈"，不封"监控消费面"**——后者由 G1 承接，不许借本条把消费缺口一起封掉 |
| TRD-A06 演练 | 施工（P1，随 L09-C05） | 17 号文验收线明写"各演练触发一次"，0/4 ⇒ 未做不等于会做；演练件须可重复（否则每次验收都要人再手操一遍=违反四要素之"自动运行"） |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 归因 |
|---|---|---|---|
| R1 | `schtasks` CSV 全量 + `Get-ScheduledTask.State` 状态列（只读，未触发未新建） | signal | 50 项四态分布；**两处 SKEL 勘误**（NightlySentiment 非禁用、C4Exam/FactoryLaneC 基件在排） |
| R2 | `schedule.yaml` `cron:` 计数 + 哨兵族槽位逐条 | signal | 29 槽与 SKEL 双验一致；R-021"假通道"先例为 L09-C04 宿主选择提供依据 |
| R3 | 全仓 grep `alert_aggregator` / Alerter sink 读者 | signal | **本册主发现**：件在、testing、零 import ⇒ 死总线 |
| R4 | `alert_threshold_registry.yaml:20-22` + `:961-1032` 四条逐字段读 | signal | `status=design` 自认；四条 `consumer` 同指一个未建件 ⇒ L09-C05 靶心改写 |
| R5 | `decision_chain_alert.jsonl` 存在性 | signal | ABSENT=上线以来零触发，与 S4 册 max() 尺缺陷闭合互证 |
| R6 | 外部对表 | **部分** | 已就位=SRE Workbook Ch.5（发布方 Google，长期维护，"alert on symptoms / 多窗 burn-rate / 监控监控本身"三判据直接命中 G6/G1）；Prometheus Apache-2.0、Grafana AGPLv3(2021-04) 沿用 SKEL §5.2 已核结论。**未做本轮独立二次核验**，延至统一轮 |

**本册封矿判据**：六向封口；现存清单以状态级实测取代记忆；四象限"产报/消费"清单成表；TRD-A06 验收线给出 0/4 + 0/4 的硬数；§9.3 偏差两条如实登记且未施工。⇒ **子模块封矿**。
