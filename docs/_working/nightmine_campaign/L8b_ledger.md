---
ttl: task_bound
title: L8b 考试可考面普查台账（逐卡实测，只读，不改卡）
created: "2026-10-10"
sid: st-nightmine-20261010
lane: L8b
family_id: NIGHTMINE-CAMPAIGN
---

# L8b 台账：考试可考面普查（preregistered + blocked_* 全量逐卡）

工作根=工棚 `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`。
产出物=`04_exam_feasibility_census.yaml`（机生，256 行逐卡，本文件是其方法+汇总+未尽事项）。
生成器（可复跑）=`.runtime/tmp/l8b_census_v7.py`（同目录 v2..v6 为本场纠偏版本链，v7=终版）。
**只读纪律**：未改任何卡、分数册、TDM、注册表；未跑考试执行器出分；未做任何 git 写操作。
探针一律在册通道（禁裸 duckdb）：

```
cd D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010 && python -c "import sys; sys.path.insert(0,'scripts/backtest'); \
from fexam.ch_data import ch_query_df, table_columns; print(ch_query_df('SELECT ...'))"
```

## 〇、快照时点与卡册现势漂移（重要：卡册在本车道运行期间持续被他道写入）

| 量 | 值 | 凭据 |
|---|---|---|
| 普查行数（=card_total） | **256** | census `card_total` |
| 快照状态构成 | preregistered 178 / blocked_on_data 52 / blocked_on_impl 26 | census `status_scope_breakdown` |
| 卡册最新 mtime | epoch 1791589985.374 = **2026-10-10 07:53:05**（本地） | census `card_book_latest_mtime_epoch` |
| 本场会话内漂移 | 205 → 211 → 243 → 247 → 249 → **256**（历次扫描实测） | l8b_run*.log 逐行 `cards in scope` |
| YAML 卡册总文件数 | 454（含 186+ empty 骨架，empty 不入本普查口径） | 复扫 `rglob("*.yaml")` 计数 |
| 半截文件（他道在途写入，未入册） | **2** | census `cards_skipped_unparsed` |

未入册的 2 张（非逃避，是读取时该文件 YAML 尚未写完）：
`position_flow/P1/TDM-P-P1-02__calibration__04_盈亏百分比腿与ATR缺失降级.yaml`（line 45 `atr_missing_arm: **…**` 别名扫描错）、
`position_flow/P3/TDM-P-P3-01__comparison__04_日亏熔断禁加期分层对照.yaml`（line 56 同类）。
→ 交接：这两张卡本身有语法缺陷（`**` 起手被 YAML 当 alias），施工道需先把值加引号；本车道重跑一次生成器即可补入普查。

## 一、三态判据（机检化定义，全部落在 census `method_notes`）

1. **主面/辅面分治**：主面 = `data_binding` 中 `signal_table / *table / *source / *refs / *series / *deriv / target*` 类键解析出的 CH 表
   （带库名正则 + 裸表名与 `system.tables` 同名解析）；辅面 = 其余键（如 `data_window_evidence`），**只登记实测不参与判据**。
   备份/重算表（`__preeng_backup_20261007`、`_recalc`、`hugebk`）剔除。
2. **卡无 data_binding 时的第二通道**（按任务书"窗口/桶/门柱＋TDM 节点 data_refs"）：
   `config/trading_decision_map.yaml` 节点 `data_refs`（81 节点有）→ `data/strategy_intake/matrix_inventory.yaml`
   `dataset_id → entity`（334 条）→ 若 entity 形如 `c\d_[a-z]+\.` 才当主面；否则判"无数据面"并写死 refs/实体名。
3. **日期列纠偏（本场第一号坑）**：业务日期列按 `trade_date / window_date / snapshot_date / cal_date / report_date /
   report_period / announce_date / update_date / valid_from / …` 优先序取；
   `ingest_ts / updated_at / fetched_at / recorded_time / crawl_time` **永不作窗口判据**——首轮误用 `ingest_ts`
   且该列多为 epoch 0，把 `c3_fundamental.news_sentiment_score` 等误判成"窗内 1970-01-01"（155 张 not_scorable 假阴），已纠。
