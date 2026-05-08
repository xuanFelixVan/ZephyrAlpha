---
module_id: KE-documentat-7_2-003
title: 7.2 流程
category: documentation
---

# 7.2 流程

7.2 流程

```
1. 运行 score_architecture.py --quarterly --dashboard
   → 产出 architecture-score-dashboard.md

2. 用户审阅 dashboard，识别：
   - 退步维度（环比下降 > 0.5 分）
   - 未达 Phase 目标的维度
   - 新增红线

3. 若存在 P0 红线（分数 < 3.0），立即进入"整改计划"：
   - 新建 KB 决策记录 分析根因
   - 排入下 Phase 任务卡
   - 下次评审检查是否恢复

4. 评审会议纪要归档到 docs/19_development_workspace/architecture-score-reviews/YYYY-QN.md
```
