---
blueprint_id: MOD-SIG-130
module_name: strategy_matrix_3d
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
path: src/zephyr/signal_ashare/strategy_matrix_3d.py
granularity: file
---

# MOD-SIG-130 strategy_matrix_3d 蓝图（量能体制风格三维策略矩阵）

> **module_id**: MOD-SIG-130 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01467（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-048，A1 模块56）
> 代码：`src/zephyr/signal_ashare/strategy_matrix_3d.py`

## 0. 定位

3×3×2=18格策略查找表（量能3×体制3×风格2，格值=仓位/选股方向/持仓周期/止损k×ATR四要素）+参数由历史回测逐格填参（注入backtest_runner）+格子查询接口+参数版本管理。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_strategy_matrix_3d.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