4. **覆盖判据（严）**：主面表窗内实测 `min ⊇ 冻结窗起 且 max ⊇ 冻结窗止`，且窗内日期数 ≥ `c1_market.trade_calendar`
   （`is_open=1`，列实测=**cal_date**，非 trade_date）同窗应有交易日数 −1。差日=不满足；**未提议任何挪窗**。
5. **now 需三件同时满足**：①主面表在册且覆盖冻结窗（实测）②`signal_column` 列名在该表 `system.columns` 实测命中
   ③卡自述 `signal_derivation` 无推导算子（词表判定，**卡标题词不作证据**）且全 binding 文本无运行产物语义
   （净值/NAV/成交/持仓/run_id/sim_trade_log/decision_daily/shadow/回测产物/实盘）且无 PG/图谱面（ig_node/ig_edge/meta_question）。
   → 5 张 now 中有 1 张（板块催化剂密度类）在 `gap_or_build_note` 记了"残留风险：卡名含聚合语义，执行期若需计数/分位再 +≈20-40 行"。
6. **SCD/PIT 特例**：表只有 `update_date`（登记时点）而有 `valid_from/valid_to` 时，加测 PIT 上下界，以 `valid_from` 作真历史起点。
7. 超大表（>4 亿行：`tick_data` 39.4 亿 / `technical_indicator` 4.04 亿 / `kline_1min` 14.9 亿 / `kline_5min` 2.96 亿）
   窗内 `countDistinct` 跳过，只按全表实测 min/max 判覆盖，连续性标"未验证"（未因此冒判有数，也不因此判死）。
8. 空结果先判静默失败：`ch_query_df` 空返回/`Code:` 体在 `probe()` 里单独记 `empty_suspect`；断言表不存在前跑过
   `python -m zephyr.library.lookup state "alt_job_postings"`（本工棚版**可用**，两源均 `-- no hits --`，快照 2026-10-10T07:50:51+08:00），
   并补手工阶梯：`git log --oneline --grep=alt_job_postings`（零命中）、`git log --grep=ipo_calendar`（命中 d6f7d233aa7 / 05bc9672d40 注册表校正、
   646569545f7 新表 DDL）、`grep -rl alt_job_postings docs/_working --include=*.md`（零）、`grep -rn "alt_job_postings|alt_livestream_gmv" config data --include=*.yaml`（零）。

## 二、探针清单（合计 **478** 次在册查询，最慢 0.73s=`cov:c1_market.kline_5min`）

| 类 | 内容 | 量 |
|---|---|---|
| 库存 | `SELECT database,name,engine,toString(total_rows) FROM system.tables WHERE database NOT IN ('system','information_schema','INFORMATION_SCHEMA')` | **246 表**全清单（含引擎，供 FINAL 复核） |
| 列/类型 | `SELECT database,table,name,type FROM system.columns WHERE (db,table) IN 卡面引用集` | 151 表逐列 |
| 表覆盖 | 每表 `SELECT toString(min(<业务日期列>)), toString(max(...)), countDistinct(...), count() FROM <t>` | 135 表（census `table_probe_registry` 全存） |
| 窗覆盖 | 每（表×卡冻结窗）`... WHERE <日期列> BETWEEN '<is_start>' AND '<oos_end>'` | 逐卡缓存去重 |
| 日历基准 | `SELECT countDistinct(cal_date) FROM c1_market.trade_calendar WHERE is_open=1 AND cal_date BETWEEN …` | 逐窗缓存 |
| 目标/富矿面 | 见下节 4 条 + 断供专项 3 条 + 替代面 4 条（census `target_face_probes`） | 13 条 |
| PIT 专项 | `sector_constituent / index_constituent / sector_constituent_sw_history / concept_board_constituent / industry_class / sector_constituent_snapshot FINAL` | 6 条 |

## 三、三态结论

**tally：scorable_now 5 ｜ scorable_with_build 134 ｜ not_scorable 117 ｜ undetermined 0（256/256 全判）**

