---
blueprint_id: MOD-INT-MKT-INTERPRETER
module_name: llm_market_interpreter
domain: D_INTELLIGENCE
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
domain_id: D_INTELLIGENCE
path: src/zephyr/intelligence/llm_market_interpreter.py
granularity: file
---

# MOD-INT-MKT-INTERPRETER llm_market_interpreter 蓝图（LLM 市场解读引擎）

> **module_id**: MOD-INT-MKT-INTERPRETER | **域**: D_INTELLIGENCE | **优先级**: P1
> **来源**: B1-00118（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，D-ALT-11，
> §功能域模块·D-ALT-DATA）
> 代码：`src/zephyr/intelligence/llm_market_interpreter.py`

## 0. 定位

三路输入（新闻/研报摘要/社媒）统一市场解读引擎：本地 LLM 盘后 + API
盘中双模解读，输出结构化结论（主题/情感/影响标的/置信度）；**仅作信号
输入不直接下单**，结论经注入 audit_sink 入审计链。

与既有族分工（查重裁定）：
- MOD-INT-AISA news_sentiment_analyzer（10605058，stable）：**单路新闻**
  情感打分+窗口聚合（规则法 MVP）。本模块为**三路统一解读**（新闻/研报/
  社媒）+主题与影响标的结构化，不复制其打分与聚合逻辑。
- MOD-INT-API-LLM-POOL api_llm_pool（10603036，testing）：provider 池化治理
  （注册/计费/健康/降级信号）。本模块经注入 callable 消费 LLM 能力，不
  复制池治理；盘中 API 模式的选择/降级归池与 gateway。
- MOD-INF-009 llm_gateway（10604864）：真实调用面；本模块零密钥零直连。
- MOD-PLAN-007 llm_premarket_analysis：盘前综合复盘单点（计划域）；本模块
  为盘中/盘后统一解读引擎，分工不重叠。

## 1. 判定核心（纯内存，无 IO）

- `interpret(bundle, mode=None)`：`MarketInputBundle`（frozen：news/research/
  social/as_of）三路全空 → ValueError Fail-Closed。
- 双模选择：`mode` 显式给定 ∈{local,api}，缺省经注入 `mode_selector(as_of)`
  决定（盘后本地/盘中 API 的装配策略留运行时）；对应 `local_llm` /
  `api_llm` callable 缺失 → ValueError。
- 结构化解析：LLM 返回须为 JSON（theme/sentiment/affected_symbols/
  confidence）；非 JSON/缺字段/sentiment∉[-1,1]/confidence∉[0,1] →
  InterpretationError Fail-Closed（不放行伪结构）。
- 审计链：每次解读产 AuditRecord（mode/sources_used/interpretation/
  raw_digest）经注入 `audit_sink(record)` 外发；sink 异常不阻断结论返回
  （留痕 sink_errors）。
- 信号边界：MarketInterpretation 只含主题/情感/影响标的/置信度，无任何
  下单/仓位语义（signal_only 不变量入 dataclass 文档与测试断言）。

## 2. 接口

```python
@dataclass(frozen=True) MarketInputBundle: news/research/social/as_of
@dataclass(frozen=True) MarketInterpretation: theme/sentiment/affected_symbols/confidence/mode/sources_used
@dataclass(frozen=True) AuditRecord: mode/sources_used/interpretation/raw_digest/occurred_at
class LlmMarketInterpreter(local_llm=None, api_llm=None, mode_selector=None, audit_sink=None):
    interpret(bundle, mode=None) -> MarketInterpretation
class InterpretationError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO；local_llm/api_llm/audit_sink 全注入式（单测不触
  模型不触网）。
- 三路来源留痕：sources_used 记录实际非空输入路。
- LLM 输出解析 Fail-Closed：结构非法即抛，不降级为自由文本。
- 零密钥字段；仅信号输入，无下单语义。

## 4. 依赖

- MOD-INT-API-LLM-POOL api_llm_pool（设计边：盘中 API 模式池治理对齐）
- MOD-INT-AISA news_sentiment_analyzer（设计边：新闻路情感语义对齐）

## 5. MVP 边界

- 运行时接线（local_llm 接本地池 qwen3:8b、api_llm 接 API 池/gateway、
  mode_selector 接交易时段真源、audit_sink 接审计链真源）留运行时装配批；
  本模块交付三路输入契约 + 双模选择 + 结构化解析 + 审计外发核心。
