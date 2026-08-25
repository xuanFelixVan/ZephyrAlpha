---
blueprint_id: MOD-ALT-002
module_name: web_scraper_engine
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
path: src/zephyr/alt_data/web_scraper_engine.py
granularity: file
---

# MOD-ALT-002 web_scraper_engine 蓝图（网页爬取引擎 / D-ALT-DATA-03）

> **module_id**: MOD-ALT-002 | **域**: D_ALT_DATA | **优先级**: P1
> **来源**: B10-02195（AUD-DRAFT-001-DIGEST P1 波 W-P1-15，§30.2.4）
> 代码：`src/zephyr/alt_data/web_scraper_engine.py`

## 0. 定位

**无 API 页面定向爬取通用核心**（D-ALT-DATA-03 §30.2.4）：目标登记（URL/域名/
提取器/限速）→ 合规限速判定（按域名最小间隔台账，纯函数）→ fetcher 注入抓取
→ 规则提取器（html→结构化记录，纯函数注册表）→ 去重（批内内容哈希内置 +
seen 注入委托 news_dedup 窗口口径）→ ScrapedRecord 行，落账 sink 委托（装配批
接 ch_writer 落 ClickHouse），调度面挂 D_DATA scheduler（装配批接线）。

查重铁律④分工（W-P1-15 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| rss_provider / eastmoney_news_provider / cls_provider / announcement_provider | MOD-L00-004 | **API/RSS 结构化源** source-specific provider（IngestProviderBase 模式） | 本模块承接**无 API 页面**（雪球热帖页/股吧列表页等）定向爬取，不复制具体源逻辑 |
| news_collector | MOD-DATA-NEWS-001 | 库内新闻查询（读 fund_news_data） | 读取面，非采集 |
| news_dedup | MOD-L00-004 | 标题哈希去重（库窗口+批内） | 去重 seen 注入委托，不复制窗口查询 |
| scheduler | MOD-L00-004 | ETL 调度与依赖管理 | 调度挂载面，本模块不含调度 |

不做什么：不直连网络（fetcher 注入）、不实现具体源 provider（东财/财联社/RSS
已有）、不内嵌调度（scheduler 已有）、不写 ClickHouse（sink 委托）、不爬
允许清单外域名（allowed_domains 配置 Fail-Closed）。

## 1. 判定规则（确定性，纯函数）

`register_target(target)`：target_id/url/domain 非空、min_interval_seconds ≥ 0、
extractor 已注册、domain ∈ allowed_domains（若配置）→ 否则 Fail-Closed；
target_id 重复 → Fail-Closed。

`can_fetch(target_id, now) -> bool`：纯函数读内存台账——
`now - last_fetch[domain] >= min_interval_seconds`（首次恒 True）。

`scrape(now, target_ids=None) -> ScrapeReport`：
- 逐目标：can_fetch False → skipped_throttle 留痕跳过；
- fetcher(url) → html/text；异常 → errors 留痕继续下一目标（单目标失败不阻断）；
  成功才更新 last_fetch[domain]=now；
- extractor(content) → 记录迭代；单条校验（record_id/title 非空）→ 非法条
  invalid 留痕；每目标截断 max_records_per_target；
- 批内去重：MD5(title+content) 批内集合 + seen(hash) 注入（seen 异常 →
  fail-open 保留并留痕，对齐 news_dedup fail-open 惯例）；
- records 按 (target_id, record_id) 排序输出；sink 可选、异常不阻断。

## 2. 接口

```python
@dataclass(frozen=True) ScrapeTarget: target_id/url/domain/extractor/min_interval_seconds=3600
@dataclass(frozen=True) ScrapedRecord: target_id/record_id/title/content/publish_time/url/content_hash
@dataclass(frozen=True) ScrapeReport: targets_visited/fetched/extracted/invalid/dedup_dropped/
    skipped_throttle/records/errors/sink_attempted/sink_ok
class WebScraperEngine(fetcher, *, extractors=None, seen=None, sink=None,
                       allowed_domains=None, max_records_per_target=200):
    .register_target(target) / .can_fetch(target_id, now) / .scrape(now, target_ids=None)
class InvalidScrapeTargetError / UnknownExtractorError / InvalidScraperConfigError(ZephyrBaseError)
```

内置提取器：`html_text`（去标签+空白规整，产单条 record_id=内容哈希的文本记录）；
自定义提取器经 extractors=dict 注入（name → callable(content) -> iterable）。

## 3. 不变量

- 判定核心纯内存无 IO（fetcher/seen/sink 全注入，单测不触网不触库）；
- 构造时 fetcher 非 callable / extractors 含非 callable → InvalidScraperConfigError；
- 目标非法/重复/未知提取器/域外 → 登记期 Fail-Closed；
- 限速判定纯函数，仅抓取成功才更新台账（失败不占用配额窗口）；
- 单目标异常不阻断批次；去重 seen 异常 fail-open 留痕（不静默丢记录）；
- frozen dataclass asdict JSON 可序列化；同输入必同输出。

## 4. 依赖

- MOD-L00-004 news_dedup（设计边：去重口径委托对齐）
- MOD-L00-004 ch_writer（设计边：落账委托面）
- MOD-L00-004 scheduler（设计边：调度挂载面，TSV 依赖前置"已有"）
- MOD-L00-004 rss_provider（设计边：API/RSS 源族分工对齐）

## 5. 测试

`tests/alt_data/test_web_scraper_engine.py`：登记校验（非法/重复/未知提取器/
域外）/ 限速（首抓恒通/间隔内跳过/失败不更新台账/按域名独立）/ 抓取异常容错 /
提取（内置 html_text/自定义注入/单条非法/截断）/ 去重（批内/seen 命中/seen
异常 fail-open）/ sink 委托与异常不阻断 / 确定性排序 / frozen。
