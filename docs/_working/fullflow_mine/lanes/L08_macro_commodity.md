---
ttl: task_bound
title: "宏观大宗族数据用途挖矿作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

# L8 宏观/大宗/海外族 数据用途挖矿作业簿

> 车道：fullflow_mine_20261001 / L8。方法论=data_source_onboarding_sop §9A/§9B + mining_sop v1.5.0 §2.5。
> 实勘方式=CH c1_market 只读（rows+max(date)，2026-10-01）；消费端=src 反查+tasks.yaml+data_asset_registry+census 台账。
> 方向修正（重要）：wiring 生成器建议的 MAC 四岛落点 `regime/regime_cycle_analyzer.py` **不成立**——实读该文件，`analyze(ohlc)` 是纯价格日历模块（只收 close 列，做月末/节后/周年日统计），无宏观序列自然落点；NB1-B5 已把 MAC 族真消费落在 `regime/features/macro_regime_sensor.py`。本簿工单按实勘重定向。

## ① 实体清单（实证：rows / max(date) / 判鲜）

| # | 实体（c1_market） | rows | max(date) | 判鲜（>3d 日频/>45d 月频） |
|---|---|---|---|---|
| 1 | macro_data | 55,433 | 2026-09-30 | 活（2,261 个 indicator_name×frequency 序列） |
| 2 | macro_data_vintage（+视图 compat/latest） | 16,091 | 2026-09-23 | 活（PIT 存证通道） |
| 3 | macro_activity_gauge | 221 | 2026-08-31 | 月频正常（9 月数据 10 月中发布） |
| 4 | macro_daily_gauge | 9,359 | 2026-09-30 | 活 |
| 5 | macro_pmi_gauge | 449 | 2026-09-30 | 活 |
| 6 | macro_price_gauge | 251 | 2026-08-31 | 月频正常；**ppi_yoy 在此（CN-002 数据实存）** |
| 7 | macro_trade_gauge | 448 | 2026-08-31 | 月频正常；**export/import 在此（CN-010 数据实存）** |
| 8 | macro_credit_money | 1,168 | 2026-08-31 | 月频正常（社融/M1/M2） |
| 9 | market_china_bond_yield | 12,000 | 2026-09-30 | 活 |
| 10 | market_cffex_member_ranking | 7,545 | 2026-09-30 | 活 |
| 11 | rate_decision_calendar | 6,172 | **2025-10-30** | **断供 11 个月**（任务在、管线死） |
| 12 | cftc_positioning | 81,270 | **2026-09-08** | 周频缺 3 期；**tasks.yaml 无刷新任务** |
| 13 | agri_wholesale_index | 23,254 | 2026-09-30 | 活 |
| 14 | commodity_spot_price | 1,134 | 2026-09-30 | 活 |
| 15 | commodity_futures_main | 189 | 2026-09-30 | 活（少量主力合约） |
| 16 | ndrc_fuel_price | 660 | 2026-09-25 | 活（旬度调价窗口） |
| 17 | road_freight_index | 86 | **2026-08-21** | 断更 ~40 天 |
| 18 | futures_warehouse_receipt | 2,920,363 | 2026-09-30 | 活（族内最大表） |
| 19 | futures_term_structure | 3,665 | 2026-09-29 | 边界（落后 1 交易日） |
| 20 | futures_position | 3,458 | **2026-09-23** | 疑断供 5 个交易日 |
| 21 | hog_futures_core | 430 | 2026-09-30 | 活 |
| 22 | hog_spot_index | 586 | 2026-09-28 | 边界（落后 2 天） |
| 23 | hog_province_spot | 1,232 | 2026-09-30 | 活；**实证非幽灵**（asset 注册+task+F10/F12 消费齐全） |
| 24 | edb_data | **0** | 1970 | 死表（0 行，无任务） |
| 25 | msci_adjustment | **0** | 1970 | 死表（0 行，无任务） |
| 26 | index_adjustment | 15,196 | 2026-09-14 | 活（事件驱动派生） |
| 27 | market_index_meta | **0** | 1970 | 死表（0 行，无任务） |
| 28 | us_index | 22,624 | 2026-09-29 | 活（隔夜链真源） |
| 29 | kline_global | 10,013 | 2026-09-30 | 活；global_hsi/nikkei/kospi/usdcnh 4 任务 disabled 待 provider |
| 30 | a50_futures_daily | 2,618 | 2026-09-30 | 活；但隔夜修正器 A50 通道仍关闭 |
| 31 | us_futures_intraday | 719 | 2026-09-30 | 活 |
| 32 | dividend_tax_node（视图） | 105,536 | 2026-07-10 | 派生视图（口径偏外族，本族只登记） |

