---
blueprint_id: MOD-PLAN-022
module_name: plan_deviation_monitor
domain: D_PLAN
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
domain_id: D_PLAN
path: src/zephyr/plan_engine/plan_deviation_monitor.py
granularity: file
---

# MOD-PLAN-022 plan_deviation_monitor 蓝图（计划偏差检测与机会评估）

> **module_id**: MOD-PLAN-022 | **域**: D_PLAN | **优先级**: P2
> **来源**: B10-01479（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PLAN-016，A1 模块38）
> 代码：`src/zephyr/plan_engine/plan_deviation_monitor.py`

## 0. 定位

盘中计划偏差实时监控（实际vs盘前计划偏离>2σ判定，有利偏差持有/不利纠错分类）+计划外强信号评估（z>3σ且E>0.5%且计划外仓位≤20%三重闸）+评估记录留痕。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/plan_engine/test_plan_deviation_monitor.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