流×判（合计）：entry_flow 5/85/85 ｜ exit_flow 0/18/7 ｜ portfolio_flow 0/20/1 ｜ position_flow 0/11/24
族×判：calibration 3/59/60 ｜ comparison 0/39/27 ｜ ablation 2/24/28 ｜ shadow 0/12/2
状态×判：preregistered 5/117/56 ｜ blocked_on_data 0/7/45 ｜ blocked_on_impl 0/10/16（**blocked_on_impl 有 10 张数据面其实已就位**，只缺件）

### 3.1 scorable_now 全清单（5 张，逐张实测面）

| 卡号 | 冻结窗 | 主面实测（表.列 → 覆盖） |
|---|---|---|
| `TDM-E-L2-02/calibration/02_接棒撤离榜` | 2021-08-02..2025-09-09 | `c1_market.kline_sector_880.close/amount` 2020-03-17..2026-10-08 / 785,204 行 / 窗内 997 日=日历应有 997 日；`c1_market.kline_index` 1990-12-19..2026-10-09 / 3,104,162 行 |
| `TDM-E-L9-A08/calibration/02_BDI领先航运链` | 2020-04-01..2025-09-09 | `c1_market.alt_shipping_index.value` 1988-10-19..2026-10-09 / 49,872 行 / 窗内 1,363 日（日历 1,322）；视图 `c1_market.v_kline_sector_880_named` 2020-03-17..2026-10-08 |
| `TDM-E-L9-A10/calibration/02_全球风险因子隔夜传导` | 2021-09-01..2025-09-09 | `c1_market.a50_futures_daily` 2016-08-29..2026-10-08 / 2,623 行 / 窗内 1,050 日；`c1_market.kline_index`、`c1_market.macro_data.indicator_value`（report_date 1993-03-31..2026-10-09） |
| `TDM-E-L9-V2/ablation/02_情绪相位六段快照就绪` | 2019-01-04..2025-09-09 | `c1_market.emotion_index`（stage='close_final'）1991-06-10..2026-09-30 / 8,617 行 / 该卡窗内 1,622 日 = 日历应有 1,622 日（逐日无缺） |
| `TDM-E-L9-V3/ablation/02_板块状态快照T-1纪律` | 2022-09-01..2025-09-09 | `c1_market.sector_state.strength` 2022-09-01..2026-10-08 / 432,088 行 / 窗内 733 日 = 日历 733 日 |

> 口径提醒：now≠零工作量。执行器 `calibration_exam.run_card()` 不自取数，仍需 W4 薄绑定（signal_spec/target_spec 注入，≤15 行胶水）。

### 3.2 not_scorable 归因（117 张，四类）

| 归因 | 张数 | 罪魁主面表（实测窗） |
|---|---|---||
| 覆盖窗不足 | **86** | `c1_market.technical_indicator` 2019-01-02..2026-09-30（16 张，前置 2019 前 + 缺 10 月两头）｜`c1_market.sector_constituent` valid_from 仅 2026-07-23..2026-10-01（11 张）｜`c1_market.limit_up_pool` 2026-09-01..2026-10-09 / 23 日（7 张）｜`c1_market.kline_daily_hfq` ..2026-09-30（6 张）｜`c1_market.market_pattern_event` 2021-09-01..2026-09-30（4 张，日期列=**anchor_trade_date**）｜`c1_market.auction_snapshot` 2026-06-01..2026-09-30（4 张）｜`c1_market.tick_depth_5` 2026-07-24..2026-09-30（4 张）｜`c1_backtest.node_verdict` 2019-04-01..2026-09-10 / **58 行**（4 张，日期列=window_start） |
| 主面表未建（不在 246 表清单） | **14** | `c1_market.alt_app_rank_daily`、`alt_bank_branch_activity`、`alt_card_payment_weekly`、`alt_ecom_price`、`alt_job_postings`、`alt_livestream_gmv`、`alt_nws_alert`、`alt_satellite_physical`、`alt_social_sentiment_global`、`alt_store_footfall`、`alt_tender_award`、`alt_trade_commodity`、`alt_xueqiu_sentiment`（13 张 alt_* 拟名面）＋ `c3_fundamental.ipo_calendar` |
| 无数据面（binding 与节点 data_refs 双路皆空） | **10** | 见 §3.4 |
| 窗内断日（中段缺日） | 7 | `limit_up_pool`/`sentiment_panel`(52 行/39 日)/`daban_board_event`(1,767 行/21 日) 等微观事件面只有 2026-09-01 起 |

