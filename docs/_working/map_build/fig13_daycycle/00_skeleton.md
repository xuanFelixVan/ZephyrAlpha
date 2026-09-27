---
ttl: task_bound
completes_when: 六图战役封矿并全部落地四件套后本件退役为归档参考；在此之前若三扫之③（消费者文献路）跑完且增量归零，本件转"待施工"
title: 图13 交易日循环图 trading_day_cycle_map·环节总骨架（撞车判定优先）
owner: st-mapbuild-20260924（图13 骨架主）
---

# 图13 交易日循环图·环节总骨架

> 会话=st-mapbuild-20260924 图13 车道｜2026-09-24｜只读研究+文档，不改 `config/`、不提交。
> 方法论指针（不复制）：`sop/mining_sop/skeleton_mining_policy.md` §1/§3/§4/§5/§6；
> `sop/trading_decision_map_sop/trading_decision_map_layering_policy.md` §1 三反模式+§2.1 定位声明+Step 1；
> 裁定 409 一域一图四道门第③门；`config/trading_decision_map.yaml:4-13` INV-1 铁律。
> 本图的路由表价值不在环节多，在 §0 那份撞车判定——判定错，后面 44 格全是第二真源。

## §0 撞车判定

### 0.1 已有资产盘点（Step 1，任务书点名 4 处 + 实测新增 2 处更强撞车面）

| # | 撞车候选 | 实查（文件:行） | 它实际画的轴 | 与本图的连接点差异 | 处置 |
|---|---|---|---|---|---|
| 1 | `src/zephyr/data/config/schedule.yaml` | 全档读；实测 `schedules:` **29 槽**（普查说 27）；**17 槽有 tasks.yaml 挂载 / 12 槽零任务**（`dloop_post`/`eod_reconciliation`/`sector_pre_open`/`sector_close_final`/`post_auction`/`nightly_sentiment`/`catchup_guard`/`data_supply_sentinel`/`calendar_coverage_check`/`consensus_crosscheck`/`daily_backfill`/`integrity_check`）；日历守卫仅覆盖 9/29（`trading_calendar.py:151-163`） | 数据管线的机生时刻表（谁几点跑、哪个执行器池） | 它没有：槽的**前置**（数据就绪门）、**因果序**（verify 恒先于 settle）、**缺席兜底**（三路补跑分工只写在 L143-147/159-167/215-227 散文注释里）、**日历语义**（其余 20 槽非交易日空跑靠底层幂等吸收，无图可查）。它答"配了什么"，不答"这一天怎样过完、谁没跑谁接" | **引用**（节点存 `slot_ref`，禁抄 cron） |
| 2 | dloop 链 `MOD-PLAN-033` | `src/zephyr/plan_engine/daily_loop_master_switch.py` 全档。**普查"十环节"实测=docstring 叙述 11 棒（L24-29）／`full` 相 16 段（L337-368 PHASE_STAGES，dispatch L402-419 同 16）**；四相 premarket 5 / intraday 4 / postmarket 8 / full 16；L246 起为 Owner 2026-09-21 扩面新段 | 进程内编排链：唤醒词驱动（`_WAKE_DAILY="daily_kline"` L69、`_WAKE_60MIN` L68）、逐段 fail-open、唯二 fail-closed（数据就绪门+输入校验）、幂等全委托底层、零下单（裁定 305 安全态 L44-45） | 它是**一条被排班的链**，不是排班表。其 L8 `[INVARIANTS]` 与 L335 注释自证归属本图（"段序契约要求唤醒词过滤通过""postmarket 内 verify 恒先于 settle"）；而每段"判什么"一句不涉及 | **融合**（序与闸进本图 D13-32；各段决策语义引用 TDM） |
| 3 | `config/trading_decision_map.yaml`（TDM） | 头 L1-19（INV-1/D108 拆分三条件）；实测 `nodes:` **182**；`activation`=continuous 40/premarket 46/intraday 43/postmarket 51/on_demand 2；`point` 值域仅 4 值（持续/盘中/盘前/盘后）；全节点正则扫 `cron|schedule.yaml|排程|槽位|排班|调度|schtasks` → 仅 4 命中（TDM-P-P2/-01/-02、TDM-F-C3-03，且都是决策语义词非时刻） | 决策树：遇什么情况→怎么判→做什么，挂 STR-*/FCT-*/DS-*/IND-*/EXA-*/MOD-* | `activation` 是**时效窗标签不是时点**：46 个 premarket 节点共享一个词，彼此无先后、无就绪门、无缺席后果。TDM 的边="谁的输出进谁的判据"，本图的边="谁必须先于谁" | **引用**（决策内容全走 `tdm_ref`） |
| 4 | battle_map（`battle_map_steps` PG 三表） | `src/zephyr/governance/persistence/battlemap_schema.py:93-108` flow_stage **11 值**（research_incubation→model_training→backtest_validation→simulation_validation→stock_selection→buy_flow→sell_flow→position_management→risk_control→execution→reconciliation）；字段表 L162-174 **无 time/cron/slot 列**；全库正则清点 **349 个 BM-* 标识**/12 族（SEL 104/BT 53/RC 50/RES 34/REC 18/BUY 24/SELL 14/MT 14/POS 10/SIM 8/EXE 6/PLAN 4）；`battle_map_coverage_ruling_20260915.md:46` 实证 `BM-REC-01 运营清算 ← MOD-OBS-001` | 业务生命周期装配轴（每环节落在哪些模块/候选/蓝图） | 它**有** `reconciliation` stage 与 BM-REC-01..05 → 盘后结算的装配落点已被它覆盖；它**没有**时间：11 个 stage 无一时钟语义，`sort_order` 只给族内序，跨族无日序。要画"15:30→15:40→16:30→16:45"只能新增第 12 个 flow_stage=`day_cycle` = 时钟轴污染生命周期轴，破坏 L162-164 CHECK 受控词表与 BM-INV-006 父子一致性 | **扩展**（不改轴；在 BM-REC-01/BM-EXE-* 以 `source_ref` 反挂 D13 编号） |
| 5 | **排班三表一入口**（任务书未点名，最强撞车面）：`config/resource_profile_registry.yaml` + `scripts/ops/schedule_overview.py` + `zephyr.governance.audit.schedule_consistency_reconciler` | registry 实测 **81 实体**（字段 `total_entities: 81`，而 reconciler docstring L31 写"86 实体"→**在册文档自漂 5**）；`window_type`=cron 36/manual 29/event 15/dynamic 1；`schedule_truth_source` 指 schedule.yaml 者 24 条，余指 `register_*.ps1`；**实测已含交易运营时点**：`sch_paper_session 25 9 * * *`、`sch_post_settlement 30 15 * * 1-5`、`sch_intraday_fund_flow`、`sch_index_minute_eod`、`sch_trading_watchdog`、`ops_qmt_watchdog`（但 window_type=manual / window_expr=**None**，真触发 08:45+12:55 未被抽到=**该视图自身漏拍**）；`schedule_overview.py:33-46` ALGO_FLOW 三段=A1 周历视图（槽位×任务，expand_windows 展开本周触发时刻表）/A2 资源档位/A3 三表一致性 | 算力资源画像与冲突（谁和谁同窗打架、内存超不超 10GB 天花板、E0 交易窗能否开工） | 它确实是跨三种触发机制的时刻清单——**本判定最痛的一刀**：时刻值真源在它和 schedule.yaml 手里，本图一个不许抄。它不管：时刻之上的**日序因果**（它做区间求交，不做"谁必须等谁"）、**就绪门**（数据缺则 SKIP 还是空跑它无此概念）、**缺席后果**（谁兜底、接不住算什么）、**段界**（盘前/盘中/盘后/夜窗是运营切分非资源切分）；`trading_sensitive` 只是 bool 闸标记无时刻归属 | **引用 + 分工契约**（本图新增职责="时序与就绪"，明确放弃"时刻值与资源档位"） |
| 6 | **`docs/_archive/57_daily_cycle_sop.md`**（交易日模拟盘+收盘后回测 日循环 SOP，已归档，任务书未点名） | §0 L22-31 六环节时点表（09:15 前/09:30-15:00/15:30 后/16:30 后/随后/当日）；§1 L35-48 三条只读命令 + C1/C2/C3 判据；§7 L103-111 GAP 族；卷首 L5 归档注记（2026-08-30 候选核销批"内容全量施工完毕核销"）、L7 `completes_when=…转 maintenance（流程图并入 55 号监控体系）` | 人照做的运行手册（六步+命令+责任人） | **离本图最近的既存件，也是它已死去的证据**：六环节只覆盖 44 格中 6 格；归档后无接替件（"并入 55 号监控体系"所承诺的图实测仓内不存在）；其 GAP-2/GAP-3 现已闭环（paper session 已挂 09:25 计划任务、post settlement 已挂 15:30）而文档已死 → **现役接线无图可查**，正是骨架 SOP §2.1 的"状态盲区"罪 | **吸收后废弃引用**（动作语义入 D13-07/09/12/24/28/31，命令与判据以 `doc_ref` 指归档件不复制；归档件不复活） |

