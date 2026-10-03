---
ttl: task_bound
title: "另类数据族数据用途挖矿作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

# L07 另类数据族数据用途挖矿作业簿（深圳环境气象+台风+航运+评论+FX）

> 车道 L07 / fullflow_mine_20261001。方法论=data_source_onboarding_sop §9A 六问+§9B 十二面（v2.0.0）+ mining_sop v1.5.0 §2.5。CH c1_market 只读实勘 2026-10-01（zephyr_reader）。
> **台账口径校正**：任务 brief 记"20 孤岛"——实测 consumption_census_ledger=**24 岛**（20 张 alt_sz_ + 台风 3 张 + alt_stock_comment）；brief 记 weather_warning【断供 2020-09】**与实测不符**（逐年连续 2008-2026，max issue_ts=2026-09-28），按实测留痕。
> **消费事实基线**：全族真实消费仅 `alt_shipping_index`（F4）与台风 track/landfall（F7——但 F7 死于 2018，见②）；reservoir_level 名义有客=supply_sentinel 监控引用，**分析型消费者未见**；上游真源=docs/_working/alt_data_consumption_plan.md（F1-F27 设计卡与已核引文）。

## ① 实体清单（行数+max 业务日期+断供，27 源表+1 产出表，全族 ≈8,000 万行）

| 表 | 行数 | max(业务日期) | 状态/断供 |
|---|---|---|---|
| alt_shipping_index | 31,691 | 2026-09-30 | 活（BDI 1988 起 14,011 行）；HRCI 停发 2011-08、BHMI 全史 1 行（缺口在册） |
| alt_fx_rate_ecb | 93 | 2026-09-30 | 活但浅：2026-08-19 起 31 交易日，3 对（EUR/USD/JPY→CNY） |
| alt_stock_comment | 67,573 | 2026-09-30 | 活但浅：2026-09-11 起 20 天，5,199 股 |
| alt_typhoon_track | 351,672 | 2026-09-29 | 活（2004-08 起） |
| alt_typhoon_landfall_history | 845 | **2018** | **断供 8 年**（1949-2018）→ 卡死 F7（实证 max signal_date=2018-11-17） |
| alt_typhoon_names | 1,260 | 静态维表 | 参考表（命名国/含义） |
| alt_sz_air_quality_daily | 108,653 | 2026-09-28 | 活（2015 起，30 监测站） |
| alt_sz_air_quality_region | 105,592 | 2026-09-29 | 活（区级 6 污染物） |
| alt_sz_climate_hist | 490,218 | 2026-08-31 | 滞后 1 月；min ddate=1970-01-01 脏日期 |
| alt_sz_enterprise_year | 44 | 2022 | 年频滞后 4 年（1979-2022） |
| alt_sz_env_meteor | 55,797 | 2026-09-30 | 活；type 枚举脏（'2'/'1'/''） |
| alt_sz_ground_obs | 1,164,844 | 2026-09-30 | 活（小时级实况） |
| alt_sz_house_area | 118,562 | 2026-09-28 | 活（分区成交） |
| alt_sz_house_daily | 231,220 | 2026-09-28 | 活（分用途网签） |
| alt_sz_house_listing | 2,434,879 | 2026-07-07 | 采集活/业务滞后 ~3 月；2.4M 明细大表 |
| alt_sz_house_presale | 3,933 | 2024-07 | 滞后 27 月；issued_date=Oracle 串 '31-7月 -24' |
| alt_sz_marine_forecast | 148,346 | 2026-09-30 | 活（9 海区，27 列宽表） |
| alt_sz_market_subject | 22 | 2023 | 年频滞后 3 年 |
| alt_sz_port_monthly | 584 | **2025-07** | **断供 15 月**（7 序列：TEU/货量/机场客货） |
| alt_sz_reservoir_level | 75,463,972 | **2026-07-31** | **半死管线**（采集活/业务停 2 月，known_data_gaps 在案，源端确认无 8 月后数据） |
| alt_sz_reservoir_rain_day | 290,531 | 2026-09-16 | 滞后 15 天（217 库） |
| alt_sz_reservoir_rain_month | 27,482 | 2026-08 | 活 |
| alt_sz_reservoir_station | 970 | 静态维表 | — |
| alt_sz_stat_analysis | 14 | **2019-08** | **死 7 年**（14 篇文本） |
| alt_sz_stat_monthly | 17,032 | **2025-06** | **断供 16 月**（17 序列，含深圳 CPI/社零/进出口） |
| alt_sz_visibility | 52,051 | 2026-09-30 | **浅史仅 29 天**（2026-09-02 起，7 站） |
| alt_sz_weather_warning | 10,026 | 2026-09-28 | 活（2008 起逐年连续；brief 断供记载不实） |
| （产出）alt_regime_signal | 10,864 | 2026-09-30 | F4/F8/F11/F12/F14/F15/F23 活；**F7 止 2018-11-17**；F10/F25 暖机未出值 |

