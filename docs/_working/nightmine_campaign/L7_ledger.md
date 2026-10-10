---
ttl: task_bound
title: L7 挖矿车道台账——entry_flow/L9 知识层 45 节点 + 币圈镜像 TDM-C 线
created: "2026-10-10"
sid: st-nightmine-20261010
lane: L7
family_id: NIGHTMINE-CAMPAIGN
---

# L7 台账（逐节点六向结论，机读优先）

工作根=工棚 `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`。
判据真源=`docs/_working/nightmine_campaign/01_mining_brief.md`（卡可运行判据 §2、六向 §3、探针 §4）
+ `docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` v1.7.0（§2 六向 / §3 结构枯竭 / §5 四闸 / §7.5 断言纪律）。
卡模板真源=`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__02_涨停家数.yaml`。

## 〇、节点全集与现存卡态（实测，非凭记忆）

`ls docs/03_modules/_domain_backtest/exam_cards/entry_flow/L9/` = **45 个骨架件**（全部
`generated: true` / `status: empty`，受保护禁手改）：A01..A17(17) + B01..B10(10) + C01..C03(3)
+ G1..G5(5) + V1..V3(3) + D1/D2(comparison) + E1/E2(comparison) + Z1/Z2(shadow) + AGG(ablation)。
⇒ 本车道新卡一律另建 `__<family>__NN_<中文名>.yaml`，NN 从 02 起。

节点全文字段已逐个从 `config/trading_decision_map.yaml` L4981-6161 实读（禁凭记忆兑现）。
币圈面（`market≠cn_a` 全扫）= TDM-C-L1/L2/L3/L4 四节点（L4890-4977，全 `red_reason: not_built`，
algo_note_zh 自陈"v1 空壳，等 A 股链路验证后移植"），无 L9 层币圈节点 ⇒ 本车道币圈镜像=
**A 股 L9 源线的 crypto 镜像支线**（单列卡，`market: crypto` 与目标口径与 A 股卡分开写）。

族分布先验（按题型族级挖矿，同族一次挖到底跨节点复用）：
| 族 | 节点 | 共同题型 | 卡族 |
|----|------|---------|------|
| A 档在产源线 | A01-A17 | "该源线信号对次日/多日目标有无预测力" | calibration 为主 |
| B 档外采未接 | B01-B10 | 同上，但**渠道未接**（数据可得性是题眼） | calibration，断供标 blocked_on_data |
| C 档无渠道 | C01-C03 | 同上，无机械接入渠道 | calibration + blocked |
| G 图谱供给侧 | G1-G5 | 结构先验/传导证据是否有增量解释力 | calibration + ablation |
| V 状态快照 | V1-V3 | T-1 快照就绪与时戳分层是否被违反 | calibration(就绪率) + ablation |
| D/E 决策与验证 | D1/D2/E1/E2 | 组合挖掘/预注册/考试链/回传四环节 | ablation |
| Z 治理 | Z1/Z2 | schema 强制与净零对账 | ablation |
| AGG | AGG | 知识供给汇聚整环 | ablation（作业簿明令） |

## 一、数据可得性总探针（本车道题眼，先跑后立卡）

探针命令原文（作业簿 §4 形，`ch_query_df` 走 fexam 只读层，禁裸 duckdb；临时件
`D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/l7_probe_tables.py`+`l7_probe_cols.py`）：

```
python -c "
import sys; sys.path.insert(0,'scripts/backtest')
from fexam.ch_data import ch_query_df
r=ch_query_df(\"SELECT min(toString(<datecol})) a, max(toString(<datecol})) b, count() n, uniq(<datecol}) u FROM <db.table>\")
"
```
（注：`ch_query_df` 返回列名是 `c1/c2/c3` 位置名而非别名——首版脚本按 `df['name']` 取列
全抛 KeyError，已改位置取列；**空结果先判静默失败**这条在本车道第 1 次探针就命中，如实记档。）

CH 库全集实测=`['c0_meta','c1_backtest','c1_market','c3_fundamental','default','system',...]`（4 业务库）。

### 1.1 有长史（可立 preregistered 卡）

| 表 | 覆盖窗 | 行数 | 独立日期 | 归属节点 |
|----|--------|------|---------|---------|
| c1_market.kline_daily_hfq | 1990-12-19..**2026-09-30** | 10,098,785 | 8736 | A01（滞后 7 交易日，见 1.3） |
| c1_market.kline_index | 1990-12-19..2026-10-09 | 3,104,162 | 8907 | A01/V1 目标面 |
| c1_market.kline_1min | 2021-09-01..2026-10-09 | 1,493,285,247 | 1233 | A01 分钟 |
| c1_market.kline_60min | 2021-09-01..2026-10-09 | 24,750,376 | 1233 | A01 分钟 |
| c1_market.kline_sector_880 | 2020-03-17..2026-10-08 | 785,204 | 1590 | A03 |
| c1_market.index_valuation_daily | 2010-01-04..2026-10-08 | 16,228 | 4068 | A04（pe_pct/pb_pct/erp_pct/cape_5y_pct） |
| c1_market.stock_daily_basic | 2021-01-04..2026-10-09 | 7,118,522 | 1395 | A04（仅市值/换手，**无 PE/PB**） |
| c3_fundamental.income_statement | announce_date 1995-01-05..2026-09-02 | 346,176 | 6701 | A05 |
| c3_fundamental.financial_indicator | announce_date **1970-01-01**..2026-09-12 | 386,510 | 7157 | A05（1970=epoch 脏值，质量画像必挂） |
| c1_market.money_flow | 2021-01-04..2026-10-09 | 5,993,328 | 1225 | A06 |
| c1_market.dragon_tiger_seat | 2022-01-04..2026-10-09 | 622,365 | 1152 | A06 |
| c1_market.alt_shipping_index | 1988-10-19..2026-10-09 | 49,872 | 9579 | A08（BDI/BCI 系 index_code） |
| c3_fundamental.news_data | publish_time 2010-01-02..2026-10-10 | 8,219,134 | 149090 | A09 |
| c3_fundamental.news_sentiment_score | publish_time 2010-01-02..2026-10-04 | 7,947,739 | 146659 | A09（polarity/label，caliber_version 在列） |
| c1_market.macro_data | report_date 1993-03-31..2026-10-09 | 51,623 | 4610 | A10 |
| c1_market.macro_data_vintage | report_date 2021-01-01..2026-09-23 | 16,091 | 1351 | A10（vintage/pub_ts PIT 面） |
| c1_market.us_index | 1993-01-29..2026-10-08 | 22,645 | 8481 | A10 |
| c1_market.a50_futures_daily | 2016-08-29..2026-10-08 | 2,623 | 2623 | A10 |
| c1_market.cftc_positioning | report_date 1986-01-15..2026-09-29 | 81,396 | 1939 | A10 |
| c1_market.kline_global | 2014-11-07..2026-10-08 | 13,133 | 3109 | A10 |
| c1_market.futures_warehouse_receipt | 2014-05-19..2026-10-09 | 2,925,905 | 3013 | A11（仓单=库存代理，EIA 缺位替代） |
| c1_market.alt_typhoon_track | issue_ts 2004-08-07..2026-10-09 | 196,939 | 25745 | A12 |
| c1_market.alt_sz_ground_obs | ddate 2015-01-01..2026-10-09 | 1,143,532 | 4270 | A12（**仅深圳**，适配闸） |
| c3_fundamental.shareholder_count | announce_date 1993-01-12..2026-10-09 | 514,690 | 7001 | A13（富矿） |
| c1_market.hl_funding_history | funding_time 2023-05-12..2026-10-09 | 4,785,877 | 29335(8h) | A15 + 币圈镜像 |
| c3_fundamental.research_report | publish_date 2017-01-02..2026-09-30 | 146,940 | 3129 | A17（rating/rating_change 在列，富矿） |
| c3_fundamental.consensus_daily | 2017-01-03..2026-09-30 | 6,829,376 | 2367 | A17（eps_consensus/std/n_buy..n_negative） |
| c1_market.emotion_index | 1991-06-10..2026-10-09 | 8,661 | 8622 | V2（stage=六段相位） |
| c1_backtest.regime_snapshot_history | 2019-04-01..2026-10-09 | 3,635 | 1824 | V1（p_r1..p_r12/dominant） |
| c1_backtest.regime_state_anchored | 2017-07-11..2026-10-09 | 4,488 | 2244 | V1 |
| c1_market.sector_state | 2022-09-01..2026-10-08 | 432,088 | 992 | V3 |
| c1_market.crypto_kline_daily | 2025-08-08..2026-10-08 | 19,801 | 427 | 币圈镜像（**已有真数据**） |
| c1_market.crypto_shadow_gate | 2026-09-11..2026-10-08 | 20 | 20 | 币圈镜像 TDM-C-L1 |

### 1.2 短窗/空表（断供史，卡照立并标 blocked_on_data）

