---
asset_id: "DOC:docs/_working/decision_map_campaign/12_data_universe_census.md"
ttl: "task_bound"
doc_type: "census"
---

# 12 · 数据面宇宙完整性总普查（2026-09-24）

- 班次：数据面宇宙总普查班（Owner 问句起源："板块为什么只有 469 个"——通达信 881xxx 行业族 0 行从未采补，举一反三全仓普查）
- 方法：CH 只读轻查询（count/min/max/uniqExact 级，未拉任何全表明细；大表用分区裁剪取最新日 distinct）+ 真源登记册比对（`src/zephyr/data/config/known_data_gaps.yaml` 1418 行全读 + `docs/_working/ultimate_library/ulib3b_supply_relationship_ledger.md` S1-S46 + 图书馆 `docs/library/data.md` 336 表卡 + `tasks.yaml` 接线抽查）
- 口径：行数=FINAL 视角（ch_reader 自动注入 FINAL）；"新鲜度=到今天了吗"以 2026-09-24（周三，交易日）为基准日
- 五问：①行数/范围/最新日（新鲜度）②宇宙完整性（实有 vs 应有）③登记状态（known_data_gaps + 图书馆）④更新机制 ⑤缺口卡编号（DU-xx）

## 0. 469 之谜解答（普查起点）

**结论：469 不是"板块少了"，而是 kline_sector_880 表天生只装 880 家族。通达信 881xxx 行业族（128 个板块）在该表 0 行，从未采补。**

实测号段分布（`SELECT DISTINCT sector_code FROM c1_market.kline_sector_880`，469 码全量分组）：

| 号段 | 语义 | 库内数 | 去向 |
|---|---|---|---|
| 8800xx | 大盘/组合指数 | 11 | kline_sector_880 有 |
| 8802xx | 地区板块 | 32 | kline_sector_880 有 |
| 8803xx/8804xx | TDX 裸码行业（61+71=132） | **0** | 仅 kline_sector_intraday 有（tdx 真值 727 实证）；日线/成分两表均缺（known_data_gaps `sector_constituent_8803_8804_missing` 已登记 open） |
| 8805xx-8809xx | 概念/风格 | 426 | kline_sector_880 有 |
| 8810xx-8814xx | 通达信行业族 | **0** | 在兄弟表 kline_sector 有（128 个：8810=23/8811=25/8812=30/8813=26/8814=24），kline_sector_880 从未采集 |

四张板块表宇宙对照（同日实测）：

| 表 | uniq(板块) | 8803/8804 | 881 行业族 | 备注 |
|---|---|---|---|---|
| kline_sector_880 | 469（近 5 日 468/日） | 0 | 0 | tqrcenter 880 capability，"469"即此表 |
| kline_sector | 596（594/日） | 0 | 128（8810-8814） | tqcenter 全量 capability |
| kline_sector_intraday | 727 | 132（裸码） | 128 | mootdx 真值 09-08=727 板块；通道 09-11 死，synth 接管（已登记） |
| sector_code_name_map | 469 | 0 | 0 | 名称映射侧同样缺 881 族与 8803/8804 |

**"应有数"判定：库内硬真值 = 727**（kline_sector_intraday mootdx 分钟真值，09-08 实测 727 板块/日）。Owner 所引外部"800+"口径无精确外部快照可对照（通达信板块目录随概念扩容浮动、无公开固定清单）——如实登记为"外部真源不可精确对照，以库内 tdx 真值 727 为准绳"。469 = 727 − 132（8803/8804 行业）− 128（881 行业）+ 2（8803/8804 各自重复计入后的口径差），即**缺 260 个行业板块（35.8%）**。

下游连带：`sector_state`（板块情绪态）uniq(sector_code)=469——同源同病，881 行业维度的情绪态从未产出；`sector_code_name_map` 名称映射 881 族=0 行。881 族日线数据本体在 kline_sector 是活的（594/日满量），**缺的是 880 表通道与名称映射**，补采=capability/映射扩面，非从零挖源。

## 1. 总普查表（每表一行五问）

> 排序按域分组；行数未标 FINAL 的取 system.tables total_rows（仅计数用）。"应有数"有外部真源的写对照，无真源的如实写"无外部真源可对照"。

### 1.1 行情主族

