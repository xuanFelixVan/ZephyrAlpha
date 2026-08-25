---
blueprint_id: MOD-ALT-003
module_name: filing_nlp_engine
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
path: src/zephyr/alt_data/filing_nlp_engine.py
granularity: file
---

# MOD-ALT-003 filing_nlp_engine 蓝图（监管文件 NLP 引擎 / D-ALT-DATA-04）

> **module_id**: MOD-ALT-003 | **域**: D_ALT_DATA | **优先级**: P1
> **来源**: B10-02196（AUD-DRAFT-001-DIGEST P1 波 W-P1-15，§30.2.4）
> 代码：`src/zephyr/alt_data/filing_nlp_engine.py`

## 0. 定位

**A 股公告文本事件级 NLP**（D-ALT-DATA-04 §30.2.4，范围限 A 股公告，SEC 美股
剔除）：巨潮公告文本（消费 announcement_provider 采集产物）→ 事件类型分类
（业绩预告/业绩快报/减持/增持/定增/诉讼/问询函/处罚/分红/回购/其他，规则
关键词优先序）+ 影响评分 [-1,1]（规则词典；可选 llm_extractor 注入升级，
输出值域校验不合格回落规则并留痕）→ FilingEvent（extractor=rule|llm 留痕），
入事件表 sink 委托（装配批接线），供事件注入与基本面信号消费。

**撞名裁定（查重铁律②）**：W-P1-14 B1-00113（D-ALT-04 FilingNLPEngine）TSV
spec——公告采集+文本解析+事件类型分类（业绩预告/减持/定增/诉讼等）+影响评分
[-1,1]+LLM 抽取写事件库——与本模块实质全等。本波先建，**canonical =
MOD-ALT-003**；W-P1-14 到时按 REVIEW 归并本模块（如其先建成则以先建节点为
canonical 反向归并，以 depgraph 实证为准）。

查重分工（W-P1-15 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| announcement_provider | MOD-L00-004 | 巨潮/交易所公告**元数据采集**（落 fund_news_data） | 本模块消费其文本产物，不重复采集 |
| financial_parser | MOD-DAT-FIN-PARSER | 财报 PDF/XBRL→**数字指标**结构化（c3 财务表口径） | 解析粒度分工：数字指标 vs 文本事件；其 docstring 已预留"Filing NLP 复用 PDF 解析产物，互补不重复" |
| news_dual_tagger | MOD-NLP-DUALTAG-001 | 新闻可预测性+预期差双标签（前端新闻页） | 标签面不同（事件类型+影响分 vs 双标签） |
| api_llm_pool | MOD-INT-API-LLM-POOL | LLM provider 池化治理/计费 | LLM 能力经 llm_extractor 注入消费，零密钥零直连 |

不做什么：不采集公告（announcement_provider 职责）、不解析财报数字指标
（financial_parser 职责）、不直连 LLM（llm_extractor 注入委托 intelligence
族）、不写事件库（sink 委托）、不覆盖美股 SEC（spec 显式剔除）。

## 1. 判定规则（确定性，纯函数）

`classify(filings) -> ClassifyReport`：
- 单条校验（Fail-Closed 到条）：filing_id/symbol/title 非空、publish_time
  合法 → 非法条 rejected 留痕；
- 规则分类：内置 EVENT_KEYWORD_RULES（事件类型→关键词组，按优先序首中即定）；
  无命中 → event_type="其他"；
- 影响评分：规则词典（正/负向关键词权重求和 clip 到 [-1,1]，无命中=0.0），
  rule 路径 confidence=0.6；
- llm_extractor 注入时：llm_extractor(filing) → {event_type, impact_score,
  confidence}；输出结构/值域非法（类型未知/分越界/置信度越界）→ 回落规则
  路径并 llm_invalid 留痕；extractor 字段如实记录 rule|llm；
- events 按 (publish_time, filing_id) 排序输出（同输入必同输出）。

## 2. 接口

```python
EVENT_TYPES: Final = ("业绩预告","业绩快报","减持","增持","定增","诉讼","问询函","处罚","分红","回购","其他")
@dataclass(frozen=True) FilingInput: filing_id/symbol/title/text/publish_time
@dataclass(frozen=True) FilingEvent: event_id/symbol/publish_time/event_type/impact_score/
    confidence/extractor/source_id/summary
@dataclass(frozen=True) ClassifyReport: filings_in/accepted/rejected/events/rule_hits/
    llm_hits/llm_invalid/errors/sink_attempted/sink_ok
class FilingNlpEngine(llm_extractor=None, *, keyword_rules=None, sink=None):
    .classify(filings) / .classify_one(filing)
class InvalidFilingError / InvalidFilingNlpConfigError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO（llm_extractor/sink 全注入，单测不触网不触库）；
- 构造时 llm_extractor/sink 非 callable（非 None 时）/ keyword_rules 含未知
  事件类型 → InvalidFilingNlpConfigError（Fail-Closed）；
- 单条非法 Fail-Closed 到条（rejected 留痕）；影响评分恒 ∈ [-1,1]、置信度
  恒 ∈ [0,1]（clip 保证）；LLM 输出非法必回落规则并留痕，不出伪 LLM 结论；
- 仅信号输入语义，无下单含义；sink 可选、异常不阻断（sink_ok 如实记录）；
- frozen dataclass asdict JSON 可序列化；同输入必同输出。

## 4. 依赖

- MOD-ALT-002 web_scraper_engine（设计边：TSV 依赖前置 B10-02195，公告附件
  页面补抓面）
- MOD-L00-004 announcement_provider（设计边：采集产物消费面分工）
- MOD-DAT-FIN-PARSER financial_parser（设计边：数字指标解析粒度分工）
- MOD-NLP-DUALTAG-001 news_dual_tagger（设计边：新闻标签面分工）
- MOD-INT-API-LLM-POOL api_llm_pool（设计边：LLM 能力委托面）

## 5. 测试

`tests/alt_data/test_filing_nlp_engine.py`：规则分类（各事件类型命中/优先序/
无命中→其他）/ 影响评分（正向/负向/混合 clip/无命中=0）/ LLM 路径（合法输出
采纳/结构非法/分越界/置信度越界→回落规则留痕）/ 单条 Fail-Closed / 配置
Fail-Closed / sink 委托与异常不阻断 / 确定性排序 / frozen。
