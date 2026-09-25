---
ttl: task_bound
doc_type: log
title: L09-S4 子模块挖矿簿 · 日刊与 decision_daily 拍板快照（双账）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L09
status: MINE 完成（六向封口；两账行数/密度为 09-26 CH 只读探针实测）
---

# L09 · S4 日刊与 decision_daily 拍板快照

**① 职责一句话**：每天留下一份"今天到底判了什么、依据什么、代价多少"的可审计快照，并把平台自身健康度并排附上——让 Owner 一天一眼就能决定"继续放权 / 收紧 / 回滚"。

**② 现状实测（2026-09-26 CH 只读探针 + 实码行号）**

### 账 A：决策复盘账 `c1_backtest.decision_daily`

| 项 | 实测 |
|---|---|
| DDL 真源 | `schemas/categories/decision_daily.py`（SKEL 口径一致）；建表器 `scripts/ch/apply_decision_daily_ddl.py` |
| 列全集（system.columns 实测 **19 列**） | `trade_date, asof_data_date, run_id, schema_version, market_state, state_confidence, budget_band_low, budget_band_high, position_cap, no_trade, no_trade_reason, degrade_reasons, degraded, gate_snapshot_json, package_set_json, sit_out_list_json, calendar_source, note, ingest_ts` |
| 体量/密度 | **72 行 / 6 个唯一 `trade_date`**，min=2026-09-16、max=**2026-09-28**；逐日：09-16=**66**、09-21=2、09-22=1、09-23=1、09-24=1、**09-28=1** |
| 关键读法 | 写侧唯一=`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py`（MergeTree 只增不改，run_id 追加修订）；读侧=仪表盘 `components/warroom.py:634-646`（取 `SQL_LATEST_BY_TARGET_DATE`="当日最新 run 行"）+ **`scripts/governance/decision_chain_sentinel.py`（本册新计入的第 2 个读侧）** |
| 下单口径 | v1 安全态 GRADUATED_PACKAGES=∅ ⇒ `no_trade`/`package_set_json` 结构性为空（ruling_registry 登记号 305），E2E 实录 expansion@1.00 cap=60% no_trade=0 degraded=1(D2:L2) |

### 账 B：平台日刊账 `c1_backtest.sim_platform_journal`

| 项 | 实测 |
|---|---|
| 件 | `scripts/backtest/sim_platform_journal.py`；头注 `[MATURITY] **experimental**`、`[CONSUMERS] c1_backtest.sim_platform_journal（平台日刊）；每日自动化（**接线另批**）；AI 检验接口消费方` |
| 列全集（12 列） | `trade_date, total_equity, pocket_count, pockets_summary, event_count, data_freshness_ok, heartbeat_ok, anomalies, degraded, run_id, note, ingest_ts` |
| 三健康检 | (1) `:129` 数据新鲜度：`kline_index max < 期望基准` ⇒ 异常；(2) `:133` 账本心跳：该日无任何钱包行 ⇒ `heartbeat_ok=0`；(3) `:140` 越界持仓：持仓市值 > `QUOTA_WARNING`。汇总 `:142` `degraded = 1 if anomalies else 0` |
| 告警出口 | `:160 alert_if_degraded()` → Alerter（`--no-alert` 可关），message 取 anomalies 前 500 字 ⇒ **有产报** |
| 体量/密度 | **16 行 / 15 个唯一 `trade_date`**，06-15、08-20、08-21、09-11、09-15 起 **连续至 09-25**（09-24=2 行）；`data_freshness_ok`/`heartbeat_ok` **16/16 全填** |
| 触发面 | 事件链 FIFO 末位（`pipeline_events.py:508 run_sim_observe_daily`，次序元组=账本→日刊→归因）+ `scripts/run_post_settlement.py:341/528 _run_sim_journal_step`（schtasks `ZephyrAlpha_PostSettlement` 15:30，本册实测在册） ⇒ **双触发面，均已接电** |
| 读侧 | **零**：全仓 grep `sim_platform_journal` = 8 命中（自身/DDL/runner/post_settlement/pipeline_events/两 test），**无一个展示或决策消费方** |

### 两本账到底差在哪（L09-C03 合流议题的实测答案）

