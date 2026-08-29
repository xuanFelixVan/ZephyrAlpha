---
blueprint_id: MOD-FE-013
module_name: wechat_bot_handler
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
path: src/zephyr/frontend/implementations/wechat_bot_handler.py
granularity: file
---

# MOD-FE-013 wechat_bot_handler 蓝图（企业微信机器人处理器）

> **module_id**: MOD-FE-013 | **域**: D_FRONTEND | **优先级**: P2
> **来源**: B9-10706（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-014，B9 D-FRONTEND-25）
> 代码：`src/zephyr/frontend/implementations/wechat_bot_handler.py`（2026-08-29 自 frontend/ 根迁入，trae_024 单一类型归位）

## 0. 定位

企业微信回调接收（消息schema校验）+指令鉴权（白名单主体+注入鉴权器）+盯盘/查询指令解析（指令词表闭合）+回复渲染（文本/卡片模板）+下单指令二次确认硬约束（确认超时拒绝）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/frontend/test_wechat_bot_handler.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