| 表 | ①行数/范围/最新日 | ②宇宙完整性 | ③登记 | ④更新机制 | ⑤卡 |
|---|---|---|---|---|---|
| kline_daily | 10,108,049｜1990-12-19..09-24｜**当日到** | 最新日 5,559 只（0=1491/3=1405/6=2314/8=5/9=344）vs 应有 5,562（stock_basic 09-15 快照实证，含北交所 343）→ **完整** | 图书馆在册；北交所缺口已 resolved（09-15 闭环） | akshare/QMT 自动日更 | — |
| kline_daily_hfq | 10,084,158｜同窗｜当日到 | 与 kline_daily 同宇宙 | 在册 | 自动（前复权派生） | — |
| kline_index | 3,101,185｜1990-12-19..09-24｜当日到 | 1,097 只指数；399106 涨跌家数两列 07-03 起断（消费侧 EQW_ALLA 补位） | known_data_gaps `kline_index_399106_breadth_stale` accepted | 自动 | 已登记 |
| kline_sector_880 | FINAL 437,204｜2020-03-17..09-24｜**当日到** | **469 vs 727 真值**：881 行业族 0 行+8803/8804 行业 0 行，缺 260 板块（35.8%） | 312 日断档已补（completed）；行业族缺口**未登记**→本普查 DU-01 | tqcenter 自动 16:30 | **DU-01** |
| kline_sector | FINAL 78,785｜2025-07-18..09-24｜当日到 | 596 vs 727（缺 8803/8804 裸码 132）；594/日满量 | 并发竞争已修（09-15）；8803/8804 已登记 open | tqcenter 自动（已串行错峰） | DU-02 |
| kline_sector_intraday | 10,436,356｜2026-07-20..09-22｜真值止 09-10 | 727=宇宙真值本体；09-11 起 mootdx 死，synth 行接管 | `kline_sector_intraday_tdx_dead` accepted | tdx 死→方案 J synth | 已登记 |
| kline_1min | 1,486,013,551｜2021-09-01..09-24｜当日到 | 最新日 5,559 只全量；2021-08 前深史在冷归档（F:）未挂回 | `cold_archive_minute_kline_e_drive` open | 桥模式自动 | 已登记 |
| kline_5/15/30/60min | 294.9M/98.6M/49.2M/24.6M｜2021-09-01..｜当日到 | 最新日各 5,559 只 | 在册 | 自动 | — |
| tick_data | 8,953,165,904｜2025-01-02..09-24｜当日到 | 最新日 7,931 标的（stock 5413/BJ 349/ETF 1168/CB 163/index 554/LOF 374）；2022-2024 全段不在库；**09-21 准零日 14,567 行（邻日 2,700 万+）→ DU-04 新发现** | 2022-2024 段已登记 open；09-21 **未登记** | 桥 tick 实时+回补 | 已登记+**DU-04** |
| tick_depth_5 | 103,509,452｜2026-07-24..09-24｜当日到 | 7,931 标的；bulk 覆盖仅 4-9 日深样本 | 已登记（tick_coverage 条目） | 桥派生自动 | 已登记 |
| stk_limit | FINAL 9,209,835｜2015-01-05..09-24｜当日到 | 5,826 只/日，涨停价真源（S16 三级解析链 100% 验证） | 在册，无缺口 | akshare 自动 | — |
| adj_factor | 21,055,072｜1990-12-19..09-24｜当日到 | 7,848 符号（含退市史） | 在册 | 自动 | — |

### 1.2 板块/情绪/资金族

| 表 | ①行数/范围/最新日 | ②宇宙完整性 | ③登记 | ④更新机制 | ⑤卡 |
|---|---|---|---|---|---|
| sector_state | FINAL 426,256｜2022-09-01..09-23｜T-1 到 | **469 板块=同 880 表宇宙**，881 行业维度情绪态从未产出 | 同源 DU-01 连带 → DU-02 | internal 派生（daban 体系） | **DU-02** |
| sector_code_name_map | 469｜09-24 晨刷新 | 881 族=0、8803/8804=0（映射侧残缺） | 未登记→DU-02 | 生成器产出（07:16 当日跑过） | **DU-02** |
| sector_list | 5,217｜单日快照 09-03 | THS 全桶（概念+行业大清单），非 880/881 体系 | 在册 | akshare 快照 | — |
| sector_constituent | FINAL 95,124｜2026-07-22..09-03 | 595 板块成分（880 族+881 行业），8803/8804 缺 | `sector_constituent_8803_8804_missing` open | 自动 | 已登记 |
| sector_constituent_snapshot | 380,496｜09-14..09-24｜当日到 | 同上 595 | 同上 | 自动 | 已登记 |
| sector_fund_flow | FINAL 3,974｜09-15..09-24｜当日到 | 90 个 THS 行业；历史不可回补（THS 仅即时口径） | `sector_fund_flow_empty` mitigated | 计划任务 5 时点快照 | 已登记 |
| emotion_index | FINAL 8,647｜1991-06-10..09-24｜**当日到** | close_final 全史 8,614 个交易日+盘中 pre_open/auction 自 09-01。**任务简报"仅 143 日"未复现——该数字已过时**（疑为 news_sentiment_window market 级旧口径 143→现 185） | 在册无缺口 | internal 聚合（盘后批 15:10） | 勘误 |
| news_sentiment_window | FINAL 19,820｜2026-02-24..09-23 | market 级 185 日在产；**symbol 级止 2026-08-20（120 日）→ DU-06 新发现** | 接线已修（completed）仅覆盖 market 腿 | nightly cron 20:08 | **DU-06** |
| news_sentiment_score | 7,733,898｜**止 2025-09-09** | 原始 news_data 活到 09-25，打分链停摆 1 年+→ **DU-05 新发现** | **未登记** | 断（任务活但拉不到/不再跑，同 reservoir 盲区型） | **DU-05** |
| news_data | 8,254,371｜..09-25｜当日到 | 新闻原始流健在 | 在册 | 自动 | — |
| market_breadth_snapshot | 151｜08-24..09-24｜当日到 | 1 快照/日 | 在册 | 自动 | — |
| limit_up_down | FINAL 4,942｜2026-07-20..09-24｜当日到 | 49 交易日浅史（外部无免费全史源可对照） | 在册 | akshare 盘中自动 | DU-14 |
| limit_up_pool | 1,077｜09-01..09-24 | 54 日浅史 | 在册 | 自动 | DU-14 |
| daban_board_event | FINAL 1,454｜09-01..**09-22** | 09-23/24 两日未见（涨停派生腿滞后观察项） | S21 台账记断供中 | 派生 | DU-14 附注 |
| money_flow | FINAL 5,954,327｜2021-01-04..09-24｜当日到 | 5,778 只/日；2021 起六年深史逐年完整（1.06M→1.23M/年） | 在册无缺口 | akshare 自动 | — |
| margin_trading | FINAL 2,065,857｜2024-09-02..**09-18** | **最新日停在 09-18，断 4 个交易日（09-21~24）→ DU-03 新发现**；4,930 标的/日 | **未登记** | akshare 自动（断因未查：任务在跑但 0 新日） | **DU-03** |
| dragon_tiger | 2,143｜2026-08-07..09-24｜当日到 | 893 只/33 日；**浅史**（2026-08 起）；深史在 dragon_tiger_seat | 未登记→DU-14 | akshare 自动 | DU-14 |
| dragon_tiger_seat | 618,963｜2022-01-04..09-24｜当日到 | 4.5 年席位深史健在（S1） | 在册 | akshare 自动 | — |
| block_trade | 1,414｜2026-08-07..09-24｜当日到 | 浅史（2026-08 起） | 未登记→DU-14 | akshare 自动 | DU-14 |
| block_trade_detail | FINAL 1,586｜2026-08-03..09-24 | 同上 | 未登记→DU-14 | akshare 自动 | DU-14 |
| auction_snapshot | FINAL 272,117｜2026-06-01..09-24｜当日到 | 6,572 标的；2026-06 前竞价过程数据永久缺口（结构性） | `auction_window_pre_202606_gap` no_source + `auction_20260918_transition_gap` | 桥派生自动（47+ 密集日累积） | 已登记 |
| auction_book | FINAL 3,475,798｜2026-07-21..09-24｜当日到 | 6,067 标的；同族结构性 | 同上 | 桥派生自动 | 已登记 |
| northbound_hold_snapshot | FINAL 30,574｜2024-09-30..2026-06-30 | 4,451 ts_code，季度快照语义；Q3（09-30）待 10 月刷新=按季新鲜 | 撞码治理 resolved+monitoring | tushare hk_hold 季更 | 已登记 |

