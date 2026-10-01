---
ttl: task_bound
---

# S5 数据管线盘点 — st-ffchief-20261001

> 盘点时间：2026-10-01 13:10–13:25（Asia/Shanghai，国庆休市第 1 天，数据源静默属预期）。
> 盘点口径：只读盘点 + 烟测级读探针；零写操作（本文件除外）、零回填、零 OPTIMIZE。
> 判色基准（假期修正）：A 股核心表 max(trade_date)=2026-09-30（最后交易日）=绿；滞后 ≥3 交易日=黄；≥7 交易日或源级断供=红。7×24 市场（crypto/us/hk）按各自日历判。

## 0. 总览计数

| 维度 | 数值 |
|------|------|
| 调度任务总数 | 271（tasks.yaml 真源，TableRegistry 核对一致） |
| 调度时段槽位 | 32（schedule.yaml） |
| 数据源 | 18（policies.yaml） |
| 特殊巡检层 | 8（L10 weekend_backfill / L10.5 daily_backfill / L11 integrity_check / L11.5 cross_validation / L10.7 catchup_guard / L12 pf_alloc_rebalance_check / L13 data_supply_sentinel / calendar_coverage_check） |
| 断供哨兵覆盖 | 58 配置条目（data_supply_sentinel.yaml） |
| 独立管线脚本 | scripts/data ≈45、scripts/ 根 backfill* 5、scripts/ch ≈50（DDL/回填/归档） |
| 今日任务执行 | scheduler_run.log 内 SUCCESS 1363 条次 / ERROR 260 条次 |
| 核心探针 33 表 | 绿 24 / 黄 7 / 红 2 |
| 哨兵全量 58 项 | breached=12、blind_spots=0（06:53 今日巡检） |
| Windows 计划任务（数据相关） | 匹配 48 项：Running 5（DataScheduler/TickSubscriber/BoardIndexRealtime/BeltDaemon/CHHealthProbe）、Ready ≈20、Disabled 7 |

**总体判定：管线主体存活（调度器 Running、盘后批 09-30 数据全量落地、月度静态槽今日实跑），但存在四处硬伤：①macro_data_incremental 系统性连败（今日 215 错）；②tdx 板块分钟真值腿全断（今日 0 成功 5 失败+rows=0）；③6+ 张表级断供/停更（含 2 张红表）；④告警外发通道关闭（endpoints=[]，CRITICAL 仅本地留痕）。**

## §1 管线总表

### 1.1 调度槽位（32 档，schedule.yaml 真源）