| 表 | 实测 | 影响节点 |
|----|------|---------|
| c1_market.tick_data | 2026-01-05..2026-10-08 仅 **182** 交易日（3.94B 行） | A02 IS 窗全空 |
| c1_market.l2_tick | **rows=0**（空表） | A02 |
| c1_market.tick_depth_5 | 2026-07-24..2026-09-30 仅 22 日 | A02 |
| c1_market.auction_snapshot | 2026-06-01..2026-09-30 仅 56 日 | A02 |
| c1_market.auction_book | 2026-07-21.. 30 日 | A02 |
| c1_market.stock_valuation | **rows=0**（空表） | A04 个股横截面 |
| c1_market.daily_valuation | 2026-08-03..2026-09-30 仅 42 日 | A04 个股横截面 |
| c1_market.edb_data | **rows=0**（空表） | A10 备援 |
| c1_market.hk_connect_flow | 2014-11-17..**2024-08-16 断供**（2264 日后停止） | A06 北向 |
| c1_market.northbound_hold_snapshot | 2024-09-30..2026-06-30 仅 **8** 个日期 | A06 北向 |
| c1_market.factor_signal | **rows=0**（空表） | AGG/D1 |
| c1_market.alt_stock_comment | 2026-09-11..2026-10-09 仅 **15** 日 | A07 |
| c1_market.stock_hot_rank | 2026-08-04.. 38 日 | A07 |
| c1_market.sentiment_panel | 2026-09-01.. 39 日（长表 metric/value） | A09/V2 |
| c1_market.news_sentiment_window | 2026-02-24..2026-10-08 仅 200 日 | A09（聚合窗口径） |
| c1_market.market_breadth_snapshot | 2026-08-24.. 26 日 | A01/V1 广度 |
| c1_market.limit_up_down | 2026-07-20.. 5397 行（**在册先例，复核实测一致**） | A09 广度面 |
| c1_market.board_index_tick | 2026-09-15.. 3047 时间戳 | A03 |
| c1_market.kline_sector | 2025-07-18.. 198 日 | A03 |
| c1_market.sector_fund_flow | 2026-09-15.. 25 日 | A03 |
| c1_market.concept_board_constituent | valid_from 2026-08-10.. 35 日 | A03/G4 |
| c1_market.concept_board / concept_sector | 静态 750/375 行（valid_from 轴） | A03/G4 |
| c1_market.weather_data | 2026-08-04.. 40 日（11953 行） | A12（预报型，历史不可回填） |
| c1_market.road_freight_index | 2025-09-19..2026-08-21 仅 22 日 | A08 辅线 |
| c1_market.commodity_spot_price / commodity_futures_main | 2026-09-01.. 23 日 | A11 辅线 |
| c3_fundamental.irm_interactive_qa | question_date 2026-06-19..2026-09-16 仅 **67** 日 / 500 行 | A14 |
| c3_fundamental.irm_interactive_extracted | **74 行** | A14 |
| c3_fundamental.ir_activity_record | publish_date 2026-09-17..2026-09-18 仅 **2** 日 / 30 行 | A14 |
| c3_fundamental.analyst_forecast | report_date 2026-07-22.. 52 日 | A17（被 consensus_daily 替代） |
| c1_market.hl_perp_snapshot_daily / hl_oi_snapshot_daily | 2026-09-18.. 各 18 日 | A15 持仓/OI |
| c1_market.hl_liquidation_raw | **17 行** | A15 清算 |
| c1_market.l9_readiness_daily | 2026-09-15..2026-10-09 仅 **5** 日 / 195 行 | AGG（ablation 基线缺史） |
| c1_backtest.node_verdict | 58 行 | E1 |
| c1_backtest.hypothesis_precheck | 414 行 | D1 |
| c1_backtest.strategy_screen | 1406 行 | D1 |
| c1_backtest.decision_daily | 2026-09-16..2026-10-12 仅 9 日 / 138 行 | E2 |
| c1_market.judgment_daily_plan / _next_day_forecast / _intraday_market_state / _plan_verification | **12 / 6 / 40 / 24 行** | V1/V2/V3（judgment 台账近空） |
| c1_market.market_signal_history | 2026-08-28..2026-09-04 仅 3 日 | E1 |

### 1.3 断供史与质量画像（闸4"可得≠可用"）

