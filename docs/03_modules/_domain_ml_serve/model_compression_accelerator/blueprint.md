---
blueprint_id: MOD-MLS-002
module_name: model_compression_accelerator
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
path: src/zephyr/ml_serve/model_compression_accelerator.py
granularity: file
---

# MOD-MLS-002 model_compression_accelerator 蓝图（模型压缩与推理加速器）

> **module_id**: MOD-MLS-002 | **域**: D_ML_SERVE | **优先级**: P2
> **来源**: B10-01872（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLS-002，A1 §29.28）
> 代码：`src/zephyr/ml_serve/model_compression_accelerator.py`

## 0. 定位

三阶段压缩编排：Phase1 ONNX+INT8（校准集防泄漏校验+数值误差<1e-5验证注入）/Phase2 llama.cpp+INT4（量化后重过Double-Lock注入）/Phase3知识蒸馏（注入distiller）+每阶段C-003完整验证门禁（CRPS/Sharpe/MaxDD不显著降判定注入）+压缩登记册。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_serve/test_model_compression_accelerator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
