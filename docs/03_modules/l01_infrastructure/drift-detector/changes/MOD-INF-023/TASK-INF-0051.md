---
task_id: "TASK-INF-0051"
title: "配置多源一致性 config_consistency.py（D-023-29）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\config_consistency.py"]
acceptance_criteria:
  - 三源(.env/YAML/硬编码defaults)提取所有配置键CONFIG_CONFLICT/MISSING_SECRET_WARNING/UNUSED_CONFIG
  - YAML为SSoT auto_fix生成config_sync.yaml
rollback_instructions: "git checkout src/zephyr/drift_detector/config_consistency.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.21"]}]
tags: ["drift-detector","decision","§6.21"]
---
# TASK-INF-0051: 配置多源一致性 config_consistency.py（D-023-29）
对标 §6.21。三源(.env/YAML/硬编码defaults)提取所有配置键CONFIG_CONFLICT/MISSING_SECRET_WARNING/UNUSED_CONFIG
