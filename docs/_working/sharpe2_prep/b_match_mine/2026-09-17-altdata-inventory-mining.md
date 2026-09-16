---
ttl: task_bound
---

# 另类数据全量盘点 + 按序挖矿记录 — Sharpe2 决赛准备战·分包 B 任务②

- 会话：st-sharpe2b-20260917 ｜ 日期：2026-09-17 ｜ 性质：沙箱研究文档（不进生产库/不进注册表）
- 机读版：[altdata_inventory.csv](altdata_inventory.csv)（40 表盘点）
- 考试底档：`.runtime/tmp/sharpe2b/exam_results/*.json`（5 份，可复核）
- **再生声明**：本件系第三度自底档机械再生（原始生成 st-sharpe2b-20260917；再生原因=他会话 worktree pre_merge stash 扫走事故两起，本件前两版分别于当日 03:05-03:16 与 04:41 前后被扫离工作区，无 stash 可恢复）。全部 E4 数字由底档 `exam_results/all_results.json` + `ALT-HOG-02.json` 机械重导出，盘点数字由 `inventory_raw.json`/`inventory_raw2.json` 重导出，经核对与原版一致。

---

## 1. 盘点口径与方法

- 范围：`c1_market` 全库 168 表中的 `alt_*` 27 张 + 指令点名的 `weather_data`/`hog_futures_core`/`hog_province_spot`/`hog_spot_index`/`calendar_event`/`ipo_calendar` + 排除令核验对象（crypto/edb/macro/news_sentiment_window/limit_up_down/stock_hot_rank）+ 事件接线物化表（market_pattern_event/technical_indicator）= **40 表**。
- 手段：逐表 count/min-max 时间/列结构/粒度 uniq 抽查（轻查询，两轮脚本 `.runtime/tmp/sharpe2b/inventory_alt.py`、`inventory_pass2b.py`）；空值率粗检以粒度 uniq 与行数自洽性替代（未逐列统计，诚实声明见 §6）。
- 消费状态核验：`alt_regime_signal` 实查 8 个 signal_id（20,822 行）：F4_BDI_MOMENTUM_Z20（1989 起 18,534 行）/F11_HOG_CYCLE_PHASE（1,064）/F14_BTC_MOMENTUM_30D（743）/F7_TYPHOON_EVENT（232，**止于 2018-11-17**）/F23_LIMITUP_EMOTION（94）/F12_HOG_DISPERSION（69）/F8_HEAT_EVENT（57，2026-08 起）/F15_FNG_INDEX（29）。与 `docs/_working/alt_data_consumption_plan.md`（C-1/C-2 批次档案）交叉一致。

## 2. 盘点全表（摘要，机读版见 csv）

**A. 有深度、可考的未消费数据面（挖矿主战场，行数/范围自底档 inventory_raw.json 重导）**

| 表 | 行数 | 范围 | 粒度 | 质量/覆盖 |
|----|------|------|------|----------|
| alt_sz_house_daily | 443,251 | 2017-01-03..2026-09-15 | 日频 3,371 成交日 | 连续 9.7 年，深圳住建局口径（report_catalog/house_usage 双序列族） |
| alt_typhoon_track | 250,210 | 2004-08-07..2026-09-13（issue_ts） | 路径点，597 风暴 | 22 年；2019 后未消费（F7 止 2018） |
| alt_sz_ground_obs | 648,159 | 2015-01-01..2026-09-15 | 日频 4,246 日 | 连续 11.7 年，深港地面观测（温/压/湿/风/雨） |
| alt_sz_climate_hist | 836,861 | 主体 1951+（ddatetime 有 1970 脏行） | 日频 20,696 日 | 长史但含脏时间戳，用前需清洗 |
| alt_sz_weather_warning | 18,712 | 2008-07-12..2026-09-14 | 事件流 14 类 | 18 年预警事件，发布时点 issue_ts 可 PIT |
| hog_spot_index | 583 | 2015-01-05..2026-09-14 | 周频 | 11.7 年连续，自带 ma_4m/6m/12m |
| calendar_event | 797 | 2021-08-20..2026-12-31 | 12 类制度事件×约 122 | **起点 2021-08**，不含 2020-2021 上半年 |

**B. 缺积累/断更/空表（死档）**：alt_stock_comment（4 个交易日/5,197 股次）、ipo_calendar（17 日）、ipo_schedule（0 行）、alt_sz_visibility（15 日）、weather_data（29 个记录日×40 城）、hog_futures_core（417 日/1 年）、hog_province_spot（980 行/2026-07 起）、alt_sz_house_listing（**止于 2024-06-17 断更**）、alt_sz_port_monthly（月频 90 点+止于 2025-07）、stock_hot_rank（13 日）、edb_data（0 行）。

**C. 静态/低频（不可日频化）**：alt_typhoon_landfall_history（845 行 1949-2018 年度）、alt_typhoon_names（字典 1,260 行）、alt_sz_market_subject（11 行年度）、alt_sz_enterprise_year（44 行年度）、alt_sz_stat_analysis（7 行文本）、alt_sz_reservoir_station（485 站元数据）。