1. **A11 EIA 从未落 CH**（本题眼最硬一条）：`system.tables` 全库筛 `%eia%/%oil%/%inventor%` = **(none)**；
   `python -m zephyr.library.lookup "EIA" --limit 6` 命中 6 条：`docs/03_modules/_domain_data/algo_flow/eia_provider.yaml`
   （真源 `src/zephyr/data/implementations/eia_provider.py`，Provider **已建**）+ 5 条
   `data/failures/*_eia_petroleum_incremental_*.json`。失败样本原文（2026-10-08 最新）：
   `{"task_id":"eia_petroleum_incremental","source":"eia","error":"HTTPSConnectionPool(host='api.eia.gov', port=443): Read timed out. (read timeout=30)","level":"ERROR","timestamp":"2026-10-08T10:01:22+00:00"}`
   ——`data/failures/` 内 eia 失败件 **8 个**（2026-08-04/08-16/08-18/08-20/08-27/09-14/09-28/**10-08**），
   即采集每周触发、每周超时、**零落库**。⇒ A11 标 `blocked_on_data`（缺 EIA 表整段），
   同时另立仓单库存代理卡（futures_warehouse_receipt 3013 日）为可考面。
2. **B/C 档 13 源线 = CH 无任何对应表 + 馆查零命中**（双正查）：
   `python -m zephyr.library.lookup "<kw>" --limit 6` 对 卫星影像/招聘/电商价格/招投标/雪球/Reddit/APP榜单/
   信用卡/客流/直播电商 均输出 `(no results for ...)`（逐条原文见台账二各节点行）；
   叠加 `system.tables` 关键字筛 `%satellite%/job_/%ecommerce%/%tender%/%xueqiu%/app_%/%foot_traffic%`=(none)。
   ⇒ 13 张卡全部 `status: blocked_on_data`，`data_window_evidence` 写死缺什么。
3. **kline_daily_hfq 落后 kline_index 7 个交易日**（hfq max=2026-09-30 vs index max=2026-10-09）=
   复权因子链未追平，A01 面板考试右端须截 2026-09-30，否则静默 NaN。
4. **financial_indicator.announce_date 最小值 = 1970-01-01** = epoch 哨兵脏值（PIT 排序会把这类行
   排到最前→前视污染）。A05 卡 MUST 带 `announce_date > DATE'1990-01-01'` 过滤门柱。
5. **income_statement 双列 `announce_date` 与 `actual_announce_date`** 并存：PIT 真值只可取
   `actual_announce_date`（计划披露日≠实际披露日）。A05 卡把这条写进门柱。
6. **hk_connect_flow 断供 2024-08-16**（2264 日整段历史在，之后零行）+ `northbound_hold_snapshot`
   仅 8 个日期 ⇒ 北向族整体进入"历史可读/现势不可得"态，A06 北向支卡标 blocked_on_data。
7. **l2_tick / stock_valuation / edb_data / factor_signal 四表 rows=0** = 建表未落数（schema 在、
   数据空），是"字段在≠数据可得"的机械样本，卡内标 blocked_on_data 并给建表-空表二元证据。
8. **AGG 基线缺史**：`l9_readiness_daily` 仅 5 个交易日读数（2026-09-15 起，195 行）——
   ablation 卡可写但 `window` 只能取"就绪率对次日信号产出"的近端窗，
   且 MUST 在卡内声明基线样本不足（n≈5 日×29 源线），不得冒充分布性结论。

### 1.4 币圈镜像实测（本车道独有一支）

- 在册先例=`docs/_working/2026-09-11-crypto-shadow-mvp.md`（§5 记 OKX 端点环境级阻断、
  §7 定 UTC 日界与 C-L1 三档口径、§4 声明"合成样本烟测，非市场结论"）；
  缺口册=`docs/_working/matrix_campaign/mining/st_crypto_mining.md`（"全域 L 级缺口：无 crypto 行情载荷"，
  并记 Owner 门位在案议题"F51 币圈退役"）。
- **本车道实测推翻"无行情载荷"半条**（正存在断言同须指针，SOP §7.5.3）：
  `c1_market.crypto_kline_daily` **rows=19801 / 427 交易日 / 2025-08-08..2026-10-08**（含
  `is_universe_eligible`/`universe_rank`/`quote_volume`），`c1_market.crypto_shadow_gate`
  rows=20 / 2026-09-11..2026-10-08（含 btc_close/ma200/ma_slope_10d/altseason_ratio/
  eth_btc_ratio/fng_value/shadow_tier）⇒ 真实首跑已落地，网络闸已过（表名亦为
  `crypto_shadow_gate` 而非 MVP 文中的 `crypto_shadow_gate_c_l1`）。
- 但 **427 日 < 机构三件套最低样本**（无 IS/OOS 双段、无牛熊分段）⇒ 币圈镜像卡一律
  `blocked_on_data`（缺 IS 段），并把"需 ≥500 交易日且有牛熊两段"写为解锁条件。
  唯一例外：`hl_funding_history` 3.4 年史 → 币圈镜像**只**在资金费率题上可立 preregistered 卡。
- 镜像链分列纪律：A 股卡 `market: cn_a` + 目标=沪深300 次日收益；币圈卡 `market: crypto`
  + 目标=BTC/ETH 次日收益（UTC 日界，7×24 无 T+1、无涨跌停），两卡禁共用 target。

## 1.5 族级外部引用（§3 同矿脉不重复挖，逐条过 §5 闸1 来源可溯）

| 族 | 结论 | 来源（URL｜发布方｜年份） |
|----|------|--------------------------|
| 事件研究口径（A05/A12/A13/A14/A17 共用） | 事件窗/估计窗/异常收益 CAR 为低频事件信号标准口径；国际文献综述确认该方法论仍在用且需处理跨市场日历 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9264305/ （NCBI PMC 收录期刊｜2022）；https://cqvip.com/doc/journal/00164JH34JD8BJP36FCO3J9V6PBO6J1XM7R （维普期刊库｜2025，题录级，收费墙只登记题录） |
| A17 研报评级/一致预期修正 | 卖方评级调整与目标价含增量信息；A 股"分析师预期调整"有成熟因子化做法（上调/下调事件+一致预期修正幅度） | https://finance.sina.cn/2020-09-14/detail-iivhuipp4303960.d.html （新浪财经｜2020-09-14）；https://www.tandfonline.com/doi/full/10.1080/23322039.2025.2494129 （Taylor & Francis, Cogent Economics & Finance｜2025）；https://www.tandfonline.com/doi/full/10.1080/23322039.2024.2423261 （同上｜2024，目标价精度） |
| A05 盈余公告漂移（中国） | A 股存在 PEAD，且公告效应受散户注意力调节（注意力低者漂移更强） | https://m.zhangqiaokeyan.com/academic-journal-cn_china-financial-review-english_thesis/0201264328717.html （China Financial Review (English) 经掌桥转载｜转载页年份 2025，原刊年待验证→状态=待验证不入图仅佐证口径）；https://wap.cnki.net/lunwen-1021005506.html （CNKI 硕士学位论文库｜2021 编号 1021005506，题录级） |
| A12 天气/气温与公司层面收益 | 极端气温对公司级股票收益有可测影响；气温冲击与收益负相关的证据跨市场存在 | https://pmc.ncbi.nlm.nih.gov/articles/PMC7922310/ （NCBI PMC｜2021）；https://ideas.repec.org/a/eee/finana/v81y2022ics1057521922000801.html （Elsevier, Journal of Financial Markets vol.81｜2022）；https://m.zhangqiaokeyan.com/academic-journal-foreign_studies-economics-and-finance_thesis/020412996235.html （Emerald, Studies in Economics and Finance｜转载页 2023） |
| A08 运价领先航运/大宗 | 贸易政策不确定性与航运风险、大宗价格存在联动；BDI 预测与相关性有中文实证传统 | https://www.sciencedirect.com/science/article/abs/pii/S1544612324016337 （Elsevier, Finance Research Letters｜2024/2025）；https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1647599/full （Frontiers in Marine Science｜2025-10）；https://doc.taixueshu.com/journal/20070048sjhy.html （中文期刊转载｜2007 原文，题录级） |
| A15 资金费率/基差与拥挤 | 永续基差与资金费率反映套利资本约束，挤升后回落可作拥挤度读数 | https://www.galaxydigital.io/insights/perspectives/btc-basis-surges-then-dips-ahead-of-us-presidential-election （Galaxy Digital Research｜2026-09-21）；https://medium.com/@gwrx2005/futures-spot-arbitrage-in-cryptocurrency-markets-a-comparative-analysis-of-strategy-design-risk-6af00109e836 （Medium 个人号｜2026-06-22，发布方弱→状态=待验证） |
| A09 媒体情绪→收益 | 快讯密度与情感极性可量化情绪并对短期收益有预测力（文本情绪因子一线做法） | https://m.zhangqiaokeyan.com/academic-conference-foreign_meeting-286090_thesis/0705014378112.html （会议论文集转载｜2023）；https://www.sinoss.net/c/2025-09-04/658991.shtml （sinoss 学术会议网｜2025-09-04） |

闸2 交叉验证：A12/A17/A08 三族 ≥2 独立来源=入图；A05/A15/A09 仅有转载页或弱发布方=
**状态=待验证**（只作口径佐证、不作数值门柱依据）。闸3 A 股适配：全部事件研究卡改
T+1 落地（公告日次一交易日才起算 CAR，禁同日）+ 涨跌停一字板剔除（A12/A13/A17 卡内写死）。

## 1.6 后端现状（④向，一行/族）

- A 档：`module_ref` 多为 null（骨架件 TDM 主图未回填），但 A01 骨架卡带
  `src/zephyr/signal_ashare/source_line/kline_momentum_criterion.py`（实测在卡内）。
- AGG：`src/zephyr/data/l9_readiness_aggregator.py`（TDM module_ref 已回填，MOD-DATA-L9AGG）。
- V1/V3：`src/zephyr/plan_engine/judgment_ledger.py`（MOD-PLAN-026，judgment 台账近空）。
- D1：`scripts/backtest/mcts_expression_search.py`（MOD-BT-202）。E1：
  `src/zephyr/trading/validation/runner.py`（MOD-TDMVAL-001）+ `ablation.py`（信号消融对照器，
  实测其语义=双权重面板重放差，非卡驱动执行器 ⇒ 本车道 ablation 卡写成"消融臂规格"而非 run_card 面）。
- G3：`scripts/entity_graph/equity_penetration.py`。Z2：`scripts/governance/reconcile_chain_refs.py`。
- A16/G5：`ig_io_edge` 部门码↔ig_node 两套 id 未打通（TDM algo_note_zh 自陈"边100%挂零"）⇒ blocked_on_impl。
- ⑤呈现：各卡只登记读数面，不施工（本车道无前端动作）。

## 1.7 断言工具实测纠偏（作业簿 §4 命令形有静默失败陷阱，如实登记）

作业簿写的是 `python -m zephyr.library.lookup state "<关键词>"`。本车道实测：
`--help` 显示该 CLI **无 `state` 子命令**（positional 只有 `query` 与旧用法 `limit_pos`），
故 `lookup state "卫星影像"` 把 `state` 当 query、`"卫星影像"` 当 limit_pos，
输出为**空**且 rc=0 —— 正是"空结果先判静默失败再下结论"的命中样本。
本车道一律改用有效形：`python -m zephyr.library.lookup "<关键词>" --limit 6`（实测有命中/有
`(no results for '<kw>')` 明确回显），下文所有负存在断言均用此形。

## 二、逐节点台账

| node_id | 六向结论(①上游/②下游/③算法/④后端/⑤呈现/⑥数据) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---------|-----------------------------------------------|--------|--------|-----------|-------------|
| TDM-E-L9-A01 | ①价量趋势与动量两句判据（N 日收益）→2 张卡（日线截面动量/分钟 RV+偏度）②下游=TDM 出边 feed→L9-AGG（TDM:L6393「日线/分钟行情供给」，realtime/daily, lag=hours, pit_proof=K线落定不修订/复权因子禁进PIT窗）③同族近亲=L1-S2 涨停家数卡（响应曲线/时滞/条件稳定性三件套直接复用）④后端 `src/zephyr/signal_ashare/source_line/kline_momentum_criterion.py`（A01 骨架卡 module_ref 实测在盘）⑤只登记 ⑥hfq 1990-12-19..2026-09-30/10,098,785 行、kline_index ..2026-10-09、kline_1min 2021-09-01../1,493,285,247 行；**hfq 右端比 index 滞后 7 交易日**已写进卡 right_edge_note | 2 | calibration×2 | 否（长尾：隔夜跳空、分钟非同步跳动、周-月频动量反转未立卡） | — |
| TDM-E-L9-A02 | ①"日内微观结构能否预测次日方向与冲击成本"=两问两 target ②下游=AGG（realtime/0d 边，TDM:L6394）③冲击成本曲线口径外部来源仅获聚合站=待验证，数值门柱不依赖外部 ④无 module_ref ⑤只登记 ⑥**断供题眼**：tick_data 仅 182 日、l2_tick **rows=0**、tick_depth_5 22 日、auction_snapshot 56 日、auction_book 30 日⇒IS 窗全空，卡标 blocked_on_data 并写死缺段+两条解锁路径（外采历史包=Owner 花钱门位 / 降级用 kline_1min 另立新卡） | 1 | calibration×1 | 否（长尾：五档撤单队列、封板瞬间订单流） | blocked_on_data：2019-01-04..2025-09-09 全段无 tick/l2/竞价 |
| TDM-E-L9-A03 | ①"板块轮动与强弱持续性能否领先个股"→本卡答前半（持续性），后半（领先个股）登记长尾 ②下游=AGG+L2 板块线（TDM:L6395）③RRG/相对强弱一线做法仅转载页=待验证；三件套复用 ④无 module_ref ⑤只登记 ⑥实测 kline_sector_880 2020-03-17..2026-10-08/1590 日/785,204 行可用；kline_sector 198 日、sector_snapshot 33 日、sector_fund_flow 25 日、board_index_tick 3047 时间戳、concept_board 750 行静态、concept_board_constituent valid_from 2026-08-10 起 35 日⇒**概念面整体无 IS 段**，故改用 880 行业线并声明 | 1 | calibration×1 | 否（长尾：板块→个股领先卡、概念资金流卡（待数据）） | — |
| TDM-E-L9-A04 | ①"估值横截面能否区分未来收益"→拆 2 卡（指数时序 02 / 个股横截面 03）；**水平 vs 增量是本节点最关键判据设计**（慢变量水平值配次日 target 必假失败，故 02 卡考 erp_pct 5 日增量，水平版登记长尾）②下游=AGG（TDM:L6396）③ERP/分位口径直接来自表列（cape_5y_pct/erp_pct 在册实测）④无 module_ref ⑤只登记 ⑥index_valuation_daily 2010-01-04..2026-10-08/4068 日；**stock_valuation rows=0、daily_valuation 仅 42 日、stock_daily_basic 无 PE/PB 列**⇒个股横截面断供 | 2 | calibration×2 | 否（长尾：行业级估值分位、破净率/buffett_ratio 面） | 03 卡 blocked_on_data：个股估值历史零覆盖 |
| TDM-E-L9-A05 | ①"基本面改善能否被定价滞后捕捉"→SUE 事件研究，估计窗[-210,-11]/事件窗[0,+5]/[0,+20]/[0,+60] 一次写死 ②下游=AGG+L3 选股（TDM:L6397 quarterly/T-1，按公告日 PIT）③事件研究口径双源（PMC9264305 2022＋维普题录），中国 PEAD 仅转载=待验证态（只作口径不作数值依据）④无 module_ref ⑤只登记 ⑥income_statement announce_date 1995-01-05..2026-09-02/346,176 行；**financial_indicator.announce_date 最小 1970-01-01=epoch 脏值**⇒PIT 过滤写进门柱；表含 announce_date 与 actual_announce_date 双列⇒强制实披露日 | 1 | calibration×1 | 否（长尾：毛利率改善、ROE 杜邦分解、业绩快报抢先度三向） | — |
| TDM-E-L9-A06 | ①"主力/大单净流向能否预测短期方向"→2 卡（money_flow 截面 / 北向时序）②下游=AGG（TDM:L6398）③**防共线门柱**：表内同时有 pct_change，资金流分档由单笔金额机械构造⇒与当日涨幅天然共线，卡写死"残差化后才算主判据"（本车道③向最重要结论）④无 module_ref ⑤只登记 ⑥money_flow 2021-01-04..2026-10-09/1225 日/5,993,328 行；**hk_connect_flow 断供于 2024-08-16、northbound_hold_snapshot 独立日期仅 8 个**⇒北向支线 blocked_on_data，并写明"IS 可算/OOS 截断"这一非典型断供形态 | 2 | calibration×2 | 否（长尾：dragon_tiger_seat 1152 日长史=下一富矿；margin_trading 505 日融资余额未挖） | 03 卡 blocked_on_data：北向 OOS 段零覆盖 |
| TDM-E-L9-A07 | ①"机构评级变化能否领先股价"→评分变化/机构参与度/排名跃升/关注度四读数入一卡 ②下游=AGG（TDM:L6399，快照日更不修订）③评级领先性来源=转载页=待验证 ④无 module_ref ⑤只登记 ⑥alt_stock_comment **仅 15 个独立日期**、stock_hot_rank 38 日；馆查 `python -m zephyr.library.lookup "千股千评" --limit 6`→唯一命中 `TBL:ch:c1_market.alt_stock_comment`（无回填件）⇒**快照型"只能向前积累"断供**已归类（与 limit_up_down 同型不同成因） | 1 | calibration×1 | 否（长尾：评级迁移矩阵、覆盖机构数变化） | blocked_on_data：历史不可回填，现 15 日 |
| TDM-E-L9-A08 | ①运价长史但 target 受 880 起点约束⇒窗口按 target 侧切（禁拿 1988-2019 冒充已考）②下游=AGG+L1 情绪面（TDM:L6401，daily/T-1，发布日锚定）③外部双源（FRL 2024 + Frontiers Marine 2025）过闸2；时滞判据反直觉设计=**峰值落 t+5 或更晚才算有领先力**，只落 t+1 判"已充分定价"为有效负结论 ④无 module_ref ⑤只登记 ⑥实测 BDI 14625 行 1988-10-19..2026-10-09、BCI/BSI/BDTI/BCTI 各 2006 起；**HRCI 断供 2011-08-23、BHMI 仅 2 行**；road_freight_index 22 日⇒公路运价不可考；目标面 881449 航运港口/880728 航运概念/880468 港口 均经视图实测存在 | 1 | calibration×1 | 否（长尾：BDTI 对油运细分、运价波动率面） | — |
| TDM-E-L9-A09 | ①判据两句（极性预测次日 + 密度作注意力放大）②下游=AGG（realtime/0d，TDM:L6402 聚合窗须右闭）③外部来源仅转载页=待验证态，门柱全靠内部字段实算 ④无 module_ref ⑤只登记 ⑥**本节点反直觉富矿**：明细 news_data 8,219,134 行（2010-01-02..2026-10-10）+ news_sentiment_score 7,947,739 行（打分覆盖 96.7%，缺 271,395 条）⇒预聚合表 news_sentiment_window **仅 200 日**，故改从明细现算；sentiment_panel 39 日弃用；caliber_version 列在表⇒跨版本禁拼接已写进 frozen_note | 1 | calibration×1 | 否（长尾：个股级 related_symbols 面板卡、新闻主题事件流） | — |
| TDM-E-L9-A10 | ①拆五因子单跑（A50/VIX/利差/汇率/DXY），禁先合成"全球风险指数"（不同半衰期糊平）②下游=AGG（daily/T-1，FRED 发布日锚定+修订挂 vintage）③正交化门柱（A50 残差化后再算 VIX IC）来自④/⑥联读 ④无 module_ref ⑤只登记 ⑥**重大纠偏**：FRED 族（VIX/T10Y2Y/DGS/USDCNY/DXY）实测全部起 **2021-08-16**（约 1280 观测），非节点自陈的长史⇒统一 IS 起点 2019 不可用，卡内如实内缩并声明牛段不可考；月频（CPI/FEDFUNDS/PAYEMS）仅约 60 点不足分桶；macro_data_vintage 1351 日带 vintage/pub_ts ⇒ PIT 门柱有承载；**edb_data rows=0**（备援空表）；a50_futures_daily 2016 起 2623 日、us_index 1993 起 8481 日=长史可用面 | 1 | calibration×1 | 否（长尾：中美利差对 A 股估值的月频卡、VIX 期限结构） | — |
| TDM-E-L9-A11 | ①库存"意外度"定义（vs 4 周变动均值）+链位分化（成品油意外→石油加工 vs 原油意外→石油开采）②下游=AGG（weekly/T-1，EIA 周报发布时点锚定）③事件研究口径复用族级双源；**低频自欺门柱**=有效独立观测≈200 周，IC 的 t 必须 Newey-West 重算，禁按 1000 个前填日观测充样本 ④`src/zephyr/data/implementations/eia_provider.py`（馆查命中，Provider 在产但增量任务持续失败）⑤只登记 ⑥**本车道最重要纠偏**：首轮据 `system.tables` 筛 %eia%=none 判"A11 无数据"，复查推翻——EIA 库存落在**通用长表 macro_data 的 indicator_name 轴**：CRUDE/GASOLINE/DISTILLATE/PROPANE_INVENTORY 各 267 周（2021-08-20..2026-10-02）+ EIA_BRENT_SPOT 1289/EIA_WTI_SPOT 1274 ⇒ 卡改 **preregistered**；断供事实另记=`data/failures/` 内 eia 失败 8 件（最新 2026-10-08 `Read timed out (api.eia.gov)`）⇒**2026-10-02 之后无新观测**（滚动重考会断，非本卡阻断）；替代面 futures_warehouse_receipt 2014..2026/3013 日/2,925,905 行（国内仓单库存，登记长尾） | 1 | calibration×1 | 否（长尾：仓单库存卡、EIA 增量断供运维挂账） | —（曾误判 blocked，已纠，见 §1.3.1 修订） |
| TDM-E-L9-A12 | ①台风（路径/强度）与高温（累计≥37℃）两支分列，禁合成"天气指数"②下游=AGG（realtime/0d，观测时戳即落定、预报分版本）③外部三源过闸2（PMC 2021 + JFM 2022 + Emerald 转载）④无 module_ref ⑤只登记 ⑥alt_typhoon_track 2004-08-07..2026-10-09/196,939 行（长史可用）；**weather_data 仅 40 日**（QWEATHER 预报型不可回填）；alt_sz_ground_obs 2015..2026/1,143,532 行但**仅深圳**⇒闸3 全国适配失败，高温支线写死为"单站探针、不外推、不喂 confidence"；目标面 880305 电力/880361 种植业 实测存在 | 1 | calibration×1 | 否（长尾：预警事件流 alt_sz_weather_warning 9661 行未立卡；全国多城观测=渠道缺口） | — |
| TDM-E-L9-A13 | ①户数环比=筹码集中度，季频不规则事件⇒事件研究三档窗 ②下游=AGG（adhoc/T-1，披露日锚定，TDM:L6405）③PEAD/注意力口径复用族级事件研究双源 ④无 module_ref ⑤只登记 ⑥**第二富矿**：shareholder_count announce_date 1993-01-12..2026-10-09/514,690 行/7001 独立披露日；质量画像=holder_count 为 Nullable(Int64)（NULL 或 <=0 会把环比算成 inf 静默污染）、表同时有 end_date（统计截止）与 announce_date（披露）⇒**用 end_date 锚定即前视**，PIT 门柱写死用 announce_date；分桶须按"同一披露季内"而非自然日 | 1 | calibration×1 | 否（长尾：十大股东 top10_shareholders 274,865 对（TDM G3 注）未立卡、户均持股市值） | — |
| TDM-E-L9-A14 | ①问句密度+回应率+题材催化三读数 ②下游=AGG（intraday/0d，问答时戳不可回填，TDM:L6406）③无外部来源命中（该题在中国口径下未获可溯双源）=**已查无并记归因**：查询词偏"互动易"产品名而非学术题，下一轮应改挖"公司-投资者线上互动 信息效应" ④无 module_ref ⑤只登记 ⑥irm_interactive_qa **67 日/500 行**（≈7.5 条/日，横截面分桶 min_obs 不可能满足）、extracted **74 行**、ir_activity_record **2 日/30 行**；馆查 `"互动易"` → `(no results for '互动易')` ⇒ blocked_on_data，历史不可回填（时戳不可回填由 pit_proof 钉死） | 1 | calibration×1 | 否（长尾：③向需换查询词重挖；IRM 采集密度缺口运维挂账） | blocked_on_data：现密度不足分桶且历史永不可回填 |
| TDM-E-L9-A15 | ①拥挤度定义（主要币费率分位加权，8h 右闭）+跨市场预警（A股 target）②下游=AGG（realtime/0d，TDM:L6407）③外部来源 Galaxy Digital 2026-09-21（可溯）+ Medium 2026-06-22（发布方弱=待验证）⇒门柱只依赖内部数据 ④无 module_ref ⑤只登记 ⑥**hl_funding_history 4,785,877 行 / 29,335 个 8h 期 / 2023-05-12..2026-10-09（富矿）**；但 **hl_perp_snapshot_daily 与 hl_oi_snapshot_daily 各仅 18 日、hl_liquidation_raw 仅 17 行**⇒"费率+OI"双因子版不可考，本卡只走费率单腿（已写死为长尾）；coin 键实测为裸 ticker（'BTC' 29,392 期）非 'BTC-USDT' | 3 | calibration×3（1 张 cn_a + 2 张币圈镜像） | 否（长尾：OI/清算双因子、跨市场与美股解耦检验） | 04 镜像卡 blocked_on_data：宇宙成分不可 PIT+target 仅 427 日+换源未留痕 |
| 币圈镜像（TDM-C 线） | ①镜像链单列纪律：A 股卡 market=cn_a/target=沪深300，币圈卡 market=crypto/target=BTCUSDT，两 target 禁共用（已落进两张卡）②下游=TDM-C-L1..L4（L1/L2/L3/L4 各存在骨架卡 `TDM-C-L*__comparison.yaml`，实测在 exam_cards 目录）③先例面双册：影子 MVP（§5 OKX 环境级阻断、§7 UTC 日界与三档口径）+ st_crypto_mining（"无 crypto 行情载荷"判定）④后端 `src/zephyr/data/implementations/{crypto_kline_collector,shadow_gate_c_l1}.py` ⑤只登记 ⑥**本车道推翻先例半条（正存在断言同挂指针，SOP §7.5.3）**：crypto_kline_daily 已有 19,801 行/427 日/141 币、crypto_shadow_gate 20 行 ⇒ 网络闸已过、真实数据已落；但落库表名为 `crypto_shadow_gate`（非 MVP 文 `crypto_shadow_gate_c_l1`）、symbol 为 BTCUSDT（非 OKX 的 BTC-USDT）、**shadow_tier 20 行全为 'trend' 一档**⇒三态判别力现势不可考；缺口登记给 TDM-C-L1 考试车道（不在本车道节点集，禁越界代建） | 2（计入 A15） | calibration×2（crypto） | 否（长尾：TDM-C-L1..L4 正式考试卡须由对应车道建，本车道只供 L9 镜像供给结论） | 换源溯源未见 Owner 裁定留痕（MVP 明言换源属 Owner 决策） |
| TDM-E-L9-A16 | ①结构先验无时间序列⇒判据设计改成"增量解释力"（控制图谱后 R² 增量 >=0.01）②下游=L1-S0/传导链（G5 同真源不同消费端，两卡分列不重复计）③传导路径机械判定的外部方法未获可溯来源=已查无（归因=查询词为中文表名，应改挖 input-output table + sectoral shock transmission）④后端真源 scripts/industry_graph/apply_industry_graph_ddl.py（G1 注在册）⑤只登记 ⑥馆查 `"投入产出"`→`(no results for '投入产出')`；CH 筛 %io_edge%/%input_output%=**[]** ⇒ 系数在 PG 不在 CH；**头号缺口=部门码↔ig_node 两套 id 未打通、边 100% 挂零（WP-0.5）**⇒ blocked_on_impl | 1 | calibration×1 | 否（长尾：③向需换英文查询词重挖；映射桥建成后的横截面复算） | blocked_on_impl：id 桥未建，无法挂到可交易单元 |
| TDM-E-L9-A17 | ①决策问题两半（评级调整 / 目标价变化）⇒分别落 02、03 卡，另"一致预期修正"作可算替代面 ②下游=AGG+D1（假设出生面）③外部双源过闸2（新浪财经 2020 分析师预期调整因子化 + T&F Cogent 2025/2024 评级相关性与目标价精度）④后端 alt_data 域 research_report_collector 已存在待补挂（TDM 自陈）⇒不阻卡 ⑤只登记 ⑥**三条硬实测**：research_report publish_date 2017-01-02..2026-09-30/146,940 行（史长）但 **rating_change 唯一取值=空串覆盖 146940/146940=100% 空** ⇒ 02 卡 blocked_on_data；rating 分布 买入101225/增持33144/空11384/持有610/中性544/**卖出30/回避2/减持1** ⇒ 卖方方向无方差（这本身是 A 股乐观偏差的量化证据）；**表内无目标价列** ⇒ 目标价半问=字段不存在（闸4 判 GAP）；替代面 consensus_daily 2017-01-03..2026-09-30/**6,829,376 行/2367 日**，逐年 1157→2614 只 ⇒ **覆盖漂移**（+126%）写为门柱；analyst_forecast 仅 52 日已排除；pdf_forecast_extracted 192,365 行登记长尾 | 2 | calibration×2 | 否（长尾：研报文本/新覆盖事件、目标价须待字段接入、_repaired 表双真源风险未处置） | 02 卡 blocked_on_data：rating_change 100% 空 + 无目标价列 |
| TDM-E-L9-B01 | ①物理量→官方数据的"领先双档"判据（发布前有 IC、发布后归零）②下游=AGG（adhoc/unknown，TDM:L6409）③机构实践未获可溯双源=待验证不入图⇒门柱全由内部量构造 ④not_built ⑤只登记 ⑥馆查 `"卫星影像"`→no results；CH 筛 %satellite%/%ndvi%/%thermal%=[] ⇒ **整表缺失**（从未接入，非断供）；PIT 未评估（连"能否进回测"都无答案）；Copernicus 免费/Planet 商业=资金门位 | 1 | calibration×1 | 否（长尾：③向需专门检索 satellite imagery + equity returns 学术证据） | blocked_on_data：渠道未接 |
| TDM-E-L9-B02 | ①预警日 vs 实际事件日两类锚点分列（混池=因果不可辨）②下游=AGG（TDM:L6410）③沿用天气族双源（JFM 2022/PMC 2021）做口径校验 ④not_built ⑤只登记 ⑥馆查 NWS/预警=无命中；CH 筛 %nws%/%noaa%/%alert%=[]；**易混面已核清**：alt_sz_weather_warning 9661 行属 A12（QWEATHER/深圳）不是 NWS ⇒ 不因国内表存在而解阻；时区门柱（海外发布→上海时区→A股交易日）写死；NWS API 免费=B 族解锁成本最低 | 1 | calibration×1 | 否（长尾：接入前的 PIT/时区评估本身需单独立项） | blocked_on_data：渠道未接（解锁优先级 B 族第一） |
| TDM-E-L9-B03 | ①JD 存量动能 + 领先 vs 同步分离（对已披露营收残差化后仍留 IC）②下游=AGG（TDM:L6411）③labor market postings 类文献未获可溯双源=待验证 ④**双缺发现**：即便接 JD，主体归并依赖 ig_entity_code_map（在册自陈仅 2 行）⑤只登记 ⑥馆查 `"招聘"`→no results；CH 筛 %job%/%recruit%/%zhaopin%=[] ⇒ 整表缺失；另标 blocked_on_impl 子项；合规注=抓取属 Owner 法律合规门位 | 1 | calibration×1 | 否（长尾：③向英文查询词；主体归并方案未挖） | blocked_on_data + 主体归并桥未建 |
| TDM-E-L9-B04 | ①高频通胀映射 + 大促周剔除（事前写死）②下游=AGG（TDM:L6412）③nowcasting 类未获可溯双源=待验证 ④not_built ⑤只登记 ⑥馆查 `"电商价格"`→no results；CH 筛 %ecom%/%keepa%/%price_sku%=[]；**易混面已核清**：commodity_spot_price 23 日/commodity_futures_main 23 日是大宗价非零售价，既不可替代也自身不可考；Keepa=付费 API⇒Owner 花钱门位 | 1 | calibration×1 | 否（长尾：促销日历剔除规则与类目映射需外部口径确认） | blocked_on_data：渠道未接（付费门位） |
| TDM-E-L9-B05 | ①"公告 vs 中标 vs 合同生效"三类识别规则事前写死（本领域最常见假结论源）②下游=AGG（TDM:L6413）③招投标类未获可溯双源=待验证 ④主体归并同 B03 双缺 ⑤只登记 ⑥馆查 `"招投标"`→no results；CH 筛 %tender%/%bid%/%award%=[]；另核实 c3_fundamental 全 32 表清单内无中标类表（防重复挖）；免费公开渠道⇒优先级第三 | 1 | calibration×1 | 否（长尾：标的主体归并 + 金额口径与营收分母对齐） | blocked_on_data：渠道未接 |
| TDM-E-L9-B06 | ①ADR 本地 + A 股溢出两 target；溢出必须控制美股隔夜后仍有 resid IC ②下游=AGG（TDM:L6414）③海外散户类未获可溯双源=待验证 ④not_built ⑤只登记 ⑥馆查 Reddit/舆情→no results；CH 筛 %reddit%/%twitter%/%social%=[]；**三重外部条件阻断**：渠道未接 + API 付费门位 + 境外平台网络级阻断（在册先例=OKX DNS 污染/SNI 干扰案）⇒ 判 B 族解锁最难之一 | 1 | calibration×1 | 否（长尾：网络通道方案属 Owner 资源） | blocked_on_data：渠道+付费+网络三重 |
| TDM-E-L9-B07 | ①散户热度的**倒 U 形状**（中低段正、极端档负）⇒把"极端档反转"升为主判据 ②下游=AGG（TDM:L6415）③本地散户讨论度文献未获可溯双源=待验证 ④not_built ⑤只登记 ⑥馆查 雪球/榜单→no results；CH 筛 %xueqiu%/%guba%/%post%=[]；**近亲面核清**：stock_hot_rank 38 日（东财热榜，部分代理关注度）不足以立考卡；sentiment_panel 39 日、emotion_index 8622 日是聚合指数非个股级⇒个股级讨论面 CH 全空白；强反爬=技术不稳渠道，优先级低于 B02/B05 | 1 | calibration×1 | 否（长尾：与 emotion_index 的增量检验已写进门柱但需热度数据才可跑） | blocked_on_data：渠道未接 |
| TDM-E-L9-B08 | ①榜单=慢信息 ⇒ 主判据含"榜首高企组后续不优于中位"拥挤检验 ②下游=AGG（TDM:L6416）③未获可溯双源=待验证 ④主体归并（开发者→上市公司）同 B03/B05 依赖桥 ⑤只登记 ⑥馆查 APP榜单/榜单→no results；CH 筛 app_%/%download%/%sensor%=[]；七麦会员/SensorTower=付费门位 | 1 | calibration×1 | 否（长尾：APP-公司归属表口径） | blocked_on_data：渠道未接（付费门位） |
| TDM-E-L9-B09 | ①量价分解 + 峰值 lag ∈[5,20] 才算"领先"（lag<=1 判同步，负结论也入档）②下游=AGG（TDM:L6417）③未获可溯双源=待验证 ④not_built ⑤只登记 ⑥**四词馆查全部 no results**（进出口/海关/贸易/Comtrade）+ 库面筛 %trade%/%customs%/%export%=[]；**列值面补筛（本车道新规程）出意外发现**：macro_data 内有 **WB_EXPORT/<ISO3> 2053 行国家年度出口序列（含 WB_EXPORT/CHN 2016..2025 仅 10 个年度观测）** ⇒ 判据从"整源缺失"改口径为"**分商品 HS 颗粒度缺失，国家年度粗颗粒已在库但 10 点不可考**"⇒ 结论更精确且仍 blocked；与 A08 BDI 交叉但两卡各跑不合并 | 1 | calibration×1 | 否（长尾：WB 粗面 vs HS 细面的口径差需专挖） | blocked_on_data：HS 分商品颗粒度未接（年度 10 点不可考） |
| TDM-E-L9-B10 | ①支付流水高频代理 + 春节农历对齐 ②下游=AGG（TDM:L6418）③未获可溯双源=待验证 ④not_built ⑤只登记 ⑥馆查 信用卡/支付消费→no results；库面筛 %card%/%payment%/%spend%=[]；**对照面反而充足**：macro_data 内 '社零*' 1617 序列 / '餐饮收入*' 26 序列（月度官方口径）⇒ 本源线**增量待证**（门柱=加入支付流水后社零 nowcast 误差降 >=10%）；SpendingPulse 为美国付费源，对 A 股适配性存疑（闸3）⇒ 判 B 族优先级最低 | 1 | calibration×1 | 否（长尾：国产替代高频消费渠道未挖） | blocked_on_data：渠道未接且增量价值待证 |
| TDM-E-L9-C01 | ①客流动能（人次非金额）可跨渠道比对②下游=AGG（TDM:L6419 挂起不入批）③未获可溯双源=待验证 ④not_built ⑤只登记 ⑥馆查 `"客流"`→no results；库面筛 %footfall%/%visit%=[]；**全库枚举复核**：system.tables（database LIKE 'c%'）实测 246 张表，清单内无任何门店客流表；C 档定义=渠道本身需被创造⇒非 AI 可自动推进；按 SOP §6 判**挂起排期**非封矿 | 1 | calibration×1 | 是（六向：①②④⑤⑥已入卡/已查无，③待验证项已在卡内标注不重复挖；C 档无外部机构矿可挖的归因=渠道不存在故无实践文献） | blocked_on_data：无接入渠道 |
| TDM-E-L9-C02 | ①网点草根活跃 vs 官方金融统计的领先性（事件锚用日历表）②下游=AGG（TDM:L6420）③未获可溯双源=待验证 ④not_built ⑤只登记 ⑥馆查 银行网点/信贷→no results；库面筛 %branch%/%loan%=[]；**官方侧不缺**（macro_credit_money 表在册 + M2/社融类序列）⇒ 本节点价值上限受"官方已够"压制；涉金融敏感数据⇒即便有渠道也过合规门位 | 1 | calibration×1 | 是（同 C01 判据；③向无矿可挖归因=渠道不存在） | blocked_on_data：无接入渠道 |
| TDM-E-L9-C03 | ①单场 GMV 意外 + 新品首销集中度②下游=AGG（TDM:L6421）③未获可溯双源=待验证 ④not_built ⑤只登记 ⑥馆查 `"直播电商"`→no results；库面筛 %live%/%gmv%/%douyin%/%kuaishou%=[]；**双层阻断**：无正式渠道 + 第三方 GMV 口径不可复核（商业机密级数据）⇒ 即便拿到也须先过质量画像；实体兑现面（income_statement）实测可用，故 target 侧就绪、只差 signal | 1 | calibration×1 | 是（同 C01/C02 判据） | blocked_on_data：无正式渠道 + 口径不可复核 |
| TDM-E-L9-G1 | ①链/节点/边三轴供给，考"边有没有用"而非"边有多少"②下游=L2-06+L3-01（TDM:L6422-6424）③结构先验的外部对标（产业链→收益）未获可溯双源=待验证 ④真源 scripts/industry_graph/apply_industry_graph_ddl.py；chain_refs 8 条在产链实测从节点取⑤只登记 ⑥馆查 `"ig_edge"`→**TBL:pg:ig_edge active**（+备份 ig_edge_bak_20260914）⇒ 表在册但在 **PG**；本车道无 PG 只读通道（须走 extract_depgraph.py，禁裸连）⇒ 记为**受阻/未完成**不当查无；消歧桥仅 2 行=假边风险⇒结论上界钉"待验证" | 1 | ablation×1 | 否（长尾：PG 读数打通后的三臂实跑） | blocked_on_impl：PG↔CH 跨存储接线未接 + 消歧桥未建 |
| TDM-E-L9-G2 | ①CKG 作 G1 的增强层，考"旧事实层还补不补得上"②下游=G1（TDM:L6422 as_of 静态先验）③已查无（开源图谱增强预测力的可溯双源未获）④导入件 scripts/industry_graph/import_ckg_dataset.py 在册 ⑤只登记 ⑥CH 筛 %fact%/%ckg%=[]⇒在 PG ig_fact（source=ckg_2021，as_of=2021-10-26）；**特有判据=老化曲线**（as_of 前后分段报增益）⇒把"快照过期"做成可读结论而非隐藏混杂 | 1 | ablation×1 | 是（六向：①②③④⑤⑥分别入卡/已查无/受阻已归因；G2 无独立数据面可再挖，长尾并入 G1 的 PG 打通） | blocked_on_impl：同 G1（可合并施工） |
| TDM-E-L9-G3 | ①穿透关联对的共动 vs 随机配对②下游=L3-12-2（席位↔实体归并，TDM:L6425）③已查无（股权网络共动文献未获可溯双源）④module_ref=scripts/entity_graph/equity_penetration.py（600566/600927/601963 实测在注）⑤只登记 ⑥馆查 `"股权"`→CH 侧只有 **equity_pledge_detail/summary（质押，非穿透）**⇒防误接；穿透真源=PG entity_graph edge_holding（valid_to IS NULL），**原 ig_equity_edge 804 条已 2026-09-29 按裁定#424 退役 DROP**（备份 F:/zephyr_cold/retired_tables/）⇒实现件与新真源接线完整性标"待核"；双轴 PIT（报告期 vs 公告日）+ 境外 BVI/开曼断线不编造均写进门柱 | 1 | ablation×1 | 否（长尾：top10 十大股东 274,865 对与 edge_holding 的公告日对齐未挖） | blocked_on_impl：PG 通道 + 退役后接线待核 |
| TDM-E-L9-G4 | ①概念标签作 L1-AGG 题材热度维度②下游=L1-AGG（TDM:L6424）③已查无（题材热度构造的可溯双源未获）④无 module_ref⑤只登记 ⑥**实测 + 方法论阻断**：concept_board_constituent valid_from 仅 2026-08-10 起 35 日、concept_board 750 行静态、market_breadth_snapshot 26 日、emotion_index 8622 日（唯一长史）⇒ **概念标签无版本历史轴=不可回溯**（不是行数少，是没有版本轴）；TDM 自陈"W6 须先补行数实测"本班已完成；概念≠产业链硬边界⇒禁把概念当传导链（防污染 G1） | 1 | ablation×1 | 是（六向全部入卡/已查无；长尾=按日落版积累后重考，属时间条件非可挖项） | blocked_on_data：概念成分无版本历史轴 |
| TDM-E-L9-G5 | ①IO 系数作行业弹性②下游=L1-S0（TDM:L6425）③已查无（IO 冲击传导的可溯双源未获，与 A16 同矿脉不重复挖）④red_reason=not_built⑤只登记 ⑥馆查 `"投入产出"`→no results、CH 筛=[]⇒在 PG ig_io_edge 16,859 条；**挂接率=0**（两套 id 未打通，WP-0.5）⇒ 三臂消融物理上不可执行；与 A16 共享施工前置（禁重复立项） | 1 | ablation×1 | 是（六向已落；长尾=挂接率 >=60% 后的三臂实跑，属实现前置非可挖项） | blocked_on_impl：io_edge 挂接率 0 |
| TDM-E-L9-V1 | ①考"时间分层纪律值多少钱"而非信号强弱（三臂含 same_day_leak 前视臂）②下游=L2/L1-AGG，出边 lag=T-1③机构三件套改臂间有序性检验④module_ref=src/zephyr/plan_engine/judgment_ledger.py（MOD-PLAN-026）且**有自家测试件** tests/plan_engine/test_judgment_ledger.py（馆查实测）⇒可用夹具做单测级验证⑤只登记 ⑥**长史可用**：regime_snapshot_history 2019-04-01..2026-10-09/1824 日/3635 行（+regime_state_anchored 2244 日）⇒ preregistered；但 judgment 台账四表实测 **12/6/40/24 行**⇒"落台带时戳"半问近乎空，登记为子项缺口（卡内不掩饰）；3635 行/1824 日⇒多版本并存须按 (run_id,snapshot_commit) 定唯一 | 1 | ablation×1 | 否（长尾：HMM 7 维概率本身对次日收益的 calibration 曲线未单独立卡） | —（judgment 台账近空已记子项） |
| TDM-E-L9-V2 | ①六段相位 T-1 落台增益（四臂含 random_stage/fixed_stage）②下游=L1-AGG 相位消费③已查无（相位机制度量未获可溯双源）④节点 red_reason=not_built/module_ref=null，聚合器"独立对话未建、纪要§8.3 定案不代建"⇒本卡用 emotion_index.stage 作**代理读数面**并声明结论上界⑤只登记 ⑥emotion_index 1991-06-10..2026-10-09/**8622 日**含 stage 列⇒可 preregistered（代理版）；sentiment_panel 仅 39 日不依赖；8661 行/8622 日⇒存在 version 重复，消融须定唯一版本行 | 1 | ablation×1 | 否（长尾：聚合器建成后的正式版重跑=他车道项） | —（正式落台未建已记为结论上界） |
| TDM-E-L9-V3 | ①板块状态 T-1 就绪 + 五成分逐臂消融（找哪一成分在扛贡献，比总消融有用）②下游=L2 板块选择③已查无④module_ref=judgment_ledger（同 V1）⑤只登记 ⑥sector_state 2022-09-01..2026-10-08/**992 日×435 板块/432,088 行**⇒preregistered；起 2022-09-01 ⇒ 统一牛段不可用（已内缩窗口并声明）；sector_code 与 880 视图编码是否同源**未核**⇒记为待核不当已验证 | 1 | ablation×1 | 否（长尾：五成分逐臂实跑 + 编码对齐核验） | — |
| TDM-E-L9-D1 | ①假设集分轨消融（gplearn/智能体/MCTS 各臂）+ **自证检测**（IS→OOS 衰减 >50% 判过拟合，优先于主判）②下游=D2 入表→E1 考试③防消融假结论门柱=各臂"同数量假设配额"必须相等（否则差是搜索预算差）④module_ref=scripts/backtest/mcts_expression_search.py（MOD-BT-202），节点自陈缺积木/考试链加固/GPU 燃料⑤只登记 ⑥实测 hypothesis_precheck **414 行**、strategy_screen **1406 行**、node_verdict **58 行**且均无日期跨度⇒IS(2019-23)/OOS(2024-25) 两段根本没数据⇒blocked_on_data；strategy_screen 的 deflated_sharpe/oos_years_decay 列**已在表**⇒多重检验口径可直接复用（④向正面发现） | 1 | ablation×1 | 否（长尾：GPU 燃料属 Owner 资源门位；三轨产能铺开后的实跑） | blocked_on_data：IS/OOS 两段零假设产出（缺算力） |
| TDM-E-L9-D2 | ①考"可证伪产量"与"挪门柱率"而非预测力（治理卡口径：窗口=流程运行时窗，非行情窗）②下游=E1③已查无（预注册收益的实证可溯双源未获，故判据全内部化）④module_ref=null/red_reason=structural/module_mounts=[MOD-AU-008]，节点自陈 registry 代码随 B7v2 尾批在飞⇒本班不代落⑤只登记 ⑥馆查 `"meta_question"`→**5 个词汇表文档命中（frequencies/layers/origins/outcomes/statuses）**⇒十态枚举有真源文件可作合法转移字典（正面产出）；CH 筛 %meta_question%/%exam_plan%=[]⇒主表在 PG 无通道；goalpost_move_rate 需开考后字段变更审计轴（未见） | 1 | ablation×1 | 否（长尾：PG 通道 + B7v2 落地后的现状基线读数，"现在有没有人挪门柱"本身是 Owner 要的数） | blocked_on_impl：主表跨存储 + 挂载代码在他车道在飞 |
| TDM-E-L9-E1 | ①假阳抑制率为主判据（三臂：旁路考试/单切分/阈值放宽 50%）②下游=E2 回传③已查无（多重检验治理的可溯双源未获，但 deflated Sharpe 口径已由内部表列承载=内部可算）④module_ref=src/zephyr/trading/validation/runner.py（MOD-TDMVAL-001）+ ablation.py 实测语义=双权重面板重放差、**非卡驱动执行器**⇒本车道 ablation 卡一律写成"消融臂规格"（已记入台账 §1.6 与每张 ablation 卡）⑤只登记 ⑥node_verdict 58 条且 validation_method 未铺开⇒三臂 min_obs 30 不可能满足；market_signal_history 仅 3 日；"假阳性裁判"需独立后验窗**不可回填**（时间条件） | 1 | ablation×1 | 否（长尾：自反性复核（E1 判据由 E2 独立复核）未展开） | blocked_on_data：考试判定 58 条不足三臂 |
| TDM-E-L9-E2 | ①三臂（不回传/当日回传/滞后 5 日）+ **死信判据** correction_hit<0.20⇒允许给出退役结论②下游=L4 修正/L0 复考退役③已查无④**module_ref=null、red_reason=pending_gate**⇒回传件本身未落地（缺实现非缺数据），三臂需生效时点开关而开关不存在⑤只登记 ⑥decision_daily 2026-09-16..**2026-10-12**/138 行/9 日（含 asof_data_date 天然时滞列，且右端晚于今日⇒须过滤 asof_data_date<=trade_date 防把未来决策日当已发生）；sim_daily_report 11 日、node_verdict 58 行；**现在就能跑的描述性读数=trade_date − asof_data_date 分布**已在卡内标为优先项 | 1 | ablation×1 | 否（长尾：实现落地后的三臂实跑） | blocked_on_impl：pending_gate，回传件未落地 |
| TDM-E-L9-Z1 | ①十态转移 + 18 列强制的旁路消融（脏条目计数为主判）②下游=全 L9 治理面③已查无④module_ref=null/red_reason=structural⑤只登记 ⑥馆查 `"meta_question"`→statuses 词汇表在册（合法转移字典真源可取）；CH 无 meta_question 表⇒在 PG；**无可旁路接缝**（三臂要求能关单件强制）⇒改留"描述性审计"口子（脏条目现值可立即产出）；version 乐观锁冲突未报错=并发覆盖（根宪法 §1.13 同源检验） | 1 | ablation×1 | 否（长尾：单测级夹具替代生产旁路的方案未挖） | blocked_on_impl：主表不可读 + 无强制开关 |
| TDM-E-L9-Z2 | ①三臂（停跑探测器/单向探测/陈旧快照）+ **瘦身允许结论**（one_way_miss_count=0 即证"双向"一半是摆设）②下游=净零审计/对账读数③已查无④module_ref=scripts/governance/reconcile_chain_refs.py（MOD-GOV-CHAINRECON）⑤只登记 ⑥CH 筛 %chain_ref%/%reconcil%=[]⇒探测输出无落台面；**易混表已区分**：c1_market.reconciliation_differences 是行情对账非图↔库资产对账，禁混用（防误接）；判据 MUST 复用 w4_1 triage canonical（节点原话"禁重画"）；本车道禁跑治理件⇒现值读数登记给他车道 | 1 | ablation×1 | 否（长尾：探测输出落库（>=8 周批次）后的三臂实跑） | blocked_on_impl：探测输出无落台面 + 无消融接缝 |
| TDM-E-L9-AGG | ①就绪度读数生产者整环消融（三臂：随机 status/全绿/旁路）+ **反证优先**（random 与 fixed_green 掉幅若≈0=下游根本没读该字段，消费关系名义存在实质零消费）②下游=MOD-FACTORY-001/MOD-TRADING-015（module_mounts 实测字段）③ablation 法=作业簿明令（全链基准→本环换随机/固定/旁路）④module_ref=src/zephyr/data/l9_readiness_aggregator.py⑤只登记 ⑥**l9_readiness_daily 2026-09-15..2026-10-09 仅 5 个独立日期/195 行**（≈39 行/日，与"29 源线+5 图谱+3 快照=37"量级吻合）⇒基线日不足三臂重放；列面含 status/freshness_lag_days/rows_in_window⇒**接线可行、样本不可得**；成因=生产者 2026-09-28 才实件化（向前积累型，非断供） | 1 | ablation×1 | 否（长尾：≥60 个就绪日 + 至少一次真实缺数事件作负例后实跑） | blocked_on_data：基线读数仅 5 日 |
<!-- 追加锚点 -->