| 维度 | 账 A（决策复盘） | 账 B（平台日刊） | 合流冲突 |
|---|---|---|---|
| 回答的问题 | "系统**判**得对不对" | "系统**活着**吗、钱在不在范围内" | 互补，不重复 |
| `trade_date` 语义 | **拍板生效日=次交易日**（前瞻）⇒ 09-25 晚写的行标 09-28 | **体检日=当日**（回顾）⇒ 本册实测 **09-19(周六)/09-20(周日) 各有一行** | **①主键同名不同时间轴**——这是最硬的冲突；直接 JOIN 会把"T 日的判决"对上"T 日的健康"，错位一个交易日 |
| 日频口径 | 只交易日、且**有空洞**（目标日 09-25 缺行） | 按日历日跑（周末也落行） | **②"连续绿天数"若按行数日差算，会被周末行虚增**——这就是 13 号文环节⑥"靠人翻台账"不只是懒，而是**算法本身会算错** |
| 幂等 | MergeTree 只增不改，run_id 追加修订（同日多行合法） | "一交易日一行幂等替换"，实测 09-24=**2 行**（替换语义未成立） | ③两账幂等模型不同，合流视图必须各自保留 run_id 维度 |
| 成熟度标签 | 事件链末棒在产（trial→在产） | **experimental** | ④把 experimental 并入 Owner 晨报需先转正 |
| 消费面 | 2 个读侧（warroom 面板 + 哨兵） | 0 个读侧 | ⑤合流不是"两账对称合并"，而是**给账 B 补读侧并与账 A 对齐时间轴** |

### 本册另发现：哨兵可被"未来日"永久消音（与 S1 册 G 项同源，此处给数）
`decision_chain_sentinel.py` 判据 `last = max(decision_daily.trade_date)`。本册实测 `max=2026-09-28`，而今日为 09-26(周六)、参照日 ref=最近开市日 09-25 ⇒ `lag = (09-28, 09-25]` 内开市日数 = **0**，哨兵静默。
**但同期真实覆盖：目标日 09-25 无行（09-17/09-18 亦无）**——即最近一个交易日的拍板缺席，哨兵读不出来。
⇒ 结构性结论：`max()` 型滞后尺**只测"最新一行有多旧"，不测"逐日是否连续"**；拍板体偶尔产出一行指向未来目标日即可长期虚报健康。这是 `TRD-A01/L09-C04` 落地后的**首个可复现缺陷**，不是"没做"，是"做了但尺子选错"。
（对照：账 B 的"心跳"检 `:133` 用的正是"该日有无钱包行"=存在性日检，口径比哨兵正确——**仓内已有正确尺子的先例，属可内收对象**。）

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：账 A=S1-S7 全链（六段态/预算带/门快照/sit_out/日历哨兵/kill_switch）；账 B=`sim_pocket_daily` 权益 + `sim_trade_log` 事件 + `kline_index` max。外部：已查无 |
| ②下游 | 内部：账 A→warroom 今日决策面板 + 决策链哨兵；账 B→**无**（Owner 人工翻 CH）。合流后目标下游=Owner 晨报视图 + 连续绿天数判定件 + L09-C02 计划vs实际核对。外部：post-trade review / 日频对账惯例（13 号文 §5.3 已对表，沿用不重列） |
| ③算法 | 内部：账 A 无算法（快照装配）；账 B 三健康检=阈值比较。外部：已查无（合流是数据工程不是算法） |
| ④后端 | 内部：①两账时间轴冲突（本册核心发现）；②账 B `INSERT` 见 `:191`，"幂等替换"与实测 09-24 双行矛盾；③账 A 无"当日是否应有行"的期望日集合真源（要判缺勤需 join `market_trade_calendar`，哨兵已 join 但只用于取 ref 单点，未用于逐日 diff）；④合流件若新建表=违反净零（应做视图/日级物化）。外部：已查无 |
| ⑤前端 | 内部：warroom `:1296 今日决策面板`（账 A 只读展示 no_trade/degraded 可视）为**唯一**人机面；账 B 零面。⇒ Owner 现有界面里**看不到"系统是否健康"，只看得到"今天判了什么"**。外部：Grafana 类面板已判不引（S1 册），Owner 面走自研 streamlit 组件同域内收 |
| ⑥数据字段 | 内部：`anomalies` 为 JSON 字符串列 ⇒ 可存但不可聚合（要按异常类型统计需 JSONEachRow/数组列）；`pockets_summary`/`gate_snapshot_json`/`package_set_json`/`sit_out_list_json` 四 JSON 列 ⇒ **"字段在"≠"可分析"**，当前无任何件把 JSON 摊平成维度。实测 `data_freshness_ok`/`heartbeat_ok` 16/16 有值、`degraded` 有值 ⇒ 健康位可得；账 A 的 `no_trade=0/degraded=1` 在 E2E 行实证可得 |

**④ 缺口清单**

