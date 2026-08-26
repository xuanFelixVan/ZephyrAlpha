---
blueprint_id: MOD-SIG-119
module_name: sector_crowding_launch
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
path: src/zephyr/signal_ashare/sector_crowding_launch.py
granularity: file
---

# MOD-SIG-119 sector_crowding_launch 蓝图（板块拥挤度与启动条件）

> **module_id**: MOD-SIG-119 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01384（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-039，A1 模块40）
> 代码：`src/zephyr/signal_ashare/sector_crowding_launch.py`

## 0. 定位

板块拥挤度（换手率+融资余额占比+持仓相关性三分量>90%分位过热）+过热预警（拥挤>90%分位+动量衰减>30%→回撤概率高）+启动条件（RS突破+资金转正3日确认状态机）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_sector_crowding_launch.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
