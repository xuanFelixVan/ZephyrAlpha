---
blueprint_id: MOD-INT-NEWS-NIGHT
module_name: nightly_sentiment_window
domain: D_INTELLIGENCE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-INT-NEWS-NIGHT nightly_sentiment_window 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：92号清单 §8.4 M3-② + 44号备忘 §4 表 M3-② 行 + 26号备忘 §2.7 + tracker #138（情绪持久化表闭环，news_sentiment_window，DS-107）/#139。
> 代码：`src/zephyr/intelligence/nightly_sentiment_window.py`

## 0. 定位

夜间新闻情绪窗口聚合器——夜间窗口=前一交易日 18:00（含）→交易日 08:00（不含）左闭右开。复用 news_collector.collect_news（PIT 严格查询）读数、NewsSentimentAnalyzer（默认规则法；LLM 扩展口经 analyzer 注入）打分、可选注入 NewsSymbolLinker（#139）做标的关联，persist=True 时写 c1_market.news_sentiment_window（#138，DS-107）。

## 1. 接口

```python
def compute_nightly_sentiment(
    trade_date: str | datetime.date,
    *, analyzer: NewsSentimentAnalyzer | None = None,
    linker: NewsSymbolLinker | None = None,      # 可选注入；未注入 linked 统计恒 0
    persist: bool = False,                        # 默认关；True=写 news_sentiment_window
    writer: Callable[[Any], bool] | None = None,  # 写表器可注入（测试 mock）
    top_n: int = 5,                               # top_events_json 头部事件条数（按 |polarity| 降序）
) -> NightlySentimentResult
```

## 2. 输出契约

`NightlySentimentResult`（frozen dataclass，JSON 可序列化）：date（交易日=窗口归属日）/window_start/window_end + sentiment_index（夜间窗口综合情绪指数 [-1,1]=窗口平均极性，与 SentimentAggregator 口径一致）+ avg_polarity + positive/negative/neutral_count + total_count（news_id 去重后窗口新闻条数）+ top_events + linked_symbol_count/ambiguous_count/market_count（#139 关联覆盖统计）+ degraded（无新闻/读取异常；sentiment_index 按 0.0 中性处理）+ persisted/reasons 留痕。

- `to_dict()` 含 **plan004_input 对接预留字段**（news_sentiment/news_total/degraded）——MOD-PLAN-004 overnight_boundary_reviser 当前无 news_sentiment 入参（实证 compute(trade_date, bs005_triggered=False)），消费接线由统筹后续波次裁定，**本模块不改 MOD-PLAN-004**
- 落库：ReplacingMergeTree 同键（scope, symbol, window_type, window_ts）替换→重跑幂等；写表列序=DDL-as-Code 真源 schemas/categories/market_news_sentiment_window.py INSERT_COLUMNS
- news_data 为 SCD 多版本表按 news_id 去重（keep first=最早版本 PIT 语义）

## 3. 不变量（头注 INVARIANTS 原文）

- 夜间窗口=前一交易日18:00(含)→交易日08:00(不含)左闭右开
- sentiment_index=窗口平均极性（与 SentimentAggregator 口径一致）
- news_data 为 SCD 多版本表按 news_id 去重（keep first=最早版本 PIT 语义）
- 空窗口→total_count=0+degraded=True 不抛
- persist 默认关，写表经 ReplacingMergeTree(scope,symbol,window_type,window_ts) 同键替换幂等
- 情绪分数作事件信号维度非独立 alpha（26号备忘 §2.7 裁定）

## 4. 降级行为

- ERROR_CONTRACT：NightlySentimentError（ZA-IT-0008）——仅 trade_date 非法时抛 ValueError（契约违反 fail-closed）；CH 查询/写表异常走降级（degraded/persisted=False+reasons 留痕）不抛

## 5. 边界（不做）

- 消费接线待统筹裁定（MOD-PLAN-004 零改动）；business_data_categories.yaml 品类补登为统筹后续项（暂用常量表名，与 overnight_boundary_reviser fallback 同约定）
- 不做标的关联本身（NewsSymbolLinker 职责，可选注入）

## 6. 测试

tests/intelligence/test_nightly_sentiment_window.py