### 0.2 判定结论：**① 新图成立**，但为**窄域①**（三条硬让渡）

**为何不是②（改挂不另造）**——两条扩节点路被实证否掉：

- 往 TDM 扩：节点规范 v1.5 必填 `decision_question`/`judgment_basis`/`strategy_refs`/`action`。`ZephyrAlpha_QMTWatchdog` 08:45 无决策问题可填、无因子/策略可挂、`activation=premarket` 但无判据 → 造第 183 类畸形节点；且 §2.1 自陈 TDM 管"动作流程的唯一真源"，看门狗与补跑兜底不是动作流程而是**运营时序**。TDM 用 `activation` 已**只切窗不切点**（46 个 premarket 节点共享一标签），扩成时点轴=改轴不改图。
- 往 battle_map 扩：唯一形态是新增第 12 个 flow_stage（见 §0.1 第 4 行），违反"扩节点不污染原轴"。
- 往排班三表扩：其字段设计有"双证纪律"（`resource_schedule_panorama_plan_v1.md` §2.1"每字段必须生产者+消费者双证，无双证不入表"），而"前置条件/缺席后果"的唯一消费者就是本图——先有本图才可能有该字段，鸡生蛋；其"图"=周历视图，答争抢不答日序。

**为何不是③（只建缺的那段）**——四段**都缺同一样东西**：没有任何一处把三种互不可见的触发机制（APScheduler 29 槽 / Windows 22 个 `register_*.ps1` / 进程内唤醒词 16 段）串成一条带前置与兜底的日序链。缺的不是某一段，是**那条脊**。

**三条硬让渡（须写进图本体 `laws`/`boundary`）**：
1. **时刻值不搬家**：节点存 `slot_ref`（schedule.yaml 槽名）/ `entity_ref`（registry task_id）/ `schtasks_ref`（tn 名），cron 字面量零复制。
2. **决策内容不进图**：任何"怎么判"唯一出路是 `tdm_ref: TDM-*`；本图节点**不得有** `judgment_basis`/`factor_refs`/`strategy_refs` 字段。
3. **管线内部结构不重画**：17 个有任务挂载的数据槽在本图只作"批次节点"（含计数与当日就绪判定），其源→库→衍生→冷备→对账内部结构归图12；对账/归因的装配落点归 battle_map BM-REC-*。

**退路（诚实备案）**：若 Owner 否决"同资产不同轴"适用于本图与排班三表之间（普查 §2.3 已为图12↔dataflowgraph 认过一次同判据），则本判定改 **②**：§2 的 44 环节降为 `schedule_overview.py` 新段 A4"日序视图"，图13 作废。扩节点清单=①`schedule_overview.py` 加 `--section daycycle`；②`resource_profile_registry.yaml` 加 `ready_gate`/`fallback_slot`/`miss_consequence` 三字段（先过双证评估）；③`align_all.py` 不新增节。

**§0 判定的唯一失效条件**：若禁则一（决策内容不进图）被违反，本图立刻退化成"第二份动作流程真源"，撞 layering policy §2.1 合并铁律，届时①应改判②。

**普查数字纠偏（四处实测不符，落地须改普查）**：

| 普查说法 | 实测 | 证据 |
|---|---|---|
| schedule.yaml 27 cron 槽 | **29 槽** | `yaml.safe_load(...)['schedules']` len=29（§7 A-1） |
| dloop 十环节 | **16 段（full）/ 11 棒（docstring）** | `daily_loop_master_switch.py:337-368` vs `:24-29`（§7 B-1） |
| 盘中 SimBridge 09:35 | **全仓无 SimBridge 实体**；`09:35` 仅出现在 `src/zephyr/backtest/core/tick_replay.py:24,80,342`（回测开盘 5 分钟窗口过滤，非排班）。盘中真实常驻=`ZephyrAlpha_PaperSession` 09:25 起、保活至 15:05 | 正则零业务命中；`paper_session.log:144` |
| 资金流 4 槽 10:05-15:05 | **5 槽 10:05/11:05/13:35/14:35/15:05** | `register_counter_trend_feeder_tasks.ps1:11-13,80` + CH `sector_fund_flow` 3,705 行 max=2026-09-24 |

## §1 域定义与四道门实证

**域职责一句话**：一个交易日从夜窗闭合到次日交接，**什么时点必须发生什么、谁给它让路、它没跑谁接、接不住当日算什么状态**。

| 门 | 判据 | 实证 |
|---|---|---|
| ①有真源可机生 | 字段须可由脚本抽出，禁手画 | 槽名/executor/29 槽←schedule.yaml；17 槽任务数←tasks.yaml `schedule:` join（实测 271 任务/23 源）；ps1 触发时刻←`New-ScheduledTaskTrigger`；dloop 16 段序←直接 import `PHASE_STAGES`；`window_expr`/`trading_sensitive`←resource_profile_registry。四源全可抽，**仅需人填 2 字段：`段归属`、`ready_gate`** |
| ②有消费者 | 建了谁读 | (a) 断供根因定位——股东户数断供两月案（skeleton policy §2.2）与 `data_supply_sentinel` 注释自证的盲区（schedule.yaml:215-217）；(b) 三路兜底分工目前只在散文里（L159-167）不可查；(c) Owner 每日拍板核对；(d) 图12 施工令的下游就绪假设；(e) `TRADING_DAY_GUARDED_SCHEDULES` 只覆盖 9/29 槽这一空洞的显性化 |
| ③不被现有图覆盖（存量优先扩节点） | §0 全文 | 六处实查；两条扩节点路被否；三条硬让渡写死；退路②已备清单 |
| ④缺口可显性化 | 空值须有语义 | `module_ref` 空=红节点（TDM 同款）；`ready_gate` 空=无前置（须声明理由）；`miss_fallback` 空=无兜底=日终风险点；`last_run_evidence` 空=**不得标 ✅**（本图独加字段，把"断供"从散文变成可数的机制） |

**边界（明确不做）**：下单/撤单执行流（TDM L4/X-S2）｜因子与策略（各库）｜数据管线内部（图12）｜资源争抢与内存天花板（排班三表）｜治理夜班（C4Exam/ModelExam/GateFullTreeAudit ~28 schtasks → GOMAP 扩排程层，普查 §5 已有归属）｜开发时会话生命周期（图11）｜24/7 三班制交接（`shift_handover_checklist` 现役件，对象是连续市场）。

## §2 环节全集（44 环节，骨架层=中类，叶层留作业簿）

编号 `D13-NN` 一经定稿即契约，作业簿文件名必须引用它。
**状态纪律**：`✅`=时点存在性+执行体存在性+最近执行证据三证齐（本文件实查、§7 可复跑）；`🔨`=有执行体但最近执行证据未取到/滞后/断供；`⬜`=空白可开入口；`🌑`=当前形态不可得（不占环节格，全部集中在 §6 点名）。

### 段 A 盘前 05:30–09:30（12 环节）