| 编号 | 内容 | 状态 |
|---|---|---|
| L09-C02 / TRD-A17 全量 | 计划 vs 实际核对实体化（`daily_decision_orchestrator.py:754-767` 仅签名）→ 状态真值全史=0（四判据唯一维持 ✗ 的项） | 在册 |
| L09-C03 / TRD-A17 | 日刊双账合流 | 在册；**本册给出"差在哪"的 5 条实测冲突**（时间轴/日频口径/幂等模型/成熟度/消费面），合流工作项见 ⑤ |
| TRD-A19 | decision_daily 逐日审计报表消费端缺 | 在册 |
| L09-C04 落地后缺陷 | **哨兵 `max()` 尺无法发现逐日空洞**（本册实测：lag=0 而目标日 09-25 缺行） | 新增·P1（属 L09-C04 转正阻塞项，不重复立项，挂在 L09-S1-G3 下） |
| L09-S4-G1（新） | **账 B 零读侧 + 头注 experimental + `[CONSUMERS]` 写"接线另批"** ⇒ 三健康检产报 16 日而无人/无件消费（除 Alerter 的异常支路）；`degraded=0` 的"绿"完全无人知晓 | 新增 |
| L09-S4-G2（新） | 周末行虚增连续天数（09-19/09-20 实测有行）⇒ 任何"连绿 N 日"算法必须先过交易日日历 | 新增 |
| L09-S4-G3（新） | 账 A 历史密度：72 行中 66 行是 09-16 一次批量，**自然日频仅 6 行** ⇒ 快照"深史"实为 6 个目标日，四判据"深史全 🟡"应下调表述为"结构已通、深史 6 日" | 新增（口径纠偏） |
| L09-S4-G4（新） | 账 B 幂等替换未成立（09-24 双行） | 新增 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由 / 解锁条件 |
|---|---|---|
| L09-C03 双账合流 | **施工（P1）**，且给出可绕开 L09-C02 的分期 | 原账本记"L09-C02 后串行"；本册实测主张**拆两半**：合流的"时间轴对齐 + 账 B 补读侧 + 连绿判定件"三步**不依赖计划vs实际核对**，可先行；只有"第四本账（计划↔实际）"必须等 L09-C02。净零要求：合流走视图或既有 warroom 组件扩面板，**不新建表** |
| 合流具体工作项（本册产出） | 施工清单 | ①定基准轴=引入 `expected_trade_date`（来自 `market_trade_calendar`）作两账共同主轴，禁止用行存在性推日频；②账 B 读侧并入 warroom 同页（`degraded`/三类异常计数）；③连绿件=按 `expected_trade_date` 序列比对两账行存在性，缺口即红（同时吃掉 G1/G2/G4）；④账 B maturity experimental→trial 转正判据="连续 20 个期望交易日有行且连绿件在跑" |
| L09-C02 计划 vs 实际 | **挂起排期 + 解锁条件** | 不是本车道能做的：它要新增落库（列或伴生表）=不可逆点（一旦有消费方难回退），且属四判据唯一 ✗ 项、需 Owner 认判定/结算分离口径（真源=`judgment-ledger-standard` §一）。解锁=L09-C01 定权威节拍后开工（否则 reconcile 跑在哪个轨道都没定） |
| L09-S4-G3 深史口径 | 施工（P3 文档，本册即交付一半） | 宪法 §4.3 文档矛盾=事故：把"深史≈10 日量级"改为实测"6 个目标日 / 72 行 / 66 行为单次批量" |
| TRD-A19 审计报表 | 挂起排期 | 解锁=合流③连绿件先落地（报表的数据源就是它），否则报表又是一个人工维护静态清单（宪法 §9.5 禁手工维护"条目+计数"） |
| 无"快照的快照"周/月循环 | 挂起排期 | 解锁=55 号周/月复盘件与本块日频件合流关系澄清（沿用 SKEL §三未挖清单第 4 项，本册未钻，标为未挖） |
| 封矿？ | **不封** | 明令禁止以"现状规模小（72 行/16 行）"封矿；本块恰是 Owner 唯一决策面，终局全貌=100% AI 自制下"人翻台账看健康"必不成立 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 归因 |
|---|---|---|---|
| R1 | 两表列全集 + 行数 + 逐日密度（CH 只读探针） | signal | 得出 19 列/12 列、72 行/16 行、6 目标日/15 日 |
| R2 | 周末行核验（`datetime` 判星期：09-19=Sat、09-20=Sun） | signal | **G2 虚增连绿**——本册最有 actionable 价值的小证据 |
| R3 | 全仓 grep 两表读写侧 | signal | 账 A 读侧=2（warroom+哨兵，SKEL 记 1，已刷新）；**账 B 读侧=0** |
| R4 | `sim_platform_journal.py:96-205` 三检与告警实码逐行 | signal | 检为真、告警为真、但绿无人知 |
| R5 | 哨兵消音复算（max=09-28 vs ref=09-25 ⇒ lag=0 而 09-25 缺行） | signal | **L09-C04 落地后首个可复现缺陷**，并找到仓内更正确尺子先例（账 B 心跳检 `:133`） |
| R6 | 外部对表 | 未做 | 延至统一轮；候选=three-way reconciliation / daily post-trade review（SKEL §5.3 已有一轮并声明开源侧无直接件，沿用其结论不重做）。登记为"本册未做外部对表" |

**本册封矿判据**：六向封口；L09-C03 的"两本账差在哪"给出 5 条实测冲突 + 可执行合流工作项；四判据中"深史全"口径纠偏。⇒ **子模块封矿（L09-C02 随裁定）**。
