---
blueprint_id: MOD-INF-090
module_name: strategic_message_bus
domain: D_INFRA_A2A
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
domain_id: D_INFRA_A2A
path: src/zephyr/infrastructure/a2a_protocol/strategic_message_bus.py
granularity: file
---

# MOD-INF-090 strategic_message_bus 蓝图（战略层消息总线）

> **module_id**: MOD-INF-090 | **域**: D_INFRA_A2A | **优先级**: P2
> **来源**: B11-02493（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAA2A-002，A7-Agent架构）
> 代码：`src/zephyr/infrastructure/a2a_protocol/strategic_message_bus.py`

## 0. 定位

三层逻辑总线：strategic.*/tactical.*/execution.*三层topic命名空间校验+发布订阅权限按Agent层级校验（层级表注入），跨层消息强制流经A2A检查网关（注入网关回调，未注入Fail-Closed），层内直连层间留痕（审计回调）。战术层/执行层总线作为同机制实例。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infrastructure/test_strategic_message_bus.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
