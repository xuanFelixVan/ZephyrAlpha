---
blueprint_id: MOD-PLAN-023
module_name: premarket_workflow_engine
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
path: src/zephyr/plan_engine/premarket_workflow_engine.py
granularity: file
---

# MOD-PLAN-023 premarket_workflow_engine 蓝图（盘前标准化工作流引擎）

> **module_id**: MOD-PLAN-023 | **域**: D_PLAN | **优先级**: P2
> **来源**: B14-04681（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PLAN-017，A9 D-TRADING-15）
> 代码：`src/zephyr/plan_engine/premarket_workflow_engine.py`

## 0. 定位

盘前标准工序编排：数据同步→隔夜复盘→情绪扫描→预案生成→盘前检查→就绪确认六工序（工序handler注入）+失败阻断（前序失败后续跳过）+人工接管点（标记后暂停等确认）+耗时统计报告。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/plan_engine/test_premarket_workflow_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