| 环节编号 | 环节名 | 段 | 时点(槽位) | 状态 | 真源映射 | 子环节数 |
|---|---|---|---|---|---|---|
| D13-01 | 调度对账补跑（错过档期自愈） | 盘前 | 05:30 全周 `catchup_guard` | 🔨 | schedule.yaml:168-171；`src/zephyr/data/catchup_guard.py:6`（"不进 TRADING_DAY_GUARDED"自证） | 4 |
| D13-02 | 数据断供哨兵（含托管质量变异巡检） | 盘前 | 06:50 全周 `data_supply_sentinel` | 🔨 | schedule.yaml:228-231；`config/data_supply_sentinel.yaml`；`config/quality_sentinel_tables.yaml` wiring 块；总闸 `data/runtime/quality_sentinel.disabled` 实测**不存在**=开着 | 3 |
| D13-03 | 交易日历逐日覆盖 diff | 盘前 | 07:10 全周 `calendar_coverage_check` | 🔨 | schedule.yaml:237-240；`zephyr.data.calendar_coverage_checker`；立论=补 max(date) 原理性失明（L234-236 注释自证 tick 内部洞/stock_basic 缺日型） | 1 |
| D13-04 | 夜间情绪窗结算（窗口 [T-1 18:00, T 08:00)） | 盘前 | 08:20 全周 `nightly_sentiment` | ✅ | schedule.yaml:178-181；CH `c1_market.news_sentiment_window` max(window_ts)=2026-09-23 18:00、全表 19,820 行（§7 C） | 2 |
| D13-05 | 币圈日线（UTC 日界→北京 08:41） | 盘前 | 08:41 全周 `daily_crypto` | 🔨 | schedule.yaml:75-78（executor light→default 幽灵池治本留痕 L77：该任务上线后从未自动跑成，水位全靠手动） | 1 |
| D13-06 | L0.5 盘前元数据（universe 与撮合约束前提） | 盘前 | 08:34 交易日 `pre_market`（JOB-077） | 🔨 | schedule.yaml:24-31；五子源实测：`stock_basic` 09-23/9,036,265 ✅、`stk_limit` 09-23/9,215,395 ✅、`limit_up_pool` 09-23/1,088 ✅、**`suspend` 0 行 max=1970-01-01 空洞**（§7 C）→ 停复牌子源断链，整槽不得 ✅ | 5 |
| D13-07 | QMT 终端看门狗 | 盘前 | 08:45 与 12:55（tn=`ZephyrAlpha_QMTWatchdog`） | ✅ | `scripts/qmt_watchdog.ps1:28`；留痕 `data/runtime/qmt_watchdog.log` 末六行=09-22 08:45/12:55、09-23 08:45/12:55、09-24 08:45(pid=47540)/12:55(pid=22860) 全 `OK process running` | 2 |
| D13-08 | 十源健康探针（57 号 C3 腿） | 盘前 | 每日一份日志（触发者待定位） | ✅ | 留痕 `logs/source_health_20260916…20260924.log` 连续每日；执行体 `zephyr.data.source_health_check`，被 `src/zephyr/data/scheduler.py:1696,1709` 消费 | 3 |
| D13-09 | 开盘前就绪门编排（C1 人工 QMT + C2 关键任务 + C3 → 当日 SKIP 判定） | 盘前 | 09:15 前 | ⬜ | 唯一真源=**已归档** `57_daily_cycle_sop.md:24,35-48`；在位合成件零（C2 靠人读 `python -m zephyr.data status`，三判据无合成器） | 3 |
| D13-10 | 板块状态盘前复制（close_final→pre_open + 偏好重映射） | 盘前 | 09:15 交易日 `sector_pre_open` | 🔨 | schedule.yaml:263-267；CH `sector_state` **stage='pre_open' max(trade_date)=09-23、469 行/日 → 当日（09-24 09:15）未产，滞后 1 交易日**（该槽 2026-09-23 才新增 L255-257；同文件 L126-128 在册先例"不热载，调度器重启后生效"） | 2 |
| D13-11 | 集合竞价高频五档采集（9:15-9:25 每 10 秒） | 盘前 | `auction_highfreq`（6 段 cron 含秒） | ✅ | schedule.yaml:183-192（3 秒→10 秒 coalesce 实证 L184-186）；CH `auction_snapshot` 09-24/283,623 行、`auction_book` 09-24/3,816,492 行 | 2 |
| D13-12 | 模拟盘会话拉起 + 交易日历闸 | 盘前 | 09:25（tn=`ZephyrAlpha_PaperSession`，`--if-trading-day`） | ✅ | `scripts/register_paper_session_task.ps1:67,40-47`（Daily 09:25，NOT AtLogOn）；`scripts/start_paper_session_daily.ps1`；留痕 `.runtime/logs/paper_session.log:146` 09-24 09:25:03 起、`:3` 09-19 09:25:03 `SKIP (is_trading_day=False)`、`:1-2` 09-17/09-18 SKIP（QMT 未开） | 4 |

### 段 B 盘中 09:30–15:00（12 环节）

| 环节编号 | 环节名 | 段 | 时点(槽位) | 状态 | 真源映射 | 子环节数 |
|---|---|---|---|---|---|---|
| D13-13 | 竞价后档位一次性聚合（情绪指数 auction 档） | 盘中 | 09:30 交易日 `post_auction` | 🔨 | schedule.yaml:34-37（2026-09-23 新增；executor light→default 同日机械代修留痕=两起同因事故 POOL-BLOCK 指正 + 仪表盘 undeclared_executor standing alert） | 1 |
| D13-14 | 盘中实时层（Tick/L2/Greeks/IV/期货/涨跌停/港股K） | 盘中 | 每 5 分钟 `intraday_realtime` | 🔨 | schedule.yaml:39-42（realtime 池）；实测挂 16 任务，本图不计叶 | 1 |
| D13-15 | 盘中分钟K线滚动层 | 盘中 | 每 5 分钟 `intraday_minute` | 🔨 | schedule.yaml:45-48；实测 16 任务 | 1 |
| D13-16 | 盘中板块分钟K线层（mootdx 直连独立池） | 盘中 | 每 5 分钟 `intraday_sector` | 🔨 | schedule.yaml:50-55（独立执行器避开 miniqmt 全市场 ~5000 股慢任务） | 1 |
| D13-17 | 事件驱动快新闻 + EDB 轮询 | 盘中(7×24) | 每 3 分钟 `event_driven` | 🔨 | schedule.yaml:57-64（*/5→*/3 提速理由=一轮~2min 留 1min 余量；一任务只属一槽的精确字符串匹配约束 L59-60） | 2 |
| D13-18 | 慢新闻/研报独立队列（限流分池） | 盘中(7×24) | 17,47 分 `news_slow` | 🔨 | schedule.yaml:66-72（akshare 单例 60 次/分共享额度，并行总时间与串行相同的实证 L67-68） | 2 |
| D13-19 | 板块资金流日内五快照（下跌段差分需段内≥1 快照） | 盘中 | 10:05/11:05/13:35/14:35/15:05（tn=`ZephyrAlpha_IntradayFundFlow`） | ✅ | `scripts/register_counter_trend_feeder_tasks.ps1:11-13,80`；CH `sector_fund_flow` 全表 3,705 行 max=09-24；留痕 `logs/fundflow_collect.log` 末两条=`采集 90 个行业 @ 2026-09-24 10:05:16` / `@ 11:05:15`，落库各 90 行 | 2 |
| D13-20 | 竞价命中判定（日内唯一带墙钟窗闸的段） | 盘中 | 10:00-10:30 Asia/Shanghai（代码内窗闸，非排班槽） | 🔨 | `daily_loop_master_switch.py:73`（`_AUCTION_WINDOW`）+`:294-313`（窗外=skipped）——**实证设计缺口**：本段只被 16:45 的 dloop 圈或人工逃生口调用，16:45 恒在窗外→自动圈下永远 skipped（待作业簿 04 复核盘中另有调用方否） | 1 |
| D13-21 | 盘中 L1 市场状态跟踪 | 盘中 | 60 分钟K唤醒词驱动 `intraday_l1` | ✅ | `daily_loop_master_switch.py:211-215`（`_WAKE_60MIN="kline_etf_60min"` L68）；CH `judgment_intraday_market_state` 按 `toDate(asof_ts,'Asia/Shanghai')` 实测 09-24=2 行（当日在产）、09-18~09-23 每日 4 行 | 1 |
| D13-22 | 盘中情景归类 | 盘中 | 同上 `classify` | 🔨 | `daily_loop_master_switch.py:218-222` → `scenario_classifier.maybe_classify_intraday_scenario` | 1 |
| D13-23 | 盘中情绪环单拍（有节拍席位、无节拍） | 盘中 | dloop 段内，非独立排班 | 🔨 | `daily_loop_master_switch.py:274-291`（docstring 自陈"单拍就绪没节拍——本段=节拍席位"）→ `zephyr.data.intraday_sentiment_loop.run_once` | 1 |
| D13-24 | 模拟盘保活与成交回路（09:30–15:05） | 盘中 | 常驻（tn=PaperSession 拉起，close_at 15:05） | ✅ | `src/zephyr/ex_core/live_strategy_adapter.py`（MOD-L06-001，`[CONSUMERS]` 自证 57 号 GAP-2 接线已落、挂计划任务=Owner 窗口已兑现）；留痕 `paper_session.log:144`"保活至 2026-09-23T15:05:00+08:00"、`:145` exit_code=0、`:141-143` slot started/`slots_running=1` | 4 |

