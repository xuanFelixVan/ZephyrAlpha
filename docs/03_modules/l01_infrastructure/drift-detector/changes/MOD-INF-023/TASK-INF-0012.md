---
task_id: "TASK-INF-0012"
title: "漂移风暴与批量处理模式（D-023-18）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
blocks: []
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - "trigger: 单次scan产生drift events >50 → storm mode"
  - "storm行为: 暂停自动修复、漂移按维度聚合(bulk_drift_event)、severity降级"
  - "expected_storm: commit含REFACTOR/MIGRATION/REFORMAT → 自动识别"
  - "unexpected_storm: 无已知原因大规模漂移 → P0告警(基础设施损坏/恶意篡改)"
  - "recovery: 连续2次scan漂移<50 或 Owner手动解除 → 对bulk_drift_event split为独立事件 → 正常生命周期"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.11"]}]
tags: ["drift-detector","storm-mode","D-023-18"]
---

# TASK-INF-0012: 漂移风暴与批量处理（D-023-18）
## 目标: 当单次scan产生>50漂移时进入storm mode，批量处理而非逐条告警。对标 §2.11。
## 执行步骤: (1) StormDetector检查 `len(new_events) > 50`。(2) 创建 `bulk_drift_event`(affected_modules列表+dimension分组)。(3) 识别expected vs unexpected storm。(4) Recovery: split bulk → individual events。