### 3.3 富矿面（实测，本夜的原料地图）

| 面 | 实测命令（原文） | 结果 |
|---|---|---|
| 指数目标面 | `SELECT min(trade_date), max(trade_date), count() FROM c1_market.kline_index WHERE symbol = '000300'` | **2005-01-04 .. 2026-10-09 / 5,284 行**（次日指数收益目标序列直接可取） |
| 未复权日线 | `SELECT min(trade_date), max(trade_date), count() FROM c1_market.kline_daily` | 1990-12-19..2026-10-09 / 10,131,522 行 |
| 涨跌停价 | `SELECT min(trade_date), max(trade_date), count(), uniqExact(symbol) FROM c1_market.stk_limit FINAL` | 2015-01-05..2026-10-09 / **FINAL 9,232,426 行 / 5,831 标的**（`system.tables.total_rows`=9,254,772，差 22,346=版本未合） |
| 新闻情绪原料 | `SELECT min(toDate(publish_time)), max(toDate(publish_time)), count() FROM c3_fundamental.news_sentiment_score` | 2010-01-02..2026-10-04 / 7,947,739 行（6,021 个日期） |
| 情绪窗口聚合 | `SELECT min(window_date), max(window_date), count() FROM c1_market.news_sentiment_window` | 2019-01-04..2026-10-08 / 22,257 行（日期列=**window_date**） |
| 研报 | `SELECT min(publish_date), max(publish_date), countDistinct(publish_date), count() FROM c3_fundamental.research_report` | 2017-01-02..2026-09-30 / 3,129 日 / 146,940 行（**真日期列=publish_date**；我首次按 `report_date` 探→CH 404） |
| 宏观 | `c1_market.macro_data`（report_date）1993-03-31..2026-10-09；`c1_market.macro_data_vintage` 16,091 行 | 事件/预期面可推导 |
| 币圈 | `c1_market.crypto_kline_daily` 2025-08-08..2026-10-08 / 19,801 行 / 141 标的；`hl_funding_history` 4,785,877 行 | 深度只 1 年 2 月（MA200 自 2026-03 起有效，卡内已自锁此事实） |

### 3.4 "无数据面" 10 张与复核线索（本车道判 not_scorable，但缺的是**绑定**不是矿）

`TDM-E-L1-S0/calibration/02_货币卡｜03_流动性卡｜04_海外卡｜05_政策事件卡`、
`TDM-E-L1-S2/calibration/07_连板家数分布`、`TDM-E-L1-S3/calibration/02_昨日涨停溢价｜03_晋级率｜04_情绪先锋四态`、
`TDM-E-L9-Z1/ablation/02_十态状态机与十八列schema强制`、`TDM-E-L9-Z2/ablation/02_净零与chain_refs双向对账`。
（前 8 张 `data_binding: null`，卡内只有 window/buckets/pillars/target。）复核线索（实测）：
- L1-S0 货币/流动性卡节点 `data_refs=[DS-098]` → 实体 `capital.margin`（**非表名，DS→表映射缺口**）；两融实表
  `c1_market.margin_trading` 实测 2024-09-02..2026-10-08 / 2,100,709 行 → 即便补映射，IS 窗 2019-2023 仍断供。
- L1-S3 涨停溢价/晋级率/先锋四态：原料在 `c1_market.limit_up_pool`（1,426 行 / 23 日）、`daban_board_event`（1,767 行 / 21 日）、
  `c1_market.emotion_index`（close_final 8,617 行 1991..2026-09-30）——微观事件面只有 2026-09-01 起，2019-2025 窗真断。
