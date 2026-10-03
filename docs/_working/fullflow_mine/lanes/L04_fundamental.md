---
ttl: task_bound
title: "基本面族挖矿作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

# L04 车道：c3_fundamental 基本面族（34 表）数据用途挖矿

> 方法论：onboarding_sop §9A 六问 + §9B 12 应用面 + mining_sop 六向寻路/自审闸三态。
> 实勘 2026-10-01，CH c3_fundamental 只读（zephyr_reader，26.6.1）；census=data/runtime/consumption_census_ledger.json（2026-09-30 读数，fundamental_table 族 10 岛全 zero/producer-only 实证）。

## 0. 结论速览

实体 34 表，总行数 4,607.7 万：**24 鲜 / 4 断供 / 2 停滞 / 4 试点**。census 孤岛 10（本车道复核 8 活跃 + 2 retired 保留件维持原判）。**consensus 断供疑云否证**（逐年连续至 2026-09-30，L12 先决已清）。接线工单 9 条（top3=W1 评分链停摆 / W2 质押断供 / W3 流通股东缺批）。三态裁定=接线 5 / 挂账 3 / 退役 0。

## 1. 族读数（CH 实证：行数 + 关键日期 + 判定）

| 表 | 行数 | max 关键日期 | 判定 |
|---|---|---|---|
| restricted_shares | 10,208,142 | announce 2026-07-02 | 鲜（解禁预告管线） |
| news_data | 8,235,585 | publish 2026-10-01 | 鲜（W1 原料侧） |
| consensus_daily | 6,828,977 | trade_date 2026-09-30 | 鲜；**2022 断供否证**（§1.1） |
| news_sentiment_score | 7,733,898 | publish 2025-09-09 | **断供 13 个月**→W1 |
| equity_pledge_summary | 1,723,195 | end_date 2026-09-24（名义） | **断供**：月行数 8950(06)→4445(07)→4(08)→4(09)→W2 |
| top10_circulating_shareholders | 2,138,764 | announce 2026-05-15 | **缺 H1-2026 批**→W3 |
| top10_shareholders | 1,500,455 | announce 2026-06-30 | 鲜（H1 批已到，对照 W3） |
| main_business | 2,094,453 | report_period 2026-03-31 | 停滞：落后一期（H1-2026 缺）→W9 |
| equity_pledge_detail | 122,922 | announce 2026-07-03 | **断供**（07 月 106 行后归零，随 W2） |
| shareholder_count | 514,396 | announce 2026-09-30 | 鲜；月供 1157~5504 只无断月（前科未复发） |
| consensus_daily_repaired | 1,655,363 | 2026-09-15 | 修复件，滞后主表 15 天 |
| balance_sheet / income_statement / cashflow_statement | 339,738/346,176/310,447 | announce 2026-09-02 | 鲜 |
| financial_indicator / financial_derived | 386,437 / 306,527 | 2026-09-12 / report_period 2026-06-30 | 鲜 |
| analyst_forecast | 118,863 | 2026-09-30 | 鲜 |
| dividend / ex_dividend_event / repurchase | 221,021/57,864/6,706 | 09-22/09-24/10-01 | 鲜 |
| share_change / share_unlock / restricted(解禁侧) | 190,580/30,449 | 09-25 / unlock 2027-09-29 | 鲜（未来解禁日=正常前瞻） |
| disclosure_plan / audit_opinion | 324,609/96,010 | 08-31/05-29 | 鲜（年报季产物季节正常） |
| research_report / earnings_forecast / express_report | 146,769/125,582/28,708 | 09-18/07-03/07-02 | 鲜（事件表淡季，待 Q3 窗验证） |
| rights_issue | 80,803 | announce 2026-06-30 | 低频正常 |
| pdf_forecast_extracted | 192,365 | publish 2021-12-31 | **停滞 5 年**→W6 定性 |
| ir_activity_record / ir_activity_extracted | 30/30 | 09-18 | 试点量级 |
| irm_interactive_qa / irm_interactive_extracted | 500/74 | 09-16/09-18 | 试点量级 |
| industry_class_suppl | 10,141 | valid_from 2026-09-30 | 鲜（ifind 5203+tushare 4938 双源） |

### 1.1 consensus 断供定案（L12 先决）

**否证。** 逐年行数 2017=38.3 万→2018=45.1 万→2019=47.4 万→2020=51.3 万→2021=56.3 万→**2022=77.2 万**→2023=97.9 万→2024=100.8 万→2025=102.7 万→2026YTD(至 09-30)=66.0 万，无年缺口、max=2026-09-30、08 月起交易日全覆盖。"2022 后断供"系讹传（2022 反为台阶上行年）。L12 FCT-EXP-003 修正广度 / FCT-EXP-005 分歧度先决已清，可开工。

## 2. 孤岛 8 表六问矩阵（census 10 岛中 8 活跃；2 张 retired 保留件除外）

| 孤岛 | Q1 因子候选 | Q2 策略 | Q3 模块 | Q4 环节 | Q5 地图 | Q6 盲点 |
|---|---|---|---|---|---|---|
| equity_pledge_summary | 质押率横截面/质押变化率/全市场质押温度 | 排雷风控、小盘负筛 | **0**（producer-only） | 盘后质押周更 | TDM 个股风控节点 | 断供 2.5 月无告警 |
| top10_circulating | 机构持股集中度/牛散跟踪/股东进出 | 跟庄、机构抱团 | **0** | 季报后更新 | TDM 个股节点 | H1 批缺无检测 |
| shareholder_count | 户数环比筹码集中度（文献强因子） | 筹码选股、散户撤离反选 | **0** | 季报后更新 | TDM 个股节点 | 前科"断供两月无人知"本期未复发 |
| share_change | 股本变动率/送转强度 | 送转预期、事件驱动 | **0** | 盘后公司行动 | TDM 公司行动节点 | 无 |
| rights_issue | 配股稀释率 | 公司行动事件、除权处理 | **0** | 盘后公司行动 | TDM 公司行动节点 | 1970 sentinel 脏值 |
| industry_class_suppl | 行业分组基准/行业动量分组 | 行业轮动、板块策略 | **0** | 盘前分组更新 | 行业图/概念板块图挂链 | 双源 symbol 格式不一致 |
| ir_activity_record | 调研热度（关注度代理） | 事件驱动、关注度因子 | **0** | 无 | TDM 资讯节点 | 试点 30 行无扩产决策 |
| irm_interactive_qa | 提问情感/回应质量（NLP） | 文本情绪增强 | **0** | 无 | 无 | 试点 500 行无扩产决策 |