断供与 0 行清单：rate_decision_calendar（任务在数停 11 个月）、cftc_positioning（无任务）、road_freight_index（停 40 天）、futures_position（停 5 交易日）、edb_data / msci_adjustment / market_index_meta（0 行 0 任务=死表）、kline_global 族 4 个 disabled 子任务（usdcnh 子任务全源失效）。

## ② 逐实体六问矩阵（Q1 因子 / Q2 策略 / Q3 模块 / Q4 环节 / Q5 地图 / Q6 盲点）

按 9 族归并判定（同族同判，逐实体微差注明）。

**A. macro_data(+vintage/视图)**：Q1 CPI/PPI/PMI/社融/M1M2 剪刀差/LPR/国债收益率分位因子——已在映射表 16 条中落地 13 wired；Q2 regime 条件化/宏观择时（TDM-E-L1-S0 改指 macro_regime_sensor）；Q3 传感器+dashboard；Q4 A 盘前（隔夜链）/月度发布日（D 段）；Q5 TDM L1 宏观组已挂；Q6 **传感器自身零消费者（见工单 WO-1）**、美系修订非农需 vintage 通道（已在）。
**B. 5 gauge+credit_money**：Q1 与窄表同源宽格式（CPI/PPI/PMI/进出口/社融 M1M2 列名直读，免序列翻译）；Q2 同 A；Q3 **零真消费者**（仅 akshare_provider+DDL，census state=zero×5）；Q4 周末校准段；Q5 未挂任何图；Q6 与 A 表双格式双真源风险——价值在"桥接 CN-002/010 的现成数据"（WO-2/3），长期应收敛或明确分工。
**C. 债利率+议息日历**：bond_yield=ERP/股债收益差核心腿（regime used_by 已声明）；rate_decision_calendar：Q2 事件驱动/Q4 事件敏感度升档输入——但**数停 11 个月且零分析消费者**（WO-5）。
**D. 期货家族**（warehouse 292 万行/term_structure/position/cffex_ranking）：Q1 仓单变化率/基差/期限结构斜率/会员持仓集中度因子；Q2 商品期货策略+周期股传导；Q3 零分析消费（term_structure 已记 census zero）；Q4 盘后段；Q5 产业链图 BOM 叶挂价挂点未挂；Q6 全族"采而不算"。
**E. 商品现货**（agri 菜篮子/ndrc 油价/road_freight/commodity_spot）：Q1 通胀高频代理/物流景气因子；Q2 通胀宏观因子（F6.24-27 底座=MAC-CN-016 清单内）；Q3 dashboard 展示级；Q4 周末段；Q6 road_freight 断更 40 天无人知（WO-11 探活）。
**F. 猪价链**：F10 基差 z/F11 周期相位/F12 分省离散度三因子已在 alt_regime_signals 实消费（SOP §9B 范例族）；Q6 hog_spot_index 落后 2 天需探活；hog_province_spot 幽灵判定**实证推翻**（asset:5846 行登记在册）。
**G. 海外族**（us_index/kline_global/a50/us_futures_intraday）：us_index=隔夜修正器+跨市场传导传感器+外资冲击判定三消费齐备（族内最健康）；a50 被 intraday_l1_tracker 读但**隔夜修正器通道 disabled**（WO-7）；kline_global 仅 coverage+dashboard；us_futures_intraday 消费未查得（719 行小体量）。
**H. cftc_positioning/index_adjustment**：cftc=商品持仓情绪因子经典源，81k 行在库却无任务无消费（WO-6）；index_adjustment 有 derive 任务（事件面外族消费）。
**I. 死表×3**：六问全查无+0 行+无任务 → 直接进三态裁定（⑥）。

## ③ 12 应用面判定（§9B 逐格）

