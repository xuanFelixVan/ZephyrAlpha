---
blueprint_id: MOD-ALT-009
module_name: research_report_collector
domain: D_ALT_DATA
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_ALT_DATA
path: src/zephyr/alt_data/research_report_collector.py
granularity: file
---

# MOD-ALT-009 research_report_collector 蓝图（研报采集器）

> **module_id**: MOD-ALT-009 | **域**: D_ALT_DATA | **优先级**: P2
> **来源**: B1-00628（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-012，C2 72）
> 代码：`src/zephyr/alt_data/research_report_collector.py`

## 0. 定位

研报元数据采集（东财研报中心语义：标题/评级/目标价/机构/日期，API注入）+评级变动检测（前后快照diff）+评级变动事件入事件总线回调+标的映射注入news_symbol_linker语义+正文结构化产物引用接口。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/alt_data/test_research_report_collector.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
