---
blueprint_id: MOD-FE-012
module_name: feishu_bot_sender
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
path: src/zephyr/frontend/feishu_bot_sender.py
granularity: file
---

# MOD-FE-012 feishu_bot_sender 蓝图（飞书机器人推送器）

> **module_id**: MOD-FE-012 | **域**: D_FRONTEND | **优先级**: P2
> **来源**: B9-10705（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-013，B9 D-FRONTEND-24）
> 代码：`src/zephyr/frontend/implementations/feishu_bot_sender.py`（2026-08-29 自 frontend/ 根迁入，trae_024 单一类型归位）

## 0. 定位

飞书自定义机器人webhook sender（EXT-004 REST语义，client注入不真发）+审批通知模板（标题/字段/按钮schema）+告警推送（作为微信备选通道路由标记）+发送回执记录。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/frontend/test_feishu_bot_sender.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
