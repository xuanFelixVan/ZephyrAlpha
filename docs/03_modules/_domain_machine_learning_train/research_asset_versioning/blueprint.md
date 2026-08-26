---
blueprint_id: MOD-ML-022
module_name: research_asset_versioning
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
path: src/zephyr/ml_train/research_asset_versioning.py
granularity: file
---

# MOD-ML-022 research_asset_versioning 蓝图（研究资产版本化管理器）

> **module_id**: MOD-ML-022 | **域**: D_ML_TRAIN | **优先级**: P2
> **来源**: B13-04341（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-030，A3 D-RESEARCH-18）
> 代码：`src/zephyr/ml_train/research_asset_versioning.py`

## 0. 定位

研究资产版本化：因子/模型/策略三类统一SemVer（major.minor.patch校验）+不可变版本记录（写后不可改）+复用索引（按资产/版本/指标三维检索）+跨项目复用登记。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_train/test_research_asset_versioning.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