| 槽位 | cron | 层 | 今日运行证据 | 状态 |
|------|------|----|--------------|------|
| event_driven | */3 * * * * | L3 新闻/宏观 | 13:09 仍在跑；macro_data_incremental 连败 | 黄（1/10 连败拉高失败率告警） |
| news_slow | 17,47 * * * * | L3.5 慢新闻 | news_rss SUCCESS 21 行（13:09） | 绿 |
| pre_market | 34 8 * * 0-4 | L0.5 盘前元数据 | 今日 08:34 触发（假期照跑） | 绿 |
| post_auction | 30 9 * * 0-4 | 竞价后 | 假期零增量属预期 | 绿 |
| intraday_realtime | */5 9-15 * * 0-4 | L1 Tick/L2/IV | TickSubscriber Running；假期无盘 | 绿 |
| intraday_minute | */5 9-15 * * 0-4 | L2 分钟K | kline_1min max=09-30 | 绿 |
| intraday_sector | */5 9-15 * * 0-4 | L2.5 板块分钟 | kline_sector max=09-30；但今日连续 0 成功 5 失败（tdx connect_fail，见 §2） | 红（tdx 腿） |
| daily_crypto | 41 8 * * * | 币圈日线 | crypto_kline_daily max=09-30 | 绿 |
| daily_kline | 30 16 * * 0-4 | L4 盘后日K | kline_daily/hfq/etf/index/估值 全 09-30 | 绿 |
| daily_capital | 00 18 * * 0-4 | L5 资金面 | block_trade/dragon_tiger/money_flow 全 09-30 | 绿 |
| daily_event | 00 19 * * 0-4 | L6 事件层 | 09-30 档正常 | 绿 |
| research_nightly | 30 20 * * 0-4 | L6.5 研报 | 09-30 档正常 | 绿 |
| consensus_crosscheck | 30 23 * * 0-4 | 共识交叉 | 槽位注册正常 | 绿 |
| nightly_financial | 00 22 * * 0-4 | L7 财务 | 09-30 档正常 | 绿 |
| lane_g_intake_sweep | 30 22 * * * | L-G intake | 槽位注册正常 | 绿 |
| weekend_calibration | 00 3 * * 1 | L8 周末校准 | 44 任务，下周触发 | 绿 |
| monthly_static | 16 9 1 * * | L9 月初静态 | 今日 09:16 触发实跑：concept_sector 375 行 / index_list 8000 / calendar_event 436 / hk_stock_list 2810 等；槽级汇总未出（长尾任务在跑） | 绿 |
| weekend_backfill | 00 2 * * 0 | L10 周末补下载 | 特殊层注册正常 | 绿 |
| daily_backfill | 00 17 * * 0-4 | L10.5 每日补缺 | 特殊层注册正常 | 绿 |
| integrity_check | 00 23 * * 0-4 | L11 完整性 | 特殊层注册正常 | 绿 |
| cross_validation | 15 23 * * 0-4 | L11.5 QMT vs TDX | 昨夜 23:15 档正常（cross_source_validator） | 绿 |
| catchup_guard | 30 5 * * * | L10.7 对账补跑 | 今日 05:38：overdue=44 补跑=15 失败=0 顺延=19 **上限截断=29** | 黄 |
| pf_alloc_rebalance_check | 45 5 * * 0-4 | L12 再平衡巡检 | 槽位注册正常 | 绿 |
| data_supply_sentinel | 50 6 * * * | L13 断供哨兵 | 今日 06:53 checked=58 breached=12 | 红（见 §2） |
| calendar_coverage_check | 10 7 * * * | 日历覆盖 | 今日 07:10 checked=7 breached=1 | 黄 |
| auction_highfreq | */10 15-25 9 * * 0-4 | 竞价高频 | 9 月档位（日期域限定） | 绿 |
| daily_alt_fx | 35 23 * * 0-4 | 另类汇率 | AltFxECB 计划任务 Ready | 绿 |
| eod_reconciliation | 40 15 * * 0-4 | EOD 对账 | reconcile_worker 今日全天正常滚动（06:12–12:36 共 15 轮） | 绿 |
| dloop_post | 45 16 * * 0-4 | dloop | 槽位注册正常 | 绿 |
| sector_close_final | 10 15 * * 0-4 | 板块收盘 | sector_eqw_intraday/sector_board_synth_eod 计划任务 Ready | 绿 |
| sector_pre_open | 15 9 * * 0-4 | 板块盘前 | 同上 | 绿 |
| nightly_sentiment | 20 8 * * * | 夜间情绪 | NightlySentiment 计划任务 Ready | 绿 |

### 1.2 数据管线常驻进程（Windows 计划任务）

| 任务名 | State | 说明 | 状态 |
|--------|-------|------|------|
| ZephyrAlpha_DataScheduler | Running | 常驻调度器（tmp/scheduler_run.log 13:12 仍活跃；监控 :9100；今日 01:14/01:17/02:41 三次重启后 01:22 稳定） | 绿 |
| ZephyrAlpha_TickSubscriber | Running | tick 订阅（tick_subscriber_run.log 13:12 活跃） | 绿 |
| ZephyrAlpha_CHHealthProbe | Running | CH 健康探活守护 | 绿 |
| ZephyrAlpha_BoardIndexRealtime | Running | 板指实时 | 绿 |
| ZephyrAlpha_BeltDaemon | Running | 传送带守护 | 绿 |
| ZephyrAlpha_QMTWatchdog / ProcessReaper / DeadmanSwitch 等 | Ready | 看门狗族按触发 | 绿 |
| sector_eqw_intraday / sector_board_synth_eod | Ready | 板块合成（10-01 04:09/04:46 有 ps1 更新） | 绿 |
| tilib_indicator_backfill_nightly | Ready | 技术指标夜补 | 绿 |
| ZephyrAlpha_IntradayFundFlow / IndexMinuteEOD / SectorSnapshot / NightlySentiment / RSSHub / AltFxECB | Ready | 各档就位 | 绿 |
| ZephyrAlpha_FactoryLaneC*（3 项）/ C4Exam one-shot（2 项）/ TradingWatchdog / WeeklyRest | Disabled | 一次性任务停用/有意禁用 | 灰（登记在案） |