## 四、车道收尾（MUST 项，逐条齐）

### 4.1 总量（全部实测，非估算）

- 本车道节点总数：**45**（entry_flow/L9 全集，逐个从 `config/trading_decision_map.yaml` L4981-6161 取全文字段）
- 已挖数（六向全部留痕的节点）：**45/45**
- 新卡总数：**51**（校验命令见 4.6；45 个节点每节点 ≥1 张，A01/A04/A06/A15/A17 多张）
- 覆盖节点数：**45**（`node_id` 去重实测=45，无遗漏无重复）
- 族分布：**calibration 36 / ablation 15**
- 状态分布：**preregistered 18 / blocked_on_data 24 / blocked_on_impl 9**
- market 分布：**cn_a 49 / crypto 2**（币圈镜像单列，见 4.5）

### 4.2 mined_out 名单（结构判据，禁降格）

**已达枯竭判据（mined_out）= 5 个**：`TDM-E-L9-C01`、`TDM-E-L9-C02`、`TDM-E-L9-C03`、
`TDM-E-L9-G2`、`TDM-E-L9-G5`
判据逐条：六向全部"已入卡 / 已查无（含归因）/ 受阻已归因"，且矿脉清单无本节点可再挖长尾
（C 三节点的外部矿归因=渠道本身不存在故无机构实践文献可引；G2/G5 的长尾是"他环实现前置"
（PG 通道 / io_edge 挂接率），属实现前置而非可挖信息项，且与 G1/A16 同矿脉已声明不重复挖）。

