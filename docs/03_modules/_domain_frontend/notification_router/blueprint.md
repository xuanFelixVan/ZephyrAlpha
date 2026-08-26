---
blueprint_id: MOD-FE-004
module_name: notification_router
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
path: src/zephyr/frontend/notification_router.py
granularity: file
---

# MOD-FE-004 notification_router 蓝图（通知路由器）

> **module_id**: MOD-FE-004 | **域**: D_FRONTEND | **优先级**: P2
> **来源**: B1-00138（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-004，C2 D-FE-13）
> 代码：`src/zephyr/frontend/notification_router.py`

## 0. 定位

通道适配（企业微信/飞书webhook发送器注入，密钥入secrets引用不落地）+严重级→通道路由表+静默时段（注入时钟）+未确认升级（超时未ack升级更严重通道）+与alert_manager挂接语义。Alertmanager路由思想。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/frontend/test_notification_router.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