### 段 C 盘后 15:00–20:00（11 环节）

| 环节编号 | 环节名 | 段 | 时点(槽位) | 状态 | 真源映射 | 子环节数 |
|---|---|---|---|---|---|---|
| D13-25 | 板块状态盘后定格（真源态） | 盘后 | 15:10 交易日 `sector_close_final` | 🔨 | schedule.yaml:255-262；CH `sector_state` **stage='close_final' max(trade_date)=09-22、>=09-20 窗内 938 行（=2 个交易日×469）→ 缺 09-23**，比 D13-10 再滞后一日；总闸 `data/runtime/sector_state_pipeline.disabled` 实测不存在 | 1 |
| D13-26 | 指数分钟K日终补拉（峰谷下跌段探测器供料） | 盘后 | 15:10（tn=`ZephyrAlpha_IndexMinuteEOD`） | ✅ | `register_counter_trend_feeder_tasks.ps1:14-15,86`；留痕 `logs/index_minute_eod.log` 末次="拉取 48 根分钟 K(20260923, 源=sina_5m) 落库成功 → c1_market.index_quote(akshare_sina_5m)"，上一行=em_1m 源失败降级记录 | 1 |
| D13-27 | 盘中持仓对账事件入口（与 D13-29 分工） | 盘后(事件侧) | 无槽，position 事件驱动 | 🔨 | schedule.yaml:204-208 注释（全流通战役 R-015 排班真源："盘中持仓对账走 position 事件入口；本槽位是定时事实核对，非自愈 reconciler 环路，宪法 §9.3 约束的是自愈环"）→ `zephyr.ex_core.position_reconciler.handle_execution_report` | 2 |
| D13-28 | 盘后结算管线（A 股 T+1 结算单就绪硬时点） | 盘后 | 15:30（tn=`ZephyrAlpha_PostSettlement`，**非 schedule.yaml 槽**） | ✅ | `scripts/register_post_settlement_task.ps1:42`（`-Weekly Mon..Fri -At "15:30"` + StartWhenAvailable 补火）+ `:26-28`（QMT 离线降级为仅系统侧核对，不伪造券商比对）；`src/zephyr/trading/post_settlement_pipeline.py:43` `POST_SETTLEMENT_CRON="30 15 * * *"`；`scripts/run_post_settlement.py`；留痕 `data/runtime/post_settlement_last_run.log` 末段 trade_date=2026-09-24、audit_status=OK、errors=(无)、account=8886156677、exit_code=0 | 3 |
| D13-29 | 日终三账核对（柜台/内部/持仓 L1+L2+L3） | 盘后 | 15:40 交易日 `eod_reconciliation` | 🔨 | schedule.yaml:202-213；`src/zephyr/trading/recon_runner.py:392 run_daily_reconciliation`（MOD-TRADING-007，`:22` 触发方式仍写"57 号文日循环 SOP §5 人工/后续调度触发=本模块不挂调度"，与已挂 15:40 槽**文档滞后**）；最近执行留痕未取到（差异表在 governance.db，本会话未定位读数） | 3 |
| D13-30 | 盘后日K线层（当日主行情落库=下游全链就绪门） | 盘后 | 16:30 交易日 `daily_kline` | ✅ | schedule.yaml:79-82（heavy 池）；CH `kline_daily` 全表 10,102,587 行 max=09-23、`kline_index` max=09-23（今日 16:30 未到时点，昨日已产=正常）；实测挂 36 任务 | 1 |
| D13-31 | 当日回测跑批（对账 L1 基准腿） | 盘后 | 16:30 之后，**无槽** | ⬜ | 唯一真源=**已归档** `57_daily_cycle_sop.md:71-80`（库级调用+显式 sink 落盘，产物 `data/backtest_artifacts/{run_id}.json`）；GAP-5 转 CAND-BT-003（`:109`）；在位排班=零 | 2 |
| D13-32 | 日循环总扳手（全链 16 段排班编排）★本图最大节点 | 盘后 | 16:45 交易日 `dloop_post` | ✅ | schedule.yaml:242-253（原 MANUAL-ONLY 经 Owner 批准 2026-09-21 解除；总闸 `data/runtime/daily_loop_master.disabled` 实测**不存在**=开着）；`daily_loop_master_switch.py:337-368` PHASE_STAGES / `:402-419` dispatch；留痕=`decision_daily` max=09-24（见 D13-34） | 16 |
| D13-33 | 收盘验证→三表结算（段序契约：verify 恒先于 settle） | 盘后 | dloop 段内（无独立时点） | 🔨 | `daily_loop_master_switch.py:225-236` + `:335` 注释"postmarket 内 verify 恒先于 settle——钩子序契约"；`judgment_settler.settle_all`；留痕 `judgment_plan_verification` 的 scenario_hits 含 `"trigger_ts":"2026-09-24 10:30:00"` | 2 |
| D13-34 | 日度拍板（裁定 305 安全态，GRADUATED_PACKAGES 恒空→结构性无实盘） | 盘后 | dloop 末段 `decision` | ✅ | `daily_loop_master_switch.py:239-243,44-45`；`strategy_pipeline.daily_decision_orchestrator.run_daily_decision`；CH `c1_backtest.decision_daily` max(trade_date)=2026-09-24（全表 69 行） | 2 |
| D13-35 | 盘后数据批次群（L5/L6 资金面·事件·当日补下载） | 盘后 | 17:00 `daily_backfill` / 18:00 `daily_capital` / 19:00 `daily_event` | ✅ | schedule.yaml:148-151,85-94；CH `money_flow` 全表 522,469 行 max=09-23（daily_capital 昨日已产）；实测挂载 43+42+…任务，**内部结构归图12（让渡 3）** | 3 |

### 段 D 夜窗与贯穿（20:00–次日 05:30 + 周月批 + 全日不变量，9 环节）

