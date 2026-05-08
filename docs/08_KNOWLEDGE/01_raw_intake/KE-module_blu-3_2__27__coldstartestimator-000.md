---
module_id: KE-module_blu-3_2__27__coldstartestimator-000
title: 3.2 #27: ColdStartEstimator
category: module_blueprint
---

# 3.2 #27: ColdStartEstimator

3.2 #27: ColdStartEstimator

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\cold_start_estimator.py`

实现 `ColdStartEstimator` 类（蓝图 L2816-2865）：
- `is_cold_start() -> bool`：判断是否为冷启动（< 7天历史数据）
- initial_budget = `MIN(owner_manual_label × 0.5, 1000req/min)`
- 7天后自动退出观察期，切换为预算自动校准
- 蓝图 L2823-2860 算法完整实现
