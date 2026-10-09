---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_06b_intraday.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-06b 盘中段（09:30–15:00）挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：FIG13 车道 `docs/_working/map_build/fig13_daycycle/`（00_skeleton.md §2 段 B + 簿04/05 + 簿04 §0.1 机制根实查）；机生图 `config/trading_day_cycle_map.yaml` segments.B；消费者扫描 `13_consumers_scan_d13.csv`（715 行，fig13 车道机生）。
- **现役挖掘 = st-fig13-bone-20261004**。本簿只读其领地；价值=①挂接收编 ②补代码消费面/字段面 ③本役三态裁定。
- **职责一句话**：09:30–15:00 行情/新闻按节拍灌库（采集层群）+ 钱怎么走/什么局面/敢不敢动（资金流与判定层）；全日决策链的发条=盘中分钟K完成事件唤醒。
- **节点与状态（图本体 2026-10-06 机生读数，16 节点）**：✅3🔨11⬜2。skeleton=✅：D13-15/19/21/24（其中 D13-24 fig13 簿05 已拆"保活腿 ✅/成交回路腿 🔨"）；🔨：D13-14/16/18/20/22/23/45/46 + D13-17（簿04 升 ✅，图镜像滞后）+ D13-13（簿04 判 🌑/红条目，recheck 字段已在册）+ D13-16（tdx 断供后由 D13-48 等权撮合收敛）；⬜：D13-G02 成交回报桥面空转、D13-G04 新闻产物表库名前缀写错（改册面归图12，本图只挂生产者腿）。

## §1 六向台账

| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上（谁触发） | 三机制并存互不可见（簿05 §0.1）：机制 A 六数据槽（post_auction/intraday_realtime/intraday_minute/intraday_sector/event_driven/news_slow）；机制 B 仅 D13-19 五时刻 schtasks（`register_counter_trend_feeder_tasks.ps1:80-83`）；**机制 C 四格**（D13-20/21/22/23+D13-24 Timer 腿）无时刻表，全赖唤醒词（`daily_loop_master_switch.py:68-73`）与事件钩子（`strategy_pipeline/pipeline_events.py:886-966`，订阅点 `wire_data_scheduler.py:1059/1085`，进程启动挂接 `scheduler.py:714-716`） | 触发机制三分=本图独有结构性发现（骨架 §2.1） | signal |
| 下（谁消费） | **本簿补充·代码消费面**：①唤醒链扇出真源=`_AUCTION_WAKE_TASKS=("kline_etf_1min","kline_etf_5min")`（`pipeline_events.py:888`）——分钟K完成事件是全日决策链唯一日内发条，`fetch_perf` rows 序列与 CH max(date) 互查可机生红（簿04 §2）；②D13-20 事件腿落 `prediction_log` 仅 1 行且 trade_date=T-1——业务日解析吃 `kline_index` max 水位（`resolve_pf_alloc_trade_date`），10:01 时今日日线未产→**恒判昨日竞价**，系统性滞后非零产（簿05 §2）；③D13-24 成交回路腿 `c1_market.execution_report` 全表 1 行（09-18 读数）→桥面空转即 D13-G02，其接线面归 env_15 簿统一裁定 | 逆势板块卡 2 吃 D13-19 五快照（下跌段段内≥1 拍，`ps1:11-13` 立论在册）；TDM `activation=intraday` 43 节点只写判据无节拍语义→处置=引用 | signal |
| 内（子环节） | D13-14 五个"跑而零产"任务分三型：假产（tick_data_snapshot/futures_tick_intraday 恒 0 行，真源是常驻 tick_subscriber WAL 链，占 realtime 池 2/4 线程）、真断供报 SUCCESS（futures_kline_qmt/hk_kline 水位停 09-16）——图本体须 `rows_last_run` 字段区分三种绿（簿04 §2）；"一任务只属一槽"精确字符串匹配（`scheduler.py:491`）落空结构：假通道 2 槽+孤儿 4 任务（`schedule: disabled` 不入 catchup 桶=双盲）+C 类 9 任务无补跑+D 类 cohort_ledger_daily 双槽挂载依赖倒置（tasks.yaml:3437/3816，list 不去重 `scheduler.py:1257-1259`）=16 受害对象（簿04 §0.1） | — | signal |
| 旁（撞车面） | D13-20 双调用方针向性错位：dloop 腿 10:00-10:30 窗闸恒关（唯一自动圈 16:45）、事件腿窗恒开——同一窗闸两真值，图本体须 `callers[]`+`window_gate_effective` 双字段（簿05 §0.1/§2）；D13-13 与 D13-11 同批五档数据的采集腿/聚合腿两格不合并；D13-14 与 D13-11 同表（auction_snapshot）两腿=补集关系 | 资源三表管池争抢，日序/就绪归本图——分工契约已在骨架 §0.1 第 5 行 | signal |
| 史 | D13-13 三态纪律教科书：骨架 🔨（槽新增+executor 已修）→簿04 🌑（零任务+无分支+17 行全来自 09-22 一次人工回灌，ingest_ts 同瞬 2026-09-22T20:11:21Z）——两态差一次 yaml join+一次 ingest_ts 分布查询；`emotion_index_auction` WIP 于当日蒸发窗被灭（EVAP-03，16 号技术目录 memo:286 在册） | 普查 SimBridge 09:35 全仓无实体证伪（骨架 B5）；D13-45 实体=SimBridgeExecute 09:35/13:05 双拍（10-04 三证立格） | signal |
| 新 | fig13 溢出在册：假通道槽子类（post_auction 明日起恒发"无任务"）、matched 不落痕（"0 条 drift"无法区分对平与没跑，O-2）、13:35 午休后第一拍无补跑兜底、`slot_effective_task_count`/`special_branch_exists` 必填字段提案；**本簿补**：机制 B 六件中 D13-45/46 两件无交易日闸（触发器纯 Daily、依赖执行体自退/假日空跑在案，骨架 10-04 回写已记）——机制 B 的日历闸覆盖面无字段表达，是字段面一致性缺口 | 无 | signal |

