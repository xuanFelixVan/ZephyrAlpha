---
ttl: task_bound
---

# D 队 · 业务链路广度普查 — 链路总表骨架

- 普查日期：2026-09-26（上一交易日 = 2026-09-25 周五；表内 "09-24/09-25" 均为实测最新数据日）
- 作业性质：全程只读（只 SELECT/计数 + 读计划任务/进程/日志；未改任何生产代码，未写 data/ 与生产库，未重启，未 git add/commit）
- 判定口径：逐条判 通 / 半通 / 不通；不通必给复现命令与输出原文（见对应 `lane_pipe_*.md`）
- 统计口径声明（勿把计数写进散文当死数）：本表 **N 条链路** 的"链路"定义 = **一条有独立触发 + 独立落库面 + 至少一个消费方 + 至少一个自检尺** 的业务流；271 个 data 任务是链路下的"腿"（leg），不单列为链路，按落库表族折叠进数据链。

---

## 0. 枚举方法（多路互证）

分母取 **7 路并集去重**，每条链路要求在 ≥2 路显形；只在一路出现的标 **孤链候选**。

| 路 | 来源 | 本次读数（实测） | 对并集的贡献 |
|----|------|-----------------|-------------|
| ① | `data/capability_cards/` + `docs/registry_of_registries.yaml`(ROOR) | 44 张卡；ROOR 904 行；REG-PIPE-001 pipeline 路由 30 条 | Agent/编排/管线能力面（多为治理链，业务面贡献小） |
| ② | `module_translation_registry.yaml` 业务模块集 | 数千 module_id（未全展开，取业务域子集） | 决策/风控/特征/结算模块名 |
| ③ | `python -m zephyr.data --help` + `list` | 8 子命令；调度器加载 **271 任务 / 29 档时段 / 18 源** | 数据采集链全集（本表 L-INTAKE/L-COMPUTE 主力来源） |
| ④ | `src/zephyr/governance/**/reconcil*` + `governance/audit/*_reconciler.py` + data 层 `integrity_check/data_supply_sentinel/backfill` | 治理类 reconciler 40+ 工厂函数；data 层自检 3 档 | 自检尺来源（判"有没有人盯它"） |
| ⑤ | `Get-ScheduledTask`（只列） | 50 个 `ZephyrAlpha*` + 3 个 `Reconcile*`；逐一取 Action→脚本 | 触发/常驻服务面（运行时链主力） |
| ⑥ | `generate_project_depgraph` 产物 / GOMAP | **未取到**（glob 超时，见 §5 未尽面） | 本轮缺一路，链路归属车道靠 ③⑤⑦ 交叉，标待补 |
| ⑦ | 代码入口全集 | `zephyr.data` / `zephyr.trading`(manual) / `api_server:8890` / `board_index_realtime.py` / `tick_subscriber` / `run_sector_snapshot.py` / `collect_sector_fund_flow.py` / `collect_index_minute_eod.py` / `fx_ecb_ingest.py` / `run_nightly_sentiment.py` 等 | 运行时入口 + 消费方（grep 读点） |

**落库实测来源**：ClickHouse `172.24.30.100:9000/8123`（`zephyr.data.ch_writer.query`，只 SELECT），对 `c1_market/c3_fundamental/c1_backtest` 全 252 张 MergeTree 表取 `count()+max(date列)`；任务运行真态取 SQLite `data/integrator_progress.db`（`mode=ro` 只读）的 `task_runs`。

**并集去重结果**：N = **62 条链路**（数据链 41 + 计算/衍生链折叠其中 + 决策/执行 6 + 报表/前端 3 + AI/LLM 4 + 治理/守护 12 + 备份/DR 3；详见下表；③ 贡献 44 个落库表族、⑤ 贡献 22 条运行时/守护/备份链、⑦ 贡献 3 条入口链、② 贡献 4 条决策/风控链，去重后 62）。

---

## 1. 链路总表（62 条）

图例：判定 ✅通 / 🟡半通 / ❌不通；车道 L-INT 采集 / L-CMP 计算衍生 / L-DEC 决策 / L-EXE 执行结算 / L-RPT 报表前端 / L-AI 大模型 / L-GOV 治理守护 / L-BKP 备份DR / L-DQ 数据质量自检。