**其余 40 个 = 未达枯竭**（有明列长尾，见 4.4）。
禁降格声明：未以"挖了两轮没新东西/时间不够/节点太多"封任何一个矿；
每个 blocked 节点仍保留长尾条目，状态 blocked 是**数据/实现的物理阻断**，不是挖矿终止判据。

### 4.3 blocked 名单与原因（24+9=33 张卡，按成因归类）

| 成因类 | 卡数 | 节点（卡号） |
|--------|------|-------------|
| A 渠道未接（B 档，CH 无表+馆查零命中） | 10 | B01 B02 B03 B04 B05 B06 B07 B08 B09 B10（各 02） |
| B 无接入渠道（C 档，渠道需被创造） | 3 | C01 C02 C03（各 02） |
| C 历史不可回填（快照型/时戳不可回填） | 3 | A07(02) A14(02) G4(02) |
| D 字段存在但内容全空/口径不可用 | 2 | A17(02)（rating_change 100% 空+无目标价列）、A02(02)（l2_tick 空表+IS 全空） |
| E 关键表空/断供致 IS 或 OOS 段零覆盖 | 3 | A04(03)（stock_valuation rows=0）、A06(03)（北向断供 2024-08-16/OOS 截断）、A15(04)（宇宙成分不可 PIT+427 日+换源未留痕） |
| F 样本量不足臂间对比（治理/验证环，向前积累型） | 6 | AGG(02) D1(02) E1(02) B-D 类其余…（AGG/D1/E1 + 见注） |
| G blocked_on_impl：跨存储（PG↔CH）或 id 桥/开关缺失 | 9 | A16(02) G1(02) G2(02) G3(02) G5(02) D2(02) E2(02) Z1(02) Z2(02) |

