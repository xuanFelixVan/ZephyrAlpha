---
ttl: task_bound
title: "T1-B6 b 档数据源全网搜索卡：指标退役候选群三档处置（有源/无源结论+接入处方+CH live 普查）"
session: st-menu-t1b6-20260930
updated: 2026-09-30
---

# B6 三档指标处置 · b 档数据源全网搜索卡（sid=st-menu-t1b6-20260930）

> 总筹=st-nightsweep-chief-20260929｜矿卡真源=nb1_b6_indicator_retirement_groups.md（b_audit）
> 本卡是 b 档全网搜索的结论真源，兼记 a 档 D21 核查与 c 档三步验证证据。

## 0. Owner 本夜批复（留痕引用）

> ①b 档（无持续数据源档）：**先全网搜索有没有数据源，搜到就可以接入使用**，搜不到才冷归档；
> ②a 档批接线（CHIPS 5 条绑获利盘 D21）；③c 档批删（每条删前过实数据三步验证）。

三档映射（本车道执行口径）：**a 档**=CHIPS 5 条（IND-CHIPS-001~005，获利盘族）；**b 档**=residual-61 中非死工具伴生的零引用条目 38 条（矿卡 B 档 32+C 档 6，按族处置）；**c 档**=矿卡 A 档死工具伴生表 19 条（在册；DS-050 本就不在册）。族⑤ macro 15 归 B5 卡/车道（st-menu-t1b5），本车道零触碰；DS-101 cn_macro 同归 B5。审计外空壳 l2_tick（0 行）/edb_data（已不在 CH）分别留观/随 B15 通道。

## 1. CH live 普查（2026-09-30 夜，DatabaseService 只读）

**59 条零引用条目对应的物理表在 CH 五库（c0_meta/c1_backtest/c1_market/c3_fundamental/system）全部不存在**（system.tables 全库精确匹配，census 快照=t1b6_ch_census.json）。本地通道（depgraph/integrator_jobs/integrator_progress/zalpha_metadata 四 sqlite 库+data/ 文件树）同样零命中。即：**全部 61 表无一有存量数据行**，矿卡"zero_ref≠空表"的保守担心落地为"表根本未物化"，全部为 2026-08-13 批设计态登记（design_maturity=design，status=candidate）。

## 2. b 档逐族数据源全网搜索结论（WebSearch 实搜 6 轮，2026-09-30）

