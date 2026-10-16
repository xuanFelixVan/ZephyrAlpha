---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
session: st-infoaxis-20261013
date: 2026-10-13
title: 信息供给轴 P0 作业簿·财报域（PEAD/超预期/财务健康）
status: mining_sealed_pending_gate
goal_block:
  goal_statement: 把"预告→快报→正式财报"三阶段落成可验证的超预期/恶化事件流＋财务健康分——每份财报在三个披露时点各自生成增量 SUE 信号与恶化否决线索
  output_contract: earnings_surprise 事件流（SUE 五档＋GAP 四态统一枚举件，事件时点∈{预告日,快报日,正式日}）＋ financial_health_score（Altman Z/O-score＋应计质量合成）双产物，全带 PIT 滞后面登记
  exam_ref: PEAD 式事件研究（预告日/快报日/正式日三时点分别做信号后 20 日漂移＋方向命中＋SUE 分桶单调性；判据数值看数前冻结预注册）
  campaign_ref: st-infoaxis-20261013（裁定#516；挂 TDM-E-L3-02 主链＋L3-04 负面否决器）
---

# 财报域作业簿（13_earnings_workbook.md）

## §0 P0 更正（2026-10-14 实查，装配批施工时发现）

- **fund_earnings_forecast / fund_express_report 两表注册在册但 CH/PG 零实存**（business_data_categories.yaml 登记 ≠ 物化）——"预告→快报→正式三时点"设计面现只有正式财报一时点可工作。预告/快报两时点＝二刀（表物化+采集接线，或降级单时点 v1 呈 P1）。
- 本更正同步 P1 包 A 表补一行（A5 业绩预告/快报表物化路径）。

## §1 问题定义（它出什么）

财报披露是 A 股最高密度、制度强制（上交所：净利润为负/扭亏/±50% 变动须次年 1/31 前
强制预告，预约披露日可查 one.sse.com.cn）的信息事件源。本域产出两件：
①**超预期/恶化事件流**——业绩预告、业绩快报、正式财报三阶段各自生成增量 SUE
（后一阶段是对前一阶段预期的修正，信息不重复）；②**财务健康分**——Altman Z/
O-score＋应计质量合成，供选股漏斗精筛与负面否决器。供：selection_funnel L3-02
五维/六要素消费、负面否决器 L3-04 恶化方向消费、PEAD 式漂移策略信号。

## §2 输出契约 v0

```
earnings_surprise 事件流（表名走 TableRegistry 派生，P2 定形）：
  event_id, event_ts(披露时点), stage∈{forecast,express,report},
  code, sue_raw, sue_band 五档(≤-2/-2~0.5/0.5~0.5/0.5~2/≥2),
  gap_state 四态(GAP_BEAT/GAP_MEET/GAP_MISS/GAP_NO_ANCHOR),
  expectation_source∈{random_walk_sigma, analyst_consensus, forecast_proxy},
  actual_eps, expected_eps, pit_lag 注册(公告日 announce_date→落库时点), freeze_batch_id
统一枚举件：SUE 五档＋GAP 四态在本域唯一出口产出，禁止各模块私有变体
financial_health_score（表名走 TableRegistry 派生）：
  code, as_of_date, z_score(修正系数按待裁 C3 默认), o_score(九变量),
  accrual_quality(Sloan 应计＋Dechow F-score 合成), health_tier, pit_lag, freeze_batch_id
SUE 主算法定为季节随机游走：SUE=(EPS_t−EPS_{t-4})/σ(ΔEPS 四季)，因 A 股分析师覆盖薄；
  分析师一致预期作对照代理（预告期用预告中值作预期代理）——看数前冻结，不做混算。
```

## §3 外部对标（2026-10-13 全网搜，详见班账 §8 车道回报）

| 来源 | 可借鉴点 |
|---|---|
| SUE 两算法谱系 | 季节随机游走（Foster 1977 系）vs 分析师预期残差（FTBM 系）；A 股覆盖薄→主用随机游走＋σ，预告作预期代理 |
| 华泰文本 PEAD (2022) | 文本情感增强版 PEAD，1-6 月持有期——超预期方向可叠文本增强（后置） |
| 上交所披露制度 | 强制预告规则＋预约披露日可查→三时点事件日可精确定位，非估计 |
| SSRN 2025（中国公告） | 公告前 20 日异常收益 3.22%——信息提前泄露/抢跑窗，PIT 检验对照 |
| LSEG GitHub 开源件 | Altman Z＋Beneish M 实现、O-score 九变量——健康分公式底座，系数按 A 股修正待裁 |
| A 股 ST 预测文献 | 样本 3% 不平衡→健康分验收用 AUC 不用 accuracy（判据纪律） |
| Sloan 1996 / Dechow F-score | 应计质量复现：Sloan 应计因子＋Dechow F-score 需自实现（仓内已有应计雏形可并） |

