---
ttl: task_bound
title: 深度审查作业簿——新闻情绪语义分析（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：新闻情绪语义分析（P07）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/intelligence/news_sentiment_analyzer.py`
- TDM 节点: TDM-E-L1-S0-1
- 生产调用方: nightly_sentiment_window.py（经 data/scheduler.py + scripts/data/run_nightly_sentiment.py 挂调度）、chain_impact_stream.py（RuleBasedSentimentScorer=L1-S0-1 上游）——**活件**
- 测试文件: tests/intelligence/test_news_sentiment_analyzer.py（实跑通过）

## 1 对象快照
MOD-INT-AISA 全文件（615 行）：规则法情绪打分（正负词典+反转语境+ST 词边界）+LLM 扩展口+1h 窗口聚合+事件检出+persist 钩子。GLM 复审修复批产物（polarity/score 语义防线已内建）。排除项：news_collector/nlp_inference/nightly_sentiment_window 内部。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 规则打分工程扎实：反转短语先扣除再匹配（防"终止重组"计正向）、ST 大小写敏感词边界（防 steady 误伤）、同词去重、±0.90 封顶 | :192-215,220-227,240-279 | 已查无 | "终止重大资产重组"应得负向非 +0.20 |
| A 深度 | **LLM 断供静默中性（checklist #6 直接命中）**：llm_scorer 异常→polarity=0.0+method="llm_fallback" 不抛——LLM 挂掉时全部新闻静默判中性→窗口指数趋 0→事件检出自愈式失明；method 列有留痕但事件链无人检查方法占比 | :426-439 | **P2** | 注入恒抛异常的 llm_scorer 跑 analyze_date_range，观察 windows 全 0 无告警 |
| A 深度 | **跨空窗防抖漏报**：_detect_events 防抖只比"前一非空窗口"；两窗口间隔数小时（中间无新闻空窗被跳过）时，后一真新 spike 被陈旧前窗抑制漏报 | :570-599,341-361 | **P2** | 造 10:00 窗 0.5 与 14:00 窗 0.4（阈值 0.3）两窗口，第二事件不触发 |
| A 边界 | 空输入返回空不报错（契约明示）；缺列报错；NaN 时间/极性行 drop | :321-333,417-418 | 已查无 | 空 df/缺列各测 |
| B 上游 | collect_news `ORDER BY publish_time`（news_collector.py:124）支撑 merge keep="first" 的 PIT 最早版本语义——契约成立且已文档化（SCD 多版本去重） | :482-487 | 已查无 | 改排序复跑窗口 count |
| C 下游 | 消费方实存三处（见头）；爆炸半径=情绪事件维度失真（26号裁定：情绪分作事件信号维度非独立 alpha——半径受限）；llm_fallback 静默会沿 nightly/chain_impact 传播 | scheduler.py/run_nightly_sentiment.py 挂载 | 已查无 | grep 消费方复跑 |
| D 旁系 | sentiment_index=窗口均极性口径与 nightly_sentiment_window 一致（两侧同式）；与 sentiment_engine 分工零交集（docstring :30） | :358 vs nightly_sentiment_window.py:8 | 已查无 | 对读两实现 |
| E 对抗 | 五问：①persist 异常降级不抛（fail-open 有 reason，钩子默认关——可接受）②llm_fallback=假阳性过关面（见 A-2）③无心跳（调度层职责）④persist ReplacingMergeTree 同键替换幂等 ⑤naive datetime 假设（CH 返回 naive，契约内） | :560-564,504 | P3 | 复跑 persist 两遍对表 |
| F 新鲜度 | **受阻**：FinBERT/中文金融情绪 LLM vs 词典法对比检索遭限流（429），如实记受阻；词典法为本件 MVP 定位（LLM 走注入扩展口），架构上已预留升级路径 | — | — | — |

## 3 SOTA 对照
受阻（限流）。架构判断（非断言）：词典规则 MVP+LLM 注入口与业界常见演进路径一致，待检索解禁后补来源。

## 4 缺陷清单
1. **P2 LLM 断供静默中性**：建议 analyze_date_range 聚合侧对 method 分布设下限（如 llm_fallback 占比>50% 记 degraded 事件/日志 ERROR）。验证法：见轴 A。
2. **P2 跨空窗防抖漏报**：建议防抖改为"距上一触发窗口时长>window×k 才抑制"。验证法：见轴 A。
3. P3 SentimentEvent.symbols 恒空（docstring 称"MVP 从标题提取"未实现——文档先行）。
4. P3 persist 行 pos_n/neg_n 由 4dp 舍入 ratio 反推，极端计数可差 1（neutral_count 吸收，无害）。

## 5 挂起疑问
- 阈值 ±0.30 与窗口 1h 的标定依据未见登记（词典法极性量纲非概率，0.30 的经验含义需 Owner 背书）。

## 6 完备性自评
六轴全查。长尾：词典收词完备性未逐词审（33+35 词，抽核未见互为子串对）；nightly_sentiment_window 内部未审（独立对象）。
