---
ttl: task_bound
---

# M1 车道：L9 另类 30 源线挖矿总索引

- 车道: M1（另类数据源因子/策略挖矿）| 日期: 2026-10-06 | sid 见战役令
- 真源: 源线清单=`docs/_working/fullcirc_closeout_chief/t3_fullflow_exam_mining.md` §1.9（A03/A06-A14/A15/A16 + B01-B10 + C01-C03 + G1-G5 共 30 条）；节点定义=`config/trading_decision_map.yaml` L9 区段（约 line 4732-5543）；DS 条目=`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`
- 方法: 每条源线 = TDM 节点定义 → data_refs → DS 条目 → **CH 实测**（行数/列名/时间覆盖，2026-10-06 时点，只读）→ 三态判定
- 判定口径: **S=可参数接线**（数据在库且历史够，直接进 S2 海选协议）｜**M=补模块**（数据在库但需自建聚合/映射模块才可考）｜**L=只登记**（结构在但现阶段语义不可回测，如实记缺口）
- 验收三态: 可挖(S/M)=9 ｜ 不可挖(L 只登记)=6 ｜ 缺数据=15

## 一页判定表（30 条全覆盖，行数/覆盖均为 CH 2026-10-06 实测）

| # | 源线ID | 名称 | 数据表（实测主表） | 在库状态（行数/覆盖） | 判定 | 规格卡 |
|---|---|---|---|---|---|---|
| 1 | TDM-E-L9-A03 | 板块/概念指数 | c1_market.kline_sector_880 + concept_board/_constituent + board_index_tick + kline_sector_intraday | 880 板块K线 763,260 行，2020-03-17→2026-09-30，729 板块；概念 750 板/成员 37,040 行（valid_from 2026-08-10→09-30，仅 2 月）；盘中板块 tick 在库 | **S** | spec_SL-A03.md |
| 2 | TDM-E-L9-A06 | 资金流 | c1_market.money_flow + sector_fund_flow + market_fund_flow_daily | money_flow 5,971,039 行，2021-01-04→2026-09-30，5,781 票（主力/超大/大/中/小单净流入）；市场级仅 146 行、板块级仅 2026-09-15 起 | **S** | spec_SL-A06.md |
| 3 | TDM-E-L9-A07 | 千股千评 | c1_market.alt_stock_comment | 67,573 行，**2026-09-11→09-30（约 14 交易日）**，5,199 票；管道在产日更 | **L** | 99_negative_results.md #1 |
| 4 | TDM-E-L9-A08 | 航运运价BDI | c1_market.alt_shipping_index | 31,686 行；BDI 1988-10-19→2026-09-30，BCI/BSI/BDTI/BCTI 2006-07→；regime 轴 F4_BDI_MOMENTUM_Z20 在产（1989→2026-09-30，9,301 条） | **S** | spec_SL-A08.md |
| 5 | TDM-E-L9-A09 | 财经快讯情绪 | c3_fundamental.news_data + news_sentiment_score + c1_market.news_sentiment_window + emotion_index | news 8,119,241 行（2010-01→2026-10-05）；已打分 7,947,739 行；窗口表 19,831 行仅 2026-02-24→；**个股映射 related_symbols 仅 ~80 行非空** | **M** | spec_SL-A09.md |
| 6 | TDM-E-L9-A10 | 国际宏观 | c1_market.us_index + cftc_positioning + a50_futures_daily + alt_fx_rate_ecb + macro_data(_vintage) | SPX/IXIC/DJI 1993→2026-09-29；CFTC 81,270 行 1986→2026-09-08（21 市场）；A50 2016-08→；FX 仅 114 行（2026-08→）；**macro_data 2,261 指标全为中国宏观，0 条国际指标（FRED 直连面缺口）** | **S** | spec_SL-A10.md |
| 7 | TDM-E-L9-A11 | 能源库存(EIA) | c1_market.edb_data | **edb_data 0 行**；全库无 EIA/能源库存表 | **缺数据** | 99_negative_results.md #7 |
| 8 | TDM-E-L9-A12 | 天气 | c1_market.alt_sz_weather_warning + weather_data + alt_typhoon_* + alt_sz_climate_hist 等 | 预警流 9,595 行 **2008-07→2026-09**（深圳，14 类信号）；qweather weather_data 11,313 行仅 2026-08→09（40 城）；台风登陆史 845 行；regime 轴 F7_TYPHOON_EVENT(116 事件 2005→2018)/F8_HEAT_EVENT(38) 在册 | **M** | spec_SL-A12.md |
| 9 | TDM-E-L9-A13 | 股东户数 | c3_fundamental.shareholder_count | **514,395 行，1993-01-12→2026-09-30，5,906 票**（announce_date+end_date 双轴） | **S** | spec_SL-A13.md |
| 10 | TDM-E-L9-A14 | 互动易问答 | c3_fundamental.irm_interactive_qa + irm_interactive_extracted + ir_activity_* | qa 仅 **500 行**（2026-06-19→09-16，241 票）；extracted 74 行；ir_activity 30 行——试点量 | **L** | 99_negative_results.md #2 |
| 11 | TDM-E-L9-A15 | 加密永续/费率 | c1_market.hl_funding_history + hl_oi_snapshot_daily + hl_perp_snapshot_daily + crypto_kline_daily | **funding 4,750,075 行，2023-05-12→2026-10-05，234 币 8h 费率**；OI/perp 快照 2026-09-18→；币 K 线 19,344 行 2025-08→；轴 F14_BTC_MOMENTUM_30D 在产（2025-09→） | **S** | spec_SL-A15.md |
| 12 | TDM-E-L9-A16 | 投入产出 | ig_io_edge（**PG depgraph 域，CH 无表**） | TDM 自述 16,859 条边 **100% 挂零**（部门码/ig_node 两套 id 缺口），挂载消费待传导链证据链建成 | **L** | 99_negative_results.md #3 |
| 13 | TDM-E-L9-B01 | 卫星影像 | 无表 | 渠道未接（Copernicus/Planet 均未接） | **缺数据** | 99_negative_results.md #8 |
| 14 | TDM-E-L9-B02 | 美国官方天气/海洋 | 无表 | 渠道未接（NWS API 未接；深圳天气面属 A12，不覆盖美国） | **缺数据** | 99_negative_results.md #9 |
| 15 | TDM-E-L9-B03 | 招聘JD | 无表 | 渠道未接（智联抓取未建） | **缺数据** | 99_negative_results.md #10 |
| 16 | TDM-E-L9-B04 | 电商价格 | 无表 | 渠道未接（Keepa 付费 API 未购） | **缺数据** | 99_negative_results.md #11 |
| 17 | TDM-E-L9-B05 | 招投标 | 无表 | 渠道未接（政采网/公共资源平台未接） | **缺数据** | 99_negative_results.md #12 |
| 18 | TDM-E-L9-B06 | 社媒舆情X/Reddit | 无表 | 渠道未接（API 未购） | **缺数据** | 99_negative_results.md #13 |
| 19 | TDM-E-L9-B07 | 雪球/股吧散户情绪 | 无专表；代理=c1_market.stock_hot_rank | 雪球/股吧未接；**东财人气榜代理 7,393 行仅 2026-08-04→09-30**（1,763 票，2 rank_type）——代理太短不可考，只作管道登记 | **缺数据** | 99_negative_results.md #14 |
| 20 | TDM-E-L9-B08 | APP榜单 | 无表 | 渠道未接（七麦会员/SensorTower 未购） | **缺数据** | 99_negative_results.md #15 |
| 21 | TDM-E-L9-B09 | 进出口贸易 | 无分商品表；macro_data 有全国总量 | UN Comtrade 未接；CN 宏观总量面（DS-101）含进出口但无分商品量价 | **缺数据** | 99_negative_results.md #16 |
| 22 | TDM-E-L9-B10 | 信用卡/支付消费 | 无表 | SpendingPulse proxy 未接 | **缺数据** | 99_negative_results.md #17 |
| 23 | TDM-E-L9-C01 | 实时门店客流 | 无表 | C 档无渠道（TDM 自述挂起不入批） | **缺数据** | 99_negative_results.md #18 |
| 24 | TDM-E-L9-C02 | 银行网点/信贷活跃 | 无表 | C 档无渠道 | **缺数据** | 99_negative_results.md #19 |
| 25 | TDM-E-L9-C03 | 直播电商实时成交 | 无表 | C 档无渠道 | **缺数据** | 99_negative_results.md #20 |
| 26 | TDM-E-L9-G1 | 图谱·Zephyr产业链 | ig_* 14 表（**PG depgraph 域，CH 无表**） | 873 链/5,560 节点/1,726 结构边；TDM chain_refs 已挂 8 条在产链；本车道 CH-only 不可达，且属结构证据非时序因子面 | **L** | 99_negative_results.md #4 |
| 27 | TDM-E-L9-G2 | 图谱·CKG事实层 | ig_fact（PG 域） | as_of=2021-10-26 静态快照，仅结构先验无时序 | **L** | 99_negative_results.md #5 |
| 28 | TDM-E-L9-G3 | 图谱·实体股权穿透 | c3_fundamental.top10_shareholders + top10_circulating_shareholders（CH 面）；edge_holding/equity_penetration.py（PG 面） | **top10 1,500,471 行，2005-01-29→2026-09-30，5,843 票**；穿透函数在册（MOD-ENTITY-GRAPH） | **M** | spec_SL-G3.md |
| 29 | TDM-E-L9-G4 | 图谱·概念/题材 | c1_market.concept_board + concept_board_constituent + stock_profile_ths | 概念 750 板；成员 37,040 行 **valid_from 仅 2026-08-10→09-30（无 PIT 历史）**；stock_profile_ths 5,217 行静态 | **L** | 99_negative_results.md #6 |
| 30 | TDM-E-L9-G5 | 图谱·投入产出传导 | ig_io_edge（PG 域，CH 无表） | 16,859 条边**100% 挂零**（id 缺口，altdata_line WP-0.5 在案） | **缺数据** | 99_negative_results.md #21 |