断供/半死清单（5）：typhoon_landfall_history(2018)、port_monthly(2025-07)、stat_monthly(2025-06)、reservoir_level(2026-07-31 半死)、stat_analysis(2019-08 死)；浅史清单(3)：fx_rate_ecb、stock_comment、visibility。

## ② 逐表六问矩阵（Q1 因子/Q2 策略/Q3 模块/Q4 环节/Q5 地图/Q6 盲点；空=查无留痕）

| 表 | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 |
|---|---|---|---|---|---|---|
| alt_shipping_index | F4 已产；运价同比/成本压力指数 | 资源链轮动；校准警告：BDI→出口方向正确率~54%（在案引文），禁外推出口链 | regime_data_loader（经 alt_regime_signal）已通 | 盘前风险日历（D 夜窗） | 产业链图干散/资源 BOM 叶**未挂**（W4） | HRCI/BHMI 断档在册；BDTI 油运零消费 |
| alt_fx_rate_ecb | FX 动量/进口成本指数 | 宏观择时/通胀对冲 | 宏观因子、macro_data 补充位 | 盘前 | 通胀链进口叶**未挂**（W5） | 31 天浅史；ECB 中间价 vs 在岸口径差未验 |
| alt_stock_comment | 机构关注度/评级变动因子 | 个股关注度溢价（文献方向） | 个股因子链（factor_feature_value 位） | 盘后 | 个股面 | 仅 20 天；DFC 口径 PIT 未验（W3） |
| alt_typhoon_track | F7b 风圈强度连续量（radius7-10/wind 未消费） | 风险日历；农产品事件（台风-菜价引文在案） | alt_regime（F7 join 腿） | 盘前风险 | 农产品叶+事件日历 | tcno='0000' 脏码剔除逻辑已在 F7；radius 列全零消费 |
| alt_typhoon_landfall_history | 事件本体（登陆省份/强度） | 同上 | F7 主腿（**死于 2018 断供**） | — | — | **族内最高价值修复点 W1** |
| alt_typhoon_names | 查无因子（命名学文本彩蛋） | — | — | — | — | 纯参考表 |
| alt_sz_air_quality_daily | AQI 极值/污染事件计数 | 无直接策略 | 事件日历 | 盘前区域事件 | — | 30 站与 region 区级双口径未合并 |
| alt_sz_air_quality_region | 分区 6 污染物横截面 | — | — | — | — | 同上；monitor_time String 型 PIT 弱 |
| alt_sz_climate_hist | 温度距平/季节基准（需多年积累） | 用电/农产品季节性 | F8 潜在上游（现 F8 用 weather_data） | — | — | 与 weather_data/ground_obs 职责重叠（内收候选）；1970 脏日 |
| alt_sz_ground_obs | 小时级温压风湿 | 高频天气事件 | F8 上游候选 | — | — | 气象四表重叠簇（收敛候选） |
| alt_sz_visibility | 能见度极值（港口/航空中断代理） | 事件驱动（盐田港作业） | — | — | 港口链 | 29 天浅史+7 站 |
| alt_sz_env_meteor | 查无（语义不明：中暑/扩散条件?） | — | — | — | — | type 码脏、字段语义未文档化 |
| alt_sz_weather_warning | 预警频次×级别→极端天气日历 | 事件驱动 regime（F8 姊妹位） | 作战室/日历 | 盘前 | 事件图 | 与 typhoon 联动未挖（台风白色预警先行指标） |
| alt_sz_marine_forecast | 海区风浪/预警（yujing 列未消费） | 港口作业/航运事件 | — | — | 港口链 | 27 列宽表近全零消费；ddatetime/forecast_time 双 PIT 未清 |
| alt_sz_house_daily | 深圳网签套数/面积（分用途分区） | 地产链轮动/政策效果验证 | regime 候选 F28 | — | 产业链地产叶（建材/家电传导） | 网签口径滞后真实成交 |
| alt_sz_house_area | 分区成交面积月度 | 同上 | — | — | — | 与 house_daily 重叠（收敛候选） |
| alt_sz_house_listing | 挂牌量/去化代理 | 领先指标（挂牌→价格） | — | — | — | 滞后 3 月；2.4M 明细零消费（降采样候选） |
| alt_sz_house_presale | 预售证节奏→供给领先 | — | — | — | — | Oracle 脏日期+滞后 27 月（W8 核源） |
| alt_sz_market_subject | 查无交易可用因子 | — | — | — | — | 年频滞后 3 年零消费（归档候选） |
| alt_sz_stat_monthly | 深圳 CPI/社零/出口/GDP 17 序列 | 宏观择时区域交叉验证 | 宏观因子 | — | 宏观图 | 断供 16 月；深圳 CPI vs 全国传导时差未验（W6） |
| alt_sz_stat_analysis | 统计分析文本（情绪源已死） | — | — | — | — | 14 篇/2019 止，归档候选 |
| alt_sz_port_monthly | 深圳港 TEU/机场货邮月度 | 出口链验证（F4 互补：港口实绩 vs 运价预期） | — | — | 产业链出口叶**未挂** | 断供 15 月（W6） |
| alt_sz_enterprise_year | 查无 | — | — | — | — | 年频滞后 4 年零消费（归档候选） |
| alt_sz_reservoir_level | 库容率/水位距平 | 查无 A 股直接策略 | 名义客=supply_sentinel | — | — | 半死管线在案；75M 行=族 94% 体积（降采样第一候选） |
| alt_sz_reservoir_rain_day | 集雨区降雨日值 | 弱 | — | — | — | 与气象表簇部分重叠 |
| alt_sz_reservoir_rain_month | 降雨月聚合 | — | — | — | — | — |
| alt_sz_reservoir_station | —（维表） | — | — | — | — | — |