### 1.3 估值/指标/指数族

| 表 | ①行数/范围/最新日 | ②宇宙完整性 | ③登记 | ④更新机制 | ⑤卡 |
|---|---|---|---|---|---|
| daily_valuation | FINAL 207,788｜2026-08-03..09-24｜当日到 | 最新日仅 1,000/5,571 只；**09-23=2,504、09-24=1,000 行=部分写入病残余（应 ~5,560）** | `daily_valuation_2026_09_10_missing` mitigated（残病 in-code） | akshare 增量（无重试/0 行静默） | 已登记+**DU-11** |
| stock_daily_basic | 7,079,611｜2021-01-04..09-24｜当日到 | 5,781 只/日满量 | 在册无缺口 | 自动 | — |
| stock_indicator | FINAL 11,685,777｜2015-01-05..09-24｜当日到 | 5,827 只；circ_mv 断供+吞并双案已 resolved（#288） | 两案 resolved | akshare 自动（映射已修） | 已闭 |
| technical_indicator | FINAL 351,276,067｜2019-01-04..09-24｜当日到 | 14,328 符号（含退市）；429 万重复 (date,symbol) 行待清 | `technical_indicator_duplicate_rows_ingest_ts` monitoring | dwm 分片自动 | 已登记 |
| stock_basic | 9,036,265｜2015-01-05..09-23 | 5,781 符号日快照族；缺 5 日不可回补（快照型） | `stock_basic_snapshot_days_missing` accepted | 双调度点 akshare | 已登记 |
| stock_list / hk_stock_list / lof_list | 5,921 / 2,798 / 371 | 清单族在量 | 1970 哨兵残留（W4/W5 登记） | 快照 | 已登记 |
| etf_list | 2,184（在市 1,748） | vs 外部 ~1,700-1,800 场内 → **完整**（tushare fund_basic 接线后） | 哨兵案 completed | tushare 月更 | 已闭 |
| index_list | 9,700｜09-11 起真源 | tushare index_basic 全市场真宇宙（8000 真行+1700 墓碑+新进料） | 错宇宙案 completed | tushare 月更 | 已闭 |
| index_constituent | 674,232｜2005-04-29..09-23 | 5 指数（000300/000905/000906/000852/000985），000985 承担全 A 语义 | 散缺案 monitoring | akshare 双调度点 | 已登记 |
| index_quote | 238,951｜2026-07-14..09-24 | 562 标的最新日；稀疏→已修（EOD 回补+tdx 历史段） | `index_quote_minute_sparse` mitigated | 计划任务 15:10 | 已登记 |
| index_valuation_daily | FINAL 8,126｜2010-01-01..09-24 | 000300+000905 双标的；派生列 WO-1 重建后全绿 | 三案 resolved | 日频 compute 腿 | 已闭 |
| regime_snapshot_history（c1_backtest） | 3,627 行/1,817 唯一日（每日双写）【09-26 勘误对齐 L01-C03】｜2019-04-01..09-24｜当日 08:45 到 | 全 A 域 regime 快照日更健在 | 在册无缺口 | 内部日更 | — |
| regime_state_anchored | 2,239｜2017-07-11..09-24 | 健在 | 在册 | 内部 | — |

