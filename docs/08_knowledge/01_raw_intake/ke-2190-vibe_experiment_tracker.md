---
module_id: KE-2097
status: active
title: 3.3 #41: VibeExperimentTracker (M-38)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.3 #41: VibeExperimentTracker (M-38)

3.3 #41: VibeExperimentTracker (M-38)

文件：`D:\ZephyrAlpha\src\zephyr\shared\vibe_experiment_tracker.py`

实现 `VibeExperimentTracker` 类：
- `start_experiment(task_desc)`: 检查日预算（200K tokens/15次/天），超限→VibeBudgetExhausted
- `end_experiment(exp_id, kept_files)`: 统计资源消耗，清理实验产物
- 配置：`vibe_experiment_budget` 节 in token_budget.yaml