| 族 | 成员（条数） | 搜索结论 | 源/接入方式 | 免费/可持续 |
|---|---|---|---|---|
| F1 ashare 因子族 | DS-015~028（14） | **有源（派生型）** | 非"下载数据集"：WorldQuant Alpha101/191 族因子由 OHLCV 派生；开源参照=yli188/WorldQuant_alpha101_code、ta-cn(PyPI, Alpha101+191)、DolphinDB wq101alpha；内部活源=kline_daily 10,131,069 行 | 免费；算法参照可用、**代码禁商用禁抄**（sop_c§9） |
| F2 财务三表+指标族 | DS-087~090（4） | **有源且真身已活** | CH 活表继任：income_statement 346,176 行/balance_sheet 339,738/cashflow_statement 310,447/financial_indicator 386,437；外源备援=akshare 东财三表 stock_balance_sheet_by_report_em/stock_profit_sheet_by_report_em/stock_cash_flow_sheet_by_report_em+新浪 stock_financial_analysis_sina | 免费（akshare 无 token）；已活无需新建 |
| F3 财务事件族 | DS-091~093（3） | **有源且真身已活** | disclosure_plan 324,609/earnings_forecast 125,582/express_report 28,708；外源备援=akshare stock_yjyg_em（业绩预告）/stock_yjkb_em（快报）/stock_report_disclosure（巨潮预约披露） | 免费；披露季偶发不稳（社区实证），活表已承载 |
| F4 股本股东事件族 | DS-095 share_float、DS-096 holder_trade（2） | **有源且真身已活** | restricted_shares 10,208,142/share_unlock 30,449/share_change 190,580+**stock_daily_basic.float_share 7,107,404 行（current 至 2026-09-30）**；外源备援=akshare stock_restricted_release_queue_em/stock_share_hold_change_sse·szse·bse/stock_ggcg_em | 免费；**D21 流通股本数据腿实际已通**（见 §6） |
| F5 龙虎榜族 | DS-080 lhb_detail（1） | **有源（免费外源）** | CH 无 lhb 表=唯一无内部继任的外源型；接入=akshare `stock_lhb_detail_em(start_date,end_date)`（东财数据中心），社区生产管道在用 | 免费；接入处方见 §5 |
| F6 ST 状态族 | DS-085 st_status（1） | **有源且真身已活** | st_stock_list 424,304 行；外源备援=akshare stock_zh_a_st_em/tushare namechange（积分） | 免费（akshare 腿） |
| F7 申万板块族 | DS-102 sw_daily（1） | **有源且真身已活** | sector_constituent_sw_history 46,133+kline_sector_880 798,294；外源备援=akshare sw_index_daily（tushare sw_daily 需 5000 积分，劣后） | 免费（akshare 腿） |
| F8 图形族 | DS-077 renko、DS-078 point_figure、DS-079 kagi（3） | **有源（派生型）** | OHLC 派生图形，无外部数据源概念；开源参照=stocktrends（OHLC→Renko/PnF/Kagi）、mplfinance（type='renko'/'pnf'，kagi 需 stocktrends）；内部活源=kline_daily | 免费；需自研 transformations 施工（未建） |
| F9 daily_basic 族 | DS-086（1） | **有源且真身已活** | 物理真身=stock_daily_basic 7,107,404 行（turnover_rate/float_share/circ_mv/total_mv 全列在产，data_source 列在册）；登记名与物理名不一致属命名残留 | 已活 |
| F10 内部运行时族 | DS-073 ai_operator_decisions、DS-074 training_dataset（2，有源储备）；DS-002 ohlc_bar、DS-040 turnover_analyzer、DS-056 realtime_push_manager、DS-057 tick_data_manager、DS-070 portfolio_aggregate、DS-075 drawdown_metric（6，**无持续数据源**） | 混合 | DS-073/074：producer 存在（src/zephyr/ml_train/ai_operator、training_pipeline）=内部 pipeline 活，储备；其余 6 条 producer 路径全部不存在（src/zephyr/factor/ashare 系、factor/analysis、data/realtime_push_manager、data/tick_data_manager、pf_core/portfolio_aggregate、risk/drawdown_tracker 均缺）且现役继任已承载同语义（见 §4 无源清单） | — |

## 3. 三态结论（族粒度）

- **有源 32 条（9 族）**：F1~F9 全部+F10 之 DS-073/074。其中 18 条"真身已活"（F2~F4/F6/F7/F9+F10 之 2 条）——继任活表已在产，登记壳无需接线；14 条派生型/外源型（F1×14）+1 条外源型（F5）+3 条派生型（F8）出接入处方（§5）。
- **无源 6 条（F10 子集）**：DS-002/040/056/057/070/075 → **冷归档**（注册表条目 status→archived+successor 注记，禁物理删；留档清单已入 G:/zephyr_cold/retire_t1b6_20260930/）。
- **搜不到才冷归档**的分支本次仅命中上述 6 条；其余族搜到源且多数真身已活。

## 4. 无源冷归档清单（6 条，successor 注记）

| 条目 | 无源判据 | successor（现役承载） |
|---|---|---|
| DS-002 ohlc_bar | producer 缺（shared/contracts 符号无）；CH/本地零数据 | kline_daily（10,131,069 行，现役日 K 真身） |
| DS-040 turnover_analyzer | src/zephyr/factor/analysis/ 不存在；零数据 | stock_daily_basic.turnover_rate+kline_daily.turnover_rate |
| DS-056 realtime_push_manager | src/zephyr/data/realtime_push_manager/ 不存在；零数据 | c1_market.tick_data（3,879,811,361 行）/tick_depth_5（130,143,451 行）实时链 |
| DS-057 tick_data_manager | src/zephyr/data/tick_data_manager/ 不存在；零数据 | 同上 tick_data/tick_depth_5 活表 |
| DS-070 portfolio_aggregate | src/zephyr/pf_core/ 不存在；零数据 | c1_backtest.sim_pocket_daily/sim_attribution_daily/account_nav_daily 组合链 |
| DS-075 drawdown_metric | src/zephyr/risk/drawdown_tracker/ 不存在；零数据 | c1_backtest.sim_daily_report/account_nav_daily 回撤语义 |

## 5. 有源接入处方（含实施面核查）

