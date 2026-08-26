---
blueprint_id: MOD-INT-OPENAPI
module_name: api_documentation_generator
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
path: src/zephyr/integration/api_documentation_generator.py
granularity: file
---

# MOD-INT-OPENAPI api_documentation_generator 蓝图（API文档生成器）

> **module_id**: MOD-INT-OPENAPI | **域**: D_INTEGRATION | **优先级**: P2
> **来源**: B1-00337（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-BACL-004，C2 D-INT-05）
> 代码：`src/zephyr/integration/api_documentation_generator.py`

## 0. 定位

从contracts/api路由注解生成OpenAPI 3.0 yaml（路由注册表+schema推导）+CI契约漂移校验（生成结果与基线diff超阈值告警）+输出至docs供MCP/前端消费语义。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/integration/test_api_documentation_generator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