**D. 低优先未挖（记录在案）**：alt_sz_air_quality_daily（4,098 日×30 监测点）、alt_sz_air_quality_region（4,695 日）、alt_sz_env_meteor（4,982 日 3 类）、alt_sz_marine_forecast（4,604 日含预报值至 2026-09-21，**PIT 需发布时点列**）、alt_sz_reservoir_level（7,580 万行/225 站/2020-01..2026-07 断更）、alt_sz_reservoir_rain_day（217 库 2,367 日）/month、alt_sz_house_area（3,031 日）、alt_sz_house_presale（2,155 条 2011 起）、alt_sz_stat_monthly（17 序列 201902-202506）。

**E. 排除令核验（不挖）**：BDI（F4 在 regime 表）/比特币（F14）/恐贪（F15）/涨停情绪（F23）——四件套+生猪 F11/F12、温度 F8、台风 F7（部分）共 8 信号已消费；宏观 macro_data（57,937 行 1993 起）与 edb_data（空）排除；新闻窗 news_sentiment_window（19,811 行）排除；产业链图谱类：c1_market 内未见独立图谱表本体（图谱资产在 data_asset_registry 挂 IGFACT 通道引用），归单独讨论，本包不碰。

## 3. 优先级排序（经济学假设可信度 × 数据质量 × 未被消费）

| 名 | 数据面 | 假设一句话 | 就绪度 |
|----|--------|-----------|--------|
| 1 | 深圳楼市日成交 | 成交量是地产链景气的高频同步指标（边际购房者对价格敏感，量在价先），成交扩张期房地产股占优 | 日频 9.7 年连续 |
| 2 | 台风路径（2019+ 未消费段） | 登陆级台风破坏产区供给→农产品涨价预期（灾损传导），事件窗内农林牧渔受益；增量=官方 typhoon_track 换掉止于 2018 的旧 F7 源 | 22 年路径点，发布时点可 PIT |
| 3 | 深圳气温距平 | 持续高温→用电负荷→电力景气（供需通道，Cao-Wei 2005 温度异常框架；情绪通道降权），距平极值期公用事业占优 | 日频 11.7 年 |
| 4 | 生猪现货动量 | 现货站上 52 周均值/4 月线站上 12 月线=周期右侧，养殖利润扩张期养殖股占优（与已消费 F11 相位同数据异变换，同源增检） | 周频 11.7 年 |
| 5 | 制度事件日历（LPR/期指交割/期权到期） | 已知日期的制度事件日存在日历效应（利率决议日银行/地产波动放大） | **起点 2021-08，标准 IS 窗 2020-2023 缺前段→缺数据档，未考** |

6 名以后（未挖，低先验）：港口月度（月频+断更）、水库水位（水电代理传导弱+断更）、海洋预报（PIT 复杂）、空气质量（假设弱）、统计月报（发布滞后+传导远）。

## 4. 实际挖矿记录（产一个考一个，共 5 次考试，0 过；下表全部数字自底档 exam_results json 机械重导）

考试口径（与前序批次同款，零重写判定）：全窗 2020-01-01..2025-08-31，WFA 8 折（24m train/6m test/6m step），IS=2020-2023（准入 Sharpe>0.5），真 OOS=2024-01 起（**OOS/IS≥0.70 硬线**），精确 DSR（官方件 MOD-SIM-024，**<0.5 否决带 fail-closed**）；回测=冻结土规成本（佣金 2.5bp+印花 10bp 卖+滑点 5bp）+T+1。判定全委托 `strategy_validation_pipeline`+`DecisionGate`+`OverfittingDetector`+`f06_e4_wfa_exam.map_exam_verdict`。

PIT 口径：数据日 D → shift(1) → 引擎 w.shift(1) 后自 D+2 起承担收益（=发布后 T+1 才可用仓）；台风事件=发布次日收盘建仓（事件窗内不再叠加滞后）。篮子=SW 一级行业等权（industry_class L1 × kline_daily_hfq：房地产 95 只/农林牧渔 114 只/公用事业 139 只）。

| # | 因子 | 假设/构造 | PIT | IS Sharpe | OOS Sharpe | OOS/IS | DSR(N) | WFA | 判定 |
|---|------|----------|-----|-----------|------------|--------|--------|-----|------|
| 1 | ALT-HOUSE-01 深圳楼市成交扩张→房地产 | 20 日均量>60 日均量持有多头（hold 44.6%） | shift(1)+T+1 | **-0.188** | 0.022 | — | 0.0796(6) 否决带 | —（IS 跳级拦截） | **不通过**（IS 未过 0.5） |
| 2 | ALT-TEMP-01 深圳气温距平→公用事业 | 7 日均温−2015-2019 固定 DOY 气候态 >+1.5°C 持有（hold 50.3%） | 基准期固定，shift(1) | **-0.091** | 0.661 | — | 0.2708(6) 否决带 | —（IS 跳级拦截） | **不通过**（IS 未过） |
| 3 | ALT-TYPHOON-01 台风南海岸事件→农林牧渔 | 路径点进入南海岸箱（lat<26,112<lon<122）且风速≥24.5m/s 首日，次日建仓持 10 交易日（205 事件，hold 24.2%） | 发布次日建仓 | 0.067 | -0.121 | -1.799 | 0.0556(6) 否决带 | 正折占比 0.375 | **不通过** |
| 4 | ALT-HOG-01 生猪现货动量→农林牧渔 | 周度现货/52 周均值−1>0 持有（hold 36.7%） | shift(1) | 0.463 | 0.625 | **1.348 过线** | 0.2627(6) 否决带 | 正折占比 0.5 | **不通过**（IS 差 0.037 + DSR 否决带） |
| 5 | ALT-HOG-02 变体复核（4 月线>12 月线滤子） | 表自带均线右侧确认，变换不同于 F11 相位 | shift(1) | **0.650 过** | 0.193 | 0.297 不过线 | 0.0915(8) 否决带 | 3/8 折通过 | **不通过**（WFA/OOS/DSR 三重否决） |