## 3. 孤岛 8 表 §9B 12 应用面矩阵（√=适用留痕即工单方向，×=不适用留痕）

| 孤岛 | 大盘 | 板块 | 个股 | 做T | 转债 | ETF | 期货 | 币圈 | 宏观 | 产业 | 事件 | 文本 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| equity_pledge_summary | √温度 | √热度 | √排雷 | × | × | × | × | × | × | × | √爆仓 | × |
| top10_circulating | × | √抱团 | √跟庄 | × | × | × | × | × | × | × | √进出 | × |
| shareholder_count | × | √聚合 | √筹码 | × | × | × | × | × | × | × | √季报窗 | × |
| share_change | × | × | √股本 | × | × | × | × | × | × | × | √送转 | × |
| rights_issue | × | × | √稀释 | × | × | × | × | × | × | × | √配股 | × |
| industry_class_suppl | × | √基准 | √归属 | × | × | × | × | × | √配置 | √映射 | × | × |
| ir_activity_record | × | × | √热度 | × | × | × | × | × | × | × | √调研 | √纪要 |
| irm_interactive_qa | × | × | √互动 | × | × | × | × | × | × | × | √提问 | √语料 |

基本面族共性：做T/转债/ETF/期货/币圈 5 面 8 表全 ×（公司行动除权处理间接服务全资产，记不适用留痕）。

## 4. 接线工单（9 条，移交总筹排期；本车道不施工）

| # | 工单 | 对象 | 依据（实勘） | 优先 |
|---|---|---|---|---|
| W1 | 恢复新闻评分链 | news_sentiment_score | 原料鲜（10-01）评分止 2025-09-09，13 个月断粮 | P0 |
| W2 | 质押数据断供修复 | equity_pledge_summary(+detail) | 月行数 8950→4；detail 07-03 归零；06 月月度 2259 只/质押率 max 78.7%/>30% 占 4.4% | P0 |
| W3 | 回补 H1-2026 十大流通股东 | top10_circulating_shareholders | max 05-15；对照 top10_shareholders 06-30 批已到 | P1 |
| W4 | 筹码集中度因子接线 | shareholder_count | 鲜+高价值+census 零消费 | P1 |
| W5 | 质押率排雷因子接线 | equity_pledge_summary | W2 修复后即接，§3 大盘/个股/事件三面 | P1 |
| W6 | pdf_forecast_extracted 定性 | 同名 | 止 2021-12-31：退役评审或断供确认二选一 | P2 |
| W7 | 1970 sentinel 清洗 | 6 表 announce_date | audit/dividend/pledge_detail/fi/main_business/rights_issue 含 1970-01-01 脏值 | P2 |
| W8 | IR/互动易试点扩产决策 | ir/irm 4 表 | 30/500 行；extracted 链已通（59+14/25+5）；扩产或挂账须裁定 | P2 |
| W9 | main_business 补 H1-2026 期 | 同名 | report_period 止 2026-03-31，落后一期 | P2 |

## 5. 六向台账（§9A 聚合留痕，查无亦记）

- **Q1 因子**：候选 12（筹码集中度/质押率/质押变化/质押温度/机构集中度/牛散/股本变动/送转/配股稀释/行业分组/调研热度/互动情感）→ 转 factor_mining_sop S0-S7 卡。
- **Q2 策略**：挂点 5（排雷风控/筹码选股/公司行动事件/行业轮动/文本情绪增强）→ strategy_registry data_refs 补挂。
- **Q3 模块**：现存消费者 **0**（8 岛 producer-only 实证）；回填口=data_asset_registry.consumed_by_jobs。
- **Q4 环节**：3（盘后公司行动/季报后筹码与股东更新/盘前行业分组）→ tasks.yaml 调度挂钩。
- **Q5 地图**：3（TDM 个股风控+资讯节点/行业图挂链/产业链行业映射）。
- **Q6 盲点**：4（断供无告警×3：评分链/质押/流通股东；试点无扩产决策；8 岛零接线；repaired 双轨无消费指引）。

## 6. 自审闸三态（§9C 出口，全留痕）

| 三态 | 实体 | 条件 |
|---|---|---|
| 接线 5 | shareholder_count、equity_pledge_summary、top10_circulating_shareholders、share_change、industry_class_suppl | 分别经 W2/W4/W5/W3+行业图挂链前置 |
| 挂账 3 | ir_activity_record、irm_interactive_qa（defer_reason=试点量级不足，W8 裁定后重评，90 天门照计）；rights_issue（defer_reason=待公司行动事件框架统一接入） | 挂账非免死牌 |
| 退役 0 | —（8 表皆留） | news_data_corrupt_20260828 / news_data_pre_tz2_20260828 维持 retired 保留件原判 |

自审：六问逐问跑过留痕（§2/§5）；12 面两态均留痕（§3）；工单全带实勘依据；本车道只读 CH、零既有文件改动、零 git 写。