### 1.4 ETF/LOF/可转债/期货/外盘/币圈

| 表 | ①行数/范围/最新日 | ②宇宙完整性 | ③登记 | ④更新机制 | ⑤卡 |
|---|---|---|---|---|---|
| kline_etf_1min | 290,394,600｜2021-07-01..09-24｜当日到 | 最新日 1,673 只 vs etf_list 在市 1,748 → 覆盖 95.7%（差=不活跃/退市过渡） | 在册 | 桥自动 | — |
| kline_etf_daily | FINAL 102,158｜2021-03-08..09-24 | 1,675 只但逐只深度 ~57 日，**弃用表**（1 只 ≥250 日） | `kline_etf_daily_shallow_depth` open | akshare 浅源 | 已登记 |
| kline_etf_60min | 6,093,724｜2005-02-23..09-24 | 四段深度窗缺口 | `kline_etf_60min_depth_windows` monitoring | 自动+待合成回补 | 已登记 |
| etf_nav | FINAL 90,389｜2021-07-29..09-23｜T-1 到 | 1,697 只 | 在册 | 自动 | — |
| kline_lof_1min | 139,240,903｜2019-01-02..09-24 | 最新日 346 只 vs lof_list 371（差=不活跃，09-11 五表族回补后健康） | LOF 案 completed | 桥自动 | 已闭 |
| convertible_bond_list | 1,051（在市口径） | vs 外部 ~700-800 在市+历史退市 → 覆盖合理；1970 五列占位 open | P6 B 族 open | 快照 | 已登记 |
| kline_cb | 245,849｜2019-01-02..09-24 | **最新日仅 310 只 vs 清单 1,051 → 可转债 K 线宇宙显著窄于清单（未登记）** | **未登记→DU-15** | 桥自动 | **DU-15** |
| convertible_bond_iv | 10,549｜..09-24 | 小宇宙（IV 链） | 在册 | 自动 | — |
| kline_futures | 8,258｜2017-01-17..**09-18** | **仅 CFFEX 4 品种（IF/IH/IC/IM 连续+合约）**，全市场 70+ 品种不覆盖；**日频停在 09-18（miniqmt 退役，akshare 周补腿不覆盖日频）→ DU-08** | **未登记→DU-08** | miniqmt 死，akshare 仅周末校准 | **DU-08** |
| futures_position / futures_term_structure | 3,458/3,404｜..09-23 | akshare 腿活 | 在册 | 自动 | — |
| futures_warehouse_receipt | 2,887,725 | CZCE 日更正常；SHFE 维度 2025-11-17 止（归档 404，永久） | `futures_warehouse_receipt_shfe_archive_cap` no_source | akshare 自动 | 已登记 |
| us_index | 22,612｜1993-01-29..09-23｜T-1 到 | **仅 3 标的（DJI/IXIC/SPX）**，迷你宇宙（设计内，10_regime 外盘传导够用；扩面无真源清单） | 在册 | akshare 日更 | DU-17（设计内留痕） |
| kline_us_daily | 594｜2026-07-20..09-23 | 11 标的（tickflow 免费源上限，登记） | `kline_us_daily_source_depth_limit` accepted | tickflow 日更 | 已登记 |
| hk_kline | 6,298｜2026-08-03..**09-16** | 191 只（QMT 源上限）；**09-16 止=miniqmt 退役断供 → DU-09**；宽通道 kline_hk_daily 活（200,768 行、最新日 5,210 只、09-24 到） | `hk_kline_source_depth_limit` accepted（断供未登记） | miniqmt 死；akshare 宽通道在产 | **DU-09** |
| hk_connect_flow | 4,052｜2014-11-17..2024-08-16 | 港交所停发，永久退役 | 双条 accepted | 空跑留痕 | 已闭 |
| crypto_kline_daily | FINAL 18,495｜2025-08-08..09-23｜T-1 到 | **94 标的但逐日宇宙缩水：09-18=71→09-23=51（-28%/5 日）→ DU-10**（dataqa 已记"半死"本普查量化） | 未立卡→DU-10 | binance.vision 日 08:30 | **DU-10** |
| hl_funding_history | 4,688,299｜..09-24 00:00 | Hyperliquid 资金费活 | 在册 | daily_crypto | — |
| hl_liquidation_raw | 6 行 | 清算链零业务行 | `hl_liquidation_raw_empty` open | 采集链待查 | 已登记 |

### 1.5 宏观/另类

