---
blueprint_id: MOD-INT-MATRIX
module_name: integration_matrix_registry
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
path: src/zephyr/integration/integration_matrix_registry.py
granularity: file
---

# MOD-INT-MATRIX integration_matrix_registry 蓝图（集成交互矩阵注册表）

> **module_id**: MOD-INT-MATRIX | **域**: D_INTEGRATION | **优先级**: P2
> **来源**: B14-04736（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-BACL-005，A10 v6.0）
> 代码：`src/zephyr/integration/integration_matrix_registry.py`

## 0. 定位

外部系统交互矩阵契约注册表（系统×交互×协议×隔离策略四要素）+数据源故障降级策略声明（降级链表）+隔离规则配置化（规则schema+校验）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/integration/test_integration_matrix_registry.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
