---
task_id: "TASK-INF-0016"
title: "多实例竞态控制——scan mutex 实现（D-023-24）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - "文件锁 data/drift_scan.lock: pid + scan_id + scan_start_time + scan_level"
  - "same_level_collision: 排队等待(前完成+max wait=SLO×2)"
  - "level_preemption: LIGHT优先级高于DEEP"
  - "reverse_preemption: DEEP中LIGHT触发→使用DEEP当前进度作为缓存"
  - "merge_strategy: 同level排队队列→合并(覆盖，基于更新HEAD)"
  - "stale lock: 持有超过SLO×2→强制清除+通知Owner"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.15"]}]
tags: ["drift-detector","mutex","concurrency","D-023-24"]
---
# TASK-INF-0016: 多实例竞态控制（D-023-24）
对标 §2.15。实现 scan mutex 文件锁 + 碰撞策略(排队/合并) + 优先级抢占 + stale lock 检测。
