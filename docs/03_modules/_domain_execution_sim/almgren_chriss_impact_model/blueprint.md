---
blueprint_id: MOD-EXSIM-001
module_name: almgren_chriss_impact_model
domain: D_EXEC_SIM
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
domain_id: D_EXEC_SIM
path: src/zephyr/execution_simulation/almgren_chriss_impact_model.py
granularity: file
---

# MOD-EXSIM-001 almgren_chriss_impact_model 蓝图（Almgren-Chriss冲击成本模型）

> **module_id**: MOD-EXSIM-001 | **域**: D_EXEC_SIM | **优先级**: P2
> **来源**: B3-06286（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-EXSIM-001，B3 R-118）
> 代码：`src/zephyr/execution_simulation/almgren_chriss_impact_model.py`

## 0. 定位

Almgren-Chriss冲击建模：临时冲击（η×(参与率)^β×σ）+永久冲击（γ×sqrt(参与率)×σ默认档）参数化+冲击衰减曲线（按成交节奏分段）+基于分钟成交额的参数估计器+冲击成本真源输出供执行仿真/回测消费。新建 src/zephyr/execution_simulation/ 包（含 __init__.py）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/execution_simulation/test_almgren_chriss_impact_model.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
