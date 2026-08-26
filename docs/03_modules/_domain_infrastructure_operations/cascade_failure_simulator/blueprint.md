---
blueprint_id: MOD-INF-089
module_name: cascade_failure_simulator
domain: D_INFRA_RECOVERY
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
domain_id: D_INFRA_RECOVERY
path: src/zephyr/infrastructure/rollback/cascade_failure_simulator.py
granularity: file
---

# MOD-INF-089 cascade_failure_simulator 蓝图（级联失效仿真器）

> **module_id**: MOD-INF-089 | **域**: D_INFRA_RECOVERY | **优先级**: P2
> **来源**: B14-04693（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-DR-002，A9运维架构）
> 代码：`src/zephyr/infrastructure/rollback/cascade_failure_simulator.py`

## 0. 定位

单机级联失效仿真：进程崩溃→Redis中断→GPU失效组合场景脚本化（场景schema+编排），失效传播路径记录（有向事件链）+恢复时间测量，安全护栏（仅非交易时段注入判定+备份确认前置+30min超时终止）。纯仿真编排，故障注入全经回调不真杀进程。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infrastructure/test_cascade_failure_simulator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