（注：F 类实数=AGG/D1/E1 三张 blocked_on_data + V 族无 blocked；上表 F 行标 6 为笔误候选，
准确数=**3**；总数校核：10+3+3+2+3+3=24 = blocked_on_data 实测数，9=blocked_on_impl 实测数。
此句本身即"计数勿写死散文"纪律（根宪法 §4.3）的自纠样本，保留不删。）

### 4.4 未挖长尾清单（明列，按族）

A 族（13 条）：A01 隔夜跳空/分钟非同步跳动/周-月频动量反转；A02 五档撤单队列、封板瞬间订单流；
A03 板块→个股领先性卡、概念资金流卡（待数据）；A04 行业级估值分位、破净率/buffett_ratio 面、
估值水平（非增量）对 20 日目标；A05 毛利率改善、ROE 杜邦分解、业绩快报抢先度；
A06 龙虎榜席位（dragon_tiger_seat 1152 日长史=下一富矿）、融资余额（margin_trading 505 日）；
A07 评级迁移矩阵、覆盖机构数变化；A08 BDTI 油运细分、运价波动率面；
A09 个股级新闻面板（news_data.related_symbols Array 列）、新闻主题事件流；
A10 中美利差对估值的月频卡、VIX 期限结构；A11 仓单库存卡（futures_warehouse_receipt 3013 日）、
EIA 增量断供运维挂账；A12 预警事件流（alt_sz_weather_warning 9661 行）、全国多城观测渠道缺口；
A13 十大股东（top10_shareholders 274,865 对）、户均持股市值；A15 OI/清算双因子、美股解耦检验；
A17 研报文本面、新覆盖（首次覆盖）事件、目标价字段接入后重考。
B/C 族（6 条）：B01-B10 各族的③向英文/学术查询词重挖（本轮仅中文产品名检索，归因=查询词不当）；
B09 的 WB 粗颗粒 vs HS 细颗粒口径差专挖；B10 的国产替代高频消费渠道；B02 接入前的时区/PIT 评估立项；
C 族三条"渠道出现后"的重考口子。
G/V/D/E/Z 族（11 条）：G1/G2/G3/G5 的 PG 只读通道打通后三臂实跑；G3 的十大股东↔edge_holding
公告日对齐；G4 的概念按日落版≥8 版本后重考；V1 的 HMM 7 维概率 calibration 曲线单卡；
V3 的 sector_code↔880 编码同源核验；D1 三轨产能铺开实跑；D2 的"现状 goalpost_move_rate 基线读数"
（不消融也能给 Owner 的数）；E1 的自反性复核（E1 判据由 E2 独立复核）；Z1 的单测夹具替代生产旁路方案；
Z2 的探测输出落库后三臂。
外部引用待验证项（须补第二来源才可入图，5 条）：A05 中国 PEAD、A15 资金费率拥挤、
A09 媒体情绪、A02 冲击成本曲线、B 族全部（未获任何可溯双源）。

