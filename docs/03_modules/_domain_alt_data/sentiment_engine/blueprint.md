---
blueprint_id: MOD-ALT-004
module_name: sentiment_engine
domain: D_ALT_DATA
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_ALT_DATA
path: src/zephyr/alt_data/sentiment_engine.py
granularity: file
---

# MOD-ALT-004 sentiment_engine 蓝图（统一情绪引擎 / D-ALT-02）

> **module_id**: MOD-ALT-004 | **域**: D_ALT_DATA | **优先级**: P1
> **来源**: B1-00112（AUD-DRAFT-001-DIGEST P1 波 W-P1-14，§功能域模块·D-ALT-DATA）
> 代码：`src/zephyr/alt_data/sentiment_engine.py`

## 0. 定位

**统一情绪聚合判定引擎**：聚合价量情绪（复用 sentiment_cycle 产出口径）+
社媒/新闻情感分（采集/打分面产物注入）→ 复合情绪分 → 252 日滚动历史分位数
→ 冰点（<10 分位）/过热（>90 分位）统一判定，输出入 C-014 大盘预测与筛选
漏斗。仅信号输入语义，无下单含义。

查重分工（W-P1-14 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| sentiment_cycle | （signal_ashare） | **价量**情绪五阶段周期定位（相位+纪律） | 价量情绪为其产出面；本件跨源聚合+历史分位判定 |
| social_sentiment_collector | MOD-ALT-001 | 帖子级社媒文本**采集**+日频聚合行 | 采集面；本件消费其日频聚合分 |
| news_sentiment_analyzer | MOD-INT-AISA | 新闻情感**打分**（单条/双模） | 打分面；本件消费其分数不内嵌打分 |
| sentiment_aggregator | MOD-NLP-AGGREGATOR-001 | 跨**新闻源**一致性投票（≥2 源同向） | 新闻源间投票；本件跨**类别**（价量/社媒/新闻）聚合+分位判定 |
| extreme_sentiment_reversal_detector | MOD-SIG-099 | 极端情绪**反转事件检测**（双冰点配对/Capitulation） | 事件检测器；本件为状态分位判定引擎，粒度和职责正交 |

不做什么：不采集（MOD-ALT-001 职责）、不做单条文本打分（intelligence 族
职责）、不做反转事件检测（MOD-SIG-099 职责）、不接 LLM/不触网不触库
（全部输入注入）。

## 1. 判定规则（确定性，纯函数）

`evaluate(rows) -> SentimentEngineReport`：
- 输入行 `SentimentInput(trade_date, symbol, price_volume_score, social_score,
  news_score)`：各路分 ∈ [-1,1]，缺失路按 None 不计（至少一路非 None，否则
  该行 rejected 留痕）；
- 复合分 composite = 加权均值（weights 配置，默认价量 0.4/社媒 0.3/新闻 0.3；
  缺失路权重按在场路归一化），clip [-1,1]；
- 历史分位：同 symbol 历史窗（window_days=252 个交易日口径，取
  trade_date 之前 PIT 严格 < 当日的 composite 序列）中 ≤ 当日 composite 的
  占比 → percentile ∈ [0,1]；历史样本 < min_history（默认 20）→ 该日
  state=INSUFFICIENT_HISTORY，不出冰点/过热判定；
- 状态机：percentile < 0.10 → ICE（冰点）；> 0.90 → OVERHEAT（过热）；
  其余 NORMAL；恰等阈值不命中（严格小于/大于）；
- 输出 SentimentDaily(trade_date/symbol/composite/percentile/state/
  components_present)；records 按 (trade_date, symbol) 排序（确定性）。

## 2. 接口

```python
SentimentState: Final = Enum {ICE, NORMAL, OVERHEAT, INSUFFICIENT_HISTORY}
@dataclass(frozen=True) SentimentInput: trade_date/symbol/price_volume_score/
    social_score/news_score（Optional，越界→Fail-Closed 到条）
@dataclass(frozen=True) SentimentDaily: trade_date/symbol/composite/percentile/
    state/components_present
@dataclass(frozen=True) SentimentEngineReport: rows_in/accepted/rejected/records/
    ice_count/overheat_count
class SentimentEngine(config=None):
    .evaluate(rows) / .evaluate_one(symbol, trade_date, scores..., history)
class SentimentEngineConfig: weights/window_days=252/min_history=20/
    ice_pct=0.10/overheat_pct=0.90
class InvalidSentimentInputError / InvalidSentimentConfigError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO（历史序列由调用方注入，PIT 严格 < 当日）；
- 分越界/日期非法/symbol 空白 → 单条 rejected 留痕（Fail-Closed 到条）；
  配置非法（权重负/窗口非正/阈值越界/ice≥overheat）→ 构造期 Fail-Closed；
- composite 恒 ∈ [-1,1]、percentile 恒 ∈ [0,1]（clip 保证）；
- 阈值严格小于/大于（恰等 0.10/0.90 不命中 ICE/OVERHEAT）；
- 样本不足 → INSUFFICIENT_HISTORY 不出伪判定；
- frozen dataclass asdict JSON 可序列化；同输入必同输出；仅信号输入语义。

## 4. 依赖

- MOD-ALT-001 social_sentiment_collector（设计边：社媒日频聚合分来源面）
- MOD-INT-AISA news_sentiment_analyzer（设计边：新闻情感分来源面）
- MOD-NLP-AGGREGATOR-001 sentiment_aggregator（设计边：跨新闻源投票分工）
- MOD-SIG-099 extreme_sentiment_reversal_detector（设计边：反转事件检测分工）

## 5. 测试

`tests/alt_data/test_sentiment_engine.py`：复合分（三路/缺路归一/clip）、
历史分位（PIT 严格 < 当日/边界占比）、状态机（ICE<0.10/OVERHEAT>0.90/恰等
不命中/样本不足）、单条 Fail-Closed、配置 Fail-Closed、确定性排序、frozen。
