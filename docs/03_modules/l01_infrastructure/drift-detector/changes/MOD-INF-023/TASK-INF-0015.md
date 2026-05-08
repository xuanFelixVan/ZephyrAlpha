---
task_id: "TASK-INF-0015"
title: "自动学习假阳性模式识别与抑制（D-023-21）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P2"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0005"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - "同一 (detector_id, module_id, pattern_hash) 被 FALSE_POSITIVE >= 3 次 → 自动创建 suppression_rule"
  - "pattern_hash = SHA256(detector_id + drift_dimension + diff_signature)"
  - "shadow_mode: 抑制后仍在后台检测，pattern 变化 → 自动解除抑制"
  - "suppression_review: 每30天提示 Owner review 活跃 suppression_rule"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.14"]}]
tags: ["drift-detector","auto-learning","D-023-21"]
---
# TASK-INF-0015: 自动学习假阳性（D-023-21）
对标 §2.14。实现 pattern_hash 归一化、3次误报自动抑制、shadow观测、pattern变化自动解除、30天定期审查。