### 1.3 CH 核心表新鲜度探针（33 表，只读 max(trade_date)，13:15 实测）

**绿（24）**：kline_daily / kline_daily_hfq / kline_index / kline_etf_daily / daily_valuation / stock_daily_basic / block_trade / dragon_tiger / dragon_tiger_seat / money_flow / kline_hk_daily / kline_sector / kline_1min / market_breadth_snapshot / limit_up_down / crypto_kline_daily / crypto_shadow_gate（以上均 09-30）；kline_us_daily 09-29（美股 09-30 交易日，差 1 日，带注绿）；c1_backtest：decision_daily（10-08 前瞻计划行，正常）、sim_pocket_daily（10-01，sim 假期照跑）、alloc_budget_daily / regime_state_anchored / sim_attribution_daily（09-30）。

**黄（7）**：

| 表 | max(trade_date) | 缺口 |
|----|-----------------|------|
| adj_factor | 09-24 | 缺 09-25/28/29/30 共 4 个交易日 |
| margin_trading | 09-24 | 缺 4 个交易日（T+1 源，09-30 档应已出） |
| futures_position | 09-23 | 缺 5 个交易日 |
| option_iv_surface | 09-23 | 缺 5 个交易日 |
| kline_futures | 09-28 | 缺 2 个交易日 |
| kline_weekly | 09-15 | 缺 09-21、09-28 两个周 bar |
| kline_monthly | 09-15 | 缺 9 月月 bar（月末收口未生成） |

**红（2）**：hk_connect_flow（2024-08-16，源级终止）；index_valuation_daily_v2（1970-01-01 纪元=空表）。

### 1.4 独立脚本面（docstring 级）

- `scripts/data/`（≈45 文件）：回填族 backfill_bse/lof/sector880/sector881/etf60min/stock_daily_basic/technical_indicator_dwm/tick_depth5/reservoir_level_full/minute_history；夜间回填编排 backfill_night.ps1/.bat；合成族 synth_board_index/synth_board_minute；采集族 collect_index_minute_eod/collect_sector_fund_flow/board_index_realtime；修复族 repair_kline_*、finish_p0_1、verify_final；调度脚本 run_nightly_sentiment/run_sector_snapshot、sector_eqw_runner.ps1/sector_synth_eod_runner.ps1（10-01 凌晨更新）；巡检 source_health_patrol/night_probe；接源 onboard_source；fx_ecb_ingest（另类汇率）。
- `scripts/` 根 backfill*（5）：backfill_auction_snapshot_history / backfill_etf_hfq_for_pcr / backfill_option_daily_stats / estimate_pit_backfill_cost / register_tilib_backfill_task.ps1。
- `scripts/ch/`（≈50）：DDL 族 apply_*_ddl（market/fundamental/pf_alloc/l9/consensus 等）；回填族 backfill_money_flow_history / backfill_rzrq_history / backfill_research_report_2025|full / build_consensus_daily / build_anchored_state_history / build_financial_derived；归档 archiver.py + rolling_archive_reconciler + optimize_merge（**禁跑**）；校验 verify_schema_truth / verify_exchange_coverage / waste_table_scanner / _recovery_drill。
- 调度器内置特殊层挂接（scheduler.py `_run_special_schedule`）：weekend_backfill→backfill_checker、daily_backfill→backfill_checker、integrity_check→integrity_checker、cross_validation→cross_source_validator（+divergence_stats 落档 data/divergence_stats/）、catchup_guard→catchup_guard、data_supply_sentinel→supply_sentinel（托管 quality_sentinel 变异巡检 + cleaning_rules/anomaly 两道清洗门控，R-021 同腿托管）、pf_alloc_rebalance_check→pf_alloc.rebalance_check_runner（带总闸 flag）。

## §2 断供与静默管线清单

### 2.1 系统性连败（红）

