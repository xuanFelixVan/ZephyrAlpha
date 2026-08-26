---
blueprint_id: MOD-ML-019
module_name: research_data_manager
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
path: src/zephyr/ml_train/research_data_manager.py
granularity: file
---

# MOD-ML-019 research_data_manager 蓝图（研究数据管理器）

> **module_id**: MOD-ML-019 | **域**: D_ML_TRAIN | **优先级**: P2
> **来源**: B13-04336（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-027，A3 D-RESEARCH-01）
> 代码：`src/zephyr/ml_train/research_data_manager.py`

## 0. 定位

研究数据管理：数据集快照（manifest+hash，Git-like版本链）+血缘挂lineage回调+质量评分（复用质量门控注入）+元数据检索+保留策略（TTL裁决）。DVC/LakeFS思想单机版。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_train/test_research_data_manager.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
