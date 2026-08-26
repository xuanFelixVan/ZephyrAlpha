---
blueprint_id: MOD-ML-017
module_name: kan_density_head
domain: D_ML_TRAIN
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
domain_id: D_ML_TRAIN
path: src/zephyr/ml_train/implementations/kan_density_head.py
granularity: file
---

# MOD-ML-017 kan_density_head 蓝图（KAN密度预测头）

> **module_id**: MOD-ML-017 | **域**: D_ML_TRAIN | **优先级**: P2
> **来源**: B10-01878（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-024，A1 §29.33）
> 代码：`src/zephyr/ml_train/implementations/kan_density_head.py`

## 0. 定位

KanDensityHead：可学习B样条激活（阶数≤4护栏，系数栅格初始化）+前向分位数输出（纯numpy，样条基函数Cox-de Boor递推）+替换QNN Stage1 MLP语义（接口对齐）+须过C-003验证语义标注（验证报告注入）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_train/implementations/test_kan_density_head.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