## §4 仓内四层盘点（六向台账·前四向）

### 4.1 数据面
- fund_income_statement=c3_fundamental.income_statement 季频（business_data_categories
  .yaml:1933，miniqmt＋akshare 双源）；PIT 锚列 announce_date（l9_readiness_aggregator
  .py:117 max_lag=100 公告日 PIT；pit_query.py:94 白名单＋版本去重）。
- 业绩预告表 fund_earnings_forecast（yaml:2077 miniqmt ProfitForecast，
  miniqmt_provider.py:2158）＋快报表 fund_express_report（yaml:2252，:2184）均在 PIT
  白名单（pit_query.py:100-101）——三阶段数据两阶段已 PIT 合规。
- 一致预期 fund_analyst_forecast（yaml:2093 akshare stock_profit_forecast_em，
  akshare_provider.py:4416-4448）**不在 PIT 白名单**，仅 news_dual_tagger.py:78-84 手工
  SQL 消费；research_report 预测值列被 Owner 裁定禁 as-of 历史消费（pit_query.py:107-111）
  ——一致预期的 PIT 合规化＝本域数据面治本点。

### 4.2 模块面
- pead_event_model.py（MOD-SIG-110，production，纯内存零 IO）：SUE=(实际EPS−一致预期)/
  |一致预期|，分母<1e-6→None（:158-172）；SueBand 五档 −2/−0.5/0.5/2（:81-105）；20 日
  漂移 close[t+20]/close[t]−1（:190-213）；财报季窗 4/30、8/31、10/31 前伸 10 日历日
  （:69,216-229）。**缺口精确位置=头注:5 [CONSUMERS] 运行时装配批（akshare 盈利预测→
  一致预期注入/c3 财务表实际 EPS 装配/CTR-002 桥接）——全仓无任何调用方构造
  EarningsEvent 注入实际数据＝纯算法壳在岗、零数据穿膛**。
- 负面否决器 negative_veto.py（MOD-SIG-137，挂 TDM-E-L3-04）：七项清单（业绩暴雷预告
  亏损/立案调查/减持/解禁>5%/商誉减值/配股/黑名单）＋high_accrual（:59-95），解禁阈值
  :39，裁决:98-113 不短路全披露。
- Sloan 产出件=fundamentals.py:245 accrual_negative_screen（已 production 在役）。
- 财务健康分无 Altman Z/O-score 现成件（最近似=应计因子族 fundamentals.py:99
  fq01_accrual）＝本域新增施工面。

### 4.3 接线面
- selection_funnel.py（MOD-SIG-086，域适配薄层 new）：BM-SEL-16 四排除（:68-71,242）→
  BM-SEL-17 五维初筛（:76-78,264）→BM-SEL-18 六要素精筛 Top50（:83-89,293），单调收敛
  不变量:8，委托 selection_funnel_skeleton.py；**待接线=头注:5（待 G08/G09/G10 sleeve
  接线）**。九阶段主链=TDM-E-L3-02（trading_map_03_e_l3_stock.md:107,151-155）；
  pool_tier_maintenance.py:5 自述"待接线"。
- 负面否决器 production（blueprint.md:7），下游已接 candidate_pool_aggregator.py:29,
  171-187（只标记不剔除，vetoed 沉底）——L3-04 消费面是全仓财报域唯一真实在役通道。

### 4.4 词表面
- news_dual_tagger.py:72-75：GAP_BEAT 超预期/GAP_MEET/GAP_MISS 低于预期/GAP_NO_ANCHOR
  封闭四态；:99 EVT-EARN-002 预告词（预增/预减/扭亏/首亏）。
- event_score.py:135-136,160-166：earnings surprise_direction＋SUE 变体。
- **SUE 五档枚举仅 pead_event_model 私有，GAP 四态在 news_dual_tagger 私有——无统一
  超预期事件流枚举件**＝词表面主病灶（三处变体待收敛唯一出口）。

## §5 六向台账（后两向）

### 5.5 判据面（看数前冻结预注册）
- PEAD 式事件研究：事件日分别取预告日/快报日/正式日三时点，各做信号后 20 日漂移
  （漂移度量沿用 pead_event_model :190-213 口径），市场模型超额收益；方向命中=SUE 档位
  符号与漂移符号一致率；SUE 五档分桶漂移单调性（方向与预注册一致）。
- 一致预期通道对照：random_walk_sigma 主算法 vs analyst_consensus 对照代理，分窗报告
  不混算；GAP_NO_ANCHOR 占比单列（预期缺失不伪装命中）。
