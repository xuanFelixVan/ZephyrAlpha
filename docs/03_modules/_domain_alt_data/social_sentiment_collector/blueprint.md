---
blueprint_id: MOD-ALT-001
module_name: social_sentiment_collector
domain: D_ALT_DATA
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_ALT_DATA
path: src/zephyr/alt_data/social_sentiment_collector.py
granularity: file
---

# MOD-ALT-001 social_sentiment_collector 蓝图（社媒情绪采集器 / B10-01341）

> **module_id**: MOD-ALT-001 | **域**: D_ALT_DATA | **优先级**: P1
> **来源**: B10-01341（AUD-DRAFT-001-DIGEST P1 波 W-P1-15，A1 §2.1）
> 代码：`src/zephyr/alt_data/social_sentiment_collector.py`

## 0. 定位

**帖子级社媒情绪日频采集器**：股吧/雪球等社媒帖子（fetcher 注入）→ 标准化
SocialPost → 情感打分（scorer 注入委托，运行时接 news_sentiment_analyzer /
nlp_inference / LLM 池）→ 按 (trade_date, symbol) 日频聚合（均值/ engagement
加权/正压比）→ SocialSentimentDaily 行，落账经 sink 委托（装配批接 ch_writer
落 ClickHouse），供 C-014 大盘预测与筛选漏斗情绪面消费。

三条"另类数据源"查重裁定（W-P1-15，细读三份 TSV spec）：B10-01341 为 canonical
（唯一给出可施工最小形态：股吧/雪球人气日频采集器落 CH 接情绪管道）；
B10-01842（§29.12 扩展框架）①社媒情绪面与本模块全等 → REVIEW 归并，残留面
（②数字足迹招聘/专利、③产业链工商司法海关可选付费 API、④卫星接口位）留后续批；
B13-04069（A3 情绪面板族）→ REVIEW 归并（详 fragment）。

查重分工（W-P1-15 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| akshare_provider stock_hot_rank | MOD-L00-004 | 东财人气/关注**数值榜单**日快照（已接线 tasks.yaml） | 本模块做**帖子级文本情绪**，非数值人气榜 |
| news_sentiment_analyzer | MOD-INT-AISA | 新闻情感打分+窗口聚合 | 本模块 scorer 注入委托其/LLM 能力，不内嵌打分引擎 |
| llm_market_interpreter | MOD-INT-MKT-INTERPRETER | 新闻/研报/社媒三路统一解读 | 下游消费面，本模块只产日频聚合行 |
| ch_writer | MOD-L00-004 | ClickHouse 写入 | 落账 sink 委托，不 import |

不做什么：不直连网络（fetcher 注入）、不内嵌 LLM/规则情感打分引擎（scorer
注入）、不写 ClickHouse（sink 委托）、不做数值人气榜（stock_hot_rank 已有）、
不做三路统一解读（MOD-INT-MKT-INTERPRETER 职责）。

## 1. 判定规则（确定性，纯函数）

`collect(trade_date, symbols) -> CollectReport`：
- trade_date 须 `YYYY-MM-DD`；symbols 非空且元素非空 → 否则 ValueError；
- fetcher(trade_date, symbols) 取原始帖（dict 或 SocialPost）；fetcher 异常
  → errors 留痕、按空批处理（不阻断）；
- 单帖校验（Fail-Closed 到条）：post_id/symbol/text 非空、publish_time 合法
  且不晚于 trade_date 23:59:59（PIT 不采未来帖）→ 非法条 rejected 留痕；
- scorer(text) → polarity ∈ [-1,1]；scorer 异常/越界/NaN → 该条 unscored
  留痕（计入 post_count 不入聚合）；
- 聚合（按 symbol）：sentiment_mean=均值 polarity；
  engagement_weighted_mean=Σ(p·w)/Σw，w=1+likes+comments+reads；
  positive_ratio=scored 中 polarity>0 占比；sources=去重排序来源元组；
- dailies 按 symbol 排序输出（同输入必同输出）。

## 2. 接口

```python
@dataclass(frozen=True) SocialPost: post_id/symbol/publish_time/text/source/likes/comments/reads
@dataclass(frozen=True) SocialSentimentDaily: trade_date/symbol/post_count/scored_count/
    sentiment_mean/engagement_weighted_mean/positive_ratio/sources
@dataclass(frozen=True) CollectReport: trade_date/fetched/accepted/rejected/unscored/
    dailies/errors/sink_attempted/sink_ok
class SocialSentimentCollector(fetcher, scorer, sink=None, *, max_posts=20000):
class InvalidSocialPostError / InvalidCollectorConfigError(ZephyrBaseError)
```

## 3. 不变量

- collect 判定纯函数无 IO（fetcher/scorer/sink 全注入，单测不触网不触库）；
- 构造时 fetcher/scorer 非 callable → InvalidCollectorConfigError（Fail-Closed）；
- 单帖非法 Fail-Closed 到条（rejected 留痕，脏数据不进聚合）；PIT 严格；
- scorer 输出必须落在 [-1,1]，越界/NaN/异常 → unscored 留痕不出伪情感分；
- sink 可选；sink 异常 → errors 留痕不阻断（sink_ok 如实记录）；
- frozen dataclass asdict JSON 可序列化；同输入必同输出。

## 4. 依赖

- MOD-L00-004 akshare_provider（设计边：数值人气榜分工对齐）
- MOD-INT-AISA news_sentiment_analyzer（设计边：情感打分管道委托面）
- MOD-INT-MKT-INTERPRETER llm_market_interpreter（设计边：下游解读面分工）
- MOD-L00-004 ch_writer（设计边：落账委托面）

## 5. 测试

`tests/alt_data/test_social_sentiment_collector.py`：聚合（均值/engagement 加权/
正压比/多标的/多来源去重）/ PIT（未来帖拒收）/ 单帖 Fail-Closed（空 id/空
symbol/空文本/坏时间）/ scorer（越界/NaN/异常→unscored）/ fetcher 异常容错 /
配置 Fail-Closed / sink 委托与异常不阻断 / 确定性排序 / frozen。
