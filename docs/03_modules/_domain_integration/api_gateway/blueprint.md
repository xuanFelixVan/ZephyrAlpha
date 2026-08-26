---
blueprint_id: MOD-INT-APIGW
module_name: api_gateway
domain: D_INTEGRATION_GATEWAY
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
domain_id: D_INTEGRATION_GATEWAY
path: src/zephyr/integration/api_gateway.py
granularity: file
---

# MOD-INT-APIGW api_gateway 蓝图（API网关）

> **module_id**: MOD-INT-APIGW | **域**: D_INTEGRATION_GATEWAY | **优先级**: P2
> **来源**: B1-00322（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-INTEGRAT-001，C2 D-INT-01）
> 代码：`src/zephyr/integration/api_gateway.py`

## 0. 定位

单进程轻量网关：请求路由表+token认证（注入）+限流/熔断挂接（注入limiter/breaker）+脱敏过滤器（敏感字段规则）+访问审计回调+AI Gateway面复用llm_gateway语义。严禁Kong/Envoy。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/integration/test_api_gateway.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
