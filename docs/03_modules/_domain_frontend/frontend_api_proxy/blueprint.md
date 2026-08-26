---
blueprint_id: MOD-FE-011
module_name: frontend_api_proxy
domain: D_FRONTEND
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
domain_id: D_FRONTEND
path: src/zephyr/frontend/frontend_api_proxy.py
granularity: file
---

# MOD-FE-011 frontend_api_proxy 蓝图（前端API代理）

> **module_id**: MOD-FE-011 | **域**: D_FRONTEND | **优先级**: P2
> **来源**: B9-10703（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-012，B9 D-FRONTEND-22）
> 代码：`src/zephyr/frontend/frontend_api_proxy.py`

## 0. 定位

前后端唯一接触点代理：请求路由表（前缀→上游）+鉴权（token校验注入）+限流（令牌桶注入时钟）+转发（upstream client注入不真发）+响应规范化。BFF思想。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/frontend/test_frontend_api_proxy.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