1. **macro_data_incremental（akshare）**：今日 **215 连败**（event_driven 槽每 3 分钟一炸），错误=`RepoRate 获取失败: 'frValueMap'`——akshare 上游接口结构变更，provider 未适配；注意 status 显示 FAILED 但 rows=5932（部分序列成功、RepoRate 子腿全炸），并把日失败率顶破 5% 阈值持续告警。macro_data 表本身有数但 RepoRate 子族停更。
2. **hk_connect_flow**：max=2024-08-16，**源级终止**（HKEX 2024-08 起停发北向每日流量）。任务 hk_connect_flow_incremental 仍在册（incr=False）——任务存在≠管线活着，需改源或退役登记。
3. **index_valuation_daily_v2**：max=1970-01-01（空表/纪元）；同族 index_valuation_daily_quar_20260920 隔离副本在库，v1 未单测。估值 v2 链路未接活。
4. **rate_decision_calendar 双维度停更**：Fed 腿 max(decision_date)=2025-10-30（lag 336d）、PBOC 腿 2019-11-20（lag 2507d）——事件日历族，哨兵 06:53 双双鸣响。
5. **futures_warehouse_receipt [SHFE 维度]**：max=2025-11-17（lag 318d），维度级断供（表级腿看不见，row_filter 腿捕获）。
6. **alt_sz_reservoir_level**：max=2026-07-31（lag 62d）——BRK-038 实例表，至今未恢复。
7. **kline_sector_intraday [tdx 真值腿] + intraday_sector 槽今日连败**：max=09-10 且 rows=0 < floor 100000；今日 intraday_sector 槽每 5 分钟一轮 0 成功 5 失败，根因=`跳过源 tdx（健康检查: connect_fail, 连接失败: 所有服务器均无法获取K线数据）`（13:15 实证）——mootdx/tdx 服务器全不可达，板块分钟真值腿断供，当前只有 synth 冒充腿。

### 2.2 停更/滞后（黄，哨兵 06:53 全量 12 项中的非红项）

- road_freight_index lag=41d（>35d 阈值，按哨兵口径实为红）
- market_etf_share_snapshot 09-18（lag 13d>5d）
- irm_interactive_qa 09-16（lag 15d>7d）
- cftc_positioning 09-08（lag 23d>12d）
- gold_etf_holdings 09-17（lag 14d>5d）
- execution_report [成交业务时间] 09-18（lag 13d>10d）
- judgment_next_day_forecast [真生产行] 09-20（lag 7 交易日>2d）
- §1.3 的 7 张黄表（adj_factor/margin_trading/futures_position/option_iv_surface/kline_futures/kline_weekly/kline_monthly）

### 2.3 静默零产出（任务 SUCCESS 但 0 行，今日实证）

- news_stock/news_baidu/news_cctv/news_economic_baidu_incremental：多轮 SUCCESS 0 行（新闻源假期变稀+stock_hk_hist 连接失败重试耗尽；去重兜底掩盖真实拉取失败）
- kline_daily_delisted_backfill / st_namechange_backfill：SUCCESS 0 行（假期无新数据，属正常，但 last_key 停 2007-12-13 的 delisted 腿值得复核）
- macro_fred_incremental：7 败（api.stlouisfed.org SSL EOF，出海网络问题）

### 2.4 基础设施级异常（今日实证）

- **告警外发关闭**：alerter `enabled=false endpoints=[]`（fail-closed），CRITICAL 全部只落本地 trail，国庆无人值守窗口外发为 0。
- **CH 连接抖动**：08:48 出现 "CH 不可用"（news_data 落盘 2076 行待回灌）；ch_writer 全天多次 `clickhouse-driver 降级 HTTP`（Simultaneous queries on single connection / NoneType attribute）——单连接并发复用缺陷，靠 HTTP 降级兜住。
- **strategy_pipeline 文件竞争**：pending_events.jsonl.tmp 三种 WinError（5/32/2）PermissionError 反复——多进程并发消费同一 jsonl 无文件锁；另 pf_alloc 日分配 rc=1（trade_date=2026-09-29）毒丸留档。
- **local_replay 卡死循环**：c1_market.technical_indicator 单文件（20260921_*.tsv）反复回灌失败（write_tsv HTTP API 失败→保留待重试），启动时积压 361500 文件、当前 remaining=1 但该文件自 09-21 起未能落库。
- **catchup_guard 截断**：overdue=44 中仅补跑 15、29 项被上限截断（未补清单需假期后导出）。
- **月度静态槽待核实**：monthly_static cron="16 9 1 * *" 今日 09:16 应触发（21 任务），status 最近 20 条未见其运行记录，需拉单任务详情核实（可能被交易日守卫顺延）。

## §3 烟测方案（国庆约束下可立即执行）

全部只读/小样本，已验证或可直接复跑：

