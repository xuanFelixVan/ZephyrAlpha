---
blueprint_id: MOD-RPT-035
module_name: strategy_explainability_reporter
domain: D_REPORTING
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
domain_id: D_REPORTING
path: src/zephyr/reporting/strategy_explainability_reporter.py
granularity: file
---

# MOD-RPT-035 strategy_explainability_reporter 蓝图（策略可解释性报告器）

> **module_id**: MOD-RPT-035 | **域**: D_REPORTING | **优先级**: P2
> **来源**: B4-06655（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-RPT-010，B4 D-REPORTING-14）
> 代码：`src/zephyr/reporting/strategy_explainability_reporter.py`

## 0. 定位

SHAP+LIME双归因报告（注入shap/lime解释器降级规则重要性兜底）+可解释性门控（解释覆盖度<阈值→策略降权/拦截）+报告发布对接（注入publisher）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/reporting/test_strategy_explainability_reporter.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