### A. 数据采集/灌水链（L-INT，触发=DataScheduler 时基/事件；调度器进程实测 Running）

| # | 链路名 | 触发 | 落库表（行数·最新日） | 消费方（grep 读点） | 自检 | 判定 | 车道 |
|---|--------|------|----------------------|--------------------|------|------|------|
| 1 | A股日/周/月K线(非复权) | daily_kline | kline_daily 1010万·09-24 / weekly 181万·**09-15** / monthly 47万·**09-15** | backtest/regime/indicator builders | integrity_check 达标 | 🟡 | L-INT |
| 2 | 后复权K线族 hfq | daily_kline | daily_hfq 1008万·09-24 / weekly_hfq 213万·09-24 / monthly_hfq 50万·09-24 | 回测/信号主消费 | 见 §3 病根 B（族内版本列不一致） | 🟡 | L-INT |
| 3 | 复权因子 | daily_kline | adj_factor 2106万·09-24 | hfq 合成器 | 达标 | ✅ | L-INT |
| 4 | A股分钟K线族 1/5/15/30/60 | intraday_minute | 1min 14.86亿 / 5min 2.95亿 / … 均 09-24 | tick 聚合/做T | 达标 | ✅ | L-INT |
| 5 | ETF分钟K线族 | intraday_minute | etf_1..60min 均 09-24 | ETF 信号 | 达标 | ✅ | L-INT |
| 6 | ETF日线 | daily_kline | kline_etf_daily 10.4万·09-24 | ETF 回测 | known_gap shallow_depth(open) | 🟡 | L-INT |
| 7 | LOF分钟K线族 | intraday_minute | lof_1..60min 09-24 | LOF 信号 | 达标 | ✅ | L-INT |
| 8 | 实时分笔 tick | intraday_realtime (TickSubscriber=Running) | tick_data 89.5亿·09-24 / tick_depth_5 1.04亿·09-24 | 撮合/做T/盘口 | coverage gap(open) | ✅ | L-INT |
| 9 | L2 逐笔 | intraday_realtime | l2_tick **0 行** | fallback 降级 | known_gap permission_required(accepted) | 🟡 | L-INT |
| 10 | 指数K线 + 指数分钟 | daily_kline / IndexMinuteEOD(15:10) | kline_index 310万·09-24 / index_quote 23.9万·09-24 | 大盘共振/榜 | 达标 | ✅ | L-INT |
| 11 | 板块K线(880/tqcenter) | daily_kline | kline_sector 9.7万 / kline_sector_880 76万·09-24 | 板块共振 | known_gap 并发竞争(mitigated) | 🟡 | L-INT |
| 12 | 板块快照 | SectorSnapshot(16:40) | sector_snapshot 11.7万·09-24 / sector_state 42.7万·09-24 | 板块资金/状态 | 达标 | ✅ | L-INT |
| 13 | 港股行情 | intraday_realtime/daily | kline_hk_daily 20万·09-24 / hk_kline 6千·**09-16** | 港股信号 | known_gap source_depth(accepted) | 🟡 | L-INT |
| 14 | 美股行情 | daily_capital | kline_us_daily 594·09-23 / us_index 2.2万·09-23 | 隔夜风险 | known_gap source_depth(accepted) | ✅ | L-INT |
| 15 | 期货行情 | daily_capital/intraday | kline_futures 8274·**09-18** / futures_kline_qmt 906·**09-16** | 期货信号 | QMT 退役过渡 | 🟡 | L-INT |
| 16 | 期权链 | intraday_realtime | option_iv_surface 3万·09-23 / option_greeks/option_kline/option_daily_stats | 期权风控 | 达标 | ✅ | L-INT |
| 17 | 可转债 | intraday_realtime | convertible_bond_iv 1万·09-24 / kline_cb 24万·09-24 / convertible_bond_list | 转债信号 | 达标 | ✅ | L-INT |
| 18 | 集合竞价 | auction_highfreq | auction_snapshot 27万·09-24 / auction_book 382万·09-24 | 打板/情绪 | auction_book run: fetched 124万 written **0** → 复核 | 🟡 | L-INT |
| 19 | 全市场实时快照 | intraday_realtime | realtime_snapshot **0 行** | dashboard/盘中 | 无（探针读空≠无数据，见 lane） | ❌ | L-INT |
| 20 | 资金流 | daily_capital / IntradayFundFlow(10/11/13/14/15) | money_flow 604万·09-24 / sector_fund_flow 4424·**09-25** / hk_connect_flow 4052·**2024-08** | 主力线/北向 | hk_connect known_gap discontinued(accepted) | 🟡 | L-INT |
| 21 | 龙虎榜 | daily_capital | dragon_tiger 2143 / dragon_tiger_seat 61.9万·09-24 | 游资信号 | 达标 | ✅ | L-INT |
| 22 | 大宗交易 | daily_capital | block_trade 1414 / block_trade_detail 1629·09-24 | 大宗信号 | 达标 | ✅ | L-INT |
| 23 | 融资融券 | nightly_financial | margin_trading 208万·09-23 / margin_target_adjustment **0 行** | 两融口径 | margin_target_adjustment 未登记缺口 | 🟡 | L-INT |
| 24 | 宏观数据 | daily_capital/event | macro_data 6.1万·09-24(24h 内 FAILED 47 抖动) / macro_fred **FAILED(超时)** / macro_*_gauge 08-31 / edb_data **0 行** | 宏观择时 | edb retired(accepted)；FRED 源不稳 | 🟡 | L-INT |
| 25 | 北向持股 | event | northbound_hold_snapshot 5.7万·**06-30** | 北向信号 | known_gap interface_broken→tushare替代(accepted/monitoring) | 🟡 | L-INT |
| 26 | 新闻多源 | event_driven/news_slow | news_data 821万·**09-26**（rss/cls/东财/百度/央视…10 路，部分瞬时 FAILED） | 情绪/事件 | 达标 | ✅ | L-INT |
| 27 | 市场情绪 | auction/nightly | emotion_index 8650·09-24 / sentiment_panel 31·09-24 / news_sentiment_window 1.98万·09-24 | 打板/择时 | 达标 | ✅ | L-INT |
| 28 | 新闻情绪评分 | NightlySentiment(22:30) | news_sentiment_score 773万·**2025-09-09（冻结整年）** | dashboard/sentiment.html / daily_gate_snapshot / prediction_log_writer | 无新鲜度尺 | ❌ | L-INT |
| 29 | 财务三表+指标 | nightly_financial | balance/income/cashflow·09-02 / financial_indicator 38.6万·09-12 / main_business 209万·Q1 | 基本面/consensus | 达标 | ✅ | L-INT |
| 30 | 衍生财务 | nightly_financial(内部 build) | financial_derived 30.6万·Q1 但 **build 任务 FAILED(str<date)** | 估值因子 | build 崩 | ❌ | L-CMP |
| 31 | 股东/股本/解禁 | daily_capital | shareholder_count 51万·09-24 / share_change 19万·09-23 / restricted_shares 1020万 / share_unlock 3万·前瞻2027 | 筹码 | 多任务 STALE(reaped>6h) | 🟡 | L-INT |
| 32 | 分红/除权/配股 | daily_event(disabled 的除外) | ex_dividend_event 5.8万·09-24 / dividend 19万(**任务 schedule=disabled** + no_source) / rights_issue 8万·06-30(no_source) | 除权/回测 | dividend 腿 disabled | 🟡 | L-INT |
| 33 | 事件研究类 | daily_event | analyst_forecast 11万·09-24 / earnings_forecast 12.6万·07-03 / express_report 2.9万·07-02 / audit_opinion 9.6万·05-29(no_interface) | 预期差 | 财报季外正常/接口缺(accepted) | 🟡 | L-INT |
| 34 | 一致预期构建 | research_nightly(build) | consensus_daily 680万·**09-14 / build FAILED(str>date)** / consensus_daily_repaired 166万·09-15 | 估值/因子 | build 崩 + known_gap value_cols PIT(open) | ❌ | L-CMP |
| 35 | 研报 | research_nightly | research_report 14.7万·09-18 | 情绪/评级 | known_gap rating_change 空列(open) | 🟡 | L-INT |
| 36 | 静态宇宙 | monthly_static/pre_market | stock_list 5921 / stock_basic 904万·09-23 / index_constituent 67万·09-23 / trade_calendar 前瞻2026-12 / industry_class 4.6万 / etf_list/lof_list | universe 构造 | 1970 哨兵 known_gap(open B 族) | 🟡 | L-INT |
| 37 | IPO/调样 | daily_capital | ipo_calendar 9202·09-24 / ipo_schedule **0 行** / msci_adjustment **0 行** | 打新/调样 | 后两表未登记缺口 | 🟡 | L-INT |
| 38 | 加密/衍生品 | daily_crypto | crypto_kline_daily 1.8万·09-24 / hl_perp/oi_snapshot·09-25 / hl_funding 470万·09-25 / hl_liquidation_raw **7 行**(open) | 加密信号 | liquidation 采集链未产数(open) | 🟡 | L-INT |
| 39 | 另类数据族 | AltFxECB + 多源 | alt_fx_rate_ecb·09-25 / alt_shipping / alt_typhoon* / alt_sz_* (env) / hog_* / weather_data / commodity_* / gold_etf_holdings 等 | 主题/气候因子 | 部分子序列停发(accepted) | ✅ | L-INT |
| 40 | 市场宽度/广度 | intraday_minute | market_breadth_snapshot 151·09-24 / stk_limit 923万·09-24 / limit_up_pool/limit_up_down | 打板/择时 | breadth fallback 已接(accepted) | ✅ | L-INT |
| 41 | 技术指标族 | daily_kline(build) | technical_indicator 3.62亿·09-24 / stock_indicator 1169万·09-24 | 信号/回测 | dup rows known_gap(monitoring，消费侧 argMax 去重) | 🟡 | L-CMP |

