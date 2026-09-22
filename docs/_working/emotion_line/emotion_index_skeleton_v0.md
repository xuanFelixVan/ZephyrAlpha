---
ttl: task_bound
title: emotion_index 骨架设计稿 v0——最小聚合版蓝图
created: 2026-09-22
sid: st-emomine-20260922
lane: emotion_line
status: draft（交下轮施工讨论，未开工）
doc_version: v0.2（auction 修正+存量模块关系）
---

# emotion_index 骨架设计稿 v0（最小聚合版）

> 定位：**独立状态变量**——今日场内温度计（0=冰点 1=沸点），与"大盘明日走势判断"是两个变量；
> 与板块层互为上下游：本线产出 emotion_index 供板块线消费，板块热度不回灌本指数（防循环）。
> 本稿只设计不施工。**禁采任何新数据**：输入表全部为仓内已有表（内部盘点册 §1 四态表为准）。
> 契约基准=总包 §2 接口契约 v0.1（Max 定，只读引用）。

## §1 输入表清单（全部已落库，零新采集）

| 成分 | 输入表 | 盘点册状态 | 近端新鲜度 |
|------|--------|-----------|-----------|
| C1 涨停温度 | c1_market.daban_board_event | 断（09-15） | 断供修复后 T 日盘后 |
| C2 晋级率 | c1_market.daban_board_event（T-1 连板股 × T 再连板，JOIN） | 断（同上） | T 日盘后 |
| C3 广度 | c1_market.kline_daily + kline_index | 通 | T 日盘后 |
| C4 量能 | c1_market.kline_daily（amount/turnover） | 通 | T 日盘后 |
| C5 杠杆 | c1_market.margin_trading | 半通（滞后 1-2 日） | as-of 最近可得日 |
| C6 新闻 | c1_market.news_sentiment_window（scope=market） | 半通（rule 法单窗） | T 日 08:00 夜间窗 |
| （v0.2 挂载位）PCR | c1_market.option_* 原料（衍生在建，小红书班第 3 件） | 半通 | 互依赖勿施工 |
| （v0.2 挂载位）画像 | c1_backtest.cohort_daily_ledger | 缺件（表未建） | cohort 班落地后 |

明确**不进**输入面：c1_market.sentiment_panel 的 fear_greed_index（币圈异轴，禁顶替——t0 判例
红线）；market_breadth_snapshot（139 行极浅，不依赖）。

## §2 成分计算口径（v0 六成分）

统一预处理：每成分先算原始值 raw_value，再对**滚动 250 交易日窗**取截面分位 percentile∈[0,1]
（历史不足 120 观测的成分如实降档：percentile 置空+weight 重分配+version 升级，禁硬凑）。

- **C1 涨停温度** = 0.4×P(涨停家数) + 0.3×P(最高连板高度) + 0.3×P(1−炸板率)。
  涨停家数=当日触板事件数；最高连板=max(consec_limit)；炸板率=开板事件数/触板事件数。
  真源 daban_board_event（事件含触板/封住/一字/首触/开板次数/封单代理/连板七要素）。
- **C2 晋级率** = P( 晋级率 )；晋级率 = {T-1 日连板高度≥1 且 T 日再涨停的股票数} ÷ {T-1 日
  连板高度≥1 的股票数}。纯 daban_board_event 自 JOIN，无外部依赖。
- **C3 广度** = 0.6×P(上涨家数占比) + 0.4×P(当日 000300 涨幅)。
  上涨占比=pct_change>0 家数/有成交家数（kline_daily）；大盘涨幅=kline_index 000300。
- **C4 量能** = 0.5×P(两市成交额合计) + 0.5×P(换手率中位数)。原料=kline_daily.amount /
  turnover（实测列在；勿引 stock_indicator——实测无换手列）。
- **C5 杠杆** = P(两融余额 20 日变化率)；as-of 对齐：T 日聚合用 ≤T 的最近可得日（现状滞后
  1-2 交易日），components 明细中 raw_value 附 data_ts 供下游审计滞后。
- **C6 新闻** = P(市场新闻情绪 5 日均值)；原料=news_sentiment_window scope='market' 的
  sentiment_index（[-1,1]→百分位），当前打分全 rule 法——成分卡如实标注"规则法"。

## §3 加权与合成

- **v0 = 等权**：emotion_index = Σ w_i × percentile_i，w_i=1/6（降档成分按剩余重分配）。
- 二期选项（考试通过后才启用，见考试卡草案卡B）：IC 加权（用成分对 T+1 大盘 RankIC 滚动
  均值作权）。
- **首版禁 PCA**：六成分历史起点不齐（daban 09-01 起、两融 07-20 起、新闻窗 02-25 起），
  主成分载荷不稳；PCA 留成分历史≥1 年后再评估。
- 输出灰度语义分档（仅展示层约定，非门禁）：≤0.2 冰点 / 0.2-0.4 降温 / 0.4-0.6 温和 /
  0.6-0.8 升温 / ≥0.8 沸点。

## §4 stage 时点与更新时点（契约 stage 四态落地）

| stage | 触发时点 | 聚合内容 | v0 状态 |
|-------|---------|---------|---------|
| close_final | T 日 15:10 盘后 | C1-C6 全量（T 收盘态），**真源/定格态** | v0 实现 |
| pre_open | T+1 日 09:15 | =T 日 close_final 态 + 隔夜新闻窗（08:00 出）+两融 as-of 更新 | v0 实现 |
| auction | T 日 09:25 | 竞价快照成分（预留：竞价成交/缺口原料未聚合） | 预留 |
| intraday_vN | T 日盘中滚动 | 盘中宽度/量能滚动（预留：宽度快照表现不达标） | 预留 |