### 4.5 币圈镜像 TDM-C 线结论（本车道独有一支，链已单列）

- 纪律落实：两张 crypto 卡（`A15__03_币圈镜像资金费率对BTC`、`A15__04_币圈镜像山寨季广度`）
  均带 `market: crypto` + `mirror_of` 指针，target=BTCUSDT/ETH-BTC 汇率（UTC 日界、7×24、
  无 T+1/无涨跌停），与 A 股卡 target（沪深300/个股 hfq）**物理分列**，禁共用结论；
  A 股侧 T+1 与一字板门柱在镜像卡内明写"不得继承"。
- 对在册先例的**双向纠偏**（正/负存在断言同纪律，SOP §7.5.3）：
  ① 正纠偏：`st_crypto_mining.md` 判"全域 L 级缺口：无 crypto 行情载荷"——实测已推翻半条，
     `crypto_kline_daily` 有 19,801 行/427 日/141 币、`crypto_shadow_gate` 20 行 ⇒ 网络闸已过、真数据已落；
  ② 负纠偏：本车道首轮判"A11 EIA 整源缺失"——实测亦推翻，EIA 四组库存落在**通用长表
     macro_data 的 indicator_name 轴**（各 267 周）⇒ 新规程=负存在断言 MUST 同筛"表名"与"列值"两路；
  ③ 口径漂移登记：落库 symbol='BTCUSDT'（MVP 文档写 OKX instId 'BTC-USDT'，后者实测 rows=0）、
     表名 `crypto_shadow_gate`（MVP 写 `crypto_shadow_gate_c_l1`）、
     `shadow_tier` 20 行**全为 'trend' 一档** ⇒ 三态判别力现势不可考（缺口挂给 TDM-C-L1 车道，
     本车道不越界代建）；换源未见 Owner 裁定留痕（MVP 明言换源属 Owner 决策）⇒ 溯源断点如实登记。

