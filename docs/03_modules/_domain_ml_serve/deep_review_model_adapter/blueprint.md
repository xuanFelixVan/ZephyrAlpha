---
blueprint_id: MOD-MLS-004
module_name: deep_review_model_adapter
domain: D_ML_SERVE
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
domain_id: D_ML_SERVE
path: src/zephyr/ml_serve/deep_review_model_adapter.py
granularity: file
---

# MOD-MLS-004 deep_review_model_adapter 蓝图（深度审查模型适配器）

> **module_id**: MOD-MLS-004 | **域**: D_ML_SERVE | **优先级**: P2
> **来源**: B10-02297（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLS-004，A1 D-ML-47）
> 代码：`src/zephyr/ml_serve/deep_review_model_adapter.py`

## 0. 定位

model_router注册GLM-5.1深度审查profile+考试校准（校准集评分分布→通过阈值标定，注入exam_runner）+审查任务schema（审查类型词表+结构化 findings 输出校验）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_serve/test_deep_review_model_adapter.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