- L9-Z1/Z2 schema/对账卡=治理面（考结构不考数据），无 CH 序列可取。

## 四、本夜普查的两处"意外"（供 Owner 早读）

1. **个股 hfq 与指标面断在 2026-09-30，而指数/未复权/结构面到 2026-10-09**（census `oct_2026_face_status`）：
   `SELECT min(trade_date), max(trade_date), count() FROM c1_market.kline_daily_hfq WHERE trade_date >= '2026-10-01'` → **0 行**
   （逐日 `trade_date >= '2026-09-24'` GROUP BY → 09-24/5,562、09-28/5,562、09-29/5,564、09-30/5,566，此后再无）；
   `technical_indicator` 同期 `WHERE trade_date BETWEEN '2026-09-24' AND '2026-10-09'` → max **2026-09-30**；
   `emotion_index WHERE stage='close_final' AND trade_date >= '2026-10-01'` → **0 行**。
   同期在位：`kline_daily` 10-08..10-09 / 5,917 行、`kline_index` 1,190 行、`stk_limit` 6,029 行、`money_flow` 16,717 行；
   日历 `SELECT countDistinct(cal_date) FROM c1_market.trade_calendar WHERE is_open=1 AND cal_date BETWEEN '2026-10-01' AND '2026-10-09'` = **2 个交易日**。
   → 结论：**后复权(hfq)与因子/指标链缺 2026-10-08、10-09 两个交易日**，凡 OOS 尾端伸到 10 月且绑 hfq/technical_indicator 的卡被这一条判死（禁挪窗）；
   补 hfq/指标 10 月两日即解锁（属数据面施工，非本车道权限）。
2. **板块/行业成分 PIT 面是结构性空洞**：三张 SCD 表 `sector_constituent`（valid_from 2026-07-23 起）、
   `concept_board_constituent`（2026-08-10 起）、`industry_class`（2026-08-03 起）**都没有 2026-07 之前的成分历史**；
   真历史只在两张替代表：`c1_market.sector_constituent_sw_history`（`min(in_date)=1990-12-10 .. max=2026-09-18`，46,133 行事件流水）
   与 `c1_market.index_constituent`（`trade_date` 2005-04-29..2026-09-30，705,916 行 / 5 指数 / 5,555 标的）；
   `sector_constituent_snapshot FINAL` 只 19 个 snapshot_date（2026-09-14..2026-10-09，1,922,366 行）。
   → 11 张绑 `sector_constituent` 的卡判 not_scorable 是"卡绑错了面"，**不是矿没有**；
   换绑/建 PIT 重建层（用 sw_history 的 in_date/out_date 流水回放，≈60-120 行）属 W4 运行期绑定工作，须由卡作者改 data_binding（本车道无权改），
   且**这不是挪窗**。另：`TDM-X-S2-02/calibration/03_新股首日分层卖出三臂` 绑 `c3_fundamental.ipo_calendar`（实测 `system.tables` 无此表），
   而 `c1_market.ipo_calendar` 存在（11,176 行，列含 subscribe_date/list_date/trade_date）→ 疑似**前缀错库**，同样属改绑不属挪窗。

## 五、scorable_with_build 的建法（族级归并，逐卡行在 census 内已写全 gap）

134 张里的主面组合分布（census `signal_source` 归并）：单 `kline_daily_hfq` **44** ｜ `hfq+kline_index+stk_limit` 9 ｜
`kline_index+kline_sector_880` 7 ｜ `hfq+technical_indicator` 5 ｜ `crypto_kline_daily` 4 ｜ `kline_daily` 4 ｜ `hfq+stk_limit` 4。
共性缺口只有一个：**`run_card()` 不自取数**。所以工作量分两段：

- **A 段（一次性，全卡共用）**：`signal_spec/target_spec` 注入适配层——按 census 每行 `measured_faces` 的
  `表.列 + 业务日期列 + 窗`，用 `ch_query_df` 拉面板 → 对齐 symbol×trade_date → 目标序列用
  `close` 对同标的次一交易日（`trade_calendar is_open=1` 排序取 shift(-1)，**禁按自然日/行号 shift**）算收益。
  量级 ≈40-60 行＋同量测试。所有卡的 now/build 差都收敛到这一段。