| 表 | ①行数/范围/最新日 | ②宇宙完整性 | ③登记 | ④更新机制 | ⑤卡 |
|---|---|---|---|---|---|
| macro_data | 50,402｜..09-24｜当日到 | 2,261 指标（akshare 主宏观源活） | 在册 | akshare | — |
| edb_data | **0 行** | iFind 退役，替代源 macro_data 在产 | `edb_data_ifind_quota_exhausted` accepted | 已退役 | 已闭 |
| rate_decision_calendar | 3,086｜decision 止 2025-10-30 | 金十退役 11 央行停更 | `rate_decision_calendar_jin10_retired` no_source | 换源待办 | 已登记 |
| cftc_positioning | 81,270｜report 止 09-08 | 周频源滞后约 2-3 周（未深查，观察项） | 未登记 | akshare 周更 | DU-14 附注 |
| alt_shipping_index | 27,206｜..09-24｜当日到 | BDI 主序列活；租船/灵便两子序列上游停发（登记） | 两子条 accepted | akshare 日更 | 已登记 |
| weather_data | 10,353｜31 记录日 | 40 城快照积累型，历史不可回补 | `weather_data_sparse_31_days` accepted | QWeather 日更 | 已登记 |
| alt_sz_reservoir_level | 75.56M｜**tdate 止 2026-07-31** | 半死管线（采集活、源停 52 天） | `reservoir_level_source_stale` monitoring | 任务活源死 | 已登记 |
| trade_calendar | 8,797｜1990-12-19..2026-12-31 | 日历本体完整（含未来） | 在册 | 静态+年度刷新 | — |

### 1.6 财务族（c3_fundamental）

| 表 | ①行数/范围/最新日 | ②宇宙完整性 | ③登记 | ④更新机制 | ⑤卡 |
|---|---|---|---|---|---|
| income_statement | 346,176｜1995-01-05..09-02 | 5,878 家；Q2 财报季披露完毕=按季新鲜 | 在册 | akshare 自动 | — |
| balance_sheet | 339,738｜1990-03-21..09-02 | 5,878 家 | 在册 | 自动 | — |
| cashflow_statement | 310,447｜1999-01-30..09-02 | 5,869 家 | 在册 | 自动 | — |
| financial_indicator | 386,331｜1970 哨兵..09-12 | 5,896 家；1970 announce 34,339 格 B 族 open | P6 open | 自动 | 已登记 |
| financial_derived | FINAL 301,752｜2004-07-01..09-02 | 派生表随三表走 | 在册 | 派生 | — |
| analyst_forecast | 111,543｜**2026-07-22..09-24** | **仅 ~3 个月窗**（B 态，国盛景气标尺原料 S5）；外部 Wind/朝阳永续全史无免费源对照 | 台账记 B 态，未立卡→**DU-13** | akshare 日更 | **DU-13** |
| earnings_forecast | 125,582｜1999-01-08..07-03 | 业绩预告季 seasonality（7 月截止正常） | 在册 | 自动 | — |
| pdf_forecast_extracted | 192,365｜2017-01-02..**2021-12-31** | **止 2021-12，5 年断档（新发现→DU-12）** | **未登记** | 停（PDF 提取链断） | **DU-12** |
| research_report | FINAL 146,769｜2017-01-02..**09-18** | 4,704 家；**最新日滞后 4 交易日**+rating_change 空列 | `research_report_hot_value_rating_change_empty` open（已收窄） | akshare 日更（滞后观察） | 已登记+**DU-12** |
| shareholder_count | FINAL 514,006｜1993-01-12..09-24｜当日到 | 5,904 家满覆盖（切源 akshare 后复活） | X-7 同族 resolved | akshare 日更 | 已闭 |
| top10_shareholders | FINAL 1,500,427｜2005-01-29..06-30 | 季度末语义；20260630 全市场补齐；20251231(73.6%)/20250930(68.6%) 覆盖率 legacy 缺口 | `top10_shareholders_incremental_starved` resolved | akshare 日更 | 已闭（余量登记） |
| top10_circulating_shareholders | 2,138,764｜2005-01-29..**05-15** | bdpan 时代止 05-15（akshare 腿未覆盖流通口径） | 未单独立卡→DU-13 附注 | akshare（未接） | DU-13 附注 |
| consensus_daily | FINAL 6,780,329｜2017-01-03..09-14 | 3,053 家；值类列 PIT 坏（平推快照）禁用 | `consensus_daily_value_cols_pit_broken` open | 在产但值坏 | **DU-07** |
| consensus_daily_repaired | 1,563,996｜2017..2021 全+2026 近窗 | **2022-2025 全断**（FINAL 0 行）；2026 段 91,367 行到 09-15 | 同上 open（回补归数据线） | 断 | **DU-07** |
| equity_pledge_summary | 1,723,194｜2014-03-07..09-18 | 4,441 家（end_date 语义） | 在册 | 自动 | — |
| restricted_shares | 10,197,952｜2005-01-10..**07-02** | 解禁队列 2026-07 后未整段重拉（P6 待办：按 symbol 重拉全队列） | P6 B 族 open | 写入修复待重拉 | 已登记 |
| share_unlock | 30,161｜unlock 2010-01-04..2027-09-21 | 派生表覆盖未来 1 年 | 在册 | 派生 | — |
| disclosure_plan | 305,685｜2001-02-06..08-31 | 披露计划季语义 | 在册 | 自动 | — |
| dividend | 191,633｜1970 哨兵..**09-22** | **09-18 登记断供后已复通**（2026-08=530/09=409 行，切源见效）；1970 announce 6,749 格 B 族 | `dividend_plan_miniqmt_retired` no_source（**状态过时，实际已复通**→勘误） | akshare 切源后自动 | 勘误 |
| ex_dividend_event | 57,864｜1991-03-11..09-24｜当日到 | 除权事件腿活 | daily_event 槽 | — |
| express_report | 28,704｜2005-01-08..07-02 | 快报季 seasonality | 在册 | 自动 | — |
| repurchase | 6,081｜2006-03-02..09-25 | 回购活（次日数据到） | 在册 | 自动 | — |
| share_change | FINAL 190,496｜2009-12-16..09-23 | cninfo 日期参数 bug 已修 resolved | resolved | akshare 自动 | 已闭 |
| main_business | 2,094,453｜report_period..2026-03-31 | **2026H1（0630 期）未见**（正常应 8 月底入，观察项）；1970 占位 B 族 | P6 附带 | 季更 | DU-13 附注 |