- 健康分验收：A 股 ST 预测样本 3% 不平衡→用 AUC 不用 accuracy；Z/O-score 阈值分档
  与后续退市/ST 事件的区分度检验。
- 三时点增量性检验：后一阶段信号相对前一阶段的信息增量（不重复计功），预注册窗宽与
  门槛数值=看数前冻结呈批（同 10_chain C2 纪律）。

### 5.6 消费面
- 挂 selection_funnel L3-02：超预期事件流进五维初筛/六要素精筛（sleeve 接线后生效）。
- 挂负面否决器 L3-04：恶化事件（GAP_MISS 深档＋业绩暴雷预告亏损）与健康分低档进否决
  候选；沿用 candidate_pool_aggregator 只标记不剔除契约。
- 健康分供 pool_tier_maintenance 分层维护（其"待接线"状态解除后生效）。
- 条件轴联动：财报季窗（4/30、8/31、10/31 前伸 10 日）内事件密度→信息事件标注
  （不占 18 格，X2-B 先例）。

## §6 病灶诊断（自审闸输入）

| # | 病灶 | 定级 | 处置走向 |
|---|---|---|---|
| D1 | pead_event_model 装配批零调用：全仓无调用方构造 EarningsEvent 注入实际数据，纯算法壳零数据穿膛 | 阻断级 | P2 主施工：装配批落地（akshare 盈利预测→一致预期注入/c3 财务表实际 EPS 装配/CTR-002 桥接），头注:5 即施工图 |
| D2 | fund_analyst_forecast 不在 PIT 白名单，仅手工 SQL 消费；research_report 预测列禁 as-of | 阻断级 | P2：一致预期 PIT 合规化（补白名单＋版本去重）或降级为预告代理（与 C1 联动） |
| D3 | SUE 五档/GAP 四态/surprise_direction 三处枚举变体，无统一超预期事件流枚举件 | 缺口级 | P2：本域唯一出口产出统一枚举件，三处收敛引用 |
| D4 | 财务健康分缺件：无 Altman Z/O-score，仅 fq01_accrual＋accrual_negative_screen 应计雏形 | 缺口级 | P2 新增：Z/O-score＋Dechow F-score 自实现，应计件并轨复用 |
| D5 | selection_funnel 头注:5 待 G08/G09/G10 sleeve 接线；pool_tier_maintenance 自述待接线 | 缺口级 | P2：随主链 TDM-E-L3-02 接线批次挂接（跨域依赖登记） |
| D6 | 三时点事件日（预告/快报/正式）无显式字段贯通，季窗硬编码 4/30、8/31、10/31 | 收口级 | P2：预约披露日/实际公告日双字段化，替代硬编码季窗 |

## §7 待裁项（进 P1 总表）

| # | 项 | 选项 | 建议默认 |
|---|---|---|---|
| C1 | 一致预期 PIT 合规化 vs 降级为预告代理 | A 补 PIT 白名单＋版本去重；B 主用随机游走，预告作预期代理 | A＋B 并行：数据面合规化，算法面主用随机游走＋σ（A 股覆盖薄） |
| C2 | 事件研究窗宽/漂移门槛/AUC 门槛等判据数值 | 看数前冻结呈批 | 20 日漂移单窗起步＋五档分桶单调性（数值留 P2） |
| C3 | Altman Z 用 A 股修正系数还是原著系数（设计裁定，自行给默认） | A 原著制造业系数；B A 股修正系数（文献重估版） | B（A 股修正，原著系数对非制造业与 A 股制度失真；O-score 九变量照原著，阈值本土化） |
| C4 | 三时点增量信号 vs 仅正式财报单点 | A 三时点各自生成增量 SUE；B 仅正式财报 | A（制度强制预告=信息最早时点，放弃=白丢 20 日前置窗） |

## §8 车道回报存档

- 仓内四层盘点：本役车道回报（2026-10-13，全带 :行号/yaml: 锚点，照录于 §4/§5.6）
- 外部对标：SUE 两算法/华泰文本 PEAD/上交所制度/SSRN 2025/LSEG 开源件/ST 预测
  AUC 纪律/Sloan＋Dechow 自实现（URL 在案班账）

## §9 自审闸三态裁定（封矿）

- [x] 六向台账齐（数据/模块/接线/词表/判据/消费）
- [x] 病灶全部定级＋处置走向（6 条，含 2 阻断级）
- [x] 待裁项进 P1 总表（4 项，C2/C3 判据与设计默认已给）
- [x] 与 10_chain 同批纪律互引（判据看数前冻结=C2 同款；消费面 L3-04 同挂）
- 状态：**过闸·封矿**（判据数值留 P2 看数前冻结呈批＝纪律不违封矿；D1 装配批=本域
  P2 首刀）