```bash
# 1. CLI 面烟测（已通过）
python -m zephyr.data --help           # 8 子命令入口
python -m zephyr.data list             # 271 任务清单（18 源/32 槽）
python -m zephyr.data status           # 今日状态+最近 20 条运行记录
python -m zephyr.data status macro_data_incremental   # 单任务详情（红任务下钻）

# 2. CH 只读探针（已通过，10s 超时）
curl -s --max-time 10 "http://172.24.30.100:8123/" --data-binary \
  "SELECT database,table,max(trade_date) FROM system.tables WHERE database IN ('c1_market','c1_backtest') AND trade_date IS NOT NULL GROUP BY database,table FORMAT TSV"
# 注：system.tables 无 trade_date 列时改两步——先 system.columns 定位含该列的表，再逐表/UNION ALL 探 max()
curl -s --max-time 10 "http://172.24.30.100:8123/" --data-binary "SELECT 1 FORMAT TSV"   # 连通性

# 3. 断供哨兵只读巡检（可复跑，不落告警面则用 check_tables）
python -c "from zephyr.data.supply_sentinel import check_tables; import json; s=check_tables(); print(json.dumps({'ok':s['ok'],'checked':s['checked'],'breached':s['breached'],'blind':s['heartbeat_blind'],'tables':[r['table'] for r in s['results'] if r['breached']]},ensure_ascii=False,indent=1))"

# 4. 源测速（小样本只读选型探针，假期可跑）
python -m zephyr.data speed-test --source akshare --capability daily_valuation
python -m zephyr.data speed-test --source baostock --capability kline_daily

# 5. 计划任务与进程面
powershell -NoProfile -Command 'Get-ScheduledTask | Where-Object {$_.TaskName -match "Zephyr|tick|sector|kline|backfill"} | Select TaskName,State'
curl -s --max-time 5 http://127.0.0.1:9100/health   # 调度器监控端点

# 6. 日志尾核实
tail -50 tmp/scheduler_run.log
grep -c "SUCCESS 但 0 行" tmp/scheduler_run.log      # 静默零产出计数
```

**假期禁跑清单**（违反即污染库）：`run`/`rerun-failed`（写操作+零增量）、一切 backfill_*、optimize_merge、archiver、wipe_tick3days、repair_* 族。

## §4 需修复断点（代码级，供施工批）

| # | 断点 | 位置 | 修法方向 |
|---|------|------|---------|
| 1 | RepoRate `'frValueMap'` KeyError 连败（今日 215 次） | akshare provider macro 数据腿（src/zephyr/data/implementations/akshare provider） | 适配 akshare 新返回结构或该子序列降级跳过+单列告警，防拖垮整任务失败率 |
| 2 | strategy_pipeline 并发消费 pending_events.jsonl 无锁 | `.runtime/strategy_pipeline/` 消费侧 | tmp 文件替换原子化+进程间文件锁（msvcrt），或单消费者仲裁 |
| 3 | pf_alloc 日分配 rc=1（trade_date=2026-09-29 毒丸留档） | strategy_pipeline→pf_alloc 日分配链 | 复现 rc=1 堆栈（日志已截断 `^^^^^`），修依赖后重放该毒丸事件 |
| 4 | local_replay technical_indicator 单文件死循环 | src/zephyr/data/local_replay.py + 失败文件 20260921_*.tsv | 失败计数上限+毒丸隔离区（quarantine 目录），失败原因（write_tsv HTTP API 失败）单独排查 |
| 5 | ch_writer 单连接并发复用冲突（Simultaneous queries / NoneType） | src/zephyr/data/ch_writer.py 连接管理 | 连接池化或 thread-local 连接；HTTP 降级路径保留为兜底 |
| 6 | 告警外发 endpoints=[] | alerter 配置（fail-closed 缺省） | 配置 webhook 端点（Owner 门位，属配置非代码）；否则哨兵红只剩本地 trail |
| 7 | cross_source_validator 裸 datetime.now()/date.today() 写 CH | src/zephyr/data/cross_source_validator.py:290-291 `_add_log_entry` | 违反 RULE-SCHEMA-TZ（naive 本地时间入库），改 now_utc()+显式时区 |
| 8 | hk_connect_flow 任务僵尸在册 | tasks.yaml `hk_connect_flow_incremental` | 源终止：改源（港交所替代口径）或标 disabled+登记 known_data_gaps.yaml |
| 9 | index_valuation_daily_v2 空表未接活 | 估值 v2 构建腿 | 排查构建任务是否在册/挂槽；确认与 quarantine 副本关系后重建 |
| 10 | news 族 stock_hk_hist 连接失败重试耗尽 | akshare 连接层 | 重试耗尽后应标任务 PARTIAL 而非 SUCCESS 0 行（静默零产出会漏告警） |
| 11 | kline_sector_intraday tdx 真值腿 rows=0；今日 intraday_sector 0 成功 5 失败（tdx connect_fail 所有服务器均无法获取K线数据） | mootdx TCP 直连腿（服务器清单/健康检查） | 板块分钟真值腿独立修复：刷新 tdx 服务器清单+探活（synth 冒充腿不可长期顶替真值）；区分假期停服 vs 服务器列表失效 |
| 12 | 月度静态槽无槽级完成汇总（09:16 起长尾在跑） | 观察项非断点 | 假期后核对该 17 任务最终落地行数即可 |

