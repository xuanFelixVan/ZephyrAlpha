---
blueprint_id: MOD-RPT-033
module_name: decision_trace_chain
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
path: src/zephyr/reporting/decision_trace_chain.py
granularity: file
---

# MOD-RPT-033 decision_trace_chain 蓝图（决策溯源链）

> **module_id**: MOD-RPT-033 | **域**: D_REPORTING | **优先级**: P2
> **来源**: B1-00220（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-RPT-008，C2 C-030）
> 代码：`src/zephyr/reporting/decision_trace_chain.py`

## 0. 定位

决策链ID贯穿信号→计划→订单→成交四段（段记录注入存储）+全链反查（按decision_id聚合）+因子贡献摘要（注入贡献度）+密度感知置信度调整（分位数→置信度映射注入训练器语义）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/reporting/test_decision_trace_chain.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
