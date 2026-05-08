---
task_id: "TASK-INF-0025"
title: "时序存储与趋势分析 trend_analyzer.py（D-023-08）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "6h"
depends_on: ["TASK-INF-0002","TASK-INF-0005"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\trend_analyzer.py"]
acceptance_criteria:
  - "drift_velocity: COUNT(∗) GROUP BY module_id, week → 单模块>5/week告警"
  - "drift_resolution_rate: COUNT(VERIFIED)/COUNT(∗) per module per month → <50%告警"
  - "mean_time_to_resolve: DETECTED→VERIFIED平均时间 → >7 days升级"
  - "detector_false_positive_ratio: per detector → >30%告警"
  - "trend_alerts: spike(>均值+3σ)、slow_growth(连续4周velocity递增)、silence(48h零漂移→检测器损坏)"
  - "storage: 90天热数据SQLite + 按年归档JSONL"
rollback_instructions: "git checkout src/zephyr/drift_detector/trend_analyzer.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§5.1"]}]
tags: ["drift-detector","time-series","trend","D-023-08"]
---
# TASK-INF-0025: 时序存储与趋势分析（D-023-08）
对标 §5.1。实现4个metrics(drift_velocity/resolution_rate/MTTR/fp_ratio)+3种trend_alerts(spike/slow_growth/silence)+90天热数据+按年归档。