| 应用面 | 判定 |
|---|---|
| 大盘/指数 | 适用：us_index/a50→隔夜修正+传导（已接）；bond_yield→ERP 择时（待 WO-1 下游） |
| 板块/行业 | 适用：PPI-CPI 剪刀差→周期/消费轮动（CN-002 缺口修复后）；cftc→商品板块情绪 |
| 个股 | 不适用：本族无个股粒度数据 |
| 做T（日内） | 边缘：us_futures_intraday 719 行可做夜盘提示，体量不足独立面——不适用（现状） |
| 可转债 | 不适用：无交集（利率仅作分母背景） |
| ETF/LOF | 边缘适用：宏观因子可驱动宽基 ETF 择时，经 regime 层间接达成，无直连工单 |
| 期货/商品 | 适用：仓单/基差/期限结构/cftc 四因子族（WO-6/9 全族工单）；hog 链已接 |
| 币圈 | 不适用：无加密数据 |
| 宏观/择时 | **主战场**：macro_regime_sensor 六组打分→caution_factor（WO-1 核心工单） |
| 产业链/传导 | 适用：commodity_spot/ndrc 油价/仓单→BOM 叶挂价挂点（挂账，图侧未建完） |
| 事件驱动 | 适用：rate_decision_calendar+FOMC 日历→事件敏感度升档（修复后生效，WO-5） |
| 文本/情绪 | 不适用：本族无数文本料 |

## ④ 接线工单（10 张；MAC 四岛细案）

**MAC 四岛现状**：CN-001（CPI"全国-同比增长"）与 CN-003（PMI"制造业-指数"）序列映射 status=wired，经 `macro_regime_sensor.read_macro_indicators()` 走 `macro_data`（PIT live/vintage 双通道）——**读取腿已通，断点在下游**：全仓 grep 证实 `MacroRegimeSensor.score()` 产出的 `weather_score/caution_factor/tier` **零消费者**（连 style_regime_model 都未读）。

- **WO-1（P0，MAC 四岛共同下游）**：给 macro_regime_sensor.score() 接第一个消费者——`plan_engine/llm_premarket_analysis.py` 盘前注入点（该文件已有"外盘族 us_index+BS-005 注入"先例，第 40/260 行模式），caution_factor 进盘前提示词与敏感度档位；第二消费者=`regime/style_regime_model.py`（已 import RegimeCycleAnalyzer，是 regime 聚合天然挂点）。落点=函数级：llm_premarket_analysis 的注入契约区+style_regime_model 的状态合成入口。
- **WO-2（P1，MAC-CN-002 PPI）**：不催采集腿（akshare_provider=st-zc9-lane-d 领地，让路维持）。短期桥接=macro_regime_sensor 读腿加宽表 fallback：`c1_market.macro_price_gauge.ppi_yoy`（实测 251 行至 2026-08-31）按 `indicator_id=MAC-CN-002` 出 (obs_date,value)；映射表 series_map 该条 series_code 回填 `macro_price_gauge.ppi_yoy`+status=wired（safe_write_text CAS）。采集腿补 job 后撤桥。
- **WO-3（P1，MAC-CN-010 贸易）**：同 WO-2 范式，数据面=`macro_trade_gauge.export_yoy/import_yoy`（实测至 2026-08-31）；方向字段用 export_yoy（direction=neutral 背景变量），映射表回填+转 wired。
- **WO-4（P2，MAC-CN-001/003 复核）**：已 wired 不另开工单；挂一条复核项——传感器 percentile 窗口与发布日历（CPI 每月 9-15 日/PMI 月末）对齐验证，防发布日空窗误判 missing。
- WO-5（P1）：rate_decision_calendar 断供修复——任务 `rate_decision_calendar_refresh` 在（daily_capital，11 央行 akshare 接口全量）但数据停 2025-10-30；排查 11 接口失效点、failures/ 留痕、修复后接事件面消费者（overnight_boundary_reviser 事件敏感度/作战室日刊）。
- WO-6（P2）：cftc_positioning 补调度任务（周频 weekend_calibration 槽）+首个消费者（期货面持仓情绪因子立卡）。
- WO-7（P1）：a50 通道启用——`overnight_boundary_reviser.py` `enable_a50_channel=False`（L211"数据源未接入"已过时：a50_futures_daily 2,618 行在库且 intraday_l1_tracker L514 `_load_a50` 有现成读法）；按既有 A50_DELIVERY_CHANNEL_WEIGHT=0.45 语义接线。
- WO-8（P3）：死表三态（⑥裁定）——edb_data/msci_adjustment/market_index_meta。
- WO-9（P2）：期货四表"采而不算"挂账建卡（仓单变化率/基差/期限结构斜率/cffex 集中度四因子 candidate），解锁条件=商品期货策略立项。
- WO-10（P3）：kline_global 族 4 个 disabled 子任务（hsi/nikkei/kospi 待 provider 封装窗口；usdcnh 全源失效需寻源）维持 disabled+reason 合规态，登记寻源长尾。
- WO-11（P1）：断供探活三查——road_freight_index（停 40 天）、futures_position（停 5 交易日）、hog_spot_index（落后 2 天）跑 supply_sentinel 核查+补跑。