- **B 段（逐卡派生）**：census `gap_or_build_note` 已写口径与量级三档——
  ≈30-50 行（单表窗口派生：MA/斜率/动量/分位/zscore）、≈60-120 行（多表联接＋分桶：成分×价量、事件×涨停池）、
  ≈150+ 行（臂回放/撮合层：净值、持仓、再平衡、成本五档敏感性）。
  族级要点：calibration=信号×前向收益的 IC/单调性；comparison=两臂 NAV（须同一撮合器同一成本档）；
  ablation=全链 vs 摘除臂（需要**链上件可跑**，非纯数据面）；shadow=影子臂产物（`sim_*`/`decision_daily` 实测只
  2026-09-16 起 / 138 行，`sim_trade_log` 仅 84 行 → shadow 族 12 张全部落 build，且多数还需先有影子链落库）。
- **PIT 纪律（写进每卡 build note 的硬约束）**：成分/行业/停牌/ST/涨跌停规则都用
  `valid_from/valid_to` 或 `trade_date` 当时值，禁当前快照回溯；`ReplacingMergeTree` 表读数一律带 `FINAL`
  或显式版本列（本场 `stk_limit` FINAL 与 `total_rows` 差 22,346 行即未合版本实例）。
- **日历对齐**：窗内连续性用 `c1_market.trade_calendar`（列 `cal_date`、`is_open=1`）实测；A 股 2026-10-01..10-07 休市为 0 交易日。

## 六、未尽事项（如实，禁装完成）

1. **未普查清单**：仅 §〇 的 2 张半截 YAML（他道在途写入）。除此之外 256/256 全判，`undetermined=0`。
   复跑 `.runtime/tmp/l8b_census_v7.py`（约 4-6 分钟，478 探针）即把新增卡与修好的 2 张一并纳入。
2. `empty` 骨架卡（186 张，任务口径不含）：其中绝大多数无 window/data_binding，属"先落卡后绑数"面，不计入三态。
   卡册总文件已 454 且仍在长，**本普查是 07:53:05 快照**，任何卡改动即失效——分数册出分前须重跑普查做卡面一致性对齐。
3. 连续性未验证的超大表（tick_data/technical_indicator/kline_1min/kline_5min/tick_depth_1）：只判了全表 min/max 覆盖，
   未做窗内逐日 count（探针代价）；若某卡对中段缺日敏感，需专项补测（可加 `countDistinct(toDate(x)) WHERE 窗` 单表跑）。
4. 视图 `c1_market.v_kline_sector_880_named` 的 `total_rows` 在 `system.tables` 返回 `\N`（View 无行数统计），
   覆盖窗按底层实测 2020-03-17..2026-10-08 登记；行数需 `count()` 专项。
5. DS→CH 表映射缺口（`capital.margin` 这类逻辑实体名，81 个节点有 data_refs、334 条 DS）：
   本车道只做只读判定，未建映射册；它是 10 张"无数据面"卡与 8 张 L1-S0/S3 卡能否解锁的前置。
6. 断言阶梯留痕：`python -m zephyr.library.lookup state` 在本工棚**可用**（两源 no hits），与总令中"工棚版可能无 state 子命令"
   的先验不同；已同时跑 git log/--grep 与 docs/_working grep 双保险（见 §一.8）。


---

# 续战班续读段（st-nightmine2-20261010，2026-10-10 12:2x 实测；14:0x 重建——原副本遭共享暂存区清扫失踪，内容自会话上下文全额复原）

> 本段=L8b 断供结论的 4 小时后现读更正 + T2 表族级联补数方案（D7 申请包四件套）。原 §四.1 断供结论除特别注明外仍然成立。

## 七、现读更正（对 §四.1 逐条）