| 环节编号 | 环节名 | 段 | 时点(槽位) | 状态 | 真源映射 | 子环节数 |
|---|---|---|---|---|---|---|
| D13-36 | 研报明细增量层（全市场逐股 ~2h） | 夜窗 | 20:30 交易日 `research_nightly` | 🔨 | schedule.yaml:96-101（max_instances=1；历史已回补 14.7 万行，日度仅补增量窗） | 1 |
| D13-37 | 夜间财务层（财报/十大股东/融资融券 T+1） | 夜窗 | 22:00 交易日 `nightly_financial` | 🔨 | schedule.yaml:113-117（heavy；22:00 因由=T+1 此时已发布）；实测挂载 21+ 任务 | 1 |
| D13-38 | 每日完整性巡检（只检测+告警，不补跑） | 夜窗 | 23:00 交易日 `integrity_check` | 🔨 | schedule.yaml:153-157；与 D13-35(17:00 补下载)、D13-01(05:30 对账) 的三路分工真源=**散文注释** L143-147,159-167（本图要把它变成三条可查边，见 §5 簿 03） | 2 |
| D13-39 | 一致预期管线双向验证（自建聚合 vs 同花顺快照对答案） | 夜窗 | 23:30 交易日 `consensus_crosscheck` | 🔨 | schedule.yaml:103-111（2026-09-14 源污染事件治本配套；秩相关/新鲜度/结构断言/PIT 零修正率四查，落 `c1_market.cross_validation_log`） | 2 |
| D13-40 | 另类宏观日频（ECB 参考汇率，假日缺价保守游标自愈） | 夜窗 | 23:35 交易日 `daily_alt_fx` | 🔨 | schedule.yaml:194-200（L1 上架流水线首个正门槽位） | 1 |
| D13-41 | 周批与月批（跨过日界的重活） | 夜窗 | 周一 02:00 `weekend_backfill` / 周一 03:00 `weekend_calibration` / 月初 09:16 `monthly_static` | 🔨 | schedule.yaml:119-141,130-134；**实测在册时钟事故两起**：L125-128"原 cron `0`=周日，与注释意图'周一'差一天——周日 QMT 不可达+晨维护窗双重撞死=09-20 周窗未 firing、daban 链断 5 日的上游根因"；而 L136-139 注释又断言"APScheduler 0=周一，非周日"→**同一文件内两条互斥的 dow 口径**（§5 簿 08） | 3 |
| D13-42 | 常驻守护三路（reaper / deadman 心跳 / guard 三件套） | 贯穿 | AtLogOn + 每 5 分钟重点火 | 🔨 | `scripts/register_guard_tasks.ps1:46-52`（DataScheduler/TickSubscriber/…+DeadmanSwitch 读 3 路心跳，stale>10min 告警）；`:20-27` 单实例唯一 SSoT=脚本级 PID 锁+心跳判定，Task Scheduler 必须不参与单实例决策（08-06/08-07 两日静默死亡根因）；`:33-37` INT-03 92 号 D3 裁定=`ZephyrAlpha_TradingWatchdog` 注册于 **Disabled 态**；`scripts/deadman_switch.ps1:138,167`（PaperSession 陈旧→`schtasks /run`）。**主体让渡 GOMAP**（普查 §5），本图只留接缝三点：09:25 前谁必须活着、15:05 后谁该退、心跳缺失算不算当日 FAIL | 3 |
| D13-43 | 交易日历闸门（本图不变量载体：事件触发禁定时器） | 贯穿 | 每槽触发时实查 | 🔨 | `src/zephyr/data/trading_calendar.py:151-163` 实测守卫 **9/29 槽**（intraday_realtime/intraday_minute/daily_kline/daily_capital/daily_event/nightly_financial/daily_backfill/integrity_check/auction_highfreq），其余 20 槽非交易日空跑由幂等吸收（schedule.yaml:247-248 dloop 自证"法定假日空跑由底层幂等闸+数据就绪门 fail-closed 吸收"）；生效实证=`paper_session.log:3`（09-19 SKIP is_trading_day=False）；铁律真源=`config/strategy_production_map.yaml:22` laws 第3条"事件触发禁定时器：trade_calendar 闸门+数据到达触发，禁 cron/sleep-loop"；宪法 §9.3 | 3 |
| D13-44 | 日界交接（T 日盘后 → T+1 日盘前的状态移交） | 贯穿(段界) | 23:35 收口 / 05:30 重启 | ⬜ | 在位件 `src/zephyr/trading/shift_handover_checklist.py`（MOD-INF-035）对象是 **24/7 三班制 UTC 0/8/16 + 持仓/保证金五项**（`:7` INVARIANTS），面向连续市场，**不覆盖 A 股日界**；A 股 T→T+1 散在 plan_engine 三件（实测在位：`intraday_tomorrow_forecast.py`/`tomorrow_boundary_planner.py`/`overnight_boundary_reviser.py`）；**实测 `judgment_next_day_forecast` 按上海日 max=09-21，缺 09-22/09-23 两交易日=断供** → 四段里唯一"名义在产、实测断链"处 | 4 |

**合计 44 环节**：盘前 12（D13-01..12）｜盘中 12（D13-13..24）｜盘后 11（D13-25..35）｜夜窗与贯穿 9（D13-36..44）。
**状态分布**：✅ 14（31.8%）｜🔨 27（61.4%）｜⬜ 3（6.8%）｜🌑 0（环节格里无 🌑；5 项不可得集中在 §6 点名，其中 4 项落在 D13-09/D13-28 的腿上，不占独立格）。
🔨 占六成是本图的诚实形态：12 个编排型特殊槽与 3 个 ps1 feeder 的**执行留痕不在仓库可读区**（调度器日志不落地、告警走 Alerter 外部通道）。**降 🔨 不升 ✅ 就是本骨架与"凭印象标 ✅"的分界**（skeleton policy §5 铁律）。

### 2.1 触发机制三分（本图独有的结构性发现，亦是"脊"必须独立成图的实证）

| 机制 | 载体 | 本图环节 | 时刻真源 | 实测缺陷 |
|---|---|---|---|---|
| A. APScheduler 进程内 cron | schedule.yaml `schedules:` | 24（29 槽） | schedule.yaml | 12 槽零任务=编排型特殊槽，走 `scheduler.py:_run_special_schedule` 硬编码白名单，新开有名无实的槽会落到"时段 X 无任务"分支后**静默返回成功=假通道**（schedule.yaml:222-227 自证 R-021） |
| B. Windows 计划任务 | 22 个 `scripts/register_*.ps1`（实测含触发器者 12 行） | 6（D13-07/12/19/26/28/42） | ps1 的 `-At` / `-Weekly -DaysOfWeek` | 完全不在 schedule.yaml 视野内；资源册 `ops_qmt_watchdog` window_expr=**None**（真触发 08:45+12:55 未被抽到）=跨机制抽取自身漏拍 |
| C. 事件/唤醒词进程内段 | `PHASE_STAGES` + `maybe_*` 钩子 | 14（D13-20..24/33/34/44 等） | `daily_loop_master_switch.py:68-73` | 无独立时刻，全赖 D13-32 的 16:45 圈或人工逃生口 → **D13-20 的 10:00-10:30 窗闸在自动圈下恒 skipped**（结构性失效） |

三机制互不可见，是 `resource_schedule_panorama_plan_v1.md` §1 自陈的病根（"排班真源散落三处、互不可见、靠人脑避坑"）；排班四件套治的是**争抢**，无人治**日序**。

## §3 与 TDM 的分工线

**一句话**：**TDM 回答"遇到什么情况→怎么判→做什么"，图13 回答"这一分钟必须发生什么→谁给它让路→它没跑算谁的责任"；前者是决策树，后者是值班表，两图对同一资产（dloop 16 段）取不同投影，同资产不同轴。**

**这条线切不切得开？用四个最难判的对象实证（切不开=图13 不该独立存在）：**

