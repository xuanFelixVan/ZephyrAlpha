---
blueprint_id: MOD-SIG-122
module_name: calendar_effects_model
domain: D_ASHARE_SIGNAL
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
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/calendar_effects_model.py
granularity: file
---

# MOD-SIG-122 calendar_effects_model 蓝图（A股日历效应模型）

> **module_id**: MOD-SIG-122 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01390（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-042，A1 模块55）
> 代码：`src/zephyr/signal_ashare/calendar_effects_model.py`

## 0. 定位

日历效应滚动统计检验：月度/周内/节假日/交割日四类（分组均值t检验注入统计器+分年稳健性）+效应日历输出（显著效应节点清单，节点数量由数据决定非人为）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_calendar_effects_model.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