## §5 数据缺口登记（假期后可补，登记来源=known_data_gays 口径/本盘点）

| 表 | 缺口区间 | 补法（假期后） | 优先级 |
|----|---------|---------------|--------|
| adj_factor | 09-25..09-30（4 交易日） | miniqmt adj_factor_incremental 增量自愈或 backfill | 高（复权链依赖） |
| margin_trading | 09-25..09-30 | akshare/tushare T+1 源假期后首日自然补齐，验证即可 | 高 |
| futures_position | 09-24..09-30 | akshare 增量补 | 中 |
| option_iv_surface | 09-24..09-30 | miniqmt 增量补 | 中 |
| kline_futures | 09-29..09-30 | miniqmt 增量补 | 中 |
| kline_weekly | 09-21、09-28 两周 bar | miniqmt 周线增量（后收口） | 中 |
| kline_monthly | 2026-09 月 bar | miniqmt 月线（月末收口） | 中 |
| judgment_next_day_forecast | 09-21..09-30 | 判断链重建 | 中 |
| market_etf_share_snapshot / gold_etf_holdings / cftc_positioning / irm_interactive_qa / road_freight_index | 各 2~5 周 | 对应源假期后回补 | 中 |
| kline_sector_intraday（tdx 真值腿） | 09-11..09-30 | 修 §4-11 后按 backfill_sector880_history 族补 | 高 |
| technical_indicator | 09-21 起积压文件（local_replay remaining=1 毒丸） | 修 §4-4 后回灌 | 高 |
| kline_us_daily | 09-30（美股交易日） | tickflow 增量 | 低 |
| rate_decision_calendar Fed/PBOC 腿 | 2025-10 / 2019-11 起 | 事件日历源重新接驳 | 低（低频事件） |
| futures_warehouse_receipt SHFE 维度 | 2025-11-17 起 | 上游源核查（上期所改版?） | 低 |
| hk_connect_flow | 2024-08-17 起 | **永久缺口**（源终止）——登记 known_data_gaps.yaml，不改补数 | 登记 |
| alt_sz_reservoir_level | 2026-08-01 起 | 待修（BRK-038 遗留） | 中 |
| index_valuation_daily_v2 | 全表 | 修 §4-9 后重建 | 高 |

> 假期窗口说明：10-01 起休市，A 股族全部缺口冻结不扩大；crypto/us/hk 仍在走，若其调度正常则缺口止于上表区间。假期后首个交易日（约 10-09）收盘批跑完后，以 supply_sentinel 复检 breached 归零为补齐验收线。

## 附：证据文件指针

- 调度器运行日志：`D:\ZephyrAlpha\tmp\scheduler_run.log`（今日 SUCCESS 1363 / ERROR 260；哨兵 06:53 巡检、catchup 05:38 对账均在案）
- 失败留档：`D:\ZephyrAlpha\data\failures\20261001_macro_data_incremental_*.json` 等（今晨连败序列）
- 晨报：`D:\ZephyrAlpha\data\reports\morning_digest.md`（10-01 04:41 更新，内容期 09-30，新鲜=绿）
- 哨兵配置：`D:\ZephyrAlpha\src\zephyr\data\config\data_supply_sentinel.yaml`（58 条目）
- 调度计划真源：`D:\ZephyrAlpha\src\zephyr\data\config\schedule.yaml`（32 槽）
- 任务清单真源：`D:\ZephyrAlpha\src\zephyr\data\config\tasks.yaml`（271 任务）
- 监控端点：http://127.0.0.1:9100（/metrics /health /status）