| 对象 | 像决策还是像时序 | 判定归属 | 依据（字段级，不是口号） |
|---|---|---|---|
| dloop 16 段链（D13-32） | **两者都像**，最难判 | **拆两边各半**：段序/幂等口径/fail-open 与唯二 fail-closed/触发时刻→图13；每段的 decision_question/判据因子/动作产物→TDM | `daily_loop_master_switch.py:337-368` 只有段序，`:8` INVARIANTS 全是时序纪律；反观 `daily_plan.py` 的"今天买什么"必走 TDM。**TDM 侧已实证有接盘位**：`TDM-E-L0-03 收盘复盘与明日边界 / activation=盘后 / point=盘后 / module_ref=src/zephyr/plan_engine/tomorrow_boundary_planner.py`（实测读出）——TDM 已在引用同一段的决策语义，图13 再引用其时序，两投影无第二真源 |
| 盘后结算+三账核对（D13-28/29） | 像流程 | 时刻与就绪归图13，对账判定归 TDM/battle_map | 普查 §2 第1问（Owner 四问定案：交易执行流不建新图，缺的只是盘后结算段→归图13）+ §5"交易执行/结算→TDM L4/X-S2 + 图13 盘后段"；battle_map `flow_stage='reconciliation'`（`battlemap_schema.py:107`）+ BM-REC-01 承载装配落点。图13 只新增一条信息：15:30 结算单就绪硬时点与 15:40 核对之间的**等待关系** |
| 交易日历闸门（D13-43） | 纯时序 | **图13 独占** | 无决策问题可填（休市日不产判定，只产"该不该跑"）；TDM 的 `activation` 枚举无法表达"今天不跑" |
| QMT 看门狗 / 模拟盘 09:25（D13-07/12） | 纯时序 | **图13 独占** | 无判据、无策略挂载位；TDM 182 节点里 `activation` 有 46 个 premarket 却零个"08:45/09:25" |

**结论：切得开，但必须写成两条禁则才守得住（施工期必然越界）**：
- 禁则一：图13 节点**不得有** `judgment_basis`/`factor_refs`/`strategy_refs`；要判据唯一出路 `tdm_ref: TDM-*`。
- 禁则二：TDM 节点**不得有** cron/时点/`ready_gate`；要时刻唯一出路 `daycycle_ref: D13-*`（新增反向锚）。
- 交叉锚机制不另造：AGENTS §8 已有"业务资产库 16 表挂 TDM 交叉轴（`_XREF_SPECS` 表驱动）"，图13↔TDM 互引应进同一 `_XREF_SPECS`（已列入 §5 末总包收口请求 2）。

## §4 批次志

| 批 | 类型 | 跑否 | 做了什么 | 环节增量 |
|---|---|---|---|---|
| B1 | 需求批（消费端缺口反挖） | ✅ | 消费端=普查 §2 第1问 + §3 图13 定义；反推缺口=无图可查 dloop 16 段与 3 个 ps1 槽的日序；起点取已归档 57 号六环节 SOP 为最小集 | 0 → 6 |
| B2 | 三扫·路①按生产者逐家过 | ✅ | 按**触发机制三分**（§2.1）逐家过：APScheduler 29 槽 / 22 个 ps1 / 进程内 16 段。机制 A 补 18 槽级、B 补 5 个 ps1-only（D13-07/12/19/26/28）、C 补 8 段内（D13-20..24/33/34/44） | 6 → 28 |
| B3 | 三扫·路②按形态/类别逐类过 | ✅ | 按四段划界逐类过，逼出 5 个不属任何数据槽的运营环节：D13-09 就绪门编排 / D13-31 当日回测跑批 / D13-35 批次群归并 / D13-42 守护接缝 / D13-43 日历闸门 | 28 → 41 |
| B4 | 案例批（一个真实交易日） | ✅ | **案例=2026-09-24（会话当日，周四交易日）**，按时点实排当日发生了什么：06:50→07:10→08:20→08:34→**08:45:02 QMT OK pid=47540**→09:15 sector_pre_open（**实测未落库**）→09:15-09:25 竞价采集（auction_book 当日 3,816,492 行）→**09:25:03 模拟盘 START**→09:30→**10:05:16 / 11:05:15 资金流各 90 行**→11:22(CST) `judgment_intraday_market_state` 当日 2 行→**12:55:02 QMT OK pid=22860**→（09-23 实证 15:05:07 保活收口 exit 0）→15:10×2→**15:30 结算 trade_date=09-24 audit OK exit 0**→15:40→16:30（`kline_daily` 停在 09-23=今日未到点，正常）→16:45 dloop（`decision_daily` 09-24 在产）→17:00→18:00→19:00→20:30→22:00→23:00→23:30→23:35。**逼出 3 个新环节**：D13-08 十源探针（只有日志面能发现，schedule 里不存在）、D13-26 指数分钟K EOD（只有 ps1 里有）、D13-44 日界交接（顺带查出 next_day_forecast 断供）。**并当场证伪 2 格 ✅**：D13-10 滞后 1 日、D13-25 滞后 2 日 | 41 → 44 |
| B5 | 考古批（旧实现/退役件清产核资） | ✅ | 五件：①57 号 SOP 已归档（2026-08-30 核销批），六环节全有现役对应物、GAP-2/GAP-3 已闭环而文档已死→现役接线无图可查；②普查点名而仓内不存在的 `SimBridge 09:35`；③普查"27 槽/十环节/资金流 4 槽"三处数字漂移（实测 29/16/5）；④`schedule_consistency_reconciler.py:31` 声称 86 实体而真源 81（在册文档自漂）；⑤`post_settlement_pipeline.py:19-25` 自陈 15:30 挂调度曾为"文档约定"（GAP-3），现由 **ps1 侧**闭环而非 schedule.yaml 侧→同一硬时点两处真源。**零新增环节，改判 4 处**：D13-09、D13-31 判 ⬜（无现役执行体）；D13-06 由候选 ✅ 降 🔨（`suspend` 0 行）；D13-29 的模块头"本模块不挂调度"与已挂 15:40 槽冲突，判文档滞后待作业簿处置 | 44 → 44 |
| B6 | 三扫·路③按消费者文献核（学术/机构/同业） | ❌ **未跑** | 只读挖矿会话未做外部检索。缺口显式化：日循环运营时序的机构口径（券商/资管 trading-day operations runbook、ITIL daily ops、MiFID II RTS 6 Art.5(2)/Art.14(2)——后者已在 layering policy §2.2.1 引过但未用于检验"时序分层是否合理"）。不跑完这扫，四段的**划界方式**无法证明优于其他切法（如按交易所时钟切 5 段、按数据 PIT 锚切） | — |

**收敛判据现状**：相邻两批增量 B4(+3)→B5(+0) 已趋零 ✅；**三扫未收敛**（路③缺）❌ → **本骨架不满足封矿四判据，禁止封顶**。
（撞车判定 §0 不依赖封顶——它是四道门第③门的独立实证，可先行交付。）

## §5 待挖清单（应开作业簿 10-12 本）

优先级 = 断链风险 × 无真源可查度：