## ③ 十二应用面判定（逐格两态留痕）

| # | 应用面 | 判定 | 依据/工单 |
|---|---|---|---|
| 1 | 大盘/指数 | **适用** | F4（BDI regime）已产；台风/预警→风险日历（W1/W7） |
| 2 | 板块/行业 | **适用** | 地产（house_daily→W8）、航运/出口（BDI+港口→W4）、公用（高温他道 F8） |
| 3 | 个股 | 仅 alt_stock_comment **适用**；其余不适用（区域面数据无个股粒度） | W3 |
| 4 | 做T（日内） | 不适用 | 全族日频/低频+1 小时气象，无日内信号 |
| 5 | 可转债 | 不适用 | 族内无转债字段（F25 走 sentiment_panel 他道） |
| 6 | ETF/LOF | 不适用（间接经板块面） | 归 #2 |
| 7 | 期货/商品 | **部分适用** | 台风→菜价/农产品事件（引文在案）、BDI→干散商品链（W7） |
| 8 | 币圈 | 不适用 | FX 为法币（ECB），非 crypto |
| 9 | 宏观/择时 | **适用** | FX 进口通胀输入（W5）；深圳 CPI 月度交叉验证（断供待修 W6） |
| 10 | 产业链/传导 | **适用（重点）** | BOM 叶挂价三候选：BDI 运价叶/USD-CNY 进口叶/深圳港 TEU 出口验证叶（W4/W5/W6） |
| 11 | 事件驱动 | **适用（重点）** | 台风轨迹/预警/海况 yujing/AQI 极值→事件日历与作战室（W1/W7） |
| 12 | 文本/情绪 | 弱适用 | stock_comment 评级统计；stat_analysis 文本源已死不适用 |