### 4.6 可复核校验命令（任何人可重跑，禁信本台账自陈）

```
cd D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/entry_flow/L9
python -c "
import glob, yaml, collections
fs=sorted(glob.glob('TDM-E-L9-*__*__0[2-9]_*.yaml'))
req=['status','signal_kind','pillars_numeric','window','buckets','pillars','target','lineage',
     'preregistered_by','preregistered_at','data_binding','family','node_id','card_id','hypothesis','title_zh']
bad=0; nodes=set(); fam=collections.Counter(); st=collections.Counter(); mk=collections.Counter()
for f in fs:
    d=yaml.safe_load(open(f,encoding='utf-8')); nodes.add(d['node_id'])
    fam[d['family']]+=1; st[d['status']]+=1; mk[d.get('market','cn_a')]+=1
    pn=d.get('pillars_numeric') or {}; db=d.get('data_binding') or {}
    for k in req:
        if k not in d: print('MISS',f,k); bad+=1
    for k in ('mono_spearman_min','ic_mean_min','ic_ir_min','regime_same_sign','oos_same_sign'):
        if k not in pn: print('PMISS',f,k); bad+=1
    for k in ('signal_table','signal_column','signal_derivation','target_source','data_window_evidence'):
        if k not in db: print('DBMISS',f,k); bad+=1
    if d.get('generated'): print('GEN-FLAG(禁)',f); bad+=1
    if d.get('preregistered_by')!='st-nightmine-20261010-L7': print('SIGNER',f); bad+=1
print('cards',len(fs),'issues',bad,'nodes',len(nodes)); print(dict(fam)); print(dict(st)); print(dict(mk))
"
```
本轮实测输出：`cards 51 issues 0 nodes 45`；
`{'calibration': 36, 'ablation': 15}`；
`{'preregistered': 18, 'blocked_on_data': 24, 'blocked_on_impl': 9}`；
`{'cn_a': 49, 'crypto': 2}`。
（骨架件 45 个 `generated: true` 未被改动；新卡均另建文件、无 generated 标=受保护。）

### 4.7 建议交叉复挖 20% 名单（9 个节点，按"复挖期望收益"排）

1. **A17**（研报）— 富矿但被一列卡死：rating_change 100% 空，须复挖 pdf_forecast_extracted
   192,365 行能否反推评级迁移；consensus_daily 6.8M 行覆盖漂移（1157→2614 只）须专门处理方案。
2. **A06**（资金流）— 复挖 dragon_tiger_seat（1152 日、622,365 行）席位行为卡；
   本车道已把"残差化防共线"门柱立住，须复用到 A01/A03 检验其动量卡是否同样被共线污染。
3. **A10**（国际宏观）— FRED 族只起 2021-08-16（本车道纠偏），须复挖 us_index(1993 起/8481 日)
   与 kline_global(2014 起) 作 VIX 缺段替代，把牛段补回来。
4. **A11**（能源库存）— 本车道两度纠偏（EIA 在长表 + 增量任务持续超时断供）；
   须复挖 futures_warehouse_receipt（3013 日、2.9M 行）国内仓单库存卡 + 运维挂账 EIA 断供。
5. **B02 / B05 / B09**（免费渠道三支）— 复挖=接入门槛最低（API 申请/公开平台，属 Owner 四件事），
   其中 B09 须先把"列值面筛"新规程走完（WB_EXPORT 粗面 vs HS 细面）。
6. **G1 + G5 + A16**（同矿脉三连）— 复挖前置=PG 只读通道 + WP-0.5 部门 id 桥；
   三卡共享一次施工，禁分别立项（净零铁律）。
7. **V1 / V2**（状态快照）— 本车道已用长史面立卡；复挖=judgment 台账 12/6/40/24 行的
   "落台为何近空"根因（属他件缺口，跨车道协同项）。
8. **E1 / D1**（考试与挖掘环）— 复挖=node_verdict 58 条的增长路径与 GPU 门位排期；
   本车道已确认 ablation 语义为"双权重面板重放"非卡驱动，须在卡片规格上对齐 runner 契约。
9. **A15 crypto 镜像**（04 卡）— 复挖=宇宙成分版本轴落库 + 换源 Owner 留痕；
   解锁后此卡与 TDM-C-L1 正式卡须一并出分（当前只有 20 行单档 gate 不可判）。

### 4.8 禁区自证（无越界）

- 未做任何 git 写操作；未改 TDM/注册表/分数册；未跑生成器；未碰他人车道目录。
- 45 个骨架件（`generated: true`）零改动（校验命令含 GEN-FLAG 检查，issues=0）。
- 分数册未写（`run_card` 未调用，全部卡为预注册/挂起态，不产生分数行）。
- 临时件全部在 `D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/`
  （l7_probe_tables.py / l7_probe_cols.py / l7_probe_report.py），项目根零临时文件。
- CH 读取一律经 `scripts/backtest/fexam/ch_data.py`（ch_query_df），无裸 duckdb/无 SQL 散落文件。
- 负/正存在断言均挂三源指针（馆查命令原文+输出摘录、system.tables 筛、列值筛），
  无"凭记忆断言"；两处本车道自我推翻（A11、G/E 族 ablation 语义）均如实保留并标注纠偏过程。

## 三、待办与矿脉清单（滚动）

- [x] CH 表全集枚举（业务库=c1_market/c1_backtest/c3_fundamental/c0_meta 四个）→ 见第一节
- [x] A 族 17 源线逐源覆盖窗/行数/断供史实测（1.1/1.2）
- [x] B/C 族 13 源线："渠道未接"=CH 无任何表 + 馆查零命中（双正查，见 1.3.2）
- [x] 币圈镜像数据落位实测（1.4，含对在册先例的纠偏）
- [x] 断言工具命令形纠偏（1.7）
- [ ] G 族：ig_* 在 PG depgraph（非 CH）→ 取数面/target 口径分离（进行中）
- [ ] V/D/E/Z/AGG：就绪率与考试链 ablation 口径（进行中）
- [ ] 交叉复挖候选：A06 残差化门柱是否反哺 A01/A03（同型共线风险）
