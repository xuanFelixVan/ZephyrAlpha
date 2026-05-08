---
module_id: KE-module_blu-3_3__23__aiskillmonitor__m-28-000
title: 3.3 #23: AISkillMonitor (M-28)
category: module_blueprint
---

# 3.3 #23: AISkillMonitor (M-28)

3.3 #23: AISkillMonitor (M-28)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\ai_skill_monitor.py`

实现 `AISkillMonitor` 类（蓝图 L2431-2501）：
- 四维 AI 技能健康度检测：
  - `test_pass_rate`: 第一轮测试通过率 → trending_down → 0.2 decay_weight
  - `merge_conflict_rate`: PR 冲突率 → trending_up → 0.25
  - `retry_loop_rate`: 修复重试次数 → trending_up → 0.25
  - `instant_acceptance_rate`: Owner 直接接受率 → trending_down → 0.30
- `compute_skill_score() -> float`：加权评分
- `detect_degradation_trend() -> bool`：评分连续下降时报警
- 蓝图 L2445-2472 算法完整实现