## ⑤ 六向台账（mining_sop §2 映射）

| 向 | 产出 | 判定 |
|---|---|---|
| ①上游 | macro_data 上游=akshare 2261 序列+FRED 22+EIA+worldbank；缺口=PPI/MLF/贸易差额采集腿（让路登记）、usdcnh 全源失效 | 3 GAP |
| ②下游 | 真消费者图谱：us_index(3)/hog 链(1 模块 3 因子)/macro 窄表(传感器)/bond_yield(声明未消费)；零消费=gauge×5/期货四表/cftc/rate_decision/kline_global/us_futures_intraday | 8 孤岛 |
| ③算法 | 传感器分位打分已实现（percentile+组加权+missing 降权）；ERP/剪刀差/基差/cftc COT 情绪=业界标准用法（方法论常识层，无外部搜索轮，内部矿脉已足） | 已查无外部缺口 |
| ④后端 | macro_regime_sensor.test 在（mock 零 CH）；隔夜链读法三先例（us_index SQL/A50 _load_a50/注入契约）；死表无 provider | 可复用件 3 |
| ⑤前端 | dashboard api_server 已挂 kline_global/a50/hog_province_spot 展示；宏观温度计页未建（只登记不施工） | 1 挂账 |
| ⑥字段 | gauge 宽表字段齐全且新（ppi_yoy/export_yoy 直用）；sensor 需要的 (indicator_id,obs_date,value) 由读层翻译；死表连 schema 消费都无 | 桥接可行 |

## ⑥ 自审闸三态（mining_sop §6）

| 实体/工单 | 三态 | 依据 |
|---|---|---|
| MAC 族→传感器下游（WO-1/2/3/4） | **施工** | 消灭"接而不通"最后一段：数据+读取+打分全在，只缺一个下游读者；直接推进 regime 条件化终局 |
| rate_decision 修复+cftc 补任务+探活三查（WO-5/6/11） | **施工** | 断供修复=管线存活底线，符合"任务存在≠管线活着"教训账 |
| a50 通道启用（WO-7） | **施工** | 数据在、读法在、权重语义在，启用即消灭一处人工预判缺位 |
| 期货四表因子卡（WO-9） | **挂起排期** | 终局有位（商品策略面），解锁条件=商品期货策略立项；现无消费端拉动 |
| 产业链 BOM 挂价 | **挂起排期** | 解锁条件=产业链图 MOD-SIG-125 建至挂点 |
| 死表×3（WO-8） | **判退役候选** | edb_data/msci_adjustment/market_index_meta：六问全查无+0 行+无任务+无注册能力——退役评审走 §10（Owner 门：注册表净删=high 门位），本簿只裁定候选 |
| 宏观温度计前端页 | **挂起排期** | 只登记不施工纪律；解锁=WO-1 落地后 dashboard 信息位空缺 |
| usdcnh 寻源 | **挂账长尾** | 全源失效实证在案，待新源登记 candidates |

挖矿日志：本轮=实勘轮（CH 31 表+3 视图全扫）+内部反查 4 轮（grep 消费端/tasks.yaml/asset 册/census 台账）；signal 6（传感器零消费者/gauge 存 PPI 贸易实数/hog 幽灵推翻/rate 断供 11 月/cftc 无任务/a50 通道过时关闭），noise 0，受阻 0。矿脉长尾：us_futures_intraday 消费方待查（719 行小体量降优先级）。
