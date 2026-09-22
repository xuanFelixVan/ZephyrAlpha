---
asset_id: "DOC:docs/_working/ultimate_library/ulib3b_demand_gap_ledger.md"
ttl: "task_bound"
---

# 需求侧缺口册（G15-② potential_consumers 增枝前置挖矿·产出二件/三件）

- 班次：st-ulib3b-20260922（增补令 #14②：从 TDM/排班表业务文档挖需求侧清单）
- 证据源：config/trading_decision_map.yaml（TDM）、docs/_working/sector_line/（骨架 v0/考试卡 S10/D2/盘点册/缺口单）、docs/_working/trading_vision/data-sufficiency-matrix、daily-orchestrator-blueprint、daily_loop_campaign 对账册
- 状态口径：已供给（写明供给表）/ 部分缺口 / 缺口 / 未明（声明了需求但四证据源找不到供表）

## 一、大盘层（L0 盘前计划 / L1 传感器）

| # | 需求 | 声明处 | 状态 |
|---|---|---|---|
| D1 | RegimeSnapshot 7 态概率分布（HMM r1-r4+overlay） | TDM:271-292 | 已供给（c1_backtest.regime_snapshot_history） |
| D2 | 涨停/跌停家数、炸板率、连板梯队高度（S2 结构传感器） | TDM:344-351 | 部分缺口（连板梯队明细表待 DDL=GAP-F-13） |
| D3 | 涨停家数/炸板率/晋级率 FCT-* 级注册条目 | TDM:308-311 | 缺口（仅 family 级） |
| D4 | 期权 IV 曲面（50ETF+300ETF ATM）主路径供表 | TDM:389-404 | 未明（后备=DS-150） |
| D5 | 宏观四组：Shibor/两融社融 M1M2 信用利差/美债美元纳指/监管动态 | TDM:419-443 | 部分缺口（两融已供 DS-098；海外/社融供表未明） |
| D6 | 情绪六段分布（周级灰度）供给件 | TDM:508-526 | 未明 |
| D7 | 8 态转移先验/相似日推理/Brier 校准消费接线 | TDM:214,236-250 | 部分缺口（L0-04 三消费点未接线） |

## 二、板块层（TDM-E-L2 + 骨架 v0）

| # | 需求 | 声明处 | 状态 |
|---|---|---|---|
| D8 | 板块日 K 深史（q3/q5/q20 动量+RRG） | 骨架:52,65 | 已供给（kline_sector_880 六年 A 态） |
| D9 | 板块实时截面 up_home/down_home/涨速 | 骨架:53 | 已供给（sector_snapshot A 态） |
| D10 | 成分股映射（涨停比分母+资金聚合） | 骨架:54 | 已供给（sector_constituent SCD-2） |
| D11 | 涨停原料（limit_up_pool 含 industry） | 骨架:57 | 部分缺口（daban 断 09-15=G3） |
| D12 | 行业净流入分位 | 骨架:56 | 缺口（sector_fund_flow 仅 6 天=G7） |
| D13 | emotion_index 成品（偏好第二轴 0-1 分位+四态） | 骨架:51,74-93 | 缺口（D 态在途 mock=G1） |
| D14 | regime dominant 全值域档（r10-r12） | 骨架:50 | 部分缺口（anchored 只产 r1-r4） |
| D15 | L2 门三原料 top/retained_sectors/score | 盘点册:68-72 | 缺口（gate 恒 not_evaluated=G4） |
| D16 | 三级门槛阈值校准（0.60/0.80+水温+tilt） | 缺口单:34 | 缺口（全 proposed=G8） |
| D17 | 拥挤度+景气+资金增强三标尺全家桶入骨架 | 盘点册:172-181 | 已供给原料在库（G14 待接线） |
| D18 | 板块坐标系裁定+概念成分时戳快照 | 缺口单:26,44 | 缺口（G5/G12，概念轴有前视硬 gate） |

## 三、个股层（L3）

| # | 需求 | 声明处 | 状态 |
|---|---|---|---|
| D19 | Universe 剔除字段组（停牌/ST/市值/成交额） | TDM:1417-1425 | 部分缺口（limit_up_down 历史仅 2026-08-03 起） |
| D20 | 龙虎榜席位名单+T-1 PIT 榜 | TDM:2054,3403 | 已供给（dragon_tiger_seat 4.5 年 A 态） |
| D21 | 流通股本数据工程（获利盘/单峰密集度） | TDM:2083-2086 | 缺口（裁定#257④ 挂起） |
| D22 | 池成员持久化载体 | TDM:1850-1862 | 缺口（M-41 待登记） |

## 四、做T/持仓层 + 考试卡 + 排班链

| # | 需求 | 声明处 | 状态 |
|---|---|---|---|
| D23 | 大盘段位直喂+20 日振幅+成本模型（做T资格门） | TDM:2822-2837 | 已供给（DS-150+CST-T0-001） |
| D24 | 封单 tick 买一档量代理（DS-195） | TDM:2662-2681 | 部分缺口（MFE/MAE 台账字段欠账） |
| D25 | 节前事件前置（财报/解禁日历）+交易日历数据源 | TDM:2953-2957 | 缺口（M-26 待登记） |
| D26 | kline_etf_60min 真实小时线（做T臂 OOS） | 矩阵:21-22 | 部分缺口（缺约 9 万 bar，合成方案在途） |
| D27 | S10 卡双窗数据集（kline_sector_880 全集） | 考试卡:30-40 | 已供给（六年 A 态） |
| D28 | D2 卡主判两轴（regime dominant+emotion_index 真值窗 W_map≥120 日） | 考试卡:84-93 | 缺口（INSUFFICIENT 预登记） |
| D29 | S2 regime 快照滞后阈值治本（供给闸 3 日 vs 消费阈 1 日） | 对账册§4 | 部分缺口（已补印未治本，Owner 清单） |
| D30 | state_matrix 六空格 pending-owner-adoption | TDM:4461-4475 | 缺口（Owner 门位未填） |
| D31 | 预算带/过渡带数值 proposed→confirmed | TDM:3713-3719 | 缺口（待 Owner 批） |
| D32 | 晨判美股夜盘+股指期货+宏观日历供表 | 蓝图:234-235 | 未明 |
| D33 | 盘中 L1 量比/涨跌家数比/拉板数五证据列 | 蓝图:230 | 部分缺口（kline_index 家数列 07-02 后断供） |
| D34 | L4-14 执行成本反馈闭环接线 | TDM:2529-2540 | 缺口（三零件在、选择器不消费=断链实证） |
| D35 | ETF 日线天量检测登记（护盘白名单） | TDM:3264-3266 | 缺口（待登记） |
| D36 | tick_depth_5 五档深度 walkforward 补齐 | 矩阵:18 | 缺口（差约 17 交易日，保留窗每晚少一天） |

## 五、需求侧结论（喂 potential_consumers 增枝设计）

1. **需求方主要按"标尺"提需求**（拥挤度/景气/情绪/宽度/杠杆），供方按"表"记账——增枝的 potential_consumers 应写"能喂哪个标尺/哪个节点"，粒度对标 TDM 节点与骨架成分，不做自由文本。
2. 已供给项的供表写法可直接机械化（kline_sector_880→板块动量标尺→TDM-E-L2/L1-S1 等），首批 potential_consumers 回填可从"已供给"36 项零推导直填。
3. 缺口/未明 20 项=需求侧反查的真正价值：从需求侧能扫出"无人供表"的缺口（正查=表找用途，反查=用途找表），potential_consumers 维度天然支持双向。
