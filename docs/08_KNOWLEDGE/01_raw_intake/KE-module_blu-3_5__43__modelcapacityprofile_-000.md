---
module_id: KE-module_blu-3_5__43__modelcapacityprofile_-000
title: 3.5 #43: ModelCapacityProfile + ModelSwitchRecalibrator
category: module_blueprint
---

# 3.5 #43: ModelCapacityProfile + ModelSwitchRecalibrator

3.5 #43: ModelCapacityProfile + ModelSwitchRecalibrator

文件：`D:\ZephyrAlpha\src\zephyr\shared\model_capacity_profile.py`

- `ModelCapacityProfile`: 每模型容量画像（成本/延迟/典型Token消耗/API限制/质量指标）
- `ModelSwitchRecalibrator.on_model_switch(from, to)`: 切换时自动重校准所有预算
