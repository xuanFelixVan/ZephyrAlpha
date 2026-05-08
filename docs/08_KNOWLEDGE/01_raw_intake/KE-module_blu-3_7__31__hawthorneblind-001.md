---
module_id: KE-module_blu-3_7__31__hawthorneblind-001
title: 3.7 #31: HawthorneBlind
category: module_blueprint
---

# 3.7 #31: HawthorneBlind

3.7 #31: HawthorneBlind

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\hawthorne_blind.py`

实现 `HawthorneBlind` 类（蓝图 L3051-3110）：
- 双轨数据源架构：`reality_track`（真实度量，用于SLO评估）vs `ai_visible_track`（AI可访问的降采样净化版）
- `filter_visible_metrics(raw_data) -> dict`：剔除敏感监控信息
