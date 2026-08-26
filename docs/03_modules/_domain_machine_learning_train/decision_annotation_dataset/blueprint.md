---
blueprint_id: MOD-ML-014
module_name: decision_annotation_dataset
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
path: src/zephyr/ml_train/decision_annotation_dataset.py
granularity: file
---

# MOD-ML-014 decision_annotation_dataset 蓝图（交易决策标注数据集）

> **module_id**: MOD-ML-014 | **域**: D_ML_TRAIN | **优先级**: P2
> **来源**: B1-00631（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-018，C2 71）
> 代码：`src/zephyr/ml_train/decision_annotation_dataset.py`

## 0. 定位

决策标注schema（decision_id/标的/时点/理由/情绪标签/图表引用/结果回填七要素）+SQLite标注库（注入连接）+录入接口（结构化校验）+结果回填（事后收益）+导出SFT样本与复盘数据集+版本管理。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_train/test_decision_annotation_dataset.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
