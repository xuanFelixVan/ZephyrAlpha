---
blueprint_id: MOD-ML-018
module_name: continual_learning_antiforget
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
path: src/zephyr/ml_train/continual_learning_antiforget.py
granularity: file
---

# MOD-ML-018 continual_learning_antiforget 蓝图（持续学习抗遗忘框架）

> **module_id**: MOD-ML-018 | **域**: D_ML_TRAIN | **优先级**: P2
> **来源**: B10-01881（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-025，A1 §29.35）
> 代码：`src/zephyr/ml_train/continual_learning_antiforget.py`

## 0. 定位

抗遗忘框架：EWC正则（Fisher信息盘后批处理注入计算，重要性权重缓存）+经验回放（每市场状态代表样本缓冲≤1000条硬约束，注入regime标注）+微调后旧状态验证（性能降≤5%门禁判定）+回滚机制（参数快照+验证失败回滚）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_train/test_continual_learning_antiforget.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
