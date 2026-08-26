---
blueprint_id: MOD-ALT-010
module_name: policy_expectation_analyzer
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
path: src/zephyr/alt_data/policy_expectation_analyzer.py
granularity: file
---

# MOD-ALT-010 policy_expectation_analyzer 蓝图（A股政策预期分析器）

> **module_id**: MOD-ALT-010 | **域**: D_ALT_DATA | **优先级**: P2
> **来源**: B5-07096（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-026，B5 D-ALT-DATA-16）
> 代码：`src/zephyr/alt_data/policy_expectation_analyzer.py`

## 0. 定位

政策预期分析：监管/交易所公开表态采集（注入源）+窗口指导关键词库命中扫描+政策事件日历+LLM预期倾向打分（注入llm，[-1,1]闭合校验）+国家队持仓变动识别（季报公开数据+ETF份额异动阈值）+预期差信号输出（标注推断性质仅作信号输入，人工审核队列）。canonical承接TESTA-013归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/alt_data/test_policy_expectation_analyzer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
