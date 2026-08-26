---
blueprint_id: MOD-MLS-003
module_name: codegen_model_adapter
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
path: src/zephyr/ml_serve/codegen_model_adapter.py
granularity: file
---

# MOD-MLS-003 codegen_model_adapter 蓝图（代码生成模型适配器）

> **module_id**: MOD-MLS-003 | **域**: D_ML_SERVE | **优先级**: P2
> **来源**: B10-02296（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLS-003，A1 D-ML-46）
> 代码：`src/zephyr/ml_serve/codegen_model_adapter.py`

## 0. 定位

model_router注册DeepSeek-V4-Pro代码生成profile（能力声明/上下文窗/成本单价）+成本计量（按token计费累计+预算告警）+调用适配（请求/响应schema规范化，client注入不真发）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_serve/test_codegen_model_adapter.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