补充底档数字（复核用）：full sharpe 分别为 -0.079/0.113/-0.0/0.515/0.499；maxDD -0.4512/-0.401/-0.2585/-0.2314（HOG-02 未存 full mdd 字段）；单边换手 0.031/0.0583/0.0175/0.0047；OOS 延长至 2026-08 参考线（不进门）0.022/0.661/-0.121/0.625。

**结论（诚实）**：0/5 通过。最有希望的生猪族 OOS 方向正确（1.348 过线、IS 变体 0.65 过线）但 DSR 全落在过拟合否决带——以现有构造不构成可晋级候选；楼市/气温两条 IS 方向即错（机制假设在 IS 段就不成立），属真阴性而非门槛擦边。全部 5 份 summary json 存 `.runtime/tmp/sharpe2b/exam_results/`，判定链路可复现。

**产出纪律声明**：本包产物全部为文档与 tmp 脚本，未写任何 CH 表、未进 intake CSV/注册表/decision map；考试参数一次锁定，无逐因子调参打捞（ALT-HOG-02 为机制驱动变体并已计入 DSR 试验数 N=8）。

## 5. 剩余清单（计算预算诚实条款）

按优先级序已挖 1-4 名（含 1 次变体）；未挖剩余：
- 第 5 名制度事件日历：缺数据档（calendar_event 起点太晚），未考。
- 6 名以后全部未挖：marine_forecast/reservoir_level/air_quality/port_monthly/stat_monthly/rain 系列/house_area/house_presale——低先验+断更或月频，留待下批。
- 深挖方向（下批建议）：生猪族 OOS 方向为正是本批唯一亮点，若续挖应先扩 N 口径登记与样本外长度（2026 段 OOS 延长线 ext=0.625 与 0.193 两口径已并存记录），并考虑换成生猪产业链股票池细分（养殖 vs 饲料 vs 动物疫苗）而非全行业篮子。
- 声明：本批考试未做参数敏感性扫描（E3 职责），IS 数值对参数选取的稳健性未验证——晋级判断一律以 E4 管线输出为准，本文档数字仅为门槛预审。

## 6. 诚实清单（本任务没做到的）

1. 空值率未逐列统计（用粒度/行数自洽+抽样替代）——逐列 null 统计在 40 表规模下查询预算超支，留待下批。
2. 第 5 名及以后未考（理由如上，非跳过不报）。
3. alt_sz_climate_hist 存在 1970 脏时间戳行（836,861 行中 ddatetime min=1970-01-02），本批未清洗未使用；ground_obs 已够用。
4. 产业链图谱类：未在本库发现图谱表本体，仅在 data_asset_registry 见 IGFACT 通道引用——按任务书归单独讨论，未展开。

## 7. 可复现附录

```bash
# 1) 盘点两轮脚本（只读 CH 轻查询）
python .runtime/tmp/sharpe2b/inventory_alt.py         # 40 表 行数/时间范围/列结构
python .runtime/tmp/sharpe2b/inventory_pass2b.py      # 粒度 uniq/年度分布/样本行
python .runtime/tmp/sharpe2b/build_inventory_csv.py   # 产 altdata_inventory.csv（读 raw json 底档，可离线重跑）

# 2) E4 考试 harness（判定全委托官方件）
python .runtime/tmp/sharpe2b/altdata_e4_exam.py       # 4 因子: 楼市/气温/台风/生猪
python .runtime/tmp/sharpe2b/hog_variant_exam.py      # ALT-HOG-02 变体复核
# 关键复用: f06_e4_wfa_exam.build_folds/fold_metrics_from_net/map_exam_verdict
#          _c4_engine.run_backtest/daily_net_returns (冻结土规+T+1)
#          strategy_validation_pipeline.run_strategy_validation
#          c4_deflated_sharpe_runner.run_deflated_sharpe_batch (精确DSR)

# 3) 消费状态核验 SQL
# SELECT signal_id, count(), min(signal_date), max(signal_date) FROM c1_market.alt_regime_signal GROUP BY 1
```

合规声明：研究方法与工程产出，不构成投资建议；本文档数字全部来自当日实查与官方判定件输出，无编造。