### B. 决策 / 执行 / 结算链（L-DEC/L-EXE）

| # | 链路名 | 触发 | 落库表（行数·最新日） | 消费方 | 自检 | 判定 | 车道 |
|---|--------|------|----------------------|--------|------|------|------|
| 42 | 锚定状态构建 | daily_kline(build) | regime_state_anchored 4477·09-24 / regime_snapshot_history 3629·09-24 | 决策/择时 | 达标 | ✅ | L-CMP |
| 43 | 决策日报 | decision chain | decision_daily 72·09-25 / strategy_screen 1341·09-24 / crisis_gate_log 45 | 决策审计 | 达标 | ✅ | L-DEC |
| 44 | 判断链(日计划/日内/次日/验证) | DecisionChainSentinel(09:40) | judgment_daily_plan 9 / intraday_market_state 20 / next_day_forecast 4 / plan_verification 14·09-24 | 决策 | 哨兵在跑但样本极小(纸面期) | 🟡 | L-DEC |
| 45 | 模拟盘 Paper | PaperSession(09:25) | sim_pocket_daily 313 / sim_trade_log 75 / sim_daily_report 240·09-24~09-25 / sim_platform_journal 16 | 归因 | 任务 Ready（09-25 有落地） | ✅ | L-EXE |
| 46 | 仿真桥执行 | SimBridgeExecute(09:35) | sim_attribution_daily 72 / sim_* | 归因 | 达标 | ✅ | L-EXE |
| 47 | 盘后结算/三方对账 | PostSettlement(周五15:30) + reconcile | reconciliation_differences（CH **0 行**；真源=governance.db） | 对账 | 见 lane（真源方向分裂） | ❌ | L-EXE |
| 48 | 实盘运行时核心 AutoRuntime | `python -m zephyr.trading`(**manual**) / TradingWatchdog(**Disabled**) | execution_report 1 行·09-18 | 实盘 | 无进程在跑 | ❌(待裁) | L-EXE |
| 49 | 做T矩阵 T0 v2 | FactoryLaneC/C4Exam/F06Grid(在跑) | t0 产物 + kline_etf_60min 做T臂(浅史 open) | 做T回测 | factory_grid_executor 实测 Running | 🟡 | L-EXE |