| 簿号 | 标题（须引用 D13 编号） | 为什么必须先挖 | 六向缺向 |
|---|---|---|---|
| `01_D13-32_dloop十六段链.md` | 日循环总扳手：16 段逐段的生产者/幂等闸/失败留痕 + "十环节"编号考古 | 本图最大节点（16 子环节），且"普查数字错、现役已扩面"的典型；`[MODIFY-GUARD]` 指向 `docs/_working/daily_loop_campaign/00_reuse_audit_ledger.md` 须一并读 | 内 / 史 |
| `02_D13-43_交易日历闸门.md` | 29 槽的日历守卫归属：为何只有 9 槽受守卫、其余 20 槽靠什么吸收；周末/法定假/调休三态；`is_trading_day` 真源与保守判据 | 宪法 §9.3 与 `strategy_production_map.yaml:22` laws 的落地核查点；判错=假日空跑或该跑不跑 | 上 / 旁 |
| `03_D13-A_三路兜底分工.md` | `catchup_guard`(05:30 档期对账) vs `daily_backfill`(17:00 行数缺口) vs `integrity_check`(23:00 只告警) 三者边界 + `data_supply_sentinel`(06:50) 第四路 | 三者分工**目前只活在 schedule.yaml 的散文注释**（L143-147,159-167,215-227），不可查、易改错；本图要把它变成三条边 | 旁 |
| `04_D13-D_盘中段的节拍缺失.md` | D13-20 竞价命中 10:00-10:30 窗闸在 16:45 自动圈下恒 skipped；D13-23"有节拍席位无节拍"；D13-22 归类调用方 | 实证设计缺口：14 个盘中/段内环节里 3 个的触发器不存在——**这是图能照出来的洞，不是文档问题** | 上 |
| `05_D13-28_29_结算与三账的时钟双真源.md` | 15:30 现存两处真源（ps1 `-At "15:30"` + `POST_SETTLEMENT_CRON` 常量）+ 15:40 三账；`reconciliation_differences` 读数与 C 类告警闭环（56 号文 C10） | INV-1 撞车面（同值两处）+ `recon_runner.py:22` 仍自陈"本模块不挂调度"=文档滞后 | 旁 / 史 |
| `06_D13-11_12_19_盘中执行体.md` | 竞价高频→模拟盘拉起→日内资金流五快照的执行体链；close_at 15:05 收口语义；Fill 持久化在位态 | 盘中段唯一有真实成交回路的三格；57 号 §2 的 GAP-2 半闭环须重判 | 内 / 新 |
| `07_D13-06_盘前元数据五子源.md` | JOB-077 五子源逐个核：**`suspend` 停复牌 0 行（1970 纪元）** 定性（未接/退役/改名）及其对 universe 构造与撮合约束的影响面 | 唯一实测发现的"名义在产、子源空洞"，是断供两月案同族 | 内 / 史 |
| `08_D13-36_41_夜窗与周月批.md` | 20:30/22:00/23:00/23:30/23:35 五槽 + 周批月批；**同一 schedule.yaml 内两条互斥的 APScheduler dow 口径**（L125"0=周日"vs L139"0=周一"）实测谁对 | 时钟事故族现役未闭（09-20 周窗未 firing 已咬过一次），必须机械化判定而非读注释 | 旁 / 史 |
| `09_D13-42_守护接缝.md` | 三路心跳（trading.heartbeat / live_strategy_biz.heartbeat / reaper）与日序的接缝；`ZephyrAlpha_TradingWatchdog` Disabled 态（92 号 D3 裁定）对本图的影响 | 与 GOMAP 的让渡面，写不清就重复建图 | 旁 |
| `10_D13-44_日界交接.md` | T→T+1 三件（`intraday_tomorrow_forecast`/`tomorrow_boundary_planner`/`overnight_boundary_reviser`）与 **`judgment_next_day_forecast` 实测断供 2 交易日** | 四段里唯一"现役断链"处；`shift_handover_checklist` 是连续市场三班制，不能顶替 | 内 / 新 |
| （余量）`11_D13-09_就绪门编排.md`、`12_D13-10_25_板块状态双槽滞后.md` | 前者=57 号三判据的合成器归位；后者=新槽未热载/未 firing 的定性（2026-09-23 新增两槽当日实测均缺产） | 视 B6 后是否溢出 | 上 / 新 |

### 总包收口请求（本车道不直写共享面）

1. `alignment_checklist.md` §3 挂图13 行时，对齐键请同时登记 **`D13-*` ↔ `slot_ref`/`entity_ref` 双向可解析性**——本图最大腐化风险是槽改名后指针失效；排班体系已有 `sched_truth_drift` warn 机制可复用（`resource_schedule_gate` blueprint §2），勿另造。
2. §3 末 `_XREF_SPECS` 交叉轴请增一行"图13 ↔ TDM"（禁则一 `tdm_ref` / 禁则二 `daycycle_ref`）。
3. 普查 `00_panorama_map_census_v1.md` 图13 段的四处数字与一个不存在的组件（SimBridge 09:35）请总包在落地批订正（本车道禁改）。
4. 施工期校验器请强制一条可红用例：**图中出现 cron 表达式字面量即判违规**（INV-1 的图13 特化）。
5. 建议同时向排班战役回传两条实测缺陷（非本图产物，本车道不修）：资源册 `ops_qmt_watchdog` window_expr 漏抽；reconciler docstring"86 实体"与真源 81 漂移。

## §6 封顶声明与 🌑 点名

**本骨架不封顶。** 封矿四判据（skeleton policy §6）现状：①三扫收敛 ❌（路③未跑）｜②相邻两批增量趋零 ✅（B4+3→B5+0）｜③🌑 清点 ✅（下表 5 项）｜④封顶声明 ⬜（本件即声明，但为"暂不封顶"声明，须待①补齐后转正式）。

**🌑 点名（当前形态不可得，留档不消）**：

| # | 🌑 项 | 为什么不可得 | 真源 |
|---|---|---|---|
| 🌑-1 | QMT 终端自动登录（挂在 D13-09 的 C1 腿） | 券商客户端无自动登录能力；Owner 裁定 2026-08-21"常开，不手动关闭就不关闭"；看门狗只能判进程在否，不能替人登录 | `scripts/qmt_watchdog.ps1:11-13`；`57_daily_cycle_sop.md:14`（结案"未做②"）、`:46`（C1 失败=当日模拟盘 SKIP + 通知 Owner） |
| 🌑-2 | 断网断电真演练 RUN-05（宪章约束五 RPO=0） | 物理操作须 Owner 执行或在场，AI 不得自行断电断网；文档口径已预置、K1/K2/K3 实测记录全 ⏳ | `57_daily_cycle_sop.md:141-169` §9 |
| 🌑-3 | 柜台侧真实结算单 | 现账户为模拟盘（account=8886156677），无经纪商真结算文件；QMT 离线时按 INVARIANTS 显式降级、不伪造券商侧比对 | `register_post_settlement_task.ps1:26-28`；`post_settlement_last_run.log` 三行 `[标注]`（日终审计=空快照最小输入；VaR 回测跳过，绝不拿空归档伪造定级） |
| 🌑-4 | 交易所/经纪商官方日终批处理完成时刻的外部真源 | 无公开可订阅信号；15:30 是 A 股 T+1 保守推定硬时点（54 号 §3.3）、15:40 为经验错峰 → D13-28/29 的"就绪"永远是推定而非确认 | `post_settlement_pipeline.py:42-43`；`schedule.yaml:202-206` |
| 🌑-5 | 15:00-15:05 尾段成交的完整捕获口径 | 模拟盘 close_at 15:05 收口 + `stop()` 自动撤未成交单；该外盘后时段的成交归属无外部规范可依 | `register_paper_session_task.ps1:47`；`paper_session.log:144-145` |

**封顶预告（满足后可转正式封顶）**：B6 跑完（产出=四段划界是否有更优切法的结论）+ 作业簿 01-10 交付后无新 D13 编号溢出（溢出须先回写本骨架 §2，回写权只在总包与本骨架主）+ **本件所有实测计数在图本体建成后一律退役为生成器字段引用**（根宪法 §9 条目 5"静态清单禁手工维护"；本件 §0.2 纠偏表与 §2 计数即属届时须删除的临时件）。

## §7 实查命令附录（可复跑核验；下列均在 2026-09-24 本会话实际跑过）

PATH 前置：`export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"`（3.12.8）。