| 面 | §四.1 快照（07:5x） | 12:2x 现读 | 判读 |
|---|---|---|---|
| kline_daily_hfq | 10 月 0 行 | 10 月仍 0 行；weekly/monthly_hfq 已到 10-09（伴生 __preeng_backup_20261007 备份表） | **st-acure 族（活跃心跳在册）正在修 hfq 族且 weekly/monthly 腿已收**；daily 腿归其处置，本班禁双开 |
| technical_indicator（daily 等 7 期） | max 09-30 | 夜批（tilib_dwm_shard_runner，02:30 起）全窗回填在跑（2021-01-01~2026-10-10，100 标的/片，25/54 片 12:0x 完成）；**已完成片抽样（shard0 标的）max 仍 09-30** | 断供在**源侧**：回填腿到位也写不进 10 月行，源恢复前补数无对象 |
| technical_indicator weekly/monthly（period 列同表） | （未单列） | max=**09-15**（月度连 09-30 月末 bar 都缺） | 比日腿更陈旧 2 周，级联补数必查项（WO-004 同族矛盾防复发） |
| emotion_index | close_final 10 月 0 行 | 10 月仅 pre_open 腿 6 行（至 10-09），**close_final 仍 0 行** | 断供结论成立（此前"已补到 10-09"系 pre_open 腿误读，已在检查点纠正） |

## 八、T2 表族级联补数方案（D7 申请包四件套）

**窗**：
- TI 日内 6 期+daily：2026-10-01..2026-10-10（日历实测 2 个交易日 10-08/10-09）
- TI weekly：2026-09-16..2026-10-09（约 4 根周 bar，含 09-15 后漏更段）
- TI monthly：2026-09-16..2026-10-09（09 月末 bar+10 月 Partial bar，**月内未完结月 bar 出不出须先声明口径**——禁默认出）
- emotion_index close_final 腿：2026-10-08..2026-10-09（2 交易日）
- hfq 族：**不在本方案内**（st-acure 在飞域，等其 daily 腿收官+族内对拍自证）

**行数**（执行时以探针实测为准，此为量级预估）：daily≈5.4K 标的×2 日；weekly≈5.4K×4；monthly≈5.4K×2；emotion close_final≈个位数指数×2 日。TI 值级跳过过滤（backfill 脚本内建）命中时行数下浮。

**验收**：
1. 逐 period `max(trade_date)`=预期收窗日（daily=10-09；weekly=10-09 所在周 bar；monthly=按已声明口径）
2. 抽 3 片已完成标的复探：行数=标的数×交易日数（源侧恢复后才可满足）
3. 级联对拍（WO-004 防复发硬门）：抽 20 标的，weekly 聚合列 vs 日线重算一致率 ≥99%，monthly 同法
4. 普查复跑：04_exam_feasibility_census 重跑（生成器在案），scorable_now 与 blocked_on_data 复动面只增不删

**解锁清单**：
- 前置闸 A：夜批在跑腿收官（runner PID 34644 退出+分片 state 全 done）——禁双开红线
- 前置闸 B：源侧恢复实证（任一已完成片标的写出 10-08/10-09 行）——否则补数无对象，改报源断工单
- 解锁面：绑 TI 的 blocked_on_data 卡按普查复跑结果解锁；emotion close_final 卡（L1-S3 先锋四态等）随腿恢复解锁
- hfq 卡解锁面：归 st-acure 处置宣告后对账，本班不代解

**执行门**：本方案为 D7 申请包，实际补数执行=前置闸 A∧B 成立后按上窗小批跑（首日 2 交易日×daily 单期试跑→对拍→放量），GPU 面零占用（CH/CPU 作业）不占 23:00 W1 窗。

## 九、监测义务履行（本班）

- process_reaper_keep.txt 已补登 backfill_night.ps1 / tilib_dwm_shard_runner（10-10 12:0x，此前仅 backfill_technical_indicator_dwm 与 ti_shard_selfheal_driver 在册，wrapper/runner 裸奔=半程被收割风险）
- 监测点位：data/runtime/dwm_shard_state/daily_shard_NNN.json（片级 exit/elapsed）；源侧恢复探针=§七 行 2 复跑