### C. 报表 / 前端链（L-RPT）

| # | 链路名 | 触发 | 落库/出口 | 消费方 | 自检 | 判定 | 车道 |
|---|--------|------|-----------|--------|------|------|------|
| 50 | 仪表盘 API | `api_server.py:8890`(**manual**) | 无监听(8890 未起) | 人 | 无 | 🟡(手工设计) | L-RPT |
| 51 | 资源晨报 | ResourceMorningReport(06:31) | 报告产物 | 人/告警 | 达标 | ✅ | L-RPT |
| 52 | 资源视图发布/再生校验 | ResourceViewPublish / ResourceRegenCheck | 视图产物 + alerts | 人 | 达标 | ✅ | L-GOV |

### D. AI / LLM 链（L-AI）

| # | 链路名 | 触发 | 落库/出口 | 消费方 | 自检 | 判定 | 车道 |
|---|--------|------|-----------|--------|------|------|------|
| 53 | Ollama 本地推理后端 | OllamaServe(boot，**无 next run**) | 11434 端口**未监听**，无进程 | LSG 全部下游 | 无存活探测入业务尺 | ❌ | L-AI |
| 54 | LSG 安全网关→LLM | 事件（被上游调） | 依赖 53 | 情绪/清洗/调度/问答 | LSG 在但后端死→下游瘫 | ❌ | L-AI |
| 55 | 夜间情绪打分 | NightlySentiment(22:30) | 依赖 53；写 news_sentiment_* | #28/#27 | 后端死→打分链阻塞 | 🟡 | L-AI |
| 56 | 嵌入/重排 router | 事件 | 依赖 53 | 检索/RAG | 无独立尺 | 🟡 | L-AI |