**四个重点挖掘方向结论**：
1. **产业链地图挂价**：MOD-SIG-125 蓝图 P2 未施工；本族可挂 BOM 叶=BDI（干散成本）/USD-CNY（进口成本）/port_teu（出口实绩验证）。挂点经 ig_node_binding 传导链商品节点，登记为 W4/W5/W6 地图回填项，解锁条件=产业链图进入施工批。
2. **宏观通胀链**：猪价链在 alt_regime F10-F12（他道已通）；本族贡献=进口通胀腿（FX）+区域验证腿（深圳 CPI 月度，断供中）+事件冲击腿（台风→菜价→CPI，consumption plan F7 增强引文在案）。
3. **regime 信号扩容**：现有 10 信号位（F4/F7/F8/F10-F12/F14/F15/F23/F25）。扩容候选：**F28 深圳地产景气**（house_daily 网签同比/环比）、**F7b 台风强度连续量**（radius7/wind 替代二元事件）、**F29 FX 动量**（USD-CNY 30 日动量）。F7 本体修复最高优（断 8 年空转）。
4. **事件驱动**：weather_warning 年 800-1500 条+marine_forecast yujing+AQI 极值全部零消费，合成"深圳本地极端事件日历"成本低（三表 JOIN 已可行），登记为 W7 配套。

## ④ 接线工单（整族挂账与个别高价值分离）

**整族挂账 defer（22 实体，defer_reason 登记入 census/wiring）**：alt_sz_ 20 岛+typhoon_names+stat_analysis。理由=区域另类数据与 A 股交易决策弱耦合、census value_score 全 0.5、登记册 declared demand 全空；90 天门照计龄。其中气象五表（climate_hist/ground_obs/visibility/env_meteor/air_quality×2）与 weather_data 构成重叠簇，待内收审计（§4 w5_1 判据）后统一裁定，defer 期间不注销。

**个别高价值接线工单（按优先级）**：

| # | 工单 | 对象→消费端 | 优先级 |
|---|---|---|---|
| W1 | **F7 复活**：landfall_history 2019-2026 回补（源=中央气象台登陆公报，或纯 track 推导登陆事件替代 join） | alt_regime F7 台风事件，regime 风险日历断 8 年实证修复 | P0 |
| W2 | reservoir_level 半死管线人工核源（缺口在案 st-data-fix 排期中）：确认源停发则转降采样+缺口封档 | 缺口治理既有流程 | P0（在案） |
| W3 | alt_stock_comment 接个股因子链：attention_index/composite_score 建 factor_registry candidate（过 S0-S7 考试） | 个股关注度因子 | P1 |
| W4 | BDI 挂产业链资源链 BOM 叶（F4 已有，补地图挂点 ig_node_binding） | MOD-SIG-125 图谱 | P1（解锁=图谱施工） |
| W5 | alt_fx_rate_ecb 挂宏观通胀进口叶；FX 对扩容评估（现 3 对） | 宏观因子节点 | P1 |
| W6 | port_monthly/stat_monthly 断供 15/16 月修复报数据线（核对 data_supply_sentinel 阈值行缺失——reservoir 案实证 sentinel 无阈值行则免检） | 停更检测补位+两表复活 | P1 |
| W7 | F7b 台风强度连续信号+深圳极端事件日历（track radius×warning×marine yujing 合成） | regime 扩容候选卡+作战室 | P2 |
| W8 | F28 深圳地产景气信号候选卡+house_presale 核源（Oracle 日期脏格式） | regime 扩容（低优） | P2 |

## ⑤ 六向台账（挖矿审计：内部动作全查，外部动作=既有引文复用）

| 向 | 结论 |
|---|---|
| ①上游 | 生产者=akshare_alt_provider（深圳数据局/气象局口岸水库）+fx_ecb_provider+台风三源；**landfall 上游 2019 起未接公报源**（断供根因）；reservoir 源端确认无 8 月后数据（在案复跑 3 次） |
| ②下游 | alt_regime_signal→regime_data_loader→condition_package（回测 regime 验证）链路实证存在；dashboard 前端呈现=零（只登记不施工） |
| ③算法/文献 | 本轮未新开网搜轮次（内部矿脉未枯尽，先挖内部）；复用 alt_data_consumption_plan.md R1-R20 已核引文（台风-菜价/CPI 测算/库存周期，URL 在案）。外部长尾：风圈×菜价新实证、FX 对扩容文献——登记未挖 |
| ④后端 | scripts/ch/apply_market_tables_ddl.py 全族 DDL；backfill_reservoir_level_full.py 在；**缺 landfall 2019+ 回补脚本**（W1 物料） |
| ⑤前端 | 全族无图表位（查无留痕；登记即可） |
| ⑥字段 | system.columns 逐表已核；脏点清单=house_presale Oracle 日期/env_meteor type 码/climate_hist 1970 脏日/tcno '0000'/visibility 29 天浅史/双 PIT 列未清（marine/ddatetime+forecast_time） |