**时戳纪律**（契约红线）：同一 ts 内成分之间禁循环依赖（板块热度不进本指数）；**T 日收盘态=
T+1 盘前输入**——pre_open 只重算新闻/两融两个滞后成分，其余沿用 close_final 值并在 components
内标注 source_stage=close_final。

## §5 输出契约与落库表草案

契约形态（总包 §2 v0.1，逐字段落实）：

```
emotion_index: float 0-1 灰度分位
ts: DateTime64(3) 显式时区（Asia/Shanghai）
stage: pre_open | auction | intraday_vN | close_final
components: [{name, raw_value, percentile, weight}]（六成分明细必带，缺供成分带 status 标注）
version: 语义化版本（成分集或权重变更=升版本，禁原地改）
```

落库表草案（DDL 真源模式= schemas/categories/market/ 下新文件，走 apply_market_tables_ddl）：

```sql
CREATE TABLE IF NOT EXISTS c1_market.emotion_index
(
    trade_date    Date                        COMMENT '交易日',
    stage         LowCardinality(String)      COMMENT 'pre_open/auction/intraday_vN/close_final',
    ts            DateTime64(3, 'Asia/Shanghai') COMMENT '状态时戳（收盘态=15:10，盘前=09:15）',
    emotion_index Float64                     COMMENT '0-1 灰度分位',
    components    String                      COMMENT 'JSON 数组 [{name,raw_value,percentile,weight,status}]',
    version       LowCardinality(String)      COMMENT '语义化版本，成分/权重变更必须升版',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stage)
```

（DateTime64(3)+显式时区合规；ReplacingMergeTree 同键幂等重跑安全；具体 DDL 以施工班
schema-as-code 流程为准，本稿只定形态。）

## §6 版本纪律

- v0.1.0：六成分等权（C1/C2 待 daban 复通后实际产出；C5 两融现状约 40 个观测，低于 §2 的
  120 观测门槛，待补史达标。此前 C1/C2/C5 置 status=insufficient、权重重分配至其余成分，
  version 不变、components 内如实标注）。
- 成分集变更（+PCR/+画像/砍成分）=升 minor；权重方案变更（等权→IC 加权）=升 major。
- 每行 components JSON 内保留逐成分 status（ok/insufficient/missing），下游可机械过滤。

## §7 不做什么（硬边界重申）

1. 不采任何新外部数据（总包 §0：只聚合已有因子）。
2. 不用 fear_greed 异轴顶替任何 A 股情绪成分（t0 判例红线）。
3. 不施工 PCR（小红书班第 3 件在建）与 cohort 画像（cohort 班写域）——只留挂载位。
4. 不动板块线写域；板块热度不回灌（防同 ts 循环依赖）。
5. 本稿=讨论稿，施工须另走 construction_workflow_policy 十五步闭环+depgraph 登记。

## §8 补遗：与存量情绪模块的关系（挖干补遗轮新增，施工前置判定项）

> 本节为 Owner"挖干了吗"质询后补干所得，**修正 §4 auction stage 的错判**并登记查重风险。

### 8.1 错判修正

§4 auction stage 原标"竞价快照成分（原料未聚合）"——**错**。实证：`c1_market.auction_snapshot`
（266,361 行→09-22，10 秒级）与 `c1_market.auction_book`（3,029,801 行→09-22，3 秒高频层）
原料**通**。修订：auction 从"预留"升为"**v0.2 可挂载（原料齐备）**"；v0 范围不变
（close_final/pre_open 先行，避免首批施工面过大）。

### 8.2 存量情绪资产地图（同域簇）

| 存量件 | 形态 | 与本线关系 |
|--------|------|-----------|
| `signal_ashare.sentiment.sentiment_cycle`（8 标准函数，production） | 五阶段分类器（冰点/反核/主升/疯狂/退潮）+ **compute_sentiment_temperature** + regime 映射 + 策略部署矩阵 | **查重最高风险**：温度函数与 emotion_index 概念直接同名 |
| `market_sentiment_analyzer.SentimentPhase` | 4+1 硬标签枚举 | 同域第三枚举，待内收判定 |
| `youzi_relay_emotion_engine.EmotionPhase` | 游资接力情绪枚举 | 同域第三枚举，待内收判定 |
| F23_LIMITUP_EMOTION（alt_regime_signals，阈值 v1 provisional） | 涨停家数/连板高度/晋级率→**阶段**（分类） | 输入与 C1/C2 同源；"档位计 vs 温度计"关系须显式判定 |
| F15/F25（alt_regime_signals） | 恐贪极值/转债溢价分位（连续） | F25 与 C 系成分思路同源（转债溢价未入 v0 六成分，留 v0.2 评估） |

### 8.3 内收判定框架（施工班开工前必做，交 Owner/Max）

差异化定位初判（待批）：emotion_index=**连续 0-1 灰度分位+契约化 components 明细+多源聚合+
四 stage 时点**，消费方是排班/仓位节流；sentiment_cycle=**离散五阶段+策略纪律/部署映射**，
消费方是策略条件化。两者可并存但须：①共用同一成分计算内核（禁两套涨停家数/晋级率口径）；
②temperature 与 phase 建立显式映射（同一输入一次计算，双向派生）；③三枚举收敛时间表。
若 Owner 判"必并"，则本骨架稿降级为 sentiment_cycle 的数据底座扩展。

### 8.4 替代源备注

daban 断供期 C1 的涨停家数子项（0.4 权重）可由 c1_market.limit_up_down（→09-22 通）替代；
连板高度/炸板率/晋级率无替代（limit_type 无连板链），仍待 daban 周窗复通。