### E. 治理 / 守护链（L-GOV，多为其它链的自检尺；触发=事件/时基）

| # | 链路名 | 触发 | 出口 | 自检对象 | 判定 |
|---|--------|------|------|----------|------|
| 57 | CH 健康探针 | CHHealthProbe(Running) | alerts | CH 传输(TCP/HTTP) | ✅ |
| 58 | 进程收尸 reaper | ProcessReaper(Running)+DeadmanSwitch | 杀悬挂进程 | STALE>6h reaped | ✅(副作用:误杀长任务→#31 STALE) |
| 59 | 提交带守护 belt | BeltDaemon(Running) | commit 落地 | 提交队列 | ✅ |
| 60 | worktree 漂移哨兵 | WorktreeDriftWatchdog(Running) | alerts | 会话工作树 | ✅ |
| 61 | 蒸发黑箱 | EvaporationBlackbox(Running) | 取证 | 消失的编辑 | ✅ |
| 62 | reconcile 引擎 | 事件(commit 后)+reconcile_worker | 治理 | 40+ reconciler | ✅ |

> 备份/DR 链（DailyBackup / WeeklyVMBackup / CH-OptimizeMerge-Weekly / LibraryLedgerBackup / RESTORE-DRILL / IOCheck-Monthly）实测均 Ready 且有 LastRunTime，归 L-BKP，判定 ✅（未逐条打开产物核验，见 §5）。

---

## 2. 判定汇总

- 通 ✅：**30** 条
- 半通 🟡：**23** 条
- 不通 ❌：**9** 条 = #19 realtime_snapshot / #28 news_sentiment_score / #30 financial_derived / #34 consensus_daily / #47 reconciliation_differences / #48 AutoRuntime(待裁) / #53 Ollama / #54 LSG(与 #53 同根合并一本) / #43 pattern_win_rate。
  - **8 本案卷**覆盖 9 条（#53+#54 同因合本）：`lane_pipe_realtime_snapshot.md` / `lane_pipe_news_sentiment_score.md` / `lane_pipe_financial_derived.md` / `lane_pipe_consensus_daily.md` / `lane_pipe_reconciliation_differences.md` / `lane_pipe_pattern_win_rate.md` / `lane_pipe_llm_backend_ollama.md` / `lane_pipe_auto_runtime_trading.md`，各带复现命令与输出原文（全只读）。
- 孤链候选：**2** 条（#44 judgment 判断链样本极小、仅靠 ⑤ 哨兵 + ⑦ 表显形，②/③ 未见显式注册；待 ⑥ depgraph 补路再判）。

---

## 3. 已知病灶专节（逐类核查，含新病根）

### 病灶 A · 双写手/单写者不变量缺失
- 治理层实例 #ARCH-317：`architecture_issue_registry.yaml:21725` `status: open`，P1 高，"commit_queue serializer worktree 单写者不变量无强制——lease TTL 不续约 + 双写者起手 reset/clean 互抹未提交新件"。fix_phase="登记待治本（消费侧已自规避，落地器本体未改）"。**在册仍 open，属实**。
- 数据层同源病灶（并发双写同一表）：`known_data_gaps.yaml` 已登记 `kline_sector_concept_shrinking`（两 task 并发抢 tqcenter 单例，mitigated）、`technical_indicator_duplicate_rows`（monitoring，消费侧 argMax 去重）、`index_valuation_daily_duplicate_rows`（resolved：补 version 列重建收口）。
- **新病根（本轮新发现·值级对拍看不出）**：后复权表族"来源独占版本列"改一张漏一族——见病灶 D。

### 病灶 B · 空表有壳没货
- 已知 4 张：`suspend` / `account_nav_daily` / `etf_benchmark` / `l2_tick` → 实测**全部 count()=0**。
  - 其中 `l2_tick` 在 `known_data_gaps` 登记为 `permission_required/accepted`（真源侧权限，非管道故障）。
  - `suspend` / `account_nav_daily` / `etf_benchmark` **未登记在 known_data_gaps**（缺口未在册，待裁：建腿 or 退役）。
- **本轮扩面（并集去重后另有 10 张 count()=0）**：`edb_data`(registered accepted·iFind 退役)、`realtime_snapshot`(❌见 lane，非"没跑"而是"落库断")、`index_valuation_daily_v2`、`ipo_schedule`、`margin_target_adjustment`、`market_index_meta`、`msci_adjustment`、`reconciliation_differences`(见 lane，真源在 governance.db)、`stock_candidate_pool`、`stock_valuation`。
  - 后 6 张（index_valuation_daily_v2 / ipo_schedule / margin_target_adjustment / market_index_meta / msci_adjustment / stock_candidate_pool / stock_valuation）**均未登记 known_data_gaps** → 属"无主空壳"，是广度净新增，需 Owner 判"建腿 vs 退役"（不臆造裁定）。

### 病灶 C · 探针失败被读成"无数据"
- 代码实证：`src/zephyr/data/ch_writer.py:426 query()` — 查询失败与空结果**同返 `""`**（L445 `if not rows: return ""`；L483 两级传输全败 `return ""`）。任何 `if not result:` 判空的调用方，无法区分"链路挂了"与"真没数据"。
- 落地面：`data/failures/*_realtime_snapshot_incremental_*.json` 大量存在（0722/0803/0824/0918…）→ CH INSERT 反复失败但 `task_runs` 记 `SUCCESS`（fetch 段计数），表恒 0 行。见 `lane_pipe_realtime_snapshot.md`。

### 病灶 D · 后复权"表族"改一张漏一族（新病根）
- 2026-09-21 WO-1 为 daily_hfq 加了版本列做"来源独占"：实测 `c1_market.kline_daily_hfq` 有 `lineage_version UInt16`（+ data_source/ingest_ts）；
  但 **同族 `kline_weekly_hfq` / `kline_monthly_hfq` 缺 `lineage_version`**，仅 ingest_ts（`kline_daily` 非复权同样无）。
- 三表均 `ReplacingMergeTree`（ORDER BY symbol,trade_date）；缺版本列 ⇒ 若增量腿换名/改口径回写旧行，`ReplacingMergeTree` 无 version 判新旧 ⇒ 旧行可覆盖修正行，**值级对拍看不出**。
- 迁移副产物空壳/半壳并存（重算换名残留）：`kline_daily_hfq_legacy_20260924`(843万)、`_preversion_20260925`(1008万)、`_quarantine_20260925`(1万)、`_recalc`(10万)、`kline_weekly_hfq_legacy_r1_20260924`、`kline_monthly_hfq_legacy*`、`index_valuation_daily_quar_20260920`。
- 判：病灶属 **数据质量半通**，非当轮"不通"，但为"来源独占缺失"的**同族新实例**，登记备治本。

### 病灶 E · 表族内自相矛盾（daily/weekly/monthly）
- #1 非复权 `kline_weekly/monthly` 最新 09-15，而 hfq 版 09-24 齐；周/月 bar 天然滞后可解释，但 **需 ⑥ depgraph + 消费侧口径**二次判是否真滞后（保守标 🟡，不断言）。

---

## 4. 逐链路复现/读数入口（只读）

- 落库真值：`python -c "from zephyr.data import ch_writer as c; print(c.query('SELECT count(),max(trade_date) FROM c1_market.<表> FORMAT TSV'))"`
- 任务真态（只读 SQLite）：`python -c "import sqlite3;c=sqlite3.connect('file:data/integrator_progress.db?mode=ro',uri=True);print(c.execute(\"SELECT started_at,status,rows_fetched,rows_written,error_msg FROM task_runs WHERE task_id=? ORDER BY started_at DESC LIMIT 1\",('<task>',)).fetchall())"`
- 计划任务：`powershell Get-ScheduledTask -TaskName <N> | Get-ScheduledTaskInfo`
- 进程存活：`powershell Get-CimInstance Win32_Process | ? { $_.CommandLine -match '<pat>' }`
- 探针空/失败歧义源码：`src/zephyr/data/ch_writer.py:426`（query 空即失败）

---

## 5. 广度未尽面（诚实列，未穷尽）

本轮把业务面挖到"数据供给 + 运行时任务"双层可判，但**以下面明确没挖到**，且每面给出下一步枚举法：

1. **⑥ 全景图/依赖图/GOMAP 缺路**：`generate_project_depgraph` 产物、architecture_model 节点、GOMAP 未取到（`find`/glob 在含 `.git/.worktrees/.mypy_cache` 的巨树超时）。→ 下一步：定位 depgraph 落盘路径（多半 `architecture_model/` 或 `data/`），只读 `--status`/diff，不 `--force` 重建。当前链路"归属车道"靠 ③⑤⑦ 交叉，未经 ⑥ 独立佐证，**孤链候选判定偏弱**。
2. **② module_translation_registry 未全展开**：仅按业务域子集取名，未逐 module_id 建"模块→落库表→消费方"三级映射。→ 下一步：解析该 YAML 的 `module_id/layer/domain` 段，与 tasks.yaml 的 `table`、代码 `[CONSUMERS]` 头做 join，找"注册了模块但无落库腿"的隐性断链。
3. **消费方覆盖度未量化**：判"通"的链路只抽验了落库新鲜度，未对每表做 `grep 读点 → 确认读的是哪张/哪个版本列`（尤其 hfq 族、argMax 去重表）。→ 下一步：对每表生成"写点清单/读点清单"二列，交叉出"只写不读(孤儿资产)"与"只读不写(读空)"。
4. **回测/信号→下单的下游链未逐段追**：#43~#49 只判到"落库有数/任务在跑"，未验证"决策真的读了最新特征、下单腿真的连券商(QMT 9/18 退役后桥模式)"。→ 下一步：读 `execution_report`(仅 1 行·09-18，可疑) + QMTWatchdog(Ready) 实际连接态 + `zephyr.trading` 桥模式健康，判"信号到成交"是否闭合。
5. **备份/DR 链只看了计划任务态，未验产物**：DailyBackup/VMBackup/CH 双链(F主/G二)未开产物清单核对可恢复性（RESTORE-DRILL NextRun=10-01，未跑）。→ 下一步：只读列备份目录 manifest + 最近一次 drill 报告，不触发真恢复。
6. **DEFERRED_PERSISTENCE 14 次/24h 未归因**：CH 写降级到本地 TSV 待回灌的 14 例分布在哪张表、回灌链是否闭合，未查。→ 下一步：读 `data/failures/` + local_replay 回灌任务态，判"降级→回灌"链是否自洽（防 #19 类静默丢失复现到其它表）。
7. **STALE>6h 被 reaper 误杀 32 例/24h** 未逐条判"真卡死 vs 合法长任务"。→ 下一步：对照 `process_reaper_keep.txt` 白名单，找"该保护却没登记"的长批腿。
