---
asset_id: "DOC:docs/_working/ultimate_library/ulib3b_supply_relationship_ledger.md"
ttl: "task_bound"
---

# 供数关系册（G15-② potential_consumers 增枝前置挖矿·产出一件/三件）

- 班次：st-ulib3b-20260922（增补令 #14，Owner 2026-09-23 追加）
- 证据源：battle_map 12 域+panorama（docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/）、图书馆馆页（docs/library/）、63 号数据利用审计（docs/_audit/data_utilization_audit_2026-08-24.csv）、板块线/情绪线/自动化战役台账（docs/_working/）
- 方法：三路只读摘抄（battle_map+馆页 / TDM+排班需求侧 / CSV+台账），本册=审编定稿
- 用途：potential_consumers 增枝申请（增补令 #11）的证据库 + 全馆 TBL 卡供数维度填充底稿

## 一、63 号审计 CSV 统计（2026-08-24 时点）

- 106 数据行（DS-001~DS-108，缺 DS-105/DS-107）：**covered=40 / zero_ref=59 / code_only=7**
- src_refs Top：backtest.result 5616｜order.target 1820｜position.snapshot 569｜tick 471（memo 116）
- zero_ref=59 张全清单见馆外原件；结构性聚集：factor.ashare_*14 张全零、barra 族 4 张全零、backtest *_result 8 张全零、data_eng 域 5 张全零、fundamental 5 表全零（fin_income/balancesheet/cashflow/indicator/daily_basic）、macro.cn_macro 与 industry.sw_daily 全域零
- CSV 只有引用计数无方向字段——消费方向以本册二/三节明文为准

## 二、明文供给关系（A 表 → 喂 B 用途，逐条带出处）

### 板块线台账（docs/_working/sector_line/sector_internal_inventory.md §12，2026-09-22 实探）

| # | 资产 | 用途 | 证据 |
|---|---|---|---|
| S1 | c1_market.dragon_tiger / dragon_tiger_seat（618k 行 4.5 年深史） | 板块 hot money 维度/游资席位 | sector_internal_inventory.md:172 |
| S2 | c1_market.margin_trading | 板块杠杆资金分布（个股经成分聚合上溯） | 同上 :173 |
| S3 | c1_market.northbound_hold_snapshot | 机构板块偏好（停 3 个月=C 态） | 同上 :174 |
| S4 | c1_market.daily_valuation | 板块估值分位（防御/进攻风格判别） | 同上 :175 |
| S5 | c3_fundamental.analyst_forecast（104k 行 B 态） | 景气度标尺原料（国盛三标尺之景气维） | 同上 :176 |
| S6 | c3_fundamental.shareholder_count / top10_shareholders | 板块筹码维（远期） | 同上 :177 |
| S7 | c1_market.stock_daily_basic（7.1M 行） | 拥挤度标尺原料（换手聚合） | 同上 :178 |
| S8 | kline_sector_880 / kline_sector / sector_snapshot / sector_fund_flow | 板块层主供（近 3 日在产满量实证） | 同上 :185-190 |
| S9 | kline_sector / concept_board | dashboard 前端展示消费 | 同上 :204-205 |

### 情绪线台账（docs/_working/emotion_line/internal_inventory.md，2026-09-22 实探）

| # | 资产 | 用途 | 证据 |
|---|---|---|---|
| S10 | kline_daily + kline_index | 涨跌家数比/大盘涨幅成分 | emotion_line/internal_inventory.md:32,68 |
| S11 | kline_daily（amount/turnover 列） | 成交额分位/换手分位原料 | 同上 :33,74 |
| S12 | margin_trading | 两融温度成分（覆盖仅 2 个月，滞后 1-2 日） | 同上 :34,80 |
| S13 | dragon_tiger / dragon_tiger_seat | 游资温度/龙头封开板代理 | 同上 :35,88 |
| S14 | block_trade / block_trade_detail | 折价率均值=机构情绪代理 | 同上 :36,91 |
| S15 | news_sentiment_window（scope=market 183 行） | 情绪成分 C6（rule 法打分） | 同上 :39,130 |
| S16 | stk_limit（921 万行） | 涨停价真源（daban 前置，三级解析链 100% 验证） | 同上 :43,57 |
| S17 | money_flow + alt_stock_comment | cohort 画像原料 | 同上 :44-45,151 |
| S18 | limit_up_down（09-22 通） | daban 断供期涨停家数替代（C1 权重 0.4 子项） | 同上 :176,206 |
| S19 | auction_snapshot（266k）+ auction_book（303 万行） | 竞价情绪成分 v0.2 可挂载 | 同上 :177-178,185 |
| S20 | research_report（14.7 万行含 rating） | 评级情绪成分候选 | 同上 :179,187 |
| S21 | daban_board_event / daban_engine_load | 涨停家数/连板/炸板/晋级四成分（09-15 断供中） | 同上 :30-31,54 |

