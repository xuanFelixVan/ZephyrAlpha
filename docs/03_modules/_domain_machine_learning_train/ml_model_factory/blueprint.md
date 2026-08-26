---
blueprint_id: MOD-ML-013
module_name: ml_model_factory
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
path: src/zephyr/ml_train/ml_model_factory.py
granularity: file
---

# MOD-ML-013 ml_model_factory 蓝图（ML模型工厂）

> **module_id**: MOD-ML-013 | **域**: D_ML_TRAIN | **优先级**: P2
> **来源**: B1-00253（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-017，C2 C-029）
> 代码：`src/zephyr/ml_train/ml_model_factory.py`

## 0. 定位

ML模型工厂：模型注册表（名称/版本/元数据）+全生命周期状态机（dev→candidate→staging→production→retired含回退）+灰度发布编排（挂gray_release_shadow_deployer语义注入）+对抗鲁棒门禁（注入validator，不过禁上线）+GPU任务队列整合（注入scheduler）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_train/test_ml_model_factory.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