## 2. 缺口卡明细（DU 编号）

> 编号规则：DU-01 起，本普查新立卡；已登记 known_data_gaps 的沿用原条目并在卡内注明映射。状态=open（待处置）/monitoring/registered（已有登记，此处只索引）。

### DU-01【open·P1】kline_sector_880 通达信行业族 0 行（469 vs 727）
- **宇宙应有数 vs 实有数**：应有 727（库内 mootdx 分钟真值 09-08 实证：8800=11/8802=32/8803=61/8804=71/8805-8809=424/8810-8814=128）；实有 469（880 家族全部，8810-8814 行业族 **0 行**、8803/8804 **0 行**）。外部"800+"无精确快照，不可对照（如实登记）。
- 现状：近 5 个交易日 468 码/日满量在产（缺的行业族不是"缺数"而是"宇宙从未包含"）。312 日历史断档已于 09-11 tqcenter 拉宽回补（2020-03-17 起零缺日，白赚 6.5 年）。
- 补采路径：tqcenter capability 扩面（881 行业族与 8803/8804 号段加入 kline_sector_880 capability 的板块清单）+ `sector_code_name_map` 映射生成器扩 881 族（tdxzs.cfg 已有 132 条主数据可派生名称）；历史回补复用 09-11 配方（TQCenterProvider.fetch days=500→1000，依赖通达信客户端开启）。
- 下游：板块线主供 S8、BM-SEL-08 板块轮动、sector_state 行业维度情绪态、方案 J 合成覆盖 580/727。

### DU-02【open·P1】sector_state/sector_code_name_map/sector_constituent 同源 881 缺席（DU-01 连带）
- 实测：sector_state uniq(sector_code)=469（2022-09-01..09-23）；sector_code_name_map 469 行、881 族 0 行、8803/8804 0 行；sector_constituent 595 码（有 881 成分但无 8803/8804）。
- 映射关系：881 行业成分已在 sector_constituent（128 码），情绪态引擎只吃 880 宇宙 → 行业维度情绪/RRG/资金分从未产出。补 DU-01 后本卡自动闭合（派生重跑即可）。

### DU-03【open·P1】margin_trading 断更 4 个交易日（09-19 起 0 新日）
- 实测：FINAL 2,065,857 行、2024-09-02..**2026-09-18**、4,930 标的/日恒量；09-21/22/23/24 四个交易日 0 行。
- 未登记 known_data_gaps（新发现）。任务接线在（tasks.yaml akshare 源），属"任务活但 0 新日"——与 daily_valuation 0 行静默同型，疑东财/交易所披露口径变化或接口静默失败，断因未查（本普查只读不修）。
- 下游：S2 板块杠杆资金、S12 两融温度（情绪线 C 成分，本已"覆盖仅 2 个月滞后 1-2 日"→现滞后 4 日+）、cohort_ledger_daily、emotion_index 成分聚合。

### DU-04【open·P1】tick_data 2026-09-21 准零日（14,567 行 vs 邻日 2,700 万+）
- 实测：09-19=0（周六）/09-20=0（周日）/09-21=**14,567 行**（周一交易日，正常 ~2,750 万）/09-22=28,523,990/09-23=27,715,731/09-24=27,589,338。
- 判读：09-21 为 miniQMT 清退（09-18）后第一个交易日，桥模式采集当日近乎全程缺勤（仅 14,567 行≈尾盘残段），09-22 起恢复正常。属清退过渡带第二例（第一例=09-17 已回补 completed，本日**未登记**）。
- 补采路径：模拟盘 QMT 服务器保留 ≈1 个月，30 天内可按 `tick_data_2026_0917_gap` 配方（E:/国金QMT交易端模拟 p0_tick_backfill.py）回补；过期即永久。
- 下游：tick 级回测回放该日无数据（K 线级不受影响）。

### DU-05【open·P2】news_sentiment_score 打分链停摆 1 年+
- 实测：FINAL 7,733,898 行，max(publish_time)=**2025-09-09**；同源原始流 news_data 活到 2026-09-25（8.25M 行）——原始新闻在产、打分停止 12 个月+。
- 未登记。形态="下游加工断、上游活着"，与 news_sentiment_window 的写入器未接线案（已修）同族但不同腿。
- 下游：新闻情绪类因子、情绪线 C6 的个股级打分（现只有 window 聚合腿可用）。

