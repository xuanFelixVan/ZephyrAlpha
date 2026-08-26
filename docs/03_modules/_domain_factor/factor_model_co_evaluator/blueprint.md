---
blueprint_id: MOD-FAC-005
module_name: factor_model_co_evaluator
domain: D_FACTOR
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
domain_id: D_FACTOR
path: src/zephyr/research/factor_model_co_evaluator.py
granularity: file
---

# MOD-FAC-005 factor_model_co_evaluator 蓝图（因子模型联合评估器）

> **module_id**: MOD-FAC-005 | **域**: D_FACTOR | **优先级**: P2
> **来源**: B10-01230（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-017，A1 v8.2）
> 代码：`src/zephyr/research/factor_model_co_evaluator.py`

## 0. 定位

R&D-Agent-Quant联合优化：FactorModelCoEvaluator因子↔模型双向评估（因子贡献于模型性能/模型对因子利用度双向报告）+淘汰/迭代建议（低贡献因子淘汰清单+高潜力迭代方向）+报告版本化。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/research/test_factor_model_co_evaluator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
