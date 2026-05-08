---
module_id: KE-module_blu-3_6__60__progressivecapacityca-000
title: 3.6 #60: ProgressiveCapacityCalibrator
category: module_blueprint
---

# 3.6 #60: ProgressiveCapacityCalibrator

3.6 #60: ProgressiveCapacityCalibrator

文件：`D:\ZephyrAlpha\src\zephyr\shared\capacity_calibrator.py`

- 校准点：[100, 200, 500, 800, 1000, 1200, 1500]
- `on_module_count_reached(count)`: 测量实际容量→对比预测→误差>20%→修正模型
- 用户看到："⚠️ 容量预测模型在500模块处校准——偏差35%——已自动修正"