```bash
# ── A 组：时点存在性
# A-1 数 schedule.yaml 槽数（实测 29；普查说 27）
python -c "import yaml;print(len(yaml.safe_load(open('src/zephyr/data/config/schedule.yaml',encoding='utf-8'))['schedules']))"
# A-2 列槽名+cron+executor 全表
python - <<'PY'
import yaml
s = yaml.safe_load(open('src/zephyr/data/config/schedule.yaml', encoding='utf-8'))['schedules']
for k, v in s.items():
    print(f"{k:26s} {v.get('cron',''):22s} {v.get('executor')}")
PY
# A-3 拆"数据管线槽（有任务挂载）"vs"编排型特殊槽（零任务）"→ 实测 271 任务 / 17 槽 / 12 槽
python - <<'PY'
import yaml
t = yaml.safe_load(open('src/zephyr/data/config/tasks.yaml', encoding='utf-8'))['tasks']
s = yaml.safe_load(open('src/zephyr/data/config/schedule.yaml', encoding='utf-8'))['schedules']
m = {x.get('schedule') for x in t if x.get('schedule')}
print('tasks=', len(t), '| mounted_slots=', len(m & set(s)), '| orchestration_slots=', sorted(set(s) - m))
PY
# A-4 Windows 计划任务侧时点（机制 B 全集，schedule.yaml 看不到；实测含触发器 12 行）
grep -rn "New-ScheduledTaskTrigger" scripts/register_*.ps1 | grep -cE 'At "|DaysOfWeek'
grep -rn "New-ScheduledTaskTrigger -Weekly.*-At\|New-ScheduledTaskTrigger -Daily.*-At" scripts/register_*.ps1
# A-5 交易日历守卫覆盖面（实测 9/29）
python - <<'PY'
import re, yaml
s = open('src/zephyr/data/trading_calendar.py', encoding='utf-8').read()
b = s[s.index('TRADING_DAY_GUARDED_SCHEDULES'):]
names = re.findall(r'"([a-z_]+)",', b)
slots = set(yaml.safe_load(open('src/zephyr/data/config/schedule.yaml', encoding='utf-8'))['schedules'])
print(len(names), 'guarded:', names)
print('ungarded:', sorted(slots - set(names)))
PY

# ── B 组：执行体存在性
# B-1 dloop 段序（实测 full=16 / premarket=5 / intraday=4 / postmarket=8；docstring 说 11 棒；普查说"十环节"）
python - <<'PY'
from zephyr.plan_engine.daily_loop_master_switch import PHASE_STAGES as P
for k, v in P.items():
    print(k, len(v), v)
PY
# B-2 某时点反查执行体（示例：16:45 dloop_post）
grep -n "dloop_post" src/zephyr/data/config/schedule.yaml src/zephyr/data/scheduler.py
# B-3 15:30 硬时点的字面量分布（证明两处真源=INV-1 撞车面）
grep -rn '30 15 \* \* \|At "15:30"\|POST_SETTLEMENT_CRON' src/zephyr/trading/post_settlement_pipeline.py scripts/register_post_settlement_task.ps1
# B-4 日界交接三件在位性
ls src/zephyr/plan_engine/intraday_tomorrow_forecast.py src/zephyr/plan_engine/tomorrow_boundary_planner.py src/zephyr/plan_engine/overnight_boundary_reviser.py
# B-5 资源册是否已含交易运营时点（含则时刻真源不唯一）+ 86/81 漂移
python - <<'PY'
import yaml, re
d = yaml.safe_load(open('config/resource_profile_registry.yaml', encoding='utf-8'))
e = d['entities']
print('total_entities field=', d['total_entities'], 'len=', len(e))
for x in e:
    if re.search('paper|settle|watchdog|fund_flow|minute_eod', str(x['task_id']), re.I):
        print(x['task_id'], x.get('window_type'), x.get('window_expr'), x.get('schedule_truth_source'))
PY
grep -n "86 实体" src/zephyr/governance/audit/schedule_consistency_reconciler.py   # 与上一行 len 对比

# ── C 组：最近执行证据（✅ 的第三证；DB 一律 DatabaseService，禁裸 duckdb）
python - <<'PY'
from zephyr.infrastructure.database_service import get_db_service
c = get_db_service().get_clickhouse_conn()

def maxd(db, t, col):
    return c.execute(f"SELECT max({col}), count() FROM {db}.{t}")[0]

# 盘前就绪 / 竞价 / 板块状态双槽（分 stage 看滞后）
print('auction_snapshot', maxd('c1_market', 'auction_snapshot', 'trade_date'))
print('auction_book   ', maxd('c1_market', 'auction_book', 'trade_date'))
print('sector_state   ', c.execute("SELECT stage, max(trade_date), count() FROM c1_market.sector_state WHERE trade_date>='2026-09-20' GROUP BY stage ORDER BY stage"))
# L0.5 五子源（suspend 实测 0 行 / 1970 纪元 = D13-06 降级理由）
for t in ['stock_basic', 'stk_limit', 'limit_up_pool', 'suspend']:
    print(t, maxd('c1_market', t, 'trade_date'))
# 盘中判定与日界交接（asof_ts 是 UTC 存储，必须换上海日再比，否则差 8h 误判断供）
for t in ['judgment_daily_plan', 'judgment_intraday_market_state', 'judgment_next_day_forecast']:
    print(t, c.execute(f"SELECT toDate(asof_ts,'Asia/Shanghai') d, count() FROM c1_market.{t} GROUP BY d ORDER BY d DESC LIMIT 5"))
print('plan_verification', c.execute("SELECT max(toDate(asof_ts,'Asia/Shanghai')), count() FROM c1_market.judgment_plan_verification"))
# 盘后与夜窗
print('decision_daily ', maxd('c1_backtest', 'decision_daily', 'trade_date'))
print('kline_daily    ', maxd('c1_market', 'kline_daily', 'trade_date'))
print('money_flow     ', maxd('c1_market', 'money_flow', 'trade_date'))
print('sector_fund_flow', maxd('c1_market', 'sector_fund_flow', 'trade_date'))
print('sentiment_window', maxd('c1_market', 'news_sentiment_window', 'window_ts'))
PY

# ── C-补 日志面留痕（主区只读；worktree 内无这些文件）
tail -6  D:/ZephyrAlpha/data/runtime/qmt_watchdog.log
tail -10 D:/ZephyrAlpha/data/runtime/post_settlement_last_run.log
grep -n "2026-09-2[234]" D:/ZephyrAlpha/.runtime/logs/paper_session.log | tail -8
tail -6  D:/ZephyrAlpha/logs/fundflow_collect.log
tail -4  D:/ZephyrAlpha/logs/index_minute_eod.log
ls -1 D:/ZephyrAlpha/logs/source_health_*.log | tail -5
# C-6 总闸实查（无输出=三闸全开着）
ls D:/ZephyrAlpha/data/runtime/daily_loop_master.disabled \
   D:/ZephyrAlpha/data/runtime/quality_sentinel.disabled \
   D:/ZephyrAlpha/data/runtime/sector_state_pipeline.disabled 2>/dev/null; echo "(空=全开)"

# ── D 组：撞车面复核（§0 每行独立可复跑）
grep -n "_FLOW_STAGES" -A16 src/zephyr/governance/persistence/battlemap_schema.py      # battle_map=生命周期轴、无时钟列
grep -n "flow_stage\|sort_order\|source_ref\|created_at" src/zephyr/governance/persistence/battlemap_schema.py | head
grep -n "^laws:" -A4 config/strategy_production_map.yaml                                # 事件触发禁定时器铁律原文
python - <<'PY'
import yaml, collections, re
n = yaml.safe_load(open('config/trading_decision_map.yaml', encoding='utf-8'))['nodes']
print('nodes=', len(n), 'activation=', dict(collections.Counter(x.get('activation') for x in n)),
      'point=', sorted({str(x.get('point')) for x in n}))
kw = re.compile('cron|schedule.yaml|排程|槽位|排班|调度|schtasks')
print('scheduling-hits=', [x['node_id'] for x in n if kw.search(str(x))])
for x in n:
    if x['node_id'] == 'TDM-E-L0-03':
        print('TDM-E-L0-03', x.get('name_zh'), x.get('activation'), x.get('point'), x.get('module_ref'))
PY
# BM-* 步号清点（实测 349 标识 / 12 族前缀）
grep -rho "BM-[A-Z]\{2,6\}-[0-9][0-9A-Z-]*" --include=*.md --include=*.py --include=*.yaml . | sort -u | wc -l
grep -rho "BM-[A-Z]\{2,6\}-[0-9][0-9A-Z-]*" --include=*.md --include=*.py --include=*.yaml . | sed -E 's/(BM-[A-Z]+)-.*/\1/' | sort | uniq -c
```

**复跑三条注意**：(1) **时点敏感**——16:30/16:45 之前跑 C 组，`kline_daily`/`decision_daily` 显示 T-1 属正常非断供，判 D13-30/32 须 16:45 后复跑；(2) `judgment_*` 表 `asof_ts` 为 UTC 存储，必须 `toDate(...,'Asia/Shanghai')` 再比，否则差 8 小时会误判或误证断供；(3) 本文件所有计数为 2026-09-24 时点快照，图本体建成后一律由生成器产出（根宪法 §9 条目 5）。
