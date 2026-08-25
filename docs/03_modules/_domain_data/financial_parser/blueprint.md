---
blueprint_id: MOD-DAT-FIN-PARSER
module_name: financial_parser
domain: D_DATA
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
domain_id: D_DATA
path: src/zephyr/data/financial_parser.py
granularity: file
---

# MOD-DAT-FIN-PARSER financial_parser 蓝图（财报结构化解析器）

> **module_id**: MOD-DAT-FIN-PARSER | **域**: D_DATA | **优先级**: P1
> **来源**: B13-04263（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，D-DATA-80，§17.1）
> 代码：`src/zephyr/data/financial_parser.py`

## 0. 定位

财报解析管道：年报/季报/快报/更正公告 PDF 与 XBRL → 结构化指标——
巨潮 PDF 下载产物经 pdfplumber 表格抽取 / XBRL(Arelle) 解析 → 指标标准化
映射 c3 财务表口径；本地 qwen3:8b 兜底非标准格式；解析置信度入
quality_flag。

与既有族分工（查重裁定）：
- announcement_provider（10603035，testing，P1W08 CAND-DAT-013）：巨潮/交易所
  **公告采集**（元数据+标题落 fund_news_data）。本模块为**财报内容结构化
  解析**（PDF/XBRL→指标），消费其公告元数据定位财报附件，不复制采集链。
- B1-00619（80 Financial Data Parser）dig 已裁定"不做-重复:B13-04263"，
  quarterly/annual 解析与财务比率明细并入本模块。
- B13-04280（Filing NLP Engine，P2 另候）：公告文本 NLP（风险事件/MD&A），
  复用本模块 PDF 解析产物，互补不重复。

## 1. 判定核心（纯内存，无 IO；解析器全注入）

- `parse_report(report)`：`ReportRef`（frozen：symbol/report_type/period/
  pdf_path/raw_tables/xbrl_facts/text）非法（空 symbol、未知 report_type
  ∈{annual,quarterly,express,correction}、空 period）→ ValueError。
- 解析路径阶梯：xbrl_facts 或注入 `xbrl_parser` → XBRL 路径
  （confidence=0.95）；否则 raw_tables 或注入 `pdf_extractor` → 表格路径
  （0.80）；否则注入 `llm_fallback` 非标准格式兜底（0.60）；三路皆无 →
  ValueError Fail-Closed。
- 指标标准化：`METRIC_MAP` 常量（中文表头/ XBRL 标签 → 规范指标键：
  revenue/net_profit/total_assets/total_liabilities/operating_cashflow/eps 等，
  c3 财务表口径）；未识别指标不入结果、计入 unmapped_keys 留痕。
- 数值清洗：千分位/括号负数/单位倍率（万元/亿元→元）归一。
- quality_flag：confidence≥0.90 good / ≥0.70 degraded / 否则 poor。

## 2. 接口

```python
METRIC_MAP: dict[str, str] 指标标准化映射常量
@dataclass(frozen=True) ReportRef: symbol/report_type/period/pdf_path/raw_tables/xbrl_facts/text
@dataclass(frozen=True) ParsedFinancials: symbol/period/report_type/metrics/parser_used/confidence/quality_flag/unmapped_keys
class FinancialParser(pdf_extractor=None, xbrl_parser=None, llm_fallback=None):
    parse_report(report) -> ParsedFinancials
```

## 3. 不变量

- 判定核心纯内存无 IO；pdf_extractor/xbrl_parser/llm_fallback 全注入式
  （pdfplumber/Arelle/qwen3:8b 真实绑定留装配批，单测不触网不触模型）。
- 同输入必同输出（确定性）；未映射指标留痕不静默丢弃。
- 置信度与 quality_flag 确定性派生，不依赖外部状态。

## 4. 依赖

- announcement_provider（设计边：财报公告元数据来源，不 import）

## 5. MVP 边界

- 巨潮 PDF 下载执行、pdfplumber/Arelle 真实绑定、qwen3:8b 本地调用、
  c3 财务表写入接线留运行时装配批；本模块交付解析路径阶梯 + 指标标准化
  映射 + 数值清洗 + 置信度/quality_flag 核心。