**避让图核查（本夜实施=零）**：采集腿 config 唯一注册点=src/zephyr/data/config/tasks.yaml、Provider 实现=src/zephyr/data/implementations/akshare_provider.py——两处均为 st-zc9-lane-d 领地（#20 换源+#19 域在飞），禁碰。故本夜出处方不施工，移交采集腿 owner 班次；处方如下：

1. **F5 lhb_detail（优先，唯一纯外源型）**：tasks.yaml 增 task（provider=akshare，fetch=stock_lhb_detail_em，按日增量 start/end=trade_date 窗口）→ 入库 c1_market.lhb_detail（Date64+显式时区，RULE-SCHEMA-TZ）→ 消费方暂缺（L2 情绪原料储备）。
2. **F1 ashare 因子族**：不建议整族接线（14 张设计壳与现役 factor 链重叠）；若复活按开源公式参照自研 alpha 计算腿（WorldQuant 101/191 → 现役 kline_daily 输入），逐条走 CREATE-GUARD+capability_lookup，禁抄外仓代码。
3. **F8 图形族**：transformations 腿施工（renko/point_figure/kagi 由 kline_daily 派生，stocktrends 算法参照）；图形胞消费面挂 G-A 图形线（C6 点火窗后评估）。
4. **真身已活 18 条**：无需接线；本卡 §2 表即"源映射卡"（矿卡 B 档要求的 DDL+字段字典+源映射储备要求以此表+G:/zephyr_cold manifest 满足），后续任何"复活 DS-087 类"施工先读本表防止重建重复表。

## 6. a 档 CHIPS 5 条绑 D21 · 现状核查记录

- **D21 未就绪（2026-09-30 夜核查）**：获利盘接线面不存在——chip_distribution_engine.py（MOD-REGIME-005）无 winner 剖面（grep winner/获利/CYQ 零命中），末次实质变更=3dcfe9dd079（裁定#257④ 量纲修复回 trial）；TDM-E-L3-12-3 算法注仍挂"获利盘占比/单峰密集度语义未实现挂起"；机账 v3 五条 state=zero（SW14 诚实重判）。
- **数据腿新事实（加速未来接线）**：裁定#257④ 挂起时点的前提"需流通股本数据工程"已部分失效——stock_daily_basic.float_share 7,107,404 行、max(trade_date)=2026-09-30（当日）在产；CYQ winner 本不依赖流通股本（chips.py 换手率衰减迭代）。备援：akshare stock_cyq_em（社区筹码分布接口）可作对拍源。
- **执行**：CHIPS 5 条保持 candidate（不晋级不删），登记"**绑 D21 获利盘接线批文已下，待其就绪**"（就绪判据=chip_distribution_engine 增补 winner 剖面直调 chips.py::CYQ+TDM 注更新+机账幂等重跑回填，即 SW14 处方①②）。登记面=本卡 §6+99 报告 B6 行+T1B6 台账。

## 7. c 档 19 条 · 三步验证记录（逐条同判据，证据共通）

- **必要性**：19 表 CH 五库全库零命中（t1b6_ch_census.json，逐条 ch=[]）+本地四 sqlite 库与 data/ 文件树零命中 → 纯设计态壳，零实体数据。
- **真实性**：两通道独立读数一致为 0（CH system.tables 全库扫描 vs 本地 sqlite_master+文件树 glob），且 produces 路径缺失（barra/data_eng services/factor/mine 等目录不存在）或 B12 判装饰（backtest services 代码在而 result 表从未物化）。
- **可逆性**：data_asset_registry.yaml 在 git（revert 即整批回滚）+全 19 条目 YAML 原文快照+19 伴生 JOB 清单已存 G:/zephyr_cold/retire_t1b6_20260930/manifest.yaml；PG depgraph dataflow_datasets 无 40~65 号行（从未同步，零 depgraph 连坐）。
- 伴生 JOB-040~048/050~054/059~063 共 19 条同批退役（一表一 job 双死壳）；JOB-049（nan_processor，输出 DS-050 本就不在册）不在批文清单，留观。SRC-INTERNAL-001.provides_datasets 同步摘除 19 id。entry_counts 预存漂移（293 vs 实 294）随批修正为实数。

## 8. 台账指针

执行台账=.runtime/tmp/st-nightsweep-20260929/T1B6_ledger.yaml；census 快照=t1b6_ch_census.json；G 留档=G:/zephyr_cold/retire_t1b6_20260930/。