## ⑥ 自审闸三态（Owner 级处置建议——本代理不执行，走宪法 §5 数据门）

| 态 | 实体 | 建议与理由 |
|---|---|---|
| **保留+接线**（6） | shipping_index、fx_rate_ecb、stock_comment、typhoon_track、typhoon_landfall（修复后）、alt_regime_signal | 已有 regime 消费链或 P1 工单在册；采集全自动、边际成本≈0，符合终局全貌 |
| **保留+defer**（14） | 深圳气象 5+楼市 4+水库 4+stat_monthly | 采集管线已长成、保留成本≈0；事件日历/区域图谱是终局候选位置——挂起排期（解锁=产业链区域节点施工批/W7 立卡），非封矿 |
| **降采样候选**（2） | reservoir_level（核源后日频聚合 75M→约 2M 行）、house_listing（明细→日聚合+明细归档冷库） | 两表=全族体积 94%+3%；reservoir 半死管线在案、source 停发则高频明细无边际价值；属资金/数据破坏性操作，**须 Owner 三步验证门** |
| **归档候选**（4） | stat_analysis（死 7 年/14 行）、enterprise_year+market_subject（年频滞后 3-4 年零消费）、house_presale（滞后 27 月脏格式，核源后定） | 六问全查无+无未挖长尾+终局无位置（区域统计文本源已死）；走 §10 源死亡处置（disabled+能力迁移清单），非删除 |

**一句话总建议**：整族"管线活着、消费没跟上"——保留全部在采管线（自动化终局资产），把修复预算压在 W1（F7 复活，8 年空转）与 W2（reservoir 半死核源）两点；体积治理（降采样 2 表）与退役（4 表）打包一次 Owner 门裁定。

## 挖矿日志（mining_sop §7 强制）

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | CH 全族实勘（28 表行数/max date/引擎） | signal | 全族 8,000 万行、断供 5 表、浅史 3 表 |
| R2 | 六问坐标逐表映射 | signal | ②矩阵：真消费 2.5/27，六问全查无 8 表 |
| R3 | census 台账核对 | signal | 24 岛实测（brief 记 20，校正）；reservoir 名义有客=哨兵引用 |
| R4 | tasks/调度反查 | signal | 27 表任务全 enabled；daily_event 槽位集中（断供前科槽位，探活义务在案） |
| R5 | known_data_gaps 反查 | signal | HRCI/BHMI/reservoir 三缺口在册；weather_warning 断供记载不实（实测连续） |
| R6 | 消费端 grep 双向 | signal | F7 max=2018-11-17 实证（landfall 断供卡死 regime 信号）；下游 regime 链存在 |
| R7 | 序列口径抽查（stat/port/house/env） | signal | stat_monthly 含深圳 CPI 17 序列；port 7 序列；env type 码脏 |
| R8 | F 槽位与 consumption plan 对齐 | signal | 扩容位 F28/F7b/F29 立卡；F10/F25 暖机未出值留痕 |
| — | 外部网搜轮 | 未开（非受阻） | 内部矿脉未尽；外部长尾已登记（⑤③向） |

> 长尾矿脉清单（未挖，登记后继）：①台风风圈×菜价/CPI 新文献轮；②FX 对扩容与在岸/离岸口径；③air_quality 双口径合并方案；④气象五表与 weather_data 内收合并审计。六向内部全查无之表=8 张（names/stat_analysis/enterprise/market_subject/reservoir 三表/marine 大部），已按⑥处置建议归类，未发现未挖长尾——内部矿脉至此枯竭。
