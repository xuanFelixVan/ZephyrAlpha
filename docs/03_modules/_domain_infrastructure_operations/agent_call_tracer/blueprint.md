---
blueprint_id: MOD-INF-083
module_name: agent_call_tracer
domain: D_INFRA_TELEMETRY
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
domain_id: D_INFRA_TELEMETRY
path: src/zephyr/infrastructure/system_telemetry/agent_call_tracer.py
granularity: file
---

# MOD-INF-083 agent_call_tracer 蓝图（AI Agent调用链追踪器）

> **module_id**: MOD-INF-083 | **域**: D_INFRA_TELEMETRY | **优先级**: P2
> **来源**: B14-04637（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRATEL-003，A9运维架构）
> 代码：`src/zephyr/infrastructure/system_telemetry/agent_call_tracer.py`

## 0. 定位

Agent调用链Span模型（意图→工具调用→LLM→决策输出四段）关联OTel TraceID，Span树构建/闭合/校验，异常/超预算调用高亮标记，调用链落审计回调供回放。LangSmith式追踪单机内存版。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infrastructure/test_agent_call_tracer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