### DU-06【open·P2】news_sentiment_window symbol 级止 2026-08-20
- 实测：market 级 185 日（2026-02-24..09-23，在产）；symbol 级 120 日（2026-02-24..**08-20**，19,635 行后断）。
- 判读：09-10 接线修复（run_nightly_sentiment.py）恢复的是 market 腿；symbol 腿 08-20 后无产出（疑夜间批只算 market 粒度或个股窗零数据静默跳过）。
- 下游：个股情绪因子；market 腿 C6 不受影响。

### DU-07【registered·P2】consensus_daily 值类 PIT 坏 + repaired 表 2022-2025 断
- 映射：known_data_gaps `consensus_daily_value_cols_pit_broken`（open）。实测：plain FINAL 6,780,329 行（2017-01-03..09-14、3,053 家，值类禁用）；repaired FINAL 1,563,996 行 = 2017-2021 五年（260-349K/年）+2026 近窗 91,367 行（到 09-15），**2022-2025 四年 0 行**。
- 应有数：全时序 ~4,900 交易日 × 3,000+ 家；实有断四年（无免费等价源对照，东财/汇智 prob 绩效源为候选）。
- 下游：S40 部分供给、预期差/一致预期因子只能用 2017-2021+2026 段回测。

### DU-08【open·P2】kline_futures 停在 09-18（miniqmt 退役断供）
- 实测：8,258 行、2017-01-17..**2026-09-18**、仅 CFFEX 4 品种（IF/IH/IC/IM 连续+分合约）；futures_position/futures_term_structure（akshare 腿）活到 09-23。
- 未登记（hk_kline 同型断供同入 DU-09）。全市场期货 70+ 品种日 K 从未覆盖（commodity_futures_main 仅 171 行）——属"设计内迷你宇宙+新发断供"叠加。
- 下游：S45 期货对冲池（37_liquidity_crisis_protocol）、BM-RC-04-E 流动性监控的期指腿。
- 补采路径：akshare 期货日 K capability（东财/新浪）挂 daily_capital 槽；商品族扩面另立项。

### DU-09【open·P3】hk_kline 停在 09-16（miniqmt 退役；宽通道在产）
- 实测：hk_kline 6,298 行、2026-08-03..**09-16**、191 只（QMT 源上限已登记）；kline_hk_daily（akshare）200,768 行、2026-08-03..**09-24**、最新日 5,210 只证券——宽通道活、窄通道死。
- 判读：断供本体影响小（kline_hk_daily 承接），但 tasks.yaml `hk_kline_incremental` source=miniqmt 已死未摘牌，属断链任务残留。

### DU-10【open·P3】crypto_kline_daily 宇宙逐日缩水 + T-1 滞后
- 实测：FINAL 18,495 行、2025-08-08..09-23；逐日标的数 09-18=71 / 09-19=69 / 09-20=67 / 09-21=59 / 09-22=55 / 09-23=**51**（5 日 -28%）；94 码全历史。今日（09-24 08:30 槽后）应到 09-23 UTC 全量，缩水为渐进失血非单日故障。
- dataqa gaps_registry_review 曾记"半死（09-19=0）"，本普查量化缩水曲线。补采：binance.vision 镜像免 key，按 universe_eligible 白名单重跑即回。

### DU-11【registered 扩面·P2】daily_valuation 部分写入病残余（09-23=2,504 / 09-24=1,000 行）
- 映射：`daily_valuation_2026_09_10_missing`（mitigated）已登记"09-16/17/18 符号覆盖缺 15-61%"；本普查续证 **09-23=2,504、09-24=1,000**（应 ~5,560），病未愈且最新两日加重。max_date 哨兵与 7 日行数地板（2,000）对该形态不可见（1,000<2,000 实际会响——09-24 当日落库中，明日复核）。
- 下游：估值分位（S4）、流通市值权重（已改道股本反推法不受害）。

### DU-12【open·P3】research_report 滞后 4 日 + rating_change 空列 + pdf_forecast_extracted 5 年断
- 实测：research_report FINAL 146,769 行、2017-01-02..**09-18**（滞后 4 交易日；月度 2026-08=1,875/09=864 在产）；rating_change 空列承续（hot_value 已随 schema 移除了结）。pdf_forecast_extracted 192,365 行**止 2021-12-31**（2022 起 0 行，PDF 提取链断，未登记新发现）。
- 下游：S20 评级情绪成分（候选）、卖方预期 PDF 矿（5 年真空）。

### DU-13【open·P3】analyst_forecast 深度仅 3 个月窗（B 态量化）
- 实测：111,543 行、**2026-07-22..09-24**（min report_date=07-22）、2,787 家。台账定性 B 态，本普查给深度数：~3 个月。top10_circulating_shareholders（止 05-15）与 main_business（止 2026Q1 期）同族浅/滞，附注同卡观察。
- 无免费全史源对照（朝阳永续/Wind 付费层，Owner 门位）。