### battle_map 12 域（docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/）

| # | 资产（L 层级） | 消费节点 | 证据 |
|---|---|---|---|
| S22 | 龙虎榜/资金流/大宗（L0） | BM-SEL-05 主力行为感知 | battle_map_05_stock_selection.md:714 |
| S23 | 板块排名/资金流（L0/L1） | BM-SEL-08 板块轮动序列 | 同上 :825 |
| S24 | 板块新高占比（L0） | BM-SEL-09/10 调整周期+生命周期 | 同上 :863,900 |
| S25 | 涨跌停/停牌/ST+上市天数（L0） | BM-SEL-16 分级指标过滤 | 同上 :1408 |
| S26 | 竞价涨幅/量比（L0 集合竞价） | BM-SEL-23-A-5 竞价强度因子 | 同上 :3094 |
| S27 | 连板断层/首板断板统计（L0） | BM-SEL-23-B 情绪周期定位 | 同上 :2434 |
| S28 | 主力净流入+大单占比（L0 资金流向/成交明细） | BM-SEL-24-A-4 资金维度 | 同上 :3259 |
| S29 | 大盘指数收益+波动率（L0） | BM-BUY-02-A-1-a 3×3 矩阵 8 态 | battle_map_06_buy_flow.md:553 |
| S30 | 大盘历史序列（L0） | BM-BUY-02-A-1-d HMM 体制转换 | 同上 :656 |
| S31 | 压力位（L1 因子层） | BM-SELL-01 突破成败信号 | battle_map_07_sell_flow.md:101 |
| S32 | 分时因子量比/CVD/VPIN（BM-SEL-02/C-009） | BM-SELL-08 做T日内套利 | 同上 :487 |
| S33 | 融资余额+流动性+政策新闻+外围指数 | BM-RC-06-A 系统性风险五信号 | battle_map_09_risk_control.md:1214 |
| S34 | 尾部数据+跳跃检测 | BM-RC-06-B 尾部风险 EVT/POT | 同上 :1247 |
| S35 | miniQMT tick + CH c1_market 日线 | BM-BT-02-B 回测多源数据接入 | battle_map_03_backtest_validation.md:63,241 |
| S36 | 成交量+持仓+行情 | BM-RC-04-E 流动性风险监控 | battle_map_09_risk_control.md:971 |

### 台账补遗（automation/campaign、dataqa 归档）

| # | 资产 | 用途 | 证据 |
|---|---|---|---|
| S37 | sim_trade_log/sim_pocket_daily/sim_platform_journal/strategy_screen | 模拟盘平台四件+成绩台账 | CAMPAIGN_LEDGER.md:21 |
| S38 | alt_fx_rate_ecb（cron 35 23 * * 0-4） | 汇率表在产 | 同上 :49,75 |
| S39 | crypto_kline_daily | 7×24 资产（daily_crypto 半死 09-19=0） | dataqa gaps_registry_review.md:32 |
| S40 | consensus_daily（165 万行） | 部分回填（2022-2025 仍断） | 同上 :62 |

## 三、馆页现状判定（供数维度缺位实证）

- docs/library/data.md（322 表卡）：**纯目录（asset_id/kind/status/home 四列），零供数语句**——"记是什么不记能喂什么"即 G15-② 系统缺口的直接物证
- battle_map 消费"L0 涨停数据/盘口/集合竞价"等抽象类，从不点名具体表；data.md 有表不挂用途——两册合计恰好互补断链，potential_consumers 维度=补此断链
