---
blueprint_id: MOD-EX-064
module_name: execution_param_optimizer
domain: D_EX_CORE
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
domain_id: D_EX_CORE
path: src/zephyr/ex_core/execution_param_optimizer.py
granularity: file
---

# MOD-EX-064 execution_param_optimizer 蓝图（执行运营自优化器）

> **module_id**: MOD-EX-064 | **域**: D_EX_CORE | **优先级**: P2
> **来源**: B1-00218（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-EX-010，C2 C-026）
> 代码：`src/zephyr/ex_core/execution_param_optimizer.py`

## 0. 定位

执行运营自优化：周期读TCA与成交质量（注入tca_reader）+optuna搜索下单算法参数与运营规则（注入study_runner，optuna未装降级网格搜索）+人工确认后生效（确认队列硬约束）+不自动改风控硬阈值（参数白名单拦截）。canonical承接EX-011归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ex_core/test_execution_param_optimizer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