### DU-14【registered 索引·P4】浅史表群（2026-07/08 起点型）
- limit_up_down（49 日）、limit_up_pool（54 日）、dragon_tiger（33 日）、block_trade/block_trade_detail（33 日）、cftc_positioning（report 止 09-08 周频滞后）、daban_board_event（09-23/24 两日未见观察）。共同点：新鲜度当日到、深度浅；外部多无免费全史源（如实登记不可对照）。板块线/情绪线以 dragon_tiger_seat（4.5 年）等深表承接，影响有限。

### DU-15【open·P4】kline_cb 可转债 K 线宇宙窄于清单
- 实测：kline_cb 最新日 310 只 vs convertible_bond_list 1,051（在市约 700）——K 线通道只覆盖约 3 成。未登记。补采=桥通道 CB 板块清单核查（同北交所分钟线先例：capability 声明板块与实际返回板块不一致家族）。

### 已登记闭合/monitoring 卡（本普查核对一致，不重立）
- kline_sector_880 312 日断档已补（completed，2020-03-17 起零缺日复核成立）✔
- 情绪指数"仅 143 日"**勘误**：emotion_index close_final 8,614 个交易日（1991-06-10..09-24）全史在产，当日到；"143"疑为 news_sentiment_window market 级旧计数。
- auction 过程数据结构性缺口（A3/09-18 过渡日）、冷归档未挂回（F: 盘）、ETF 分钟 tz 劈叉（resolved 回滚窗在库）、tick 2022-2024（bdpan 通道评估）、kline_etf_daily 弃用、1970 哨兵 P6（A 族清零/B 族 open）、reservoir 半死管线（monitoring 维持）、SHFE 仓单上限、金十退役、edb_data 退役——均与库内实测一致。

## 3. 补采优先级（按下游环节影响排序）

| 序 | 卡 | 一句话理由（下游环节影响） | 通道与量级 |
|---|---|---|---|
| 1 | DU-01/02 881 行业族 0 行 | Owner 原问；板块线主供（S8）行业维度 35.8% 缺席；sector_state/轮动/合成全连带；数据本体在兄弟表活着，补采=capability 扩面+历史拉宽，**性价比最高** | tqcenter 拉宽 days=1000（复用 09-11 配方）+映射生成器扩族；预估一次客户端会话完成 |
| 2 | DU-03 margin_trading 断 4 日 | 两融温度/杠杆资金/情绪成分三处降级且每日扩大；任务在跑只需查断因（接口静默 0 行同型病已有告警缺口） | 查 fetch_perf+akshare 接口实弹；补跑增量即回 |
| 3 | DU-04 tick 09-21 准零日 | 回测回放连续性；模拟盘源 30 天窗口倒计时，**过期永久** | 复用 p0_tick_backfill.py 模拟盘配方；~2,700 万行级 |
| 4 | DU-11 daily_valuation 部分写入 | 估值分位/权重消费最新两日加重（1,000/5,560）；已有幂等重跑工单，需排期执行 | full_refresh 历史窗重跑（~11h/次） |
| 5 | DU-07 consensus 2022-2025 断 | 预期因子四年真空，回测窗系统性缺角；免费源换源立项 | 换源/重灌（数据线工单，已有登记） |
| 6 | DU-05/06 情绪双腿停摆 | 原始新闻在产而打分停 1 年+，修接线即回（近因修复类）；个股情绪因子前置 | 夜间批扩 symbol 腿+打分任务重启 |
| 7 | DU-08/09 期货/港股断供 | 对冲池与外盘腿；kline_hk_daily 宽通道已承接港股，期货需 akshare capability 立项 | akshare 期货日 K 挂 daily_capital |
| 8 | DU-10 crypto 缩水 | 7×24 卡半死，量级小但白送（镜像免 key） | binance.vision 重跑白名单 |
| 9 | DU-12/13/15 研报/预期/转债 | 单点因子原料；pdf 提取链 5 年断需工程项 | 各自独立小工单 |

## 4. 空表清单（0 行，附判读）

`edb_data`（退役已登记）/ `l2_tick`（L2 权限已登记）/ `suspend`（停牌，akshare 无批量源，未登记观察）/ `msci_adjustment`、`ipo_schedule`、`market_index_meta`、`etf_benchmark`、`stock_valuation`、`account_nav_daily`、`margin_target_adjustment`、`reconciliation_differences`、`index_valuation_daily_v2`（0 行占位/待启用，均未在 known_data_gaps 立卡——多为 schema 先行或退役残留，建议下轮"净零内收"审计批量定性，本普查只登记不动）。

## 5. 普查边界与诚实条款

- 行数双口径已注明（FINAL vs total_rows）；大表 distinct 仅取最新日（分区裁剪），全史 uniq 可能更大。
- "应有数"仅股票（5,562 库内实证）、ETF（1,748 在市）、指数（9,700）、板块（727 库内真值）有可靠锚；期货全品种、港股全清单、美股、预期类全史——**无外部真源可对照**处均已如实标注，未编数。
- 断因判定仅到"任务/源/派生"层级（只读普查），未做 fetch_perf 级取证；DU-03/05/06/12 的根因留待修复班实弹核查。
- 本文档为新建件，未改动任何现有文件；未执行任何 git 写操作。