## §2 挖干自评

- **三扫收敛**：fig13 簿04/05 六向齐（消费者面有 13_consumers_scan_d13.csv 机生件）；本役补面后无新增矿脉，增量归零。
- **长尾**：①D13-20 业务日错位修法=业务日解析改吃竞价带自身时点而非日线水位——`resolve_pf_alloc_trade_date` 与 D13-32 输入日同源，跨段耦合须整体裁定；②机制 C 四格 `callers[]` 字段化是图本体 schema 输入，非代码施工。
- **🌑 清点**：D13-13 🌑 已在册（mining_recheck=unreachable）；无新增 🌑。

## §3 挖后自审闸三态裁定

**挂起排期**。
- 理由：①16 节点已由 fig13 两簿挖透且机生图收编（blood_stage f2_done），本役无独有可施工项；②盘中段缺口性质=图本体 schema 字段面（rows_last_run/callers[]/window_gate_effective/机制 B 日历闸标记）+两处结构洞（D13-13 假通道、D13-20 业务日错位），前者随图本体施工批，后者与 D13-32 输入日语义同源耦合——单独施工会把一个错修成两半；③成交回报桥面空转（G02/execution_report）挂 env_15 簿统一裁定，本簿不拆。
- 解锁条件：fig13 封矿 + `resolve_pf_alloc_trade_date` 业务日语义经 Owner 裁定 → 随图本体施工批落字段与修边。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 产出 |
|---|---|---|---|
| 1 | 读骨架 §2 段 B + 簿04/05（§0/§0.1/§2 关键节） | 挂接完成：D13-13 🌑、D13-20"半对半错"改判、D13-24 拆腿全部收编 | §0/§1 |
| 2 | 机生图 segments.B 解析与簿判态对表 | signal：skeleton_status 与簿判态 3 处镜像滞后（D13-13/16/17），非矛盾 | §0 状态行 |
| 3 | 唤醒链/业务日错位/机制 B 日历闸覆盖面 grep 复核 | signal：D13-45/46 无日历闸=字段面一致性缺口（本簿新增登记） | §1 上/新 向 |
| 4 | 三态裁定自审 | 挂起排期成立；D13-20 修法耦合点显式化 | §3 |