## 三态计数

| 三态 | 条数 | 源线 |
|---|---|---|
| **可挖（S 接线 7 + M 补模块 2）** | **9** | A03/A06/A08/A10/A13/A15（S）；A09/A12（M）；G3（M） |
| **不可挖（L 只登记）** | **6** | A07/A14/A16/G1/G2/G4 |
| **缺数据** | **15** | A11/B01-B10/C01-C03/G5 |

## 有戏前 5（按 数据厚度×PIT 干净度×假设成熟度）

1. **A13 股东户数**——33 年×5,906 票，announce_date 双轴 PIT，卖方金工共识假设（筹码集中度）。
2. **A06 主力资金流**——5.97M 行×5.7 年×全 A，列即因子（超大/大单净流入率），T-1 盘后落定零修订。
3. **A08 BDI 运价**——37 年历史，regime 轴 F4_BDI_MOMENTUM_Z20 已在产（bizmine F 车道先例），条件化考法现成。
4. **A15 HL 资金费率**——4.75M 行×3.5 年 8h 费率，跨市场杠杆拥挤轴（TDM 决策问题原话"全球杠杆拥挤预警 A股情绪"）。
5. **A03 板块指数**——763K 行×6.5 年×729 板块，T3 缺口 M3（板块主干最简版）的直接原料，一鱼两吃。

## 纪律声明

- 本索引全部行数/覆盖=CH 只读实测（2026-10-06），非抄注册表声称值（P3 先例：声称覆盖必须复核）。
- 规格卡=预注册卡**模板预填**（status: draft_pre_freeze），SOP 铁律二：跑数前冻结，启动后不得改动。
- 禁凑数：9 张卡每条给齐三件套（经济逻辑一句话/数据列名/计算式）；21 条不可挖逐条进负结果台账（exam_policy §5 纪律，另类挖矿 0/5 前科在案）。
