---
blueprint_id: MOD-INT-AIROUTE
module_name: ai_service_route_matrix
domain: D_INTEGRATION
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
domain_id: D_INTEGRATION
path: src/zephyr/integration/ai_service_route_matrix.py
granularity: file
---

# MOD-INT-AIROUTE ai_service_route_matrix 蓝图（AI服务分级路由表）

> **module_id**: MOD-INT-AIROUTE | **域**: D_INTEGRATION | **优先级**: P2
> **来源**: B14-04762（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-BACL-006，A10）
> 代码：`src/zephyr/integration/ai_service_route_matrix.py`

## 0. 定位

AI服务分级路由表（本地LLM/API/ASR/MCP四类+L1/L2/L3分级）+成本延迟画像（单价/延迟P50P99登记）+故障降级链（首选不可用→按链降级+标记）。LiteLLM路由思想。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/integration/test_ai_service_route_matrix.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
